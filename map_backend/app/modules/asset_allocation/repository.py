"""
modules/asset_allocation/repository.py — TDSQL 存取层
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.asset_allocation.models import AssetClassConfig, SaaDraft


async def get_draft(db: AsyncSession, draft_id: int) -> SaaDraft | None:
    result = await db.execute(
        select(SaaDraft).where(SaaDraft.id == draft_id, SaaDraft.is_deleted == 0)
    )
    return result.scalar_one_or_none()


async def list_drafts(db: AsyncSession, user_id: int, status: str | None = None) -> list[SaaDraft]:
    q = select(SaaDraft).where(SaaDraft.user_id == user_id, SaaDraft.is_deleted == 0)
    if status:
        q = q.where(SaaDraft.status == status)
    q = q.order_by(SaaDraft.version.desc())
    result = await db.execute(q)
    return list(result.scalars().all())


async def _next_version(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        select(func.max(SaaDraft.version)).where(
            SaaDraft.user_id == user_id, SaaDraft.is_deleted == 0
        )
    )
    max_ver = result.scalar_one_or_none()
    return (max_ver or 0) + 1


async def save_draft(db: AsyncSession, data: dict) -> SaaDraft:
    version = await _next_version(db, data["user_id"])
    draft = SaaDraft(
        user_id=data["user_id"],
        version=version,
        risk_level=data["risk_level"],
        total_amount=data["total_amount"],
        weights=data.get("weights", {}),
        expected_return=data.get("expected_return"),
        expected_volatility=data.get("expected_volatility"),
        constraints=data.get("constraints", {}),
        notes=data.get("notes"),
    )
    db.add(draft)
    await db.flush()
    await db.refresh(draft)
    return draft


async def update_draft_status(
    db: AsyncSession,
    draft_id: int,
    status: str,
    *,
    approver_id: int | None = None,
    reject_reason: str | None = None,
) -> SaaDraft | None:
    draft = await get_draft(db, draft_id)
    if draft is None:
        return None
    draft.status = status
    if approver_id is not None:
        draft.approver_id = approver_id
    if reject_reason is not None:
        draft.reject_reason = reject_reason
    await db.flush()
    return draft


async def list_asset_class_configs(db: AsyncSession) -> list[AssetClassConfig]:
    result = await db.execute(
        select(AssetClassConfig)
        .where(AssetClassConfig.is_active == 1, AssetClassConfig.is_deleted == 0)
        .order_by(AssetClassConfig.sort_order)
    )
    return list(result.scalars().all())
