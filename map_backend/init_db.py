#!/usr/bin/env python3
"""
init_db.py — 根据 SQLAlchemy 模型在本地 SQLite 中创建表结构

用途：应用启动前的快速本地测试，不连接 TDSQL/MySQL。

用法（在 backend 目录下执行，保证能解析 app 包）：
    cd backend
    python init_db.py

可选参数：
    python init_db.py --db sqlite:///./map_local.sqlite
    python init_db.py --echo

说明：
    - 仅执行 CREATE TABLE，不会迁移数据，也不会删除已有表。
    - 若需重建表，请先手动删除 .sqlite 文件后再运行本脚本。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _ensure_backend_on_path() -> None:
    """允许从任意 cwd 双击运行：将 backend 根目录加入 sys.path。"""
    backend_root = Path(__file__).resolve().parent
    root_str = str(backend_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def main() -> int:
    _ensure_backend_on_path()

    parser = argparse.ArgumentParser(description="Create SQLite tables from SQLAlchemy models.")
    parser.add_argument(
        "--db",
        default="sqlite:///./map_local.sqlite",
        help="SQLAlchemy database URL (default: sqlite in backend dir)",
    )
    parser.add_argument("--echo", action="store_true", help="Echo SQL statements")
    args = parser.parse_args()

    # 导入 Base 与所有 ORM 模块（副作用：向 Base.metadata 注册表）
    from sqlalchemy import create_engine

    from app.core.orm_base import Base

    # 每新增一个含模型的模块，在此追加一行 import 即可
    import app.modules.committee.models  # noqa: F401
    import app.modules.committee.mixed_models  # noqa: F401  ← 混合投委会问卷表
    import app.modules.orchestrator.models  # noqa: F401
    import app.modules.asset_allocation.models  # noqa: F401
    import app.modules.auth.models  # noqa: F401  ← SSO 用户表

    engine = create_engine(
        args.db,
        echo=args.echo,
        future=True,
    )

    Base.metadata.create_all(bind=engine)
    engine.dispose()

    print(f"OK: tables created on {args.db}")
    print("Registered tables:", sorted(Base.metadata.tables.keys()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
