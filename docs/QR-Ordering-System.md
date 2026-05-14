# Clap Cafe 点餐系统产品文档
# Clap Cafe QR Ordering System — Product Document

> **Version 1.0 | 2026-05-14**
> 中文版本在后，English version starts after Chinese content.

---

## 1. 产品概述 / Product Overview

### 1.1 是什么 / What It Is

Clap Cafe 扫码点餐系统是一套基于 QR 码的顾客自助点餐 + 后厨实时通知解决方案。顾客入座后扫描桌上 QR 码，在手机浏览器中完成点餐和支付；厨房通过独立屏幕实时接收订单，全程无需服务员介入。

The Clap Cafe QR Ordering System is a QR code-based self-service ordering and kitchen notification platform. Customers scan the QR code at their table, order and pay directly in their mobile browser; kitchen staff receive orders in real time on a dedicated screen — no server involvement required.

### 1.2 核心价值主张 / Core Value Proposition

| 顾客视角 Customer | 商家视角 Operator |
|---|---|
| 扫码即点，无需下载 App Scan & order, no app download | 减少排队，提升翻台率 Reduce queue, increase table turnover |
| 支持中英文，游客友好 Bilingual CN/EN, tourist-friendly | 后厨实时接单，减少出错 Kitchen receives orders live, fewer errors |
| 支持 PayNow / Visa / MC / GrabPay / Apple Pay | 支付即到账，自动核销 Payment auto-confirmed, no manual reconciliation |

---

## 2. 使用场景 / Use Cases

### 2.1 顾客流程 / Customer Flow

```
入座 Seat → 扫描 QR 码 Scan QR → 选择语言 Choose lang (ZH/EN)
→ 浏览菜单 Browse menu → 加入购物车 Add to cart → 发起支付 Pay
→ 支付成功确认 Payment confirmed → 后厨接单 Kitchen receives
→ 取餐 / 就餐 Enjoy meal → 离座 Leave
```

### 2.2 商家操作流 / Operator Flow

```
开业 → 检查 QR 码完好 → KDS 屏幕亮起 → 接收订单 → 完成备餐 → 标记完成
Open → Check QR codes → KDS lights up → Receive order → Prepare → Mark done
```

---

## 3. 功能清单 / Feature List

### 3.1 顾客端 / Customer Frontend（H5）

- [x] QR 码入口，支持座位号 + 语言参数 `?seat=T01&lang=zh`
- [x] 中英文双语菜单，随页面切换即时切换
- [x] 菜品分类浏览（早餐/主食/饮料/小食/甜点）
- [x] 购物车（增/减/清空）
- [x] 订单确认页（下单前复核）
- [x] Stripe PaymentElement 支付（Visa/MC/Amex/GrabPay/Apple Pay/Google Pay）
- [x] PayNow 支付（生成 QR code 后扫码支付）
- [x] 支付超时处理（15 分钟超时自动取消）
- [x] 订单状态实时轮询（已下单 → 制作中 → 已完成）
- [x] 支付成功/失败引导页

### 3.2 后厨屏 / Kitchen Display System（KDS）

- [x] SSE 实时推送新订单，无需刷新
- [x] 订单列表（按时间倒序）
- [x] 订单状态流转（待接单 → 制作中 → 已完成）
- [x] 手动拒单 + 原因记录
- [x] 语音/视觉提醒
- [x] 完成后自动从主屏消失

### 3.3 后端 / Backend API

- [x] `/v1/seats` 座位管理（CRUD + 状态查询）
- [x] `/v1/menu` 菜单查询（分类 + 菜品）
- [x] `/v1/orders` 订单创建 + 状态管理
- [x] `/v1/payments/create-intent` Stripe PaymentIntent 创建
- [x] `/v1/payments/confirm-paynow` PayNow 支付确认
- [x] `/v1/payments/{id}/status` 支付状态查询
- [x] `/v1/kds/orders` 厨房订单列表（待处理/制作中）
- [x] `/v1/kds/orders/stream` SSE 实时订单流
- [x] `/v1/webhooks/stripe` Stripe Webhook（支付成功自动更新订单）
- [x] `/health` 健康检查
- [x] 支付超时自动取消（后台 worker，每 60 秒检查）

