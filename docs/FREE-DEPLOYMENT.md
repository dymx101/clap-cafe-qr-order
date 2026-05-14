# Clap Cafe 扫码点餐系统 — 免费部署方案（替代 Railway）
# Clap Cafe QR Ordering System — Free Deployment (Alternative to Railway)

**文档版本:** v1.0
**日期:** 2026-05-14
**前提:** Railway 需付费订阅，本方案使用完全免费服务

---

## 免费技术栈

| 组件 | 推荐服务 | 免费额度 | 限制 |
|------|---------|---------|------|
| PostgreSQL | Supabase | 500MB 存储，2GB 传输/月 | 睡眠后唤醒需 30s |
| Redis | Upstash | 1GB，10K 命令/天 | 超出命令限制降速 |
| 后端 API | Render | 500h/月（共享 CPU 512MB） | 15min 无活动进入睡眠 |
| 前端 H5 | Vercel | 无限请求 | 无 |
| KDS | Vercel | 无限请求 | 无 |
| CDN/DNS | Cloudflare | 免费 | 无 |

> **咖啡店场景评估**: 用餐高峰 11:00-14:00、18:00-21:00 几乎不会触发 Render 睡眠。
> 凌晨低峰期睡眠无影响。**月成本: $0**。

---

## 目录

