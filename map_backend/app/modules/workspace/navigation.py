"""
modules/workspace/navigation.py — 九宫格动态布局计算引擎

设计原则：
  - 全部为纯函数，零 I/O，零外部依赖，极易单元测试
  - 根据用户角色 (UserRole) 过滤可见卡片
  - 根据系统运行时状态（最新决议 / 调仓紧急度）动态追加徽标 (badge)
  - 每个角色最多展示 9 个卡片（九宫格）
"""
from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


# ── 用户角色（单一事实源，与未来 JWT profile 字段对齐） ───────────────────────


class UserRole(str, enum.Enum):
    ANALYST = "ANALYST"                         # 研究员
    PM = "PM"                                   # 组合经理
    RISK_OFFICER = "RISK_OFFICER"               # 风险官
    COMMITTEE_MEMBER = "COMMITTEE_MEMBER"       # 混合投委会委员
    COMMITTEE_SECRETARY = "COMMITTEE_SECRETARY" # 混合投委会秘书
    COMMITTEE_CHAIR = "COMMITTEE_CHAIR"         # 混合投委会主任委员
    FICC_MEMBER = "FICC_MEMBER"                 # FICC投委会委员
    FICC_SECRETARY = "FICC_SECRETARY"           # FICC投委会秘书
    FICC_CHAIR = "FICC_CHAIR"                   # FICC投委会主任委员
    ADMIN = "ADMIN"                             # 超级管理员（全卡片可见）


# ── 九宫格卡片静态配置（不可变，严禁在运行时修改） ───────────────────────────


@dataclass(frozen=True)
class TileConfig:
    tile_id: str
    title: str
    icon: str          # 与前端 icon 库 key 对应
    route: str
    priority: int      # 数字越小，优先级越高
    roles: tuple[str, ...] = ()  # 空 tuple = 全角色可见


# 所有卡片静态定义（priority 决定九宫格排列顺序）
_ALL_TILES: tuple[TileConfig, ...] = (
    # ── 全角色通用 ─────────────────────────────────────────────────────
    TileConfig("workspace",      "工作台",     "layout",       "/workspace",             priority=1),
    TileConfig("news_feed",      "资讯中心",   "newspaper",    "/news",                  priority=2),
    TileConfig("messages",       "消息通知",   "bell",         "/messages",              priority=3),

    # ── 研究员 / 组合经理 / Admin ────────────────────────────────────
    TileConfig("research",       "研究报告",   "file-text",    "/research",              priority=4,
               roles=("ANALYST", "PM", "ADMIN")),
    TileConfig("portfolio_analysis", "组合分析", "pie-chart",  "/portfolio/analysis",    priority=5,
               roles=("ANALYST", "PM", "ADMIN")),
    TileConfig("data_terminal",  "数据终端",   "database",     "/data",                  priority=6,
               roles=("ANALYST", "ADMIN")),

    # ── 组合经理 / Admin ──────────────────────────────────────────────
    TileConfig("portfolio_mgmt", "组合管理",   "briefcase",    "/portfolio",             priority=4,
               roles=("PM", "ADMIN")),
    TileConfig("taa_guidance",   "资配指引",   "compass",      "/taa",                   priority=5,
               roles=("PM", "RISK_OFFICER", "ADMIN")),
    TileConfig("trade_execution","交易执行",   "activity",     "/trade",                 priority=6,
               roles=("PM", "ADMIN")),

    # ── 风险官 / Admin ────────────────────────────────────────────────
    TileConfig("risk_monitor",   "风险监控",   "shield",       "/risk",                  priority=4,
               roles=("RISK_OFFICER", "ADMIN")),
    TileConfig("compliance",     "合规检查",   "check-circle", "/compliance",            priority=5,
               roles=("RISK_OFFICER", "ADMIN")),
    TileConfig("stress_test",    "压力测试",   "zap",          "/stress-test",           priority=6,
               roles=("RISK_OFFICER", "ADMIN")),

    # ── 投委会（混合 & FICC）全角色 / PM（查阅历史）/ Admin ───────────
    TileConfig("ic_decision",    "投委会决策", "users",        "/committee/decisions",   priority=4,
               roles=("COMMITTEE_MEMBER", "COMMITTEE_SECRETARY", "COMMITTEE_CHAIR",
                      "FICC_MEMBER", "FICC_SECRETARY", "FICC_CHAIR", "ADMIN")),
    TileConfig("ic_voting",      "投票管理",   "check-square", "/committee/voting",      priority=5,
               roles=("COMMITTEE_MEMBER", "COMMITTEE_SECRETARY", "COMMITTEE_CHAIR",
                      "FICC_MEMBER", "FICC_SECRETARY", "FICC_CHAIR", "ADMIN")),
    TileConfig("ic_history",     "历史决议",   "archive",      "/committee/history",     priority=6,
               roles=("COMMITTEE_MEMBER", "COMMITTEE_SECRETARY", "COMMITTEE_CHAIR",
                      "FICC_MEMBER", "FICC_SECRETARY", "FICC_CHAIR", "PM", "ADMIN")),
)

