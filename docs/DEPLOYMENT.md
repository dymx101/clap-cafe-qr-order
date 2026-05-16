# Clap Cafe 扫码点餐系统 — 部署指南
# Clap Cafe QR Ordering System — Deployment Guide

**文档版本:** v1.1
**日期:** 2026-05-16
**基于:** ENGINEERING.md v1.1

---

## 目录

1. [基础架构总览](#1-基础架构总览)
2. [已部署服务](#2-已部署服务)
3. [后端 Railway 部署](#3-后端-railway-部署)
4. [Admin Panel Vercel 部署](#4-admin-panel-vercel-部署)
5. [前端 Vercel 部署](#5-前端-vercel-部署)
6. [KDS Vercel 部署](#6-kds-vercel-部署)
7. [Cloudflare DNS 配置](#7-cloudflare-dns-配置)
8. [Stripe 配置](#8-stripe-配置)
9. [QR 码生成](#9-qr-码生成)
10. [环境变量清单](#10-环境变量清单)
11. [部署 Checklist](#11-部署-checklist)
12. [GitHub Actions CI](#12-github-actions-ci)

---

## 1. 基础架构总览

```
用户手机
  │
  ├─ QR码: https://order.clapcafe.sg/?seat=T01&lang=zh
  │         ────────────────────────────────────────
  │         Vercel (Frontend H5)
  │            │  /api/* → rewrite → clap-cafe-qr-order.onrender.com
  │            ▼
  │         Render (FastAPI Backend)
  │            ├─ PostgreSQL (Render)
  │            ├─ Redis (Upstash)
  │            └─ Stripe Webhook
  │
  ├─ Admin 管理面板: https://clap-cafe-admin.netlify.app
  │         Netlify (Admin Vue 3)
  │            └─ /api/* → clap-cafe-qr-order.onrender.com/v1/
  │
  └─ KDS 平板: https://kds.clapcafe.sg
                Vercel (KDS Vue 3)
                  └─ SSE → clap-cafe-qr-order.onrender.com/v1/kds/stream
```

### 域名

| 用途 | 域名 | 指向 |
|------|------|------|
| 顾客点餐 H5 | `order.clapcafe.sg` | Vercel Frontend |
| Admin 管理面板 | `admin.clapcafe.sg` | Netlify Admin |
| KDS 后厨端 | `kds.clapcafe.sg` | Vercel KDS |
| API 后端 | `api.order.clapcafe.sg` | Render |
| Stripe Webhook | `api.order.clapcafe.sg/v1/webhooks/stripe` | Render |

---

## 2. 已部署服务

> **状态:** 生产环境已部署 (2026-05-16)

| 服务 | 平台 | URL | 状态 |
|------|------|-----|------|
| Backend API | Render | `clap-cafe-qr-order.onrender.com` | ✅ Running |
| Frontend H5 | Vercel | `frontend-clap-cafe.vercel.app` | ✅ Running |
| KDS Kitchen | Vercel | `kds-sandy.vercel.app` | ✅ Running |
| Admin Panel | **Netlify** | `clap-cafe-admin.netlify.app` | ✅ Running |

> **注意:** Admin Panel 部署在 **Netlify**（而非 Vercel），以避免 Vercel Edge 认证层的浏览器访问限制问题。

### 验证已部署服务

```bash
# API 健康检查
curl https://clap-cafe-qr-order.onrender.com/health
# → {"status":"ok","timestamp":"...","version":"1.0.0"}

# Menu API
curl "https://clap-cafe-qr-order.onrender.com/v1/menu?lang=zh"
# → 返回完整菜单 JSON

# Admin API（需要 JWT token）
curl https://clap-cafe-qr-order.onrender.com/v1/admin/categories/
# → {"detail":"Missing authorization header"}
```

---

## 3. 后端 Render 部署

> **注意:** Backend currently deployed on Render. Railway migration is documented in Section 3a for future reference.

文件位置: `src/backend/Dockerfile`

### 安全特性

- **多阶段构建**: builder stage 编译依赖，runtime stage 只运行
- **Digest Pinning**: `python:3.11-slim@sha256:...` 防止供应链攻击
- **非 root 用户**: `appuser:appgroup` (UID 1000)
- **Health Check**: `/health` 端点，30秒间隔
- **只读文件系统**: 仅 `/app` 可写（Railway 默认）

### 获取当前 Digest

```bash
# 在有 Docker 环境的机器上执行
docker pull python:3.11-slim
docker inspect --format='{{index .RepoDigests 0}}' python:3.11-slim
# 输出: python@sha256:6e4a843db37e3c5d2e39cc4d0e1c4f460484f2a3c9f3ed3b1f5b3c7e9d6e9f0
```

> **注意**: 以上 digest 是占位符。实际部署前请用上述命令获取真实值并更新到 Dockerfile 两处。

### Railway 部署步骤

```bash
# 1. 安装 Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# 2. 登录
railway login

# 3. 初始化项目（已在 GitHub 连接则跳过）
railway init
# → 选择 "Empty Project"，命名为 "Clap Cafe API"

# 4. 关联 GitHub repo
railway link <project-id>

# 5. 添加 PostgreSQL
railway add
# → 选择 "PostgreSQL"
# → 记下 DATABASE_URL

# 6. 添加 Redis
railway add
# → 选择 "Redis"
# → 记下 REDIS_URL

# 7. 配置环境变量（在 Railway Dashboard 或 CLI）
railway env set APP_ENV=production
railway env set DEBUG=false
railway env set STRIPE_SECRET_KEY=sk_live_...
railway env set STRIPE_PUBLISHABLE_KEY=pk_live_...
railway env set STRIPE_WEBHOOK_SECRET=whsec_...
railway env set CORS_ORIGINS=https://order.clapcafe.sg,https://kds.clapcafe.sg,https://admin.clapcafe.sg
railway env set KDS_API_KEY=<generate-strong-random-key>
railway env set SECRET_KEY=<generate-strong-random-key>

# 8. 部署
railway up

# 9. 验证健康检查
curl https://api.order.clapcafe.sg/health
# 应返回: {"status":"ok","timestamp":"...","version":"1.0.0"}

# 10. 运行数据库迁移
railway run alembic upgrade head

# 11. 初始化种子数据
railway run python -m app.scripts.init_seats
railway run python -m app.scripts.seed_data
```

### Railway.toml 配置

```toml
[build]
dockerfilePath = "Dockerfile"

[deploy]
healthCheckPath = "/health"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port 8000"

[settings]
minReplicas = 1
maxReplicas = 3
maxTimeout = 30
```

---

## 4. Admin Panel Netlify 部署

文件位置: `src/admin/netlify.toml` ✅ 已创建

### 部署步骤

```bash
# 1. 安装 Netlify CLI
npm install -g netlify-cli

# 2. 登录
netlify login

# 3. 部署
cd src/admin
netlify deploy --prod --dir=dist
# → 输入项目名称，例如 clap-cafe-admin
# → 选择 dymx101's team
# → 部署完成，获取 URL: https://clap-cafe-admin.netlify.app
```

### netlify.toml 配置

```toml
[build]
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "20"

[[redirects]]
  from = "/api/*"
  to = "https://clap-cafe-qr-order.onrender.com/v1/:splat"
  status = 200
  force = true
```

### 自定义域名

1. Netlify Dashboard → Sites → clap-cafe-admin → **Domain management**
2. 添加自定义域名 `admin.clapcafe.sg`
3. Cloudflare 中添加 CNAME: `admin.clapcafe.sg → clap-cafe-admin.netlify.app`

---

## 5. 前端 Vercel 部署

文件位置: `src/frontend/vercel.json` ✅ 已创建

### 部署步骤

```bash
# 1. 安装 Vercel CLI
npm i -g vercel

# 2. 登录
vercel login

# 3. 进入 frontend 目录
cd src/frontend

# 4. 预览部署
vercel

# 5. 生产部署
vercel --prod

# 6. 设置环境变量
vercel env add VITE_API_BASE_URL
# → 输入: https://api.order.clapcafe.sg
```

### vercel.json 说明

```json
{
  "rewrites": [
    // 所有 /api/* 请求代理到后端
    { "source": "/api/:path*", "destination": "https://api.order.clapcafe.sg/v1/:path*" }
  ]
}
```

前端代码中 API 调用使用相对路径 `/api/...`，Vercel rewrite 会自动转发到后端。

### 自定义域名

1. Vercel Dashboard → frontend 项目 → Settings → Domains
2. 添加 `order.clapcafe.sg`
3. Cloudflare 中添加 CNAME: `order.clapcafe.sg → cname.vercel-dns.com`

---

## 6. KDS Vercel 部署

文件位置: `src/kds/vercel.json` ✅ 已创建

### 部署步骤

```bash
cd src/kds
vercel                    # 预览
vercel --prod             # 生产

# 环境变量
vercel env add VITE_API_BASE_URL
# → 输入: https://api.order.clapcafe.sg
```

### 自定义域名

1. Vercel Dashboard → kds 项目 → Settings → Domains
2. 添加 `kds.clapcafe.sg`

---

## 7. Cloudflare DNS 配置

### DNS 记录设置

在 Cloudflare Dashboard → Domains → clapcafe.sg → DNS 设置：

| 类型 | 名称 | 内容 | 代理状态 |
|------|------|------|----------|
| A | `api.order` | Railway 分配的域名或 IP | DNS only |
| CNAME | `order` | `cname.vercel-dns.com` | Proxied |
| CNAME | `admin` | `cname.vercel-dns.com` | Proxied |
| CNAME | `kds` | `cname.vercel-dns.com` | Proxied |
| TXT | `order` | `v=spf1 include:sendgrid.net ~all` | — |

> **注意**: A 记录指向 Railway 分配的域名（格式类似 `economical-train.up.railway.app`）。Railway 分配的是动态域名，建议在 Cloudflare 页面规则中配置。

### SSL/TLS 设置

1. SSL/TLS → Overview → **Full (strict)**
2. 边缘证书由 Cloudflare 自动管理
3. 始终使用 HTTPS: SSL/TLS → Edge Certificates → Always Use HTTPS = ON

### 页面规则

| 匹配模式 | 功能 |
|----------|------|
| `order.clapcafe.sg/*` | Always Use HTTPS |
| `kds.clapcafe.sg/*` | Always Use HTTPS |
| `admin.clapcafe.sg/*` | Always Use HTTPS |
| `api.order.clapcafe.sg/*` | Always Use HTTPS, Cache Level = Basic |

---

## 8. Stripe 配置

### 获取 Stripe API Keys

1. [Stripe Dashboard](https://dashboard.stripe.com/apikeys) → Developers → API keys
2. 复制 **Publishable key** (`pk_live_...`) → 填入 `STRIPE_PUBLISHABLE_KEY`
3. 复制 **Secret key** (`sk_live_...`) → 填入 `STRIPE_SECRET_KEY`

> 测试模式前缀: `pk_test_` / `sk_test_`。上线前切换到 live keys。

### 配置 Webhook

1. Stripe Dashboard → Developers → Webhooks
2. 点击 **Add endpoint**
3. **Endpoint URL**: `https://api.order.clapcafe.sg/v1/webhooks/stripe`
4. 监听事件（全部勾选）:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.canceled`
   - `charge.refunded`
5. 点击 **Add endpoint**
6. 复制 **Webhook signing secret** (`whsec_...`) → 填入 `STRIPE_WEBHOOK_SECRET`

### 本地测试 Stripe Webhook

```bash
# 安装 Stripe CLI
brew install stripe/stripe-cli/stripe

# 登录
stripe login

# 转发 webhook 到本地
stripe listen --forward-to localhost:8000/v1/webhooks/stripe

# 复制输出的 whsec_xxx 到 .env
# STRIPE_WEBHOOK_SECRET=whsec_...

# 触发测试事件
stripe trigger payment_intent.succeeded
stripe trigger payment_intent.canceled

# 验证订单状态更新
curl http://localhost:8000/v1/orders/CC-20260514-001/status
```

### Stripe 费率（新加坡，2024）

| 支付方式 | 费率 |
|----------|------|
| Visa/Mastercard | 3.5% + S$0.50 |
| GrabPay | 3.5% + S$0.50 |
| PayNow | 3.5% + S$0.50 |
| 退款 | 免费 |

来源: [Stripe Singapore Pricing](https://stripe.com/sg/pricing)

---

## 9. QR 码生成

文件位置: `scripts/generate_qrcodes.py` ✅ 见下方

### 安装依赖

```bash
uv pip install qrcode pillow
# 或
pip install qrcode pillow
```

### 执行

```bash
python scripts/generate_qrcodes.py
```

输出:
- `public/qr-codes/T01_zh.png` / `T01_en.png`
- `public/qr-codes/O01_zh.png` / `O01_en.png`
- `public/qr-codes/B01_zh.png` / `B01_en.png`
- `public/qr-codes/QR-Codes-Summary.pdf`（可选汇总页）

### 打印规格

- QR 码尺寸: 5cm × 5cm（300 DPI 下约 590×590 px）
- 误差校正等级: **H**（最高 30% 损失仍可扫描）
- 静默区: QR 码周围保留 4 个模块宽度空白

---

## 10. 环境变量清单

### 后端 `.env`（ Railway 环境变量）

| 变量名 | 示例值 | 说明 |
|--------|--------|------|
| `APP_ENV` | `production` | 运行环境 |
| `DEBUG` | `false` | 关闭 debug 日志 |
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host:5432/clapcafe` | PostgreSQL 连接串 |
| `REDIS_URL` | `redis://host:6379/0` | Redis 连接串 |
| `STRIPE_SECRET_KEY` | `sk_live_...` | Stripe Secret Key |
| `STRIPE_PUBLISHABLE_KEY` | `pk_live_...` | Stripe Publishable Key |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` | Stripe Webhook 签名 |
| `STRIPE_PAYMENT_TIMEOUT_MINUTES` | `15` | 支付超时时间 |
| `CORS_ORIGINS` | `https://frontend-clap-cafe.vercel.app,https://kds-sandy.vercel.app,https://clap-cafe-admin.netlify.app` | CORS 白名单 |
| `KDS_API_KEY` | `<随机字符串>` | KDS 内部认证密钥 |
| `SECRET_KEY` | `<随机字符串>` | JWT 签名密钥 |

### 前端 `.env`

| 变量名 | 示例值 | 说明 |
|--------|--------|------|
| `VITE_API_BASE_URL` | `https://api.order.clapcafe.sg` | 构建时嵌入 |

### KDS `.env`

| 变量名 | 示例值 | 说明 |
|--------|--------|------|
| `VITE_API_BASE_URL` | `https://api.order.clapcafe.sg` | 构建时嵌入 |

### Admin `.env`

| 变量名 | 示例值 | 说明 |
|--------|--------|------|
| `VITE_API_BASE_URL` | `https://api.order.clapcafe.sg` | 构建时嵌入 |

---

## 11. 部署 Checklist

### 上线前必查（对应 T50）

- [x] **T50.1** 所有 `.env` 变量已配置，无真实密钥残留 ✅
- [x] **T50.2** `CORS_ORIGINS` 不再是 `*`，已配置具体域名 ✅
- [ ] **T50.3** Stripe 费率已确认（GrabPay/PayNow 额外收费）
- [ ] **T50.4** PayNow 真实扫码测试（Stripe test mode）
- [ ] **T50.5** QR 码各机型扫码测试（iOS Safari / Android Chrome / 微信）
- [ ] **T50.6** KDS 平板横屏显示正常（iPad 10.2" 推荐）
- [x] **T50.7** 生产环境日志级别为 `INFO`，非 `DEBUG` ✅
- [ ] **T50.8** UptimeRobot 监控 `/health` 端点（60秒轮询）
- [ ] **T50.9** Cloudflare Analytics 确认请求正常
- [ ] **T50.10** 数据库备份恢复流程已验证

### 上线后 24 小时内

- [ ] 监控 Stripe Dashboard 支付成功率
- [ ] 监控 Railway 日志错误率
- [ ] 确认 KDS SSE 连接稳定
- [ ] 收集首批真实用户反馈

---

## 12. GitHub Actions CI

文件位置: `.github/workflows/ci.yml`

### 功能

- **后端**: `ruff format` + `ruff check` + `pyright`
- **Frontend/Admin/KDS**: type-check + build
- 数据库迁移验证（dry-run）
- 多 Python/Node 版本矩阵测试

### 配置

需要在 GitHub Secrets 中配置以下变量：

| Secret | 说明 |
|--------|------|
| `VERCEL_TOKEN` | Vercel API Token |
| `VERCEL_ORG_ID` | Vercel Organisation ID |
| `VERCEL_FRONTEND_ID` | Frontend Vercel Project ID |
| `VERCEL_ADMIN_ID` | Admin Vercel Project ID |
| `VERCEL_KDS_ID` | KDS Vercel Project ID |

### 本地 pre-commit 钩子（可选）

```bash
# 安装 pre-commit
pip install pre-commit

# 安装钩子
pre-commit install

# 手动运行
pre-commit run --all-files
```

---

## 快速启动命令汇总

```bash
# 1. 后端部署（Railway）
railway login
railway init
railway add postgres
railway add redis
railway env set $(cat .env.production)
railway up

# 2. 运行迁移
railway run alembic upgrade head

# 3. 初始化座位
railway run python -m app.scripts.init_seats

# 4. Admin 部署（Netlify）
cd src/admin
netlify deploy --prod --dir=dist

# 5. 前端部署（Vercel）
cd src/frontend
vercel --prod

# 6. KDS 部署（Vercel）
cd src/kds
vercel --prod

# 7. 生成 QR 码
python scripts/generate_qrcodes.py
```
