"""
dependencies.py — FastAPI 全局依赖注入
将 core 层的原始生成器/工具包装为 Annotated 类型，统一供路由函数使用。
"""
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db_tdsql import get_db
from app.core.security import decode_access_token

# ── DB Session ────────────────────────────────────────────────────────────────

DBSession = Annotated[AsyncSession, Depends(get_db)]

# ── 当前用户身份（Bearer JWT） ─────────────────────────────────────────────────


async def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
) -> int:
    """
    从请求头 Authorization: Bearer <token> 中解析用户 ID。
    路由函数使用示例：
        async def endpoint(user_id: CurrentUserID): ...
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_access_token(token)
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
        )


CurrentUserID = Annotated[int, Depends(get_current_user_id)]


async def get_portal_user_id(
    authorization: Annotated[str | None, Header()] = None,
) -> int:
    """
    门户 BFF 快照专用：优先解析 JWT；在 DEBUG 且无合法 Token 时回退 user_id=1，
    便于本地前端直连联调（生产环境仍须携带有效 Bearer）。
    """
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        try:
            return int(decode_access_token(token)["sub"])
        except (JWTError, KeyError, ValueError):
            if not settings.DEBUG:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is invalid or expired",
                )
    # 本地默认 APP_ENV=development，便于未配 JWT 时与前端 Vite 联调
    if settings.DEBUG or settings.APP_ENV == "development":
        return 1
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid Authorization header",
    )


PortalUserID = Annotated[int, Depends(get_portal_user_id)]
