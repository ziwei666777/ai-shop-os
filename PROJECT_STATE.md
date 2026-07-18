## 2026-07-18 生产每日任务读取真实商家数据 V1

本次新增：
- `run_daily_operations_job()` 在 Postgres 模式通过 `daily_operations_data_provider.py` 读取商品、订单和售后数据。
- 真实数据可生成开播前检查和下播复盘输入，进入 `live_workflow_runs`、Savings Engine 和 CEO 日报快照。
- 数据为空或读取失败时，生产任务显式 `blocked`，不会把安全基线巡检伪装成商家真实工作结果。

当前仍未完成：
- 优惠券、直播中在线人数、成交率、停留率和互动指标仍需抖店/淘宝直播连接。
- 云端 database migration、WMS/ERP 凭证和真实 endpoint 回执尚未验证。

## 2026-07-18 CEO 日报快照证据链 V1

本次新增：
- 每日主动工作完成后，将 CEO 日报的节省金额、ROI、数据可信状态和 proof points 写入 `ceo_daily_report_snapshots`。
- 新增内存/PostgreSQL 快照仓储和 Supabase migration `202607180001_ceo_daily_report_snapshots.sql`。
- `/health/ready` 与生产定时任务现在同时要求 `CEO_REPORT_SNAPSHOT_STORAGE=postgres` 和日报快照表存在。
- 新增测试验证每日运行会保存一份可追踪的 CEO 日报证据快照。

当前仍未完成：
- 尚未在真实云数据库执行 migration。
- 尚未配置真实 WMS/ERP 凭证和抖店/淘宝直播数据，因此线上 readiness 仍不能宣称通过。
## 2026-07-18 每日主动工作证据链 Guard V0

本次新增：
- `run_daily_operations_job()` 在 `LIVE_WORKFLOW_LOG_STORAGE=postgres` 时会先检查 `evidence_chain_ready`。
- 如果数据库、证据链表、Postgres 仓储模式、WMS/ERP sender 或凭证未 ready，定时任务会返回 blocked，不会写入看似真实的每日 AI 工作记录。
- `DailyOperationsJobResult` 新增 `evidence_chain_ready` 和 `evidence_chain_blockers`，让部署日志直接暴露阻断原因。
- 保留本地 memory 模式可跑安全基线巡检，用于开发和演示，但生产 postgres 模式必须真实证据链 ready。

替代岗位：
- 技术运营 / 运营负责人每天检查定时任务是否真实写入生产证据链、是否误用演示估算的工作。

本轮最终全量后端测试：87 passed。
- 每次生产定时任务排查减少约 10-20 分钟。
- 通过阻止假生产日志，降低老板日报和 Savings Engine 被演示估算污染的风险。

当前边界：
- Guard 已完成，但线上仍需执行 migrations、启用 Postgres storage、配置真实 WMS/ERP 凭证和真实平台数据。
- 战略审计总分从 76 到 77；真实数据证据链从 48 到 50；Agent 协同保持 90。

验证：
- 每日任务与生产 readiness 测试通过。
- 核心测试通过：57 passed。
## 2026-07-18 生产证据链 Readiness Gate V0

本次新增：
- `run_production_bootstrap()` 新增 `evidence_chain_ready` 和 `evidence_chain_blockers`。
- 新增 `assess_evidence_chain_readiness()`，统一检查 AI Employee OS 真实证据链是否达到生产启用条件。
- readiness gate 覆盖 DATABASE_URL、四张证据链表、三套 Postgres 仓储模式、WMS/ERP HTTP sender、WMS/ERP URL 和 API key。
- `/health/ready` 新增 `evidence_chain_ready` 和 `evidence_chain_blockers`，避免数据库连通但证据链未启用时误报 ready。
- 生产 bootstrap 总状态改为：商家桥接和证据链都 ready 才 ready。

替代岗位：
- 技术运营 / 实施人员 / 运营负责人上线前手工核对数据库、迁移、仓储模式、WMS/ERP 凭证和证据链状态的工作。

节省估算：
- 每次部署前可减少约 20-40 分钟人工核对。
- 通过阻止“假 ready”，减少上线后老板看到演示估算却误以为是真实节省数据的风险。

当前边界：
- readiness gate 已完成，但线上真实数据库、真实 WMS/ERP 凭证和真实平台数据仍需生产环境配置。
- 战略审计总分从 75 到 76；真实数据证据链从 42 到 48；Agent 协同保持 90。

验证：
- 生产 readiness / health 测试通过。
- 核心测试通过：56 passed。
## 2026-07-17 WMS/ERP HTTP Sender 边界 V0