### 3.4 QR 码 / QR Codes

- [x] 22 个独立 QR 码（T01-T12 室内、O01-O04 户外、B01-B06 吧台）
- [x] 每个 QR 码含座位号 + 语言参数
- [x] 中英文双语标签（贴在 QR 码旁边）
- [x] QR 码 PNG 文件：`public/qr-codes/`

---

## 4. 菜单结构 / Menu Structure

### 4.1 分类 / Categories

| ID | 中文名 | English Name |
|---|---|---|
| breakfast | 早餐 | Breakfast |
| mains | 主食 | Mains |
| drinks | 饮料 | Drinks |
| snacks | 小食 | Snacks |
| desserts | 甜点 | Desserts |

### 4.2 座位布局 / Seat Layout

**室内 Indoor（T01–T12）**：12 桌，每桌 2-4 人

**户外 Outdoor（O01–O04）**：4 桌，每桌 2 人

**吧台 Bar（B01–B06）**：6 位，单人高脚凳

**总计 Total：22 个座位 / 22 seats**

---

## 5. 支付方式 / Payment Methods

### 5.1 支持列表 / Supported Methods

| 支付方式 | Type | 说明 |
|---|---|---|
| Visa / Mastercard | 信用卡 Credit Card | Stripe PaymentElement |
| American Express | 信用卡 Credit Card | Stripe PaymentElement |
| GrabPay | 电子钱包 E-wallet | Stripe PaymentElement |
| Apple Pay | 电子钱包 E-wallet | Stripe PaymentElement（Safari only）|
| Google Pay | 电子钱包 E-wallet | Stripe PaymentElement（Chrome only）|
| PayNow | 实时转账 Real-time transfer | 扫码支付，需手动确认 |

### 5.2 支付流程差异 / Payment Flow Differences

**Stripe（信用卡/钱包）**：创建 PaymentIntent → 前端 Stripe.js 加密提交 → Webhook 回调自动确认订单

**PayNow**：创建 PaymentIntent → 生成 Reference → 顾客打开银行 App 扫码 → 15 分钟内手动确认或等待 Webhook 超时

---

## 6. 技术架构 / Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Customer H5                          │
│              https://order.clapcafe.sg/                     │
│                 (Vue 3 + Vite + i18n)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Render Backend                           │
│           https://clap-cafe-qr-order.onrender.com           │
│                  (FastAPI + SQLAlchemy async)               │
│                                                              │
│   ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐  │
│   │   Seats  │  │  Menu    │  │     Payments             │  │
│   │  CRUD    │  │  Items   │  │  Stripe / PayNow         │  │
│   └──────────┘  └──────────┘  └──────────────────────────┘  │
│                                                              │
│   ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐  │
│   │  Orders  │  │   KDS    │  │  Payment Timeout Worker  │  │
│   │          │  │  SSE     │  │  (60s polling, 15min)   │  │
│   └──────────┘  └──────────┘  └──────────────────────────┘  │
└──────────┬────────────────────┬─────────────────────────────┘
           │                    │
           ▼                    ▼
┌──────────────────┐  ┌─────────────────────────────────────────┐
│  Render Postgre  │  │           Upstash Redis                │
│  dpg-d82ucd6k... │  │    cool-teal-123918.upstash.io         │
│                  │  │  • KDS SSE pub/sub                     │
│                  │  │  • Order status cache                  │
└──────────────────┘  └─────────────────────────────────────────┘
                                         │
                                         ▼
                         ┌─────────────────────────────┐
                         │    KDS Display (Vercel)      │
                         │  https://kds.clapcafe.sg/   │
                         │    (Vue 3 + SSE stream)      │
                         └─────────────────────────────┘
