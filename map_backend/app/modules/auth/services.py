"""
app/modules/auth/services.py — SSO 认证业务逻辑
包含：门户 token 校验、用户查找/创建、登录态更新。
"""
from datetime import UTC, datetime

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ExternalServiceException
from app.modules.auth.models import MapUser, UserStatus
from app.modules.auth.schemas import PortalUserInfo


# ── 门户 Token 校验 ───────────────────────────────────────────────────────────

async def validate_sso_token(token_id: str) -> PortalUserInfo:
    """
    调用门户远程接口校验 ssoTokenId，返回解析后的用户信息。
    门户接口：GET {SSO_VALIDATE_URL}?tokenId=xxx
    """
    try:
        async with httpx.AsyncClient(timeout=settings.EXTERNAL_HTTP_TIMEOUT) as client:
            resp = await client.get(
                settings.SSO_VALIDATE_URL,
                params={"tokenId": token_id},
            )
            resp.raise_for_status()
            raw = resp.json()
    except httpx.TimeoutException as exc:
        raise ExternalServiceException("门户 token 校验超时") from exc
    except httpx.HTTPStatusError as exc:
        raise ExternalServiceException(f"门户 token 校验失败: HTTP {exc.response.status_code}") from exc
    except httpx.RequestError as exc:
        raise ExternalServiceException(f"门户 token 校验请求失败: {exc}") from exc

    # 解析门户返回的用户信息
    # 具体字段结构需与门户确认，此处按常见格式适配
    user_info = _parse_portal_response(raw)
    user_info.raw_data = raw
    return user_info


def _parse_portal_response(raw: dict) -> PortalUserInfo:
    """
    将门户返回的原始 JSON 解析为 PortalUserInfo。
    需根据门户实际返回格式调整映射关系。
    """
    # 常见门户返回格式适配 — 按实际返回结构调整
    return PortalUserInfo(
        user_id=str(
            raw.get("userId")
            or raw.get("user_id")
            or raw.get("uid")
            or raw.get("id", "")
        ),
        username=raw.get("userName") or raw.get("username") or raw.get("loginName") or "",
        display_name=raw.get("displayName") or raw.get("display_name") or raw.get("name") or None,
        email=raw.get("email") or None,
        department=raw.get("department") or raw.get("deptName") or None,
    )


# ── 用户查找 / 创建 ──────────────────────────────────────────────────────────


def _parse_portal_user_id(portal_user_id: str) -> int:
    """
    安全地将门户用户 ID 转为整数。
    非数字字符串会抛出 UnauthenticatedException。
    """
    try:
        return int(portal_user_id)
    except (ValueError, TypeError):
        from app.core.exceptions import UnauthenticatedException
        raise UnauthenticatedException(f"门户返回的 user_id 格式无效: {portal_user_id}")


async def find_or_create_user(
    db: AsyncSession,
    portal_user_id: str,
    portal_info: PortalUserInfo,
) -> MapUser:
    """
    按门户用户 ID 查找本地用户，不存在则自动创建（首次登录注册）。
    """
    pid = _parse_portal_user_id(portal_user_id)
    stmt = select(MapUser).where(MapUser.portal_user_id == pid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is not None:
        return user

    # 首次登录：自动创建本地用户
    user = MapUser(
        portal_user_id=pid,
        username=portal_info.username or f"portal_{portal_user_id}",
        display_name=portal_info.display_name,
        email=portal_info.email,
        department=portal_info.department,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_last_login(db: AsyncSession, user: MapUser) -> None:
    """更新用户最近登录时间。"""
    user.last_login_at = datetime.now(UTC)
    db.add(user)
    await db.commit()


async def get_user_by_id(db: AsyncSession, user_id: int) -> MapUser | None:
    """按本地用户 ID 查询。"""
    stmt = select(MapUser).where(MapUser.id == user_id, MapUser.is_deleted == 0)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def check_user_status(user: MapUser) -> None:
    """
    检查用户状态，禁用用户抛异常。
    正常情况无返回值；禁用时抛出 PermissionDeniedException。
    """
    from app.core.exceptions import PermissionDeniedException

    if user.status != UserStatus.ACTIVE:
        raise PermissionDeniedException("用户已被禁用，请联系管理员")