本次新增：
- 仓库通知派发从 `export_queue` 推进到可配置 `http_api` sender 边界。
- 新增 `HttpApiWarehouseNotificationSender`，可向真实 WMS/ERP endpoint POST 补发/换货通知。
- WMS/ERP sender 会发送 notification_id、source_outcome_id、source_workflow_id、action、status、proof、created_at。
- 支持 `Authorization: Bearer <api_key>`、超时配置、外部单号 `external_reference` 解析。
- 未配置 API URL、HTTP 错误、超时或响应异常时，仓库通知进入 failed 状态。
- CEO 日报会把 failed 仓库通知提升为老板风险和 priority action，而不只是藏在 proof 里。

替代岗位：
- 仓库协调员 / 售后主管把补发换货审批结果手动录入 WMS/ERP、追踪失败通知、向老板汇报异常的工作。

节省估算：
- 单次真实 WMS/ERP 通知和外部单号回写节省约 5-10 分钟。
- 失败通知自动进入 CEO 日报，可减少漏通知、重复催仓和二次售后沟通。

当前边界：
- 已具备 HTTP API sender 代码边界和测试覆盖，但生产仍需配置真实 `WAREHOUSE_NOTIFICATION_WMS_API_URL` / `WAREHOUSE_NOTIFICATION_WMS_API_KEY`。
- 真实数据证据链仍需线上执行 migrations 并启用 Postgres 仓储。
- 战略审计整体仍为 75；Agent 协同推进到 90；真实数据证据链仍为 42。

验证：
- 相关测试通过：20 passed。
- 核心测试通过：38 passed。
## 2026-07-17 仓库通知派发状态流转 V0

本次新增：
- `warehouse_notifications` 从“只生成编号”推进到“可派发状态流转”：queued / sent / failed / cancelled。
- 新增 `POST /v1/warehouse-notifications/dispatch`，用于派发待处理仓库通知。
- 当前默认 `export_queue` 模式会把补发/换货通知标记为 sent，并生成 `external_reference`，作为真实 WMS/ERP 接入前的导出队列边界。
- 售后决策汇总新增 queued/sent/failed 计数和最新通知状态。
- CEO 日报会显示仓库通知 sent / queued / failed 状态，让老板知道补发/换货通知是否真正送出。
- 增加失败 sender 测试，证明真实 WMS/ERP 异常时通知会进入 failed，不会悄悄丢失。

替代岗位：
- 仓库协调员 / 售后主管手动把老板审批后的补发换货单转交仓库，并回填发送状态的工作。

节省估算：
- 单次补发/换货通知派发和状态回填节省约 5-10 分钟。
- 每天 5-10 单补发/换货时，可减少约 25-100 分钟跨系统沟通和追踪。

当前边界：
- 当前是 export queue / 状态流转边界，不是直接调用真实 WMS/ERP API。
- 生产仍需要启用 Postgres 仓储、执行 migrations，并把 export queue 替换为真实 WMS/ERP webhook/API。
- 战略审计整体仍为 75，真实数据证据链仍是最大缺口；Agent 协同推进到 89。

验证：
- Python 语法检查通过。
- 核心测试通过：34 passed。
## 2026-07-17 CEO 日报接入售后决策证据链 V0

本次新增：
- 修复退款协同测试的全局仓储状态泄漏，审批记录和售后决策结果在每个测试前后都会恢复到内存仓储。
- 售后决策汇总新增 after_sale_cost_yuan、warehouse_notification_count、latest_warehouse_notification_id。
- CEO 日报 proof_points 现在会直接展示售后审批结果数量、售后成本、仓库通知数量和最新仓库通知编号。
- CEO 日报 priority_actions 会在存在仓库通知时提醒 AI AfterSale 跟进补发/换货通知。
- 新增测试覆盖“退款协同 -> 老板审批 -> 售后结果 -> 仓库通知 -> CEO 日报证据”。

替代岗位：
- 售后主管 / 仓库协调员 / 运营负责人每天汇总售后审批结果、售后成本和补发换货通知的工作。

节省估算：
- 单次售后审批决策回写节省 12-16 分钟。
- 每天 5-10 单高风险售后时，可减少约 1-3 小时跨岗位沟通和日报汇总。

当前边界：
- 战略审计总分仍为 75，Agent 协同 88，真实数据证据链仍为最大缺口。
- 线上仍需执行 live_workflow_runs、approval_records、after_sale_decision_outcomes migrations，并配置 *_STORAGE=postgres。
- 仓库通知当前已进入可持久化记录和 CEO 证据链，但还没有真正调用 WMS/ERP/仓库系统 API。

验证：
- Python 语法检查通过。
- 核心测试通过：33 passed。
## 2026-07-16 审批决策回写与仓库通知 V0

本次新增：
- 新增 `after_sale_decision_workflow`，老板审批通过/拒绝后会生成售后处理结果。
- 新增 `POST /v1/approvals/{approval_id}/decision`。
- 审批通过后可生成退款、补发/换货、赔偿或拒绝结果。
- 补发/换货场景会生成 `warehouse_notification_id`，让仓库动作进入 workflow 证据链。
- 售后决策结果会计入 Savings Engine 的 AI AfterSale 完成工作数、节省分钟和节省金额。