```

### 6.1 技术栈 / Tech Stack

| 层级 | 技术 | 说明 |
|---|---|---|
| 前端 H5 | Vue 3 + Vite + TypeScript + Pinia + Vue Router + i18n | 响应式 H5，兼容微信浏览器 |
| KDS | Vue 3 + Vite + TypeScript | 独立部署，Vercel |
| 后端 | Python 3.11 + FastAPI + SQLAlchemy async | Render Web Service |
| 数据库 | PostgreSQL（Render 内置）| 异步驱动 asyncpg |
| 缓存/订阅 | Upstash Redis | KDS SSE pub/sub |
| 支付 | Stripe（Visa/MC/Amex/GrabPay/Apple Pay/Google Pay）+ PayNow | |
| 域名/CDN | Cloudflare | DNS + SSL |
| 部署 | Render（后端）+ Vercel（前端/KDS）+ GitHub Actions（CI）| |

### 6.2 API 端点 / API Endpoints

**座位 Seats**
- `GET /v1/seats` — 所有座位列表
- `GET /v1/seats/{seat_id}` — 单个座位
- `PATCH /v1/seats/{seat_id}/status` — 更新座位状态

**菜单 Menu**
- `GET /v1/menu` — 全量菜单（分类 + 菜品）
- `GET /v1/menu/items/{item_id}` — 单个菜品详情

**订单 Orders**
- `POST /v1/orders` — 创建订单
- `GET /v1/orders/{order_id}` — 查询订单
- `PATCH /v1/orders/{order_id}/cancel` — 取消订单
- `PATCH /v1/orders/{order_id}/reject` — KDS 拒单

**支付 Payments**
- `POST /v1/payments/create-intent` — 创建 PaymentIntent
- `POST /v1/payments/confirm-paynow` — 确认 PayNow 支付
- `GET /v1/payments/{payment_intent_id}/status` — 查询支付状态

**KDS**
- `GET /v1/kds/orders` — 待处理 + 制作中订单
- `GET /v1/kds/orders/stream` — SSE 实时订单流
- `PATCH /v1/kds/orders/{order_id}/status` — 更新制作状态

**Webhook**
- `POST /v1/webhooks/stripe` — Stripe 支付回调

---

## 7. QR 码规范 / QR Code Specification

### 7.1 URL 格式 / URL Format

```
https://order.clapcafe.sg/?seat={SEAT_ID}&lang={LANG}
```

| 参数 | 值 | 说明 |
|---|---|---|
| `seat` | `T01`–`T12`, `O01`–`O04`, `B01`–`B06` | 座位号 |
| `lang` | `zh` / `en` | 语言偏好 |

### 7.2 QR 码文件 / QR Code Files

| 目录 | 说明 |
|---|---|
| `public/qr-codes/` | 22 个 QR 码 PNG，中英双语标签已嵌入 |

### 7.3 QR 码尺寸 / Size

- 物理打印尺寸建议：**3cm × 3cm**（300 DPI 下约 354 × 354 px）
- 建议覆膜防水，建议贴于桌面亚克力立牌或墙面

### 7.4 座位标签模板 / Seat Label Template

每个座位 QR 码旁应附带：

```
中文：扫描点餐｜座位号 {seat}
EN:   Scan to order | Seat {seat}
```

---

## 8. 数据模型 / Data Model

### 8.1 座位 / Seats

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | VARCHAR(10) PK | 主键，如 `T01` |
| `name` | VARCHAR(50) | 显示名，如 `室内 01` |
| `zone` | ENUM | `indoor` / `outdoor` / `bar` |
| `capacity` | INT | 可坐人数 |
| `status` | ENUM | `available` / `occupied` / `reserved` |
| `created_at` | TIMESTAMP | 创建时间 |
| `updated_at` | TIMESTAMP | 更新时间 |

### 8.2 菜品 / MenuItems

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | UUID PK | 主键 |
| `category_id` | VARCHAR(20) FK | 分类 ID |
| `name_zh` | VARCHAR(100) | 中文名 |
| `name_en` | VARCHAR(100) | 英文名 |
| `description_zh` | TEXT | 中文描述 |
| `description_en` | TEXT | 英文描述 |
| `price` | DECIMAL(10,2) | 价格（SGD）|
| `image_url` | VARCHAR(500) | 图片 URL |
| `is_available` | BOOLEAN | 是否可售 |
| `created_at` | TIMESTAMP | 创建时间 |

### 8.3 订单 / Orders

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | UUID PK | 主键 |
| `order_number` | VARCHAR(10) | 展示用编号，如 `A001` |
| `seat_id` | VARCHAR(10) FK | 座位号 |
| `customer_name` | VARCHAR(100) | 顾客姓名（可选）|
| `status` | ENUM | `pending`/`paid`/`preparing`/`ready`/`completed`/`cancelled`/`rejected` |
| `total_amount` | DECIMAL(10,2) | 订单总额 |
| `notes` | TEXT | 备注 |
| `payment_intent_id` | VARCHAR(100) | Stripe PaymentIntent ID |
| `created_at` | TIMESTAMP | 创建时间 |
| `updated_at` | TIMESTAMP | 更新时间 |

### 8.4 订单明细 / OrderItems

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | UUID PK | 主键 |
| `order_id` | UUID FK | 所属订单 |
| `menu_item_id` | UUID FK | 菜品 ID |
| `quantity` | INT | 数量 |
| `unit_price` | DECIMAL(10,2) | 下单时单价 |
| `subtotal` | DECIMAL(10,2) | 小计 |

---

## 9. 业务流程 / Business Flows

### 9.1 完整下单流程 / End-to-End Ordering Flow

```
1. 顾客扫描桌上 QR 码（https://order.clapcafe.sg/?seat=T01&lang=zh）
   Customer scans QR code

