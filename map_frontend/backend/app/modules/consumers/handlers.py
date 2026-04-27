"""
modules/consumers/handlers.py — RocketMQ 消息处理路由（骨架）
根据消息 Tag 路由到对应业务处理函数。
"""
import logging

logger = logging.getLogger(__name__)

# Tag -> handler 映射注册表
_HANDLERS: dict = {}


def register_handler(tag: str):
    """装饰器：将处理函数注册到 Tag 路由表。"""
    def decorator(fn):
        _HANDLERS[tag] = fn
        return fn
    return decorator


async def dispatch(tag: str, body: dict) -> None:
    handler = _HANDLERS.get(tag)
    if handler is None:
        logger.warning("No handler registered for tag=%s", tag)
        return
    await handler(body)


# ── 示例 Handler（开发阶段占位） ──────────────────────────────────────────────

@register_handler("SAA_RESULT_READY")
async def handle_saa_result(body: dict) -> None:
    """接收外部系统计算完成的 SAA 结果，写入 DB 并触发 SSE 推送。"""
    raise NotImplementedError
