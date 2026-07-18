## 2026-07-18 Production Merchant Data Gate V1

### Added

- Production daily operations now loads merchant products, orders, and after-sale records before it runs workflows.
- Added tests for database-backed payload generation, empty-source blocking, and scheduled workflow forwarding.

### Changed

- Postgres scheduled jobs block when merchant source data is empty or unavailable; they no longer write `safe_baseline` results as production evidence.

## 2026-07-18 CEO 日报快照证据链 V1

### Added

- 新增 `ceo_daily_report_snapshots` PostgreSQL migration 和内存/PostgreSQL 仓储。
- 每日主动工作完成后保存 CEO 日报快照，包含数据可信状态、Savings/ROI 和 proof points。
- 生产证据链门禁新增 `CEO_REPORT_SNAPSHOT_STORAGE=postgres` 和快照表检查。
- 新增 CEO 快照持久化测试。

- 全量 API 测试：87 passed。

- 生产每日任务未完成日报快照持久化配置时保持 `blocked`，不写入看似真实的工作结果。
## 2026-07-18 每日主动工作证据链 Guard V0

### Added

- `DailyOperationsJobResult` 新增 `evidence_chain_ready` 和 `evidence_chain_blockers`。
- 生产定时任务在 `LIVE_WORKFLOW_LOG_STORAGE=postgres` 时会检查完整 evidence chain readiness。
- 新增测试覆盖“数据库存在但证据链未 ready 时，定时任务 blocked”。

### Changed

- 定时任务不再只检查 live workflow storage 和 DATABASE_URL，而是检查完整 AI Employee OS 证据链。
- 战略审计真实数据证据链更新为 50，总分更新为 77。

### Verification

- 核心测试通过：57 passed。
## 2026-07-18 生产证据链 Readiness Gate V0

### Added

- `ProductionBootstrapResult` 新增 `evidence_chain_ready` 和 `evidence_chain_blockers`。
- 新增 `assess_evidence_chain_readiness()`，检查 Postgres 仓储模式、证据链表、WMS/ERP sender 和凭证。
- `/health/ready` 返回 evidence chain readiness 状态和 blockers。
- 新增测试覆盖默认 blocked、完整配置 ready、缺失证据链表 blocked。

### Changed

- 生产 bootstrap 只有在商家桥接和证据链都 ready 时才返回 ready。
- 战略审计真实数据证据链更新为 48，总分更新为 76。

### Verification

- 核心测试通过：56 passed。
## 2026-07-17 WMS/ERP HTTP Sender 边界 V0

### Added

- 新增 `HttpApiWarehouseNotificationSender`，支持把仓库通知 POST 到真实 WMS/ERP HTTP endpoint。
- 新增 WMS/ERP 配置：`WAREHOUSE_NOTIFICATION_WMS_API_URL`、`WAREHOUSE_NOTIFICATION_WMS_API_KEY`、`WAREHOUSE_NOTIFICATION_WMS_TIMEOUT_SECONDS`。
- 新增测试覆盖 WMS/ERP HTTP payload、Bearer key、外部单号解析、缺少 API URL 失败路径。
- CEO 日报会把 failed 仓库通知展示为老板风险和 priority action。

### Changed

- `warehouse_notification_sender_from_settings()` 支持 `WAREHOUSE_NOTIFICATION_DELIVERY_MODE=http_api`。
- 战略审计 Agent 协同更新为 90，但真实数据证据链仍保留为 P0 缺口。

### Verification

- 相关测试通过：20 passed。
- 核心测试通过：38 passed。
## 2026-07-17 仓库通知派发状态流转 V0

### Added

- 新增 `POST /v1/warehouse-notifications/dispatch`。
- 仓库通知支持 queued / sent / failed / cancelled 状态流转。
- 默认 `export_queue` 派发模式会生成 WMS/ERP 导出引用 `external_reference`。
- CEO 日报新增仓库通知 sent / queued / failed 状态证据。
- 新增测试覆盖成功派发和 WMS sender 失败状态。

### Changed

