## 当前下一步：连接直播实时指标并在线验证证据链

优先级：P0。

本轮已完成：
- 生产 Postgres 定时任务会读取 `products`、`orders`、`after_sale_cases`，生成数据库来源的 `merchant_payload`。
- 数据为空或读取失败时任务返回 `blocked`，不会把 `safe_baseline` 写为生产 Workflow、Savings 或 CEO 证据。
- 全量后端测试：`87 passed`。

仍需外部生产动作：
1. 在线执行四份 evidence-chain migration，并启用四个 PostgreSQL storage 配置。
2. 导入真实商品、订单和售后数据，运行 `npm run api:daily-operations`，确认 `input_mode=merchant_payload`。
3. 配置真实 WMS/ERP endpoint、API key，并验证补发通知的外部回执。
4. 接入抖店/淘宝直播实时优惠券和直播中指标，补齐 `live_metrics`。
5. 访问 `/health/ready`，确认 `evidence_chain_ready=true`，再验证 CEO 快照与 Savings 都读取持久化日志。

## 当前下一步：线上启用完整 AI Employee OS 证据链

优先级：P0。

本轮已完成：
- CEO 日报在每日主动工作完成后会保存 `ceo_daily_report_snapshots` 快照。
- 本轮最终全量后端测试：`87 passed`。

仍需外部生产动作：
1. 在线执行 `202607150001_live_workflow_runs.sql`、`202607160001_approval_records.sql`、`202607170001_after_sale_decision_outcomes.sql`、`202607180001_ceo_daily_report_snapshots.sql`。
2. 配置 `LIVE_WORKFLOW_LOG_STORAGE=postgres`、`APPROVAL_RECORD_STORAGE=postgres`、`AFTER_SALE_DECISION_STORAGE=postgres`、`CEO_REPORT_SNAPSHOT_STORAGE=postgres`。
3. 配置真实 WMS/ERP URL、API key 和抖店/淘宝直播数据源。
4. 运行 `/health/ready`，确认 `evidence_chain_ready=true`，再运行 `npm run api:daily-operations`。
5. 保持不新增客服聊天、Prompt、知识库或无关 Dashboard，只推进真实 Workflow、Savings 和 CEO 证据。
## 当前下一步：让线上定时任务通过 evidence_chain_ready 后写入真实日志

优先级：P0。

刚完成：
- 生产定时任务已加入 evidence chain guard。
- `LIVE_WORKFLOW_LOG_STORAGE=postgres` 时，如果证据链未 ready，任务会 blocked，不会写入假生产日志。
- 当前战略审计：总分 77，真实数据证据链 50，Agent 协同 90。
- 当前核心测试：57 passed。

继续推进：
1. 在线执行 `202607150001_live_workflow_runs.sql`、`202607160001_approval_records.sql`、`202607170001_after_sale_decision_outcomes.sql`。
2. 生产环境设置 `LIVE_WORKFLOW_LOG_STORAGE=postgres`、`APPROVAL_RECORD_STORAGE=postgres`、`AFTER_SALE_DECISION_STORAGE=postgres`。
3. 生产环境设置 `WAREHOUSE_NOTIFICATION_DELIVERY_MODE=http_api`、真实 `WAREHOUSE_NOTIFICATION_WMS_API_URL`、真实 `WAREHOUSE_NOTIFICATION_WMS_API_KEY`。
4. 跑 `/health/ready`，确认 `evidence_chain_ready=true`。
5. 跑 `npm run api:daily-operations`，确认定时任务写入真实 `live_workflow_runs`，不是 memory 或 safe-only 估算。
6. 接入真实抖店/淘宝直播数据，让每日主动工作从 safe_baseline 变成 merchant_payload。
7. 继续保持原则：不新增页面、不新增客服聊天、不新增 Agent，只补 workflow 证据链和节省金额计算。
## 当前下一步：执行线上 migrations 并让 evidence_chain_ready=true

优先级：P0。

刚完成：
- `/health/ready` 和 `npm run api:bootstrap` 已能检查真实证据链 readiness。
- 未启用 Postgres 仓储、缺少证据链表、缺少 WMS/ERP URL/key 时会明确 blocked。
- 当前战略审计：总分 76，真实数据证据链 48，Agent 协同 90。
- 当前核心测试：56 passed。

