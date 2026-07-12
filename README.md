# AI Shop OS

AI Shop OS 是一套 AI 电商员工操作系统，让老板管理多个可协作、可审批、可追踪的 AI 员工。

## 当前 Sprint

Sprint 1 只完成基础架构、数据库、登录、Dashboard 和 AI Employee 框架。

当前已补充 AI客服与 AI售后商家试用版工作台。

暂不实现复杂 RAG、多轮 Agent 自主决策或非授权外部平台抓取。

## Monorepo 结构

```text
apps/web              Next.js 前端
apps/api              FastAPI 后端
packages/shared       前后端共享常量和类型
supabase/migrations   PostgreSQL + pgvector 迁移
docs                  架构和数据库文档
```

## 本地运行

要求：

```text
Node.js 18.17 或更高版本
npm 9 或更高版本
Python 3.11 或更高版本
```

前端：

```bash
npm install
npm run dev:web
```

后端：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r apps/api/requirements.txt
npm run api:dev
```

默认访问：

```text
Web: http://localhost:3000
API: http://localhost:8000
```

## 商家试用入口

```text
/ai-employees/ai-customer/workbench
/ai-employees/ai-after-sale/workbench
/settings/integrations
/settings/data-collection
```

## Supabase

已执行数据库结构 migration，当前项目连接说明见：

```text
docs/supabase-setup.md
```

模板复用与安全审计见：

```text
docs/template-audit.md
```

后端 `DATABASE_URL` 未填真实数据库密码前，会自动使用内存 fallback，保证本地开发和页面预览不被阻塞。

商家试用演示数据位于：

```text
supabase/seed/202607100001_pilot_trial_data.sql
```

## 核心原则

- Everything is Agent
- Everything is Workflow
- Everything is Memory
- Everything is Knowledge
- Everything is Tool
- Everything is Observable
- Everything is Approval

## 长期维护文件

后续 Codex 开发必须优先阅读：

```text
PROJECT_GUIDE.md   项目总指导
PROJECT_STATE.md   当前开发状态
NEXT_TASK.md       下一步唯一开发任务
CHANGELOG.md       每次开发记录
IDEAS.md           暂不开发的新想法
```