- 售后决策仓储协议新增 queued 通知查询和状态更新方法。
- InMemory 与 PostgreSQL 仓储都支持仓库通知状态统计。
- 战略审计 Agent 协同更新为 89，仍保持真实数据证据链为 P0 缺口。

### Verification

- Python 语法检查通过。
- 核心测试通过：34 passed。
## 2026-07-17 CEO 日报接入售后决策证据链 V0

### Added

- CEO 日报新增售后决策证据点：审批结果数量、售后成本、仓库通知数量、最新仓库通知编号。
- 售后决策汇总新增 after_sale_cost_yuan、warehouse_notification_count、latest_warehouse_notification_id。
- 新增测试验证售后审批和仓库通知可以进入 CEO 日报 proof_points 与 priority_actions。

### Changed

- 修复退款协同测试隔离，避免 Postgres 仓储切换测试污染 Savings、CEO 日报和每日运营测试。
- 保持 AI Employee OS 方向：不新增客服聊天、不新增 Prompt 页面、不新增知识库页面、不新增无关 Dashboard。

### Verification

- Python 语法检查通过。
- 核心测试通过：33 passed。
## 2026-07-16 审批决策回写与仓库通知 V0

### Added

- 新增 `after_sale_decision_workflow`。
- 新增 `POST /v1/approvals/{approval_id}/decision`。
- 新增 `ApprovalDecisionRequest` 和 `ApprovalDecisionResponse`。
- 新增测试验证老板审批后生成售后结果、仓库通知编号，并进入 Savings Engine。

### Changed

- 审批记录仓储支持 `approved` / `rejected` 决策回写。
- Savings Engine 会把售后审批决策结果计入 AI AfterSale 的工作量和节省金额。
- 战略自检中 Agent 协同能力更新为已具备审批决策回写和仓库通知生成。

### Notes

- 本次不新增页面、不新增 Agent、不新增客服聊天功能。
- 下一步应持久化售后决策结果，并接真实 WMS/ERP/仓库通知 API。
## 2026-07-16 退款协同真实订单证据链 V0

### Added

- 新增 `refund_business_evidence`，支持按 `order_external_id` 读取订单、物流、订单明细和库存证据。
- 退款协同请求新增可选 `order_external_id`。
- 退款协同响应新增 `evidence_source`。
- 新增测试验证真实订单证据优先于手工参数。

### Changed

- 退款协同 Workflow 会把真实订单证据写入 proof 和步骤 evidence。
- 战略自检中 Agent 协同能力更新为已具备真实订单/物流/库存证据读取能力。

### Notes

- 本次不新增页面、不新增 Agent、不新增客服聊天功能。
- 下一步应把审批决策写回售后成本、仓库通知和客户最终回复。
## 2026-07-16 审批记录持久化边界 V0

### Added

- 新增 `InMemoryApprovalRecordRepository` 和 `PostgresApprovalRecordRepository`。
- 新增 `configure_approval_record_repository_from_settings()`，API 启动时按配置选择审批记录仓储。
- 新增 Supabase migration：`202607160001_approval_records.sql`。
- 新增 `APPROVAL_RECORD_STORAGE` 环境变量示例。
- 新增测试保护审批仓储注入、postgres 切换和 migration 必要字段。

### Changed

- 高风险退款产生的 `approval_id` 已具备生产持久化通道。
- 老板待审批事项从“内存列表”推进到“可切换数据库仓储”。

### Notes

- 本次不新增页面、不新增 Agent、不新增客服聊天功能。
- 生产环境仍需执行 migration 并显式设置 `APPROVAL_RECORD_STORAGE=postgres` 才会落库。
## 2026-07-16 高风险退款审批记录 V0

### Added

- 新增 `approval_records` 模块，用于沉淀 workflow 产生的老板待审批事项。
- 退款协同结果新增 `approval_id`，高风险退款会写入待审批池。
- 新增测试验证 `/v1/approvals/pending` 能看到高风险退款 workflow 产生的审批记录。

### Changed

- `/v1/approvals/pending` 从静态样例改为读取审批记录列表。
- 退款协同 Workflow 从“响应里提示需要审批”推进到“生成老板可追踪的待办”。

### Notes

