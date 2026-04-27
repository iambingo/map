"""
modules/message_center/sse_push.py — SSE 长连接实时推送

设计：
  - 每个 user_id 维护订阅队列列表（支持同一用户多标签页）
  - push_event() 向指定用户投递事件
  - event_stream() 是 FastAPI StreamingResponse 的异步生成器
  - 连接断开时自动清理队列，防止内存泄漏
"""
import asyncio
import json
import logging
from collections import defaultdict
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

_subscribers: dict[int, list[asyncio.Queue]] = defaultdict(list)
_HEARTBEAT_INTERVAL = 25  # seconds，防止代理/浏览器断开空闲连接


async def push_event(user_id: int, event_type: str, data: dict) -> None:
    """向指定用户的所有活跃连接推送事件。"""
    queues = _subscribers.get(user_id, [])
    if not queues:
        return
    payload = json.dumps({"type": event_type, "data": data}, ensure_ascii=False)
    for q in queues:
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            logger.warning("SSE queue full for user_id=%s, dropping event", user_id)


async def broadcast_event(event_type: str, data: dict) -> None:
    """向所有在线用户广播事件。"""
    for user_id in list(_subscribers.keys()):
        await push_event(user_id, event_type, data)


async def event_stream(user_id: int) -> AsyncGenerator[str, None]:
    """
    SSE 事件流生成器，挂载到 StreamingResponse。
    格式遵循 SSE 规范：data: <json>\\n\\n
    """
    q: asyncio.Queue = asyncio.Queue(maxsize=64)
    _subscribers[user_id].append(q)
    logger.info("SSE connected: user_id=%s active=%d", user_id, len(_subscribers[user_id]))
    try:
        while True:
            try:
                payload = await asyncio.wait_for(q.get(), timeout=_HEARTBEAT_INTERVAL)
                yield f"data: {payload}\n\n"
            except asyncio.TimeoutError:
                yield ": heartbeat\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        _subscribers[user_id].remove(q)
        if not _subscribers[user_id]:
            del _subscribers[user_id]
        logger.info("SSE disconnected: user_id=%s", user_id)
