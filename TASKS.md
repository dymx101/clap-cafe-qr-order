# Clap Cafe 扫码点餐系统 — 任务清单
# Clap Cafe QR Ordering System — Task List

**文档版本 / Version:** v1.0
**编制日期 / Created:** 2026-05-14
**基于 / Based on:** ENGINEERING.md v1.0, QR-Ordering-System.md v1.1
**状态 / Status:** 待开发 / To Do

---

## 符号说明 / Legend

| 符号 | 含义 |
|------|------|
| 🔴 | Critical path（关键路径，影响其他任务）|
| 🟡 | Medium priority |
| ⚪ | Can run in parallel with critical path |
| `backend/` | 后端任务 |
| `frontend/` | 前端 H5 任务 |
| `kds/` | KDS 后厨端任务 |
| `infra/` | 基础设施/部署任务 |
| `test/` | 测试任务 |

---

## Phase 1 · 基础设施 / Infrastructure

---

### T1 · 初始化 Git 仓库与目录结构
**owner:** `infra`
**estimated:** 0.5h
**depends:** —

- [ ] 1.1 初始化 Git 仓库 `git init`
- [ ] 1.2 创建 `.gitignore`（Python / Node / macOS / IDE）
- [ ] 1.3 创建目录结构：`frontend/` `backend/` `docs/` `scripts/`
- [ ] 1.4 初始 commit 并创建 `main` 分支
- [ ] 1.5 pre-commit hook：安装 `pip install pre-commit`，创建 `.pre-commit-config.yaml`：
  - `ruff check`（Python linting，修复 F401/F541 等）
  - `ESLint --max-warnings 0`（TypeScript linting）
  - `mypy app/`（Python 类型检查）
  - `vue-tsc --noEmit`（TypeScript 编译检查）
- [ ] 1.6 分支规范：`main`（生产）、`staging`（预发布）、`feature/*`（功能分支）、`hotfix/*`（热修复）

---

### T2 · 后端项目初始化
**owner:** `backend`
**estimated:** 1h
**depends:** T1
**parallel:** T3

- [ ] 2.1 创建 `backend/` 虚拟环境 `python -m venv venv && source venv/bin/activate`
- [ ] 2.2 安装依赖：`pip install fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic python-dotenv pydantic-settings stripe redis python-multipart aiofiles httpx pytest pytest-asyncio`
- [ ] 2.3 创建 `backend/app/` 目录结构（按 ENGINEERING.md Section 1）
- [ ] 2.4 验证 FastAPI 启动：`uvicorn app.main:app --reload`，访问 `/health` 返回 200

---

### T3 · 前端项目初始化
**owner:** `frontend`
**estimated:** 1h
**depends:** T1
**parallel:** T2

- [ ] 3.1 创建 Vue 3 项目：`npm create vite@latest frontend -- --template vue-ts`
- [ ] 3.2 安装依赖：`pinia vue-router vue-i18n axios @vueuse/core`
- [ ] 3.3 安装开发依赖：`npm install -D typescript @types/node vite-plugin-vue-type-imports`
- [ ] 3.4 创建 `frontend/src/` 目录结构（按 ENGINEERING.md Section 1）
- [ ] 3.5 配置 `vite.config.ts`：proxy 指向 `http://localhost:8000`，alias `@` → `src/`
- [ ] 3.6 验证前端启动：`npm run dev`，访问 `localhost:5173` 正常渲染

---

### T4 · 数据库与缓存实例申请
**owner:** `infra`
**estimated:** 1h
**depends:** T1

- [ ] 4.1 在 Railway 申请 PostgreSQL 实例，获取 `postgresql://user:pass@host:5432/db`
- [ ] 4.2 在 Railway 或 Upstash 申请 Redis 实例，获取 `redis://host:6379`
- [ ] 4.3 在 Cloudflare 申请 Workers 和 Pages 项目（或使用 Vercel）
- [ ] 4.4 将连接 URL 填入 `backend/.env` 和 `frontend/.env`
- [ ] 4.5 验证连接：`python -c "import asyncpg; asyncio.run(asyncpg.connect(URL))"`

---

### T5 · 配置管理
**owner:** `backend`
**estimated:** 1h
**depends:** T4

- [ ] 5.1 创建 `backend/app/config.py`，继承 `pydantic_settings.BaseSettings`
- [ ] 5.2 配置字段（按 ENGINEERING.md Section 4）：`DATABASE_URL` `REDIS_URL` `STRIPE_SECRET_KEY` `STRIPE_PUBLISHABLE_KEY` `STRIPE_WEBHOOK_SECRET` `STRIPE_PAYMENT_TIMEOUT_MINUTES=15` `APP_ENV` `DEBUG`
- [ ] 5.3 创建 `.env.example`：所有环境变量占位符，注明哪些需要真实值
- [ ] 5.4 创建 `backend/app/__init__.py` 和 `backend/app/core/__init__.py`
- [ ] 5.5 验证：`python -c "from app.config import settings; print(settings.APP_ENV)"`

---

## Phase 2 · 数据库 / Database

---

### T6 · 数据库 Schema 与迁移
**owner:** `backend`
**estimated:** 3h
**depends:** T2, T4
**🔴 Critical**

