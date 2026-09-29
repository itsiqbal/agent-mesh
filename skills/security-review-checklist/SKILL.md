---
name: security-review-checklist
description: Security review checklist covering authentication, authorization, input handling, secrets, and dependencies. Use before shipping anything that touches auth, user data, payments, or external input, or when asked to do a security review.
---
# Security Review Checklist

## AuthN/AuthZ
- Every endpoint checks authentication and the caller's authorization for the specific resource (not just "is logged in" — "is allowed to touch *this* record").
- Passwords hashed with bcrypt/argon2, never stored or logged in plaintext; tokens/sessions have a sane expiry.

## Input handling
- All external input validated and sanitized at the boundary; parameterized queries only (no string-built SQL); output-encode anything rendered back into HTML to prevent XSS.
- File uploads: validate type/size, store outside the web root or in object storage (GCS), never trust the client-provided filename or content-type.

## Secrets
- No secrets, keys, or credentials in source control, logs, or error messages; use env vars / GCP Secret Manager, and rotate anything that was ever accidentally committed.

## Dependencies
- Check for known-vulnerable dependencies (`npm audit`, OWASP Dependency-Check / Snyk) before adding new libraries and periodically thereafter.

## Transport & headers
- HTTPS everywhere; set standard security headers (CSP, X-Content-Type-Options, X-Frame-Options/frame-ancestors); set secure/HttpOnly/SameSite on cookies.

## Logging
- Log security-relevant events (auth failures, permission denials) without logging sensitive payloads (passwords, tokens, full card numbers, PII beyond what's needed).

## Output
- Report findings by severity with a concrete fix for each, don't just flag "this looks risky" without a remediation.
