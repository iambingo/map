"""
main.py — FastAPI 应用入口
负责：App 初始化 / 生命周期管理 / 全局中间件 / 路由挂载 / 异常处理器注册。
"""
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import (
    MAPException,
    map_exception_handler,
    unhandled_exception_handler,
)
from app.core.redis_client import close_redis, get_redis
from app.core.rocketmq_client import mq_producer
from app.modules.consumers.worker import consumer_worker


# ── 生命周期 ──────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- startup ----
    await mq_producer.start()
    await consumer_worker.start()
    try:
        await get_redis()
    except Exception:
        pass  # Redis 不可用时降级，不阻断启动
    yield
    # ---- shutdown ----
    await consumer_worker.stop()
    await mq_producer.shutdown()
    await close_redis()
    # 关闭外部系统 HTTP client，防止连接泄漏
    from app.modules.adapters.portfolio_sys import portfolio_adapter
    from app.modules.adapters.risk_sys import risk_adapter
    if hasattr(portfolio_adapter, "aclose"):
        await portfolio_adapter.aclose()
    if hasattr(risk_adapter, "aclose"):
        await risk_adapter.aclose()


# ── App 实例 ──────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── 中间件 ────────────────────────────────────────────────────────────────────

cors_origins = settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or ["*"],
    allow_credentials=bool(cors_origins is not None),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 异常处理器 ────────────────────────────────────────────────────────────────

app.add_exception_handler(MAPException, map_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, unhandled_exception_handler)

# ── 路由挂载 ──────────────────────────────────────────────────────────────────

from app.modules.committee.router import router as committee_router
from app.modules.committee.mixed_router import router as mixed_committee_router
from app.modules.workspace.router import router as workspace_router
from app.modules.orchestrator.router import router as orchestrator_router
from app.modules.asset_allocation.router import router as asset_allocation_router
from app.modules.message_center.router import router as message_center_router
from app.modules.auth.router import router as auth_router
from app.modules.auth.sso_router import router as sso_router

app.include_router(committee_router, prefix="/api/v1/committee", tags=["Committee"])
app.include_router(mixed_committee_router, prefix="/api/v1/committee", tags=["混合投委会-问卷"])
app.include_router(workspace_router, prefix="/api/v1/workspace", tags=["Workspace"])
app.include_router(orchestrator_router, prefix="/api/v1/orchestrator", tags=["Orchestrator"])
app.include_router(asset_allocation_router, prefix="/api/v1/asset-allocation", tags=["AssetAllocation"])
app.include_router(message_center_router, prefix="/api/v1/messages", tags=["MessageCenter"])

# SSO 回调端点挂在根路径（门户回调 URL）
app.include_router(sso_router, prefix="", tags=["SSO"])
# 认证相关 API 端点
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    return {"status": "ok", "version": settings.APP_VERSION, "env": settings.APP_ENV}


# ── 本地开发直接运行 ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
