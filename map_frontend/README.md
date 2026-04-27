# MAP · 大类资产管理平台

Multi-Asset Platform —— 面向机构投资者的大类资产配置与组合管理系统。

---

## 项目结构

```
MAP/
├── docs/                   # 项目文档
│   ├── prd.md              # 产品需求文档
│   ├── arc.md              # 技术架构文档
│   └── project.md          # 项目进度文档
├── frontend/               # Vue 2.7 前端
│   ├── src/
│   │   ├── api/            # 接口定义
│   │   ├── components/     # 组件（ui/ + charts/ + common/）
│   │   ├── composables/    # 组合式函数
│   │   ├── layouts/        # 页面布局
│   │   ├── pages/          # 路由页面
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── types/          # TypeScript 类型
│   │   └── utils/          # 工具函数
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.ts
├── backend/                # Spring Boot 3 后端
│   ├── src/main/java/com/map/
│   │   ├── config/         # Spring 配置类
│   │   ├── controller/     # REST 控制器
│   │   ├── service/        # 业务逻辑层
│   │   ├── mapper/         # MyBatis-Plus Mapper
│   │   ├── entity/         # 数据库实体
│   │   ├── dto/            # 请求/响应 DTO
│   │   └── common/         # 公共组件（Result、异常处理等）
│   ├── src/main/resources/
│   │   └── application.yml
│   └── pom.xml
└── reference/              # 开发规范 & 参考资料
    └── tec.md
```

---

## 技术栈

| 端 | 技术 |
|---|---|
| 前端 | Vue 2.7 · TypeScript · Vite 7 · Tailwind CSS 4 · Pinia · shadcn-vue · Axios · vue-query · Zod 4 |
| 后端 | Java 17 · Spring Boot 3 · MyBatis-Plus 3.5 · Spring Security |
| 数据库 | PostgreSQL 15 · Redis 7 |

---

## 快速开始

### 前端

```bash
cd frontend
npm install
npm run dev      # 启动开发服务器，默认 http://localhost:5173
```

### 后端

```bash
cd backend
./mvnw spring-boot:run   # 启动 Spring Boot，默认 http://localhost:8080
```

### 本地数据库（Docker）

```bash
docker run -d --name map-postgres \
  -e POSTGRES_DB=map_db \
  -e POSTGRES_USER=map_user \
  -e POSTGRES_PASSWORD=map_pass \
  -p 5432:5432 postgres:15

docker run -d --name map-redis \
  -p 6379:6379 redis:7
```

---

## 文档

- [产品需求文档 (PRD)](./docs/prd.md)
- [技术架构文档 (ARC)](./docs/arc.md)
- [项目进度文档 (PROJECT)](./docs/project.md)