- 本次不新增页面、不新增 Agent、不新增客服聊天功能。
- 下一步应把审批记录持久化到数据库，并接真实订单、库存、物流和售后成本记录。
## 2026-07-16 退款协同 Workflow V0

### Added

- 新增 `POST /v1/workflows/refund-collaboration/run`。
- 新增退款协同 Workflow 领域模型、执行引擎和测试。
- 新增退款协同结果进入 Savings Engine 的售后统计。

### Changed

- 战略自检中 Agent 协同能力更新为已有退款执行链。
- Savings Engine 文件改为稳定 ASCII 源码，避免 Windows 中文编码破坏 Python 文件。

### Notes

- 本次不新增页面、不新增 Agent、不新增客服聊天功能。
- 下一步应接真实订单、库存、仓库通知和老板审批记录。
## 2026-07-16 V2 战略缺口自检

### Added

- 新增 `GET /v1/strategy/audit`。
- 新增战略自检领域模型和后端引擎。
- 新增测试验证战略自检必须聚焦 AI Employee OS、直播运营助理、Savings/ROI 和 Agent 协同。

### Notes

- 本次不新增页面、不新增 Agent、不新增客服聊天功能。
- 当前最重要缺口仍是真实数据证据链和端到端 Agent 协同 Workflow。
## 2026-07-16 API 启动接入直播 Workflow 持久化配置

### Changed

- API 应用启动时会调用直播 Workflow 日志仓储配置逻辑。
- 当 `LIVE_WORKFLOW_LOG_STORAGE=postgres` 且 `DATABASE_URL` 可用时，网页触发的 Workflow 也会使用 PostgreSQL/Supabase 仓储。

### Added

- 新增测试保护 API 启动时必须配置直播 Workflow 日志仓储。

### Notes

- 本次不新增页面、不新增 Agent。
- 线上仍需先执行 Supabase migration，再启用 postgres 存储模式。
# CHANGELOG

## 2026-07-16 跨平台定时任务与 Render Cron

### Added

- 新增 `tools/run-api-module.cjs`，跨平台运行后端 Python 模块。
- `render.yaml` 新增每日主动工作 Cron 服务。
- `docker-compose.production.yml` 新增 `daily-operations` 可选 job。
- 新增测试保护 `api:daily-operations` 脚本和 Render Cron 配置。

### Changed

- `npm run api:daily-operations` 改为通过 Node 启动器执行，不再绑定 Windows `.venv\Scripts\python`。
- `npm run api:bootstrap` 同步改为跨平台启动器。

### Notes

- 本次不新增页面、不新增 Agent、不开发聊天功能。
- 生产自动执行仍需要部署平台启用 Cron，并配置真实数据库持久化。

## 2026-07-16 每日主动工作定时任务入口

### Added

- 新增 `daily_operations_job.py`，提供每日主动工作命令行入口。
- 新增 `npm run api:daily-operations`，方便本地和服务器 Cron 调用。
- 新增测试覆盖 memory 模式执行和 postgres 必需但数据库缺失时的 blocked 逻辑。
- 更新每日主动工作文档，补充生产定时任务和 PostgreSQL 持久化要求。

### Notes

- 本次不新增页面、不新增 Agent、不开发聊天功能。
- 真实平台数据接入仍是下一步。

## 2026-07-16 老板首页每日主动工作入口

### Added

- 老板首页新增“让 AI 开始今日工作”按钮，调用真实后端 `POST /v1/daily-operations/run`。
- 新增前端 `DailyOperationsRun` 和 `LiveWorkflowRun` 类型。
- 新增 `runDailyOperations()` API client 方法。
- 执行后在老板首页展示完成工作数、节省分钟、节省金额、数据模式和下一步提示。

### Notes

- 本次不新增页面、不新增 Agent、不开发客服聊天功能。
- 当前仍需接入真实平台数据和生产定时任务，才能实现每天自动工作。

## 2026-07-15 每日主动工作编排器

### Added