- [ ] 6.1 初始化 Alembic：`alembic init alembic`，配置 `alembic.ini` 中的 `sqlalchemy.url`
- [ ] 6.2 创建 `alembic/versions/001_init_schema.py` 迁移文件，内容如下：
- [ ] 6.3 创建 `categories` 表（含 `sort_order` 索引）
- [ ] 6.4 创建 `items` 表（含 `idx_items_category` `idx_items_available` 部分索引 `idx_items_stock WHERE stock IS NOT NULL`）
- [ ] 6.5 创建 `seats` 表（含 `zone`/`status` CHECK 约束，`idx_seats_zone` `idx_seats_status`）
- [ ] 6.6 创建 `orders` 表（含 `status`/`payment_status` CHECK 约束，所有索引）
- [ ] 6.7 创建 `order_items` 表（含 `print_group` 默认值）
- [ ] 6.8 创建 `payment_transactions` 表（含 `idx_pt_order` `idx_pt_payment_intent`）
- [ ] 6.9 执行 `alembic upgrade head`，验证所有表创建成功
- [ ] 6.10 编写 downgrade 回滚脚本并测试

```python
# 参考：alembic/versions/001_init_schema.py 结构
def upgrade():
    op.create_table('categories', ...)
    op.create_table('items', ...)
    op.create_table('seats', ...)
    op.create_table('orders', ...)
    op.create_table('order_items', ...)
    op.create_table('payment_transactions', ...)
    # 所有 INDEX 和 CHECK CONSTRAINT

def downgrade():
    op.drop_table('payment_transactions')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('seats')
    op.drop_table('items')
    op.drop_table('categories')
```

---

### T7 · 座位数据初始化
**owner:** `backend`
**estimated:** 0.5h
**depends:** T6

- [ ] 7.1 创建 `backend/app/scripts/init_seats.py`
- [ ] 7.2 按 ENGINEERING.md Section 5.4 数据生成 22 条座位记录：
  - T01-T12（12 indoor）
  - O01-O04（4 outdoor）
  - B01-B06（6 bar）
- [ ] 7.3 所有座位初始状态 `status='vacant'`，`is_active=True`
- [ ] 7.4 执行脚本：`python -m app.scripts.init_seats`
- [ ] 7.5 验证：`SELECT COUNT(*) FROM seats WHERE is_active=True` 应返回 22

---

### T8 · 数据库连接模块
**owner:** `backend`
**estimated:** 1h
**depends:** T5, T6

- [ ] 8.1 创建 `backend/app/database.py`：`engine`（AsyncEngine）、`AsyncSessionLocal`（async sessionmaker）、`get_db()` 依赖
- [ ] 8.2 创建 `backend/app/models/__init__.py`
- [ ] 8.3 创建 `backend/app/models/base.py`：所有模型的 SQLAlchemy `Base`
- [ ] 8.4 创建 `backend/app/models/category.py`：ORM 模型，对应 `categories` 表
- [ ] 8.5 创建 `backend/app/models/item.py`：ORM 模型，含 `options_config` JSONB 字段
- [ ] 8.6 创建 `backend/app/models/seat.py`：ORM 模型，含 `status` CHECK
- [ ] 8.7 创建 `backend/app/models/order.py`：ORM 模型，含 ENUM status
- [ ] 8.8 创建 `backend/app/models/order_item.py`：ORM 模型
- [ ] 8.9 创建 `backend/app/models/payment.py`：ORM 模型
- [ ] 8.10 验证模型导入：`python -c "from app.models import Category, Item, Seat, Order, OrderItem, PaymentTransaction; print('OK')"`

---

## Phase 3 · 后端核心 API / Backend Core API

---

### T9 · `GET /menu` 菜单接口
**owner:** `backend`
**estimated:** 2h
**depends:** T8
**🔴 Critical**

- [ ] 9.1 创建 `backend/app/api/v1/menu.py` 路由文件
- [ ] 9.2 `GET /v1/menu`：查询所有 `is_active=True` 的分类，按 `sort_order` 排序
- [ ] 9.3 每个分类下挂 `items` 列表，按 `name_zh/name_en` 排序，`is_available=True`
- [ ] 9.4 支持 `?lang=zh|en` 参数，默认 `zh`
- [ ] 9.5 响应结构：嵌套 JSON，`categories[].items[]` 包含所有字段（id/name/description/price_sgd/image_url/options_config/is_available）
- [ ] 9.6 单元测试：分类排序、items 过滤、`lang` 参数切换
- [ ] 9.7 HTTP 测试：`curl http://localhost:8000/v1/menu?lang=en` 返回 200

---

### T10 · `GET /menu/items/{item_id}` 单品接口
**owner:** `backend`
**estimated:** 1h
**depends:** T9

- [ ] 10.1 `GET /v1/menu/items/{item_id}`：查询单个 item
- [ ] 10.2 404 处理：`ItemService.get_item_or_404(item_id)` 抛出 `HTTPException(404)`
- [ ] 10.3 验证 UUID 格式：`raise HTTPException(400)` 如果格式错误
- [ ] 10.4 单元测试：正常查询、item 不存在404、UUID 格式错误400

---

### T11 · `POST /orders` 创建订单
**owner:** `backend`
**estimated:** 4h
**depends:** T9, T10
**🔴 Critical**

- [ ] 11.1 创建 `backend/app/api/v1/order.py` 路由文件
- [ ] 11.2 创建 `backend/app/services/order_service.py`：业务逻辑层
- [ ] 11.3 `POST /v1/orders` 请求体验证（pydantic schema）：
  ```python
  {
    "seat_id": str,         # "T01"
    "items": [
      {
        "item_id": str,      # UUID
        "quantity": int,
        "options": {},       # 规格选项
        "notes": str | null
      }
    ],
    "notes": str | null,
    "lang": "zh" | "en"
  }
  ```
- [ ] 11.4 订单号生成逻辑：`order_id = f"CC-{date}-{nnn:03d}"`（当日自增）
  - 查询当天最大订单号：`SELECT id FROM orders WHERE id LIKE 'CC-YYYYMMDD-%' ORDER BY id DESC LIMIT 1`
  - 解析后缀 NNN 并 +1