替代岗位：
- 售后主管 / 仓库协调员 / 客服主管在老板审批后手工通知仓库、记录售后成本、整理客户回复的工作。

节省估算：
- 单次审批决策回写节省 12-16 分钟。
- 高风险售后从“判断 -> 审批 -> 仓库/客户动作”形成闭环后，每天 5-10 单可减少约 1-3 小时跨岗位沟通。

当前边界：
- 决策结果当前先作为 workflow 证据记录，尚未持久化到独立生产表。
- 仓库通知当前生成通知编号，还没有真正调用 WMS/ERP/仓库系统 API。
- 下一步不做新页面，优先补生产持久化和真实仓库/ERP 通知。
## 2026-07-16 退款协同真实订单证据链 V0

本次新增：
- 新增 `refund_business_evidence`，用于从真实 `orders`、`shipments`、`order_items`、`products` 读取退款协同证据。
- `POST /v1/workflows/refund-collaboration/run` 新增可选 `order_external_id`。
- 当传入订单号且数据库可查询时，workflow 优先使用真实订单金额、物流签收状态、订单明细和库存证据。
- 退款协同响应新增 `evidence_source`，区分 `manual_payload` 和 `real_order_records`。
- workflow proof 和步骤证据会显示真实订单证据来源，方便 CEO 日报和 Savings Engine 后续追踪。

替代岗位：
- 售后主管 / 仓库协调员 / 运营助理手工查订单、查物流、查库存再上报老板的工作。

节省估算：
- 单次高风险售后保守节省 10-20 分钟查证时间；叠加审批整理后仍按 24 分钟计入当前 Savings。
- 每天 5-10 单高风险售后时，可减少 1-3 小时人工查证和沟通。

当前边界：
- 当前是“读取真实证据”，还没有把审批通过/拒绝写回售后成本、仓库通知和客户最终回复。
- 生产启用仍依赖真实数据库、订单/物流/商品导入，以及 `approval_records` / `live_workflow_runs` migration。
- 下一步不做新页面，继续做审批决策回写和仓库通知 workflow。
## 2026-07-16 审批记录持久化边界 V0

本次新增：
- 新增 `approval_records` 仓储边界，默认使用内存，生产环境可显式切换 PostgreSQL。
- 新增 `PostgresApprovalRecordRepository`，高风险退款 workflow 生成的老板待审批事项具备落库通道。
- 新增 Supabase migration：`202607160001_approval_records.sql`。
- 新增配置：`APPROVAL_RECORD_STORAGE=memory|postgres`。
- API 启动时会按配置初始化审批记录仓储，和直播 workflow 日志保持同一套生产切换模式。

替代岗位：
- 售后主管 / 运营负责人每天整理高风险退款、上报老板、追踪审批状态的工作。

节省估算：
- 单次高风险售后保守节省 24 分钟。
- 审批记录持久化后，老板日报和 Savings Engine 可以按天追踪真实审批任务，减少人工汇总和漏审风险。

当前边界：
- 本地默认仍为 memory，避免开发环境误连数据库。
- 生产启用前需要在线执行 `202607160001_approval_records.sql`，并设置 `APPROVAL_RECORD_STORAGE=postgres`。
- 下一步仍是接真实 order/inventory/logistics 数据，并把审批通过/拒绝结果回写售后成本和客户回复。
## 2026-07-16 高风险退款审批记录 V0

本次新增：
- 高风险退款协同 Workflow 会生成真实待审批记录，而不只是返回 `approval_required`。
- `RefundCollaborationRun` 新增 `approval_id`，用于把售后协同结果和老板审批池串起来。
- `GET /v1/approvals/pending` 改为读取审批记录模块，优先返回 workflow 产生的待审批事项。
- 测试已覆盖：高风险退款进入老板待审批列表；缺少证据的退款保持 blocked，不生成审批记录。

替代岗位：
- 售后主管 / 客服主管的高风险退款整理和上报工作。

节省估算：
- 单次高风险售后仍按 24 分钟节省计入。
- 每天 5-10 单高风险售后时，可减少 2-4 小时人工整理、判断和上报时间。

当前边界：
- 审批记录当前仍是内存记录，尚未持久化到数据库。
- 退款金额、发货状态、库存状态当前仍来自 workflow 入参，下一步要接真实 order/inventory 数据。
- 下一步不做新页面，优先把 approval records 持久化，并把审批通过/拒绝结果回写售后成本和客户回复。
## 2026-07-16 退款协同 Workflow V0

本次新增：

- 新增 `POST /v1/workflows/refund-collaboration/run`。
- 新增退款协同领域模型和执行引擎。
- Workflow 覆盖：客服识别退款/投诉意图、售后判断退款/补发/赔偿/缺证据、运营校验订单和库存、老板审批高风险退款、客服按结果回复。
- 退款协同运行结果会进入 Savings Engine 的 AI 售后统计，增加完成工作数、节省分钟、节省金额和证据句。
- 战略自检中 Agent 协同能力从“仅路由级”推进到“已有退款执行链”。

