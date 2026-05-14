# Clap Cafe 扫码点餐系统产品文档
## Clap Cafe QR Ordering System — Product Documentation

**文档版本 / Document Version:** v1.0
**发布日期 / Release Date:** 2026-05-14
**适用门店 / Store:** Clap Cafe Singapore — #01-02, Coliwoo Midtown, 141 Middle Rd, Singapore 188976

---

## 1. 产品概述 / Product Overview

### 1.1 项目背景 / Background

Clap Cafe Singapore 是一家位于武吉士区（Bugis）的中型精品咖啡馆，主打特色饮品和轻食。目前采用人工点餐模式，高峰时段排队时间长，客户体验有待提升。

本系统通过在每张餐桌放置独立 QR 码，实现顾客自助扫码点餐、自动关联座位号、支持新加坡主流电子支付的全流程自动化。

### 1.2 核心价值 / Core Value Proposition

| 维度 / Dimension | 现状 / Current State | 目标 / Target State |
|-----------------|---------------------|-------------------|
| 点餐方式 / Ordering | 人工柜台点餐 / Counter service | QR 扫码 + 柜台并行 / QR + Counter |
| 平均点餐耗时 / Avg. order time | 5-8 分钟（假设）/ 5-8 min (estimated) | < 2 分钟 / < 2 min |
| 座位关联 / Seat mapping | 无 / None | QR 内嵌座位号，自动同步后厨 / QR auto-carries seat ID |
| 支付方式 / Payment | 现金 + 单一支付 / Cash only | 全电子支付 / Full e-payment |
| 目标客群 / Target users | — | 年轻人 + 游客 / Young people + tourists |
| 定位 / Positioning | — | 柜台点餐的补充，非替代 / Supplementary to counter ordering |

**说明：** QR 扫码是附加选项，不是唯一入口。柜台点餐保留，适合年长顾客或特殊需求人群。

### 1.3 成功指标 / Success Metrics

> ⚠️ **注意：** 咖啡店尚未开业，以下为上线后需要通过实际运营数据统计的目标值，非已有 baseline。运营满 1 个月后统计初始数据，目标基于合理假设设定，待数据验证后调整。

**上线后测量指标（MVP 上线后 1 个月）：**

| 指标 / Metric | 目标 / Target | 测量方式 / How to Measure |
|--------------|--------------|--------------------------|
| QR 扫码渗透率 | ≥ 40% | 订单来源统计（QR vs 柜台）|
| 扫码用户平均点餐时长 | < 2 分钟 | 提交订单时间戳 - 开始点餐时间戳 |
| 支付成功率 | ≥ 99% | Stripe Dashboard |
| 扫码到下单转化率 | ≥ 50% | QR 扫描 PV / 实际订单数 |

**MVP 上线前准备清单：**
- [ ] 高峰时段（周六/周日中午）实地掐表记录柜台点餐平均耗时
- [ ] 统计目标客群（年轻人+游客）占总客流占比
- [ ] 记录开业后第 1 周每日的 QR 扫码使用率（每日更新）

---

## 2. 功能规格 / Functional Specifications

### 2.1 核心功能 / Core Features

#### F1: 扫码入口 / Scan-to-Order

- 每桌独立 QR 码，内嵌 URL 格式：`https://order.clapcafe.sg/?seat={SEAT_ID}&lang={LANG}`
- 支持微信/小红书/浏览器全平台扫描
- 首次访问自动识别用户语言偏好（中文/English），可手动切换
- 无需下载 App，基于 H5 响应式页面

#### F2: 菜单展示 / Menu Display

- 实时展示当日菜单（含节假日特别套餐）
- 支持中英文双语切换
- 商品分类：咖啡、茶饮、奶茶、气泡水、甜点、轻食、套餐
- 每件商品展示：名称、价格（SGD）、图片、规格选项、备注栏
- 规格选项：杯型（S/M/L）、甜度（无糖/少糖/正常/多糖）、温度（冰/热/去冰）、加料
- 库存状态实时显示（售罄自动灰显）

#### F3: 购物车 / Cart

- 加入购物车后自动保存，支持中途退出
- 购物车角标实时显示商品数量
- 支持增减数量、删除单项、清空购物车
- 实时显示金额明细：小计 + 税（GST 9%）+ 总计

#### F4: 座位号关联 / Seat Association

