"""
modules/committee/mixed_services.py — 混合投委会问卷提交业务逻辑层

层次职责划分：
  ┌─ 纯函数区（无 I/O，可直接单元测试） ──────────────────────────────────────┐
  │  _resolve_session_code()    解析/生成当前活跃会期标识                     │
  └───────────────────────────────────────────────────────────────────────────┘
  ┌─ 服务函数区（async，协调 DB I/O 与领域逻辑） ──────────────────────────────┐
  │  submit_mixed_viewpoint()   幂等提交/覆盖资配观点（核心入口）              │
  │  get_session_submissions()  查询当前会期所有提交（管理视角）               │
  └───────────────────────────────────────────────────────────────────────────┘

设计原则：
  - meeting_id 对前端透明：前端只传 viewpoint_json，不感知任何内部 ID
  - session_code 由后端自动生成（基于当前日期推算季度），前端可选传入覆盖
  - 幂等设计：同一 (session_code, submitter_id) 重复提交覆盖而非新建
"""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.committee.mixed_models import (
    IcMixedQuestionnaireSubmission,
    MixedSubmissionStatus,
)
from app.modules.committee.mixed_schemas import (
    HistorySessionItem,
    MixedHistoryResponse,
    MixedRemindRequest,
    MixedSubmissionListResponse,
    MixedSubmissionResponse,
    SubmitMixedViewpointRequest,
)


# ══════════════════════════════════════════════════════════════════════════════
#  纯函数区 — 零外部依赖，零 I/O
# ══════════════════════════════════════════════════════════════════════════════


def _resolve_session_code(requested: str | None) -> str:
    """
    解析会期标识。

    逻辑：
    - 若调用方显式传入 session_code，直接使用（前端高级用法 / 管理员补录）
    - 否则根据当前日期推算季度，格式为 YYYYQN（如 "2026Q2"）
      - Q1: 1-3月, Q2: 4-6月, Q3: 7-9月, Q4: 10-12月

    此函数纯粹计算，无任何 I/O，可直接单元测试。
    """
    if requested and requested.strip():
        return requested.strip()

    now = datetime.now(UTC)
    quarter = (now.month - 1) // 3 + 1
    return f"{now.year}Q{quarter}"


# ══════════════════════════════════════════════════════════════════════════════
#  服务函数区 — 异步，协调 DB I/O 与领域逻辑
# ══════════════════════════════════════════════════════════════════════════════


