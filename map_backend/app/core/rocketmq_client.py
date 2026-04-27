"""
core/rocketmq_client.py — RocketMQ 生产者初始化封装
提供异步安全的 Producer 单例，供各模块调用 send_message()。
消费者守护进程在 modules/consumers/worker.py 中管理，不在此处启动。
⚠️  禁止在此处编写任何业务路由 / Tag 处理逻辑。
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class MQMessage:
    """投递给 RocketMQ 的标准消息载体。"""

    topic: str
    tag: str
    body: dict[str, Any]
    keys: str = ""
    delay_level: int = 0  # 0 = 不延迟


class RocketMQProducer:
    """
    RocketMQ 生产者封装。
    当前使用 rocketmq-client-python（C SDK 绑定）；
    若切换为 HTTP API 模式，只需替换 _send_impl 即可。
    """

    def __init__(self) -> None:
        self._producer: Any = None
        self._lock = asyncio.Lock()
        self._started = False

    async def start(self) -> None:
        async with self._lock:
            if self._started:
                return
            try:
                # 延迟导入，避免未安装 SDK 时启动失败
                from rocketmq.client import Producer, SendStatus  # type: ignore[import]

                p = Producer(settings.ROCKETMQ_PRODUCER_GROUP)
                p.set_name_server_address(settings.ROCKETMQ_NAME_SERVER)
                p.start()
                self._producer = p
                self._started = True
                logger.info(
                    "RocketMQ producer started: group=%s ns=%s",
                    settings.ROCKETMQ_PRODUCER_GROUP,
                    settings.ROCKETMQ_NAME_SERVER,
                )
            except ImportError:
                logger.warning(
                    "rocketmq-client-python not installed; producer disabled (stub mode)."
                )
            except Exception as exc:
                logger.error("Failed to start RocketMQ producer: %s", exc)
                raise

    async def shutdown(self) -> None:
        if self._producer and self._started:
            try:
                self._producer.shutdown()
            except Exception as exc:
                logger.warning("RocketMQ producer shutdown error: %s", exc)
            finally:
                self._started = False

    async def send_message(self, msg: MQMessage) -> bool:
        """
        异步发送普通消息（非事务消息）。
        :returns: True 表示发送成功，False 表示 stub 模式或发送失败。
        """
        if not self._started or self._producer is None:
            logger.debug("MQ stub: would send tag=%s body=%s", msg.tag, msg.body)
            return False

        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(None, self._send_sync, msg)
            return True
        except Exception as exc:
            logger.error("RocketMQ send failed tag=%s: %s", msg.tag, exc)
            return False

    def _send_sync(self, msg: MQMessage) -> None:
        import json

        from rocketmq.client import Message, SendStatus  # type: ignore[import]

        rmq_msg = Message(msg.topic)
        rmq_msg.set_tags(msg.tag)
        rmq_msg.set_keys(msg.keys)
        rmq_msg.set_body(json.dumps(msg.body, ensure_ascii=False).encode())
        if msg.delay_level > 0:
            rmq_msg.set_delay_time_level(msg.delay_level)

        result = self._producer.send_sync(rmq_msg)
        from rocketmq.client import SendStatus  # type: ignore[import]

        if result.status != SendStatus.OK:
            raise RuntimeError(f"RocketMQ send status={result.status}")


# ── 全局单例 ──────────────────────────────────────────────────────────────────

mq_producer = RocketMQProducer()


@asynccontextmanager
async def lifespan_mq():
    """在 FastAPI lifespan 中使用，保证启停顺序。"""
    await mq_producer.start()
    try:
        yield
    finally:
        await mq_producer.shutdown()
