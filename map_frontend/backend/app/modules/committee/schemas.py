"""
modules/committee/schemas.py — Pydantic V2 Request / Response 模型
枚举类型从 models.py 统一导入，避免两套常量漂移。
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.modules.committee.models import MeetingStatus, MeetingType


# ── 投票内容载体（vote_json 的结构契约） ──────────────────────────────────────


class FiccVotePayload(BaseModel):
    """
    FICC / MIXED 会议的标准投票内容。

    - choice_items:  分类选择题，key=指标名，value=选项字符串
                     计票时取 **众数 (Mode)**。
                     例：{"equity_view": "overweight", "bond_view": "neutral"}

    - numeric_items: 数值点位预测，key=指标名，value=预测数值
                     计票时取 **均值 (Mean)**。
                     例：{"hs300_target": 4200.0, "cn10y_yield": 2.35}
    """

    choice_items: dict[str, str] = Field(
        default_factory=dict,
        description="分类选择题，计票取众数",
        examples=[{"equity_view": "overweight", "bond_view": "neutral"}],
    )
    numeric_items: dict[str, float] = Field(
        default_factory=dict,
        description="数值点位预测，计票取均值",
        examples=[{"hs300_target": 4200.0, "cn10y_yield": 2.35}],
    )

    @model_validator(mode="after")
    def _require_at_least_one_item(self) -> FiccVotePayload:
        if not self.choice_items and not self.numeric_items:
            raise ValueError("投票内容不能为空：choice_items 与 numeric_items 至少填写一项")
        return self


# ── Request Schemas ───────────────────────────────────────────────────────────


class CreateMeetingRequest(BaseModel):
    meeting_code: str = Field(..., min_length=1, max_length=64, description="会议编码（全局唯一）")
    title: str = Field(..., min_length=1, max_length=256, description="会议标题")
    type: MeetingType = Field(..., description="会议类型 FICC / MIXED")
    scheduled_at: datetime | None = Field(None, description="计划召开时间（可选）")


class SubmitVoteRequest(BaseModel):
    vote: FiccVotePayload = Field(..., description="投票内容，遵循 FICC 标准格式")


# ── Response Schemas ──────────────────────────────────────────────────────────


class MeetingResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    meeting_code: str
    title: str
    type: MeetingType
    status: MeetingStatus
    scheduled_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime


class VoteRecordResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    meeting_id: int
    user_id: int
    vote_json: dict[str, Any]
    submitted_at: datetime | None
    created_at: datetime


# ── 聚合结果子结构（用于 ResolutionResponse 内的类型标注与文档生成） ───────────


class ChoiceAggregation(BaseModel):
    """单个分类题的众数聚合结果。"""

    winner: str = Field(description="得票最多的选项")
    vote_counts: dict[str, int] = Field(description="各选项得票数")


class NumericAggregation(BaseModel):
    """单个点位题的均值聚合结果。"""

    mean: float = Field(description="算术均值")
    std: float | None = Field(None, description="标准差（样本≥2时计算）")
    min: float = Field(description="最小值")
    max: float = Field(description="最大值")
    count: int = Field(description="有效投票数")


class ResolutionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    meeting_id: int
    aggregated_taa: dict[str, Any] = Field(description="聚合决议 JSON，含 choice_results 与 numeric_results")
    ai_minutes: str | None = Field(None, description="AI 生成会议纪要")
    published_at: datetime | None
    published_by: int | None
    created_at: datetime


class PublishResponse(BaseModel):
    """发布决议的聚合响应：同时返回更新后的会议状态与决议内容。"""

    meeting: MeetingResponse
    resolution: ResolutionResponse


class CommitteeVoteRow(BaseModel):
    """投委会页上下文中的单条投票摘要（不含 vote_json 全文，避免 payload 过大）。"""

    user_id: int
    submitted_at: datetime | None


class CommitteePageContextResponse(BaseModel):
    """
    投委会视图首屏只读上下文：最近一次已发布决议 + 会议元数据 + 本场投票提交列表。
    无数据时各字段为 null / 空数组，前端应降级展示 Mock 占位。
    """

    meeting: MeetingResponse | None = None
    resolution: ResolutionResponse | None = None
    votes: list[CommitteeVoteRow] = Field(default_factory=list)
