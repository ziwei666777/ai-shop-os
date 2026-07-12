# Supabase 配置说明

## 当前状态

- Supabase Project Ref：`lulxdtssayycqohbfedp`
- Project URL：`https://lulxdtssayycqohbfedp.supabase.co`
- 已执行 migration：
  - `supabase/migrations/202607090001_sprint1_core_schema.sql`
  - `supabase/migrations/202607090002_customer_after_sale_pilot.sql`
- 已验证核心表存在：`companies`、`agents`、`messages`、`after_sale_cases`、`learning_events`、`agent_feedback_metrics`、`platform_connections`

## 本地环境变量

前端配置文件：

```text
apps/web/.env.local
```

后端配置文件：

```text
apps/api/.env
```

后端当前 `DATABASE_URL` 仍保留 `YOUR_DATABASE_PASSWORD` 占位符。只要密码未替换，FastAPI 会自动使用内存仓储，保证本地页面和测试继续可运行。

## 登录态保护

前端使用 Supabase SSR Auth：

- 浏览器登录客户端：`apps/web/src/shared/api/supabase-client.ts`
- 服务端客户端：`apps/web/src/shared/api/supabase-server.ts`
- 路由保护：`apps/web/middleware.ts`

当前保护页面：

```text
/dashboard
/ai-employees
/orders
/products
/customers
/knowledge-base
/workflow
/analytics
/settings
/profile
```

未登录访问以上页面会跳转到 `/login`。如果本地没有配置 Supabase URL 和 anon key，middleware 会自动放行，避免阻塞本地开发。

## 启用真实数据库

在 Supabase Dashboard 进入：

```text
Project Settings -> Database -> Connection string
```

复制 PostgreSQL 连接串，把 `apps/api/.env` 中的 `DATABASE_URL` 替换为真实连接串。

重要边界：

- 不要把 `service_role` key 写入前端。
- 当前本地只需要数据库连接串，不需要暴露 Supabase 高权限密钥。
- 如果后续要做服务端绕过 RLS 的管理任务，再单独增加后端专用密钥配置。

## 商家试用种子数据

试用数据文件：

```text
supabase/seed/202607100001_pilot_trial_data.sql
```

用途：

- 初始化 AI Boss、AI Customer、AI After-sale。
- 初始化 Shopify 与淘宝连接状态占位。
- 初始化客服消息、售后 case、Dashboard 指标和 KPI 权重。

执行方式：

1. 打开 Supabase SQL Editor。
2. 粘贴 `supabase/seed/202607100001_pilot_trial_data.sql`。
3. 点击 Run。

这不是生产 migration，只用于演示和早期商家试用。
