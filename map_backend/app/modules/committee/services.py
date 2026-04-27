"""
modules/committee/services.py — 投委会业务逻辑层

层次职责划分：
  ┌─ 纯函数区（无 I/O，可直接单元测试） ──────────────────────────────────────┐
  │  _compute_mode()          分类选择题 → 众数                               │
  │  _compute_numeric_stats() 数值点位题 → 均值 / 标准差 / 极值               │
  │  _aggregate_votes()       整合两类计算，生成 aggregated_taa dict          │
  └───────────────────────────────────────────────────────────────────────────┘
  ┌─ 服务函数区（async，协调 DB I/O 与领域逻辑） ──────────────────────────────┐
  │  create_meeting()                                                         │
  │  submit_vote()            幂等提交（覆盖已有投票）                         │
  │  aggregate_ficc_resolution()  核心计票聚合 + 发布决议                     │
  └───────────────────────────────────────────────────────────────────────────┘
"""
import statistics
from collections import Counter
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleException, NotFoundException
from app.modules.committee.models import (
    IcMeeting,
    IcResolution,
    IcVoteRecord,
    MeetingStatus,
    MeetingType,
)
from app.modules.committee.schemas import (
    CommitteePageContextResponse,
    CommitteeVoteRow,
    CreateMeetingRequest,
    FiccVotePayload,
    MeetingResponse,
    ResolutionResponse,
)


# ══════════════════════════════════════════════════════════════════════════════
#  纯函数区 — 零外部依赖，零 I/O，极易单元测试
# ══════════════════════════════════════════════════════════════════════════════


def _compute_mode(values: list[str]) -> tuple[str, dict[str, int]]:
    """
    对字符串列表求众数。

    Returns:
        (winner, vote_counts)
        winner: 得票最多的选项；若首位平票则取字典序第一个（保证确定性）。
        vote_counts: 全部选项的得票统计。
    """
    if not values:
        raise ValueError("_compute_mode: 输入列表为空")
    counter = Counter(values)
    # most_common 内部按频次降序，相同频次保留插入顺序；
    # 追加 min() 确保平票时结果确定性
    max_count = counter.most_common(1)[0][1]
    tied_winners = sorted(k for k, v in counter.items() if v == max_count)
    return tied_winners[0], dict(counter)


def _compute_numeric_stats(values: list[float]) -> dict[str, Any]:
    """
    对数值列表计算统计指标（均值 / 标准差 / 最大 / 最小 / 个数）。
    标准差在样本数 < 2 时为 None（无统计意义）。
    """
    if not values:
        raise ValueError("_compute_numeric_stats: 输入列表为空")
    return {
        "mean": statistics.mean(values),
        "std": statistics.stdev(values) if len(values) >= 2 else None,
        "min": min(values),
        "max": max(values),
        "count": len(values),
    }


