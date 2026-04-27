"""
modules/orchestrator/commands.py — 跨域指令登记与分发

职责：
  1. 将指令写入 pending_commands 表（幂等保障）
  2. 根据 command_type 路由到 MQ 异步投递 或 同步 Adapter 调用
  3. 返回 task_id 供前端轮询 / SSE 监听

指令路由表（COMMAND_ROUTES）：
  - dispatch_mode="MQ"   → 发 RocketMQ 消息，消费者异步处理
  - dispatch_mode="SYNC" → 直接调用对应 Adapter，同步返回结果

新增指令类型时，只需在 COMMAND_ROUTES 中追加一行，无需修改分发逻辑。
"""
import logging
import time
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BusinessRuleException
from app.core.rocketmq_client import MQMessage, mq_producer
from app.modules.orchestrator.models import CommandStatus, PendingCommand

logger = logging.getLogger(__name__)

# ── 指令路由表 ────────────────────────────────────────────────────────────────
# command_type -> dispatch_mode
# MQ:   异步，消费者在 consumers/handlers.py 中处理
# SYNC: 同步，直接调用 Adapter（适合低延迟、强一致场景）

COMMAND_ROUTES: dict[str, str] = {
    # 资配模块
    "SUBMIT_SAA_FOR_APPROVAL": "MQ",
    "PUBLISH_SAA_RESULT": "MQ",
    # 组合模块
    "TRIGGER_PORTFOLIO_REBALANCE": "MQ",
    "SYNC_PORTFOLIO_SNAPSHOT": "SYNC",
    # 投委会模块
    "NOTIFY_IC_RESOLUTION_PUBLISHED": "MQ",
    # 研究模块
    "REQUEST_RESEARCH_REPORT": "MQ",
}


def _make_idempotency_key(command_type: str, payload: dict) -> str:
    """
    生成幂等键。
    优先使用 payload 中的 idempotency_key 字段（调用方显式指定）；
    否则自动生成：{command_type}:{timestamp_ms}
    """
    if explicit := payload.get("idempotency_key"):
        return str(explicit)
    ts_ms = int(time.time() * 1000)
    return f"{command_type}:{ts_ms}"


