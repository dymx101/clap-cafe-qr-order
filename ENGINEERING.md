# Clap Cafe 扫码点餐系统 — 工程文档
## Clap Cafe QR Ordering System — Engineering Documentation

**文档版本 / Document Version:** v1.0
**编制日期 / Created:** 2026-05-14
**基于产品文档 / Based on:** QR-Ordering-System.md v1.0

---

## 目录 / Table of Contents

1. [项目结构 / Project Structure](#1-项目结构)
2. [技术栈总览 / Tech Stack Overview](#2-技术栈总览)
3. [前端工程 / Frontend Engineering](#3-前端工程)
4. [后端工程 / Backend Engineering](#4-后端工程)
5. [数据库设计 / Database Design](#5-数据库设计)
6. [API 规范 / API Specification](#6-api-规范)
7. [支付集成 / Payment Integration](#7-支付集成)
8. [KDS 后厨端 / Kitchen Display System](#8-kds-后厨端)
9. [部署架构 / Deployment Architecture](#9-部署架构)
10. [环境配置 / Environment Configuration](#10-环境配置)
11. [安全规范 / Security](#11-安全规范)
12. [测试策略 / Testing Strategy](#12-测试策略)
13. [监控与日志 / Monitoring & Logging](#13-监控与日志)
14. [CI/CD 流水线 / CI/CD Pipeline](#14-cicd-流水线)

---

## 1. 项目结构 / Project Structure

```
clap-cafe-qr-order/
├── frontend/                    # Vue 3 H5 前端
│   ├── public/
│   │   └── qr-codes/          # 预生成的 QR 码静态资源
│   ├── src/
│   │   ├── api/               # API 请求模块
│   │   │   ├── client.ts      # Axios 实例 + 拦截器
│   │   │   ├── menu.ts        # 菜单 API
│   │   │   ├── order.ts       # 订单 API
│   │   │   ├── payment.ts     # 支付 API
│   │   │   └── seat.ts        # 座位 API
│   │   ├── components/        # 公共组件
│   │   │   ├── CartBadge.vue
│   │   │   ├── ItemCard.vue
│   │   │   ├── LanguageSwitch.vue
│   │   │   ├── OrderStatusBadge.vue
│   │   │   └── SeatSelector.vue
│   │   ├── composables/       # Vue Composables
│   │   │   ├── useCart.ts
│   │   │   ├── useOrder.ts
│   │   │   ├── usePayment.ts
│   │   │   ├── usePolling.ts
│   │   │   └── useSeat.ts
│   │   ├── locales/            # i18n 国际化
│   │   │   ├── zh.json
│   │   │   └── en.json
│   │   ├── router/
│   │   │   └── index.ts
│   │   ├── stores/            # Pinia 状态管理
│   │   │   ├── cart.ts
│   │   │   ├── menu.ts
│   │   │   ├── order.ts
│   │   │   └── seat.ts
│   │   ├── types/             # TypeScript 类型定义
│   │   │   ├── menu.ts
│   │   │   ├── order.ts
│   │   │   ├── seat.ts
│   │   │   └── payment.ts
│   │   ├── views/             # 页面视图
│   │   │   ├── MenuView.vue       # 菜单浏览
│   │   │   ├── ItemDetailView.vue # 商品详情
│   │   │   ├── CartView.vue       # 购物车
│   │   │   ├── CheckoutView.vue   # 结账
│   │   │   ├── PaymentView.vue    # 支付页
│   │   │   ├── OrderConfirmView.vue # 订单确认
│   │   │   ├── OrderStatusView.vue  # 订单追踪
│   │   │   └── OrderHistoryView.vue # 历史订单
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                    # Python FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── dependencies.py    # 依赖注入
│   │   ├── api/               # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── menu.py
│   │   │   │   ├── order.py
│   │   │   │   ├── payment.py
│   │   │   │   ├── seat.py
│   │   │   │   ├── webhook.py
│   │   │   │   └── health.py
│   │   │   └── prefix.py      # API 前缀处理
│   │   ├── core/              # 核心业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── order_service.py
│   │   │   ├── payment_service.py
│   │   │   ├── seat_service.py
│   │   │   └── print_service.py
│   │   ├── models/           # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── category.py
│   │   │   ├── item.py
│   │   │   ├── seat.py
│   │   │   ├── order.py
│   │   │   └── order_item.py
│   │   ├── schemas/          # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── menu.py
│   │   │   ├── order.py
│   │   │   ├── payment.py
│   │   │   └── seat.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── order_id.py    # 订单号生成
│   │       └── timeout.py     # 超时任务
│   ├── alembic/              # 数据库迁移
│   │   ├── env.py
│   │   └── versions/
│   ├── tests/                # 测试
│   │   ├── api/
│   │   ├── core/
│   │   └── conftest.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pytest.ini
│
├── kds/                       # 后厨显示系统 (KDS)
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.vue
│   │   ├── api/
│   │   │   └── kds.ts
│   │   ├── components/
│   │   │   ├── OrderCard.vue
│   │   │   ├── OrderList.vue
│   │   │   └── AudioAlert.vue
│   │   └── main.ts
│   ├── vite.config.ts
│   └── package.json
│
├── admin/                     # 管理后台 (可选)
│   ├── src/
│   └── package.json
│
├── infra/                     # 基础设施即代码
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── docs/                      # 文档
│   ├── QR-Ordering-System.md  # 产品文档
│   ├── qr_codes/              # QR 码静态文件
│   └── api-schema/            # OpenAPI schema
│       └── openapi.json
│
├── scripts/
│   ├── generate_qr.py         # QR 码批量生成脚本
│   ├── seed_menu.py           # 菜单初始化数据
│   └── init_db.py             # 数据库初始化
│
├── .env.example
├── .gitignore
├── docker-compose.yml         # 全量开发环境
└── README.md
```

---

## 2. 技术栈总览 / Tech Stack Overview

| 层级 | 技术选型 | 版本 | 用途 |
|------|---------|------|------|
| 前端框架 | Vue 3 + Composition API | ^3.4 | 顾客点餐 H5 |
| 构建工具 | Vite | ^5.0 | 前端构建 |
| 状态管理 | Pinia | ^2.1 | 前端状态 |
| 国际化 | Vue I18n | ^9.0 | 中英文 |
| HTTP 客户端 | Axios | ^1.6 | API 请求 |
| 后端框架 | FastAPI | ^0.109 | REST API |
| Python | Python | 3.11+ | 后端语言 |
| ORM | SQLAlchemy 2.0 | ^2.0 | 数据库 ORM |
| 数据库 | PostgreSQL | 15 | 主数据库 |
| 缓存 | Redis | 7 | Session/队列 |
| 支付 | Stripe Python SDK | ^6.0 | 支付集成 |
| 打印 | python-escpos | ^3.0 | 小票打印 |
| 推送 | Twilio / OneSignal | — | 订单通知 |
| KDS 前端 | Vue 3 | ^3.4 | 后厨显示 |
| 容器化 | Docker | 24 | 开发/部署 |
| CDN | Cloudflare | — | 静态资源 |
| 托管 | Railway / Render | — | 后端托管 |

---

## 3. 前端工程 / Frontend Engineering

### 3.1 技术选型说明

**为什么选 Vue 3 + Vite？**
- 组合式 API（Composition API）天然适合点餐这类状态复杂但页面相对简单的场景
- Vite 热更新速度快，开发体验好
- TypeScript 支持完善，类型安全

### 3.2 页面路由 / Routes

| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | MenuView | 首页=菜单（redirect from root）|
| `/?seat=T01&lang=zh` | MenuView | 带座位参数的入口 |
| `/item/:id` | ItemDetailView | 商品详情 |
| `/cart` | CartView | 购物车 |
| `/checkout` | CheckoutView | 确认订单 |
| `/payment/:orderId` | PaymentView | 支付页 |
| `/order/:orderId/confirm` | OrderConfirmView | 订单确认 |
| `/order/:orderId/status` | OrderStatusView | 订单追踪 |
| `/orders/history` | OrderHistoryView | 历史订单 |

### 3.3 核心 Composables

#### useCart — 购物车状态（Pinia Store）

```typescript
// src/composables/useCart.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface CartItem {
  item_id: string
  name_zh: string
  name_en: string
  price_sgd: number
  quantity: number
  options: {
    size?: 'S' | 'M' | 'L'
    sweetness?: string
    temperature?: string
    extras?: string[]
  }
  notes?: string
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  const seatId = ref<string>('')

  const subtotal = computed(() =>
    items.value.reduce((sum, i) => sum + i.price_sgd * i.quantity, 0)
  )
  const tax = computed(() => Math.round(subtotal.value * 0.09 * 100) / 100)
  const total = computed(() => subtotal.value + tax.value)
  const itemCount = computed(() =>
    items.value.reduce((sum, i) => sum + i.quantity, 0)
  )

  function addItem(item: CartItem) {
    // 本地去重逻辑：同 item_id + options 合并数量
    const key = JSON.stringify({ item_id: item.item_id, options: item.options })
    const existing = items.value.find(
      i => JSON.stringify({ item_id: i.item_id, options: i.options }) === key
    )
    if (existing) {
      existing.quantity += item.quantity
    } else {
      items.value.push({ ...item })
    }
  }

  function removeItem(index: number) {
    items.value.splice(index, 1)
  }

  function updateQuantity(index: number, qty: number) {
    if (qty <= 0) removeItem(index)
    else items.value[index].quantity = qty
  }

  function clear() {
    items.value = []
  }

  function setSeat(id: string) {
    seatId.value = id
  }

  return { items, seatId, subtotal, tax, total, itemCount, addItem, removeItem, updateQuantity, clear, setSeat }
})
```

#### usePolling — 订单状态轮询

```typescript
// src/composables/usePolling.ts
import { ref, onUnmounted } from 'vue'

export function usePolling<T>(
  fetcher: () => Promise<T>,
  onUpdate: (data: T) => void,
  intervalMs = 3000
) {
  const data = ref<T | null>(null) as { value: T | null }
  const loading = ref(false)
  let timer: ReturnType<typeof setInterval> | null = null

  async function poll() {
    loading.value = true
    try {
      const result = await fetcher()
      data.value = result
      onUpdate(result)
    } finally {
      loading.value = false
    }
  }

  function start() {
    poll() // 立即执行一次
    timer = setInterval(poll, intervalMs)
  }

  function stop() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  onUnmounted(stop)

  return { data, loading, start, stop }
}
```

> **泛型说明：** `T` 既约束 `fetcher` 返回值类型，也约束 `data.value` 和 `onUpdate` 参数类型，确保类型安全。

### 3.4 国际化 / i18n

```typescript
// src/locales/zh.json (示例结构)
{
  "menu": {
    "title": "菜单",
    "categories": {
      "coffee": "咖啡",
      "tea": "茶饮",
      "milk_tea": "奶茶",
      "sparkling": "气泡水",
      "dessert": "甜点",
      "food": "轻食",
      "combo": "套餐"
    }
  },
  "cart": {
    "title": "购物车",
    "empty": "购物车是空的",
    "subtotal": "小计",
    "tax": "税 (GST 9%)",
    "total": "总计",
    "checkout": "去结账"
  },
  "order": {
    "seat": "座位",
    "notes": "备注",
    "notes_placeholder": "过敏原、少辣等要求",
    "submit": "提交订单",
    "status": {
      "submitted": "已提交",
      "confirmed": "已确认",
      "preparing": "制作中",
      "ready": "已完成",
      "completed": "已取餐",
      "cancelled": "已取消"
    }
  },
  "payment": {
    "title": "选择支付方式",
    "waiting": "等待支付...",
    "success": "支付成功",
    "failed": "支付失败，请重试",
    "timeout": "支付超时，请重新下单"
  }
}
```

### 3.5 API 客户端 / Axios Setup

```typescript
// src/api/client.ts
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'https://api.order.clapcafe.sg/v1',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

// 请求拦截器：注入 seat_id from URL
client.interceptors.request.use(config => {
  const params = new URLSearchParams(window.location.search)
  const seat = params.get('seat')
  if (seat) {
    config.headers['X-Seat-ID'] = seat
  }
  const lang = params.get('lang') || 'zh'
  config.headers['Accept-Language'] = lang
  return config
})

// 响应拦截器：统一错误处理
client.interceptors.response.use(
  res => res.data,
  err => {
    if (err.response?.status === 401) {
      // 未授权
    } else if (err.response?.status === 422) {
      // 业务错误
      console.error('API Error:', err.response.data)
    }
    return Promise.reject(err)
  }
)

export default client
```

---

## 4. 后端工程 / Backend Engineering

### 4.1 FastAPI 应用入口

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1 import menu, order, payment, seat, webhook, health, kds
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：连接数据库、初始化Redis
    from app.database import engine
    from app.utils.timeout import start_timeout_worker
    start_timeout_worker()
    yield
    # 关闭时：清理资源
    from app.utils.timeout import stop_timeout_worker
    stop_timeout_worker()


app = FastAPI(
    title="Clap Cafe Ordering API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS — 生产环境需限制为明确域名（见 .env.example CORS_ORIGINS）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ MVP 默认；生产环境改为 https://order.clapcafe.sg 等
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 健康检查（不含鉴权）
app.include_router(health.router, tags=["Health"])

# API v1 路由
app.include_router(menu.router, prefix="/v1/menu", tags=["Menu"])
app.include_router(order.router, prefix="/v1/orders", tags=["Orders"])
app.include_router(payment.router, prefix="/v1/payments", tags=["Payments"])
app.include_router(seat.router, prefix="/v1/seats", tags=["Seats"])
app.include_router(webhook.router, prefix="/v1/webhooks", tags=["Webhooks"])

# KDS 专用路由（Server-Sent Events 实时推送）
app.include_router(kds.router, prefix="/v1/kds", tags=["KDS"])
```

### 4.2 配置管理

```python
# backend/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "Clap Cafe Ordering"
    APP_ENV: str = "development"  # development | staging | production
    DEBUG: bool = False

    # 数据库
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/clapcafe"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_WEBHOOK_PATH: str = "/v1/webhooks/stripe"  # 固定路径，Stripe Dashboard 和代码必须统一
    STRIPE_PAYMENT_TIMEOUT_MINUTES: int = 15

    # PayNow
    PAYNOW_UEN: str = ""
    PAYNOW_MERCHANT_NAME: str = "CLAP CAFE SINGAPORE"

    # 推送
    ONESIGNAL_APP_ID: str = ""
    ONESIGNAL_API_KEY: str = ""

    # 小票打印
    PRINTER_ENABLED: bool = False
    PRINTER_TYPE: str = "escpos"  # escpos / usb / bluetooth

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

### 4.3 依赖注入

```python
# backend/app/dependencies.py
from fastapi import Header, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db


async def get_seat_id(
    x_seat_id: Optional[str] = Header(None, alias="X-Seat-ID"),
    request: Request = None
) -> str:
    """从请求头或URL参数获取座位号"""
    if x_seat_id:
        return x_seat_id
    # fallback：从 URL query params 读取
    seat = request.query_params.get("seat") if request else None
    if not seat:
        raise HTTPException(status_code=400, detail="Missing seat ID")
    return seat


async def get_db_session() -> AsyncSession:
    async for session in get_db():
        yield session
```

---

## 5. 数据库设计 / Database Design

### 5.1 数据库选型

- **PostgreSQL 15**：主数据库，支持 JSONB、事务、全文搜索
- **Redis 7**：缓存订单状态、Session、实时队列

### 5.2 表结构 / Schema

#### categories — 菜单分类

```sql
CREATE TABLE categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_zh     VARCHAR(100) NOT NULL,          -- "咖啡"
    name_en     VARCHAR(100) NOT NULL,          -- "Coffee"
    sort_order  INTEGER NOT NULL DEFAULT 0,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_categories_active ON categories(is_active);
CREATE INDEX idx_categories_sort ON categories(sort_order);
```

#### items — 商品

```sql
CREATE TABLE items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id     UUID NOT NULL REFERENCES categories(id),
    name_zh         VARCHAR(200) NOT NULL,       -- "海盐拿铁"
    name_en         VARCHAR(200) NOT NULL,       -- "Sea Salt Latte"
    description_zh  TEXT,
    description_en  TEXT,
    price_sgd       DECIMAL(10,2) NOT NULL,
    image_url       VARCHAR(500),
    options_config  JSONB NOT NULL DEFAULT '{}', -- 规格选项配置
    is_available   BOOLEAN NOT NULL DEFAULT TRUE,
    stock           INTEGER,                     -- NULL 表示无限库存
    sort_order      INTEGER NOT NULL DEFAULT 0,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_items_category ON items(category_id);
CREATE INDEX idx_items_available ON items(is_available, is_active);
CREATE INDEX idx_items_stock ON items(stock) WHERE stock IS NOT NULL;

-- options_config 示例：
-- {
--   "sizes": ["S", "M", "L"],
--   "sweetness": ["无糖", "少糖", "正常", "多糖"],
--   "temperature": ["冰", "热", "去冰"],
--   "extras": [{"name": "珍珠", "price": 0.5}, {"name": "椰果", "price": 0.5}]
-- }
```

#### seats — 座位

```sql
CREATE TABLE seats (
    id          VARCHAR(10) PRIMARY KEY,         -- "T01", "O03", "B06"
    label_zh    VARCHAR(50) NOT NULL,            -- "3号桌"
    label_en    VARCHAR(50) NOT NULL,            -- "Table 03"
    zone        VARCHAR(20) NOT NULL,            -- "indoor" / "outdoor" / "bar"
    status      VARCHAR(20) NOT NULL DEFAULT 'vacant'
                                        -- 座位占用状态：vacant / occupied / reserved / inactive
                        CHECK (status IN ('vacant','occupied','reserved','inactive')),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_seats_zone ON seats(zone);
CREATE INDEX idx_seats_status ON seats(status);
```

> **注意：** `zone`（室内/户外/吧台）和 `status`（空置/占用/预约/停用）是两个独立字段。

#### orders — 订单主表

```sql
CREATE TABLE orders (
    id                  VARCHAR(20) PRIMARY KEY,  -- "CC-20260514-001"
    seat_id             VARCHAR(10) NOT NULL REFERENCES seats(id),
    status              VARCHAR(20) NOT NULL DEFAULT 'submitted'
                        CHECK (status IN (
                            'submitted','confirmed','preparing',
                            'ready','completed','cancelled','rejected'
                        )),
    payment_status      VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (payment_status IN (
                            'pending','paid','failed','refunded','cancelled'
                        )),
    payment_method      VARCHAR(30),             -- "stripe_card", "paynow", "grabpay"
    payment_intent_id   VARCHAR(200),             -- Stripe PaymentIntent ID
    subtotal_sgd        DECIMAL(10,2) NOT NULL,
    tax_sgd             DECIMAL(10,2) NOT NULL,
    total_sgd           DECIMAL(10,2) NOT NULL,
    notes               TEXT,
    customer_notes      TEXT,                     -- 顾客备注（过敏原等）
    rejected_reason     VARCHAR(200),             -- 拒单原因
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    paid_at             TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    cancelled_at        TIMESTAMPTZ
);

CREATE INDEX idx_orders_seat ON orders(seat_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_payment ON orders(payment_status);
CREATE INDEX idx_orders_created ON orders(created_at DESC);
```

#### order_items — 订单明细

```sql
CREATE TABLE order_items (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id    VARCHAR(20) NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    item_id     UUID NOT NULL REFERENCES items(id),
    item_name_zh VARCHAR(200) NOT NULL,         -- 下单时快照
    item_name_en VARCHAR(200) NOT NULL,
    quantity    INTEGER NOT NULL DEFAULT 1,
    unit_price  DECIMAL(10,2) NOT NULL,          -- 下单时快照（含规格加价）
    options     JSONB NOT NULL DEFAULT '{}',     -- 规格选项快照
    notes       TEXT,
    print_group VARCHAR(20) DEFAULT 'drink',     -- 'drink' / 'food'
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
```

#### payment_transactions — 支付流水

```sql
CREATE TABLE payment_transactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id            VARCHAR(20) NOT NULL REFERENCES orders(id),
    stripe_payment_intent VARCHAR(200),
    paynow_reference    VARCHAR(100),
    amount_sgd          DECIMAL(10,2) NOT NULL,
    currency            VARCHAR(3) NOT NULL DEFAULT 'SGD',
    status              VARCHAR(20) NOT NULL,    -- pending/processing/succeeded/failed
    payment_method      VARCHAR(30),
    failure_code        VARCHAR(50),
    failure_message     TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pt_order ON payment_transactions(order_id);
CREATE INDEX idx_pt_payment_intent ON payment_transactions(stripe_payment_intent);
```

> **注意：** `stripe_payment_intent` 建索引用于 Webhook 回调时快速查找关联订单。

### 5.3 数据库迁移 / Alembic

```bash
# 生成迁移
cd backend
alembic revision --autogenerate -m "init schema"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### 5.4 座位数据初始化

```python
# backend/app/scripts/init_seats.py
SEATS_DATA = [
    # Indoor
    *[{"id": f"T{i:02d}", "label_zh": f"{i}号桌", "label_en": f"Table {i:02d}", "zone": "indoor"}
      for i in range(1, 13)],
    # Outdoor
    *[{"id": f"O{i:02d}", "label_zh": f"户外{i}号桌", "label_en": f"Outdoor {i:02d}", "zone": "outdoor"}
      for i in range(1, 5)],
    # Bar
    *[{"id": f"B{i:02d}", "label_zh": f"吧台{i}号座", "label_en": f"Bar Seat {i:02d}", "zone": "bar"}
      for i in range(1, 7)],
]
```

---

## 6. API 规范 / API Specification

### 6.1 基础信息

| 项目 | 值 |
|------|-----|
| Base URL | `https://api.order.clapcafe.sg/v1` |
| 认证 | 无需登录（扫码匿名点餐）|
| 字符编码 | UTF-8 |
| 内容类型 | `application/json` |

### 6.2 API 列表

#### 健康检查

```
GET /health
Response 200: { "status": "ok", "timestamp": "2026-05-14T08:00:00Z" }
```

#### 菜单

```
GET /menu
Query: lang (zh | en, default: zh)
Response 200:
{
  "categories": [
    {
      "id": "uuid",
      "name": "咖啡",          // 根据lang返回对应语言
      "sort_order": 1,
      "items": [
        {
          "id": "uuid",
          "name": "海盐拿铁",
          "description": "...",
          "price_sgd": 7.50,
          "image_url": "https://...",
          "options_config": { ... },
          "is_available": true
        }
      ]
    }
  ]
}

GET /menu/items/{item_id}
Response 200: { "id": "...", "name": "...", ... }
```

#### 座位

```
GET /seats
Response 200:
{
  "seats": [
    { "id": "T01", "label": "1号桌", "zone": "indoor", "is_active": true },
    ...
  ]
}

GET /seats/{seat_id}
Response 200: { "id": "T01", "label": "1号桌", ... }

PUT /seats/{seat_id}/status
Body: { "status": "occupied" | "vacant" | "reserved" | "inactive" }
Response 200: { "id": "T01", "status": "occupied" }
```

#### 订单

```
POST /orders
Headers: X-Seat-ID: T01
Body:
{
  "seat_id": "T01",
  "items": [
    {
      "item_id": "uuid",
      "quantity": 2,
      "options": { "size": "M", "sweetness": "少糖", "temperature": "冰" },
      "notes": "少冰"
    }
  ],
  "customer_notes": "过敏"
}
Response 201:
{
  "id": "CC-20260514-001",
  "seat_id": "T01",
  "status": "submitted",
  "payment_status": "pending",
  "items": [...],
  "subtotal_sgd": 14.00,
  "tax_sgd": 1.26,
  "total_sgd": 15.26,
  "created_at": "2026-05-14T08:00:00Z"
}

GET /orders/{order_id}
Response 200: { full order object }

GET /orders/{order_id}/status
Response 200: { "id": "CC-20260514-001", "status": "preparing", "updated_at": "..." }

PUT /orders/{order_id}/status   (KDS / 后厨专用)
Body: { "status": "confirmed" | "preparing" | "ready" | "completed" }
Response 200: { ... }

PUT /orders/{order_id}/reject   (KDS / 后厨专用)
Body: { "reason": "out_of_stock", "items": ["uuid1", "uuid2"] }
Response 200: { ... }

POST /orders/{order_id}/cancel
Body: { "reason": "customer_request" }
Response 200: { "id": "CC-20260514-001", "status": "cancelled" }
```

#### 支付

```
POST /payments/create-intent
Body:
{
  "order_id": "CC-20260514-001",
  "payment_method_types": ["card", "grabpay", "paynow"]
}
Response 200:
{
  "client_secret": "pi_xxx_secret_xxx",   // Stripe Client Secret
  "payment_intent_id": "pi_xxx",
  "amount": 1526,                           // cents
  "currency": "sgd"
}

POST /payments/confirm-paynow
Body:
{
  "order_id": "CC-20260514-001",
  "payment_method_type": "paynow"          // 明确指定 paynow
}
Response 200:
{
  "paynow_qr_url": "https://...",           // PayNow QR码数据URL
  "paynow_reference": "CC20260514001",
  "expires_at": "2026-05-14T08:15:00Z"
}

GET /payments/{payment_intent_id}/status
Response 200: { "status": "succeeded" | "processing" | "failed" }
```

#### Webhooks

```
POST /webhooks/stripe
Headers: Stripe-Signature: sig_xxx
Body: Stripe Event JSON
处理事件:
  - payment_intent.succeeded    → 更新订单 payment_status=paid, status=confirmed
  - payment_intent.payment_failed → 更新订单 payment_status=failed
  - payment_intent.canceled    → 更新订单 payment_status=cancelled, status=cancelled

POST /webhooks/paynow
Body: PayNow webhook payload (银行格式)
处理: 支付成功回调，更新订单状态

> **Webhook 幂等性：** Stripe Webhook `payment_intent.succeeded` 可能发送多次（Stripe 重试机制）。处理时必须先查订单当前状态，已是 `paid` 则直接返回 200，不重复更新。
> ```python
> if order.payment_status == "paid":
>     return  # 幂等：已处理过，直接返回
> ```


### 6.3 错误响应格式

```json
{
  "error": {
    "code": "ORDER_NOT_FOUND",
    "message": "Order CC-20260514-999 does not exist",
    "detail": {}
  }
}
```

| HTTP 状态码 | 含义 |
|------------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 409 | 冲突（如重复下单）|
| 422 | 业务校验失败 |
| 500 | 服务器错误 |

---

## 7. 支付集成 / Payment Integration

### 7.1 Stripe 集成

```python
# backend/app/core/payment_service.py
import asyncio
import time
import stripe
from app.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:

    def create_payment_intent(self, order_id: str, amount_cents: int, metadata: dict):
        """创建 Stripe PaymentIntent"""
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="sgd",
            metadata={
                **metadata,
                "order_id": order_id  # order_id 必须放 spread 之后，防止调用方传入的同名 key 被覆盖
            },
            payment_method_types=["card", "grabpay", "paynow"],  # 显式声明，否则 PayNow 不会出现在支付界面
            automatic_payment_methods={"enabled": True},
            # 15分钟超时
            expires_at=int(time.time()) + settings.STRIPE_PAYMENT_TIMEOUT_MINUTES * 60
        )
        return intent

    def construct_webhook_event(self, payload: bytes, signature: str):
        """验证并解析 Stripe Webhook（同步调用，包装为非阻塞）"""
        return stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET
        )

    async def construct_webhook_event_async(self, payload: bytes, signature: str):
        """异步版：避免阻塞事件循环"""
        return await asyncio.to_thread(
            stripe.Webhook.construct_event,
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET
        )

    def retrieve_payment_intent(self, intent_id: str):
        """同步调用，KDS 轮询等非关键路径可用"""
        return stripe.PaymentIntent.retrieve(intent_id)

    async def retrieve_payment_intent_async(self, intent_id: str):
        """异步版：KDS SSE 推送路径使用"""
        return await asyncio.to_thread(stripe.PaymentIntent.retrieve, intent_id)

    def create_refund(self, payment_intent_id: str, amount_cents: int = None):
        """创建退款"""
        kwargs = {"payment_intent": payment_intent_id}
        if amount_cents:
            kwargs["amount"] = amount_cents
        return stripe.Refund.create(**kwargs)
```

### 7.2 支付超时处理

```python
# backend/app/utils/timeout.py
import asyncio
from sqlalchemy import select, and_
from app.database import AsyncSessionLocal
from app.models.order import Order
from app.core.payment_service import PaymentService
from app.config import settings


async def check_unpaid_orders():
    """定时任务：取消超15分钟未支付的订单"""
    async with AsyncSessionLocal() as db:
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(minutes=settings.STRIPE_PAYMENT_TIMEOUT_MINUTES)
        # 使用 FOR UPDATE SKIP LOCKED：跳过被其他 worker 锁定的行，防止并发 worker 重复处理
        result = await db.execute(
            select(Order).where(
                and_(
                    Order.payment_status == "pending",
                    Order.status == "submitted",
                    Order.created_at < cutoff
                )
            ).with_for_update(skip_locked=True)
        )
        for order in result.scalars():
            # 更新状态
            order.status = "cancelled"
            order.payment_status = "cancelled"
            order.cancelled_at = datetime.utcnow()
            # 释放座位（参数化查询，无 SQL 注入风险）
            from sqlalchemy import update
            from app.models.seat import Seat
            await db.execute(
                update(Seat).where(Seat.id == order.seat_id).values(status="vacant")
            )
            await db.commit()


def start_timeout_worker():
    loop = asyncio.get_event_loop()
    loop.create_task(_timeout_loop())


async def _timeout_loop():
    while True:
        await asyncio.sleep(60)  # 每分钟检查一次
        try:
            await check_unpaid_orders()
        except Exception as e:
            print(f"Timeout worker error: {e}")
```

### 7.3 PayNow 集成说明 / PayNow Integration

> ⚠️ **重要澄清**：Stripe 的 `automatic_payment_methods: { enabled: true }` 启用的是 Visa/MC/Amex/Apple Pay/Google Pay，**不包含 PayNow**。PayNow 需要单独在 `payment_method_types` 中显式声明。

**方式一：Stripe Payment Request Button（推荐，最简）**
```python
intent = stripe.PaymentIntent.create(
    amount=amount_cents,
    currency="sgd",
    payment_method_types=["card", "grabpay", "paynow"],  # 显式声明 PayNow
    automatic_payment_methods={"enabled": True},
    metadata={"order_id": order_id}
)
```
PayNow QR 由 Stripe 自动生成，顾客扫码后银行 App 完成支付，Stripe Webhook 统一回调。

**方式二：独立 PayNow SGQR（银行直连）**
适用于希望使用自有银行 PayNow 账户的场景：
```python
# 参考：https://www.abs.org.sg/consumer-finance/paynow
# 联系银行（推荐 UOB / OCBC）获取 SGQR merchant API
# PayNow QR 由银行生成，通过独立 webhook 回调
```

---

## 8. KDS 后厨端 / Kitchen Display System

### 8.1 技术选型

- 独立 Vue 3 应用，部署在 `kds.clapcafe.sg`
- Server-Sent Events（SSE）实时推送订单（Redis Pub/Sub）
- 支持声音提醒（Audio Alert）
- 触控优化（平板/大屏）

### 8.2 核心功能

```vue
<!-- KDS 订单卡片 -->
<template>
  <div :class="['order-card', order.status]">
    <div class="header">
      <span class="seat-label">{{ order.seat_id }}</span>
      <span class="order-id">{{ order.id }}</span>
      <span class="time">{{ formatTime(order.created_at) }}</span>
    </div>
    <div class="items">
      <div
        v-for="item in order.items"
        :key="item.id"
        :class="['item', item.print_group]"
      >
        <span class="qty">{{ item.quantity }}x</span>
        <span class="name">{{ item.item_name_zh }}</span>
        <span class="options">{{ formatOptions(item.options) }}</span>
        <span v-if="item.notes" class="notes">📝 {{ item.notes }}</span>
      </div>
    </div>
    <div v-if="order.customer_notes" class="customer-notes">
      ⚠️ 顾客备注: {{ order.customer_notes }}
    </div>
    <div class="actions">
      <button
        v-if="order.status === 'submitted'"
        class="btn-confirm"
        @click="confirm(order.id)"
      >接单</button>
      <button
        v-if="order.status === 'confirmed' || order.status === 'preparing'"
        class="btn-ready"
        @click="markReady(order.id)"
      >完成</button>
      <button
        class="btn-reject"
        @click="showRejectModal = true"
      >拒单</button>
    </div>
  </div>
</template>
```

### 8.3 实时推送（SSE）

```python
# backend/app/api/v1/kds.py
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

router = APIRouter()


@router.get("/orders/stream")
async def orders_stream(request: Request):
    async def event_generator():
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("kds:orders")
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    yield {"event": "new_order", "data": message["data"]}
                # 心跳保活（SSE 规范要求 data 字段非空，部分客户端忽略空 data）
                yield {"event": "ping", "data": "pong"}
                await asyncio.sleep(5)
        finally:
            await pubsub.unsubscribe("kds:orders")

    return EventSourceResponse(event_generator())
```

---

## 9. 部署架构 / Deployment Architecture

### 9.1 生产架构

```
                          ┌──────────────────┐
                          │   Cloudflare      │
                          │  (CDN + DNS)     │
                          └────────┬─────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
   ┌──────────▼──────┐  ┌─────────▼──────┐  ┌─────────▼──────┐
   │ order.clapcafe.sg│  │ admin.clapcafe. │  │  kds.clapcafe. │
   │ (Cloudflare Pages)│  │      sg         │  │       sg       │
   │  Vue3 H5 前端    │  │ (Cloudflare     │  │ (Cloudflare    │
   │  静态托管        │  │  Pages)          │  │  Pages)        │
   └──────────────────┘  └─────────────────┘  └─────────────────┘
                                   │
                          HTTPS (直接调用)
                                   │
                    ┌──────────────▼──────────────┐
                    │       Railway               │
                    │  ┌─────────────────────┐   │
                    │  │  FastAPI 后端        │   │
                    │  │  (2x instances)      │   │
                    │  └──────────┬──────────┘   │
                    │             │              │
                    │  ┌──────────▼──────────┐   │
                    │  │ Railway Postgres    │   │
                    │  │ Railway Redis       │   │
                    │  └─────────────────────┘   │
                    └────────────────────────────┘
                                   │
                          ┌────────▼────────┐
                          │  AWS S3 / R2    │
                          │  (菜单图片)     │
                          └─────────────────┘
```

> **架构说明：** Railway 直接暴露 HTTPS 端点（`https://api.order.clapcafe.sg`），无需 Cloudflare Workers 中转。Workers 仅用于边缘计算场景（如 A/B 测试、请求日志），不作为反向代理。

### 9.2 开发环境 (Docker Compose)

```yaml
# infra/docker-compose.yml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: clapcafe
      POSTGRES_USER: clapcafe
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ../backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://clapcafe:dev_password@postgres:5432/clapcafe
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ../backend:/app

  frontend:
    build: ../frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_BASE_URL: http://localhost:8000/v1

  kds:
    build: ../kds
    ports:
      - "3001:3001"

volumes:
  postgres_data:
  redis_data:
```

### 9.3 环境变量 / Environment Variables

```bash
# backend/.env.example

# 应用
DEBUG=false
APP_NAME="Clap Cafe Ordering"

# 数据库
DATABASE_URL=postgresql+asyncpg://clapcafe:password@host:5432/clapcafe
REDIS_URL=redis://localhost:6379/0

# Stripe
STRIPE_SECRET_KEY=sk_live_xxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxx
STRIPE_PAYMENT_TIMEOUT_MINUTES=15

# PayNow
PAYNOW_UEN=202012345A
PAYNOW_MERCHANT_NAME="CLAP CAFE SINGAPORE"

# 推送
ONESIGNAL_APP_ID=
ONESIGNAL_API_KEY=

# 打印
PRINTER_ENABLED=false
PRINTER_TYPE=escpos

# 域名
FRONTEND_URL=https://order.clapcafe.sg
API_URL=https://api.order.clapcafe.sg

# CORS（生产）
CORS_ORIGINS=https://order.clapcafe.sg,https://admin.clapcafe.sg,https://kds.clapcafe.sg
```

```bash
# frontend/.env.example
VITE_API_BASE_URL=https://api.order.clapcafe.sg/v1
VITE_APP_NAME=Clap Cafe Ordering
```

---

## 10. 环境配置 / Environment Configuration

### 10.1 Railway 部署配置

```json
// backend/railway.json
{
  "$schema": "https://railway.app/schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "numReplicas": 2,
    "restartPolicy": {
      "type": "ON_FAILURE",
      "retries": 3
    }
  },
  "variables": {
    "DEBUG": "false"
  }
}
```

### 10.2 Cloudflare Pages 部署

```
// frontend/_routes.json
{
  "include": ["/*"],
  "exclude": ["/api/*"],
  "fetch": "/index.html"
}
```

部署命令：
```bash
wrangler pages deploy frontend/dist --project-name=clap-cafe-order
wrangler pages deploy kds/dist --project-name=clap-cafe-kds
```

---

## 11. 安全规范 / Security

### 11.1 前端安全

- **无登录认证**：扫码即用，通过 `seat_id` 追踪，不收集用户个人信息
- **输入验证**：所有用户输入在提交前做格式校验（数量、规格等）
- **XSS 防护**：Vue 3 默认防护，不使用 `v-html` 处理用户内容
- **敏感信息**：不存储任何个人身份信息（PII）

### 11.2 后端安全

- **CORS**：生产环境限制为 `order.clapcafe.sg` 等指定域名
- **速率限制**：每个座位号每分钟最多 10 次下单请求
- **Stripe Webhook 验证**：使用 `Stripe-Signature` 头验签，防止伪造
- **SQL 注入**：SQLAlchemy ORM 参数化查询，完全防护
- **环境变量**：所有密钥存储在环境变量，不提交到代码仓库

```python
# 速率限制示例
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/orders")
@limiter.limit("10/minute")
async def create_order(request: Request, ...):
    ...
```

### 11.3 支付安全

- Stripe Elements / Payment Request Button：卡号不过商户服务器
- PCI DSS 合规由 Stripe 承担
- 支付超时 15 分钟自动取消，防止卡单占用库存
- Webhook 回调需验签

---

## 12. 测试策略 / Testing Strategy

### 12.1 测试金字塔

```
       /\
      /  \     E2E 测试 (Playwright)
     /____\    - 完整点餐流程
    /      \   - 支付成功/失败流程
   /  Integration \
  /______________\  - API 集成测试
  /               \
 /    Unit Tests   \  - Service 层单元测试
/__________________\ - Model 单元测试
```

### 12.2 单元测试示例

```python
# backend/tests/core/test_order_service.py
import pytest
from datetime import datetime
from app.core.order_service import OrderService
from app.schemas.order import CreateOrderRequest


@pytest.fixture
def order_service():
    return OrderService()


def test_generate_order_id():
    """测试订单号生成格式"""
    order_id = generate_order_id()
    assert order_id.startswith("CC-")
    assert len(order_id) == 17  # CC-YYYYMMDD-NNN
    parts = order_id.split("-")
    assert parts[1] == datetime.now().strftime("%Y%m%d")


def test_calculate_totals():
    """测试金额计算（含 GST）"""
    items = [
        {"price_sgd": 7.50, "quantity": 2},
        {"price_sgd": 5.00, "quantity": 1}
    ]
    subtotal = 7.50 * 2 + 5.00 * 1  # 20.00
    tax = round(20.00 * 0.09, 2)    # 1.80
    total = 21.80
    assert subtotal == 20.00
    assert tax == 1.80
    assert total == 21.80


@pytest.mark.asyncio
async def test_create_order_updates_seat():
    """测试下单后座位状态变为 occupied"""
    service = OrderService()
    await service.create_order(...)
    seat = await service.get_seat("T01")
    assert seat.status == "occupied"
```

### 12.3 API 集成测试

```python
# backend/tests/api/test_order.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_create_order():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/orders",
            headers={"X-Seat-ID": "T01"},
            json={
                "seat_id": "T01",
                "items": [
                    {
                        "item_id": "valid-uuid",
                        "quantity": 1,
                        "options": {}
                    }
                ]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["seat_id"] == "T01"
        assert data["status"] == "submitted"
        assert "CC-2026" in data["id"]


@pytest.mark.asyncio
async def test_get_order_status():
    ...
```

### 12.4 E2E 测试（Playwright）

```typescript
// frontend/tests/e2e/order-flow.spec.ts
import { test, expect } from '@playwright/test'

test('完整点餐流程', async ({ page }) => {
  await page.goto('https://order.clapcafe.sg/?seat=T01&lang=zh')

  // 选择商品
  await page.click('[data-testid="item-card"]')
  await page.selectOption('[data-testid="size-select"]', 'M')
  await page.click('text=加入购物车')

  // 购物车
  await page.click('[data-testid="cart-badge"]')
  await page.click('text=去结账')

  // 确认订单
  await page.click('text=提交订单')

  // 支付（Mock Stripe）
  await page.click('text=Visa')
  await page.click('text=确认支付')

  // 订单确认
  await expect(page.locator('text=订单提交成功')).toBeVisible()
})
```

---

## 13. 监控与日志 / Monitoring & Logging

### 13.1 日志规范

```python
# backend/app/utils/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


# 关键日志点
logger.info("Order created", extra={
    "order_id": order_id,
    "seat_id": seat_id,
    "total_sgd": total
})
logger.warning("Payment timeout", extra={"order_id": order_id})
logger.error("Stripe webhook failed", extra={
    "error": str(e),
    "event_type": event_type
})
```

### 13.2 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| API 响应时间 P99 | 后端 API | > 2s |
| 支付成功率 | Stripe | < 95% |
| 错误率 | 5xx | > 1% |
| 下单量 | 实时 | 突发为0 |
| Webhook 失败数 | Stripe | > 0 |

### 13.3 监控工具配置

```python
# Cloudflare Workers + Datadog
# 后端健康检查
@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "checks": {
            "database": await check_db(),
            "redis": await check_redis()
        }
    }
```

---

## 14. CI/CD 流水线 / CI/CD Pipeline

### 14.1 GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r backend/requirements.txt
      - run: pip install pytest pytest-asyncio httpx
      - run: cd backend && pytest tests/ -v --tb=short

      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd frontend && npm ci
      - run: cd frontend && npm run build
      - run: cd frontend && npm run type-check

  deploy:
    needs: [backend-test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # 部署后端到 Railway
      - uses: railway deploy@v1
        with:
          token: ${{ secrets.RAILWAY_TOKEN }}
          service: backend

      # 部署前端到 Cloudflare Pages
      - uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: clap-cafe-order
          directory: frontend/dist
```

### 14.2 分支策略

| 分支 | 用途 | 部署环境 |
|------|------|----------|
| `main` | 生产代码 | production |
| `develop` | 开发集成 | staging |
| `feature/xxx` | 功能开发 | preview |

---

## 附录 A：OpenAPI Schema

完整 OpenAPI 3.0 Schema 导出：

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
curl http://localhost:8000/openapi.json > ../docs/api-schema/openapi.json
```

---

*本文档与产品文档 QR-Ordering-System.md 配套使用*
*文档版本：v1.0 | 编制日期：2026-05-14*
