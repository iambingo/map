#!/usr/bin/env python3
"""
seed_mixed.py — 混合投委会问卷示例数据初始化脚本

用途：
    他人 clone 项目后，先运行 init_db.py 建表，再运行本脚本写入示例数据，
    即可直接体验完整功能，无需手动录入。

用法（在 map_backend 目录下执行）：
    cd map_backend
    python init_db.py          # 先建表
    python seed_mixed.py       # 再写入示例数据

注意：
    - 脚本具有幂等性：按 (session_code, submitter_id) 查重，已存在则跳过（不覆盖）。
    - 默认使用当前目录下的 map_local.sqlite，可通过 --db 参数覆盖。
    - 使用原生 sqlite3 库直接插入，手动分配 id，兼容 SQLAlchemy BigInteger DDL。
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path


# ── 示例数据 ────────────────────────────────────────────────────────────────

SEED_RECORDS = [
    {
        "session_code": "2026Q2",
        "submitter_id": 1,
        "questionnaire_json": {
            "section_a": {"债券": 4, "权益-红利": 4, "权益-成长": 3, "权益-价值": 4, "黄金": 5, "原油": 2},
            "section_b": {"债券": True, "权益-红利": False, "权益-成长": False, "权益-价值": False, "黄金": True, "原油": False},
            "section_c": ["利率债", "黄金", "REITs"],
            "core_view": "利率下行趋势下债券配置价值提升，建议增加久期。黄金作为避险资产在地缘不确定性下具备配置价值。",
            "risk_flag": False,
        },
    },
    {
        "session_code": "2026Q2",
        "submitter_id": 2,
        "questionnaire_json": {
            "section_a": {"债券": 3, "权益-红利": 4, "权益-成长": 4, "权益-价值": 3, "黄金": 3, "原油": 3},
            "section_b": {"债券": False, "权益-红利": True, "权益-成长": True, "权益-价值": False, "黄金": False, "原油": False},
            "section_c": ["可转债", "港股", "A股大盘"],
            "core_view": "A股市场结构性机会明确，科技与红利板块值得重点关注。港股估值优势明显，建议通过沪港通适度增配。",
            "risk_flag": False,
        },
    },
    {
        "session_code": "2026Q2",
        "submitter_id": 3,
        "questionnaire_json": {
            "section_a": {"债券": 5, "权益-红利": 2, "权益-成长": 2, "权益-价值": 3, "黄金": 5, "原油": 3},
            "section_b": {"债券": True, "权益-红利": False, "权益-成长": False, "权益-价值": False, "黄金": True, "原油": False},
            "section_c": ["利率债", "信用债"],
            "core_view": "地缘风险仍存，维持均衡配置，债券防御价值突出。信用利差处于历史低位需警惕信用事件风险。",
            "risk_flag": True,
        },
    },
    {
        "session_code": "2025Q4",
        "submitter_id": 1,
        "questionnaire_json": {
            "section_a": {"债券": 3, "权益-红利": 4, "权益-成长": 3, "权益-价值": 4, "黄金": 3, "原油": 1},
            "section_b": {"债券": False, "权益-红利": True, "权益-成长": False, "权益-价值": True, "黄金": False, "原油": False},
            "section_c": ["利率债", "A股大盘"],
            "core_view": "Q4经济温和修复，红利策略持续占优。",
            "risk_flag": False,
        },
    },
    {
        "session_code": "2025Q4",
        "submitter_id": 2,
        "questionnaire_json": {
            "section_a": {"债券": 3, "权益-红利": 5, "权益-成长": 2, "权益-价值": 3, "黄金": 4, "原油": 2},
            "section_b": {"债券": False, "权益-红利": True, "权益-成长": False, "权益-价值": False, "黄金": True, "原油": False},
            "section_c": ["利率债", "黄金"],
            "core_view": "红利策略延续强势，黄金配置价值提升。",
            "risk_flag": False,
        },
    },
    {
        "session_code": "2025Q4",
        "submitter_id": 3,
        "questionnaire_json": {
            "section_a": {"债券": 4, "权益-红利": 3, "权益-成长": 3, "权益-价值": 4, "黄金": 3, "原油": 2},
            "section_b": {"债券": True, "权益-红利": False, "权益-成长": False, "权益-价值": True, "黄金": False, "原油": False},
            "section_c": ["信用债", "港股"],
            "core_view": "信用环境改善，关注高收益债机会。",
            "risk_flag": False,
        },
    },
    {
        "session_code": "2025Q3",
        "submitter_id": 1,
        "questionnaire_json": {
            "section_a": {"债券": 5, "权益-红利": 2, "权益-成长": 2, "权益-价值": 3, "黄金": 5, "原油": 3},
            "section_b": {"债券": True, "权益-红利": False, "权益-成长": False, "权益-价值": False, "黄金": True, "原油": False},
            "section_c": ["利率债", "黄金"],
            "core_view": "避险情绪主导，债券黄金双优。",
            "risk_flag": True,
        },
    },
    {
        "session_code": "2025Q3",
        "submitter_id": 2,
        "questionnaire_json": {
            "section_a": {"债券": 5, "权益-红利": 3, "权益-成长": 1, "权益-价值": 2, "黄金": 5, "原油": 3},
            "section_b": {"债券": True, "权益-红利": False, "权益-成长": False, "权益-价值": False, "黄金": True, "原油": False},
            "section_c": ["利率债", "信用债", "黄金"],
            "core_view": "地缘冲突加剧，防御配置为主。",
            "risk_flag": True,
        },
    },
    {
        "session_code": "2025Q3",
        "submitter_id": 3,
        "questionnaire_json": {
            "section_a": {"债券": 4, "权益-红利": 2, "权益-成长": 3, "权益-价值": 3, "黄金": 4, "原油": 2},
            "section_b": {"债券": True, "权益-红利": False, "权益-成长": False, "权益-价值": False, "黄金": True, "原油": False},
            "section_c": ["利率债", "REITs"],
            "core_view": "波动加大，维持防御性配置。",
            "risk_flag": False,
        },
    },
]


# ── 主逻辑 ──────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed mixed questionnaire demo data.")
    parser.add_argument(
        "--db",
        default="map_local.sqlite",
        help="SQLite 文件路径（默认：当前目录 map_local.sqlite）",
    )
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"ERROR: 数据库文件不存在: {db_path.resolve()}")
        print("请先运行 python init_db.py 建表后再执行本脚本。")
        return 1

    inserted = 0
    skipped = 0
    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row

        # 获取当前最大 id，手动自增（兼容 BigInteger DDL 无 AUTOINCREMENT 的情况）
        max_id_row = conn.execute(
            "SELECT COALESCE(MAX(id), 0) FROM ic_mixed_questionnaire_submissions"
        ).fetchone()
        next_id = (max_id_row[0] or 0) + 1

        for rec in SEED_RECORDS:
            # 幂等检查
            row = conn.execute(
                "SELECT id FROM ic_mixed_questionnaire_submissions "
                "WHERE session_code=? AND submitter_id=? AND is_deleted=0",
                (rec["session_code"], rec["submitter_id"]),
            ).fetchone()

            if row:
                print(
                    f"  SKIP  session={rec['session_code']} "
                    f"submitter={rec['submitter_id']} (已存在，不覆盖)"
                )
                skipped += 1
                continue

            conn.execute(
                "INSERT INTO ic_mixed_questionnaire_submissions "
                "(id, session_code, submitter_id, status, questionnaire_json, submitted_at, is_deleted) "
                "VALUES (?, ?, ?, ?, ?, ?, 0)",
                (
                    next_id,
                    rec["session_code"],
                    rec["submitter_id"],
                    "SUBMITTED",
                    json.dumps(rec["questionnaire_json"], ensure_ascii=False),
                    now_str,
                ),
            )
            print(
                f"  INSERT id={next_id} session={rec['session_code']} "
                f"submitter={rec['submitter_id']}"
            )
            next_id += 1
            inserted += 1

        conn.commit()

    print(f"\n完成：新增 {inserted} 条，跳过 {skipped} 条（已存在）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
