"""
modules/orchestrator/router.py — 跨域发令枪路由骨架
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/commands", summary="登记并分发跨域指令（占位）")
async def dispatch_command(body: dict):
    return {"data": {}, "message": "orchestrator module placeholder"}
