"""
modules/committee/router.py — 投委会决策模块 API 路由

端点清单
--------
  GET  /page-context                   投委会视图只读上下文（最近已发布决议 + 投票摘要）
  POST /meetings                       创建会议（DRAFT 状态）
  POST /meetings/{meeting_id}/submit-vote   提交 / 覆盖投票（幂等）
  POST /meetings/{meeting_id}/publish  触发计票聚合并发布决议
"""
from fastapi import APIRouter

from app.dependencies import DBSession, PortalUserID
from app.modules.committee import services
from app.modules.committee.schemas import (
    CommitteePageContextResponse,
    CreateMeetingRequest,
    MeetingResponse,
    PublishResponse,
    ResolutionResponse,
    SubmitVoteRequest,
    VoteRecordResponse,
)

router = APIRouter()


@router.get(
    "/page-context",
    response_model=CommitteePageContextResponse,
    summary="投委会视图只读上下文",
    description=(
        "供前端投委会 Tab 首屏使用：ic_resolutions 中 id 最小的一条决议、会议元数据、"
        "本场会议投票提交列表（不含 vote_json 全文）。\n\n"
        "无数据时返回空对象，不 404。鉴权与 POST 相同：使用 Portal 联调策略（开发环境可不带 Token）。"
    ),
)
async def get_committee_page_context(
    db: DBSession,
    _user_id: PortalUserID,
) -> CommitteePageContextResponse:
    return await services.get_committee_page_context(db)


@router.post(
    "/meetings",
    response_model=MeetingResponse,
    status_code=201,
    summary="创建投委会会议",
    description=(
        "新建一场投委会会议，初始状态为 **DRAFT**。\n\n"
        "`meeting_code` 全局唯一，重复提交将返回 409。"
    ),
)
async def create_meeting(
    body: CreateMeetingRequest,
    db: DBSession,
    user_id: PortalUserID,
) -> MeetingResponse:
    meeting = await services.create_meeting(db, body, user_id)
    return MeetingResponse.model_validate(meeting)


@router.post(
    "/meetings/{meeting_id}/submit-vote",
    response_model=VoteRecordResponse,
    status_code=200,
    summary="提交投票",
    description=(
        "委员提交本场会议的投票内容（幂等接口，允许覆盖）。\n\n"
        "- 首票提交时，会议状态自动从 `DRAFT` 推进到 `VOTING`。\n"
        "- 决议已发布（`PUBLISHED`）后禁止再提交。\n\n"
        "`vote.choice_items` 用于众数计票，`vote.numeric_items` 用于均值计票。"
    ),
)
async def submit_vote(
    meeting_id: int,
    body: SubmitVoteRequest,
    db: DBSession,
    user_id: PortalUserID,
) -> VoteRecordResponse:
    record = await services.submit_vote(db, meeting_id, user_id, body.vote)
    return VoteRecordResponse.model_validate(record)


@router.post(
    "/meetings/{meeting_id}/publish",
    response_model=PublishResponse,
    status_code=200,
    summary="触发计票聚合并发布决议",
    description=(
        "对处于 **VOTING** 状态的会议执行计票并发布决议（不可逆操作）。\n\n"
        "**FICC 计票规则**\n"
        "- `choice_items` → 各选项取 **众数 (Mode)**，平票时取字典序最小值\n"
        "- `numeric_items` → 各指标取 **算术均值 (Mean)**，并附带标准差、极值统计\n\n"
        "响应中同时返回更新后的会议信息与完整决议内容。"
    ),
)
async def publish_meeting(
    meeting_id: int,
    db: DBSession,
    user_id: PortalUserID,
) -> PublishResponse:
    meeting, resolution = await services.aggregate_ficc_resolution(
        db, meeting_id, user_id
    )
    return PublishResponse(
        meeting=MeetingResponse.model_validate(meeting),
        resolution=ResolutionResponse.model_validate(resolution),
    )
