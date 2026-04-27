"""
modules/asset_allocation/services.py — 资配业务编排层
协调 domain 规则引擎与 repository 的存取操作。
"""
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleException
from app.modules.asset_allocation.domain.saa_calculator import AllocationInput, calculate_saa
from app.modules.asset_allocation.models import DraftStatus
from app.modules.asset_allocation import repository as repo

logger = logging.getLogger(__name__)


async def run_saa_calculation(db: AsyncSession, user_id: int, params: dict) -> dict:
    """计算 SAA 权重并保存草稿。params: {risk_level, total_amount, constraints?, notes?}"""
    risk_level = int(params.get("risk_level", 0))
    total_amount = float(params.get("total_amount", 0))

    inp = AllocationInput(
        risk_level=risk_level,
        total_amount=total_amount,
        constraints=params.get("constraints", {}),
    )
    result = calculate_saa(inp)

    draft = await repo.save_draft(db, {
        "user_id": user_id,
        "risk_level": risk_level,
        "total_amount": total_amount,
        "weights": result.weights,
        "expected_return": result.expected_return,
        "expected_volatility": result.expected_volatility,
        "constraints": params.get("constraints", {}),
        "notes": params.get("notes"),
    })

    logger.info("SAA calculated: user_id=%s draft_id=%s version=%s", user_id, draft.id, draft.version)
    return _draft_to_dict(draft, amount_breakdown=result.amount_breakdown)


async def get_draft_detail(db: AsyncSession, draft_id: int, user_id: int) -> dict:
    draft = await repo.get_draft(db, draft_id)
    if draft is None or draft.user_id != user_id:
        raise BusinessRuleException(f"草稿不存在或无权访问: draft_id={draft_id}")
    return _draft_to_dict(draft)


async def list_user_drafts(db: AsyncSession, user_id: int, status: str | None = None) -> list[dict]:
    drafts = await repo.list_drafts(db, user_id, status=status)
    return [_draft_to_dict(d) for d in drafts]


async def submit_for_approval(db: AsyncSession, user_id: int, draft_id: int) -> dict:
    """将草稿状态推进到 PENDING_APPROVAL。"""
    draft = await repo.get_draft(db, draft_id)
    if draft is None or draft.user_id != user_id:
        raise BusinessRuleException(f"草稿不存在或无权访问: draft_id={draft_id}")
    if draft.status != DraftStatus.DRAFT:
        raise BusinessRuleException(f"只有 DRAFT 状态的草稿可提交审批，当前状态: {draft.status}")

    updated = await repo.update_draft_status(db, draft_id, DraftStatus.PENDING_APPROVAL)
    logger.info("SAA submitted for approval: draft_id=%s user_id=%s", draft_id, user_id)
    return _draft_to_dict(updated)


async def approve_draft(db: AsyncSession, approver_id: int, draft_id: int) -> dict:
    draft = await repo.get_draft(db, draft_id)
    if draft is None:
        raise BusinessRuleException(f"草稿不存在: draft_id={draft_id}")
    if draft.status != DraftStatus.PENDING_APPROVAL:
        raise BusinessRuleException(f"只有 PENDING_APPROVAL 状态可审批，当前: {draft.status}")

    updated = await repo.update_draft_status(
        db, draft_id, DraftStatus.APPROVED, approver_id=approver_id
    )
    logger.info("SAA approved: draft_id=%s approver_id=%s", draft_id, approver_id)
    return _draft_to_dict(updated)


async def reject_draft(db: AsyncSession, approver_id: int, draft_id: int, reason: str) -> dict:
    draft = await repo.get_draft(db, draft_id)
    if draft is None:
        raise BusinessRuleException(f"草稿不存在: draft_id={draft_id}")
    if draft.status != DraftStatus.PENDING_APPROVAL:
        raise BusinessRuleException(f"只有 PENDING_APPROVAL 状态可拒绝，当前: {draft.status}")

    updated = await repo.update_draft_status(
        db, draft_id, DraftStatus.REJECTED, approver_id=approver_id, reject_reason=reason
    )
    logger.info("SAA rejected: draft_id=%s approver_id=%s", draft_id, approver_id)
    return _draft_to_dict(updated)


async def list_asset_classes(db: AsyncSession) -> list[dict]:
    configs = await repo.list_asset_class_configs(db)
    return [c.to_dict() for c in configs]


def _draft_to_dict(draft, *, amount_breakdown: dict | None = None) -> dict:
    d = draft.to_dict()
    if amount_breakdown is not None:
        d["amount_breakdown"] = amount_breakdown
    return d
