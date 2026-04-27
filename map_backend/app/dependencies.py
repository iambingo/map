"""
dependencies.py — FastAPI 全局依赖注入
将 core 层的原始生成器/工具包装为 Annotated 类型，统一供路由函数使用。
"""
from typing import Annotated

from fastapi import Cookie, Depends, Header, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db_tdsql import get_db
from app.core.security import decode_access_token

# ── DB Session ────────────────────────────────────────────────────────────────

DBSession = Annotated[AsyncSession, Depends(get_db)]

# ── 当前用户身份（支持 Bearer Header 或 HttpOnly Cookie） ──────────────────────


def _extract_user_id_from_token(token: str) -> int:
    """从 JWT token 中解析用户 ID。"""
    try:
        payload = decode_access_token(token)
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
        )


async def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
    map_token: Annotated[str | None, Cookie()] = None,
) -> int:
    """
    从请求头 Authorization: Bearer <token> 或 HttpOnly Cookie (mapToken) 中解析用户 ID。
    开发/DEBUG 模式下无 token 时回退 user_id=1，便于本地直连联调。
    路由函数使用示例：
        async def endpoint(user_id: CurrentUserID): ...
    """
    # 优先使用 Bearer Header
    if authorization and authorization.startswith("Bearer "):
        try:
            return _extract_user_id_from_token(authorization.removeprefix("Bearer ").strip())
        except HTTPException:
            if not settings.DEBUG:
                raise
    # 回退到 HttpOnly Cookie
    if map_token:
        try:
            return _extract_user_id_from_token(map_token)
        except HTTPException:
            if not settings.DEBUG:
                raise
    # 本地直连兜底
    if settings.DEBUG or settings.APP_ENV == "development":
        return 1
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication",
    )


CurrentUserID = Annotated[int, Depends(get_current_user_id)]


async def get_portal_user_id(
    authorization: Annotated[str | None, Header()] = None,
    map_token: Annotated[str | None, Cookie()] = None,
) -> int:
    """
    门户 BFF 快照专用：优先解析 JWT（Header 或 Cookie）；在 DEBUG 且无合法 Token 时回退 user_id=1，
    便于本地前端直连联调（生产环境仍须携带有效 Bearer）。
    """
    if authorization and authorization.startswith("Bearer "):
        try:
            return _extract_user_id_from_token(authorization.removeprefix("Bearer ").strip())
        except HTTPException:
            if not settings.DEBUG:
                raise
    if map_token:
        try:
            return _extract_user_id_from_token(map_token)
        except HTTPException:
            if not settings.DEBUG:
                raise
    # 本地默认 APP_ENV=development，便于未配 JWT 时与前端 Vite 联调
    if settings.DEBUG or settings.APP_ENV == "development":
        return 1
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication",
    )


PortalUserID = Annotated[int, Depends(get_portal_user_id)]
