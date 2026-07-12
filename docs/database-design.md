# Sprint 1 数据库设计

当前数据库迁移位于：

```text
supabase/migrations/202607090001_sprint1_core_schema.sql
```

## 设计目标

- 支持多公司、多成员、多 AI 员工。
- Agent 不直接互相调用，后续通过 Workflow 协作。
- Knowledge 使用 pgvector 存储向量。
- Memory 明确分为 conversation、customer、business、company 四层。
- 所有关键行为可审批、可追踪、可审计。

## 核心表

- 身份与组织：`companies`、`users`、`company_members`
- AI 员工：`agents`、`agent_prompts`、`agent_tools`、`agent_kpis`
- 业务对象：`customers`、`products`、`orders`
- 会话客服：`conversations`、`messages`
- Knowledge/RAG：`knowledge_sources`、`knowledge_chunks`
- Memory：`memories`
- Workflow：`workflows`、`workflow_runs`、`workflow_steps`
- Approval：`approvals`
- Observable：`agent_logs`、`audit_logs`
- Dashboard：`daily_business_snapshots`
- 商家试用：`platform_connections`、`after_sale_cases`、`learning_events`、`agent_feedback_metrics`

## 约束

- 除 `companies` 外，业务表都包含 `company_id`。
- 所有表包含 `created_at` 和 `updated_at`。
- 所有核心表启用 RLS。
- migration 只建立结构，不写生产种子数据。
- 第二个 migration 补充 AI客服与 AI售后商家试用所需的数据采集表。
- 商家试用演示数据独立放在 `supabase/seed/202607100001_pilot_trial_data.sql`，需要试用时手动执行。
