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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- 请将以下 CORS 配置代码块原封不动地加在 app = FastAPI() 之后 ---
app.add_middleware(
    CORSMiddleware,
    # 允许所有本地来源的请求 (开发阶段用 "*" 最省事)
    # 如果你想严谨一点，可以写成 ["http://localhost:5173", "http://127.0.0.1:5173"]
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], # 允许所有请求方法 (GET, POST, OPTIONS 等)
    allow_headers=["*"], # 允许所有请求头
)
# ----------------------------------------------------------------

# 下面是你原有的路由代码...
# @app.get("/workspace/portal-snapshot")
# def get_snapshot():
#     ...
# ── 生命周期 ──────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- startup ----
    await mq_producer.start()
    await get_redis()   # 预热连接池，首个请求无冷启动延迟
    yield
    # ---- shutdown ----
    await mq_producer.shutdown()
    await close_redis()


# ── App 实例 ──────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ── 中间件 ────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 异常处理器 ────────────────────────────────────────────────────────────────

app.add_exception_handler(MAPException, map_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, unhandled_exception_handler)

# ── 路由挂载 ─────────────────────────────────────────────────────────────────-
# 完整 URL：无尾随斜杠。例：GET /api/v1/committee/page-context
# 前端 Axios baseURL=/api、path=/v1/committee/page-context → 与本处一致。
# 前端纯 Mock 联调：frontend/.env 设 VITE_COMMITTEE_OFFLINE_MOCK=true 可跳过上述 BFF 请求（见 demoStore）。
from app.modules.committee.router import router as committee_router
from app.modules.workspace.router import router as workspace_router

app.include_router(committee_router, prefix="/api/v1/committee", tags=["Committee"])
app.include_router(workspace_router, prefix="/api/v1/workspace", tags=["Workspace"])


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    return {"status": "ok", "version": settings.APP_VERSION, "env": settings.APP_ENV}


# ── 本地开发直接运行 ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
