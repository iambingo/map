"""
modules/adapters/base.py — 防腐层拦截基类
所有外部 HTTP Adapter 必须继承此类，强制实现超时与重试。
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, TypeVar

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import ErrorCode, ExternalServiceException

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseAdapter(ABC):
    """
    外部系统 HTTP 适配器基类。
    子类仅需实现 _parse_response()，框架自动注入超时与重试。
    """

    base_url: str = ""
    service_name: str = "external"

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=settings.EXTERNAL_HTTP_TIMEOUT,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        reraise=True,
    )
    async def _get(self, path: str, **kwargs: Any) -> dict:
        try:
            resp = await self._client.get(path, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except httpx.TimeoutException as exc:
            raise ExternalServiceException(
                f"{self.service_name} request timed out",
                error_code=ErrorCode.EXTERNAL_TIMEOUT,
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceException(
                f"{self.service_name} responded with {exc.response.status_code}",
                error_code=ErrorCode.EXTERNAL_BAD_RESPONSE,
            ) from exc

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        reraise=True,
    )
    async def _post(self, path: str, json: dict, **kwargs: Any) -> dict:
        try:
            resp = await self._client.post(path, json=json, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except httpx.TimeoutException as exc:
            raise ExternalServiceException(
                f"{self.service_name} request timed out",
                error_code=ErrorCode.EXTERNAL_TIMEOUT,
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise ExternalServiceException(
                f"{self.service_name} responded with {exc.response.status_code}",
                error_code=ErrorCode.EXTERNAL_BAD_RESPONSE,
            ) from exc

    @abstractmethod
    def _parse_response(self, raw: dict) -> Any:
        """将外部原始 JSON 翻译为 MAP 内部 Pydantic 模型。"""

    async def aclose(self) -> None:
        await self._client.aclose()