- [ ] 11.5 库存校验：查 `items` 表 `stock` 字段，若 `stock < quantity` 返回 400
- [ ] 11.6 座位状态校验：若 `seats.status != 'vacant'` 返回 409
- [ ] 11.7 价格快照：`unit_price` 取下单时 `items.price_sgd`（不取实时价格）
- [ ] 11.8 写入 `orders` 和 `order_items` 表，事务保证原子性
- [ ] 11.9 更新座位状态为 `occupied`
- [ ] 11.10 幂等性：同一个 `seat_id` + `items` 哈希 5 分钟内重复提交返回原订单（避免刷新重提交）
- [ ] 11.11 Redis 缓存订单号计数器：`INCR order:counter:{date}`（或用 DB 序列）
- [ ] 11.12 单元测试：正常创建、库存不足400、座位已占用409、UUID 错误400
- [ ] 11.13 HTTP 测试：完整创建流程，验证 `orders` 和 `order_items` 表数据

---

### T12 · `GET /orders/{order_id}` 查询订单
**owner:** `backend`
**estimated:** 1h
**depends:** T11

- [ ] 12.1 `GET /v1/orders/{order_id}`：返回完整订单（含 `order_items` 列表）
- [ ] 12.2 `GET /v1/orders/{order_id}/status`：仅返回 `{id, status, payment_status, updated_at}`
- [ ] 12.3 404 处理：订单不存在返回 `ORDER_NOT_FOUND`
- [ ] 12.4 订单号格式校验：`CC-YYYYMMDD-NNN` 格式校验

---

### T13 · `PUT /orders/{order_id}/status` 状态更新（KDS）
**owner:** `backend`
**estimated:** 2h
**depends:** T12
**🔴 Critical**

- [ ] 13.1 创建 `ORDER_STATUS_TRANSITIONS` 状态机（ENGINEERING.md Section 6）：
  ```
  submitted → confirmed → preparing → ready → completed
            → rejected
  submitted/cancelled → cancelled
  ```
- [ ] 13.2 状态转换校验函数：不在 `ORDER_STATUS_TRANSITIONS[current]` 中的目标状态返回 422
- [ ] 13.3 更新 `orders.status`，设置 `updated_at`
- [ ] 13.4 当 `status → completed` 时，更新 `seats.status = 'vacant'`
- [ ] 13.5 KDS 专属路由前缀 `/v1/kds/orders/...`（与公开 `orders/` 分离）
- [ ] 13.6 权限：KDS 端点无需认证（内部网络），但需 IP 白名单或 API Key 保护
- [ ] 13.7 Redis Pub/Sub：状态变更后 publish 到 `channel:orders`，payload 含 `order_id/status`
- [ ] 13.8 单元测试：合法状态转换、非法转换返回422、各状态流转

---

### T14 · `PUT /orders/{order_id}/reject` 拒单
**owner:** `backend`
**estimated:** 1.5h
**depends:** T13

- [ ] 14.1 请求体：`{"reason": "out_of_stock"|"customer_request"|"other", "items": ["uuid1", "uuid2"]}`
- [ ] 14.2 全单拒单：`items` 为空或 null，`orders.status = 'rejected'`，更新库存
- [ ] 14.3 部分拒单：`items` 非空，仅标记指定 `order_items`，更新对应商品库存
- [ ] 14.4 记录 `orders.rejected_reason`
- [ ] 14.5 退款：自动调用 `PaymentService.create_refund()`（如已支付）
- [ ] 14.6 座位释放：`status = 'vacant'`
- [ ] 14.7 Redis Pub/Sub 通知

---

### T15 · `POST /orders/{order_id}/cancel` 取消订单
**owner:** `backend`
**estimated:** 1.5h
**depends:** T13

- [ ] 15.1 取消条件校验：`status` 仅为 `submitted` 时可取消（已 `confirmed`/`preparing` 不可取消）
- [ ] 15.2 释放座位：`update(Seat).where(Seat.id == order.seat_id).values(status="vacant")`
- [ ] 15.3 更新 `orders.status = 'cancelled'`，`orders.cancelled_at = NOW()`
- [ ] 15.4 已支付订单：自动调用 `PaymentService.create_refund()`
- [ ] 15.5 退款后释放座位
- [ ] 15.6 单元测试：submitted 可取消、confirmed 不可取消404、座位正确释放

---

### T16 · 座位 API
**owner:** `backend`
**estimated:** 1h
**depends:** T8

- [ ] 16.1 `GET /v1/seats`：返回所有 `is_active=True` 座位列表，含 `status/label_zh/label_en`
- [ ] 16.2 `GET /v1/seats/{seat_id}`：返回单个座位详情
- [ ] 16.3 `PUT /v1/seats/{seat_id}/status`：更新座位状态（`vacant/occupied/reserved/inactive`）
- [ ] 16.4 `status=inactive` 的座位不显示在 `GET /v1/seats` 列表中
- [ ] 16.5 单元测试

---

### T17 · 健康检查端点
**owner:** `backend`
**estimated:** 0.5h
**depends:** T5

- [ ] 17.1 `GET /health`：返回 `{"status": "ok", "timestamp": "...", "version": "1.0.0"}`
- [ ] 17.2 `GET /health/ready`：检查 DB 连接 + Redis 连接，全部 OK 才返回 200，否则 503

---

## Phase 4 · 支付集成 / Payment Integration

---

### T18 · `POST /payments/create-intent` 创建支付
**owner:** `backend`
**estimated:** 2h
**depends:** T11
**🔴 Critical**

