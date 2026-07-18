# OpenAI Codex for Open Source Application Draft

Official form: <https://openai.com/form/codex-for-oss/>

Use this file as the copy source when submitting AI Shop OS after the GitHub repository is public.

## Required Fields

### GitHub Username

TODO: your public GitHub username

### GitHub Repository URL

TODO: public GitHub repository URL

### Maintainer Role

Primary maintainer

Suggested answer:

```text
I am the project owner and primary maintainer of AI Shop OS. I define the product strategy, maintain the roadmap, review changes, run tests, prepare releases, and use Codex to turn ecommerce operations research into auditable open-source workflows.
```

## Why This Repository Qualifies

OpenAI limit: 500 characters.

Suggested English answer:

```text
AI Shop OS is an open-source AI Employee OS prototype for ecommerce teams. It focuses on real operations workflows: livestream checks, CEO daily reports, savings/ROI proof, refund collaboration, approvals, and warehouse evidence. The project is important because many merchants need auditable AI work, not another chat widget.
```

Suggested Chinese answer:

```text
AI Shop OS 是面向电商团队的开源 AI Employee OS 原型，重点不是客服聊天，而是直播运营巡检、老板日报、省钱/ROI 证据、退款协同、审批和仓库通知闭环。它服务于中小商家真实降本场景，有明确工作流和可审计证据链。
```

## Interest Selection

Recommended selections:

- API credits for my project.
- Codex Security, if OpenAI allows security review for the public repository.

## OpenAI Organization ID

TODO: find this in your OpenAI account settings.

## How API Credits Will Be Used

OpenAI limit: 500 characters.

Suggested English answer:

```text
We will use API credits for open-source maintainer workflows: generating and reviewing workflow tests, checking production readiness gates, summarizing issues, drafting release notes, and building safe examples for ecommerce operations automation. Credits will not be used for private merchant data without authorization.
```

Suggested Chinese answer:

```text
API 额度将用于开源维护工作：生成和审查 Workflow 测试、检查生产证据链 readiness、总结 issues、生成 release notes、构建安全的电商运营自动化示例。不会在未经授权的真实商家数据上使用。
```

## Anything Else We Should Know

OpenAI limit: 500 characters.

Suggested English answer:

```text
The project has a strict safety boundary: no unauthorized scraping, no automatic refunds or ad-budget changes without approvals, and no fake production savings logs. The current P0 work is to make AI operations evidence auditable through PostgreSQL workflow logs, after-sale decisions, warehouse notifications, and CEO reports.
```

Suggested Chinese answer:

```text
项目有明确安全边界：不做非授权抓取，不绕过审批自动退款/赔偿/调广告，不把演示数据伪装成生产省钱证据。当前 P0 是用 PostgreSQL 工作流日志、售后决策、仓库通知和老板日报补齐真实证据链。
```

## Current Evidence To Mention In Issues Or README

- Latest local backend verification: 87 passed across `apps/api/tests`.
- Strategy audit endpoint: `GET /v1/strategy/audit`.
- Production readiness endpoint: `GET /health/ready`.
- Daily operations entrypoint: `POST /v1/daily-operations/run` and `npm run api:daily-operations`.
- Production guard blocks fake daily operation logs unless `evidence_chain_ready=true`.

## Final Submission Checklist

- Public GitHub profile is visible.
- Repository is public.
- Repository has README, license, contributing guide, security policy, code of conduct, issue templates, PR template, and CI.
- Repository does not contain secrets or private merchant data.
- Application answers are concise and honest.