继续推进：
1. 在线执行 `202607150001_live_workflow_runs.sql`、`202607160001_approval_records.sql`、`202607170001_after_sale_decision_outcomes.sql`。
2. 生产环境设置 `LIVE_WORKFLOW_LOG_STORAGE=postgres`、`APPROVAL_RECORD_STORAGE=postgres`、`AFTER_SALE_DECISION_STORAGE=postgres`。
3. 生产环境设置 `WAREHOUSE_NOTIFICATION_DELIVERY_MODE=http_api`。
4. 配置真实 `WAREHOUSE_NOTIFICATION_WMS_API_URL` 和 `WAREHOUSE_NOTIFICATION_WMS_API_KEY`。
5. 跑 `/health/ready` 和 `npm run api:bootstrap`，直到 `evidence_chain_ready=true`。
6. 继续保持原则：不新增页面、不新增客服聊天、不新增 Agent，只补 workflow 证据链和节省金额计算。
## 当前下一步：生产启用 Postgres 证据链 + 配置真实 WMS/ERP 凭证

优先级：P0。

刚完成：
- 仓库通知已支持 `export_queue` 和 `http_api` 两种 sender。
- `http_api` sender 可 POST 到真实 WMS/ERP endpoint，并解析外部单号。
- WMS/ERP 失败会进入 failed 状态，并出现在 CEO 日报风险和老板待办里。
- 当前核心测试：38 passed。

继续推进：
1. 在线执行 `202607150001_live_workflow_runs.sql`、`202607160001_approval_records.sql`、`202607170001_after_sale_decision_outcomes.sql`。
2. 生产环境设置 `LIVE_WORKFLOW_LOG_STORAGE=postgres`、`APPROVAL_RECORD_STORAGE=postgres`、`AFTER_SALE_DECISION_STORAGE=postgres`。
3. 生产环境设置 `WAREHOUSE_NOTIFICATION_DELIVERY_MODE=http_api`。
4. 配置真实 `WAREHOUSE_NOTIFICATION_WMS_API_URL` 和 `WAREHOUSE_NOTIFICATION_WMS_API_KEY`。
5. 增加真实 WMS/ERP 回执样例测试，确认 external_reference 字段与商家系统一致。
6. CEO 日报继续把 failed 仓库通知作为老板异常事项，直到 sent 或 cancelled。
7. 继续保持原则：不新增页面、不新增客服聊天、不新增 Agent，只补 workflow 证据链和节省金额计算。
## 当前下一步：替换 export queue 为真实 WMS/ERP API

优先级：P0。

刚完成：
- 仓库通知已支持 queued / sent / failed / cancelled 状态流转。
- `POST /v1/warehouse-notifications/dispatch` 可派发待处理仓库通知。
- CEO 日报已展示仓库通知 sent / queued / failed 状态。
- WMS/ERP 发送失败会进入 failed 状态，不会丢失。
- 当前核心测试：34 passed。

继续推进：
1. 在线执行 `202607150001_live_workflow_runs.sql`、`202607160001_approval_records.sql`、`202607170001_after_sale_decision_outcomes.sql`。
2. 生产环境设置 `LIVE_WORKFLOW_LOG_STORAGE=postgres`、`APPROVAL_RECORD_STORAGE=postgres`、`AFTER_SALE_DECISION_STORAGE=postgres`。
3. 把当前 `export_queue` sender 替换为真实 WMS/ERP webhook/API sender。
4. 为真实 sender 增加签名、重试、超时、失败原因和外部单号回写。
5. CEO 日报把 failed 仓库通知列为老板异常事项，并提示是否人工跟进。
6. 继续保持原则：不新增页面、不新增客服聊天、不新增 Agent，只补 workflow 证据链和节省金额计算。
## 当前下一步：真实 WMS/ERP 仓库通知发送 + 生产证据链启用

优先级：P0。

刚完成：
- 售后决策结果已具备 memory/PostgreSQL 仓储边界。
- 仓库通知已具备 warehouse_notification_id 和 warehouse_notifications 持久化表。
- Savings Engine 已读取售后决策结果。
- CEO 日报已展示售后成本、仓库通知数量和最新仓库通知证据。
- 当前核心测试：33 passed。

继续推进：
1. 在线执行 `202607150001_live_workflow_runs.sql`、`202607160001_approval_records.sql`、`202607170001_after_sale_decision_outcomes.sql`。
2. 生产环境设置 `LIVE_WORKFLOW_LOG_STORAGE=postgres`、`APPROVAL_RECORD_STORAGE=postgres`、`AFTER_SALE_DECISION_STORAGE=postgres`。
3. 为 `warehouse_notifications` 增加真实发送状态流转：queued / sent / failed / cancelled。
4. 接入真实 WMS/ERP/仓库 API 或导出队列，把补发/换货通知从“生成记录”推进到“真实送达”。
5. CEO 日报读取仓库通知发送状态，把失败通知作为老板异常事项。
6. 继续保持原则：不新增页面、不新增客服聊天、不新增 Agent，优先补 workflow 证据链和节省金额计算。
## 当前下一步：售后决策结果持久化 + 真实仓库/ERP 通知

优先级：P0。

