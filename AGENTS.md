# Global Engineering Rules

These are read automatically by every tool this kit installs for: opencode and Claude Code
read this file directly (as `AGENTS.md`, at your project root or your global config
directory); Antigravity reads the same content from its own `GEMINI.md` slot. One file,
edited once, reaches all three.

## Stack
- Backend services: Java 21 + Spring Boot (core domain services), Node.js + TypeScript + Express/NestJS (BFFs, lightweight/glue services)
- Frontend: Next.js (App Router) + React + TypeScript, Tailwind CSS
- Data: PostgreSQL and MySQL (primary relational stores), MongoDB (document/flexible-schema use cases), Redis (caching, sessions, rate limiting)
- Infra: Google Cloud Platform — Cloud Run / GKE, Cloud SQL, Memorystore, Artifact Registry, Cloud Build, Secret Manager, Terraform

## How to work
1. For anything beyond a trivial fix, use the `architect` agent first to produce a short implementation plan before writing code.
2. Delegate stack-specific implementation to the matching agent: `backend-engineer-java`, `backend-engineer-node`, `frontend-engineer`, `database-engineer`, `devops-gcp`.
3. Before marking a task done, run `qa-test-engineer`, and for anything touching auth, payments, or personal data, also run `security-auditor`.
4. For a code review, use `code-reviewer` (general quality, including branch-vs-release-branch diff review) plus `java-code-reviewer` or `frontend-code-reviewer` for a deeper stack-specific pass, and `security-auditor` if the diff is security-sensitive. For a design doc, RFC, or architecture proposal, use `system-design-reviewer` instead.
5. Prefer the project's own existing conventions (linters, folder structure, naming) over these defaults when they conflict — read a few existing files before generating new ones.

## Interview prep & practice
These are for your own learning, separate from any production codebase:
- `interview-coach` — study plans, concept explanations, resume/answer review, for Backend, Frontend, System Design, and DevOps tracks.
- `interview-questioner` — runs a live mock interview: one question at a time, waits for your answer, then gives feedback.
Just ask for either by name — e.g. "use the interview-questioner agent for a system design mock interview." The `/interview-prep` and `/mock-interview` slash commands wrap these two flows.

## Non-negotiables
- Never commit secrets, API keys, or .env files. Use environment variables or GCP Secret Manager.
- Never run destructive commands (DROP TABLE, rm -rf, git push --force, terraform destroy, deleting cloud resources) without explicit confirmation.
- Every new endpoint or business-logic function needs at least one automated test.
- Every database schema change needs a reversible migration (Flyway/Liquibase for Java, Prisma/knex/node-pg-migrate for Node) — never a manual ALTER against a shared environment.
- Use conventional commits (feat:, fix:, chore:, refactor:, test:, docs:) for all commit messages.
- Keep PRs/diffs small and focused; if a task naturally splits into independent pieces, say so instead of doing everything in one giant change.

## Code style
- TypeScript: strict mode on, no `any` unless justified in a comment, explicit return types on exported functions.
- Java: standard Java conventions, constructor injection over field injection, DTOs at API boundaries (never expose JPA entities directly).
- React: functional components + hooks only, colocate component/test/styles, Server Components by default in the Next.js App Router, "use client" only when interactivity requires it.
- SQL: explicit column lists (no SELECT *), add an index for any new query pattern you introduce.

## Communication
- When a request is ambiguous, state the assumption you're making and proceed, rather than stalling on a clarifying question, unless the ambiguity changes the architecture.
- Summarize what changed and why at the end of a task, not a play-by-play of every file touched.
