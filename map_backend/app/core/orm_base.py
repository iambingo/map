"""
core/orm_base.py — ORM 声明基类（无引擎、无配置依赖）

供业务模型与 init_db 等离线脚本共用，避免 import db_tdsql 时强制加载 MySQL 异步驱动。
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, SmallInteger, func, inspect, text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """
    所有 ORM Model 的公共基类。
    内置软删除 (is_deleted)、审计时间戳 (created_at / updated_at)
    以及 BigInt 自增主键 (id)。
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="主键 ID",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="最后更新时间",
    )

    is_deleted: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
        server_default=text("0"),
        nullable=False,
        index=True,
        comment="软删除标志 0=正常 1=已删除",
    )

    def to_dict(self) -> dict:
        mapper = inspect(self.__class__)
        return {col.key: getattr(self, col.key) for col in mapper.columns}
