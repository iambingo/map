"""
modules/asset_allocation/services.py — 资配业务编排层（骨架）
协调 domain 规则引擎与 repository 的存取操作。
"""


async def run_saa_calculation(user_id: int, params: dict) -> dict:
    raise NotImplementedError


async def submit_for_approval(user_id: int, draft_id: int) -> dict:
    raise NotImplementedError