替代岗位：

- 客服主管 / 售后主管 / 仓库协调。

节省估算：

- 单次退款协同节省 18-24 分钟。
- 按每天 5-10 单高风险售后估算，每天可节省 1.5-4 小时。

当前边界：

- 订单、库存、仓库通知仍是输入参数模拟，尚未接真实订单/库存系统。
- 老板审批结果还未持久化到审批表。
- 下一步应接真实 order/inventory/approval records，而不是新增页面。
## 2026-07-16 V2 战略缺口自检

本次新增：

- 新增 `GET /v1/strategy/audit`，让系统自己输出 AI Employee OS 战略完成度、缺口和下一步 P0 动作。
- 自检覆盖直播运营助理、CEO 老板日报、Savings/ROI、每日主动工作、Agent 协同和真实数据证据链。
- 自检结果明确列出停止方向：不新增 AI 客服页面、不新增聊天功能、不新增 Prompt 页面、不新增普通知识库页面、不为展示新增 Dashboard。
- 新增测试保护 V2 战略不跑回传统 AI 客服 SaaS。

当前判断：

- P0 基础骨架已经存在：直播三段 Workflow、CEO 日报、Savings/ROI、每日主动工作入口。
- 最大缺口仍是两件事：真实平台数据证据链、端到端 Agent 协同执行链。
- 下一步优先不是新增页面，而是补“退款协同 Workflow”和“live_workflow_runs 生产持久化”。

商业意义：

- 这个接口替代产品经理/运营负责人每天手工判断项目是否跑偏。
- 后续 CEO 日报、自动任务和部署检查可以直接读取战略缺口，确保每次开发都围绕节省人工和节省金额。
## 2026-07-16 API 启动接入直播 Workflow 持久化配置

本次新增：

- 后端 API 应用启动时会根据 `LIVE_WORKFLOW_LOG_STORAGE` 和 `DATABASE_URL` 配置直播 Workflow 日志仓储。
- 普通网页触发的开播前检查、直播中扫描、下播复盘，和定时任务一样具备切换 PostgreSQL/Supabase 持久化的入口。
- 新增测试保护 API 启动配置，避免生产环境只让 Cron 写 PostgreSQL、网页请求仍写内存日志。

商业意义：

- 老板在网页上手动触发 AI 工作时，生产环境也能进入真实证据链。
- Savings Engine、CEO 日报和 ROI 后续可以统一读取 `live_workflow_runs`，不再区分“按钮触发”和“定时触发”。

当前边界：

- 仍需在线上 Supabase 执行 `202607150001_live_workflow_runs.sql`。
- 仍需生产环境配置真实 `DATABASE_URL` 和 `LIVE_WORKFLOW_LOG_STORAGE=postgres`。
# PROJECT_STATE
## 2026-07-16 跨平台定时任务与 Render Cron

本次新增：

- 新增 `tools/run-api-module.cjs`，让 `npm run api:daily-operations` 在 Windows、Linux 和 macOS 都能运行。
- 修复 `api:daily-operations` 不再依赖 Windows 专用 `.venv\Scripts\python` 路径。
- `render.yaml` 新增 `ai-commerce-os-daily-operations` Cron 服务，每天北京时间早上 8 点执行每日主动工作。
- `docker-compose.production.yml` 新增 `daily-operations` 可选 job，方便服务器手动或外部定时器调用。
- 新增测试保护跨平台脚本和 Render Cron 配置。

商业意义：

- AI 从“有一个可运行命令”推进到“有生产 Cron 配置”。
- 老板早上打开系统时，可以看到 AI 已经先完成直播运营巡检和省钱记录。

当前边界：

- Render Cron 配置需要部署平台读取后才会生效。
- 真实生产证据仍要求先执行 Supabase migration 并配置 `LIVE_WORKFLOW_LOG_STORAGE=postgres`。
## 2026-07-16 每日主动工作定时任务入口

本次新增：

- 新增 `apps/api/app/infrastructure/daily_operations_job.py`。
- 新增 `npm run api:daily-operations`，可在本地或服务器上触发每日主动工作。
- 生产环境设置 `LIVE_WORKFLOW_LOG_STORAGE=postgres` 但数据库不可用时，任务会返回 blocked，避免虚假记录省钱结果。
- 文档补充 Railway Cron、Render Cron、Linux crontab 和 Windows 任务计划的接入方式。

商业意义：

- AI 从“老板点按钮才执行”推进到“每天到点自动上班”。
- 老板打开系统时可以直接看到 AI 已完成的巡检、节省金额和风险证据。

当前边界：

- 定时任务当前默认跑安全基线巡检。
- 接入真实抖店/淘宝直播数据后，才会成为完整商家数据巡检。
## 2026-07-16 老板首页接入每日主动工作

