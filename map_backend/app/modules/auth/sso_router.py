"""
app/modules/auth/sso_router.py — 门户 SSO 回调路由（挂在根路径）
仅包含 GET /auth/sso-callback，无需认证。
"""
from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.core.config import settings
from app.core.security import create_access_token
from app.dependencies import DBSession
from app.modules.auth import services
from app.modules.auth.schemas import PortalUserInfo

router = APIRouter()


@router.get(
    "/auth/sso-callback",
    summary="门户 SSO 回调",
    description=(
        "门户登录后重定向至此端点，携带 ssoTokenId 参数。"
        "后端校验 token 后签发内部 JWT，通过 HttpOnly Cookie 返回前端。"
    ),
)
async def sso_callback(
    db: DBSession,
    sso_token_id: str = Query(..., alias="ssoTokenId", description="门户生成的 SSO Token ID"),
) -> RedirectResponse:
    """
    门户 SSO 回调处理：
    1. 调门户远程接口校验 token
    2. 查找或创建本地用户
    3. 签发内部 JWT
    4. 设置 HttpOnly Secure Cookie 并重定向到前端
    """
    # 1. 校验门户 token，获取用户信息
    portal_info = await services.validate_sso_token(sso_token_id)

    if not portal_info.user_id:
        return RedirectResponse(
            url=f"{settings.SSO_LOGIN_REDIRECT_URL}?error=invalid_token",
            status_code=HTTP_302_FOUND,
        )

    # 2. 查找或创建本地用户
    user = await services.find_or_create_user(db, portal_info.user_id, portal_info)

    # 检查用户状态
    services.check_user_status(user)

    # 3. 更新最后登录时间
    await services.update_last_login(db, user)

    # 4. 签发内部 JWT
    internal_token = create_access_token(
        subject=user.id,
        extra_claims={"username": user.username, "portal_id": user.portal_user_id},
    )

    # 5. 通过 HttpOnly Cookie 返回 JWT，重定向到前端
    response = RedirectResponse(url=settings.SSO_LOGIN_REDIRECT_URL, status_code=HTTP_302_FOUND)
    response.set_cookie(
        key="mapToken",
        value=internal_token,
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return response