- QR 码扫描后自动携带座位号（如 "Table 03" / "3号桌"），顾客无需选择
- 订单提交后座位号自动写入 staff 终端（KDS），后厨直接看到送餐桌号
- 支持 staff 手动修正座位号（用于拼桌等特殊情况）
- 顾客端和后厨端均显示座位号，确保送餐准确

#### F5: 订单提交 / Order Submission

- 提交前展示完整订单预览（含座位号）
- 支持顾客备注（过敏原、少辣等）
- 提交后生成唯一订单号（格式：`CC-{YYYYMMDD}-{SEQ}`）
- 订单状态：已提交 → 已确认 → 制作中 → 已完成 → 已取餐

#### F6: 订单追踪 / Order Tracking

- 实时推送订单状态更新（轮询 fallback，MVP 阶段不引入 WebSocket）
- 顾客端显示预计等待时间
- 支持历史订单查询（30 天内）

#### F7: 后厨通知 / Kitchen Display

- 后厨端（KDS）实时接收新订单
- 订单按时间倒序排列
- 支持接单/拒单（缺货时需选原因）操作
- 完成制作后点击"完成"，顾客端同步更新

#### F8: 打印输出 / Print Output

- 支持 USB/蓝牙小票打印机（ESC/POS 协议）
- 每张订单自动打印：订单号、座位号、时间、商品明细、总价、支付状态
- 厨房联打：同一订单分单打印（饮品类/食品类分开）

---

## 3. QR 码设计 / QR Code Design

### 3.1 QR 码生成规则 / QR Generation Rules

每个座位生成独立 QR 码，URL 模板：

```
https://order.clapcafe.sg/?seat={SEAT_ID}&lang={LANG}
```

| 参数 / Parameter | 说明 / Description | 示例 / Example |
|----------------|-------------------|---------------|
| `seat` | 座位编号 / Seat ID | `T03`（Table 3） |
| `lang` | 首选语言 / Preferred language | `zh` / `en` |

### 3.2 QR 码规格 / QR Specifications

| 项目 / Item | 规格 / Spec |
|------------|-----------|
| 尺寸（最小）/ Min size | 3cm × 3cm（建议 5cm × 5cm） |
| 纠错级别 / Error correction | Level M（约 15% 恢复率） |
| 边距 / Quiet zone | 4 个模块宽度 |
| 技术标准 / Tech standard | ISO/IEC 18004 |
| 材质 / Material | 覆膜防水纸（可擦拭） |
| 底色 / Background | 白色（可定制 Logo 底色） |
| Logo 叠加 / Logo overlay | 中心覆盖 ≤ 30% 面积 |

### 3.3 座位 QR 码示例 / Sample QR Codes

| 座位 / Seat | QR URL | 贴纸码 / Sticker Code |
|------------|--------|----------------------|
| Table 01 | `https://order.clapcafe.sg/?seat=T01&lang=zh` | T01 |
| Table 02 | `https://order.clapcafe.sg/?seat=T02&lang=zh` | T02 |
| Table 03 | `https://order.clapcafe.sg/?seat=T03&lang=zh` | T03 |
| ... | ... | ... |
| Table 20 | `https://order.clapcafe.sg/?seat=T20&lang=zh` | T20 |
| Bar Seat | `https://order.clapcafe.sg/?seat=B01&lang=zh` | B01 |

### 3.4 QR 码展示架设计 / Display Stand Design

推荐桌面立牌规格（新加坡常见）：

| 类型 / Type | 尺寸 / Size | 推荐场景 / Use Case |
|------------|------------|-------------------|
| 桌面立牌 / Table tent | A6（105×148mm） | 正式餐桌 |
| 圆形杯垫 / Coaster | 90mm 直径 | 咖啡桌 |
| 墙贴 / Wall sticker | A5（148×210mm） | 靠墙座位 |

---

## 4. 支付集成 / Payment Integration

### 4.1 支持的支付方式 / Supported Payment Methods

#### 优先集成 / Must Have（上线 MVP）

| 支付方式 / Payment Method | 类型 / Type | 说明 / Notes |
|--------------------------|------------|--------------|
| Visa / Mastercard / Amex | 信用卡 / Credit card | 全球游客必备 |
| GrabPay | 电子钱包 / E-wallet | 新加坡第一大电子钱包 |
| PayNow | 银行转账 / Bank transfer | 新加坡覆盖率超 90%，QR 支付 |
| Apple Pay / Google Pay | 钱包 / Wallet | 年轻用户首选 |

