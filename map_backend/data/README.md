# MAP — 投研一体化平台

智能事件中枢 (Orchestrator)、智能门户 (BFF)、MAP 自有资配大脑。

## 快速开始

### 1. 启动数据库（Docker）

```bash
docker compose up -d
```

首次启动时会自动执行 `docker/mysql/init/01_init_schema_and_data.sql`，建表并载入示例数据。

### 2. 启动后端

```bash
cd map_backend
# 安装依赖
pip install -r requirements.txt
# 启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端默认连接 Docker 中的 MySQL（`.env` 已配好）。API 文档：http://127.0.0.1:8000/docs

### 3. 启动前端

```bash
cd map_frontend
npm install
npm run dev
```

访问：http://127.0.0.1:3000

## 连接信息

| 组件 | 地址 |
|------|------|
| 后端 API | http://127.0.0.1:8000 |
| 前端页面 | http://127.0.0.1:3000 |
| MySQL | 127.0.0.1:3306 (user: mapuser / pass: mappass) |

## 技术栈

- **后端**: Python 3.10+ / FastAPI / SQLAlchemy async / MySQL 8.0
- **前端**: Vue 3 / TypeScript / Vite / Element Plus / TailwindCSS / ECharts
- **基础设施**: Docker Compose / Redis (可选) / RocketMQ (可选)

## 架构

```
map_backend/app/
├── core/                      # 基座域：配置、DB、安全、Redis
├── modules/
│   ├── committee/             # 投委会决策（含混合投委会问卷）
│   ├── workspace/             # 智能门户 BFF（九宫格 + 快照缓存）
│   ├── asset_allocation/      # 资产配置（SAA 规则引擎）
│   ├── orchestrator/          # 跨域指令分发
│   ├── message_center/        # 消息中心（SSE + Webhook）
│   ├── adapters/              # 防腐层（外部系统适配）
│   └── consumers/             # MQ 消费者
```

## 数据库说明

本地开发使用 Docker MySQL 8.0，兼容公司内网 TDSQL（MySQL 协议完全兼容）。
初始化脚本 `docker/mysql/init/01_init_schema_and_data.sql` 包含完整表结构和示例数据，
clone 后 `docker compose up -d` 即可直接使用，无需手动建表。
