# CEO 日报 API

## 目标

CEO 日报不是聊天总结，也不是传统数据看板。它的目标是让老板每天第一眼知道：

1. 今天经营状态怎么样。
2. 哪里有风险。
3. 先处理什么。
4. AI 今天替代了多少人工。
5. AI 今天节省了多少钱。

## 替代岗位

老板 / 运营主管每天整理日报和判断优先级的工作。

## 节省时间

每天预计节省 20 到 40 分钟；按每月 26 个工作日计算，每月节省约 9 到 17 小时。

## 老板为什么愿意付钱

老板不想看十几个后台，也不想自己分析订单、退款、库存、直播和客服。老板需要的是一句话结论、风险原因、动作建议和省钱证据。

## API

`GET /v1/ceo/daily-report`

返回内容包括：

- `headline`：今天一句话结论。
- `business_health_score`：经营健康分。
- `boss_message`：老板该先看什么。
- `saved_money_today_yuan`：今日 AI 节省金额。
- `projected_monthly_saving_yuan`：预计月节省。
- `annual_roi_percent`：年度 ROI。
- `live_operation_status`：直播运营状态。
- `top_risks`：最高风险。
- `priority_actions`：今日优先动作。
- `ai_employee_notes`：AI 员工绩效说明。
- `proof_points`：证据点，说明节省金额和 Workflow 运行记录。

## 当前边界

当前日报使用现有直播运营、Savings Engine、售后决策和仓库通知证据。生产环境需要先执行证据链 migrations，并让日报快照与 Workflow 日志使用 PostgreSQL 仓储。

## 下一步

把 `/dashboard` 首屏接入 CEO 日报 API，让老板打开系统先看到结论，而不是先看复杂页面。
## Dashboard 已接入

当前 `/dashboard` 已经读取 `GET /v1/ceo/daily-report`，并把 CEO 日报放在老板首页第一屏。

首页第一屏现在优先展示：

- 今天一句话结论。
- 今日 AI 节省金额。
- 预计月节省。
- 经营健康分。
- 最高风险。
- 今日优先动作。
- Savings Engine 与 Workflow 证据点。

下一步不是继续改页面，而是把直播 Workflow 日志落到 Supabase，让首页展示的节省金额拥有长期证据链。

## 数据可信状态

CEO 日报现在包含数据可信状态：

- `data_status = demo_estimate`：当前没有真实 Workflow 运行记录，页面用于试用演示和接入前校准。
- `data_status = real_workflow_logs`：已读取直播 Workflow 运行记录，节省金额来自实际执行日志。

Dashboard 首屏会显示状态徽标和解释，避免商家误解数据来源。
