"""
core/exceptions.py — 全局异常体系
定义 MAP 统一错误码与异常类，由 main.py 注册异常处理器。
⚠️  禁止在此处编写任何业务逻辑。
"""
from enum import IntEnum
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse


# ── 错误码枚举 ────────────────────────────────────────────────────────────────


class ErrorCode(IntEnum):
    # 通用
    UNKNOWN = 10000
    VALIDATION_ERROR = 10001
    NOT_FOUND = 10002
    PERMISSION_DENIED = 10003
    UNAUTHENTICATED = 10004
    RATE_LIMITED = 10005

    # 外部系统
    EXTERNAL_TIMEOUT = 20001
    EXTERNAL_UNAVAILABLE = 20002
    EXTERNAL_BAD_RESPONSE = 20003

    # 业务
    BUSINESS_RULE_VIOLATION = 30001
    STALE_SNAPSHOT = 30002
    TASK_ALREADY_PROCESSING = 30003


# ── 异常基类 ──────────────────────────────────────────────────────────────────


class MAPException(Exception):
    """MAP 系统所有受控异常的基类。"""

    http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: ErrorCode = ErrorCode.UNKNOWN

    def __init__(
        self,
        message: str = "Internal server error",
        detail: Any = None,
        *,
        error_code: ErrorCode | None = None,
    ) -> None:
        self.message = message
        self.detail = detail
        if error_code is not None:
            self.error_code = error_code
        super().__init__(message)


class NotFoundException(MAPException):
    http_status = status.HTTP_404_NOT_FOUND
    error_code = ErrorCode.NOT_FOUND

    def __init__(self, message: str = "Resource not found", detail: Any = None) -> None:
        super().__init__(message, detail)


class PermissionDeniedException(MAPException):
    http_status = status.HTTP_403_FORBIDDEN
    error_code = ErrorCode.PERMISSION_DENIED

    def __init__(self, message: str = "Permission denied", detail: Any = None) -> None:
        super().__init__(message, detail)


class UnauthenticatedException(MAPException):
    http_status = status.HTTP_401_UNAUTHORIZED
    error_code = ErrorCode.UNAUTHENTICATED

    def __init__(self, message: str = "Not authenticated", detail: Any = None) -> None:
        super().__init__(message, detail)


class ExternalServiceException(MAPException):
    """外部系统调用失败（超时 / 不可用 / 响应异常）。"""

    http_status = status.HTTP_502_BAD_GATEWAY
    error_code = ErrorCode.EXTERNAL_UNAVAILABLE

    def __init__(
        self,
        message: str = "External service error",
        detail: Any = None,
        *,
        error_code: ErrorCode = ErrorCode.EXTERNAL_UNAVAILABLE,
    ) -> None:
        super().__init__(message, detail, error_code=error_code)


class BusinessRuleException(MAPException):
    """业务规则校验失败。"""

    http_status = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = ErrorCode.BUSINESS_RULE_VIOLATION

    def __init__(self, message: str = "Business rule violation", detail: Any = None) -> None:
        super().__init__(message, detail)


# ── FastAPI 全局异常处理器 ─────────────────────────────────────────────────────


def _error_response(
    status_code: int,
    error_code: int,
    message: str,
    detail: Any = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error_code": error_code,
            "message": message,
            "detail": detail,
        },
    )


async def map_exception_handler(request: Request, exc: MAPException) -> JSONResponse:
    return _error_response(exc.http_status, exc.error_code, exc.message, exc.detail)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.UNKNOWN,
        "An unexpected error occurred.",
        str(exc) if __debug__ else None,
    )
