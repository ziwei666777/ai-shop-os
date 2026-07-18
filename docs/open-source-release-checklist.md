# Open Source Release Checklist

This checklist prepares AI Shop OS for a public GitHub release and for the OpenAI Codex for Open Source application.

Official OpenAI application page: <https://openai.com/form/codex-for-oss/>

## OpenAI Criteria To Satisfy

OpenAI asks for:

- Public GitHub username.
- Public GitHub repository URL.
- Maintainer role: primary maintainer or core maintainer.
- Why the repository qualifies, including usage, adoption, or ecosystem importance.
- OpenAI Organization ID.
- How API credits will support open-source coding, review, maintainer automation, release workflows, or core OSS work.

OpenAI says applications are reviewed on a rolling basis and selected maintainers may receive six months of ChatGPT Pro, conditional Codex Security access, and API credits.

## Local Repository Status

Completed in this preparation pass:

- Rewrote `README.md` for public open-source reviewers.
- Added `LICENSE`.
- Added `CONTRIBUTING.md`.
- Added `SECURITY.md`.
- Added `CODE_OF_CONDUCT.md`.
- Added GitHub issue and pull request templates.
- Added a GitHub Actions CI workflow for API evidence-chain tests.
- Added an OpenAI application draft.

Still required outside local code edits:

1. Create or choose a GitHub repository.
2. Push this project to GitHub.
3. Set the repository visibility to public.
4. Set the maintainer GitHub profile visibility to public.
5. Fill in the OpenAI Organization ID.
6. Submit the application at the official OpenAI form.

## Suggested Public Repository Description

AI Employee OS for ecommerce teams: livestream operation workflows, CEO daily reports, after-sale collaboration, warehouse evidence, and savings/ROI proof chains.

## Suggested GitHub Topics

```text
ai-agents ecommerce fastapi nextjs workflow-automation livestream-commerce operations ai-employee-os savings-engine open-source
```

## Before First Public Push

- Confirm `.env`, `.env.local`, `.venv`, `node_modules`, `.next`, logs, and real credentials are ignored.
- Search for secrets before publishing.
- Remove any private customer data or merchant records.
- Keep demo data clearly labeled as demo data.
- Confirm `README.md` explains production readiness boundaries.

## First Release Recommendation

Create a first public prerelease tag:

```text
v0.1.0-oss-preview
```

Release title:

```text
AI Shop OS OSS Preview: AI Employee OS evidence-chain prototype
```

Release notes should highlight:

- AI Live Operation Agent workflows.
- CEO daily report.
- Savings and ROI proof chain.
- Refund collaboration and after-sale decision evidence.
- Production readiness gate for real data evidence.