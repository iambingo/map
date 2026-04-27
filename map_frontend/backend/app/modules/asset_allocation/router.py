"""
modules/asset_allocation/router.py — 资配业务路由骨架
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/drafts", summary="获取资配草稿列表（占位）")
async def list_drafts():
    return {"data": [], "message": "asset_allocation module placeholder"}