- [ ] 18.1 创建 `backend/app/core/payment_service.py`（ENGINEERING.md Section 7.1）
- [ ] 18.2 `create_payment_intent(order_id, amount_cents, metadata)`：
  ```python
  metadata={
      **metadata,
      "order_id": order_id  # order_id 必须在 spread 之后，防止覆盖
  },
  payment_method_types=["card", "grabpay", "paynow"],
  automatic_payment_methods={"enabled": True},
  expires_at=int(time.time()) + 15 * 60
  ```
- [ ] 18.3 `amount_cents`：从订单 `total_sgd * 100` 传入
- [ ] 18.4 记录 `payment_transactions`：`status='pending'`
- [ ] 18.5 签名：`stripe.api_key = settings.STRIPE_SECRET_KEY`
- [ ] 18.6 返回 `client_secret` 和 `payment_intent_id` 给前端
- [ ] 18.7 单元测试：创建成功、金额为0处理

---

### T19 · Stripe Webhook Handler
**owner:** `backend`
**estimated:** 3h
**depends:** T18
**🔴 Critical**

- [ ] 19.1 `POST /v1/webhooks/stripe` 端点（路由已在 `include_router` 中注册）
- [ ] 19.2 读取 raw body（`request.body()`）用于签名验证，**不使用 `await request.json()`**
- [ ] 19.3 签名验证：`stripe.Webhook.construct_event(raw_body, sig, settings.STRIPE_WEBHOOK_SECRET)`
- [ ] 19.4 幂等性处理：
  ```python
  order = await get_order_by_payment_intent(payment_intent_id)
  if order.payment_status == "paid":
      return {"received": True}  # 已处理过，直接返回
  ```
- [ ] 19.5 事件处理：
  - `payment_intent.succeeded` → `payment_status='paid'`, `status='confirmed'`, `paid_at=NOW()`
  - `payment_intent.payment_failed` → `payment_status='failed'`
  - `payment_intent.canceled` → `payment_status='cancelled'`, `status='cancelled'`
- [ ] 19.6 响应：必须在 3 秒内返回 200，否则 Stripe 重试（使用 `asyncio.to_thread` 处理耗时逻辑）
- [ ] 19.7 本地测试：`stripe listen --forward-to localhost:8000/v1/webhooks/stripe`
- [ ] 19.8 端到端 Webhook 测试：触发 `payment_intent.succeeded`，验证订单状态更新

---

### T20 · `POST /payments/confirm-paynow` PayNow 确认
**owner:** `backend`
**estimated:** 1.5h
**depends:** T18

- [ ] 20.1 请求体：`{"order_id": "...", "payment_method_type": "paynow"}`
- [ ] 20.2 从 PaymentIntent 获取 PayNow QR 数据：`payment_intent.next_action.display_bank_transfer_instructions`
- [ ] 20.3 返回 `paynow_qr_url`（Stripe 生成的 Data URL）和 `paynow_reference`
- [ ] 20.4 设置过期时间（15 分钟）
- [ ] 20.5 超时后 Stripe Webhook `payment_intent.canceled` 自动处理

---

### T21 · 支付超时后台 Worker
**owner:** `backend`
**estimated:** 2h
**depends:** T19

- [ ] 21.1 创建 `backend/app/utils/timeout.py`
- [ ] 21.2 `check_unpaid_orders()` 函数：
  - 查询条件：`payment_status='pending' AND status='submitted' AND created_at < cutoff`
  - 使用 `.with_for_update(skip_locked=True)` 防止并发重复处理
  - 循环内每次 `await db.commit()`（不等整个函数结束）
- [ ] 21.3 座位释放：`update(Seat).where(Seat.id == order.seat_id).values(status="vacant")`
- [ ] 21.4 `start_timeout_worker()`：获取事件循环，创建 `_timeout_loop()` 任务
- [ ] 21.5 在 `main.py` startup 时调用 `start_timeout_worker()`
- [ ] 21.6 单元测试：mock DB 数据，验证超时订单被正确取消

---

### T22 · `GET /payments/{payment_intent_id}/status` 支付状态查询
**owner:** `backend`
**estimated:** 1h
**depends:** T18

- [ ] 22.1 查询 `payment_transactions` 表（或直接调用 Stripe）
- [ ] 22.2 返回：`{status: "pending"|"processing"|"succeeded"|"failed"}`
- [ ] 22.3 用于 KDS SSE 轮询 fallback（如 SSE 不可用）

---

## Phase 5 · 前端 H5 / Frontend H5

---

### T23 · 路由配置
**owner:** `frontend`
**estimated:** 1h
**depends:** T3
**🔴 Critical**

- [ ] 23.1 安装 `vue-router`：`npm install vue-router`
- [ ] 23.2 创建 `src/router/index.ts`：9 个路由（`/` `/item/:id` `/cart` `/checkout` `/payment/:orderId` `/order/:orderId/confirm` `/order/:orderId/status` `/orders/history`）
- [ ] 23.3 路由守卫：解析 `/?seat=T01&lang=zh`，写入 Pinia `seatStore`
- [ ] 23.4 404 路由处理
- [ ] 23.5 验证：每个路由渲染正确页面组件

---

### T24 · `useCartStore` 购物车 Pinia Store
**owner:** `frontend`
**estimated:** 2h
**depends:** T23

- [ ] 24.1 创建 `src/stores/cart.ts`（Pinia Store，不是 composable）
- [ ] 24.2 状态：`items: CartItem[]`、`seatId: string`
- [ ] 24.3 计算属性：`subtotal`、`tax`（9% GST新加坡）、`total`、`itemCount`
- [ ] 24.4 `addItem(item)`：同 item_id + options 合并数量（本地去重 key = `JSON.stringify({item_id, options})`）
- [ ] 24.5 `removeItem(index)` / `updateQuantity(index, qty)` / `clear()`
- [ ] 24.6 `setSeat(id)`：QR 解析后写入
- [ ] 24.7 持久化：使用 `pinia-plugin-persistedstate`，刷新后恢复购物车
- [ ] 24.8 单元测试（Vitest）：addItem 去重逻辑、GST 计算、clear

