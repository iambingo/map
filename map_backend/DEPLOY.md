# MAP 后端运行与部署指南

## 本地开发环境启动

### 前置条件

| 组件 | 必须？ | 说明 |
|------|--------|------|
| Python 3.12+ | 必须 | |
| TDSQL (MySQL 8.0) | 推荐 | 通过 `docker compose up -d` 启动，或使用 SQLite 模式跳过 |
| Redis | 可选 | 未启动时自动降级，不影响功能 |
| RocketMQ | 可选 | 未安装时使用 Mock 模式 |

### 快速启动（最简模式）

不需要任何外部依赖，一条命令即可：

```powershell
# 在 map_backend 目录下
.\install_deps.ps1   # 首次运行或依赖变更时执行，安装到 backend\venv

# 使用 SQLite 模式启动（无需 MySQL/Redis/RocketMQ）
$env:MAP_USE_SQLITE = "true"
.\run_dev.ps1
```

启动成功后访问：
- **API 文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

### 完整模式（含 TDSQL + Redis + RocketMQ）

```powershell
# 1. 启动 TDSQL
cd D:\Desktop\MAP项目
docker compose up -d

# 2. 初始化数据库（创建表结构）
cd map_backend
python init_db.py --db "mysql+aiomysql://mapuser:mappass@127.0.0.1:5400/mapdb?charset=utf8mb4"

# 3. 启动后端
.\run_dev.ps1
```

### 认证说明

本地 `DEBUG=true` 模式下，所有接口自动使用 `user_id=1`，无需 SSO 登录：

```powershell
# 直连测试（无需 token）
curl http://localhost:8000/api/v1/committee/meetings
curl http://localhost:8000/api/v1/workspace/navigation
curl http://localhost:8000/api/v1/asset-allocation/classes
```

如需手动模拟认证（模拟 SSO 登录后的请求）：

```powershell
# 1. 生成一个测试 JWT
python -c "from app.core.security import create_access_token; print(create_access_token(subject=1))"

# 2. 在请求头中携带
curl -H "Authorization: Bearer <上面输出的token>" http://localhost:8000/api/v1/auth/me
```

### 端口清单

| 服务 | 端口 | 用途 |
|------|------|------|
| FastAPI / Uvicorn | 8000 | 后端主服务 |
| TDSQL (MySQL) | 5400 | 数据库（Docker 映射） |
| Redis | 6379 | 缓存 |
| RocketMQ | 9876 | 消息队列 |

### 常用运维脚本

| 脚本 | 功能 |
|------|------|
| `.\run_dev.ps1` | 启动开发服务器（热重载） |
| `.\install_deps.ps1` | 安装/更新 Python 依赖到 `venv` |
| `python init_db.py` | 创建/更新数据库表（SQLite 或 TDSQL） |
| `docker compose down -v` | 清空 TDSQL 数据（谨慎使用） |

---

## 生产环境部署

### 配置变更清单

以下配置项必须从开发值改为生产值：

| 配置项 | 开发值 | 生产值 | 说明 |
|--------|--------|--------|------|
| `APP_ENV` | `development` | `production` | |
| `DEBUG` | `true` | `false` | |
| `SECRET_KEY` | `dev-secret-key-change-in-production` | **必须更换为随机密钥** | |
| `DB_HOST` | `127.0.0.1` | 生产 TDSQL 地址 | |
| `DB_USER` / `DB_PASSWORD` | `mapuser` / `mappass` | 生产账号 | |
| `REDIS_HOST` | `127.0.0.1` | 生产 Redis 地址 | |
| `ROCKETMQ_NAME_SERVER` | `127.0.0.1:9876` | 生产 RocketMQ 地址 | |
| `SSO_LOGIN_REDIRECT_URL` | `http://localhost:5173` | 生产前端地址 | |
| `CORS_ORIGINS` | `*` | 前端实际域名 | |
| `PORTFOLIO_SYS_URL` | 空 | 组合系统 API 地址 | 可选 |
| `RISK_SYS_URL` | 空 | 风控系统 API 地址 | 可选 |

### CORS 配置

只需在 `.env` 中配置，无需改代码：

```ini
CORS_ORIGINS=https://your-frontend-domain.com
```

### SSO 回调配置

在公司统一门户后台配置回调 URL：

```
https://your-backend-domain/auth/sso-callback
```

### 部署前检查清单

- [ ] `SECRET_KEY` 已更换为高强度随机密钥
- [ ] `DEBUG` 设为 `false`
- [ ] `APP_ENV` 设为 `production`
- [ ] 数据库、Redis、RocketMQ 地址已更新
- [ ] `SSO_LOGIN_REDIRECT_URL` 指向生产前端
- [ ] `CORS_ORIGINS` 已指定前端域名
- [ ] `map_users` 表已创建
- [ ] 门户后台已配置 SSO 回调 URL

### 健康检查

```
GET https://your-backend-domain/health
```

返回：
```json
{"status": "ok", "version": "0.1.0", "env": "production"}
```

### 启动命令（生产）

生产环境建议使用 Gunicorn + Uvicorn workers：

```bash
gunicorn app.main:app \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker
```

---

## 无需修改的项

| 配置项 | 说明 |
|--------|------|
| `SSO_VALIDATE_URL` | 默认值已指向门户生产校验接口 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 8 小时，按需调整 |
| `EXTERNAL_HTTP_TIMEOUT` | 10s |
| `EXTERNAL_HTTP_RETRIES` | 3 次 |
