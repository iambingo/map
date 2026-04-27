"""
app/modules/auth/schemas.py — SSO 认证相关 Pydantic Schema
"""
from pydantic import BaseModel, Field


class PortalUserInfo(BaseModel):
    """门户 token 校验接口返回的用户信息解析。
    具体字段需与门户确认，此处预留常见字段。
    """
    user_id: str | None = Field(default=None, description="门户用户 ID")
    username: str | None = Field(default=None, description="用户名/工号")
    display_name: str | None = Field(default=None, description="显示名称")
    email: str | None = Field(default=None, description="邮箱")
    department: str | None = Field(default=None, description="部门")

    # 透传原始数据，便于适配未知字段
    raw_data: dict | None = Field(default=None, description="门户返回的原始 JSON（调试用）")


class UserInfo(BaseModel):
    """本地用户信息返回 Schema。"""
    model_config = {"from_attributes": True}

    id: int
    portal_user_id: int
    username: str
    display_name: str | None = None
    email: str | None = None
    department: str | None = None
