"""
modules/workspace/router.py — 智能门户 (BFF) 路由

端点清单
─────────────────────────────────────────────────────────────────────────────
  GET /portal-snapshot   返回门户首页所需的全量预渲染 JSON 快照
─────────────────────────────────────────────────────────────────────────────

【接口响应速度设计】
  快路径（缓存命中）：Redis GET × 1 + 纯函数计算 = < 5 ms
  慢路径（缓存未命中）：DB 查询 + Adapter 调用 + Redis SET = ~100 ms

  无论何种情况，接口必须在 EXTERNAL_HTTP_TIMEOUT 内响应。
  外部系统故障时，优先从 stale 缓存降级，绝不 500。

【偏离度计算规则】
  TAA 指引视图   →  目标仓位区间
  ──────────────────────────────
  overweight     → [55%, 75%]
  neutral        → [40%, 55%]
  underweight    → [15%, 40%]

  deviation_pct = current_ratio - 区间边界
    < 0 → 低于下限（欠配）
    = 0 → 在区间内（合规）
    > 0 → 超过上限（超配）

  urgency 等级 (max_deviation_abs 决定)
    NONE     0%
    LOW    < 3%
    MEDIUM < 7%
    HIGH   < 15%
    CRITICAL ≥ 15%
"""
from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import get_redis
from app.dependencies import DBSession, PortalUserID
from app.modules.adapters.portfolio_sys import PortfolioPositionData, get_portfolio_adapter
from app.modules.committee.models import IcResolution
from app.modules.workspace.navigation import UserRole, compute_navigation_layout
from app.modules.workspace.widget_snapshot import get_cached_snapshot, set_cached_snapshot

logger = logging.getLogger(__name__)

router = APIRouter()


def _coerce_json_object(val: Any) -> dict[str, Any]:
    """
    ORM JSON 列在部分驱动/SQLite 下可能以 str 返回；统一转为 dict，避免 .get 触发 TypeError。
    """
    if val is None:
        return {}
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            logger.warning("JSON 字段解析失败（前 120 字符）: %s", val[:120])
            return {}
    return {}

# ── 常量 ──────────────────────────────────────────────────────────────────────

_CACHE_KEY = "portal_snapshot:base"

# TAA 指引视图 → 目标仓位区间 [min, max]
_VIEW_TARGET_RANGES: dict[str, tuple[float, float]] = {
    "overweight":  (0.55, 0.75),
    "neutral":     (0.40, 0.55),
    "underweight": (0.15, 0.40),
}

# IcResolution choice_results key → PortfolioPositionData positions key
_TAA_KEY_TO_POSITION_KEY: dict[str, str] = {
    "equity_view":    "equity",
    "bond_view":      "bond",
    "commodity_view": "commodity",
    "cash_view":      "cash",
}

_ASSET_DISPLAY_NAMES: dict[str, str] = {
    "equity": "股票", "bond": "债券", "commodity": "商品", "cash": "现金",
}


# ── Response Schema ───────────────────────────────────────────────────────────


class PortalSnapshotResponse(BaseModel):
    snapshot_at: str
    is_stale: bool
    stale_reason: str | None

    taa_guidance: dict[str, Any]
    positions: dict[str, Any] | None

    deviation_analysis: dict[str, Any]
    rebalance_urgency: dict[str, Any]

    navigation_tiles: list[dict[str, Any]]


# ── 纯函数区（偏离度 / 紧急度计算，零 I/O） ──────────────────────────────────


def _compute_deviation_analysis(
    choice_results: dict[str, Any],
    positions: dict[str, Any],
) -> tuple[dict[str, Any], float]:
    """
    对比 TAA 指引与当前头寸，逐资产类别计算偏离情况。

    Returns
    -------
    (deviation_analysis, max_abs_deviation)
      deviation_analysis : 各资产类别偏离详情
      max_abs_deviation  : 所有资产中偏离绝对值最大值（用于确定紧急度）
    """
    analysis: dict[str, Any] = {}
    max_abs_dev = 0.0

    for taa_key, pos_key in _TAA_KEY_TO_POSITION_KEY.items():
        if taa_key not in choice_results:
            continue
        entry = choice_results[taa_key]
        if not isinstance(entry, dict):
            continue
        guidance_view = str(entry.get("winner", "") or "")
        target_range = _VIEW_TARGET_RANGES.get(guidance_view)
        pos_data = positions.get(pos_key)
        current_ratio: float | None = None
        if isinstance(pos_data, dict) and pos_data.get("ratio") is not None:
            try:
                current_ratio = float(pos_data["ratio"])
            except (TypeError, ValueError):
                current_ratio = None

        if target_range is None or current_ratio is None:
            continue

        lo, hi = target_range
        if current_ratio < lo:
            deviation = current_ratio - lo   # 负数：欠配
        elif current_ratio > hi:
            deviation = current_ratio - hi   # 正数：超配
        else:
            deviation = 0.0

        abs_dev = abs(deviation)
        max_abs_dev = max(max_abs_dev, abs_dev)

        analysis[pos_key] = {
            "guidance_view":  guidance_view,
            "current_ratio":  current_ratio,
            "target_range":   {"min": lo, "max": hi},
            "deviation_pct":  round(deviation * 100, 2),
            "is_compliant":   deviation == 0.0,
        }

    return analysis, max_abs_dev


