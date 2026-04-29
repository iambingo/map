#!/usr/bin/env python3
"""
seed_db.py — 本地开发种子数据脚本

在 init_db.py 建完表后运行，向 SQLite（或任意 SQLAlchemy 支持的数据库）
写入足够的测试数据，让投委会、FICC、混合问卷等页面有内容可展示。

用法：
    cd map_backend
    python ../seed_db.py                              # SQLite 默认路径
    python ../seed_db.py --db sqlite:///./map_local.sqlite
    python ../seed_db.py --db mysql+pymysql://...    # 也支持 MySQL
    python ../seed_db.py --truncate                  # 先清空再写入
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def _ensure_backend_on_path() -> None:
    backend_root = Path(__file__).resolve().parent / "map_backend"
    root_str = str(backend_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def main() -> int:
    _ensure_backend_on_path()

    parser = argparse.ArgumentParser(description="Seed local DB with test data.")
    parser.add_argument("--db", default="sqlite:///./map_local.sqlite")
    parser.add_argument("--truncate", action="store_true",
                        help="Delete existing rows before seeding (idempotent re-run)")
    args = parser.parse_args()

    from sqlalchemy import create_engine, delete, text
    from sqlalchemy.orm import Session

    from app.modules.committee.models import (
        IcMeeting, IcVoteRecord, IcResolution,
        MeetingStatus, MeetingType,
    )
    from app.modules.committee.mixed_models import (
        IcMixedQuestionnaireSubmission, MixedSubmissionStatus,
    )

    engine = create_engine(args.db, future=True)

    with Session(engine) as session:
        if args.truncate:
            for tbl in (IcResolution, IcVoteRecord,
                        IcMixedQuestionnaireSubmission, IcMeeting):
                session.execute(delete(tbl))
            session.commit()
            print("Truncated committee tables.")

        # ── 1. 会议 ────────────────────────────────────────────────────────
        now = datetime.now()
        meetings_seed = [
            IcMeeting(
                meeting_code="IC-2026-Q2-MIXED-001",
                title="混合投资委员会 2026 Q2 配置决策会议",
                type=MeetingType.MIXED,
                status=MeetingStatus.VOTING,
                scheduled_at=now - timedelta(hours=2),
                created_by=1,
            ),
            IcMeeting(
                meeting_code="IC-2026-Q2-FICC-001",
                title="FICC 投资委员会 2026 Q2 债券配置会议",
                type=MeetingType.FICC,
                status=MeetingStatus.DRAFT,
                scheduled_at=now + timedelta(days=3),
                created_by=1,
            ),
            IcMeeting(
                meeting_code="IC-2026-Q1-MIXED-001",
                title="混合投资委员会 2026 Q1 配置决策会议",
                type=MeetingType.MIXED,
                status=MeetingStatus.PUBLISHED,
                scheduled_at=now - timedelta(days=90),
                created_by=1,
            ),
        ]
        for m in meetings_seed:
            exists = session.query(IcMeeting).filter_by(
                meeting_code=m.meeting_code).first()
            if not exists:
                session.add(m)
        session.flush()

        # 取出刚写入（或已存在）的 VOTING 会议 id
        mixed_voting = session.query(IcMeeting).filter_by(
            meeting_code="IC-2026-Q2-MIXED-001").one()
        published_meeting = session.query(IcMeeting).filter_by(
            meeting_code="IC-2026-Q1-MIXED-001").one()

        # ── 2. 混合投委会问卷提交（会前筹备 / 会员中心数据来源） ─────────
        session_code_q2 = "2026Q2"
        qs_data = [
            (1, {
                "section_a": {"债券": 4, "权益-红利": 4, "权益-成长": 3, "权益-价值": 4, "黄金": 5, "原油": 2},
                "section_b": {"债券": True, "权益-红利": False, "权益-成长": False, "权益-价值": False, "黄金": True, "原油": False},
                "section_c": ["利率债", "黄金", "REITs"],
                "core_view": "利率下行趋势下债券配置价值提升，建议增加久期。黄金作为避险资产在地缘不确定性下具备配置价值。",
                "risk_flag": False,
            }),
            (2, {
                "section_a": {"债券": 3, "权益-红利": 4, "权益-成长": 4, "权益-价值": 3, "黄金": 3, "原油": 3},
                "section_b": {"债券": False, "权益-红利": True, "权益-成长": True, "权益-价值": False, "黄金": False, "原油": False},
                "section_c": ["可转债", "港股", "A股大盘"],
                "core_view": "A股市场结构性机会明确，科技与红利板块值得重点关注。港股估值优势明显，建议通过沪港通适度增配。",
                "risk_flag": False,
            }),
            (3, {
                "section_a": {"债券": 5, "权益-红利": 2, "权益-成长": 2, "权益-价值": 3, "黄金": 5, "原油": 3},
                "section_b": {"债券": True, "权益-红利": False, "权益-成长": False, "权益-价值": False, "黄金": True, "原油": False},
                "section_c": ["利率债", "信用债"],
                "core_view": "地缘风险仍存，维持均衡配置，债券防御价值突出。信用利差处于历史低位需警惕信用事件风险。",
                "risk_flag": True,
            }),
            (4, {
                "section_a": {"债券": 3, "权益-红利": 3, "权益-成长": 5, "权益-价值": 3, "黄金": 2, "原油": 4},
                "section_b": {"债券": False, "权益-红利": False, "权益-成长": True, "权益-价值": False, "黄金": False, "原油": True},
                "section_c": ["A股大盘", "海外权益", "商品"],
                "core_view": "科技成长板块在 AI 产业周期驱动下具备超额收益空间，维持高仓位。原油供需格局偏紧，建议保留商品配置。",
                "risk_flag": False,
            }),
        ]
        for submitter_id, qj in qs_data:
            exists = session.query(IcMixedQuestionnaireSubmission).filter_by(
                session_code=session_code_q2, submitter_id=submitter_id).first()
            if not exists:
                session.add(IcMixedQuestionnaireSubmission(
                    session_code=session_code_q2,
                    submitter_id=submitter_id,
                    status=MixedSubmissionStatus.SUBMITTED,
                    questionnaire_json=qj,
                    submitted_at=now - timedelta(hours=3),
                ))

        # ── 3. 投票记录（VOTING 会议） ────────────────────────────────────
        vote_template = {
            "choice_items": {
                "equity_view":   {"value": "overweight", "label": "增配"},
                "bond_view":     {"value": "neutral",    "label": "标配"},
                "gold_view":     {"value": "overweight", "label": "增配"},
                "commodity_view":{"value": "underweight","label": "减配"},
            },
            "numeric_items": {
                "equity_target": 40,
                "bond_target":   45,
                "gold_target":   10,
                "cash_target":    5,
            },
        }
        for uid in [1, 2, 3]:
            exists = session.query(IcVoteRecord).filter_by(
                meeting_id=mixed_voting.id, user_id=uid).first()
            if not exists:
                vote = dict(vote_template)
                # 给每人的数值稍作扰动，让聚合结果有意义
                vote["numeric_items"] = {
                    "equity_target": 40 + (uid - 2) * 3,
                    "bond_target":   45 - (uid - 2) * 2,
                    "gold_target":   10 + (uid - 2),
                    "cash_target":    5,
                }
                session.add(IcVoteRecord(
                    meeting_id=mixed_voting.id,
                    user_id=uid,
                    vote_json=vote,
                    submitted_at=now - timedelta(hours=1),
                ))

        # ── 4. 已发布决议（PUBLISHED 会议） ──────────────────────────────
        exists = session.query(IcResolution).filter_by(
            meeting_id=published_meeting.id).first()
        if not exists:
            session.add(IcResolution(
                meeting_id=published_meeting.id,
                aggregated_taa={
                    "equity_view":    "overweight",
                    "bond_view":      "neutral",
                    "gold_view":      "overweight",
                    "commodity_view": "underweight",
                    "choice_results": {
                        "equity_view":    {"mode": "overweight", "votes": {"overweight": 4, "neutral": 1, "underweight": 0}},
                        "bond_view":      {"mode": "neutral",    "votes": {"overweight": 1, "neutral": 3, "underweight": 1}},
                        "gold_view":      {"mode": "overweight", "votes": {"overweight": 3, "neutral": 2, "underweight": 0}},
                        "commodity_view": {"mode": "underweight","votes": {"overweight": 0, "neutral": 1, "underweight": 4}},
                    },
                    "numeric_results": {
                        "equity_target":   {"mean": 40.0, "median": 40.0, "std": 3.0},
                        "bond_target":     {"mean": 45.0, "median": 45.0, "std": 2.0},
                        "gold_target":     {"mean": 10.0, "median": 10.0, "std": 1.0},
                        "cash_target":     {"mean":  5.0, "median":  5.0, "std": 0.0},
                    },
                    "published_at": (now - timedelta(days=88)).isoformat(),
                },
                ai_minutes="本次会议委员整体对权益资产持增配观点，债券维持标配，黄金作为避险资产适度增配，大宗商品整体减配。",
                published_at=now - timedelta(days=88),
                published_by=1,
            ))

        session.commit()

    print("✅ Seed data written successfully.")
    print("   Meetings : IC-2026-Q2-MIXED-001 (VOTING), IC-2026-Q2-FICC-001 (DRAFT), IC-2026-Q1-MIXED-001 (PUBLISHED)")
    print("   Mixed QS : 4 submissions for session 2026Q2")
    print("   Votes    : 3 vote records for VOTING meeting")
    print("   Resolution: 1 published resolution for Q1 meeting")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
