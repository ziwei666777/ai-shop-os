# AI Shop OS

AI Shop OS is an open-source prototype for an **AI Employee OS for ecommerce teams**. It is not another AI customer-service chat widget. The goal is to turn repeatable ecommerce operations into auditable workflows that can reduce manual work, expose operational risk, and calculate how much money the AI team saved today.

The current product strategy focuses on Chinese ecommerce merchants and the highest-cost daily workflow: **AI Live Operation Agent** for livestream commerce, supported by CEO daily reports, after-sale collaboration, warehouse notifications, and a Savings Engine.

## Why This Exists

Many ecommerce teams still need people to manually check livestream inventory, coupons, pricing, scripts, product order, refund risk, warehouse follow-up, daily sales, ad spend, and after-sale costs. AI Shop OS explores a different product shape:

- Not chat first, workflow first.
- Not more pages, more complete operating loops.
- Not more agents, better agent collaboration.
- Not vague automation, measurable saved time and saved money.

The long-term goal is to help a 20-person ecommerce operation run with a smaller team by giving owners AI employees that proactively work, escalate decisions, and leave evidence.

## Current Scope

P0 capabilities currently implemented or in progress:

- AI Live Operation Agent: pre-live checks, live metric scans, post-live reviews, workflow logs, and savings evidence.
- CEO Agent: daily report with money saved, risk, priority actions, AI employee performance, and proof points.
- Savings Engine and ROI Engine: estimates saved minutes, saved money, monthly savings, and annual ROI.
- Refund collaboration workflow: customer issue -> after-sale decision -> boss approval -> warehouse notification -> Savings -> CEO daily report.
- Production readiness gate: blocks fake production logs until database tables, PostgreSQL storage modes, WMS/ERP sender, and real credentials are ready.

The project intentionally avoids new customer-service chat pages, generic prompt pages, unrelated dashboards, and unauthorized scraping of ecommerce platforms.

## Architecture

```text
apps/web              Next.js ecommerce owner console
apps/api              FastAPI backend and workflow engines
packages/shared       shared constants and types
supabase/migrations   PostgreSQL/Supabase migrations
docs                  product, workflow, deployment, and operating docs
```

Core backend APIs include:

```text
GET  /health/ready
GET  /v1/strategy/audit
GET  /v1/ceo/daily-report
GET  /v1/savings/summary
POST /v1/daily-operations/run
POST /v1/live-operations/pre-live-check
POST /v1/live-operations/live-metric-scan
POST /v1/live-operations/post-live-review
POST /v1/workflows/refund-collaboration/run
POST /v1/approvals/{approval_id}/decision
POST /v1/warehouse-notifications/dispatch
```

## Local Development

Requirements:

```text
Node.js 18.17+
npm 9+
Python 3.11+
```

Install frontend dependencies:

```bash
npm install
```

Run the web app:

```bash
npm run dev:web
```

Run the API:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r apps/api/requirements.txt
npm run api:dev
```

Default local URLs:

```text
Web: http://localhost:3000
API: http://localhost:8000
```

## Validation

Run the full API test suite:

```bash
npm run api:test
```

Run the current core evidence-chain tests:

```bash
python -m pytest \
  apps/api/tests/test_refund_collaboration_workflow.py \
  apps/api/tests/test_strategy_audit.py \
  apps/api/tests/test_live_operations_and_savings.py \
  apps/api/tests/test_daily_operations_job.py \
  apps/api/tests/test_ceo_daily_report.py \
  apps/api/tests/test_production_bootstrap.py \
  apps/api/tests/test_health.py
```

The latest local backend verification is `87 passed` across `apps/api/tests`.

## Production Evidence Chain

AI Shop OS separates demo-safe local behavior from production evidence. In production mode, daily AI work should not write fake savings logs unless the evidence chain is ready.

Production readiness expects:

- `DATABASE_URL` configured for Supabase/PostgreSQL.
- Migrations executed for `live_workflow_runs`, `approval_records`, `after_sale_decision_outcomes`, `warehouse_notifications`, and `ceo_daily_report_snapshots`.
- Storage modes set to PostgreSQL for live workflow logs, approval records, after-sale decisions, and CEO report snapshots.
- `WAREHOUSE_NOTIFICATION_DELIVERY_MODE=http_api` with real WMS/ERP URL and API key.
- `/health/ready` returning `evidence_chain_ready=true`.

See `docs/production-deployment.md` and `NEXT_TASK.md` for the current production checklist.

## Open Source Status

This repository is being prepared for public open-source release and for the OpenAI **Codex for Open Source** maintainer-support program. See:

- `docs/open-source-release-checklist.md`
- `docs/openai-codex-for-open-source-application.md`

OpenAI's official application page says selected maintainers may receive six months of ChatGPT Pro, Codex Security access, and API credits for qualifying open-source maintenance work: <https://openai.com/form/codex-for-oss/>

## Contributing

Contributions are welcome after the repository is made public. Please read `CONTRIBUTING.md`, `SECURITY.md`, and `CODE_OF_CONDUCT.md` first.

Strategic rule for every contribution:

1. Which human role does this replace or reduce?
2. How much time does it save per day?
3. How much labor does it save per month?
4. Why would a business owner pay for it?
5. Can it enter a real workflow and leave evidence?
6. Can it calculate saved money?

If the answer is unclear, the feature should not be built yet.

## License

MIT License. See `LICENSE`.