def _determine_urgency(max_abs_deviation: float) -> str:
    if max_abs_deviation == 0:
        return "NONE"
    if max_abs_deviation < 0.03:
        return "LOW"
    if max_abs_deviation < 0.07:
        return "MEDIUM"
    if max_abs_deviation < 0.15:
        return "HIGH"
    return "CRITICAL"


def _urgency_reason(urgency: str, deviation_analysis: dict[str, Any]) -> str:
    if urgency == "NONE" or not deviation_analysis:
        return "所有资产类别均在配置指引范围内"

    # 找出偏离绝对值最大的资产
    worst_key = max(
        deviation_analysis, key=lambda k: abs(deviation_analysis[k]["deviation_pct"])
    )
    info = deviation_analysis[worst_key]
    dev_pct = info["deviation_pct"]
    direction = "低于" if dev_pct < 0 else "高于"
    asset_name = _ASSET_DISPLAY_NAMES.get(worst_key, worst_key)

    templates = {
        "LOW":      f"{asset_name}仓位{direction}指引 {abs(dev_pct):.1f}%，可择机调整",
        "MEDIUM":   f"{asset_name}仓位{direction}指引 {abs(dev_pct):.1f}%，建议近期调仓",
        "HIGH":     f"{asset_name}仓位{direction}指引 {abs(dev_pct):.1f}%，建议尽快调仓",
        "CRITICAL": f"{asset_name}仓位{direction}指引 {abs(dev_pct):.1f}%，严重偏离，需立即处理",
    }
    return templates.get(urgency, "")


# ── 异步辅助函数（DB / Adapter I/O） ──────────────────────────────────────────