- 新增 `apps/api/app/domain/daily_operations.py`，定义每日主动工作运行结果。
- 新增 `apps/api/app/infrastructure/daily_operations_runner.py`，复用直播 Workflow、CEO 日报和 Savings Engine 完成一轮每日工作。
- 新增 `POST /v1/daily-operations/run`，支持 `manual`、`scheduled`、`webhook` 三种触发来源。
- 新增 `DailyOperationsRunRequest` 和 `DailyOperationsRunResponse`。
- 新增测试覆盖无真实数据的安全基线巡检和有商家数据的三段 Workflow 执行。
- 新增 `docs/daily-operations-runner.md`，说明替代岗位、节省时间、商业价值和接入方式。

### Changed

- CEO 日报响应补齐 `data_status`、`data_status_label`、`data_status_reason`，避免商家误解数据可信状态。

### Notes

- 本次不新增页面、不新增 Agent、不开发聊天功能。
- 生产定时执行和平台真实 API 接入仍是下一步。

## 2026-07-15 直播 Workflow 生产表 Migration

### Added

- 新增 `supabase/migrations/202607150001_live_workflow_runs.sql`，为直播运营 Workflow 增加生产数据库表。
- 表字段覆盖 Workflow 阶段、状态、风险提醒、建议动作、老板审批、证据句、节省分钟、节省金额和风险分。
- 新增后端测试，保护 `live_workflow_runs` migration 必须保留省钱统计和证据字段。

### Notes

