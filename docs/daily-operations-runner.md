# 每日主动工作编排器

## 开发目标

本模块不是新增页面，也不是新增聊天能力。

它的目标是让 AI 每天主动完成一轮电商运营工作，并把结果写入 Workflow 日志、Savings Engine 和 CEO 老板日报。

## 替代岗位

优先替代：直播运营助理。

当前覆盖工作：

1. 开播前检查：商品、库存、优惠券、价格、脚本、赠品和商品排序。
2. 直播中扫描：在线人数、成交率、停留率、评论、点赞、商品点击率、库存变化、异常订单。
3. 下播后复盘：成交、退款、评论、主播表现和第二天建议。

## 节省时间

- 无真实数据时：执行安全基线巡检，预计节省 10-20 分钟整理时间。
- 有真实商家数据时：执行完整三段 Workflow，预计节省 20-40 分钟运营检查和复盘时间。
- 按每月 26 个工作日计算，预计节省 10-20 小时/月。

## 老板为什么愿意付钱

老板不需要看聊天记录，也不需要自己翻表。

系统每天直接告诉老板：

- AI 做了几项工作。
- 发现了哪些直播风险。
- 哪些动作需要老板审批。
- 今天节省了多少分钟。
- 今天折合节省了多少钱。
- 这些数字来自哪些 Workflow 运行记录。

## API

`POST /v1/daily-operations/run`

适用触发方式：

- `manual`：商家控制台手动点一次。
- `scheduled`：服务器定时任务每天自动执行。
- `webhook`：平台数据到达后自动触发。

## 数据模式

### safe_baseline

请求里不传真实店铺数据时，系统会跑安全基线巡检。

这个模式可以证明系统流程可用，但不能当成真实店铺结论。

### merchant_payload

请求里传入直播商品、直播中数据、下播复盘数据时，系统会按商家真实字段执行 Workflow。

这个模式的结果可以进入老板日报、Savings Engine、Replay 和 Evaluation。

## 下一步

1. 把 `POST /v1/daily-operations/run` 接到商家控制台的一键今日工作按钮。
2. 生产部署后用平台定时任务或 Railway Cron 每天自动调用。
3. 接入抖店、淘宝直播真实数据后，把触发来源改成 `scheduled` 或 `webhook`。
4. 将 Workflow 日志切到 Supabase `live_workflow_runs` 表，形成可审计证据。

## 定时任务运行方式

本地验证：

```bash
npm run api:daily-operations
```

生产环境建议直接运行 Python 模块：

```bash
python -m apps.api.app.infrastructure.daily_operations_job
```

可接入的位置：

1. Railway Cron：每天早上 8:00 执行一次。
2. Render Cron Job：每天早上 8:00 执行一次。
3. Linux crontab：每天早上 8:00 执行一次。
4. Windows 任务计划程序：每天早上 8:00 执行一次。

## 生产安全要求

如果要让老板日报和 Savings Engine 使用真实可追踪证据，生产环境必须设置：

```bash
LIVE_WORKFLOW_LOG_STORAGE=postgres
APPROVAL_RECORD_STORAGE=postgres
AFTER_SALE_DECISION_STORAGE=postgres
CEO_REPORT_SNAPSHOT_STORAGE=postgres
DATABASE_URL=真实 Supabase PostgreSQL 连接串
```

并先执行：

```text
supabase/migrations/202607150001_live_workflow_runs.sql
supabase/migrations/202607160001_approval_records.sql
supabase/migrations/202607170001_after_sale_decision_outcomes.sql
supabase/migrations/202607180001_ceo_daily_report_snapshots.sql
```

如果设置了 `LIVE_WORKFLOW_LOG_STORAGE=postgres
APPROVAL_RECORD_STORAGE=postgres
AFTER_SALE_DECISION_STORAGE=postgres
CEO_REPORT_SNAPSHOT_STORAGE=postgres` 但数据库不可用，定时任务会返回 `blocked`，不会假装已经完成工作。

## 当前边界

本地 memory 模式默认执行安全基线巡检，便于开发和演示。

生产 Postgres 模式会从 `products`、`orders` 和 `after_sale_cases` 读取商家数据，通过 `daily_operations_data_provider.py` 生成开播前检查和下播复盘输入；如果数据为空或读取失败，任务会 `blocked`，不会写入 safe baseline。

接入抖店、淘宝直播后，还需要把优惠券、直播中在线人数、成交率、停留率、评论、点赞、点击率和异常订单同步进 `live_metrics`，再由 `scheduled` 或 `webhook` 触发。

## 云端 Cron 配置

项目已新增 Render Cron 配置：

```yaml
- type: cron
  name: ai-commerce-os-daily-operations
  schedule: "0 0 * * *"
  dockerCommand: "python -m apps.api.app.infrastructure.daily_operations_job"
```

`0 0 * * *` 表示每天 UTC 0 点执行，对应北京时间早上 8 点。

如果使用 Docker Compose，可以手动运行一次：

```bash
docker compose -f docker-compose.production.yml --profile jobs run --rm daily-operations
```

## 跨平台脚本

本地和服务器统一使用：

```bash
npm run api:daily-operations
```

该命令会通过 `tools/run-api-module.cjs` 自动寻找当前系统可用的 Python：

- Windows：优先使用 `.venv/Scripts/python.exe`。
- Linux / macOS：优先使用 `.venv/bin/python`，然后尝试 `python3` 和 `python`。

这样同一个命令可以在本机、Linux 服务器和 CI 环境中使用。
