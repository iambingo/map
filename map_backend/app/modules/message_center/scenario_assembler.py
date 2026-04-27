"""
modules/message_center/scenario_assembler.py — 场景组装引擎

职责：
  - 接收标准化信号，组装成前端可直接渲染的场景卡片
  - 通过 sse_push 实时推送给相关用户
  - 广播事件（IC_RESOLUTION、RESEARCH_REPORT）推全员，其余按 user_id 定向推送
"""
import logging

from app.modules.message_center.sse_push import broadcast_event, push_event

logger = logging.getLogger(__name__)

_EVENT_TITLE: dict[str, str] = {
    "RISK_ALERT":       "风险预警",
    "REBALANCE_DONE":   "调仓完成",
    "SAA_PUBLISHED":    "SAA 方案已发布",
    "IC_RESOLUTION":    "投委会决议更新",
    "RESEARCH_REPORT":  "研究报告就绪",
}

_BROADCAST_EVENTS = {"IC_RESOLUTION", "RESEARCH_REPORT"}


async def assemble_and_push(signal: dict) -> None:
    """组装场景卡片并推送 SSE。signal 为 normalize_signal() 的返回值。"""
    event_type = signal.get("event_type", "UNKNOWN")
    payload = signal.get("payload", {})

    card = {
        "event_type": event_type,
        "title": _EVENT_TITLE.get(event_type, event_type),
        "source": signal.get("source", ""),
        "summary": _build_summary(event_type, payload),
        "payload": payload,
        "occurred_at": signal.get("occurred_at"),
    }

    logger.info("Assembled scene card: event_type=%s", event_type)

    if event_type in _BROADCAST_EVENTS:
        await broadcast_event("SCENE_CARD", card)
    else:
        user_id = payload.get("user_id")
        if user_id:
            await push_event(int(user_id), "SCENE_CARD", card)
        else:
            await broadcast_event("SCENE_CARD", card)


def _build_summary(event_type: str, payload: dict) -> str:
    if event_type == "RISK_ALERT":
        return f"风险等级 {payload.get('level', '未知')}，请及时关注"
    if event_type == "REBALANCE_DONE":
        return f"组合 {payload.get('portfolio_id', '-')} 调仓已完成"
    if event_type == "SAA_PUBLISHED":
        return f"SAA 草稿 #{payload.get('draft_id', '-')} 已发布生效"
    if event_type == "IC_RESOLUTION":
        return f"投委会会议 #{payload.get('meeting_id', '-')} 决议已更新"
    if event_type == "RESEARCH_REPORT":
        return f"研究报告《{payload.get('title', '新报告')}》已就绪"
    return "收到新消息"