---

### T25 · `usePolling<T>` 泛型轮询 Composable
**owner:** `frontend`
**estimated:** 1.5h
**depends:** T24

- [ ] 25.1 创建 `src/composables/usePolling.ts`
- [ ] 25.2 泛型参数 `T`：类型安全，错误使用在编译期捕获
- [ ] 25.3 `const data = ref<T | null>(null)` — 初始值
- [ ] 25.4 `onUpdate: (data: T) => void` — 数据更新回调，接收 `T` 类型
- [ ] 25.5 返回值：`{ data: Ref<T | null>, loading: Ref<boolean>, stop: () => void }`
- [ ] 25.6 内部 `setInterval(poll, intervalMs)`，页面卸载 `clearInterval`
- [ ] 25.7 单元测试

---

### T26 · `MenuView` 菜单页
**owner:** `frontend`
**estimated:** 3h
**depends:** T23, T24

- [ ] 26.1 布局：顶部 LanguageSwitch + CartBadge 购物车图标
- [ ] 26.2 分类 Tab 栏：横向滚动，`activeCategory` 高亮
- [ ] 26.3 商品网格：`ItemCard` 组件，图片 + 名称 + 价格
- [ ] 26.4 点击商品跳转 `/item/{id}`
- [ ] 26.5 加载状态骨架屏（loading skeleton）
- [ ] 26.6 空分类处理
- [ ] 26.7 `useMenuStore`：缓存菜单数据，`lang` 切换时重新请求

---

### T27 · `ItemDetailView` 商品详情页
**owner:** `frontend`
**estimated:** 3h
**depends:** T26

- [ ] 27.1 顶部商品图片（大图）
- [ ] 27.2 名称（中英双语）、价格（SGD 格式）
- [ ] 27.3 规格选项解析（`options_config` JSON）：
  - 尺寸：S/M/L 单选
  - 甜度：无糖/少糖/正常/多糖 单选
  - 温度：冰/热/去冰 单选
  - 加料：珍珠/椰果等多选
- [ ] 27.4 已选规格高亮显示
- [ ] 27.5 数量选择器（+/-）
- [ ] 27.6 顾客备注输入框
- [ ] 27.7 "加入购物车"按钮：调用 `cartStore.addItem()`，显示成功 toast
- [ ] 27.8 库存不足显示（如 API 返回 `is_available=false`）

---

### T28 · `CartView` 购物车页
**owner:** `frontend`
**estimated:** 2h
**depends:** T27

- [ ] 28.1 显示座位号（QR 解析来的，如 "T01 / 1号桌"）
- [ ] 28.2 商品列表：每个 CartItem 显示名称 / 规格 / 数量调整 / 单价小计
- [ ] 28.3 数量调整：+/- 按钮，调用 `updateQuantity(index, qty)`
- [ ] 28.4 删除按钮：调用 `removeItem(index)`
- [ ] 28.5 底部：subtotal / tax(9%) / total
- [ ] 28.6 清空购物车按钮
- [ ] 28.7 空购物车处理：显示插图 + "去选购" 按钮
- [ ] 28.8 "确认订单" 按钮：跳转 `/checkout`

---

### T29 · `CheckoutView` 确认订单页
**owner:** `frontend`
**estimated:** 2h
**depends:** T28

- [ ] 29.1 订单摘要：商品列表 + 规格 + 数量 + 单价
- [ ] 29.2 费用明细：subtotal / GST(9%) / total
- [ ] 29.3 座位号显示（中英双语，如 "Table 01 / 1号桌"）
- [ ] 29.4 顾客备注输入（过敏原等）
- [ ] 29.5 语言切换 `?lang=` 参数透传
- [ ] 29.6 "提交订单" 按钮：
  - 调用 `POST /v1/orders`
  - 成功后跳转 `/payment/{orderId}`
  - 失败显示错误 toast
- [ ] 29.7 提交中 loading 状态（防止双击）

---

### T30 · `PaymentView` 支付页
**owner:** `frontend`
**estimated:** 4h
**depends:** T29
**🔴 Critical**

- [ ] 30.1 加载 Stripe `PaymentElement`：
  - 调用 `POST /v1/payments/create-intent` 获取 `client_secret`
  - 初始化 `stripe.elements({ clientSecret })`
  - 挂载 `<div id="payment-element">`
- [ ] 30.2 显示订单金额（从 order 对象读取）
- [ ] 30.3 "立即支付" 按钮：`await stripe.confirmPayment({ elements, confirmParams: { return_url: '.../order/{orderId}/confirm' } })`
- [ ] 30.4 支付成功：跳转 `/order/{orderId}/confirm`
- [ ] 30.5 支付失败：显示 Stripe 返回的错误信息
- [ ] 30.6 PayNow 特殊处理：`POST /v1/payments/confirm-paynow`，显示 Stripe 返回的 QR 码
- [ ] 30.7 支付超时（15 分钟）：显示倒计时，超时提示
- [ ] 30.8 loading / error 状态处理

---

### T31 · `OrderStatusView` 订单追踪页
**owner:** `frontend`
**estimated:** 2h
**depends:** T30

- [ ] 31.1 调用 `usePolling<OrderStatus>(fetcher, onUpdate, 3000)`
- [ ] 31.2 `OrderStatusBadge` 组件：不同状态不同颜色（submitted=灰 / confirmed=蓝 / preparing=黄 / ready=绿 / cancelled=红）
- [ ] 31.3 预计等待时间（可在 `GET /menu` 中返回 `avg_wait_minutes`）
- [ ] 31.4 订单完成（ready）：显示取餐提示
- [ ] 31.5 订单取消/拒单：显示原因
- [ ] 31.6 "再来一单" 按钮：复制上一单 items 到购物车

