"""
modules/orchestrator/models.py — 跨域指令持久化模型

pending_commands 表职责：
  - 保障指令幂等（idempotency_key 唯一索引）
  - 记录指令全生命周期状态（PENDING → PROCESSING → DONE / FAILED）
  - 失败时保存错误信息，支持重试或人工介入
"""
import enum

from sqlalchemy import BigInteger, Index, String, Text
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm_base import Base


class CommandStatus(str, enum.Enum):
    PENDING = "PENDING"          # 已登记，等待分发
    PROCESSING = "PROCESSING"    # 已发出（MQ 投递 / Adapter 调用中）
    DONE = "DONE"                # 成功完成
    FAILED = "FAILED"            # 最终失败，需人工介入


class PendingCommand(Base):
    """
    跨域指令登记表。

    idempotency_key 由调用方生成，建议格式：
        {command_type}:{业务主键}:{timestamp_ms}
    同一 key 重复提交时唯一索引报错，业务层捕获后直接返回已有 task_id。
    """

    __tablename__ = "pending_commands"
    __table_args__ = (
        Index("uq_pending_commands_idempotency_key", "idempotency_key", unique=True),
        Index("ix_pending_commands_status", "status", "is_deleted"),
        Index("ix_pending_commands_user_id", "user_id"),
        {"comment": "跨域指令登记表，保障幂等与全链路可追溯"},
    )

    command_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="指令类型，如 SUBMIT_SAA_FOR_APPROVAL / TRIGGER_PORTFOLIO_REBALANCE",
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="幂等键，全局唯一，防止重复投递",
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="发起人 user_id",
    )
    payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="指令业务参数 JSON",
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=CommandStatus.PENDING,
        server_default="PENDING",
        comment="指令状态 PENDING→PROCESSING→DONE/FAILED",
    )
    dispatch_mode: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="MQ",
        server_default="MQ",
        comment="分发模式：MQ=异步消息队列 SYNC=同步 Adapter 调用",
    )
    result: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="执行结果摘要（成功返回值或失败错误信息）",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="失败时的错误详情",
    )
    retry_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        server_default="0",
        comment="已重试次数",
    )