本次新增：

- 老板首页新增“让 AI 开始今日工作”按钮。
- 按钮调用 `POST /v1/daily-operations/run`，不是前端模拟弹窗。
- 执行后展示 AI 完成工作数、节省分钟、节省金额和数据模式。
- 无真实数据时显示“安全基线巡检”，避免商家误以为已经接入真实店铺。
- 保留“上传真实直播数据”入口，引导商家把基线巡检升级成真实数据执行。

商业意义：

- 商家打开控制台后，不再只是不知道看什么，而是可以直接让 AI 开始工作。
- 这一步把老板日报、直播 Workflow、Savings Engine 串成一个可操作闭环。

当前边界：

- 现在是手动触发；下一步要接服务器定时任务。
- 真正替代直播运营助理，需要接入抖店/淘宝直播真实数据源。
## 2026-07-15 每日主动工作编排器

本次新增：

- 新增 `POST /v1/daily-operations/run`，一次触发 AI 完成每日直播运营巡检。
- 无真实数据时返回 `safe_baseline`，明确提示这只是安全基线巡检。
- 有商家真实直播数据时返回 `merchant_payload`，并执行开播前、直播中、下播后三段 Workflow。
- 每次执行都会写入直播 Workflow 日志，并进入 Savings Engine 和 CEO 老板日报。

商业意义：

- 产品从“老板点单个工具”推进到“AI 每天主动完成一轮工作”。
- 当前优先替代直播运营助理每天的数据整理、风险检查和复盘动作。
- 预计每天节省 20-40 分钟，每月节省 10-20 小时。

当前边界：

- 还没有接入生产定时任务。
- 还没有直接读取抖店、淘宝直播真实 API。
- 正式商家使用时，需要把平台数据转换成接口字段后调用。
## 2026-07-15 直播 Workflow 生产表迁移草案

本次新增：

- 新增 Supabase migration：`202607150001_live_workflow_runs.sql`。
- 该表用于持久化开播前检查、直播中扫描、下播复盘等 Workflow 的运行证据。
- 字段包含 Workflow 阶段、状态、风险、建议动作、是否需要老板审批、证据句、节省分钟和节省金额。
- 后端已有 PostgreSQL 仓储可切换到该表，但默认仍使用内存仓储，避免未执行线上迁移前影响当前演示环境。

当前边界：

- migration 只在本地项目中生成，尚未执行到线上 Supabase。
- 正式启用前需要配置真实 `DATABASE_URL`，执行 migration，并设置 `LIVE_WORKFLOW_LOG_STORAGE=postgres`。
- 表只保存工作流证据和统计，不保存平台密钥、客户身份证、地址明文或完整平台原始响应。

商业意义：

- 老板首页的“节省多少钱”可以从真实 Workflow 运行记录计算，而不是只靠演示估算。
- 后续商家试用时，可以按天复盘 AI 直播运营助理到底替代了多少人工整理、检查和复盘工作。

## 2026-07-14 直播 Workflow 日志 V0

本次新增：

- `GET /v1/live-operations/runs`：查询直播 Workflow 运行日志。
- 开播前检查、直播中扫描、下播复盘执行后会自动记录日志。
- Savings Engine 优先读取真实 Workflow 日志聚合 AI直播运营助理的完成工作数、节省分钟、节省金额和绩效分。

当前边界：

- 日志当前是内存仓储，适合验证口径和测试流程。
- 正式商家试点前，需要先确认数据库设计，再把日志持久化到 Supabase。

下一步：

1. 建立直播数据导入模板。
2. 设计并确认直播 Workflow 日志表。
3. 将日志从内存迁移到 Supabase。
4. 接入真实抖店或淘宝直播数据。

## 2026-07-14 V2 战略升级进展

产品定位已经从传统 AI 客服 SaaS 调整为：

**AI Employee OS（企业 AI 数字员工操作系统）**

当前开发重心：

- P0：AI Live Operation Agent（直播运营助理）
- P0：CEO Agent 老板日报
- P0：Savings Engine 省钱引擎
- P0：ROI Engine 投入产出比

本次已经完成：

- 新增直播运营助理后端摘要接口：`GET /v1/live-operations/summary`
- 新增省钱与 ROI 后端摘要接口：`GET /v1/savings/summary`
- 新增开播前检查 Workflow：`POST /v1/live-operations/pre-live-check`
- 新增直播中指标扫描 Workflow：`POST /v1/live-operations/live-metric-scan`
- 新增下播复盘 Workflow：`POST /v1/live-operations/post-live-review`
- 老板首页第一屏改为展示今天节省金额、直播运营风险、岗位替代进度、AI 员工绩效和 ROI
- `NEXT_TASK.md` 已从 Commerce Dataset 优先改为直播运营助理与 Savings Engine 优先
- `PROJECT_GUIDE.md` 已增加 V2 战略约束，禁止继续把产品做成普通客服 SaaS