#### 次优集成 / Should Have（上线后迭代）

| 支付方式 / Payment Method | 类型 / Type | 说明 / Notes |
|--------------------------|------------|--------------|
| 微信支付 / WeChat Pay | 跨境支付 | 中国游客 |
| Alipay+ | 跨境支付 | 支付宝国际版，中国游客 |
| Singtel Dash | 电信钱包 | 本地用户补充 |

#### 可选集成 / Nice to Have（按需）

| 支付方式 / Payment Method | 类型 / Type | 说明 / Notes |
|--------------------------|------------|--------------|
| Atome | BNPL | 先买后付，年轻消费者 |
| Boost | 电子钱包 | 马来西亚用户 |
| LINE Pay | 电子钱包 | 跨境用户 |

### 4.2 支付网关选型 / Payment Gateway Options

#### 推荐方案 A：Stripe（综合最优）

**优势 / Advantages:**
- 一站式集成 Visa/MC/Amex + GrabPay + PayNow + Apple Pay/Google Pay
- 结算周期 T+7（新加坡标准）
- 管理后台强大，支持退款、对账
- API 文档完善，支持 Node.js/Python/PHP

**接入费用 / Fees:**
- 每笔交易 3.4% + S$0.50（国际卡）
- 国内卡（GrabPay/PayNow）3.25% + S$0.50
- 无月费、无安装费

**推荐指数 / Rating:** ⭐⭐⭐⭐⭐

#### 推荐方案 B：Square（硬件优先场景）

适合有实体 POS 需求的场景，可与 QR 点餐共用同一个终端。

**推荐指数 / Rating:** ⭐⭐⭐⭐

#### 推荐方案 C：Changi Pay / CCInfo（本地化）

适合希望服务中国游客为主打的门店。

**推荐指数 / Rating:** ⭐⭐⭐

### 4.3 PayNow 特别集成说明 / PayNow Integration

PayNow 是新加坡特有的大型实时支付系统，覆盖率超过 90%，是必须支持的支付方式。

**集成方式：** Stripe + PayNow（通过 Stripe Payment Request Button）或独立 PayNow QR（通过 DBS/OCBC/UOB 商业 QR API）。

**PayNow QR 码生成：**
- 使用新加坡银行提供的企业 QR 码标准（SGQR）
- 支持 PayNow UEN 绑定，顾客扫码后跳转银行 App 完成支付
- 支付完成后 Webhook 回调确认，适用于点餐系统

### 4.4 支付流程 / Payment Flow

```
顾客选择商品 → 确认订单 → 选择支付方式 → 跳转支付网关 / 展示 QR 码
    ↓
[在线支付] Stripe 处理卡/钱包 → 支付成功 → Webhook 确认 → 更新订单状态
    ↓
[PayNow] 展示银行 QR → 顾客扫码支付 → 银行 Webhook 回调 → 更新订单状态
```

### 4.5 支付安全 / Payment Security

- 所有支付数据通过 TLS 1.3 加密传输
- 银行卡信息不经由商户服务器（Stripe Elements 前端化）
- 符合 PCI DSS Level 1 标准（使用 Stripe）
- 支付超时：15 分钟自动取消订单

---

## 5. 技术架构 / Technical Architecture

### 5.1 系统组件 / System Components

```
┌─────────────────────────────────────────────────────┐
│                  顾客端 / Customer UI               │
│            (H5 响应式 / Mobile-first)               │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────┐
│              API 网关 / API Gateway                  │
│         (Cloudflare Workers / Lambda)               │
└──────┬──────────────┬──────────────┬────────────────┘
       │              │              │
┌──────▼──────┐ ┌─────▼─────┐ ┌────▼─────┐
│  菜单服务   │ │  订单服务  │ │  支付服务 │
│ Menu Svc   │ │ Order Svc │ │Payment Svc│
└────────────┘ └───────────┘ └──────────┘
       │              │              │
┌──────▼──────────────▼──────────────▼──────────────┐
│              数据层 / Data Layer                     │
│   PostgreSQL (主库) + Redis (缓存) + S3 (图片)      │
└─────────────────────────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │   KDS / 后厨端   │
              │ Kitchen Display  │
              └──────────────────┘
```

### 5.2 技术栈 / Tech Stack