刚完成：
- 老板审批可通过 `POST /v1/approvals/{approval_id}/decision` 写回结果。
- 补发/换货审批会生成 `warehouse_notification_id`。
- 售后决策结果已进入 Savings Engine。

继续推进：
1. 新增售后决策结果 / 仓库通知持久化表。
2. 把 `after_sale_decision_workflow` 从内存结果升级为可切换 PostgreSQL 仓储。
3. 接入真实 WMS/ERP/仓库通知 API 或导出队列。
4. CEO 日报读取审批决策、售后成本和仓库通知证据点。
5. 保持原则：不新增页面、不新增 Agent、不做客服聊天，把 workflow 闭环补完整。
## 当前下一步：审批决策回写 + 仓库通知 Workflow

优先级：P0。

刚完成：
- 退款协同已支持 `order_external_id`。
- 有数据库时优先读取真实订单、物流、订单明细和库存证据。
- Workflow 响应会标明 `evidence_source=real_order_records`。

继续推进：
1. 增加审批通过/拒绝接口，把老板决策写回 `approval_records`。
2. 审批通过后生成售后成本记录、退款原因和客户最终回复。
3. 补发/换货场景生成仓库通知记录。
4. Savings Engine 和 CEO 日报读取审批决策、售后成本和仓库通知证据。
5. 保持原则：不新增页面、不新增 Agent、不做客服聊天，把 workflow 闭环补完整。
## 当前下一步：真实订单 / 库存 / 物流证据链

优先级：P0。

刚完成：
- 审批记录已经有内存/PostgreSQL 仓储边界。
- 已新增 `approval_records` migration。
- 高风险退款 workflow 生成的 `approval_id` 具备生产落库通道。

继续推进：
1. 在线执行 `202607160001_approval_records.sql`，生产设置 `APPROVAL_RECORD_STORAGE=postgres`。
2. 退款协同读取真实订单金额、发货状态、物流状态和库存状态，不再依赖手工入参。
3. 审批通过/拒绝后，写入售后成本、退款原因、客户回复和老板日报证据点。
4. Savings Engine 改为按真实退款协同记录和审批记录计算节省金额。
5. 保持原则：不新增页面、不新增 Agent、不做客服聊天，把 workflow 证据链补完整。
## 当前下一步：审批记录持久化 + 真实订单证据链

优先级：P0。

刚完成：
- 高风险退款协同现在会生成 `approval_id`。
- 老板待审批接口 `/v1/approvals/pending` 已经能读到退款 workflow 产生的审批记录。

继续推进：
1. 新增 `approval_records` 数据库表或复用现有审批表，把当前内存审批记录持久化。
2. 退款协同读取真实订单金额、发货状态、物流状态和库存状态，不再依赖手工入参。
3. 审批通过/拒绝后，回写售后成本、客户回复和 Savings/CEO 日报证据点。
4. 保持原则：不新增页面、不新增 Agent、不做客服聊天，把 workflow 证据链补完整。
# NEXT_TASK

更新时间：2026-07-14

## 当前唯一方向

产品战略已经升级为：

**AI Employee OS（企业 AI 数字员工操作系统）**

未来三个月不再继续堆 AI 客服页面、聊天功能、Prompt 页面或知识库页面。

当前 P0：

1. AI Live Operation Agent（直播运营助理）
2. CEO Agent 老板日报
3. Savings Engine 省钱引擎
4. ROI Engine 投入产出比

## 已完成的 V2 基础能力

- 已新增直播运营摘要接口：`GET /v1/live-operations/summary`
- 已新增省钱引擎摘要接口：`GET /v1/savings/summary`
- 已新增开播前检查 Workflow：`POST /v1/live-operations/pre-live-check`
- 已新增直播中扫描 Workflow：`POST /v1/live-operations/live-metric-scan`
- 已新增下播复盘 Workflow：`POST /v1/live-operations/post-live-review`
- 老板首页已经优先展示省钱金额、ROI、直播运营风险和 AI 员工绩效。

## 为什么先做直播运营助理

真实商家反馈里，当前最贵、最忙、最容易被流程化替代的岗位不是客服，而是直播运营助理。

直播运营助理每天要做：

- 开播前检查库存、优惠券、价格、脚本、商品排序、赠品和违禁词。
- 直播中盯在线人数、停留率、评论、商品点击率、库存、成交和异常订单。
- 下播后做成交复盘、商品分析、主播表现分析、评论分析、退款风险分析和第二天建议。

这些不是聊天，是工作流。

## 当前验收目标

老板打开首页以后，第一眼必须能看到：

- AI 今天替代了哪些岗位。
- AI 今天完成了多少工作。
- AI 今天节省了多少分钟。
- AI 今天节省了多少钱。
- 当前 ROI 是多少。
- 直播运营有什么风险。
- 哪些事情必须老板审批。

