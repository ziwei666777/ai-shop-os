# Contributing to AI Shop OS

Thank you for your interest in AI Shop OS. This project is being developed as an AI Employee OS for ecommerce operations, not as a traditional AI customer-service SaaS.

## Product Direction

Before proposing a feature, answer these six questions:

1. Which human role does this replace or reduce?
2. How much time does it save per day?
3. How much labor does it save per month?
4. Why would a business owner pay for it?
5. Can it enter a real workflow and leave evidence?
6. Can it calculate saved money?

If a proposal cannot answer those questions, it is probably out of scope for now.

## What Is In Scope

- AI Live Operation Agent workflows.
- CEO daily reports with proof points.
- Savings and ROI calculations backed by workflow evidence.
- Refund collaboration, after-sale decisions, approval records, and warehouse/WMS notification evidence.
- Production readiness gates that prevent fake production logs.
- Tests and docs that make the workflow evidence chain clearer.

## What Is Out Of Scope

- New generic AI customer-service chat pages.
- New prompt libraries or unrelated knowledge-base pages.
- Decorative dashboards that do not change a real workflow.
- Unauthorized scraping or control of ecommerce platforms.
- Automatic refund, compensation, ad spend, or budget changes without explicit approval boundaries.

## Development Setup

```bash
npm install
python -m venv .venv
.venv\Scripts\activate
pip install -r apps/api/requirements.txt
```

Run the API tests:

```bash
npm run api:test
```

Run the web checks when frontend code changes:

```bash
npm run lint:web
npm run typecheck:web
npm run build:web
```

## Pull Request Expectations

A good pull request should include:

- The role replaced or reduced.
- The expected time saved.
- The workflow evidence produced.
- Tests for risky behavior.
- Documentation updates when behavior or setup changes.

Keep changes small and focused. Do not refactor unrelated modules while implementing a product workflow.