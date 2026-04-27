"""
modules/committee/models.py — 投委会 ORM 模型
⚠️  架构纪律：
    - 严禁物理外键 (FOREIGN KEY)，跨表关联通过逻辑 ID + 索引实现
    - JSON 类型用于存储投票内容与聚合结果（MySQL 5.7+ / TDSQL 原生支持）
    - 枚举常量定义于此，供 schemas / services 层统一导入，杜绝重复定义
"""
import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, Index, String, Text
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm_base import Base


# ── 枚举定义（单一事实源） ─────────────────────────────────────────────────────


class MeetingType(str, enum.Enum):
    FICC = "FICC"
    MIXED = "MIXED"


class MeetingStatus(str, enum.Enum):
    DRAFT = "DRAFT"        # 草稿，尚未开放投票
    VOTING = "VOTING"      # 投票进行中
    PUBLISHED = "PUBLISHED"  # 决议已发布，终态


# ── ORM 模型 ──────────────────────────────────────────────────────────────────


class IcMeeting(Base):
    """
    投委会会议主表。
    一场会议对应多条 IcVoteRecord 和至多一条 IcResolution（逻辑关联）。
    """

    __tablename__ = "ic_meetings"
    __table_args__ = (
        # meeting_code 全局唯一，业务层用于幂等创建
        Index("uq_ic_meetings_meeting_code", "meeting_code", unique=True),
        # 高频查询：按状态+软删除过滤列表
        Index("ix_ic_meetings_status_deleted", "status", "is_deleted"),
        {"comment": "投委会会议主表"},
    )

    meeting_code: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="会议编码，业务唯一键",
    )
    title: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="会议标题",
    )
    type: Mapped[MeetingType] = mapped_column(
        Enum(MeetingType),
        nullable=False,
        comment="会议类型 FICC=固定收益 MIXED=混合",
    )
    status: Mapped[MeetingStatus] = mapped_column(
        Enum(MeetingStatus),
        nullable=False,
        default=MeetingStatus.DRAFT,
        server_default="DRAFT",
        comment="会议状态 DRAFT→VOTING→PUBLISHED",
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="计划召开时间（可空）",
    )
    created_by: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
        comment="创建人 user_id（逻辑关联，无物理外键）",
    )


class IcVoteRecord(Base):
    """
    投委会投票记录表。
    每位委员每场会议只能提交一份投票（meeting_id + user_id 联合唯一索引保障）。

    vote_json 结构（FICC 标准格式）：
    {
        "choice_items":  {"equity_view": "overweight", "bond_view": "neutral"},
        "numeric_items": {"hs300_target": 4200.0, "cn10y_yield": 2.35}
    }
    """

    __tablename__ = "ic_vote_records"
    __table_args__ = (
        # 每人每场会议唯一，保障幂等覆写
        Index("uq_ic_vote_records_meeting_user", "meeting_id", "user_id", unique=True),
        # 单字段索引：支持按会议或按用户独立查询
        Index("ix_ic_vote_records_meeting_id", "meeting_id"),
        Index("ix_ic_vote_records_user_id", "user_id"),
        {"comment": "投委会投票记录，每人每场会议唯一"},
    )

    meeting_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="会议 ID（逻辑关联，无物理外键）",
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="投票人 user_id（逻辑关联，无物理外键）",
    )
    vote_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="投票内容 JSON：choice_items（众数项）+ numeric_items（均值项）",
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="投票提交时间",
    )


class IcResolution(Base):
    """
    投委会决议表。
    每场会议至多一条决议（meeting_id 唯一索引），由计票聚合后写入。

    aggregated_taa 结构：
    {
        "meeting_type": "FICC",
        "total_voters": 8,
        "computed_at": "2026-04-19T10:00:00Z",
        "choice_results": {
            "equity_view": {
                "winner": "overweight",
                "vote_counts": {"overweight": 5, "neutral": 2, "underweight": 1}
            }
        },
        "numeric_results": {
            "hs300_target": {"mean": 4200.0, "std": 150.5, "min": 3900.0, "max": 4500.0, "count": 8}
        }
    }
    """

    __tablename__ = "ic_resolutions"
    __table_args__ = (
        Index("uq_ic_resolutions_meeting_id", "meeting_id", unique=True),
        {"comment": "投委会决议，每场会议唯一，由计票聚合写入"},
    )

    meeting_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="会议 ID（逻辑关联，无物理外键）",
    )
    aggregated_taa: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="聚合后的最终资产配置指引 JSON",
    )
    ai_minutes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="AI 生成会议纪要（异步生成，初始为空）",
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="决议发布时间",
    )
    published_by: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        comment="发布操作人 user_id（逻辑关联，无物理外键）",
    )
