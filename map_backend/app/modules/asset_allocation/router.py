"""
modules/asset_allocation/router.py — 资配业务路由
"""
from fastapi import APIRouter, Query

from app.dependencies import CurrentUserID, DBSession, PortalUserID
from app.modules.asset_allocation import services

router = APIRouter()


@router.get("/asset-classes", summary="获取资产类别配置列表")
async def list_asset_classes(db: DBSession, _user_id: PortalUserID):
    data = await services.list_asset_classes(db)
    return {"data": data}


@router.get("/drafts", summary="获取当前用户草稿列表")
async def list_drafts(
    db: DBSession,
    user_id: PortalUserID,
    status: str | None = Query(default=None, description="按状态过滤"),
):
    data = await services.list_user_drafts(db, user_id, status=status)
    return {"data": data}


@router.get("/drafts/{draft_id}", summary="获取草稿详情")
async def get_draft(draft_id: int, db: DBSession, user_id: PortalUserID):
    data = await services.get_draft_detail(db, draft_id, user_id)
    return {"data": data}


@router.post("/drafts/calculate", summary="计算 SAA 权重并保存草稿")
async def calculate_saa(body: dict, db: DBSession, user_id: PortalUserID):
    """body: {risk_level: int, total_amount: float, constraints?: dict, notes?: str}"""
    data = await services.run_saa_calculation(db, user_id, body)
    await db.commit()
    return {"data": data}


@router.post("/drafts/{draft_id}/submit", summary="提交草稿至审批")
async def submit_draft(draft_id: int, db: DBSession, user_id: PortalUserID):
    data = await services.submit_for_approval(db, user_id, draft_id)
    await db.commit()
    return {"data": data}


@router.post("/drafts/{draft_id}/approve", summary="审批通过")
async def approve_draft(draft_id: int, db: DBSession, approver_id: CurrentUserID):
    data = await services.approve_draft(db, approver_id, draft_id)
    await db.commit()
    return {"data": data}


@router.post("/drafts/{draft_id}/reject", summary="审批拒绝")
async def reject_draft(draft_id: int, body: dict, db: DBSession, approver_id: CurrentUserID):
    reason = body.get("reason", "")
    data = await services.reject_draft(db, approver_id, draft_id, reason)
    await db.commit()
    return {"data": data}