| 层级 / Layer | 技术选型 / Technology | 说明 / Notes |
|-------------|----------------------|-------------|
| 前端 / Frontend | Vue 3 + Vite / React | 移动端 H5，SSR optional |
| 后端 / Backend | Node.js (Fastify) / Python (FastAPI) | 推荐 FastAPI (Python) |
| 数据库 / Database | PostgreSQL 15 | 主数据存储 |
| 缓存 / Cache | Redis 7 | Session、实时状态 |
| 文件存储 / Storage | AWS S3 / Cloudflare R2 | 菜单图片 |
| CDN | Cloudflare | 静态资源加速 |
| 支付网关 / Payment | Stripe | 全功能支付 |
| SMS/推送 / Notifications | Twilio / OneSignal | 订单状态推送（轮询，MVP）|
| 日志 / Logging | Cloudflare Logpush / Datadog | 请求日志 |
| 监控 / Monitoring | UptimeRobot / Cloudflare Analytics | 可用性监控 |
| SSL 证书 | Let's Encrypt (auto-renew) | HTTPS |

### 5.3 域名与托管 / Domain & Hosting

| 项目 / Item | 值 / Value |
|------------|-----------|
| 主域名 / Primary domain | `order.clapcafe.sg` |
| 管理后台 / Admin panel | `admin.clapcafe.sg` |
| KDS 后厨端 / Kitchen display | `kds.clapcafe.sg` |
| 推荐托管 / Recommended hosting | Cloudflare Pages (前端) + Railway/Render (后端) |

### 5.4 数据模型 / Data Models

#### 菜单分类 / Category
```
Category {
  id: UUID
  name_zh: string        // "咖啡"
  name_en: string         // "Coffee"
  sort_order: integer     // 排序权重
  is_active: boolean
}
```

#### 商品 / Item
```
Item {
  id: UUID
  category_id: UUID
  name_zh: string
  name_en: string
  description_zh: string
  description_en: string
  price_sgd: decimal(10,2)
  image_url: string
  options: JSON           // 规格选项配置
  is_available: boolean
  stock: integer          // 库存（可选）
}
```

#### 座位 / Seat
```
Seat {
  id: string              // "T01", "BAR01"
  label_zh: string        // "3号桌"
  label_en: string        // "Table 03"
  zone: string            // "indoor", "outdoor", "bar"
  is_active: boolean
}
```

#### 订单 / Order
```
Order {
  id: string              // "CC-20260514-001"
  seat_id: string
  status: enum            // submitted/confirmed/preparing/ready/completed/cancelled
  items: JSON             // 订单明细
  subtotal: decimal
  tax_sgd: decimal(9%)
  total_sgd: decimal
  payment_method: string
  payment_status: enum    // pending/paid/failed/refunded
  payment_intent_id: string // Stripe payment intent ID
  notes: string           // 顾客备注
  created_at: timestamp
  updated_at: timestamp
}
```

---

## 6. 用户流程 / User Flow

### 6.1 扫码点餐流程 / Scan & Order Flow

```
顾客入座 → 扫描桌面 QR 码 → 打开点餐页面（自动带座位号）
    ↓
[语言选择] 首次访问选择中文/English，后续自动记忆
    ↓
[浏览菜单] 分类查看商品 → 点击查看详情 → 选择规格
    ↓
[加入购物车] 重复添加 → 购物车图标显示数量
    ↓
[确认订单] 检查商品/数量/座位号 → 填写备注
    ↓
[选择支付] 选择支付方式（见第4节）
    ↓
[完成支付] Stripe 跳转 / PayNow 扫码
    ↓
[订单确认] 显示订单号 + 预计等待时间
    ↓
[等待通知] 订单状态实时推送（制作中 → 已完成）
    ↓
[取餐] 凭订单号至柜台取餐（座位号已同步后厨）
```

### 6.2 后厨处理流程 / Kitchen Flow

```
新订单到达 KDS → 语音/视觉提醒
    ↓
后厨点击"接单" → 订单状态 → 制作中
    ↓
完成制作 → 点击"完成" → 订单状态 → 已完成
    ↓
顾客端收到推送通知 → "您的订单已完成，请取餐"
```

---

## 7. 座位管理 / Seat Management

### 7.1 座位布局 / Seat Layout

