# Clap Cafe 扫码点餐系统 — 行动清单
# Clap Cafe QR Ordering System — Action Items

**文档版本 / Version:** v1.0
**编制日期 / Created:** 2026-05-16
**基于 / Based on:** QR-Ordering-System.md v1.1, ENGINEERING.md v1.1

---

## 符号说明 / Legend

| 符号 | 含义 |
|------|------|
| 🔴 | Critical — 影响核心流程 |
| 🟡 | Medium — 运营效率 |
| ⚪ | Low — 体验增强 |

---

## 一、v1 遗留问题 / v1遗留 / v1 Carry-over

### A. 管理员订单管理 / Admin Order Management
**owner:** backend + admin
**priority:** 🔴

- [ ] 创建 `POST/PATCH/DELETE /v1/admin/orders` 端点
- [ ] 创建 Admin OrderListView — 支持按状态筛选（submitted/confirmed/preparing/ready/completed/cancelled）
- [ ] Admin OrderDetailView — 查看订单明细和操作历史
- [ ] Admin 可手动取消订单（条件：仅 submitted 状态）
- [ ] Admin 可修改订单备注（customer_notes）

### B. 健康检查端点 / Health Check Endpoint
**owner:** backend
**priority:** 🟡

- [ ] 实现 `GET /health/ready` 真实检查 — DB 连接 + Redis 连接
- [ ] 任意一项失败返回 503，含 `{"checks": {"database": "ok"|"fail", "redis": "ok"|"fail"}}`

---

## 二、v1.5 运营增强 / Operational Enhancements

### C. KDS 多语言支持 / KDS Bilingual Support
**owner:** kds
**priority:** 🟡

- [ ] KDS 语言切换组件（中/英，供外籍员工使用）
- [ ] 所有 KDS 静态文本（按钮/标签/提示）支持 zh/en
- [ ] KDS 路由守卫：`/?lang=en` 或 `/?lang=zh`

### D. 商品库存预警 / Stock Alert
**owner:** backend + admin
**priority:** 🟡

- [ ] `items` 表加 `low_stock_threshold` 字段（默认 5）
- [ ] Admin MenuManagerView 显示库存警告图标（低于阈值）
- [ ] Admin 可设置每件商品的低库存阈值
- [ ] 管理员首页 Dashboard 显示"库存不足"商品列表

### E. 订单超时分级提醒 / Graded Order Timeout Alerts
**owner:** kds
**priority:** 🟡

- [ ] KDS 订单卡片：下单超过 5 分钟显示黄色警告边框
- [ ] KDS 订单卡片：下单超过 10 分钟显示红色警告 + 声音升级
- [ ] 配置化：`VITE_ORDER_WARNING_MINUTES=5`, `VITE_ORDER_URGENT_MINUTES=10`

### F. Admin 操作日志 / Admin Audit Log
**owner:** backend + admin
**priority:** 🟡

- [ ] 新建 `admin_audit_logs` 表：`id, admin_user_id, action, target_type, target_id, old_value, new_value, created_at`
- [ ] Admin 中间件：每次写操作（创建/更新/删除 menu/seat/item）记录一条日志
- [ ] Admin Dashboard 新增"最近操作"面板

### G. 批量商品上下架 / Bulk Item Availability
**owner:** backend + admin
**priority:** ⚪

- [ ] Admin MenuManagerView 支持多选商品（checkbox）
- [ ] 批量设置"上架"/"下架"
- [ ] 批量删除（仅 is_active=False）
- [ ] 批量分类移动

### H. 顾客端历史订单分页 / Order History Pagination
**owner:** frontend
**priority:** 🟡

- [ ] `GET /v1/orders` 添加分页参数 `?page=1&limit=20`
- [ ] 前端 OrderHistoryView 下拉加载更多（infinite scroll）
- [ ] 响应加 `total_count` 和 `total_pages`

---

## 三、v2 优先功能 / v2 Priority Features

### I. 微信/支付宝集成 / WeChat & Alipay
**owner:** backend + frontend
**priority:** 🟡

- [ ] 研究 Stripe 已支持的 WeChat Pay / Alipay（Stripe Singapore）
- [ ] 后端添加 `wechat_pay` / `alipay` payment_method_types
- [ ] 前端支付页添加对应图标和说明

### J. 积分/会员系统 / Loyalty & Membership
**owner:** backend + frontend + admin
**priority:** ⚪

- [ ] 新建 `customers` 表（手机号/微信 unionid，积分余额）
- [ ] 首次下单自动创建会员（手机号或扫码授权）
- [ ] Admin 新增"会员管理"页面（查询积分、增减积分）
- [ ] 前端订单确认页显示"本次获得 X 积分"

### K. 销售数据看板 / Admin Analytics Dashboard
**owner:** backend + admin
**priority:** ⚪

