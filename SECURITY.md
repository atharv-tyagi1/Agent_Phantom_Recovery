# Security Policy

## Reporting Vulnerabilities

The Agent Phantom Recovery team takes security seriously. If you discover a security vulnerability, please **DO NOT** open a public GitHub issue.

Instead, please report vulnerabilities privately by emailing the maintainers or submitting a private disclosure.

### What to Include in a Report:
- A detailed description of the vulnerability.
- Steps to reproduce the issue.
- Impact analysis and potential exploit scenarios.
- Suggested remediation steps if available.

---

## Security Safeguards Implemented

Agent Phantom Recovery enforces strict enterprise security controls:

1. **OAuth PKCE & Signed HMAC State**: Prevents OAuth replay attacks and CSRF.
2. **Secret Redactor (`SecretMasker`)**: Automatically sanitizes API keys, JWT tokens, and passwords from logs, traces, and DB payloads (`***REDACTED***`).
3. **Fernet AES-256 Encryption**: Encrypts OAuth user tokens at rest in PostgreSQL.
4. **Nonce-Based Content Security Policy (CSP)**: Next.js Edge middleware enforces dynamic base64 script nonces (`script-src 'self' 'nonce-{nonce}' 'strict-dynamic'`).
5. **Rate Limiting**: Redis sliding-window rate limiter prevents API abuse.
6. **Multi-Tenant RBAC**: Enforces strict workspace access boundaries (`OWNER` > `ADMIN` > `MEMBER`).