# badge 类型常量
_BADGE_INFO    = "info"
_BADGE_WARNING = "warning"
_BADGE_DANGER  = "danger"


# ── 纯函数：九宫格布局计算 ────────────────────────────────────────────────────


def compute_navigation_layout(
    user_role: UserRole,
    latest_resolution: dict[str, Any] | None = None,
    rebalance_urgency: str = "NONE",
) -> list[dict[str, Any]]:
    """
    根据用户角色与系统运行态，计算并返回门户九宫格卡片列表。

    Parameters
    ----------
    user_role           当前登录用户的角色
    latest_resolution   最近一次已发布的 IcResolution.aggregated_taa（可为 None）
    rebalance_urgency   调仓紧急度等级：NONE / LOW / MEDIUM / HIGH / CRITICAL

    Returns
    -------
    最多 9 个卡片的字典列表，按 priority 升序，直接可序列化给前端。
    """
    role_str = user_role.value
    days_since_pub = _days_since_published(latest_resolution)

    # ① 按角色过滤
    visible = [t for t in _ALL_TILES if not t.roles or role_str in t.roles]

    # ② 按 priority 排序，取前 9
    sorted_tiles = sorted(visible, key=lambda t: t.priority)[:9]

    # ③ 逐卡片计算动态 badge（不修改 frozen dataclass，只在输出 dict 中附加）
    result: list[dict[str, Any]] = []
    for tile in sorted_tiles:
        badge: str | None = None
        badge_type: str | None = None

        if tile.tile_id == "taa_guidance":
            # 新决议徽标：7 天内发布过的决议
            if days_since_pub is not None and days_since_pub < 7:
                badge, badge_type = "新决议", _BADGE_INFO

        if tile.tile_id in ("portfolio_mgmt", "taa_guidance"):
            # 调仓紧急度徽标（优先级高于新决议）
            if rebalance_urgency in ("HIGH", "CRITICAL"):
                badge, badge_type = "待调仓", _BADGE_DANGER
            elif rebalance_urgency == "MEDIUM" and badge is None:
                badge, badge_type = "关注", _BADGE_WARNING

        if tile.tile_id == "ic_decision":
            # 投票中：委员收到待投票提示
            # 此处预留，后续由 committee 模块注入状态
            pass

        result.append({
            "tile_id":    tile.tile_id,
            "title":      tile.title,
            "icon":       tile.icon,
            "route":      tile.route,
            "badge":      badge,
            "badge_type": badge_type,
        })

    return result


# ── 辅助函数 ──────────────────────────────────────────────────────────────────


def _days_since_published(resolution: dict[str, Any] | None) -> float | None:
    """
    计算最近一次决议距今天数。
    resolution 是 aggregated_taa dict，其中含 published_at（由 services 层注入）。
    """
    if resolution is None:
        return None
    published_at = resolution.get("published_at")
    if not published_at:
        return None
    try:
        if isinstance(published_at, str):
            dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        elif isinstance(published_at, datetime):
            dt = published_at
        else:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return (datetime.now(UTC) - dt).total_seconds() / 86400
    except (ValueError, TypeError):
        return None