当前还未完成：

- 尚未接入真实抖店/淘宝直播实时数据
- 尚未建立直播 Workflow 的数据库日志记录
- 尚未建立直播中实时预警推送
- 尚未把下播后复盘写入老板日报
- Savings Engine 当前是 V0 估算，后续必须改成按真实任务日志计算

下一步应该做：

1. 建立直播 Workflow 日志。
2. 建立直播数据导入模板。
3. 把每个 Workflow 的节省分钟写入 Savings Engine。
4. 接入真实抖店或淘宝直播数据。
5. 在老板日报里展示直播异常和第二天建议。

## 2026-07-14 最新生产化进展

当前新增了生产初始化工具：

- `npm run api:bootstrap` 可以在真实 `DATABASE_URL` 配好后检查数据库、核心表、关键字段。
- 初始化默认公司、AI老板、AI客服、AI售后、AI运营。
- 初始化淘宝、抖音、闲鱼的外部消息桥接连接，方便真实店铺消息进入 AI 客服。
- 如果数据库或桥接密钥没配好，会返回明确的 blocked 和下一步动作。

当前最关键阻塞：

- 仍需要把真实 Supabase PostgreSQL `DATABASE_URL` 写入后端部署环境。
- 仍需要淘宝、天猫、抖店、拼多多等官方平台 App Key、App Secret、Webhook 或服务商授权。
- 没有这些真实凭证时，系统只能做文件导入、手动录入和合规外部消息桥接，不能直接控制平台客服窗口。

当前判断：

- 产品已经从纯展示页推进到“可部署的商家控制台 + 后端消息入口 + 生产初始化工具”。
- 距离“商家打开网页即可接入真实店铺客服并自动工作”，还差真实数据库连接、后端公网部署、平台官方授权三件事。

更新时间：2026-07-13

## 一、当前阶段

项目处于 V0.x。

当前不是完整可商用产品，而是 AI Commerce OS 的基础骨架和商家试用原型。

核心方向已经从“继续堆 Agent 页面”调整为“验证 AI 是否真的能替代电商岗位工作”。

## 二、当前产品形态

当前系统是一套浏览器里的 AI 电商员工控制台。

已有模块：

- Dashboard 老板首页。
- 老板首页第一眼行动区和省钱进度试算。
- AI Employees AI员工框架。
- AI Customer 工作台。
- AI AfterSale 工作台。
- 订单、商品、客户基础表格。
- Commerce Dataset 标准数据集入口。
- Replay Engine V0.1 回放验证入口。
- Evaluation Engine V0.1 AI 团队评分入口。
- Training Center V0.1 训练中心入口。
- Simulation Engine V0.1 模拟客户压测入口。
- 平台集成入口。
- 淘宝、抖音、拼多多、闲鱼数据导入说明和模板入口。
- AI客服商家使用说明书。
- 商家完整使用说明书和真实数据接入前检查清单。
- 电商技能知识库，已吸收 `eCommerce-Skills` 的客服、售后、商品、投流、库存、价格和评价分析框架。
- ToB 宣传网站 `/promo`。

## 三、当前架构

Monorepo：

- `apps/web`：Next.js 前端。
- `apps/api`：FastAPI 后端。
- `packages/shared`：共享常量与类型。
- `supabase/migrations`：数据库迁移。
- `docs`：架构、数据库、部署、说明文档。

已采用：

- Next.js
- React
- TypeScript
- TailwindCSS
- FastAPI
- SQLAlchemy
- Supabase PostgreSQL
- pgvector 预留
- Redis/RQ 预留
- LangGraph 预留

## 四、当前完成度

距离“替代深圳约 4 万/月电商团队”的目标：

- AI Customer：约 45%
- AI AfterSale：约 30%
- AI Operation：约 15%
- 产品建设成熟度：约 60%
- 真实可替代重复性人工：约 30% 到 35%

当前结论：已经可以做商家试用和数据采集，但还不能直接替代完整团队；当前更适合替代客服、售后、运营中的重复性、低风险、可审批工作。

## 五、已完成能力

AI Customer：

- 平台消息收件箱。
- AI 回复草稿。
- 自动回复与人工确认状态。
- 人工接管。
- 商家修改记录。
- 使用说明书。
- 高风险问题暂停规则。
- Knowledge / Memory 低风险回复草稿引擎。
- 回复草稿展示命中知识、命中记忆、预计节省分钟和预计节省金额。

AI AfterSale：

- 售后工作台。
- 售后 case 列表。
- 风险等级。
- AI 判断和审批建议。
- 高风险售后必须人工确认。

Commerce Data：