def _aggregate_votes(
    vote_records: list[IcVoteRecord],
    meeting_type: MeetingType,
) -> dict[str, Any]:
    """
    FICC / MIXED 核心计票算法（纯函数）：

    算法规则
    --------
    - choice_items  → 逐 key 收集所有委员的选项字符串 → **众数 (Mode)**
    - numeric_items → 逐 key 收集所有委员的数值预测   → **均值 (Mean)**

    容错机制
    --------
    - 若某委员未填写某 key，跳过该条目（不参与该 key 的统计）
    - numeric_items 中非合法浮点数值将被丢弃并记录缺失，不中断整体计算

    Returns:
        aggregated_taa dict，可直接写入 IcResolution.aggregated_taa
    """
    if not vote_records:
        raise BusinessRuleException("无有效投票记录，无法生成决议")

    # 按 key 分桶
    choice_buckets: dict[str, list[str]] = {}
    numeric_buckets: dict[str, list[float]] = {}

    for record in vote_records:
        payload: dict = record.vote_json or {}

        for key, val in payload.get("choice_items", {}).items():
            choice_buckets.setdefault(key, []).append(str(val))

        for key, val in payload.get("numeric_items", {}).items():
            try:
                numeric_buckets.setdefault(key, []).append(float(val))
            except (TypeError, ValueError):
                # 非法值：跳过该条目，不影响其他委员的数值参与统计
                pass

    # 计算众数
    choice_results: dict[str, Any] = {}
    for key, values in choice_buckets.items():
        winner, counts = _compute_mode(values)
        choice_results[key] = {
            "winner": winner,
            "vote_counts": counts,
        }

    # 计算均值（含辅助统计）
    numeric_results: dict[str, Any] = {}
    for key, values in numeric_buckets.items():
        numeric_results[key] = _compute_numeric_stats(values)

    return {
        "meeting_type": meeting_type.value,
        "total_voters": len(vote_records),
        "computed_at": datetime.now(UTC).isoformat(),
        "choice_results": choice_results,
        "numeric_results": numeric_results,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  服务函数区 — 异步，协调 DB I/O 与领域逻辑
# ══════════════════════════════════════════════════════════════════════════════


async def _fetch_active_meeting(db: AsyncSession, meeting_id: int) -> IcMeeting:
    """通用查询：获取未软删除的会议；不存在则抛 NotFoundException。"""
    stmt = select(IcMeeting).where(
        IcMeeting.id == meeting_id,
        IcMeeting.is_deleted == 0,
    )
    meeting = (await db.execute(stmt)).scalar_one_or_none()
    if meeting is None:
        raise NotFoundException(f"会议 {meeting_id} 不存在或已删除")
    return meeting


async def list_meetings(
    db: AsyncSession,
    *,
    status: str | None = None,
) -> list[IcMeeting]:
    """按创建时间倒序返回会议列表，可选按状态过滤。"""
    stmt = select(IcMeeting).where(IcMeeting.is_deleted == 0)
    if status:
        stmt = stmt.where(IcMeeting.status == MeetingStatus(status))
    stmt = stmt.order_by(IcMeeting.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_meeting(
    db: AsyncSession,
    payload: CreateMeetingRequest,
    user_id: int,
) -> IcMeeting:
    """
    创建一场新会议，初始状态为 DRAFT。
    meeting_code 唯一索引由数据库兜底；若重复将抛 IntegrityError（由全局处理器转化为 409）。
    """
    meeting = IcMeeting(
        meeting_code=payload.meeting_code,
        title=payload.title,
        type=MeetingType(payload.type.value),
        status=MeetingStatus.DRAFT,
        scheduled_at=payload.scheduled_at,
        created_by=user_id,
    )
    db.add(meeting)
    await db.flush()       # 触发 INSERT，获取自增 id
    await db.refresh(meeting)
    return meeting


async def submit_vote(
    db: AsyncSession,
    meeting_id: int,
    user_id: int,
    vote_payload: FiccVotePayload,
) -> IcVoteRecord:
    """
    提交或覆盖投票（幂等设计）。

    状态机副作用：
      DRAFT  → 自动推进到 VOTING（首票到达时打开投票窗口）
      VOTING → 正常接受投票
      PUBLISHED → 拒绝（终态保护）

    幂等性：同一 (meeting_id, user_id) 再次提交将覆盖 vote_json，不新建记录。
    """
    meeting = await _fetch_active_meeting(db, meeting_id)

    if meeting.status == MeetingStatus.PUBLISHED:
        raise BusinessRuleException("会议已发布决议，投票窗口已关闭")

    # 首票到达，推进状态
    if meeting.status == MeetingStatus.DRAFT:
        meeting.status = MeetingStatus.VOTING

    now = datetime.now(UTC)

    # 幂等查询：是否已存在该委员的投票记录
    existing_stmt = select(IcVoteRecord).where(
        IcVoteRecord.meeting_id == meeting_id,
        IcVoteRecord.user_id == user_id,
        IcVoteRecord.is_deleted == 0,
    )
    existing = (await db.execute(existing_stmt)).scalar_one_or_none()

    if existing:
        # 覆盖：更新投票内容和提交时间
        existing.vote_json = vote_payload.model_dump()
        existing.submitted_at = now
        await db.flush()
        await db.refresh(existing)
        return existing

    record = IcVoteRecord(
        meeting_id=meeting_id,
        user_id=user_id,
        vote_json=vote_payload.model_dump(),
        submitted_at=now,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def aggregate_ficc_resolution(
    db: AsyncSession,
    meeting_id: int,
    publisher_id: int,
) -> tuple[IcMeeting, IcResolution]:
    """
    FICC 计票聚合并发布决议（服务主入口）。

    执行步骤
    --------
    1. 校验会议存在且处于 VOTING 状态（DRAFT 未投票 / PUBLISHED 终态均拒绝）
    2. 读取全部有效投票记录（is_deleted = 0）
    3. 调用纯函数 _aggregate_votes() 完成众数 / 均值计算
    4. Upsert IcResolution（允许在发布前重新聚合，覆盖旧结果）
    5. 将会议状态推进到 PUBLISHED（终态，不可回滚）

    Returns:
        (updated_meeting, upserted_resolution)
    """
    meeting = await _fetch_active_meeting(db, meeting_id)

    if meeting.status == MeetingStatus.DRAFT:
        raise BusinessRuleException("会议尚未开放投票（DRAFT），无法发布决议")
    if meeting.status == MeetingStatus.PUBLISHED:
        raise BusinessRuleException("会议已发布决议，禁止重复操作")

    # 拉取全部有效投票
    votes_stmt = select(IcVoteRecord).where(
        IcVoteRecord.meeting_id == meeting_id,
        IcVoteRecord.is_deleted == 0,
    )
    votes: list[IcVoteRecord] = list(
        (await db.execute(votes_stmt)).scalars().all()
    )

    if not votes:
        raise BusinessRuleException("当前无有效投票记录，无法生成决议")

    # 核心计票（纯函数，不含 I/O）
    aggregated = _aggregate_votes(votes, meeting.type)

    # Upsert IcResolution
    res_stmt = select(IcResolution).where(
        IcResolution.meeting_id == meeting_id,
        IcResolution.is_deleted == 0,
    )
    resolution = (await db.execute(res_stmt)).scalar_one_or_none()
    now = datetime.now(UTC)

    if resolution:
        resolution.aggregated_taa = aggregated
        resolution.published_at = now
        resolution.published_by = publisher_id
    else:
        resolution = IcResolution(
            meeting_id=meeting_id,
            aggregated_taa=aggregated,
            ai_minutes=None,
            published_at=now,
            published_by=publisher_id,
        )
        db.add(resolution)

    # 推进会议到终态
    meeting.status = MeetingStatus.PUBLISHED

    await db.flush()
    await db.refresh(meeting)
    await db.refresh(resolution)
    return meeting, resolution


async def get_committee_page_context(db: AsyncSession) -> CommitteePageContextResponse:
    """
    投委会视图：拉取 ic_resolutions 表中 id 最小的一条（第一条）决议及会议、投票摘要。
    与本地联调一致：不要求 published_at；无记录时返回空壳。
    """
    stmt = (
        select(IcResolution, IcMeeting)
        .join(IcMeeting, IcMeeting.id == IcResolution.meeting_id)
        .where(
            IcResolution.is_deleted == 0,
            IcMeeting.is_deleted == 0,
        )
        .order_by(IcResolution.id.asc())
        .limit(1)
    )
    row = (await db.execute(stmt)).first()
    if row is None:
        return CommitteePageContextResponse()

    resolution, meeting = row

    votes_stmt = (
        select(IcVoteRecord)
        .where(
            IcVoteRecord.meeting_id == meeting.id,
            IcVoteRecord.is_deleted == 0,
        )
        .order_by(IcVoteRecord.submitted_at.desc().nulls_last())
    )
    vote_rows = list((await db.execute(votes_stmt)).scalars().all())

    return CommitteePageContextResponse(
        meeting=MeetingResponse.model_validate(meeting),
        resolution=ResolutionResponse.model_validate(resolution),
        votes=[
            CommitteeVoteRow(user_id=v.user_id, submitted_at=v.submitted_at)
            for v in vote_rows
        ],
    )
