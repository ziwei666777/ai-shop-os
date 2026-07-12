# AI Shop OS 架构说明

## 分层

```text
Frontend Next.js
Backend FastAPI
Application Use Cases
Domain Models
Infrastructure Repositories
Workflow Engine
Memory + Knowledge
MCP Tool Layer
External Commerce Platforms
```

## Sprint 1 边界

- 前端只通过 FastAPI 读取业务数据。
- 后端已支持 PostgreSQL 仓储；当 `DATABASE_URL` 仍是占位符时自动回退到内存仓储。
- 数据库 migration 已在 Supabase 项目中执行，核心结构和商家试用表已建立。
- AI Customer 不执行真实对话，不调用 LLM，不调用外部平台。

## 后续替换点

- `apps/api/app/infrastructure/repository_provider.py` 负责在 PostgreSQL 仓储和内存 fallback 之间切换。
- `apps/web/src/shared/api/client.ts` 后续可增加认证头和错误追踪。
- `knowledge_chunks.embedding` 后续由异步 Embedding Worker 写入。

## 商家试用版边界

- AI客服允许 FAQ、订单、物流类低风险自动回复。
- 退款、赔偿、投诉、差评和金额相关问题必须人工确认。
- Shopify 优先接入官方授权、Webhook 和 Admin API。
- 淘宝保留开放平台 Connector 边界，真实联调依赖应用密钥和权限。
- 商家修改、采纳、拒绝都会记录为 Learning Event。
- 试用数据权重为：客服问答修正 60%，售后决策样本 30%，KPI 10%。