2. 前端请求 GET /v1/menu → 显示中英文菜单
   Frontend fetches menu

3. 顾客选择菜品 → 加入购物车
   Customer adds items to cart

4. 顾客点击结算 → POST /v1/orders → 创建订单（状态: pending）
   Customer submits → Order created (pending)

5. 顾客选择支付方式：
   5a. Stripe：POST /v1/payments/create-intent → Stripe.js 提交卡号 → 支付成功
   5b. PayNow：POST /v1/payments/create-intent → 显示 PayNow QR → 顾客扫码支付
   Customer selects payment method

6. Stripe Webhook 回调 → POST /v1/webhooks/stripe → 订单更新为 paid
   Stripe webhook → Order updated to paid

   （或 PayNow）顾客银行转账 → 手动/自动确认 → 订单更新为 paid

7. KDS 实时收到 SSE 推送 → 显示新订单 → 后厨开始备餐
   KDS receives SSE push → Kitchen starts preparing

8. 后厨完成 → KDS 点击完成 → 订单状态 → ready/completed
   Kitchen marks done → Order ready

9. 顾客取餐 → 订单完成
   Customer picks up → Order completed
```

### 9.2 支付超时流程 / Payment Timeout Flow

```
顾客创建订单（pending）
  ↓
15 分钟内完成支付 → Webhook 确认 → paid
  ↓
15 分钟未支付 → 后台 worker（每 60s 检查）
  ↓
超时订单 → cancelled → 座位释放
```

---

## 10. 环境变量 / Environment Variables

### 10.1 后端 / Backend（Render）

| 变量名 | 说明 | 示例 |
|---|---|---|
| `APP_ENV` | 环境 | `production` |
| `DEBUG` | 调试模式 | `false` |
| `DATABASE_URL` | PostgreSQL 连接串（Render 自动提供）| `postgresql://...` |
| `REDIS_URL` | Upstash Redis 连接串 | `redis://default....upstash.io:6379` |
| `STRIPE_SECRET_KEY` | Stripe Secret Key | `sk_live_...` |
| `STRIPE_PUBLISHABLE_KEY` | Stripe Publishable Key | `pk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Stripe Webhook 签名密钥 | `whsec_...` |
| `STRIPE_PAYMENT_TIMEOUT_MINUTES` | 支付超时（分钟）| `15` |
| `CORS_ORIGINS` | 允许的前端域名（逗号分隔）| `https://order.clapcafe.sg` |

