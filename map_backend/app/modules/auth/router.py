"""
app/modules/auth/router.py — 认证相关 API 路由（挂在 /api/v1/auth 前缀下）
包含：
  GET /api/v1/auth/me  — 获取当前用户信息（需 JWT）
"""
from fastapi import APIRouter

from app.dependencies import CurrentUserID, DBSession
from app.modules.auth import services
from app.modules.auth.schemas import UserInfo

router = APIRouter()


@router.get(
    "/me",
    response_model=UserInfo,
    summary="获取当前用户信息",
    description="返回当前登录用户的详细信息，需要携带有效 JWT。",
)
async def get_current_user(
    db: DBSession,
    user_id: CurrentUserID,
) -> UserInfo:
    user = await services.get_user_by_id(db, user_id)
    if user is None:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("用户不存在")
    services.check_user_status(user)
    return UserInfo.model_validate(user)
