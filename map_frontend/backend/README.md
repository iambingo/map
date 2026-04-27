# MAP Backend - AI 编程架构指南与约束

## 1. 核心定位 (System Philosophy)
* **系统角色:** 智能事件中枢 (Orchestrator)、智能门户 (BFF)、MAP自有资配大脑。
* **设计底线:**
  - 拒绝在本项目内做重度的风控、回测等底层计算，交由外部系统。
  - 首页体验至上，利用柔性缓存抗住高并发，绝不因外部系统缓慢而阻塞。

## 2. 技术栈 (Tech Stack)
* **语言与框架:** Python 3.10+ / FastAPI (异步优先)
* **数据库:** TDSQL (MySQL InnoDB，使用异步 SQLAlchemy)
* **通信与中间件:** `httpx` (异步 HTTP 调用)、RocketMQ (MQ 事件消费)
* **数据校验:** Pydantic V2

---

# MAP 投研一体化平台后端 - AI 编程架构指南与约束 (RocketMQ版)

## 1. 核心定位 (System Philosophy)
* **系统角色:** 事件中枢 (Orchestrator)、智能门户 (BFF)、MAP自有资配大脑。
* **设计底线:**
  - 拒绝在本项目内做重度的风控、回测等底层计算，交由外部系统。
  - 首页体验至上，利用柔性缓存抗住高并发，绝不因外部系统缓慢而阻塞。

## 2. 技术栈 (Tech Stack)
* **语言与框架:** Python 3.10+ / FastAPI (异步优先)
* **数据库:** TDSQL (MySQL InnoDB，使用异步 SQLAlchemy)
* **通信中间件:** `httpx` (异步 HTTP 调用)
* **消息队列:** RocketMQ (利用其事务消息保障状态一致性，利用 Tag 进行业务路由)
* **数据校验:** Pydantic V2

---

## 3. 强制目录树骨架 (Strict Directory Tree)
> **【注意】：** 在创建或修改文件时，必须严格遵守以下物理目录结构！禁止自行发明新的根目录或跨域揉捏文件。

```text
map_backend/
├── app/
│   ├── core/                        # 【基座域】全局配置与引擎（禁止包含业务逻辑）
│   │   ├── config.py                
│   │   ├── exceptions.py            
│   │   ├── security.py              
│   │   ├── db_tdsql.py              
│   │   └── rocketmq_client.py       # RocketMQ 生产者与消费者初始化封装
│   │
│   ├── modules/                     # 【业务域】各模块高度内聚
│   │   ├── workspace/               # 📍 智能门户 (BFF)
│   │   │   ├── navigation.py        # 九宫格动态布局计算引擎
│   │   │   ├── widget_snapshot.py   # TDSQL JSON 柔性快照管理
│   │   │   └── router.py            
│   │   │
│   │   ├── asset_allocation/        # 📍 MAP自有业务 (资配主观微调)
│   │   │   ├── domain/              # --- 纯 Python 规则引擎，零外部依赖 ---
│   │   │   │   └── saa_calculator.py
│   │   │   ├── repository.py        # TDSQL 存取草稿与最终版本
│   │   │   ├── services.py          
│   │   │   └── router.py            
│   │   │
│   │   ├── orchestrator/            # 📍 跨域发令枪
│   │   │   ├── commands.py          # 接收指令，登记待办，触发外部调用或发送事务消息
│   │   │   └── router.py            
│   │   │
│   │   ├── message_center/          # 📍 统一信息流与智能场景组装 (更新点 🌟)
│   │   │   ├── webhooks.py          # 接收外部 API 推送的极简原始信号 (Raw Signals)
│   │   │   ├── scenario_assembler.py# 场景组装引擎 (结合本地 TDSQL 画像)
│   │   │   ├── deep_link_engine.py  # 深链接生成器
│   │   │   ├── sse_push.py          # SSE 长连接实时推送
│   │   │   └── router.py            
│   │   │
│   │   ├── adapters/                # 📍 防腐层 (对外 HTTP/RPC 请求)
│   │   │   ├── portfolio_sys.py     
│   │   │   ├── risk_sys.py          
│   │   │   └── base.py              # 必须实现硬超时与重试的拦截基类
│   │   │
│   │   └── consumers/               # 📍 事件消费者 (监听 RocketMQ)
│   │       ├── handlers.py          # 根据 Tag 路由到不同处理逻辑
│   │       └── worker.py            # 常驻后台 RocketMQ 守护进程
│   │
│   ├── main.py                      # FastAPI App 初始化入口
│   └── dependencies.py              # 依赖注入 (如获取 DB Session)


4. 架构开发纪律 (Architectural Guidelines)
【AI 助手注意】：在具体实现业务逻辑时，无需死板硬套，请根据具体上下文，灵活运用以下四大原则。

原则 1: 灵活的“快慢车道”分流 (Sync vs. Async Flow)
在设计 API 或业务流时，需根据物理耗时预期决定流转模式：

快车道 (同步流): 如果业务是纯本地规则运算（如 asset_allocation 内的权重计算），或单纯读取本地快照数据，请保持架构极简，直接同步 await 执行并返回最终结果。

慢车道 (异步事件流): 如果需要调用外部沉重的计算资源（如深度组合模拟），请果断切断 HTTP 阻塞。采用“记录任务 -> 抛出指令 -> 立即向前端响应（如排队中） -> 监听 MQ 异步结果 -> SSE 推送前端”的闭环。

原则 2: 防腐与边界隔离 (Anti-Corruption Layer)
保护 MAP 的纯洁性，不要让外部系统的混乱污染本地代码。

所有外部 API 的对接代码必须关在 adapters/ 目录下。

必须在 Adapter 中捕获外部系统的原始 JSON，将其“翻译”为 MAP 内部标准的 Pydantic 模型后再向上层返回。

外部调用必须有超时意识（Timeout），绝不允许无限期挂起。

原则 3: 柔性快照与优雅降级 (Graceful Degradation)
工作台看板数据的核心准则是“不能卡”。

读取外部卡片汇总时，优先从 TDSQL (widget_snapshots 表) 读取 JSON 快照。

如果快照缺失或过期，再去触发 Adapter 获取最新数据并覆写数据库。

降级底线： 如果外部系统宕机或超时，必须捕获异常，并提取哪怕过期的旧快照返回给前端（可附加提示标识），绝不允许直接向前端抛出 500 错误导致白屏。

原则 4: 本地领域的纯洁性 (Domain Purity)
asset_allocation/domain/ 下的业务规则代码，应尽可能保持为纯粹的 Python 函数。隔离数据库 Session 和网络框架对象（Request），使其极度容易进行单元测试。