---

### T32 · `OrderHistoryView` 历史订单页
**owner:** `frontend`
**estimated:** 1.5h
**depends:** T31

- [ ] 32.1 `GET /v1/orders?page=1&limit=20`：分页查询
- [ ] 32.2 订单卡片列表：订单号 / 时间 / 金额 / 状态标签
- [ ] 32.3 点击查看订单详情（跳转 `/order/{orderId}/status`）
- [ ] 32.4 空状态处理
- [ ] 32.5 分页加载（下拉加载更多）

---

### T33 · 国际化（i18n）
**owner:** `frontend`
**estimated:** 2h
**depends:** T26, T27, T28

- [ ] 33.1 创建 `src/locales/zh.json`：所有界面文字
- [ ] 33.2 创建 `src/locales/en.json`：所有界面文字
- [ ] 33.3 配置 `vue-i18n`
- [ ] 33.4 `LanguageSwitch` 组件：切换 `locale`，URL 参数 `?lang=` 更新
- [ ] 33.5 刷新保持语言：URL `?lang=` 参数透传，所有 API 调用带上 `lang` 参数
- [ ] 33.6 菜单接口：`GET /v1/menu?lang=en` 返回英文名

---

## Phase 6 · KDS 后厨端 / Kitchen Display System

---

### T34 · KDS 项目初始化
**owner:** `kds`
**estimated:** 1h
**depends:** T3

- [ ] 34.1 创建 `kds/` 目录，初始化 Vue 3 + Vite + TypeScript（同 T3）
- [ ] 34.2 安装依赖：`pinia vue-router vue-i18n axios`
- [ ] 34.3 目录结构：`src/views/` `src/components/` `src/stores/` `src/api/`
- [ ] 34.4 部署配置：Vercel 子域名 `kds.clapcafe.sg` 或 Cloudflare Pages

---

### T35 · SSE 连接与 Redis Pub/Sub
**owner:** `kds`
**estimated:** 3h
**depends:** T13, T34
**🔴 Critical**

- [ ] 35.1 后端 SSE 端点：`GET /v1/kds/stream`
- [ ] 35.2 后端 Redis 订阅：channel = `orders:*`，或使用 Redis Streams
- [ ] 35.3 SSE 心跳：`yield {"event": "ping", "data": "pong"}`（每 15 秒）
- [ ] 35.4 KDS 前端 SSE 客户端：`new EventSource('/v1/kds/stream')`
- [ ] 35.5 SSE 连接状态：connected / reconnecting / error，显示状态指示
- [ ] 35.6 自动重连逻辑（EventSource 自带，但需处理断线后重新订阅）
- [ ] 35.7 新订单事件处理：`event.data` 解析后写入 Pinia store

---

### T36 · KDS 订单卡片组件
**owner:** `kds`
**estimated:** 2h
**depends:** T35

- [ ] 36.1 布局：左侧新订单队列（按时间倒序），右侧已完成的今日统计
- [ ] 36.2 订单卡片设计（ENGINEERING.md Section 8.2 Vue 模板）：
  ```
  ┌──────────────────────┐
  │ T01    #CC-20260514  │  ← 座位号高亮（醒目大字）
  │ 14:35               │  ← 下单时间
  ├──────────────────────┤
  │ 1x 海盐拿铁 (M, 少糖) │
  │ 1x 珍珠奶茶 (L)       │
  ├──────────────────────┤
  │ [接单] [拒单]         │  ← 操作按钮
  └──────────────────────┘
  ```
- [ ] 36.3 `seat_id` 显示：字号最大，使用 `label_zh`（厨房中文更习惯）
- [ ] 36.4 等待计时器：下单后超过 N 分钟显示警告色
- [ ] 36.5 按状态筛选 Tab：全部 / 待接单 / 制作中 / 待取餐 / 已完成

---

### T37 · KDS 操作按钮
**owner:** `kds`
**estimated:** 1.5h
**depends:** T36

- [ ] 37.1 [接单] 按钮：`PUT /v1/orders/{order_id}/status` → `status='confirmed'`
- [ ] 37.2 [开始制作] 按钮：`PUT /v1/orders/{order_id}/status` → `status='preparing'`
- [ ] 37.3 [完成] 按钮：`PUT /v1/orders/{order_id}/status` → `status='ready'`
- [ ] 37.4 [拒单] 按钮：弹出原因选择，`PUT /v1/orders/{order_id}/reject`
- [ ] 37.5 操作后 SSE 推送更新所有 KDS 客户端（Redis Pub/Sub 广播）
- [ ] 37.6 操作失败提示：toast 报错

---

### T38 · 声音提醒
**owner:** `kds`
**estimated:** 1h
**depends:** T35

- [ ] 38.1 新订单到达时播放提示音（Web Audio API）
- [ ] 38.2 提供 `notification.mp3` 音频文件（或使用 Web Speech API TTS）
- [ ] 38.3 KDS 设置：支持静音切换
- [ ] 38.4 浏览器权限：首次加载时请求 Audio 权限（自动播放限制）

---

### T39 · 触控优化
**owner:** `kds`
**estimated:** 1h
**depends:** T36

- [ ] 39.1 布局：平板横屏优先（1024px+），大按钮（最小 48x48px）
- [ ] 39.2 字体：至少 16px，确保厨房远距离可读
- [ ] 39.3 颜色对比：WCAG AA 标准，状态色盲友好
- [ ] 39.4 防止误触：操作按钮需 300ms 以上长按或二次确认
- [ ] 39.5 响应式：横屏 / 竖屏自适应布局

