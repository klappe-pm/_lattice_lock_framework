# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.1.x   | :white_check_mark: |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability within the Lattice Lock Framework, please follow these steps:

1. **Do NOT create a public GitHub issue.** This allows us to assess the risk and create a fix before the vulnerability is made public.
2. Email our security team at security@lattice-lock.io
3. Include as much detail as possible:
   - Description of the vulnerability.
   - Steps to reproduce.
   - Potential impact.
   - Any proof-of-concept code (if safe to share privately).

## Responsible Disclosure

We are committed to working with researchers to verify and address vulnerabilities.

- We will acknowledge receipt of your report within 48 hours.
- We will provide regular updates on our progress.
- We aim to resolve critical issues within 14 days.
- We will credit you (if desired) in the changelog and release notes once the fix is public.

## Security Features

Lattice Lock includes several built-in security features:

- **Sheriff Static Analysis:** Scans for prohibited code patterns and potential security risks.
- **Dependency Scanning:** We use Snyk and dependabot to monitor dependencies.
- **Secret Detection:** Pre-commit hooks prevent accidental commit of API keys.

