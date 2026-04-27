"""
app/modules/auth/models.py — 用户模型
门户 SSO 登录态对应的本地用户表。
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger, DateTime, Enum as SAEnum, Index, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm_base import Base


class UserStatus(int, Enum):
    ACTIVE = 1
    DISABLED = 0


class MapUser(Base):
    __tablename__ = "map_users"
    __table_args__ = (
        Index("uq_map_users_portal_id", "portal_user_id", unique=True),
        Index("uq_map_users_username", "username", unique=True),
        {"comment": "MAP 系统用户表"},
    )

    portal_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True, comment="门户用户 ID（逻辑关联）")
    username: Mapped[str] = mapped_column(String(128), nullable=False, comment="登录用户名")
    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="显示名称/姓名")
    email: Mapped[str | None] = mapped_column(String(256), nullable=True, comment="邮箱")
    department: Mapped[str | None] = mapped_column(String(256), nullable=True, comment="所属部门")
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=UserStatus.ACTIVE, server_default="1", comment="状态 1=正常 0=禁用")
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="最近登录时间")
