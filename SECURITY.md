# Security Policy

## Supported Version

AI Shop OS is currently a pre-1.0 prototype. Security fixes should target the main branch unless a maintained release branch is created later.

## Reporting a Vulnerability

Please do not open public issues for vulnerabilities that expose secrets, customer data, platform credentials, or unauthorized operational control.

After the repository is public, report security issues through GitHub private vulnerability reporting if enabled. If it is not enabled yet, contact the project owner through the public maintainer profile and provide only a high-level description until a private channel is established.

## Security Boundaries

AI Shop OS must not:

- Store real platform secrets in source control.
- Commit `.env`, `.env.local`, virtual environments, build artifacts, or logs.
- Automatically refund, compensate, change ad budgets, or alter platform state without explicit approval boundaries.
- Scrape or control ecommerce platforms without official authorization.
- Present demo savings as production evidence.

Production readiness requires `/health/ready` to report `evidence_chain_ready=true` before production jobs write real evidence logs.