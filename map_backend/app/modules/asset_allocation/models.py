"""
modules/asset_allocation/models.py — 资产配置 ORM 模型

表结构：
  - saa_drafts        : SAA 草稿（含权重 JSON、状态机）
  - asset_class_config: 资产类别基础配置（上下限、预期收益率等）
"""
import enum

from sqlalchemy import BigInteger, Float, Index, JSON, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm_base import Base


class DraftStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"


class SaaDraft(Base):
    """SAA 草稿表，每次调整权重生成新版本（version 递增）。"""

    __tablename__ = "saa_drafts"
    __table_args__ = (
        Index("ix_saa_drafts_user_status", "user_id", "status", "is_deleted"),
        Index("ix_saa_drafts_version", "user_id", "version"),
        {"comment": "SAA 战略资产配置草稿表"},
    )

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="创建人 user_id")
    version: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1, comment="版本号")
    risk_level: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="风险等级 1-5")
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, comment="总配置金额（万元）")
    weights: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict, comment="资产类别权重")
    expected_return: Mapped[float | None] = mapped_column(Float, nullable=True, comment="预期年化收益率")
    expected_volatility: Mapped[float | None] = mapped_column(Float, nullable=True, comment="预期年化波动率")
    constraints: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict, comment="约束条件")
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=DraftStatus.DRAFT, server_default="DRAFT", comment="草稿状态"
    )
    reject_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="审批拒绝原因")
    approver_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="审批人 user_id")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注说明")


class AssetClassConfig(Base):
    """资产类别基础配置表，供 SAA 计算引擎使用。"""

    __tablename__ = "asset_class_configs"
    __table_args__ = (
        Index("uq_asset_class_code", "code", unique=True),
        {"comment": "资产类别配置表"},
    )

    code: Mapped[str] = mapped_column(String(32), nullable=False, comment="资产类别代码")
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="资产类别名称")
    expected_return: Mapped[float] = mapped_column(Float, nullable=False, comment="预期年化收益率")
    expected_volatility: Mapped[float] = mapped_column(Float, nullable=False, comment="预期年化波动率")
    default_min_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="默认最低权重")
    default_max_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0, comment="默认最高权重")
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, comment="展示排序")
    is_active: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1", comment="是否启用")
