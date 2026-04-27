# MAP (大类资产配置平台) 后端架构设计规范

## 1. 架构定位与核心思想

MAP 平台的后端架构采用 **Hub & Spoke (枢纽-辐射)** 模式，定位为“轻量级编排中台与 AI 智脑”。
本系统不重复造轮子，不存储海量异构行情明细，而是作为资管体系的**资配指挥中心**。

**核心架构原则 (The Golden Rules):**
1. **消费者驱动契约 (Consumer-Driven Contract)**：MAP 作为需求方，定义并提供标准的 API 接口规范 (Swagger/OpenAPI)。所有被集成的外部系统（数据魔方、组合分析、指令等）必须开发 Adapter（适配器）或防腐层，主动将数据转换为 MAP 要求的格式进行推/拉。
2. **读写分离与双 Hub 隔离**：
   * **Data Hub (数据枢纽)**：负责“读”。对接外部数据源，清洗、统一数据字典（特别是固收类资产的久期、评级、估值等维度），为模型和 UI 提供标准数据。
   * **Service Hub (服务枢纽)**：负责“写”与“算”。对接外部计算与执行引擎，通过工作流引擎（Workflow）串联模型试算、风控检查和指令下发。
3. **AI Native 准备度**：所有 API 设计必须是“大模型友好”的（JSON 结构扁平、语义清晰），为 Alpha Mind 等 AI Agent 自主调用（Function Calling）预留通道。

---

## 2. 逻辑架构图 (Logical Architecture)

```text
+-----------------------------------------------------------------------------------+
|                              MAP 前端交互层 (Vue 2.7)                             |
|  [资配工作台]  |  [模型中心]  |  [观点/因子车间]  |  [AI 助手 Alpha Mind]           |
+-----------------------------------------------------------------------------------+
                                        | (RESTful / GraphQL / WebSocket)
+===================================================================================+
|                             MAP Backend (Hub 层)                                  |
|                                                                                   |
|  +-------------------------+                     +-----------------------------+  |
|  |       Service Hub       |                     |          Data Hub           |  |
|  | (微服务编排 & 任务调度) | <======(融合)======>|  (数据字典 & 缓存 & 向量库) |  |
|  |                         |                     |                             |  |
|  | - 意向组合状态机        |                     | - 基础资产标准化 (Master)   |  |
|  | - 调仓指令生成器        |                     | - 市场行情缓存 (Redis)      |  |
|  | - AI Function 网关      |                     | - 投研知识向量库 (Milvus)   |  |
|  +-------------------------+                     +-----------------------------+  |
+===================================================================================+
       | (MAP 定义接口标准)                               | (MAP 定义数据 Schema)
       v                                                  v
+-----------------------+                      +------------------------------------+
|   内部计算/执行系统   |                      |           内部/外部数据源          |
|  (提供标准 API 实现)  |                      |        (提供标准 Data Feed)        |
+-----------------------+                      +------------------------------------+
| [组合分析] - 绩效/归因|                      | [数据魔方] - 内部持仓/流水         |
| [风控系统] - 事前试算 |                      | [Wind/DM]  - 宏观数据/债券行情     |
| [指令系统] - 交易下发 |                      | [信评系统] - 内部主体/债项评级     |
+-----------------------+                      +------------------------------------+
```

---

## 3. Data Hub 契约设计 (示例)

Data Hub 采用 **拉取缓存 (Pull-and-Cache)** 模式。下游系统无需实时被 MAP 查询打垮，MAP 会在每日盘前/盘后，或由投资经理手动触发时，按照标准化 Schema 拉取数据。

### 3.1 资产主数据接口 (Asset Master)
**MAP 要求外部（如数据魔方）提供的接口格式：**

* **API Path**: `GET /api/v1/map-hub/data/assets/{asset_code}`
* **MAP 核心诉求**: 屏蔽掉外部系统复杂的底层表结构，MAP 只需要资配最核心的指标（以固收为例）。
* **Response Schema (MAP 要求的标准返回)**:
```json
{
  "asset_code": "019686.SH",
  "asset_name": "22附息国债24",
  "asset_class": "FI", 
  "metrics": {
    "price": 102.45,
    "yield_to_maturity": 2.15, 
    "modified_duration": 4.82, 
    "credit_rating_internal": "AAA", 
    "dv01": 0.045
  },
  "update_time": "2026-03-31T09:00:00Z"
}
```

---

## 4. Service Hub 契约设计 (示例)

Service Hub 采用 **事件驱动 (Event-Driven)** 与 **异步调用** 模式。MAP 只是发起方，耗时的计算过程异步返回。

### 4.1 组合试算与归因服务 (集成组合分析系统)
**MAP 要求「组合分析系统」提供的计算接口：**

* **API Path**: `POST /api/v1/map-hub/service/portfolio/simulate`
* **请求体 (MAP 发出的调仓意向)**:
```json
{
  "portfolio_id": "PORT_A001",
  "intent_actions": [
    {"action": "SELL", "asset": "019686.SH", "weight_change": -0.05},
    {"action": "BUY", "asset": "512890.SH", "weight_change": 0.05}
  ],
  "benchmark_id": "BMK_001" 
}
```
* **MAP 核心诉求**: MAP 内部不重写 Brinson 或 Campisi 归因模型，外部系统算完后，严格按照 MAP 要求的视图格式返回，供前端 UI 渲染或 Alpha Mind 大模型解析。
* **Response Schema (MAP 要求的返回格式)**:
```json
{
  "status": "SUCCESS",
  "post_trade_metrics": {
    "expected_return": 0.035,
    "portfolio_duration": 3.1, 
    "tracking_error": 0.012
  },
  "attribution_preview": [
    {"factor": "Asset Allocation", "contribution": 0.01},
    {"factor": "Security Selection", "contribution": 0.02}
  ]
}
```

### 4.2 调仓指令下发服务 (集成指令系统)
* **API Path**: `POST /api/v1/map-hub/service/trade/execute`
* **MAP 核心诉求**: MAP 侧只管理“意向 (Intent)”，一旦通过风控，生成标准指令包丢给下游，由下游去拆单并对接底层的交易终端。
* **Request Schema**:
```json
{
  "intent_snapshot_id": "SNAP_20260331_001",
  "authorizer_id": "PM_007",
  "execution_strategy": "TWAP", 
  "orders": [
    {"ticker": "512890.SH", "side": "BUY", "amount_cny": 5000000}
  ]
}
```

---

## 5. 系统对接协同原则 (SOP)

为保障研发进度与质量，跨部门协同需遵循以下原则：

1. **接口先行 (API-First)**：本 `arc.md` 涉及的 JSON 结构即为强契约。在 MAP 后端开发的第一天，就会生成对应的 Mock Server 供前端联调。
2. **防腐层要求 (Anti-corruption Layer)**：若「数据魔方」或「指令系统」现有接口格式与 MAP 要求不符，原则上由外部系统开发适配器，**MAP 后端不处理异构系统的脏数据清洗逻辑**。
3. **幂等性与重试机制**：所有 Service Hub 发起的 POST/PUT 请求，外部系统必须支持幂等性（基于 `intent_snapshot_id` 或流水号），防止指令重复下发或试算重复记账。