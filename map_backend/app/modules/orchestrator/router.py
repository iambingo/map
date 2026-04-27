"""
modules/orchestrator/router.py — 跨域指令路由

端点：
  POST /commands              登记并分发指令
  GET  /commands/{task_id}    查询指令执行状态（前端轮询）
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.dependencies import CurrentUserID, DBSession
from app.modules.orchestrator.commands import (
    COMMAND_ROUTES,
    get_command_status,
    register_and_dispatch,
)

router = APIRouter()


class DispatchCommandRequest(BaseModel):
    command_type: str = Field(..., description=f"指令类型，可选值: {list(COMMAND_ROUTES.keys())}")
    payload: dict = Field(default_factory=dict, description="指令业务参数")


@router.post(
    "/commands",
    summary="登记并分发跨域指令",
    status_code=status.HTTP_202_ACCEPTED,
)
async def dispatch_command(
    body: DispatchCommandRequest,
    db: DBSession,
    user_id: CurrentUserID,
):
    result = await register_and_dispatch(
        db=db,
        command_type=body.command_type,
        payload=body.payload,
        user_id=user_id,
    )
    await db.commit()
    return {"success": True, "data": result}


@router.get("/commands/{task_id}", summary="查询跨域指令执行状态")
async def get_command(task_id: int, db: DBSession, user_id: CurrentUserID):
    result = await get_command_status(db, task_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"task_id={task_id} 不存在")
    return {"success": True, "data": result}