async def submit_mixed_viewpoint(
    db: AsyncSession,
    payload: SubmitMixedViewpointRequest,
    submitter_id: int,
) -> IcMixedQuestionnaireSubmission:
    """
    幂等提交/覆盖混合投委会资配观点（核心服务入口）。

    执行步骤
    --------
    1. 解析会期标识（前端未传时自动推算当前季度）
    2. 查询该 (session_code, submitter_id) 是否已有提交记录
    3. 存在则覆盖 questionnaire_json 和 submitted_at；不存在则新建
    4. 状态统一置为 SUBMITTED（确认提交）

    幂等性保证：
      唯一索引 uq_ic_mixed_qs_session_submitter (session_code, submitter_id)
      服务层先查后写，避免依赖数据库异常做流程控制。

    对前端透明：
      - 前端只需传 viewpoint_json（以及可选的 session_code）
      - submitter_id 从 JWT 中解析，不由前端传入
      - 返回值中不含 meeting_id 等内部字段

    Returns:
        已创建或已更新的 IcMixedQuestionnaireSubmission ORM 对象
    """
    session_code = _resolve_session_code(payload.session_code)
    now = datetime.now(UTC)

    # 幂等查询：是否已存在本人本会期的提交
    stmt = select(IcMixedQuestionnaireSubmission).where(
        IcMixedQuestionnaireSubmission.session_code == session_code,
        IcMixedQuestionnaireSubmission.submitter_id == submitter_id,
        IcMixedQuestionnaireSubmission.is_deleted == 0,
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()

    if existing:
        # 覆盖：更新问卷内容、提交时间和状态
        existing.questionnaire_json = payload.viewpoint_json
        existing.submitted_at = now
        existing.status = MixedSubmissionStatus.SUBMITTED
        await db.flush()
        await db.refresh(existing)
        return existing

    # 新建：首次提交
    record = IcMixedQuestionnaireSubmission(
        session_code=session_code,
        submitter_id=submitter_id,
        status=MixedSubmissionStatus.SUBMITTED,
        questionnaire_json=payload.viewpoint_json,
        submitted_at=now,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get_session_submissions(
    db: AsyncSession,
    session_code: str | None = None,
) -> MixedSubmissionListResponse:
    """
    查询指定会期（或当前会期）所有已提交的问卷记录。
    供管理员/秘书视角查看提交进度。

    Returns:
        MixedSubmissionListResponse 含会期标识、总数和提交列表
    """
    resolved_code = _resolve_session_code(session_code)

    stmt = (
        select(IcMixedQuestionnaireSubmission)
        .where(
            IcMixedQuestionnaireSubmission.session_code == resolved_code,
            IcMixedQuestionnaireSubmission.is_deleted == 0,
            IcMixedQuestionnaireSubmission.status == MixedSubmissionStatus.SUBMITTED,
        )
        .order_by(IcMixedQuestionnaireSubmission.submitted_at.asc())
    )
    rows: list[IcMixedQuestionnaireSubmission] = list(
        (await db.execute(stmt)).scalars().all()
    )

    return MixedSubmissionListResponse(
        session_code=resolved_code,
        total=len(rows),
        submissions=[MixedSubmissionResponse.model_validate(r) for r in rows],
    )


async def get_history_sessions(
    db: AsyncSession,
    limit: int = 10,
) -> MixedHistoryResponse:
    """
    查询最近 N 期会期及其评分聚合数据。

    对每期会期：
    1. 查询所有已提交问卷
    2. 从 questionnaire_json 中提取 section_a 的资产评分
    3. 计算每项资产的 avg/max/min

    Returns:
        历史会期列表，按 session_code 降序排列
    """
    # 获取所有不同 session_code，按最新排序
    from sqlalchemy import distinct  # noqa: E402

    code_stmt = (
        select(distinct(IcMixedQuestionnaireSubmission.session_code))
        .where(
            IcMixedQuestionnaireSubmission.is_deleted == 0,
            IcMixedQuestionnaireSubmission.status == MixedSubmissionStatus.SUBMITTED,
        )
        .order_by(IcMixedQuestionnaireSubmission.session_code.desc())
        .limit(limit)
    )
    codes: list[str] = list(
        (await db.execute(code_stmt)).scalars().all()
    )

    sessions: list[HistorySessionItem] = []
    for code in codes:
        stmt = (
            select(IcMixedQuestionnaireSubmission)
            .where(
                IcMixedQuestionnaireSubmission.session_code == code,
                IcMixedQuestionnaireSubmission.is_deleted == 0,
                IcMixedQuestionnaireSubmission.status == MixedSubmissionStatus.SUBMITTED,
            )
        )
        rows: list[IcMixedQuestionnaireSubmission] = list(
            (await db.execute(stmt)).scalars().all()
        )

        # 聚合 section_a 评分
        scores: dict[str, dict[str, float | int]] = {}
        if rows:
            asset_scores: dict[str, list[int]] = {}
            for row in rows:
                qj = row.questionnaire_json or {}
                section_a = qj.get("section_a", {})
                if not isinstance(section_a, dict):
                    continue
                for asset, score in section_a.items():
                    if isinstance(score, (int, float)):
                        asset_scores.setdefault(asset, []).append(int(score))

            for asset, vals in asset_scores.items():
                if vals:
                    scores[asset] = {
                        "avg": round(sum(vals) / len(vals), 1),
                        "max": max(vals),
                        "min": min(vals),
                        "count": len(vals),
                    }

        sessions.append(
            HistorySessionItem(
                session_code=code,
                submitted_count=len(rows),
                scores=scores,
            )
        )

    return MixedHistoryResponse(sessions=sessions)


async def send_reminder(
    db: AsyncSession,
    payload: MixedRemindRequest,
    sender_id: int,
) -> None:
    """
    发送催办通知给指定委员。

    当前实现为占位逻辑：记录日志即可，后续可接入消息中心（SSE/RocketMQ）。

    TODO: 接入消息中心后，改为：
      1. 检查该委员是否已提交（未提交才催办）
      2. 通过 SSE 推送站内消息
      3. 可选：发送邮件/企微/钉钉通知
    """
    session_code = _resolve_session_code(payload.session_code)
    # TODO: 接入真实消息推送渠道
    print(
        f"[REMINDER] sender={sender_id} → member={payload.member_name} "
        f"(session={session_code})"
    )
