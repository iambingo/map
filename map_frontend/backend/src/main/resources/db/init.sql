-- MAP 大类资产管理平台 · 数据库初始化脚本
-- PostgreSQL 15

-- ─── 扩展 ──────────────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── 用户表 ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sys_user (
    id          BIGSERIAL PRIMARY KEY,
    username    VARCHAR(64)  NOT NULL UNIQUE,
    password    VARCHAR(128) NOT NULL,
    nickname    VARCHAR(64)  NOT NULL,
    email       VARCHAR(128),
    role        VARCHAR(32)  NOT NULL DEFAULT 'VIEWER',
    avatar      VARCHAR(256),
    enabled     BOOLEAN      NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_by  BIGINT,
    is_deleted  BOOLEAN      NOT NULL DEFAULT FALSE
);

-- ─── 大类资产类别 ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS asset_category (
    id          BIGSERIAL PRIMARY KEY,
    code        VARCHAR(32)  NOT NULL UNIQUE,
    name        VARCHAR(64)  NOT NULL,
    name_en     VARCHAR(64),
    description TEXT,
    color       VARCHAR(16),
    icon        VARCHAR(64),
    enabled     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_by  BIGINT,
    is_deleted  BOOLEAN      NOT NULL DEFAULT FALSE
);

-- ─── 资产配置表（SAA / TAA） ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS asset_class_config (
    id               BIGSERIAL PRIMARY KEY,
    category_id      BIGINT       NOT NULL REFERENCES asset_category(id),
    saa_weight       NUMERIC(6,2) NOT NULL DEFAULT 0,
    taa_weight_min   NUMERIC(6,2) NOT NULL DEFAULT 0,
    taa_weight_max   NUMERIC(6,2) NOT NULL DEFAULT 100,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_by       BIGINT,
    is_deleted       BOOLEAN      NOT NULL DEFAULT FALSE
);

-- ─── 组合表 ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS portfolio (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(128) NOT NULL,
    code            VARCHAR(32)  NOT NULL UNIQUE,
    description     TEXT,
    benchmark_code  VARCHAR(64),
    benchmark_name  VARCHAR(128),
    total_value     NUMERIC(20,4) DEFAULT 0,
    currency        VARCHAR(8)   NOT NULL DEFAULT 'CNY',
    inception_date  DATE,
    status          VARCHAR(16)  NOT NULL DEFAULT 'ACTIVE',
    manager_id      BIGINT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_by      BIGINT,
    is_deleted      BOOLEAN      NOT NULL DEFAULT FALSE
);

-- ─── 持仓表 ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS holding (
    id               BIGSERIAL PRIMARY KEY,
    portfolio_id     BIGINT        NOT NULL REFERENCES portfolio(id),
    asset_code       VARCHAR(32)   NOT NULL,
    asset_name       VARCHAR(128)  NOT NULL,
    category_code    VARCHAR(32)   NOT NULL,
    quantity         NUMERIC(20,6) NOT NULL DEFAULT 0,
    cost_price       NUMERIC(20,6) NOT NULL DEFAULT 0,
    market_price     NUMERIC(20,6) NOT NULL DEFAULT 0,
    market_value     NUMERIC(20,4) NOT NULL DEFAULT 0,
    weight           NUMERIC(6,4)  NOT NULL DEFAULT 0,
    unrealized_pnl   NUMERIC(20,4) NOT NULL DEFAULT 0,
    unrealized_pnl_pct NUMERIC(8,4) NOT NULL DEFAULT 0,
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    created_by       BIGINT,
    is_deleted       BOOLEAN       NOT NULL DEFAULT FALSE
);

-- ─── 种子数据 ──────────────────────────────────────────────────────────────────
INSERT INTO asset_category (code, name, name_en, color, enabled) VALUES
    ('EQUITY',       '股票',   'Equity',      '#3b82f6', true),
    ('BOND',         '债券',   'Bond',        '#10b981', true),
    ('COMMODITY',    '商品',   'Commodity',   '#f59e0b', true),
    ('REAL_ESTATE',  '房地产', 'Real Estate', '#8b5cf6', true),
    ('CASH',         '现金',   'Cash',        '#6b7280', true),
    ('ALTERNATIVE',  '另类投资','Alternative','#ec4899', true)
ON CONFLICT (code) DO NOTHING;

-- 默认管理员（密码: Admin@123，BCrypt 加密）
INSERT INTO sys_user (username, password, nickname, email, role) VALUES
    ('admin', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2NJL9tFRby', '系统管理员', 'admin@map.com', 'SUPER_ADMIN')
ON CONFLICT (username) DO NOTHING;
