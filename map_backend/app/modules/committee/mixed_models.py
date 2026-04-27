"""
modules/committee/mixed_models.py — 混合投委会问卷提交 ORM 模型

设计原则：
  - 对前端透明：不暴露 meeting_id，前端只需传 session_code（会期标识）
  - 后端内部用 session_code 关联会议；meeting_id 绑定逻辑在 service 层处理
  - questionnaire_json 存储结构化资配观点，兼容 TDSQL JSON 类型
  - 严禁物理外键，跨表通过逻辑 ID + 索引关联
"""
import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, Index, String
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm_base import Base


# ── 枚举定义 ──────────────────────────────────────────────────────────────────


class MixedSubmissionStatus(str, enum.Enum):
    DRAFT = "DRAFT"        # 草稿（尚未最终提交）
    SUBMITTED = "SUBMITTED"  # 已确认提交


# ── ORM 模型 ──────────────────────────────────────────────────────────────────


class IcMixedQuestionnaireSubmission(Base):
    """
    混合投委会 — 会前筹备与填报阶段问卷提交记录表。

    设计说明
    --------
    - session_code：会期标识（如 "2026Q2-MIXED-001"），对前端透明；
      后端 service 层负责将其与 ic_meetings.meeting_code 关联，
      前端无需感知 meeting_id。
    - submitter_id：提交人 user_id（逻辑关联，无物理外键）
    - status：DRAFT（草稿）/ SUBMITTED（确认提交）
    - questionnaire_json：资配观点结构化内容，示例：
      {
        "section_a_allocation": {
          "equity_domestic": "增配",
          "equity_overseas": "中性",
          "bond_interest_rate": "减配",
          "bond_credit": "中性",
          "commodity": "增配",
          "alternatives": "中性"
        },
        "section_b_macro": {
          "gdp_growth_view": "温和复苏",
          "inflation_view": "温和通胀",
          "policy_stance": "宽松偏积极"
        },
        "section_c_core_view": "当前经济处于温和复苏通道，建议适度增配权益…",
        "section_d_target_positions": {
          "hs300_target": 4200.0,
          "cn10y_yield_target": 2.35,
          "gold_view": "中性偏多"
        }
      }
    - submitted_at：确认提交时间（DRAFT 状态下为空）

    唯一性约束：同一 session_code + submitter_id 只允许一条记录（幂等覆盖）
    """

    __tablename__ = "ic_mixed_questionnaire_submissions"
    __table_args__ = (
        # 同一会期同一提交人唯一（保障幂等）
        Index(
            "uq_ic_mixed_qs_session_submitter",
            "session_code", "submitter_id",
            unique=True,
        ),
        # 高频查询：按会期过滤所有提交
        Index("ix_ic_mixed_qs_session_code", "session_code"),
        # 高频查询：按提交人查询历史
        Index("ix_ic_mixed_qs_submitter_id", "submitter_id"),
        # 按状态过滤（管理后台用）
        Index("ix_ic_mixed_qs_status", "status"),
        {"comment": "混合投委会会前筹备问卷提交记录，每人每场会期唯一"},
    )

    session_code: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="会期标识，如 2026Q2-MIXED-001；对前端透明，后端内部与 ic_meetings 关联",
    )
    submitter_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="提交人 user_id（逻辑关联，无物理外键）",
    )
    status: Mapped[MixedSubmissionStatus] = mapped_column(
        Enum(MixedSubmissionStatus),
        nullable=False,
        default=MixedSubmissionStatus.DRAFT,
        server_default="DRAFT",
        comment="提交状态 DRAFT=草稿 SUBMITTED=已确认提交",
    )
    questionnaire_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment=(
            "资配观点结构化内容 JSON，含 section_a_allocation / section_b_macro / "
            "section_c_core_view / section_d_target_positions 等板块"
        ),
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="确认提交时间（DRAFT 状态下为空）",
    )