- 淘宝、抖音、闲鱼导入结构。
- 商品、订单、客户、物流、售后导入接口。
- CSV、Excel、JSON 文件预览和导入基础能力。
- 淘宝/天猫、抖店、拼多多、闲鱼 CSV 模板下载入口。
- 拼多多当前只开放模板和接入准备模式，尚未开启正式入库，避免未确认数据库平台枚举前产生不一致数据。
- Commerce Dataset 页面，用于说明数据类型、字段完整率、Replay 准备度和 Evaluation 指标。
- Commerce Dataset 页面已读取后端准备度 API，开始统计当前记录数、预计可回放样本数和下一步导入建议。

Replay Engine：

- 已新增回放 API。
- 已新增回放验证页面。
- 已能对客服、售后、物流、运营信号输出准确率、自动处理率、人工接管率、节省分钟数和预估节省金额。
- 已优先读取真实/导入业务数据生成 Replay Case；没有数据库时使用内存试用数据和种子数据。

Evaluation Engine：

- 已新增 AI 团队评分页面和 API。
- 已能基于真实 Replay 输出综合评分、准确率、人工接管率、高风险拦截和 4 万/月成本替代进度。
- 已把 Commerce Dataset 真实数据准备度纳入评分。
- 当前评分仍是 V0 样例评分，尚不能作为正式商家结算依据。

Training Center：

- 已新增训练中心页面和 API。
- 已能展示老板修改样本如何进入 Memory、Knowledge 和 Workflow。
- 已接入真实 `learning_events` 聚合；老板/客服/售后产生真实修改后，训练中心会优先展示真实训练样本。
- 已新增 Memory、Knowledge、Workflow 沉淀候选池，每条学习样本会生成可复核的候选资产和业务价值说明。
- 已新增“确认沉淀”能力，老板确认后可把候选资产写入长期 Memory、Knowledge 或 Workflow 草稿。
- 没有真实学习事件时，才回退显示 V0 样例训练样本。

Simulation Engine：

- 已新增模拟客户压测页面和 API。
- 已覆盖物流咨询、砍价、退款、投诉和私域跟进等典型场景。
- 当前是小样本压测，后续要扩展到批量模拟和自动评估。

文档：

- 架构文档。
- 数据库文档。
- Supabase 配置说明。
- 客服使用说明书。
- 部署形态说明。
- AI团队替代进度说明。
- 商家完整使用说明书。
- 真实商家数据接入前检查清单。
- `eCommerce-Skills` 开源技能吸收审计。

Knowledge：

- `/knowledge-base` 已从建设中页面升级为电商技能知识库。
- 已吸收客服、售后、商品内容、投流预算、库存补货、价格竞品、评价口碑、安全边界 8 类知识。
- 外部技能当前只作为 Knowledge / SOP，不直接变成 Agent 权限。

Boss Dashboard：

- 已新增“老板今天先看这里”，把审批、节省金额、下一步数据导入放在第一屏。
- 已新增“接真实数据前最后检查”，让商家按下载模板、导入 30 天数据、跑回放验证、看省钱金额四步准备试用。
- 已新增省钱进度试算，按 AI 已处理任务估算今日节省工时和本月节省金额。
- 该金额当前是试算值；Replay Engine V0.1 已具备样例校准能力，后续必须改为真实历史数据校准。

## 六、未完成关键能力

当前阻塞正式商用的能力：

- Supabase migration 尚未确认已执行到远程数据库。
- `DATABASE_URL` 仍需真实数据库密码。
- Redis/RQ Worker 尚未部署。
- 淘宝、抖音真实开放平台凭证尚未配置。
- 真实平台消息尚未自动进入 AI Customer。
- Memory、Knowledge、Workflow 尚未形成真实学习闭环。
- Replay Engine 已完成真实/导入业务数据回放 V0.1，后续需要增加真实人工结果字段、满意度和错误原因。
- Simulation Engine 已完成 V0.1 样例压测，尚未支持批量 10000+ 自动模拟。
- Evaluation Engine 已完成 V0.1 样例评分，尚未接入真实商家数据。
- Training Center 已完成真实 learning_events 聚合、沉淀候选池和确认写入 V0.1，后续需要接入向量化、版本管理和回滚。
- AI Operation 仍处于预留和规划阶段。

## 十一、当前演示材料

当前主要演示入口：

```text
/promo
```

该页面用于 ToB 商务演示，包含：

- 产品定位。
- 成本痛点。
- AI客服、AI售后、AI运营说明。
- 可点击演示界面。
- 7 天试用流程。
- 验收指标。

PPT 文件继续保留，但不作为主要演示材料。此前手写 OpenXML PPT 在部分查看器中可能空白，因此优先用宣传网站进行演示。

## 七、当前最高优先级

下一阶段优先级：

1. Commerce Dataset
2. Replay Engine
3. Evaluation Engine
4. Training Center
5. Simulation Engine

当前上述五个方向均已完成 V0.1 骨架，下一阶段应把真实商家历史数据接入这些引擎，而不是继续新增页面或 Agent。

最新进展：

