"""
modules/consumers/worker.py — RocketMQ 消费者守护进程（骨架）
在 FastAPI lifespan 或独立进程中启动，持续拉取消息并分发到 handlers。
"""
import asyncio
import logging

from app.core.config import settings
from app.modules.consumers.handlers import dispatch

logger = logging.getLogger(__name__)


class RocketMQConsumerWorker:
    def __init__(self) -> None:
        self._running = False
        self._consumer = None

    async def start(self) -> None:
        self._running = True
        logger.info("RocketMQ consumer worker starting...")
        asyncio.create_task(self._consume_loop())

    async def stop(self) -> None:
        self._running = False
        if self._consumer:
            try:
                self._consumer.shutdown()
            except Exception as exc:
                logger.warning("Consumer shutdown error: %s", exc)

    async def _consume_loop(self) -> None:
        """
        实际消费循环。
        生产就绪时替换为真实 SDK 订阅逻辑；当前为 stub 轮询占位。
        """
        while self._running:
            try:
                await self._poll_once()
            except Exception as exc:
                logger.error("Consumer poll error: %s", exc)
            await asyncio.sleep(1)

    async def _poll_once(self) -> None:
        # TODO: 接入 rocketmq-client-python 的 pull/push consumer
        pass


consumer_worker = RocketMQConsumerWorker()