- [ ] `GET /v1/admin/analytics/orders` — 日/周/月订单量+销售额
- [ ] `GET /v1/admin/analytics/popular-items` — 热销商品 Top 10
- [ ] Admin Dashboard 新增图表（可使用 Chart.js 或简单表格）
- [ ] Admin 导出 CSV 功能（日结报表）

### L. 每日推荐菜品 / Daily Specials
**owner:** backend + frontend + admin
**priority:** ⚪

- [ ] `items` 表加 `is_daily_special` BOOLEAN
- [ ] Admin MenuManager 可标记"今日推荐"
- [ ] `GET /v1/menu` 响应中每日推荐菜品排在最前
- [ ] 前端 MenuView 顶部 Banner 展示今日推荐

### M. 座位预约功能 / Seat Reservation
**owner:** backend + frontend + admin
**priority:** ⚪

- [ ] 新建 `reservations` 表
- [ ] Admin 新增"预约管理"页面（审核/确认/取消预约）
- [ ] 预约顾客扫码后显示预约信息确认页
- [ ] 与座位状态联动（预约确认后 seat.status = 'reserved'）

### N. 后厨叫号广播 / Kitchen Call-out Broadcast
**owner:** kds
**priority:** ⚪

- [ ] KDS "完成"按钮支持"叫号"操作（不只是状态更新）
- [ ] 通过 TTS（Web Speech API）朗读："T01 号，请取餐"
- [ ] 管理员可配置是否开启语音播报

---

## 四、工程改进 / Engineering Improvements

### O. 测试覆盖 / Test Coverage
**owner:** backend + frontend
**priority:** 🟡

- [ ] 后端：pytest-asyncio 集成测试（order create flow, webhook idempotency, timeout worker）
- [ ] 前端：Vitest 单元测试（cart deduplication, GST 计算, usePolling）
- [ ] E2E：Playwright 基础用例（扫码→点餐→支付→KDS 接单）
- [ ] CI 添加 `mypy backend/app/` + `vue-tsc --noEmit` 前端类型检查

### P. pre-commit Hooks
**owner:** infra
**priority:** 🟡

- [ ] 安装 `.pre-commit-config.yaml`（ruff, eslint, mypy, vue-tsc）
- [ ] GitHub Actions CI 中运行静态检查

### Q. 日志与监控完善 / Logging & Monitoring
**owner:** backend
**priority:** ⚪

- [ ] 统一 JSON 日志格式（timestamp, level, order_id, seat_id）
- [ ] 关键日志点：订单创建/状态变更/支付回调/超时取消
- [ ] Railway 日志导出到外部（可选：Datadog/Logtail）

### R. 离线支持 / PWA Offline Support
**owner:** frontend
**priority:** ⚪

- [ ] 前端添加 `vite-plugin-pwa`
- [ ] Service Worker 缓存菜单数据（刷新间隔 5 分钟）
- [ ] 离线时提示"当前离线，菜单仅供参考"

---

## 任务汇总 / Summary

| ID | 任务 | Owner | Priority | Est. |
|----|------|-------|----------|------|
| A | Admin 订单管理 | backend+admin | 🔴 | 4h |
| B | Health/ready 真实检查 | backend | 🟡 | 1h |
| C | KDS 多语言 | kds | 🟡 | 2h |
| D | 库存预警 | backend+admin | 🟡 | 3h |
| E | 超时分级提醒 | kds | 🟡 | 2h |
| F | Admin 操作日志 | backend+admin | 🟡 | 3h |
| G | 批量商品上下架 | backend+admin | ⚪ | 2h |
| H | 历史订单分页 | frontend | 🟡 | 2h |
| I | 微信/支付宝 | backend+frontend | ⚪ | 4h |
| J | 会员积分系统 | backend+frontend+admin | ⚪ | 8h |
| K | 数据看板 | backend+admin | ⚪ | 4h |
| L | 每日推荐 | backend+frontend+admin | ⚪ | 3h |
| M | 座位预约 | backend+frontend+admin | ⚪ | 6h |
| N | 后厨叫号 | kds | ⚪ | 2h |
| O | 测试覆盖 | backend+frontend | 🟡 | 6h |
| P | pre-commit hooks | infra | 🟡 | 1h |
| Q | 日志监控 | backend | ⚪ | 2h |
| R | PWA 离线 | frontend | ⚪ | 3h |

---

## 并行策略 / Parallelization

| 组 | 任务 | 可并行 |
|----|------|--------|
| 1 | A（Admin 订单） | B（health） |
| 2 | C（KDS 多语言） | E（超时提醒） |
| 3 | D（库存预警） | F（操作日志） |
| 4 | O（测试）+ P（pre-commit） | — |
| 5 | G（批量上下架） | H（分页） |

---

*本文档随产品迭代持续更新*