| 区域 / Zone | 座位数 / Count | 座位编号 / Seat IDs |
|------------|--------------|-------------------|
| 室内 / Indoor | 12 | T01–T12 |
| 室外 / Outdoor | 4 | O01–O04 |
| 吧台 / Bar | 6 | B01–B06 |
| 合计 / Total | 22 | — |

### 7.2 座位状态 / Seat Status

| 状态 / Status | 颜色标识 / Color | 说明 / Description |
|-------------|----------------|-------------------|
| 空置 / Vacant | 绿色 / Green | 可用 |
| 已开台 / Occupied | 橙色 / Orange | 有活跃订单 |
| 已预约 / Reserved | 蓝色 / Blue | 已预约，待客人入座 |
| 停用 / Inactive | 灰色 / Grey | 维修/不可用 |

### 7.3 座位管理 API / Seat Management API

| 端点 / Endpoint | 方法 / Method | 说明 / Description |
|---------------|--------------|-------------------|
| `GET /seats` | GET | 获取所有座位列表及状态 |
| `GET /seats/{id}` | GET | 获取指定座位详情 |
| `PUT /seats/{id}/status` | PUT | 更新座位状态 |
| `POST /seats/{id}/assign` | POST | 绑定座位（开台） |

---

## 8. 订单管理 / Order Management

### 8.1 订单状态流转 / Order State Machine

```
┌──────────┐    提交    ┌──────────┐   确认    ┌───────────┐  完成   ┌────────┐
│ SUBMITTED│ ──────── → │CONFIRMED │ ───────→ │PREPARING │ ────→ │  READY │
└──────────┘            └──────────┘           └───────────┘        └────────┘
     │                       │                     │                   │
     │ [缺货/超时取消]        │ [拒单]               │ [取消]             │ [取餐]
     ▼                      ▼                     ▼                   ▼
┌──────────┐          ┌──────────┐           ┌──────────┐        ┌──────────┐
│ CANCELLED│          │REJECTED  │           │ CANCELLED│        │COMPLETED │
└──────────┘          └──────────┘           └──────────┘        └──────────┘
```

### 8.2 订单时效规则 / Order Timeout Rules

| 场景 / Scenario | 超时时间 / Timeout | 自动操作 / Auto Action |
|---------------|-------------------|----------------------|
| 订单提交未支付 / Unpaid after submission | 15 分钟 / 15 min | 自动取消，释放座位 |
| 支付中卡单 / Payment stuck | 5 分钟 / 5 min | 自动重试（最多2次）|
| 订单完成未取 / Ready but not collected | 30 分钟 / 30 min | 推送提醒 |

### 8.3 退款政策 / Refund Policy

- 未确认订单：全额自动退款（超时取消）
- 制作中取消：人工确认后退款（WhatsApp 通知店员）
- 已完成订单：不支持退款（当面处理）

---

## 9. 安装部署 / Installation Guide

### 9.1 前期准备 / Prerequisites

| 项目 / Item | 要求 / Requirement |
|------------|------------------|
| 域名 / Domain | `order.clapcafe.sg`（需自行注册或转移） |
| 商业注册 / Business registration | 新加坡 ACRA 注册（UEN）|
| Stripe 商业账户 / Stripe business account | stripe.com/sg |
| PayNow 企业账号 / PayNow corporate | 联系开户银行开通 |
| QR 码打印机 / QR printer | 推荐 Dymo Label Printer 或 Epson |
| 小票打印机 / Receipt printer | ESC/POS 协议（推荐 Epson TM-M30II）|

### 9.2 QR 码生成步骤 / QR Code Generation Steps

**步骤 1：准备座位清单**
```python
# 使用 Python qrcode 库批量生成
import qrcode

seats = [f"T{i:02d}" for i in range(1, 13)]  # T01-T12
seats += [f"O{i:02d}" for i in range(1, 5)]   # O01-O04
seats += [f"B{i:02d}" for i in range(1, 7)]    # B01-B06

for seat_id in seats:
    url = f"https://order.clapcafe.sg/?seat={seat_id}&lang=zh"
    qr = qrcode.make(url)
    qr.save(f"qr_codes/{seat_id}_zh.png")

    qr_en = qrcode.make(f"https://order.clapcafe.sg/?seat={seat_id}&lang=en")
    qr_en.save(f"qr_codes/{seat_id}_en.png")

    # 打印贴纸时显示编号即为座位号（如 T01），无需额外前缀
```

