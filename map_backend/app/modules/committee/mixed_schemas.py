"""
modules/committee/mixed_schemas.py — 混合投委会问卷提交 Pydantic V2 Schema

设计原则：
  - 对前端透明：前端只需传资配观点 JSON，不感知 meeting_id / session 内部机制
  - session_code 由后端根据当前活跃会期自动解析，前端可传也可不传（留空时后端兜底）
  - viewpoint_json 为宽松 dict，支持前端各版本字段，后端不做严格校验（向后兼容）
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Request Schemas ───────────────────────────────────────────────────────────


class SubmitMixedViewpointRequest(BaseModel):
    """
    前端提交资配观点的请求体。

    session_code: 会期标识，可选。
        - 传入时：使用指定会期
        - 不传时：后端自动使用最新活跃会期（对前端透明）
        格式建议：YYYYQN，如 "2026Q2"

    viewpoint_json: 资配观点内容，结构宽松，与前端 CommitteeView STEP 0 表单对齐。
        典型结构示例：
        {
          "section_a": {"股票": "增", "债券": "减", "商品": "中性"},
          "section_b": {"hs300_target": 4200.0, "cn10y_yield": 2.35},
          "core_view": "当前宏观环境利好权益资产...",
          "risk_level": "中性偏积极"
        }
    """

    session_code: str | None = Field(
        default=None,
        max_length=32,
        description="会期标识（可选），不传时后端自动使用当前活跃会期",
        examples=["2026Q2"],
    )
    viewpoint_json: dict[str, Any] = Field(
        ...,
        description="资配观点内容 JSON，字段宽松，与前端表单结构对齐",
    )


# ── Response Schemas ──────────────────────────────────────────────────────────


class MixedSubmissionResponse(BaseModel):
    """
    提交成功后返回的记录摘要。
    不向前端暴露 meeting_id 内部字段。
    """

    model_config = {"from_attributes": True}

    id: int = Field(description="提交记录主键 ID")
    session_code: str = Field(description="本次提交对应的会期标识")
    submitter_id: int = Field(description="提交人 user_id")
    submitted_at: datetime | None = Field(None, description="提交时间")
    created_at: datetime = Field(description="记录创建时间")
    questionnaire_json: dict[str, Any] | None = Field(
        default=None,
        description="资配观点内容 JSON，包含 section_a/section_b/section_c 等评分明细",
    )


class MixedSubmissionListResponse(BaseModel):
    """管理员查看当前会期所有提交的列表响应。"""

    session_code: str
    total: int
    submissions: list[MixedSubmissionResponse]


# ── History & Reminder Schemas ────────────────────────────────────────────────


class HistorySessionItem(BaseModel):
    """历史会期摘要，含该期所有委员评分聚合数据。"""

    session_code: str = Field(description="会期标识")
    submitted_count: int = Field(description="已提交人数")
    scores: dict[str, dict[str, float | int]] = Field(
        description="按资产聚合的评分数据，每项资产含 avg/max/min/delta 等字段",
    )


class MixedHistoryResponse(BaseModel):
    """历史会期列表响应。"""

    sessions: list[HistorySessionItem] = Field(description="历史会期列表，按时间倒序")


class MixedRemindRequest(BaseModel):
    """催办通知请求体。"""

    session_code: str | None = Field(
        default=None,
        description="会期标识（可选），不传时默认为当前季度",
    )
    member_name: str = Field(description="被催办委员姓名（用于日志记录）")
    member_id: int | None = Field(
        default=None,
        description="被催办委员 user_id（可选，留空时后端根据 member_name 查找）",
    )
