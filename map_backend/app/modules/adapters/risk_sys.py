"""
modules/adapters/risk_sys.py — 风控系统适配器

双模式：
  MockRiskAdapter   — 本地 Mock，返回基础风控指标
  RiskSystemAdapter — 真实 HTTP 适配器，配置 RISK_SYS_URL 后启用
"""
from __future__ import annotations

import logging

from pydantic import BaseModel

from app.core.config import settings
from app.modules.adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class RiskMetrics(BaseModel):
    """风控指标标准结构。"""
    portfolio_id: str
    var_95: float = 0.0            # 95% VaR
    max_drawdown: float = 0.0      # 最大回撤
    sharpe_ratio: float = 0.0      # 夏普比率
    volatility: float = 0.0        # 年化波动率
    concentration: float = 0.0     # 集中度


class MockRiskAdapter:
    """本地 Mock 风控适配器，返回中性风控指标。"""

    service_name = "MockRiskSystem"

    async def get_risk_metrics(self, portfolio_id: str = "MAP-MAIN-001") -> RiskMetrics:
        logger.debug("MockRiskAdapter: returning simulated risk metrics for %s", portfolio_id)
        return RiskMetrics(
            portfolio_id=portfolio_id,
            var_95=0.02,
            max_drawdown=0.05,
            sharpe_ratio=1.2,
            volatility=0.12,
            concentration=0.15,
        )


class RiskSystemAdapter(BaseAdapter):
    """
    对接真实风控系统的 HTTP 适配器。
    激活方式：在 .env 设置 RISK_SYS_URL=http://your-risk-system/api
    """

    service_name = "RiskSystem"

    def __init__(self) -> None:
        self.base_url = settings.RISK_SYS_URL
        super().__init__()

    def _parse_response(self, raw: dict) -> RiskMetrics:
        return RiskMetrics(
            portfolio_id=raw.get("portfolio_id", ""),
            var_95=float(raw.get("var_95", 0)),
            max_drawdown=float(raw.get("max_drawdown", 0)),
            sharpe_ratio=float(raw.get("sharpe_ratio", 0)),
            volatility=float(raw.get("volatility", 0)),
            concentration=float(raw.get("concentration", 0)),
        )

    async def get_risk_metrics(self, portfolio_id: str = "MAP-MAIN-001") -> RiskMetrics:
        raw = await self._get(f"/risk/{portfolio_id}/metrics")
        return self._parse_response(raw)


def get_risk_adapter() -> MockRiskAdapter | RiskSystemAdapter:
    """根据配置决定返回 Mock 还是真实风控适配器。"""
    risk_url = settings.RISK_SYS_URL
    if risk_url:
        logger.info("Using real RiskSystemAdapter: %s", risk_url)
        return RiskSystemAdapter()
    logger.debug("Using MockRiskAdapter (RISK_SYS_URL not configured)")
    return MockRiskAdapter()


# ── 模块级单例 ───────────────────────────────────────────────────────────────

risk_adapter: MockRiskAdapter | RiskSystemAdapter = get_risk_adapter()