## 下一步

继续把直播运营助理从 V0 工作流推进到可接真实数据：

1. 建立直播 Workflow 日志，让每次检查、预警、复盘都有可追踪记录。
2. 建立直播数据导入模板，先支持 CSV / Excel / JSON。
3. 把每次直播 Workflow 的节省分钟写入 Savings Engine。
4. 接入真实抖店或淘宝直播数据。
5. 在老板日报里展示直播异常和第二天建议。

## 开发边界

允许：

- 在现有后端增加直播运营 Workflow。
- 在现有老板首页展示直播运营风险、省钱金额和 ROI。
- 在现有 Agent / Evaluation / Replay / Training 基础上增加节省人工的证明。
- 增加测试和文档。

不允许：

- 推倒重构。
- 新增大量页面。
- 继续做新的客服聊天功能。
- 修改数据库结构，除非先提出明确方案。
- 非授权抓取淘宝、抖音、闲鱼或拼多多数据。

## 每次开发前必须回答

1. 这个功能替代哪个岗位？
2. 一天能节约多少时间？
3. 一个月能节约多少人工？
4. 老板为什么愿意付钱？
5. 是否能进入真实 Workflow？
6. 是否能计算节省金额？

回答不了，就不要开发。

## 下一步：直播模板驱动 Workflow

优先级：P0。

目标：让商家上传直播运营模板后，系统自动识别模板类型，并调用对应 Workflow：

1. `live-products-template.csv` + `live-coupons-template.csv` + `live-script-template.csv` → 开播前检查。
2. `live-metrics-template.csv` → 直播中扫描。
3. `live-post-review-template.csv` → 下播复盘。

验收标准：

- 上传样例文件后能生成真实检查报告。
- 报告进入 Workflow 日志。
- Savings Engine 可以读取日志并计算节省金额。
- 不新增无关页面，不新增新 Agent。

## 下一步：直播 Workflow 持久化

优先级：P0。

当前直播模板已经能在网页触发 Workflow。下一步不要继续做新页面，应把 Workflow 日志从内存改为 Supabase 持久化：

1. 确认 `docs/live-workflow-log-schema-proposal.md` 的表结构。
2. 新增 migration。
3. 将 `live_workflow_log_store` 替换为数据库 repository。
4. Dashboard 和 Savings Engine 改为读取真实日志聚合。

这样老板每天看到的节省金额才有真实证据链。

## 下一步：老板首页接入 CEO 日报

优先级：P0。

目标：不新增新页面，而是把 `/dashboard` 首屏改为读取 `GET /v1/ceo/daily-report`。

验收标准：

- 老板打开首页第一眼看到一句话结论、今日节省金额、最高风险和下一步动作。
- 不再让老板先看聊天、表格或复杂图表。
- CEO 日报必须显示证据点，说明节省金额来自哪些 Workflow。
- 前端失败时使用本地 fallback，但文案必须明确是演示数据。

## 下一步：直播日志 Supabase 持久化

优先级：P0。

老板首页已经能显示 CEO 日报。下一步必须让证据链从内存日志变成 Supabase 持久化日志：

1. 确认 `docs/live-workflow-log-schema-proposal.md` 表结构。
2. 新增 `live_workflow_runs` migration。
3. 新增 PostgreSQL/Supabase 版 `LiveWorkflowRunRepository`。
4. Savings Engine 和 CEO 日报读取真实持久化日志。
5. 老板首页显示“真实数据 / 演示数据”状态，避免商家误解。

## 下一步：退款协同 Workflow

优先级：P0。

目标：补齐 Agent 协同从“路由级”到“执行级”的缺口。

拟替代岗位：客服主管 / 售后主管 / 仓库协调。

预估节省：每天 15-30 分钟，每月 6.5-13 小时。

验收标准：

1. 客服收到退款/投诉意图后，不直接回复，而是进入售后协同 Workflow。
2. 售后 Agent 判断退款、补发、换货、赔偿或人工审批。
3. Workflow 产出老板可读证据、建议动作、是否需要审批、节省分钟和节省金额。
4. 结果进入 Savings Engine 和 CEO 日报证据链。
5. 不新增页面，不新增客服聊天功能。
## 下一步：退款协同接真实订单和审批记录

优先级：P0。

目标：把退款协同 Workflow 从参数模拟推进到真实业务记录。

验收标准：

1. 退款协同读取真实订单金额、发货状态、物流状态和库存状态。
2. 高风险退款写入老板审批记录，而不是只在响应里标记 `approval_required`。
3. 审批通过后生成客服回复和售后成本记录。
4. Savings Engine 和 CEO 日报读取真实退款协同运行记录。
5. 不新增页面，不新增客服聊天功能。