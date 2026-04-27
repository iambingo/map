"""
modules/orchestrator/commands.py — 跨域指令登记与分发（骨架）
职责：接收指令 -> 持久化待办 -> 触发外部调用或发送事务 MQ 消息。
"""


async def register_and_dispatch(command_type: str, payload: dict, user_id: int) -> dict:
    """
    1. 将指令写入 TDSQL pending_commands 表（保障幂等）
    2. 根据 command_type 决定走同步 Adapter 或异步 MQ 事件
    3. 返回 task_id 供前端轮询 / SSE 监听
    """
    raise NotImplementedError
