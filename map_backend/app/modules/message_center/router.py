"""
modules/message_center/router.py — 消息中心路由

端点：
  GET  /events/stream       SSE 长连接，前端订阅实时事件
  POST /webhooks/signal     接收外部系统推送的原始信号
"""
import asyncio

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.dependencies import PortalUserID
from app.modules.message_center.scenario_assembler import assemble_and_push
from app.modules.message_center.sse_push import event_stream
from app.modules.message_center.webhooks import RawSignal, normalize_signal

router = APIRouter()


@router.get("/events/stream", summary="SSE 实时事件流")
async def sse_stream(user_id: PortalUserID):
    return StreamingResponse(
        event_stream(user_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/webhooks/signal", summary="接收外部系统原始信号", status_code=202)
async def receive_signal(body: RawSignal):
    signal = normalize_signal(body)
    asyncio.create_task(assemble_and_push(signal))
    return {"accepted": True, "event_type": body.event_type}