- 已新增数据准备度桥接层。
- `/v1/commerce-dataset/readiness` 会把商品、订单、客户、消息、售后、物流转换成 Replay / Evaluation 可用的准备度快照。
- 这一步让产品从“静态样例验证”开始进入“商家导入数据后自动判断能不能验证”的阶段。

暂时不要新增更多 Agent。

## 八、当前安全边界

AI 可以：

- 生成客服回复草稿。
- 判断是否需要人工。
- 标记售后风险。
- 输出运营建议草稿。
- 记录商家修改。

AI 不可以：

- 自动退款。
- 自动赔偿。
- 自动投广告。
- 自动调整预算。
- 自动承诺优惠金额。
- 自动导出客户隐私数据。
- 绕过平台官方授权抓取数据。

## 九、下一步验收指标

下一阶段必须开始围绕指标开发：

- 客服自动回复率。
- 客服错误率。
- 人工接管率。
- 售后分类准确率。
- 售后高风险拦截率。
- 运营建议采纳率。
- 每日节省人工分钟数。
- 预估节省人力成本。

## 十、交付包

当前已生成安全源码包：

```text
dist/AI-Shop-OS-current-package.zip
```

该包不包含真实 `.env`、`.env.local`、`.venv`、`node_modules`、`.next`、日志和密钥。

## 直播运营数据标准化状态

当前已完成直播运营助理的第一批数据模板：商品、优惠券、脚本、直播中指标、下播复盘。模板已接入“设置 / 平台数据导入”页面，可供商家按标准填写真实数据。

当前没有修改数据库。直播 Workflow 日志表仍是待确认设计，详见 `docs/live-workflow-log-schema-proposal.md`。

下一步应把直播模板导入结果直接转成 Workflow 输入，自动调用开播前检查、直播中扫描、下播复盘，并把结果写入持久化日志。

## 直播模板执行状态

当前“设置 / 平台数据导入”已不只是模板下载页。商家可以上传直播运营模板，并直接触发后端直播 Workflow：

1. 商品 + 优惠券 + 脚本模板 → 开播前检查。
2. 直播中数据模板 → 直播中扫描。
3. 下播复盘模板 → 下播复盘。

执行结果会在页面展示 AI 评分、风险提醒、下一步动作、节省分钟数和预估节省金额。当前结果写入已有内存 Workflow 日志；生产环境仍需把日志落到 Supabase 表。

## 直播 Workflow 日志仓储边界状态

当前直播 Workflow 日志仍未写入数据库，但已经完成仓储边界：

- 领域层有 `LiveWorkflowRunRepository`。
- 基础设施层有 `InMemoryLiveWorkflowRunRepository`。
- 路由和 Savings Engine 继续通过统一函数读取日志。
- 测试已验证仓储可以被注入，方便后续切换 Supabase/PostgreSQL。

下一步仍然是确认并执行 `docs/live-workflow-log-schema-proposal.md` 中的数据库表设计。

## CEO 日报 API 状态

当前已完成后端 CEO 日报底座：`GET /v1/ceo/daily-report`。

日报会输出：

- 今日经营一句话结论。
- 经营健康分。
- 今日 AI 节省金额。
- 预计月节省。
- 年度 ROI。
- 直播运营状态。
- 今日最高风险。
- 老板优先动作。
- AI 员工绩效说明。
- Savings Engine 和 Workflow 证据点。

当前还没有新增 Dashboard 页面。下一步应把 CEO 日报接入老板首页第一屏，让老板打开系统先看到“今天发生了什么、为什么、该做什么、省了多少钱”。

## 老板首页 CEO 日报接入状态

当前 `/dashboard` 已接入 CEO 日报 API：

- 第一屏展示今日经营结论。
- 显示今日 AI 节省金额和预计月节省。
- 显示最高风险和建议动作。
- 显示老板优先动作。
- 显示 Savings Engine 与 Workflow 证据点。
- 保留直播运营 Workflow 和 AI 员工绩效区。

这一步符合 V2 战略：老板打开系统不是先看聊天记录，而是先看“今天发生了什么、为什么、该做什么、省了多少钱”。

## CEO 日报数据可信状态

当前老板首页已经显示“真实 Workflow 数据 / 演示估算数据”状态。

判断规则：

- 如果直播 Workflow 有运行记录，CEO 日报返回 `real_workflow_logs`。
- 如果还没有运行记录，CEO 日报返回 `demo_estimate`。

这一步解决商家试用时的信任问题：页面会明确告诉老板当前节省金额是来自真实 Workflow 证据，还是接入前的演示估算。

## PostgreSQL 直播日志仓储预留状态

当前已经具备 PostgreSQL 版直播 Workflow 日志仓储实现，但默认仍使用内存仓储。

启用条件：

1. `LIVE_WORKFLOW_LOG_STORAGE=postgres`。
2. `DATABASE_URL` 已配置且可用。
3. Supabase 已执行 `live_workflow_runs` 表 migration。

目前第 3 步尚未执行，因此产品仍保持安全 fallback，不会误写不存在的生产表。






