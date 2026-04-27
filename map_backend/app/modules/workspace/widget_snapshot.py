"""
modules/workspace/widget_snapshot.py — 柔性 Redis 缓存层

双键缓存策略（核心设计）
─────────────────────────────────────────────────────────────────
  live  key: workspace:<cache_key>          TTL = 300s（5 分钟热数据）
  stale key: workspace:<cache_key>:stale    TTL = 86400s（24 小时保险层）

读取流程：
  1. 优先读 live key → 命中时 is_stale=False
  2. live miss → 读 stale key → 命中时 is_stale=True（降级）
  3. 双 miss → 返回 (None, False)

写入流程：
  每次成功回源后同时写 live + stale 两个 key，
  保证 stale 始终比 live 更新或同新。

降级底线（README 要求）：
  外部系统宕机时，用 stale 数据兜底并附加 is_stale=True 标识，
  绝不向前端抛出 500，绝不白屏。

Redis 故障透传：
  所有函数均捕获 RedisError，Redis 自身故障时直接跳过缓存层，
  确保链路可用性不依赖 Redis 的可用性。
"""
from __future__ import annotations

import json
import logging
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

_KEY_PREFIX = "workspace"
_LIVE_TTL   = 300     # seconds — 5 分钟，数据"足够新"
_STALE_TTL  = 86400   # seconds — 24 小时，降级保险层


def _live_key(cache_key: str) -> str:
    return f"{_KEY_PREFIX}:{cache_key}"


def _stale_key(cache_key: str) -> str:
    return f"{_KEY_PREFIX}:{cache_key}:stale"


async def get_cached_snapshot(
    redis: Redis,
    cache_key: str,
) -> tuple[dict[str, Any] | None, bool]:
    """
    读取缓存快照。

    Returns
    -------
    (data, is_stale)
      data     — 反序列化后的字典；None 表示完全缓存未命中
      is_stale — True 表示返回的是过期 stale 备份数据
    """
    try:
        # ① 读 live key
        raw = await redis.get(_live_key(cache_key))
        if raw:
            return json.loads(raw), False

        # ② live miss → 尝试 stale 降级
        raw = await redis.get(_stale_key(cache_key))
        if raw:
            logger.warning("Serving stale snapshot for key=%s", cache_key)
            return json.loads(raw), True

        return None, False

    except RedisError as exc:
        logger.error("Redis read error (cache bypassed) key=%s: %s", cache_key, exc)
        return None, False


async def set_cached_snapshot(
    redis: Redis,
    cache_key: str,
    data: dict[str, Any],
    live_ttl: int = _LIVE_TTL,
    stale_ttl: int = _STALE_TTL,
) -> None:
    """
    写入 live + stale 双键缓存。
    Redis 故障时静默忽略，不中断主流程。
    """
    try:
        serialized = json.dumps(data, ensure_ascii=False, default=str)
        pipe = redis.pipeline()
        pipe.setex(_live_key(cache_key), live_ttl, serialized)
        pipe.setex(_stale_key(cache_key), stale_ttl, serialized)
        await pipe.execute()
    except RedisError as exc:
        logger.error("Redis write error (snapshot not cached) key=%s: %s", cache_key, exc)


async def invalidate_snapshot(redis: Redis, cache_key: str) -> None:
    """
    主动失效某个快照的 live key（强制下次请求回源）。
    stale key 保留，确保回源失败时仍有降级数据可用。
    """
    try:
        await redis.delete(_live_key(cache_key))
        logger.info("Snapshot invalidated: key=%s", cache_key)
    except RedisError as exc:
        logger.warning("Redis delete error key=%s: %s", cache_key, exc)
