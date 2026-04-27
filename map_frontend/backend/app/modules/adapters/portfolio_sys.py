"""
modules/adapters/portfolio_sys.py — 组合系统适配器

双模式设计：
  MockPortfolioAdapter   — 本地 Mock，返回固定仿真头寸数据，用于开发/测试
  PortfolioSystemAdapter — 真实 HTTP 适配器，对接组合系统，继承 BaseAdapter
                           配置 PORTFOLIO_SYS_URL 后自动启用

调用方（workspace/router.py）通过工厂函数 get_portfolio_adapter() 获取当前实例，
无需关心底层是 Mock 还是真实 HTTP。
"""
from __future__ import annotations

import logging
import random
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

from app.core.config import settings
from app.modules.adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


# ── 内部数据模型（MAP 标准头寸结构） ──────────────────────────────────────────


class AssetPosition(BaseModel):
    """单个资产类别的持仓快照。"""

    asset_class: str
    ratio: float          # 占总净值比例，0-1
    market_value: float   # 市值（元）
    currency: str = "CNY"
    change_1d: float = 0.0  # 日涨跌幅


class PortfolioPositionData(BaseModel):
    """组合系统返回的标准头寸快照，由 _parse_response() 翻译而来。"""

    portfolio_id: str
    snapshot_at: datetime
    total_nav: float
    positions: dict[str, AssetPosition]  # key = asset_class


# ── Mock 适配器 ───────────────────────────────────────────────────────────────


class MockPortfolioAdapter:
    """
    本地 Mock：不发起任何网络请求，直接返回仿真头寸数据。
    适用于：开发阶段 / CI 测试 / 真实系统未部署时。

    Mock 数据说明（刻意让股票仓位低于 TAA overweight 指引下限，触发 HIGH 调仓紧急度）：
      equity    42%  ←  TAA overweight 目标范围 [55%, 75%]，偏低 -13pp
      bond      38%  ←  TAA neutral    目标范围 [40%, 55%]，略低  -2pp
      commodity  8%  ←  无 TAA 指引，中性展示
      cash      12%  ←  余量
    """

    service_name = "MockPortfolioSystem"

    async def get_all_positions(self, portfolio_id: str = "MAP-MAIN-001") -> PortfolioPositionData:
        logger.debug("MockPortfolioAdapter: returning simulated positions for %s", portfolio_id)
        total_nav = 1_000_000_000.0  # 10亿
        raw_positions = {
            "equity":    (0.42, random.uniform(-0.012, 0.018)),
            "bond":      (0.38, random.uniform(-0.005, 0.008)),
            "commodity": (0.08, random.uniform(-0.020, 0.030)),
            "cash":      (0.12, 0.0),
        }
        positions = {
            cls: AssetPosition(
                asset_class=cls,
                ratio=ratio,
                market_value=round(ratio * total_nav, 2),
                change_1d=round(chg, 4),
            )
            for cls, (ratio, chg) in raw_positions.items()
        }
        return PortfolioPositionData(
            portfolio_id=portfolio_id,
            snapshot_at=datetime.now(UTC),
            total_nav=total_nav,
            positions=positions,
        )


# ── 真实 HTTP 适配器（生产就绪后切换） ────────────────────────────────────────


class PortfolioSystemAdapter(BaseAdapter):
    """
    对接真实组合系统的 HTTP 适配器。
    继承 BaseAdapter，自动获得超时保护与指数退避重试。
    激活方式：在 .env 设置 PORTFOLIO_SYS_URL=http://your-system/api
    """

    service_name = "PortfolioSystem"

    def __init__(self) -> None:
        # base_url 从配置读取，避免硬编码
        self.base_url = getattr(settings, "PORTFOLIO_SYS_URL", "")
        super().__init__()

    def _parse_response(self, raw: dict) -> PortfolioPositionData:
        """
        将外部系统原始 JSON 翻译为 MAP 内部 PortfolioPositionData。
        外部字段名变更时只需修改此处，不污染上层业务代码。
        """
        positions: dict[str, AssetPosition] = {}
        for item in raw.get("holdings", []):
            cls = item.get("asset_class", "unknown")
            positions[cls] = AssetPosition(
                asset_class=cls,
                ratio=float(item.get("weight", 0)),
                market_value=float(item.get("market_value", 0)),
                currency=item.get("currency", "CNY"),
                change_1d=float(item.get("daily_return", 0)),
            )
        return PortfolioPositionData(
            portfolio_id=raw.get("portfolio_id", ""),
            snapshot_at=datetime.fromisoformat(raw.get("as_of", datetime.now(UTC).isoformat())),
            total_nav=float(raw.get("total_nav", 0)),
            positions=positions,
        )

    async def get_all_positions(self, portfolio_id: str = "MAP-MAIN-001") -> PortfolioPositionData:
        raw = await self._get(f"/portfolios/{portfolio_id}/positions")
        return self._parse_response(raw)


# ── 工厂函数（调用方通过此函数获取当前有效适配器） ─────────────────────────────


def get_portfolio_adapter() -> MockPortfolioAdapter | PortfolioSystemAdapter:
    """
    根据配置决定返回 Mock 还是真实适配器。
    若 PORTFOLIO_SYS_URL 已配置且非空，使用真实适配器；否则使用 Mock。
    """
    portfolio_url = getattr(settings, "PORTFOLIO_SYS_URL", "")
    if portfolio_url:
        logger.info("Using real PortfolioSystemAdapter: %s", portfolio_url)
        return PortfolioSystemAdapter()
    logger.debug("Using MockPortfolioAdapter (PORTFOLIO_SYS_URL not configured)")
    return MockPortfolioAdapter()
