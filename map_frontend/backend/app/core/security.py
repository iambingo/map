"""
core/security.py — JWT 签发与校验工具
⚠️  禁止在此处编写用户管理等业务逻辑；仅封装令牌的生成/解析能力。
"""
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ── 密码哈希 ──────────────────────────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT ───────────────────────────────────────────────────────────────────────

ALGORITHM = "HS256"


def create_access_token(
    subject: str | int,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    签发 Access Token。
    :param subject:  通常为 user_id（字符串或整数）。
    :param extra_claims: 追加写入 payload 的自定义字段（如 role、tenant_id）。
    :param expires_delta: 自定义过期时长；默认使用配置值。
    """
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    校验并解码 Access Token。
    :raises JWTError: 令牌无效或已过期。
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