- 本次只生成本地 migration，不执行线上 Supabase。
- 默认日志仓储仍为 memory；执行生产迁移后再切换 `LIVE_WORKFLOW_LOG_STORAGE=postgres。

## 2026-07-14

### Added

- 新增 GET /v1/live-operations/runs，可查询开播前检查、直播中扫描、下播复盘产生的 Workflow 运行日志。
- 新增 pps/api/app/infrastructure/live_workflow_log_store.py，先以内存仓储记录直播 Workflow 日志，并供 Savings Engine 聚合。

- 新增 `GET /v1/live-operations/summary`，输出直播运营助理的开播前检查、直播中预警、下播后复盘工作流。
- 新增 `GET /v1/savings/summary`，输出 AI 员工替代岗位、今日节省分钟、今日节省金额、本月预测节省和年度 ROI。
- 新增 `POST /v1/live-operations/pre-live-check`，支持用商品、库存、优惠券、价格、脚本、赠品和商品排序数据执行开播前检查。
- 新增 `POST /v1/live-operations/live-metric-scan`，支持用在线人数、成交率、停留率、评论、商品点击率、库存变化和异常订单执行直播中扫描。
- 新增 `POST /v1/live-operations/post-live-review`，支持用销售额、订单数、观看人数、退款数、爆款商品、负面评论和主播脚本得分生成下播复盘。
- 新增 `apps/api/app/domain/live_operations.py` 和 `apps/api/app/infrastructure/live_operation_engine.py`，把直播运营助理与 Savings Engine 从页面概念沉到后端业务层。
- 新增 `apps/api/app/infrastructure/live_operation_workflows.py`，把开播前、直播中、下播后三段工作流变成可测试规则引擎。
- 新增 `docs/live-operation-agent.md`，记录直播运营助理目标、接口、字段映射、安全边界和下一步。
- 新增 `apps/api/tests/test_live_operations_and_savings.py`，验证直播运营助理与省钱引擎接口。
- 新增 `apps/web/src/shared/api/employee-os-fallback-data.ts`，后端不可用时仍能展示 V2 战略下的正确老板首页。
- 新增 `apps/api/app/infrastructure/production_bootstrap.py`，用于生产环境数据库就绪检查和默认商家数据初始化。
- 新增 `npm run api:bootstrap`，数据库连接配置好后可一键检查表结构、初始化 AI 老板、AI 客服、AI 售后、AI 运营和外部消息桥接连接。
- 新增 `apps/api/tests/test_production_bootstrap.py`，覆盖数据库未配置时的阻塞提示和商家公司 ID 选择逻辑。

### Changed

- Savings Engine 现在优先读取直播 Workflow 运行日志；暂无日志时才回退到 V0 估算。

- 老板首页改为优先展示直播运营风险、AI 今日节省金额、岗位替代进度、AI 员工绩效和 ROI，不再把客服聊天作为第一屏核心。
- `NEXT_TASK.md` 改为 2026 V2 战略：P0 只围绕直播运营助理、老板日报、Savings Engine 和 ROI Engine。
- `PROJECT_GUIDE.md` 增加 V2 战略约束：开发前必须回答替代哪个岗位、节省多少时间、老板为什么付钱。
- 重写 `docs/production-deployment.md` 为正常中文，明确商家如何使用、后端如何部署、生产初始化如何执行、哪些密钥不能暴露。

### Notes

- 本次不修改数据库 migration，不推倒架构，不新增 Agent。
- 当前仍需要真实 Supabase `DATABASE_URL` 和平台官方密钥，才能让真实店铺消息稳定进入后端。

## 2026-07-12

### Added

- 新增 GET /v1/live-operations/runs，可查询开播前检查、直播中扫描、下播复盘产生的 Workflow 运行日志。
- 新增 pps/api/app/infrastructure/live_workflow_log_store.py，先以内存仓储记录直播 Workflow 日志，并供 Savings Engine 聚合。

- 新增 `docs/commerce-dataset.md`，明确 Commerce Dataset 的范围、Replay 方法和 Evaluation 指标。
- 新增 `/commerce-dataset` 标准电商数据集页面，展示数据类型、字段完整率、Replay 准备度和导入入口。
- 老板首页新增“今天先看这里”和“省钱进度”，让商家第一眼知道该看什么、点哪里、为什么值得继续用。
- 新增 `docs/replay-engine.md`，明确 Replay Engine 的目标、业务规则、指标和下一步接入真实数据的方法。
- 新增 `docs/validation-engines.md`，定义 Evaluation、Training Center、Simulation 的验证链路。
- 新增 `GET /v1/replay/summary`，返回历史工作回放样例、准确率、自动处理率、人工接管率和预估节省金额。
- 新增 `/replay` 回放验证页面，用来展示 AI 与历史人工处理结果的对比。
- 新增 `GET /v1/evaluation/summary` 和 `/evaluation`，用于输出 AI 团队评分、替代进度和阻塞项。
- 新增 `GET /v1/training-center/summary` 和 `/training-center`，用于展示老板修正样本如何进入 Memory、Knowledge、Workflow。
- 新增 `GET /v1/simulation/summary` 和 `/simulation`，用于模拟客户咨询、砍价、退款、投诉和私域跟进场景。
- 新增 `GET /v1/commerce-dataset/readiness`，把商品、订单、客户、消息、售后、物流转换为验证准备度快照。
- 新增 Sites 无依赖宣传站发布包脚本 `tools/create_sites_vinext_promo_archive.py`，用于线上部署 ToB 宣传页。
- 新增 `docs/ai-commerce-os-super-simple-operation-manual.md`，用极简中文说明老板、客服、售后、运营每天怎么使用系统。
- 新增 `docs/open-source-adoption-mall-app-web.md`，记录 `mall-app-web` 的订单、商品、售后字段吸收范围。
- 新增 `docs/merchant-full-user-manual.md` 和 `/merchant-manual` 商家说明书，逐项解释菜单、图标、按钮、客服、售后和平台接入。
- 新增四个平台 CSV 导入模板：淘宝/天猫、抖店、拼多多、闲鱼，帮助商家按统一字段整理试用数据。
- 新增 `docs/pre-real-data-readiness.md`，明确真实商家数据接入前的资料准备、平台边界和验收指标。
- 新增 `docs/open-source-adoption-ecommerce-skills.md`，记录 `eCommerce-Skills` 的审计结论、可吸收能力和暂不吸收范围。
- 新增 `/knowledge-base` 电商技能知识库页面，展示已吸收的客服、售后、商品、投流、库存、价格、评价知识框架。

- 新增 `PROJECT_GUIDE.md`，固化 AI Commerce OS 长期开发原则。
- 新增 `PROJECT_STATE.md`，记录当前产品状态、完成度、阻塞点和安全边界。
- 新增 `NEXT_TASK.md`，明确下一阶段只开发 Commerce Dataset，不继续新增 Agent。
- 新增 `IDEAS.md`，用于收纳暂不开发的新想法。
- 新增产品宣传书 `docs/product-brochure.md`。
- 新增一页版宣传书 `docs/product-brochure-one-page.md`。
- 新增宣传主视觉图 `assets/marketing/ai-commerce-os-hero.png`。
- 新增中文宣传海报 `assets/marketing/ai-commerce-os-poster.svg`。
- 新增 ToB 商务版主视觉图 `assets/marketing/ai-commerce-os-b2b-hero.png`。
- 新增 ToB 商务版 PPT `assets/marketing/AI-Commerce-OS-B2B-Deck.pptx`。
- 新增 PPT 生成脚本 `tools/create_b2b_marketing_pptx.py`。
- 新增商务路演版 PPT `assets/marketing/AI-Commerce-OS-Business-Roadshow-Deck.pptx`。
- 新增商家成交版 PPT `assets/marketing/AI-Commerce-OS-Merchant-Sales-Deck.pptx`。
- 新增商家成交版 PPT 生成脚本 `tools/create_merchant_sales_pptx.py`。
- 新增 ToB 宣传网站页面 `/promo`。
- 新增可点击演示界面，支持切换 AI客服、AI售后、AI运营和老板审批。
- 新增前端公开营销素材 `apps/web/public/marketing/ai-commerce-os-b2b-hero.png`。

### Changed

- Savings Engine 现在优先读取直播 Workflow 运行日志；暂无日志时才回退到 V0 估算。

- 平台数据导入支持 JSON 预览与字段映射，和 CSV、Excel 共用同一套导入链路。
- 售后回放样例默认进入审批，避免 AI 在退款、退货、赔偿场景越权。
- 侧边栏新增“AI 评分”“训练中心”“模拟压测”，形成数据集、回放、评分、训练、模拟的验证闭环。
- `/commerce-dataset` 改为读取后端数据准备度，不再只展示静态百分比。
- Evaluation Engine 新增“真实数据准备度”评分项。
- Training Center 改为优先读取真实 `learning_events`，老板修改 AI 回复后会进入真实训练队列。
- Training Center 新增 Memory、Knowledge、Workflow 沉淀候选池，先生成可复核资产，不直接污染长期记忆。
- Training Center 新增“确认沉淀”接口和按钮，确认后可写入 `memories`、`knowledge_sources` / `knowledge_chunks` 或 `workflows` 草稿。
- Replay Engine 改为优先读取客服消息、售后 case、物流和客户行为生成回放样本，不再只依赖固定样例。
- Evaluation Engine 改为基于真实 Replay 样本数量计算评分。
- AI客服回复草稿改为通过 Knowledge / Memory 低风险回复引擎生成，并在工作台展示命中知识、命中记忆、预计节省分钟和预计节省金额。
- 数据导入预览吸收成熟商城常见字段，支持自动识别 `orderSn`、`payAmount`、`productName`、`productSkuCode`、`deliverySn`、`proofPics` 等字段。
- 老板首页新增“商家一键开始”四步入口：导入店铺数据、处理客户消息、处理售后审批、查看省钱结果。
- AI客服工作台的消息查看改为支持稳定 URL 链接，例如 `/ai-employees/ai-customer/workbench?message=msg-2`，降低商家点击失败时的使用门槛。
- 平台集成页升级为淘宝、抖店、拼多多、闲鱼四个平台接入窗口，补充商家准备材料、操作步骤和安全边界说明。
- 平台数据导入页新增模板下载区和拼多多接入准备模式；拼多多暂不提交入库，避免未确认数据库平台枚举前产生不一致数据。
- 老板首页新增真实数据接入前检查卡片，提示下载模板、导入 30 天数据、跑回放验证和查看省钱金额。
- 知识库从“建设中”升级为可用的电商技能库；外部 Skills 只作为 Knowledge / SOP，不直接赋予 AI 自动执行权限。
- 将项目最高优先级调整为 Commerce Dataset、Replay Engine、Simulation Engine、Evaluation Engine、Training Center。
- 明确当前目标是节省电商人力成本，优先验证 AI Customer、AI AfterSale、AI Operation 是否能替代岗位工作。
- 将 PPT 从主要演示材料降级为辅助材料，优先使用 `/promo` 做商家演示。

### Notes

- 当前不修改数据库。
- 当前不重构目录。
- 当前不引入新框架。
- 当前不推倒重来。

## 2026-07-14 直播运营导入模板

- 新增 5 个直播运营 CSV 模板：直播商品、优惠券、脚本、直播中数据、下播复盘。
- 在“平台数据导入”页面增加直播运营模板下载入口。
- 新增 `docs/live-data-import-templates.md`，说明每个模板字段与对应 Workflow。
- 新增 `docs/live-workflow-log-schema-proposal.md`，提出直播 Workflow 日志表设计，但未执行数据库 migration。

## 2026-07-14 直播模板直接执行 Workflow

- 将“平台数据导入”页升级为可执行入口：上传直播商品、优惠券、脚本、直播中数据、下播复盘模板后，可直接调用直播运营 Workflow。
- 开播前检查会生成库存、优惠券、价格、脚本、赠品、商品顺序等风险报告。
- 直播中扫描会生成成交率、停留率、点击率、库存变化、异常订单等提醒。
- 下播复盘会生成成交分析、退款风险、主播表现和第二天建议。
- 页面直接展示 AI 评分、节省分钟数、预估节省金额和下一步动作。
- 未修改数据库，继续复用现有直播 Workflow API 与内存日志。

## 2026-07-14 直播 Workflow 日志仓储边界

- 新增 `LiveWorkflowRunRepository` 领域仓储接口，明确直播 Workflow 日志是 Savings Engine 的证据来源。
- 将原来的全局内存列表封装为 `InMemoryLiveWorkflowRunRepository`，保留当前行为但去掉业务层对全局变量的直接依赖。
- 增加仓储注入入口，后续替换 PostgreSQL/Supabase 实现时不需要改直播 Workflow 路由和 Savings Engine。
- 增强直播运营测试隔离，每个测试使用独立日志仓储实例。

## 2026-07-15 CEO 日报 API

- 新增 CEO 日报领域模型和生成引擎，聚合直播运营、Savings Engine 和 Workflow 日志。
- 新增 `GET /v1/ceo/daily-report`，返回老板第一眼需要看的经营结论、风险、动作和省钱证据。
- CEO 日报不新增页面、不改数据库，先作为老板首页首屏和未来 AI Boss 的后端底座。
- 新增 CEO 日报测试，验证默认日报和真实直播 Workflow 运行记录会进入 proof points。

## 2026-07-15 Dashboard 接入 CEO 日报

- 将 `/dashboard` 首屏接入 `GET /v1/ceo/daily-report`。
- 老板首页第一屏改为展示一句话结论、今日节省金额、最高风险、今日优先动作和证据点。
- 新增前端 CEO 日报类型、API client 方法和 fallback 数据。
- 清理老板首页核心区域历史乱码文案，统一为中文经营日报表达。
- 未新增页面，未修改数据库。

## 2026-07-15 CEO 日报数据可信状态

- CEO 日报新增 `data_status`、`data_status_label`、`data_status_reason`。
- 当直播 Workflow 有运行记录时，日报显示“真实 Workflow 数据”。
- 当没有真实运行记录时，日报显示“演示估算数据”，并解释当前用于试用演示和接入前校准。
- Dashboard 首屏展示数据状态徽标和说明，避免商家误以为演示估算就是已接入真实店铺。
- 顺手清理 CEO 日报后端引擎中的历史乱码文案。

## 2026-07-15 PostgreSQL 直播日志仓储预留

- 新增 `PostgresLiveWorkflowRunRepository`，用于后续把直播 Workflow 日志写入 Supabase/PostgreSQL。
- 新增 `LIVE_WORKFLOW_LOG_STORAGE=memory` 配置示例，默认不启用 PostgreSQL。
- 新增仓储选择函数：只有显式设置为 `postgres` 且数据库可用时才切换。
- 当前不执行 migration，继续遵守数据库设计先确认的原则。