---

## Phase 7 · 部署 / Deployment

---

### T40 · 后端 Dockerfile 与 Railway 部署
**owner:** `infra`
**estimated:** 2h
**depends:** T18
**🔴 Critical**

- [ ] 40.1 创建 `backend/Dockerfile`（多阶段构建，镜像 digest pinning）：
  ```dockerfile
  # 查询当前 digest：docker pull python:3.11-slim@sha256:xxxx
  # 禁止裸 tag 拉取，强制 digest pinning 防止供应链攻击
  FROM python:3.11-slim@sha256:xxxx AS builder
  COPY requirements.txt
  RUN pip install --no-cache-dir --platform manylinux2014_x86_64 --target=/pylibs -r requirements.txt

  FROM python:3.11-slim@sha256:xxxx
  COPY --from=builder /pylibs /usr/local/lib/python3.11/site-packages
  COPY ./app /app/app
  WORKDIR /app
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```
- [ ] 40.2 `backend/requirements.txt`：锁定所有依赖版本（`pip freeze > requirements.txt`）
- [ ] 40.3 Railway 部署：连接 GitHub repo，Railway 自动检测 Dockerfile
- [ ] 40.4 环境变量配置（Railway dashboard）：所有 `.env` 变量
- [ ] 40.5 健康检查：`GET /health/ready` 返回 200
- [ ] 40.6 验证：`curl https://api.order.clapcafe.sg/health` 返回 200

---

### T41 · 前端 H5 Vercel 部署
**owner:** `infra`
**estimated:** 1.5h
**depends:** T30

- [ ] 41.1 `frontend/vercel.json`：
  ```json
  {
    "rewrites": [{ "source": "/api/(.*)", "destination": "https://api.order.clapcafe.sg/v1/(.*)" }]
  }
  ```
- [ ] 41.2 环境变量：`VITE_API_BASE_URL`（构建时嵌入）
- [ ] 41.3 Vercel 部署：连接 GitHub，main 分支自动部署
- [ ] 41.4 自定义域名：`order.clapcafe.sg`
- [ ] 41.5 验证：`curl https://order.clapcafe.sg/?seat=T01&lang=zh` 返回页面

---

### T42 · KDS 部署
**owner:** `infra`
**estimated:** 1h
**depends:** T39

- [ ] 42.1 Vercel 部署 `kds/` 项目
- [ ] 42.2 自定义域名：`kds.clapcafe.sg`
- [ ] 42.3 环境变量：`VITE_API_BASE_URL=https://api.order.clapcafe.sg`
- [ ] 42.4 访问验证

---

### T43 · Cloudflare DNS 配置
**owner:** `infra`
**estimated:** 0.5h
**depends:** T40, T41, T42

- [ ] 43.1 DNS A 记录 / CNAME：
  - `api.order.clapcafe.sg` → Railway 分配的域名
  - `order.clapcafe.sg` → Vercel 域名
  - `kds.clapcafe.sg` → KDS Vercel 域名
- [ ] 43.2 SSL/TLS：Cloudflare 边缘证书，Full(strict) 模式
- [ ] 43.3 页面规则：强制 HTTPS 跳转

---

### T44 · Stripe 后台配置
**owner:** `infra`
**estimated:** 0.5h
**depends:** T19

- [ ] 44.1 Stripe Dashboard → Developers → Webhooks
- [ ] 44.2 添加端点：`https://api.order.clapcafe.sg/v1/webhooks/stripe`
- [ ] 44.3 勾选监听事件：`payment_intent.succeeded` `payment_intent.payment_failed` `payment_intent.canceled`
- [ ] 44.4 获取 Webhook signing secret（`whsec_xxx`）填入 `STRIPE_WEBHOOK_SECRET`
- [ ] 44.5 本地 `stripe listen` 测试：确认本地能收到事件
- [ ] 44.6 测试卡号：Stripe 提供 `4242 4242 4242 4242` 等测试卡

---

### T45 · QR 码生成
**owner:** `infra`
**estimated:** 1.5h
**depends:** T41

- [ ] 45.1 创建 `scripts/generate_qrcodes.py`
- [ ] 45.2 安装：`pip install qrcode pillow`
- [ ] 45.3 为 22 个座位生成 QR 码（`T01-T12/O01-O04/B01-B06`）：
  - 中文版：`https://order.clapcafe.sg/?seat=T01&lang=zh`
  - 英文版：`https://order.clapcafe.sg/?seat=T01&lang=en`
- [ ] 45.4 输出到 `frontend/public/qr-codes/`：
  - `T01_zh.png` / `T01_en.png`
  - `O01_zh.png` / `O01_en.png`
  - `B01_zh.png` / `B01_en.png`
- [ ] 45.5 QR 规格：尺寸 5cm×5cm（300 DPI），高对比度，保留静音区
- [ ] 45.6 打印排版：每页 6 个 QR 码（贴纸格式），提供 PDF 下载链接
- [ ] 45.7 座位号贴纸设计稿（AI/Canva），包含：
  - QR 码居中
  - 座位号大字（如 "1号桌 / Table 01"）
  - Clap Cafe Logo

---

## Phase 8 · 测试与上线 / Testing & Launch

---

### T46 · 单元测试
**owner:** `backend` / `frontend`
**estimated:** 4h
**depends:** T18, T24

**后端（pytest）：**
- [ ] 46.1 订单号生成：`test_order_id_format()` 验证 `CC-YYYYMMDD-NNN` 格式
- [ ] 46.2 状态机转换：所有合法/非法转换覆盖
- [ ] 46.3 GST 计算：验证 `subtotal * 0.09` 精度
- [ ] 46.4 库存校验：库存不足时返回 400
- [ ] 46.5 `check_unpaid_orders`：超时订单取消逻辑
- [ ] 46.6 Webhook 幂等性：重复 `payment_intent.succeeded` 不重复更新