async def register_and_dispatch(
    db: AsyncSession,
    command_type: str,
    payload: dict,
    user_id: int,
) -> dict:
    """
    登记并分发跨域指令。

    Returns:
        {
            "task_id": int,           # pending_commands.id
            "idempotency_key": str,
            "status": str,            # PENDING / PROCESSING / DONE
            "dispatch_mode": str,     # MQ / SYNC
            "duplicate": bool,        # True 表示幂等命中，返回已有记录
        }
    """
    if command_type not in COMMAND_ROUTES:
        raise BusinessRuleException(
            f"未知指令类型: {command_type}，请在 COMMAND_ROUTES 中注册"
        )

    dispatch_mode = COMMAND_ROUTES[command_type]
    idempotency_key = _make_idempotency_key(command_type, payload)

    # ── 1. 幂等写入 pending_commands ─────────────────────────────────────────
    cmd = PendingCommand(
        command_type=command_type,
        idempotency_key=idempotency_key,
        user_id=user_id,
        payload=payload,
        status=CommandStatus.PENDING,
        dispatch_mode=dispatch_mode,
    )
    db.add(cmd)
    try:
        await db.flush()
        await db.refresh(cmd)
        duplicate = False
    except IntegrityError:
        await db.rollback()
        # 幂等命中：查出已有记录直接返回
        existing = (
            await db.execute(
                select(PendingCommand).where(
                    PendingCommand.idempotency_key == idempotency_key,
                    PendingCommand.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if existing is None:
            raise
        logger.info("Idempotency hit: key=%s task_id=%s", idempotency_key, existing.id)
        return {
            "task_id": existing.id,
            "idempotency_key": idempotency_key,
            "status": existing.status,
            "dispatch_mode": existing.dispatch_mode,
            "duplicate": True,
        }

    # ── 2. 分发 ──────────────────────────────────────────────────────────────
    try:
        if dispatch_mode == "MQ":
            await _dispatch_mq(cmd)
        else:
            await _dispatch_sync(cmd, db)
    except Exception as exc:
        # 分发失败：标记 FAILED，不阻断调用方（异步重试由运维/定时任务处理）
        cmd.status = CommandStatus.FAILED
        cmd.error_message = str(exc)
        await db.flush()
        logger.error("Command dispatch failed: type=%s key=%s err=%s", command_type, idempotency_key, exc)

    return {
        "task_id": cmd.id,
        "idempotency_key": idempotency_key,
        "status": cmd.status,
        "dispatch_mode": dispatch_mode,
        "duplicate": duplicate,
    }


async def _dispatch_mq(cmd: PendingCommand) -> None:
    """投递 RocketMQ 消息，tag 与 command_type 一一对应。"""
    msg = MQMessage(
        topic=settings.ROCKETMQ_TOPIC,
        tag=cmd.command_type,
        body={
            "task_id": cmd.id,
            "command_type": cmd.command_type,
            "user_id": cmd.user_id,
            "payload": cmd.payload,
            "dispatched_at": datetime.now(UTC).isoformat(),
        },
        keys=cmd.idempotency_key,
    )
    sent = await mq_producer.send_message(msg)
    cmd.status = CommandStatus.PROCESSING if sent else CommandStatus.PENDING
    logger.info(
        "MQ dispatch: type=%s task_id=%s sent=%s",
        cmd.command_type, cmd.id, sent,
    )


async def _dispatch_sync(cmd: PendingCommand, db: AsyncSession) -> None:
    """
    同步 Adapter 调用占位。
    各 command_type 的具体 Adapter 调用在此 switch 中扩展。
    """
    result: dict = {}

    if cmd.command_type == "SYNC_PORTFOLIO_SNAPSHOT":
        from app.modules.adapters.portfolio_sys import portfolio_adapter
        result = await portfolio_adapter.fetch_snapshot(cmd.payload)
    else:
        logger.warning("SYNC dispatch not implemented for type=%s", cmd.command_type)
        result = {"warning": "sync handler not implemented"}

    cmd.status = CommandStatus.DONE
    cmd.result = result
    logger.info("SYNC dispatch done: type=%s task_id=%s", cmd.command_type, cmd.id)


async def mark_command_done(db: AsyncSession, task_id: int, result: dict) -> None:
    """将指令标记为 DONE 并写入结果，供 MQ handler 回调使用。"""
    cmd = (
        await db.execute(
            select(PendingCommand).where(
                PendingCommand.id == task_id,
                PendingCommand.is_deleted == 0,
            )
        )
    ).scalar_one_or_none()
    if cmd is None:
        logger.warning("mark_command_done: task_id=%s not found", task_id)
        return
    cmd.status = CommandStatus.DONE
    cmd.result = result
    await db.flush()
    logger.info("Command DONE: task_id=%s", task_id)


async def mark_command_failed(db: AsyncSession, task_id: int, error_message: str) -> None:
    """将指令标记为 FAILED 并写入错误信息，供 MQ handler 回调使用。"""
    cmd = (
        await db.execute(
            select(PendingCommand).where(
                PendingCommand.id == task_id,
                PendingCommand.is_deleted == 0,
            )
        )
    ).scalar_one_or_none()
    if cmd is None:
        logger.warning("mark_command_failed: task_id=%s not found", task_id)
        return
    cmd.status = CommandStatus.FAILED
    cmd.error_message = error_message
    cmd.retry_count = (cmd.retry_count or 0) + 1
    await db.flush()
    logger.error("Command FAILED: task_id=%s err=%s", task_id, error_message)


async def get_command_status(db: AsyncSession, task_id: int) -> dict | None:
    """查询指令执行状态，供前端轮询接口使用。"""
    cmd = (
        await db.execute(
            select(PendingCommand).where(
                PendingCommand.id == task_id,
                PendingCommand.is_deleted == 0,
            )
        )
    ).scalar_one_or_none()

    if cmd is None:
        return None

    return {
        "task_id": cmd.id,
        "command_type": cmd.command_type,
        "status": cmd.status,
        "dispatch_mode": cmd.dispatch_mode,
        "result": cmd.result,
        "error_message": cmd.error_message,
        "retry_count": cmd.retry_count,
        "created_at": cmd.created_at.isoformat() if cmd.created_at else None,
        "updated_at": cmd.updated_at.isoformat() if cmd.updated_at else None,
    }
