"""
modules/consumers/worker.py — RocketMQ 消费者守护进程

在 FastAPI lifespan 中启动，持续拉取消息并分发到 handlers.dispatch()。

SDK 接入策略：
  - 优先尝试导入 rocketmq-client-python（C SDK 绑定）
  - SDK 不可用时自动降级为 stub 模式（仅打印日志，不消费真实消息）
  - 生产环境替换 _try_init_sdk() 内部逻辑即可，其余不变
"""
import asyncio
import json
import logging

from app.core.config import settings
from app.modules.consumers.handlers import dispatch

logger = logging.getLogger(__name__)

_POLL_INTERVAL = 1.0   # 正常轮询间隔（秒）
_ERROR_BACKOFF = 5.0   # 出错后退避间隔（秒）


class RocketMQConsumerWorker:
    def __init__(self) -> None:
        self._running = False
        self._consumer = None
        self._sdk_available = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._sdk_available = self._try_init_sdk()
        self._task = asyncio.create_task(self._consume_loop(), name="rocketmq-consumer")
        logger.info(
            "RocketMQ consumer worker started (sdk=%s topic=%s group=%s)",
            self._sdk_available,
            settings.ROCKETMQ_TOPIC,
            settings.ROCKETMQ_CONSUMER_GROUP,
        )

    async def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._consumer:
            try:
                self._consumer.shutdown()
            except Exception as exc:
                logger.warning("Consumer shutdown error: %s", exc)
            self._consumer = None
        logger.info("RocketMQ consumer worker stopped.")

    def _try_init_sdk(self) -> bool:
        """尝试初始化 Push Consumer；失败则降级 stub，不阻断启动。"""
        try:
            from rocketmq.client import PushConsumer  # type: ignore[import]

            consumer = PushConsumer(settings.ROCKETMQ_CONSUMER_GROUP)
            consumer.set_name_server_address(settings.ROCKETMQ_NAME_SERVER)
            consumer.subscribe(settings.ROCKETMQ_TOPIC, self._sync_message_callback)
            consumer.start()
            self._consumer = consumer
            logger.info("RocketMQ Push Consumer initialized.")
            return True
        except ImportError:
            logger.warning("rocketmq-client-python not installed; stub mode active.")
            return False
        except Exception as exc:
            logger.error("Failed to init RocketMQ consumer: %s", exc)
            return False

    def _sync_message_callback(self, msg) -> "ConsumeStatus":  # type: ignore[name-defined]
        """
        SDK 同步回调（在 C 线程中执行）。
        将消息投入 asyncio 事件循环，避免阻塞 C 线程。
        """
        try:
            from rocketmq.client import ConsumeStatus  # type: ignore[import]

            tag = msg.tags.decode() if isinstance(msg.tags, bytes) else msg.tags
            raw = msg.body.decode() if isinstance(msg.body, bytes) else msg.body
            body = json.loads(raw)

            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(dispatch(tag, body), loop)
            return ConsumeStatus.CONSUME_SUCCESS
        except Exception as exc:
            logger.error("Message callback error: %s", exc)
            from rocketmq.client import ConsumeStatus  # type: ignore[import]
            return ConsumeStatus.RECONSUME_LATER

    async def _consume_loop(self) -> None:
        """
        主消费循环。
        SDK 模式：Push Consumer 已在后台运行，此循环仅做存活保持。
        Stub 模式：空轮询，本地开发时可直接调用 dispatch() 注入测试消息。
        """
        while self._running:
            try:
                await asyncio.sleep(_POLL_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Consumer loop error: %s", exc)
                await asyncio.sleep(_ERROR_BACKOFF)


consumer_worker = RocketMQConsumerWorker()
