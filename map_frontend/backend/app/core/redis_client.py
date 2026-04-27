"""
core/redis_client.py — 异步 Redis 客户端单例
提供懒加载连接池、健康检查和优雅关闭能力。
⚠️  禁止在此处编写任何业务逻辑；仅封装基础设施连接管理。
"""
import logging

import redis.asyncio as aioredis
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_client: Redis | None = None


async def get_redis() -> Redis:
    """
    获取全局 Redis 客户端（懒加载，首次调用时建立连接池）。
    连接失败时抛出 RedisError，调用方应捕获并降级处理。
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        logger.info("Redis client initialized: %s", settings.REDIS_URL)
    return _redis_client


async def close_redis() -> None:
    """在 FastAPI lifespan shutdown 阶段调用，释放连接池。"""
    global _redis_client
    if _redis_client is not None:
        try:
            await _redis_client.aclose()
            logger.info("Redis client closed.")
        except RedisError as exc:
            logger.warning("Redis close error (ignored): %s", exc)
        finally:
            _redis_client = None


async def ping_redis() -> bool:
    """健康检查，返回 True 表示 Redis 可达。"""
    try:
        client = await get_redis()
        return await client.ping()
    except RedisError:
        return False
