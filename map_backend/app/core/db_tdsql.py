"""
core/db_tdsql.py — 异步数据库引擎与 Session 工厂
封装 SQLAlchemy 2.0 AsyncEngine / AsyncSession；ORM 基类见 `orm_base.py`。

延迟初始化说明：
  不在模块 import 时立刻 create_async_engine，避免 uvicorn --reload 子进程
  或 PATH 混用导致「缺 aiomysql」时在启动阶段直接 ModuleNotFoundError。
  首次进入 get_db()（或显式访问 engine / AsyncSessionFactory）时才创建引擎。
⚠️  禁止在此处编写任何业务逻辑。
"""
from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.orm_base import Base

# ── 延迟引擎（首次 get_db / 访问 engine 时初始化）──────────────────────────────

_engine: AsyncEngine | None = None
AsyncSessionFactory: async_sessionmaker[AsyncSession] | None = None


def _ensure_engine_and_factory() -> async_sessionmaker[AsyncSession]:
    global _engine, AsyncSessionFactory
    if AsyncSessionFactory is not None:
        return AsyncSessionFactory

    url = settings.DATABASE_URL
    if url.startswith("sqlite"):
        try:
            import aiosqlite  # noqa: F401
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "已启用 MAP_USE_SQLITE，但缺少 aiosqlite。请执行：\n"
                "  cd backend\n"
                "  .\\venv\\Scripts\\pip install aiosqlite\n"
                "或 pip install -r requirements.txt"
            ) from exc
        _engine = create_async_engine(url, echo=settings.DEBUG)
    else:
        try:
            import aiomysql  # noqa: F401
            import pymysql  # noqa: F401
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "缺少 MySQL 异步驱动。请在「运行 uvicorn 的同一解释器」中安装：\n"
                "  cd backend\n"
                "  .\\venv\\Scripts\\pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple\n"
                "或执行 .\\install_deps.ps1\n"
                "若 conda base 与 venv 同时激活，请优先使用 .\\run_dev.ps1 启动。\n"
                "若本机未安装 MySQL，可在 .env 中设置 MAP_USE_SQLITE=true 使用本地 SQLite。"
            ) from exc

        _engine = create_async_engine(
            url,
            echo=settings.DEBUG,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_pre_ping=True,
        )
    AsyncSessionFactory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return AsyncSessionFactory


def __getattr__(name: str) -> AsyncEngine | async_sessionmaker[AsyncSession]:
    """PEP 562：延迟导出 engine / AsyncSessionFactory。"""
    if name == "engine":
        _ensure_engine_and_factory()
        assert _engine is not None
        return _engine
    if name == "AsyncSessionFactory":
        return _ensure_engine_and_factory()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Base 定义见 app.core.orm_base（此处 re-export，兼容 from app.core.db_tdsql import Base）
__all__ = ["Base", "engine", "AsyncSessionFactory", "get_db"]


# ── Session 依赖 ───────────────────────────────────────────────────────────────


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 异步 Session 生成器。
    用法示例：
        async def endpoint(db: AsyncSession = Depends(get_db)): ...
    事务在正常退出时自动提交，异常时回滚。
    """
    factory = _ensure_engine_and_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