### 10.2 前端 / Frontend（Vercel）

| 变量名 | 说明 |
|---|---|
| `VITE_API_BASE_URL` | 后端 API 基础 URL |
| `VITE_STRIPE_PUBLISHABLE_KEY` | Stripe Publishable Key |

---

## 11. 域名规划 / Domain Plan

| 用途 | 域名 | 类型 |
|---|---|---|
| 顾客点餐 H5 | `order.clapcafe.sg` | Vercel 部署 |
| 后厨屏 KDS | `kds.clapcafe.sg` | Vercel 部署 |
| 后端 API | `api.order.clapcafe.sg` | Render 部署 |
| Stripe Webhook | `api.order.clapcafe.sg/v1/webhooks/stripe` | Render |

---

## 12. 安全考量 / Security Considerations

- [x] SQL 注入防护：所有 DB 操作使用 SQLAlchemy ORM 参数化查询
- [x] CORS 白名单：生产环境仅允许 `order.clapcafe.sg` 和 `kds.clapcafe.sg`
- [x] Stripe Webhook 签名验证：所有回调均验签后处理
- [x] 支付超时幂等性：`FOR UPDATE SKIP LOCKED` 防止多 worker 重复处理
- [x] KDS SSE 鉴权：KDS_API_KEY 头部校验
- [x] 不存储卡号：全部通过 Stripe Tokenization处理

---

## 13. 运营参数 / Operational Parameters

| 参数 | 值 | 说明 |
|---|---|---|
| 支付超时 | 15 分钟 | 超过后订单自动取消 |
| 订单轮询间隔 | 5 秒 | 前端轮询订单状态 |
| KDS SSE 心跳 | 30 秒 | 防止连接断开 |
| 超时 worker 检查间隔 | 60 秒 | 每分钟检查一次超时订单 |
| Redis pub/sub channel | `kds:orders` | KDS 实时推送频道 |

---

## 14. 部署状态 / Deployment Status

| 组件 | 状态 | URL |
|---|---|---|
| 后端 Backend | ✅ 已部署 | `https://clap-cafe-qr-order.onrender.com` |
| 数据库 PostgreSQL | ✅ 已创建 | Render 内置 |
| Redis | ✅ 已创建 | `cool-teal-123918.upstash.io` |
| GitHub Repo | ✅ 已创建 | `github.com/dymx101/clap-cafe-qr-order` |
| 前端 H5 | 🔲 待部署 | Vercel |
| KDS | 🔲 待部署 | Vercel |
| Cloudflare DNS | 🔲 待配置 | |
| Stripe Webhook | 🔲 待配置 | |

---

## 15. 已知限制 / Known Limitations

- PayNow 支付需要顾客手动打开银行 App 扫码，确认时间不确定；建议优先推广 Stripe 支付
- Render Free Tier 休眠：若 15 分钟无请求后端会休眠，冷启动约 30 秒
- KDS SSE 在后端休眠后需重新连接
- 座位状态管理目前为手动更新（未来可结合离座检测自动释放）

---

## 16. 未来规划 / Roadmap

- [ ] 微信/支付宝集成（中国游客）
- [ ] 离线支持（PWA + 本地缓存菜单）
- [ ] 积分/会员系统
- [ ] 每日推荐菜品
- [ ] 后厨叫号广播
- [ ] 销售数据看板
- [ ] 座位预约功能
- [ ] Stripe ACH / Singapore PayNow 深度集成

---

## 17. 附录：QR 码座位对照表 / Appendix: Seat QR Code Reference

| 座位号 | 区域 | 标签 Label |
|---|---|---|
| T01–T12 | 室内 Indoor | 室内 01–12 |
| O01–O04 | 户外 Outdoor | 户外 01–04 |
| B01–B06 | 吧台 Bar | 吧台 01–06 |

QR 码文件路径: `src/frontend/public/qr-codes/`

---

*文档版本: v1.0 | 最后更新: 2026-05-14*
*Document version: v1.0 | Last updated: 2026-05-14*
