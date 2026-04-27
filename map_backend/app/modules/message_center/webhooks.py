"""
modules/message_center/webhooks.py — 接收外部推送的原始信号

职责：
  - 提供极简 HTTP 端点，接收外部系统（风控、组合、研究）的事件推送
  - 只做格式校验 + 标准化，不做业务处理（交由 scenario_assembler）
  - 所有 payload 字段均为可选，保持最大兼容性
"""
import logging
from datetime import UTC, datetime

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RawSignal(BaseModel):
    """外部系统推送的原始信号结构。"""
    source: str = Field(..., description="信号来源，如 risk_sys / portfolio_sys / research_sys")
    event_type: str = Field(..., description="事件类型，如 RISK_ALERT / REBALANCE_DONE")
    payload: dict = Field(default_factory=dict, description="原始业务数据")
    occurred_at: str | None = Field(default=None, description="事件发生时间 ISO8601")
    idempotency_key: str | None = Field(default=None, description="幂等键，防重复处理")


def normalize_signal(raw: RawSignal) -> dict:
    """将外部原始信号标准化为 MAP 内部格式。"""
    return {
        "source": raw.source,
        "event_type": raw.event_type,
        "payload": raw.payload,
        "occurred_at": raw.occurred_at or datetime.now(UTC).isoformat(),
        "idempotency_key": raw.idempotency_key,
        "received_at": datetime.now(UTC).isoformat(),
    }