**前端（Vitest）：**
- [ ] 46.7 购物车去重逻辑（相同 item_id + options 合并）
- [ ] 46.8 GST 计算
- [ ] 46.9 `usePolling` mock 测试

**静态分析：**
- [ ] 46.10 后端：`mypy app/`（验证 pydantic-settings 和类型注解，`pyproject.toml` 配置 `strict = true`）
- [ ] 46.11 前端：`vue-tsc --noEmit`（TypeScript 编译期检查，`tsconfig.json` 设置 `strict: true`）
- [ ] 46.12 Python Lint：`ruff check app/`，修复 F401（未使用导入）/ F541（无用 f-string）/ E501（行长）
- [ ] 46.13 TypeScript Lint：`ESLint --max-warnings 0`，修复 no-unused-vars / no-explicit-any
- [ ] 46.14 pre-commit hook 集成：所有静态分析加入 T1.5 pre-commit 配置

---

### T47 · API 集成测试
**owner:** `backend`
**estimated:** 3h
**depends:** T46

- [ ] 47.1 `pytest` + `pytest-asyncio` + `httpx.AsyncClient`
- [ ] 47.2 `test_menu_get`：验证分类排序、items 过滤
- [ ] 47.3 `test_order_create_flow`：创建 → 查询 → 状态更新 → 取消
- [ ] 47.4 `test_payment_intent_create`：验证 `client_secret` 返回
- [ ] 47.5 `test_webhook_payment_succeeded`：模拟 Stripe 事件
- [ ] 47.6 `test_concurrent_timeout_orders`：两个 worker 并发运行超时不重复
- [ ] 47.7 错误响应格式：`{"error": {"code": "...", "message": "..."}}`
- [ ] 47.8 所有端点 401/404/422 错误码

---

### T48 · Stripe Webhook 本地测试
**owner:** `backend`
**estimated:** 1h
**depends:** T19

- [ ] 48.1 安装 Stripe CLI：`brew install stripe/stripe-cli/stripe`
- [ ] 48.2 登录：`stripe login`
- [ ] 48.3 本地转发：`stripe listen --forward-to localhost:8000/v1/webhooks/stripe`
- [ ] 48.4 复制 `whsec_xxx` 到 `.env`
- [ ] 48.5 触发测试事件：`stripe trigger payment_intent.succeeded`
- [ ] 48.6 验证数据库订单状态更新
- [ ] 48.7 PayNow 测试：使用 Stripe 测试模式 PayNow

---

### T49 · 端到端测试（E2E）
**owner:** `infra`
**estimated:** 2h
**depends:** T40, T41, T48

- [ ] 49.1 安装 Playwright：`npm install -D @playwright/test`
- [ ] 49.2 E2E 测试用例：
  - TC01：扫码进入 → 选择商品 → 加入购物车 → 提交订单 → 支付（Stripe 测试卡）
  - TC02：KDS 收到订单 → 接单 → 完成 → 顾客端状态更新
  - TC03：订单超时（手动修改 created_at）→ 验证自动取消
  - TC04：拒单 → 验证退款 → 验证座位释放
- [ ] 49.3 在 CI 中运行 E2E 测试（GitHub Actions）
- [ ] 49.4 测试报告：HTML 报告 + 截图失败证据

---

### T50 · 上线前 Checklist
**owner:** `infra`
**estimated:** 1h
**depends:** T49

- [ ] 50.1 环境变量复查：`.env` 无真实密钥残留（使用 `.env.example` 对照）
- [ ] 50.2 CORS 白名单：`allow_origins` 不再是 `["*"]`（已改为 `order.clapcafe.sg` 等）
- [ ] 50.3 Stripe 手续费确认：新加坡 Stripe 费率 3.5%（GrabPay/PayNow 额外）
- [ ] 50.4 PayNow 测试支付：真实扫码，确认 QR 显示正常
- [ ] 50.5 QR 码扫描测试：微信 / Alipay / Safari / Chrome 各测一次
- [ ] 50.6 KDS 平板测试：iPad/AndroidPad 横屏显示正常
- [ ] 50.7 日志级别：生产环境 `INFO`，非 `DEBUG`
- [ ] 50.8 UptimeRobot 监控配置：`/health` 端点 60s 轮询
- [ ] 50.9 Cloudflare Analytics：确认请求正常到达
- [ ] 50.10 备份策略：Railway 自动备份，验证可恢复性

---

## 任务汇总 / Summary

| Phase | 任务数 | 预估工时 |
|-------|--------|---------|
| 1. 基础设施 | 5 | 3.5h |
| 2. 数据库 | 3 | 4.5h |
| 3. 后端 API | 9 | 14h |
| 4. 支付集成 | 5 | 9.5h |
| 5. 前端 H5 | 11 | 21.5h |
| 6. KDS | 6 | 9.5h |
| 7. 部署 | 6 | 6.5h |
| 8. 测试+上线 | 5 | 11h |
| **合计** | **50** | **~80h（约3周单人）** |

---

## 并行策略 / Parallelization

以下任务可以并行安排（不同人独立负责）：

| 并行组 | 任务 | 负责人 |
|--------|------|--------|
| A | T2 + T3（后端+前端初始化）| 后端 + 前端 |
| B | T9 + T10 + T12 + T16（菜单+座位API）| 后端 |
| C | T23 + T26 + T27 + T28 + T29 + T30（前端核心页面）| 前端 |
| D | T18 + T19 + T20 + T21（支付相关）| 后端 |
| E | T40 + T41 + T42 + T43（部署，三套环境）| DevOps |

---