async def _fetch_latest_resolution(db: AsyncSession) -> IcResolution | None:
    """查询 ic_resolutions 表中第一条有效决议（按主键 id 升序），便于本地库仅有草稿数据时仍可展示。"""
    stmt = (
        select(IcResolution)
        .where(IcResolution.is_deleted == 0)
        .order_by(IcResolution.id.asc())
        .limit(1)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def _build_base_snapshot(db: AsyncSession) -> dict[str, Any]:
    """
    从源头构建门户基础快照（缓存未命中时调用）。
    包含：TAA 指引 + 实时头寸 + 偏离度分析 + 紧急度评级。

    此函数是唯一允许调用外部 Adapter 的地方。
    """
    # ① 获取最新决议
    resolution = await _fetch_latest_resolution(db)
    taa_guidance: dict[str, Any] = {}
    resolution_meta: dict[str, Any] | None = None

    if resolution:
        taa_guidance = _coerce_json_object(resolution.aggregated_taa)
        resolution_meta = {
            "resolution_id":  resolution.id,
            "meeting_id":     resolution.meeting_id,
            "published_at":   resolution.published_at.isoformat() if resolution.published_at else None,
        }

    # 归一化 TAA 子结构，防止历史脏数据（非 dict）导致 TypeError
    cr_raw = taa_guidance.get("choice_results", {})
    choice_results: dict[str, Any] = cr_raw if isinstance(cr_raw, dict) else {}
    nr_raw = taa_guidance.get("numeric_results", {})
    numeric_results: dict[str, Any] = nr_raw if isinstance(nr_raw, dict) else {}
    taa_guidance = {**taa_guidance, "choice_results": choice_results, "numeric_results": numeric_results}

    # ② 获取头寸（外部 Adapter，含超时保护）
    positions_raw: dict[str, Any] | None = None
    try:
        adapter = get_portfolio_adapter()
        pos_data: PortfolioPositionData = await adapter.get_all_positions()
        positions_raw = {
            "portfolio_id": pos_data.portfolio_id,
            "snapshot_at":  pos_data.snapshot_at.isoformat(),
            "total_nav":    pos_data.total_nav,
            **{
                cls: {
                    "ratio":        p.ratio,
                    "market_value": p.market_value,
                    "currency":     p.currency,
                    "change_1d":    p.change_1d,
                }
                for cls, p in pos_data.positions.items()
            },
        }
    except Exception as exc:
        logger.error("Portfolio adapter failed, positions unavailable: %s", exc)
        # 外部系统故障时 positions 置 None，偏离度无法计算

    # ③ 偏离度计算
    choice_results = taa_guidance.get("choice_results", {}) if isinstance(taa_guidance.get("choice_results"), dict) else {}
    if positions_raw and choice_results:
        deviation_analysis, max_abs_dev = _compute_deviation_analysis(
            choice_results, positions_raw
        )
        urgency = _determine_urgency(max_abs_dev)
        urgency_reason = _urgency_reason(urgency, deviation_analysis)
    else:
        deviation_analysis = {}
        urgency = "NONE"
        urgency_reason = "暂无资配指引或头寸数据，无法评估偏离度"

    return {
        "snapshot_at":    datetime.now(UTC).isoformat(),
        "taa_guidance": {
            "source_resolution": resolution_meta,
            "choice_results":    choice_results,
            "numeric_results":   taa_guidance.get("numeric_results", {}),
            "published_at":      resolution_meta["published_at"] if resolution_meta else None,
        },
        "positions":          positions_raw,
        "deviation_analysis": deviation_analysis,
        "rebalance_urgency": {
            "level":  urgency,
            "reason": urgency_reason,
        },
    }


def _empty_snapshot() -> dict[str, Any]:
    """Redis + DB + Adapter 全部失败时的保底兜底快照。"""
    return {
        "snapshot_at":    datetime.now(UTC).isoformat(),
        "taa_guidance":   {"source_resolution": None, "choice_results": {}, "numeric_results": {}, "published_at": None},
        "positions":      None,
        "deviation_analysis": {},
        "rebalance_urgency":  {"level": "NONE", "reason": "数据加载失败，请稍后重试"},
    }


# ── API 端点 ──────────────────────────────────────────────────────────────────


@router.get(
    "/portal-snapshot",
    response_model=PortalSnapshotResponse,
    summary="获取门户首页完整快照",
    description=(
        "返回门户首页所需的全量预渲染 JSON，前端**直接渲染无需二次计算**。\n\n"
        "**快路径（< 5 ms）**：Redis 缓存命中 → 直接返回，仅追加九宫格布局（纯函数）。\n\n"
        "**慢路径（~100 ms）**：缓存未命中 → 查 DB + 调 Adapter → 写缓存 → 返回。\n\n"
        "**降级保底**：外部系统故障时返回 `is_stale=true` + stale 数据，绝不 500。"
    ),
)
async def get_portal_snapshot(
    db: DBSession,
    user_id: PortalUserID,
    role: UserRole = Query(
        default=UserRole.PM,
        description="用户角色，用于生成个性化九宫格布局（临时参数，生产环境从 JWT profile 读取）",
    ),
) -> PortalSnapshotResponse:
    # ── Step 1: 尝试读 Redis 缓存（快路径） ─────────────────────────────────
    stale_reason: str | None = None
    base_snapshot: dict[str, Any] | None = None
    is_stale = False

    try:
        redis = await get_redis()
        base_snapshot, is_stale = await get_cached_snapshot(redis, _CACHE_KEY)
        if is_stale:
            stale_reason = "外部系统暂时不可达，展示最近缓存数据"
    except Exception as exc:
        logger.warning("Redis unavailable, bypassing cache: %s", exc)
        redis = None  # 后续跳过写缓存

    # ── Step 2: 缓存未命中 → 回源构建（慢路径） ─────────────────────────────
    if base_snapshot is None:
        try:
            base_snapshot = await _build_base_snapshot(db)
            # 成功回源后写入缓存
            if redis is not None:
                await set_cached_snapshot(redis, _CACHE_KEY, base_snapshot)
            is_stale = False
        except Exception as exc:
            logger.error("Failed to build portal snapshot from source: %s", exc)
            # 三重降级：回源也失败，返回空白占位快照
            base_snapshot = _empty_snapshot()
            is_stale = True
            stale_reason = f"数据服务异常（{type(exc).__name__}），展示空白快照"

    # ── Step 3: 计算个性化九宫格（纯函数，< 1 ms） ───────────────────────────
    taa_info = base_snapshot.get("taa_guidance", {})
    urgency_level = base_snapshot.get("rebalance_urgency", {}).get("level", "NONE")

    nav_tiles = compute_navigation_layout(
        user_role=role,
        latest_resolution=taa_info,
        rebalance_urgency=urgency_level,
    )

    return PortalSnapshotResponse(
        snapshot_at=base_snapshot["snapshot_at"],
        is_stale=is_stale,
        stale_reason=stale_reason,
        taa_guidance=base_snapshot["taa_guidance"],
        positions=base_snapshot.get("positions"),
        deviation_analysis=base_snapshot["deviation_analysis"],
        rebalance_urgency=base_snapshot["rebalance_urgency"],
        navigation_tiles=nav_tiles,
    )
