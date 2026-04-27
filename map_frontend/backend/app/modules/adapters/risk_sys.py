"""
modules/adapters/risk_sys.py — 风控系统适配器（骨架）
"""
from app.modules.adapters.base import BaseAdapter


class RiskSystemAdapter(BaseAdapter):
    service_name = "RiskSystem"
    base_url = ""  # 从 settings 中读取

    def _parse_response(self, raw: dict):
        raise NotImplementedError

    async def get_risk_metrics(self, portfolio_id: str) -> dict:
        raw = await self._get(f"/risk/{portfolio_id}/metrics")
        return self._parse_response(raw)
