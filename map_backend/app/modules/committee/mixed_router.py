"""
modules/committee/mixed_router.py — 混合投委会问卷提交路由层

端点：
  POST /submit       提交/覆盖资配观点（前端核心入口）
  GET  /sessions     查询指定会期所有提交（管理员视角，含问卷评分明细）
  GET  /sessions/history  查询历史会期列表及每期聚合评分
  POST /remind       向指定委员发送催办通知
"""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.dependencies import CurrentUserID, DBSession
from app.modules.committee.mixed_schemas import (
    MixedHistoryResponse,
    MixedRemindRequest,
    MixedSubmissionListResponse,
    MixedSubmissionResponse,
    SubmitMixedViewpointRequest,
)
from app.modules.committee.mixed_services import (
    get_history_sessions,
    get_session_submissions,
    send_reminder,
    submit_mixed_viewpoint,
)

router = APIRouter(prefix="/mixed", tags=["混合投委会-问卷"])


# ---------------------------------------------------------------------------
# 端点
# ---------------------------------------------------------------------------


@router.post(
    "/submit",
    response_model=MixedSubmissionResponse,
    summary="提交/覆盖混合投委会资配观点",
    description=(
        "幂等提交：同一 (session_code, submitter_id) 重复调用将覆盖上一次提交。\n\n"
        "- `session_code` 可不传，后端自动推算当前季度（格式 YYYYQN）\n"
        "- `submitter_id` 从 JWT token 中自动解析，无需前端传入"
    ),
)
async def submit_viewpoint(
    payload: SubmitMixedViewpointRequest,
    db: DBSession,
    submitter_id: CurrentUserID,
) -> MixedSubmissionResponse:
    record = await submit_mixed_viewpoint(db=db, payload=payload, submitter_id=submitter_id)
    return MixedSubmissionResponse.model_validate(record)


@router.get(
    "/sessions",
    response_model=MixedSubmissionListResponse,
    summary="查询会期所有提交（管理员）",
    description="不传 session_code 时默认查询当前季度会期的所有提交记录，含完整问卷评分明细。",
)
async def list_session_submissions(
    db: DBSession,
    session_code: str | None = Query(None, description="会期标识，如 2026Q2；不传则取当前季度"),
) -> MixedSubmissionListResponse:
    return await get_session_submissions(db=db, session_code=session_code)


@router.get(
    "/sessions/history",
    response_model=MixedHistoryResponse,
    summary="查询历史会期及聚合评分",
    description="返回所有历史会期列表，每期包含委员评分聚合数据（均值、最高/最低分等）。",
)
async def list_history_sessions(
    db: DBSession,
    limit: int = Query(10, ge=1, le=50, description="返回最近 N 期，默认 10"),
) -> MixedHistoryResponse:
    return await get_history_sessions(db=db, limit=limit)


@router.post(
    "/remind",
    summary="向指定委员发送催办通知",
    description="发送催办提醒给尚未提交问卷的委员。",
)
async def remind_member(
    payload: MixedRemindRequest,
    db: DBSession,
    sender_id: CurrentUserID,
) -> dict:
    await send_reminder(db=db, payload=payload, sender_id=sender_id)
    return {"ok": True, "message": "催办通知已发送"}
