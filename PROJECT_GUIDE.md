# AI Commerce OS - Codex Development Guide

## 一、项目定位

AI Commerce OS 不是 AI 客服，不是 ERP，也不是普通 SaaS。

目标是打造一个真正帮助中小电商企业工作的 AI 企业操作系统。

当前仅聚焦三个部门：

- AI Customer（客服）
- AI Operation（运营）
- AI AfterSale（售后）

最终目标：帮助企业减少 4 到 5 名员工，老板只负责审批。

## 二、当前开发原则

项目已经开发到 V0.x。

禁止：

- 推倒重来。
- 修改整体架构。
- 修改已确认的数据库设计。
- 重构目录结构。
- 引入大量新框架。

所有开发必须在当前项目基础上增量开发。

## 三、当前最高优先级

暂停增加新 Agent。

下一阶段重点：

1. Commerce Dataset
2. Replay Engine
3. Simulation Engine
4. Evaluation Engine
5. Training Center

当前不是继续堆功能，而是真正验证 AI 是否能够工作。

## 四、Commerce Dataset

建立标准电商数据集，所有 Agent 共用。

数据范围：

- Products
- Orders
- Customers
- Messages
- Refunds
- Reviews
- Inventory
- Coupons
- Advertisements
- Competitors
- Logistics
- Support Tickets

必须支持：

- CSV
- Excel
- JSON
- Import

## 五、Replay Engine

Replay Engine 是整个系统最重要的验证工具。

它读取历史真实订单、聊天和售后记录，让 AI 重新执行，再比较人工结果和 AI 结果。

输出指标：

- 准确率
- 满意度
- 响应时间
- 是否需要人工
- 采纳率
- 错误率

## 六、Simulation Engine

建立模拟客户，用于训练和压力测试。

模拟场景：

- 咨询
- 砍价
- 退款
- 投诉
- 物流
- 售后

长期目标：每天模拟 10000+ 客户。

## 七、Evaluation Engine

所有 Agent 必须评分。

核心指标：

- Response Time
- Accuracy
- Knowledge Coverage
- Customer Satisfaction
- Refund Success
- Conversion Rate
- Manual Rate

系统每天自动生成评估报告。

## 八、Training Center

老板或客服修改 AI 回复后，必须永久进入：

- Memory
- Knowledge
- Workflow

以后遇到相同问题，AI 必须优先使用老板经验。

## 九、Memory

所有 Agent 共用 Memory。

保存：

- 聊天
- 运营经验
- 售后经验
- 老板审批
- Prompt
- 企业 SOP
- 长期学习记录

## 十、Workflow

Agent 必须通过 Workflow 协作，不能互相硬编码直连。

示例：

```text
AI Customer
↓
发现大量客户咨询尺寸
↓
AI Operation
↓
判断详情页缺少尺寸说明
↓
生成新的详情页建议
↓
老板审批
↓
上线
↓
Memory 学习
```

## 十一、Github 优先研究

后续开发前优先研究成熟开源方案，避免重复造轮子。

Agent：

- LangGraph
- OpenAI Agents SDK
- CrewAI
- Mastra

Commerce：

- Medusa
- Saleor
- Vendure

RAG：

- FastGPT
- Dify
- Ragflow

Memory：

- Mem0
- LangMem
- Zep

Workflow：

- LangGraph
- n8n
- Temporal

Browser：

- Browser Use
- Playwright
- Skyvern

ERP：

- ERPNext
- Odoo

CRM：

- Twenty CRM

Database：

- Supabase
- PostgreSQL
- pgvector

Monitoring：

- Langfuse

Evaluation：

- DeepEval
- Promptfoo
- Ragas

MCP：

- Browser
- Filesystem
- GitHub
- Playwright
- Postgres
- Google
- Notion

未来平台：

- 淘宝
- 1688
- Shopify
- Amazon
- TikTok

## 十二、不要重复开发

不要自己开发：

- 订单系统
- 商品系统
- 库存系统
- 支付系统
- 物流系统

优先复用成熟开源项目和官方平台 API。

## 十三、真正需要自己开发

系统真正需要自研的是：

- Workflow
- Memory
- Knowledge
- Replay
- Simulation
- Evaluation
- Training
- Boss Dashboard
- Agent Communication
- Enterprise SOP

## 十四、开发流程

每次开发必须按顺序执行：

1. 查看当前代码。
2. 分析是否已有模块。
3. 分析是否有成熟开源方案可复用。
4. 决定 Fork、封装 API，还是自研。
5. 只完成当前模块。
6. 更新 `PROJECT_STATE.md`。
7. 更新 `CHANGELOG.md`。
8. 如有新想法但不开发，写入 `IDEAS.md`。

## 十五、长期路线

V1：

- AI Customer
- AI Operation
- AI AfterSale

V2：

- 跨境电商

V3：

- 供应链

V4：

- 物流

V5：

- Enterprise AI Operating System

## 十六、最终目标

打造一套真正能够帮助企业赚钱、降本、提效的 AI 企业操作系统，而不是一个简单的 AI 工具。
