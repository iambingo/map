# MAP 后端本地开发环境 — 启动指南

## 前置条件

| 组件 | 版本/说明 |
|------|-----------|
| Python | 3.12+ |
| Docker Desktop | 必须运行中（Windows 下先打开 Docker Desktop 等它就绪） |

可选组件（未启动时自动降级）：
- **Redis**：未启动时自动跳过，不影响功能
- **RocketMQ**：未配置时使用 Mock 模式，不影响功能

---

## 方式一：完整模式（MySQL + 完整功能）

### 第 1 步：确认 Docker Desktop 在运行

在任务栏右下角看到 Docker 图标（绿色表示运行中）即可。**必须先开 Docker，否则后面的 `docker compose up` 会失败。**

### 第 2 步：启动 MySQL 容器

```powershell
cd D:\Desktop\MAP项目
docker compose up -d
```

容器名 `map_tdsql`，端口 `127.0.0.1:5400`，账号 `mapuser / mappass`。

**如需清空数据重建**（比如种子数据乱码时）：
```powershell
docker compose down -v   # 删除数据卷
docker compose up -d     # 重建，会自动执行 init SQL
```

### 第 3 步：安装 Python 依赖

```powershell
cd D:\Desktop\MAP项目\map_backend

# 首次需要创建 venv
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\activate

# 安装依赖（首次或 requirements.txt 变更时执行）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> **注意**：必须激活 venv 后再安装，确保依赖装在正确的解释器里。
> 如果 `requirements.txt` 安装时报 `UnicodeDecodeError`，说明文件编码有问题，重新下载或保存为 UTF-8-BOM 格式。

### 第 4 步：初始化数据库表

```powershell
# 通过 init_db.py 创建表结构（使用同步引擎直接连 MySQL）
python -c "
import asyncio
from app.core.db_tdsql import engine
from app.core.orm_base import Base
import app.modules.committee.models
import app.modules.committee.mixed_models
import app.modules.orchestrator.models
import app.modules.asset_allocation.models
import app.modules.auth.models

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

asyncio.run(main())
print('Tables created.')
"
```

或使用 `init_db.py` 走同步连接（需要额外安装 `pymysql`）：
```powershell
python init_db.py --db "mysql+pymysql://mapuser:mappass@127.0.0.1:5400/mapdb?charset=utf8mb4"
```

### 第 5 步：（可选）灌入演示数据

```powershell
python seed_mixed.py
```

### 第 6 步：启动开发服务器

```powershell
# 方式 A：用虚拟环境的 python 直接运行
.\venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 方式 B：已激活 venv 的情况下
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动成功后访问：
- **API 文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

### 验证

```powershell
# 健康检查
curl http://localhost:8000/health

# 问卷汇总接口（验证中文编码是否正常）
curl http://localhost:8000/api/v1/committee/mixed/sessions
```

---

## 方式二：最简模式（SQLite，无需 Docker）

不需要 MySQL/Redis/RocketMQ，适合快速跑通代码。

```powershell
cd D:\Desktop\MAP项目\map_backend

# 创建 venv（首次）
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 创建 SQLite 数据库表
python init_db.py

# 设置环境变量使用 SQLite
$env:MAP_USE_SQLITE = "true"

# 启动
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 方式三：一键启动脚本

如果 venv 和依赖都已经装好：

```powershell
cd D:\Desktop\MAP项目\map_backend
.\run_dev.ps1
```

> `run_dev.ps1` 仅启动 uvicorn，不会自动创建 venv 或安装依赖。
> 如果脚本报错 `ModuleNotFoundError`，说明 venv 里缺依赖，回到方式一第 3 步重新装。

---

## 端口清单

| 服务 | 端口 | 说明 |
|------|------|------|
| FastAPI / Uvicorn | 8000 | 后端主服务 |
| MySQL (Docker) | 5400 | 数据库，Docker 映射端口 |

---

## 认证说明

本地 `DEBUG=true` 模式下，所有接口自动使用 `user_id=1`，无需 SSO 登录：

```powershell
# 直连测试（无需 token）
curl http://localhost:8000/api/v1/committee/meetings
curl http://localhost:8000/api/v1/workspace/navigation
```

如需手动模拟认证：

```powershell
# 生成测试 JWT
.\venv\Scripts\python -c "from app.core.security import create_access_token; print(create_access_token(subject=1))"

# 携带 token 请求
curl -H "Authorization: Bearer <上面输出的token>" http://localhost:8000/api/v1/auth/me
```

---

## 常见问题

### Docker Desktop 没有运行

`docker compose up -d` 会报错。必须先打开 Docker Desktop，等状态栏图标变绿后再执行。

### `pip install` 报 `UnicodeDecodeError: 'gbk' codec can't decode`

Windows 下 pip 读取 `requirements.txt` 时可能用 GBK 解码。该文件已保存为 UTF-8 with BOM，如果仍有问题，可以尝试：
```powershell
pip install -r requirements.txt --no-cache-dir
```

### MySQL 容器启动后连不上

检查容器状态：
```powershell
docker ps | Select-String map_tdsql
```
如果没有运行，查看日志：
```powershell
docker logs map_tdsql
```

### 种子数据中文乱码

MySQL 容器首次启动时执行了 init SQL，如果当时文件编码不对就会存成乱码。解决：
```powershell
docker compose down -v    # 清空数据
docker compose up -d      # 重建，会重新执行 init SQL（确保 .sql 文件是 UTF-8 编码）
```

### `ModuleNotFoundError: No module named 'xxx'`

说明依赖没装在运行 uvicorn 的那个解释器里。确认：
```powershell
# 用 venv 里的 python 启动，不要直接用全局 python
.\venv\Scripts\python -m uvicorn app.main:app --reload
```

---

## 环境变量配置

核心配置在 `.env` 文件中，常见需要调整的：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `MAP_USE_SQLITE` | `false` | 设为 `true` 使用 SQLite |
| `DB_PORT` | `5400` | MySQL 端口 |
| `DEBUG` | `true` | 开发模式免认证 |
| `SECRET_KEY` | `dev-secret-key...` | **生产环境必须更换** |
| `CORS_ORIGINS` | `*` | 生产环境改为前端域名 |
