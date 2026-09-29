---
description: Review the current uncommitted changes (or a specified PR/branch) for correctness, style, and risk.
---

# /code-review
Review the current uncommitted changes (or a specified PR/branch) for correctness, style, and risk.

## Steps
1. Get the diff (`git diff` for uncommitted changes, or fetch the PR diff if a PR number/URL is given).
2. Hand off to the `code-reviewer` subagent to do the review itself, using the code-review-checklist skill plus the relevant stack skill (spring-boot-api-conventions, node-express-api-conventions, nextjs-react-conventions) and the project's own linter config.
3. If the diff touches auth, data access, external input, or anything else security-sensitive, also run `security-auditor`.
4. If the diff lacks a test for the new/changed behavior, route that specifically to `qa-test-engineer` rather than having the reviewer write it.
5. If the diff is a large architectural or cross-service change rather than a normal PR, suggest `/system-design-review` instead of (or in addition to) this workflow.
6. Report findings grouped by severity (blocking / should-fix / nit), each with a concrete suggested fix — don't just flag issues without a fix.