1. [免费方案 vs Railway 对比](#1-免费方案-vs-railway-对比)
2. [Supabase PostgreSQL 申请](#2-supabase-postgresql-申请)
3. [Upstash Redis 申请](#3-upstash-redis-申请)
4. [Render 后端部署](#4-render-后端部署)
5. [Vercel 前端部署](#5-vercel-前端部署)
6. [Cloudflare DNS 配置](#6-cloudflare-dns-配置)
7. [环境变量汇总](#7-环境变量汇总)
8. [完整部署 Checklist](#8-完整部署-checklist)

---

## 1. 免费方案 vs Railway 对比

| 维度 | Railway（付费） | Render + Supabase + Upstash（免费） |
|------|----------------|-------------------------------------|
| PostgreSQL | $5-20/月（按量） | Supabase 永久免费（500MB） |
| Redis | $5-10/月 | Upstash 永久免费（1GB） |
| 后端部署 | $5-20/月 | Render 500h/月（够用） |
| 前端部署 | — | Vercel 免费 |
| SSL | 自动 | 自动 |
| 冷启动 | <2s | Render 冷启动 ~30s |
| 睡眠策略 | 永不休眠 | 15min 无活动进入睡眠 |
| 信用卡 | 必须 | Supabase/Upstash 不需要 |

---

## 2. Supabase PostgreSQL 申请

### 2.1 创建账号

1. 访问 [supabase.com](https://supabase.com) → Sign up（可用 GitHub 登录）
2. **不需要信用卡**
3. 创建新项目 → 填写：
   - Organization: Clap Cafe
   - Name: `clap-cafe-db`
   - Database Password: **生成强随机密码，保存到 1Password**
   - Region: `Southeast Asia (Singapore)` — 延迟最低

### 2.2 获取连接信息

项目 Dashboard → Settings → Database → Connection string：

```
# URI 格式（用于代码）
postgresql+asyncpg://postgres.[ref]:[password]@aws-[region].aws.prod.supabase.com:5432/postgres

# 示例（你自己的 ref 和 password）
postgresql+asyncpg://postgres.xxxxxx:abcdefgh@aws.ap-southeast-1.aws.prod.supabase.com:5432/postgres
```

> **注意**: 连接信息长期有效，除非重置密码。

### 2.3 启用 pgvector（可选，菜单 AI 搜索用）

Supabase Dashboard → SQL Editor → 运行：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2.4 配置连接池（重要）

Supabase Dashboard → Connection Pooling：
- Pool Mode: **Transaction**（默认）
- Pool Size: **默认即可**

Supabase 推荐使用连接池而非直连，格式不变，只是不需要加 `:6543` 端口。

---

## 3. Upstash Redis 申请

### 3.1 创建账号

1. 访问 [upstash.com](https://upstash.com) → Sign up（GitHub 登录）
2. **不需要信用卡**

### 3.2 创建 Redis 数据库

1. Console → Create Database
2. Name: `clap-cafe-redis`
3. Region: `Singapore`（最低延迟）
4. Plan: **Free**

### 3.3 获取连接信息

Redis Dashboard → REST API → `.env` 格式：

```
UPSTASH_REDIS_REST_URL=https://[xxx].upstash.io
UPSTASH_REDIS_REST_TOKEN=[token字符串]
```

> Upstash 同时提供标准 Redis 协议连接：
> ```
> redis://default.[xxx]:[token]@xxx.upstash.io:6379
> ```

### 3.4 免费额度和告警

免费版：1GB 存储，10,000 命令/天。

设置告警（防止超限）：
1. Upstash Console → Billing → Usage Alerts
2. 设定阈值 80%（8,000 命令/天）
3. 告警邮箱通知

---

## 4. Render 后端部署

### 4.1 创建 Web Service

1. [render.com](https://render.com) → Sign up（GitHub 登录）
2. Dashboard → New → **Web Service**
3. 关联 GitHub repo: `your-username/clap-cafe-qr-order`
4. 设置：

| 配置项 | 值 |
|--------|-----|
| Name | `clap-cafe-api` |
| Region | Singapore |
| Branch | `main` |
| Root Directory | `src/backend` |
| Runtime | `Dockerfile` |
| Plan | **Free** |

5. 点击 **Create Web Service**

### 4.2 环境变量配置

在 Render Dashboard → Environment → 添加以下变量：

```
APP_ENV=production
DEBUG=false
DATABASE_URL=postgresql+asyncpg://postgres.[ref]:[password]@aws-ap-southeast-1.aws.prod.supabase.com:5432/postgres
REDIS_URL=redis://default.[xxx]:[token]@xxx.upstash.io:6379
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PAYMENT_TIMEOUT_MINUTES=15
CORS_ORIGINS=https://order.clapcafe.sg,https://kds.clapcafe.sg
KDS_API_KEY=<generate: openssl rand -hex 32>
```

### 4.3 冷启动问题

Render Free 套餐 15 分钟无活动进入睡眠。咖啡店场景：
- 高峰期（午/晚）不会睡眠
- 凌晨 2:00-6:00 睡眠无影响
- 早上第一次扫码需等待 ~30s

**优化建议**：用 [Kaffeine](https://kaffeine.heroku.com/) 或 [cron-job.org](https://cron-job.org) 每 10 分钟 ping 一次 `https://api.order.clapcafe.sg/health`，保持活跃：

```
# cron-job.org 免费计划，设定每 10 分钟请求
GET https://api.order.clapcafe.sg/health
```

### 4.4 自定义域名 + SSL

1. Render Dashboard → clap-cafe-api → Settings → Custom Domains
2. 添加 `api.order.clapcafe.sg`
3. Render 自动颁发 SSL 证书（Let's Encrypt）
4. DNS 配置见第 6 节

### 4.5 健康检查

Render 免费版使用 `/health` 端点。验证：
```bash
curl https://clap-cafe-api.onrender.com/health
# 应返回: {"status":"ok","timestamp":"...","version":"1.0.0"}
```

### 4.6 Supabase 本地开发连接

开发时使用 Supabase 本地 CLI 或直接连云端：

```bash
# .env.local 开发
DATABASE_URL=postgresql+asyncpg://postgres.[ref]:[password]@aws-ap-southeast-1.aws.prod.supabase.com:5432/postgres
```

---

## 5. Vercel 前端部署

### 5.1 H5 点餐前端

```bash
cd src/frontend
vercel --prod
```

Vercel Dashboard → 项目 → Settings → Environment Variables：
```
VITE_API_BASE_URL=https://api.order.clapcafe.sg
```

添加自定义域名 `order.clapcafe.sg`（见第 6 节）。

### 5.2 KDS 后厨端

```bash
cd src/kds
vercel --prod
```

Vercel Dashboard → 项目 → Settings → Environment Variables：
```
VITE_API_BASE_URL=https://api.order.clapcafe.sg
```

添加自定义域名 `kds.clapcafe.sg`（见第 6 节）。

### 5.3 vercel.json API 代理（已配置）

```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://api.order.clapcafe.sg/v1/:path*" }
  ]
}
```

前端所有 `/api/*` 请求自动代理到 Render 后端，无需后端配置 CORS。

---

## 6. Cloudflare DNS 配置

在 Cloudflare Dashboard → clapcafe.sg → DNS：

| 类型 | 名称 | 内容 | 代理状态 |
|------|------|------|----------|
| A | `api.order` | Render 分配的域名（见下方） | DNS only |
| CNAME | `order` | `cname.vercel-dns.com` | Proxied |
| CNAME | `kds` | `cname.vercel-dns.com` | Proxied |

**获取 Render A 记录值**：
Render Dashboard → clap-cafe-api → Details → 查看分配域名，类似：
`clap-cafe-api.onrender.com`

> 如果 Render 只提供 CNAME，用 CNAME 代替 A 记录，代理状态改为 DNS only。

**SSL/TLS**：
- SSL/TLS → Overview → **Full (strict)**
- Edge Certificates → Always Use HTTPS = ON

---

## 7. 环境变量汇总

### 生产环境（Render）

| 变量名 | 示例值 | 来源 |
|--------|--------|------|
| `APP_ENV` | `production` | 固定 |
| `DEBUG` | `false` | 固定 |
| `DATABASE_URL` | `postgresql+asyncpg://postgres.x:pass@aws-ap-southeast-1.aws.prod.supabase.com:5432/postgres` | Supabase |
| `REDIS_URL` | `redis://default.x:token@xxx.upstash.io:6379` | Upstash |
| `STRIPE_SECRET_KEY` | `sk_test_...` | Stripe Dashboard |
| `STRIPE_PUBLISHABLE_KEY` | `pk_test_...` | Stripe Dashboard |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` | Stripe Dashboard |
| `STRIPE_PAYMENT_TIMEOUT_MINUTES` | `15` | 固定 |
| `CORS_ORIGINS` | `https://order.clapcafe.sg,https://kds.clapcafe.sg` | 固定 |
| `KDS_API_KEY` | `<openssl rand -hex 32>` | 自己生成 |

### 前端 / KDS（Vercel）

| 变量名 | 值 |
|--------|-----|
| `VITE_API_BASE_URL` | `https://api.order.clapcafe.sg` |

---

## 8. 完整部署 Checklist

### 部署顺序

```
□ 1. Supabase PostgreSQL 创建完成，获取 DATABASE_URL
□ 2. Upstash Redis 创建完成，获取 REDIS_URL
□ 3. Supabase SQL Editor 运行数据库迁移
□ 4. Supabase SQL Editor 初始化座位数据
□ 5. Render 后端部署完成，健康检查通过
□ 6. Vercel H5 前端部署完成
□ 7. Vercel KDS 部署完成
□ 8. Cloudflare DNS 解析生效（等待 5 分钟）
□ 9. Stripe Webhook 配置完成
□ 10. QR 码生成并打印（scripts/generate_qrcodes.py）
□ 11. 测试完整点餐流程（test mode）
□ 12. 测试支付（PayNow Stripe test mode）
□ 13. 设定 Upstash 用量告警（80%）
□ 14. 设定 Render 监控（可选 UptimeRobot）
□ 15. cron-job.org ping 每 10 分钟（防止 Render 睡眠）
```

### 数据库迁移命令

```bash
# 方式 A: 直接用 alembic（推荐）
alembic upgrade head

# 方式 B: 用 Supabase SQL Editor 粘贴 migrations/*.sql 内容手动执行
```

### 座位初始化

Supabase SQL Editor：
```sql
-- 室内 T01-T12
INSERT INTO seats (seat_id, zone, seat_number, status)
SELECT 'T' || LPAD(i::text, 2, '0'), 'T', i, 'available'
FROM generate_series(1, 12) AS i
ON CONFLICT (seat_id) DO NOTHING;

-- 户外 O01-O04
INSERT INTO seats (seat_id, zone, seat_number, status)
SELECT 'O' || LPAD(i::text, 2, '0'), 'O', i, 'available'
FROM generate_series(1, 4) AS i
ON CONFLICT (seat_id) DO NOTHING;

-- 吧台 B01-B06
INSERT INTO seats (seat_id, zone, seat_number, status)
SELECT 'B' || LPAD(i::text, 2, '0'), 'B', i, 'available'
FROM generate_series(1, 6) AS i
ON CONFLICT (seat_id) DO NOTHING;
```

### Cron Job 防睡眠配置（推荐）

注册 [cron-job.org](https://cron-job.org)（免费）：

1. 创建账户 → Dashboard → CREATE
2. **Execution URL**: `https://api.order.clapcafe.sg/health`
3. **Schedule**: Every 10 minutes
4. **Timeout**: 30 seconds
5. Notifications: Email on failure only

---

## 月度成本

| 服务 | 费用 |
|------|------|
| Supabase PostgreSQL | $0 |
| Upstash Redis | $0 |
| Render Web Service | $0（500h/月够用） |
| Vercel H5 + KDS | $0 |
| Cloudflare DNS | $0 |
| Stripe 支付手续费 | 按交易笔数（交易量小可忽略） |

**总计: $0/月**

---

## Render vs Railway 优劣

| | Render（免费） | Railway（付费） |
|--|--------------|----------------|
| 冷启动 | ~30s | <2s |
| Redis | 需第三方（Upstash） | 内置 |
| PostgreSQL | 需第三方（Supabase） | 内置 |
| 部署体验 | 简单 | 极简 |
| 生态 | 成熟但偏向静态/CDN | 专为 DB + 服务设计 |
| 超时 | 30s | 60s |
| 并发 | 受限于 512MB RAM | 可升级 |

> 咖啡店系统并发有限（主要午餐/晚餐高峰），Render 免费版足够。
> 若未来月 PV > 100,000 或用户投诉冷启动，再迁移 Railway。
