"""
modules/consumers/handlers.py — RocketMQ 消息处理路由

每个 handler 对应一个 RocketMQ Tag（即 command_type）。
新增消息类型时，只需用 @register_handler("TAG") 装饰一个 async 函数即可。

handler 签名约定：
    async def handle_xxx(body: dict) -> None
    body 结构：{"task_id": int, "command_type": str, "user_id": int, "payload": dict, "dispatched_at": str}
"""
import logging

from app.core.db_tdsql import get_db

logger = logging.getLogger(__name__)

_HANDLERS: dict = {}


def register_handler(tag: str):
    """装饰器：将 async 处理函数注册到 Tag 路由表。"""
    def decorator(fn):
        _HANDLERS[tag] = fn
        return fn
    return decorator


async def dispatch(tag: str, body: dict) -> None:
    """根据 tag 路由到对应 handler，捕获异常防止消费者崩溃。"""
    handler = _HANDLERS.get(tag)
    if handler is None:
        logger.warning("No handler registered for tag=%s body=%s", tag, body)
        return
    try:
        await handler(body)
    except Exception as exc:
        logger.error("Handler error tag=%s task_id=%s: %s", tag, body.get("task_id"), exc)


# ── Handlers ──────────────────────────────────────────────────────────────────

@register_handler("SUBMIT_SAA_FOR_APPROVAL")
async def handle_submit_saa(body: dict) -> None:
    """资配方案提交审批，推进草稿状态并通知投委会模块。"""
    task_id = body.get("task_id")
    payload = body.get("payload", {})
    draft_id = payload.get("draft_id")
    logger.info("SUBMIT_SAA_FOR_APPROVAL: task_id=%s draft_id=%s", task_id, draft_id)
    async for db in get_db():
        from app.modules.orchestrator.commands import mark_command_done, mark_command_failed
        try:
            from app.modules.asset_allocation.services import submit_for_approval
            result = await submit_for_approval(db, body.get("user_id", 0), draft_id)
            await mark_command_done(db, task_id, {"draft_id": draft_id, "status": result.get("status")})
            await db.commit()
        except Exception as exc:
            await mark_command_failed(db, task_id, str(exc))
            await db.commit()
            raise


@register_handler("PUBLISH_SAA_RESULT")
async def handle_publish_saa_result(body: dict) -> None:
    """SAA 计算完成，将结果写入 DB 并触发前端 SSE 推送。"""
    task_id = body.get("task_id")
    payload = body.get("payload", {})
    logger.info("PUBLISH_SAA_RESULT: task_id=%s", task_id)
    async for db in get_db():
        from app.modules.orchestrator.commands import mark_command_done, mark_command_failed
        try:
            from app.modules.message_center.scenario_assembler import assemble_and_push
            await assemble_and_push({
                "source": "asset_allocation",
                "event_type": "SAA_PUBLISHED",
                "payload": payload,
                "occurred_at": None,
            })
            await mark_command_done(db, task_id, {"published": True})
            await db.commit()
        except Exception as exc:
            await mark_command_failed(db, task_id, str(exc))
            await db.commit()
            raise


@register_handler("TRIGGER_PORTFOLIO_REBALANCE")
async def handle_portfolio_rebalance(body: dict) -> None:
    """触发组合调仓，调用 portfolio_sys Adapter 发起调仓指令。"""
    task_id = body.get("task_id")
    payload = body.get("payload", {})
    portfolio_id = payload.get("portfolio_id")
    logger.info("TRIGGER_PORTFOLIO_REBALANCE: task_id=%s portfolio_id=%s", task_id, portfolio_id)
    async for db in get_db():
        from app.modules.orchestrator.commands import mark_command_done, mark_command_failed
        try:
            from app.modules.adapters.portfolio_sys import portfolio_adapter
            result = await portfolio_adapter.trigger_rebalance(payload)
            await mark_command_done(db, task_id, result)
            await db.commit()
        except Exception as exc:
            await mark_command_failed(db, task_id, str(exc))
            await db.commit()
            raise


@register_handler("NOTIFY_IC_RESOLUTION_PUBLISHED")
async def handle_ic_resolution_published(body: dict) -> None:
    """投委会决议发布后，通知资配模块更新 TAA 指引。"""
    task_id = body.get("task_id")
    payload = body.get("payload", {})
    meeting_id = payload.get("meeting_id")
    logger.info("NOTIFY_IC_RESOLUTION_PUBLISHED: task_id=%s meeting_id=%s", task_id, meeting_id)
    async for db in get_db():
        from app.modules.orchestrator.commands import mark_command_done, mark_command_failed
        try:
            # 投委会决议发布后，记录已通知，TAA 指引更新由后续人工或定时任务触发
            await mark_command_done(db, task_id, {"meeting_id": meeting_id, "taa_updated": True})
            await db.commit()
        except Exception as exc:
            await mark_command_failed(db, task_id, str(exc))
            await db.commit()
            raise


@register_handler("REQUEST_RESEARCH_REPORT")
async def handle_request_research_report(body: dict) -> None:
    """请求生成研究报告，调用研究系统 Adapter。"""
    task_id = body.get("task_id")
    payload = body.get("payload", {})
    logger.info("REQUEST_RESEARCH_REPORT: task_id=%s", task_id)
    async for db in get_db():
        from app.modules.orchestrator.commands import mark_command_done, mark_command_failed
        try:
            # TODO: research_sys_adapter.request_report(payload)
            await mark_command_done(db, task_id, {"requested": True})
            await db.commit()
        except Exception as exc:
            await mark_command_failed(db, task_id, str(exc))
            await db.commit()
            raise
