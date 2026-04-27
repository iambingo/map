"""
modules/asset_allocation/repository.py — TDSQL 存取草稿与最终版本（骨架）
"""
from sqlalchemy.ext.asyncio import AsyncSession


async def get_draft(db: AsyncSession, draft_id: int) -> dict | None:
    raise NotImplementedError


async def save_draft(db: AsyncSession, data: dict) -> int:
    """返回新建草稿的 ID。"""
    raise NotImplementedError


async def publish_draft(db: AsyncSession, draft_id: int) -> bool:
    raise NotImplementedError