**步骤 2：打印并覆膜**
- 尺寸：5cm × 5cm（300 DPI）
- 覆膜：防水防油污，延长使用寿命
- 建议附带座位号标签（CC-T01 格式）

### 9.3 支付网关申请 / Payment Gateway Setup

#### Stripe 申请流程
1. 访问 stripe.com/sg → 注册企业账户
2. 提交新加坡 UEN、董事身份证
3. 完成 KYC（通常 1-3 个工作日）
4. 获取 API Keys（Publishable Key + Secret Key）
5. 配置 Webhook URL：`https://order.clapcafe.sg/api/webhooks/stripe`

#### PayNow 申请流程
1. 联系开户银行（推荐 UOB / OCBC，企业服务热线）
2. 申请企业 PayNow QR（SGQR 标准）
3. 获取 UEN 绑定 QR 码
4. 集成方式：独立 API 或通过 Stripe Payment Request Button

### 9.4 部署清单 / Deployment Checklist

| 序号 / # | 任务 / Task | 状态 / Status |
|---------|------------|-------------|
| 1 | 注册域名 `order.clapcafe.sg` | ☐ |
| 2 | 申请 Stripe 企业账户 | ☐ |
| 3 | 申请 PayNow 企业 QR | ☐ |
| 4 | 部署后端服务（Railway/Render）| ☐ |
| 5 | 部署前端（Cloudflare Pages）| ☐ |
| 6 | 配置 SSL 证书 | ☐ |
| 7 | 配置 Stripe Webhook | ☐ |
| 8 | 导入菜单数据（双语）| ☐ |
| 9 | 生成并打印所有 QR 码 | ☐ |
| 10 | 部署 KDS 后厨端 | ☐ |
| 11 | 配置小票打印机 | ☐ |
| 12 | 员工培训（1小时操作培训）| ☐ |
| 13 | 内测验收（员工模拟点餐）| ☐ |
| 14 | 正式上线 | ☐ |

### 9.5 预算估算 / Budget Estimate

| 项目 / Item | 一次性费用 / One-time | 月费 / Monthly | 备注 / Notes |
|------------|---------------------|----------------|-------------|
| 域名 / Domain | S$20/年 | — | .sg 域名 |
| Stripe 手续费 | — | 按交易量 | ~3.4% + S$0.50 |
| 托管（前端）| S$0 | S$0 | Cloudflare Pages 免费版 |
| 托管（后端）| — | S$20-50 | Railway/Render |
| 数据库 | — | S$15-30 | Supabase / Railway Postgres |
| QR 码打印（22张）| S$20-50 | — | 覆膜纸 |
| 小票打印机 | S$200-400 | — | Epson TM-M30II |
| 技术开发（外包）| S$3,000-8,000 | — | 若不自研 |

---

## 附录 A：QR 码样本 / Appendix A: QR Code Samples

```
┌─────────────────────────────────┐
│                                 │
│   [QR Code - T01]              │
│   尺寸: 5cm × 5cm               │
│   内容: order.clapcafe.sg       │
│         ?seat=T01&lang=zh       │
│                                 │
├─────────────────────────────────┤
│  🪑 1号桌 / Table 01            │
│  📱 扫码点餐 / Scan to order     │
│                                 │
│  CLAP CAFE SINGAPORE            │
│  ☕ Specialty Coffee & More     │
└─────────────────────────────────┘
```

---

## 附录 B：支持支付方式汇总 / Appendix B: Payment Methods Summary

| 类型 / Type | 方式 / Method | 覆盖人群 / Coverage |
|------------|--------------|-------------------|
| 信用卡 / Credit | Visa, Mastercard, Amex | 全球游客 |
| 电子钱包 / E-wallet | GrabPay | 新加坡居民（主流）|
| 银行转账 / Bank Transfer | PayNow (9家银行) | 新加坡居民（全覆盖）|
| 先买后付 / BNPL | Atome | 年轻消费者 |
| 跨境支付 / Cross-border | 微信支付, Alipay+ | 中国游客 |
| 电信钱包 / Telco | Singtel Dash | 本地用户 |

---

*文档生成时间 / Generated: 2026-05-14*
*下次审查时间 / Next Review: 2026-08-14（每季度审查一次）*

---

**© Clap Cafe Singapore — Internal Document**
**项目路径 / Project Path:** `~/Documents/clap-cafe-qr-order/`
