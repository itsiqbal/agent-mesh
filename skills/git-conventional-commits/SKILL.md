---
name: git-conventional-commits
description: Git commit message and pull request conventions. Use whenever committing code or opening a pull request.
---
# Git & Commit Conventions

## Commit messages
- Conventional commits format: `type(scope): summary`, types: feat, fix, refactor, test, docs, chore, perf, ci.
- Imperative mood, under ~72 chars for the summary line; body explains *why*, not a restatement of the diff.

## PRs
- One logical change per PR; if a task naturally splits into independent pieces, say so and propose separate PRs rather than bundling everything.
- PR description: what changed, why, how it was tested, and any follow-up work intentionally left out of scope.

## Branching
- Feature branches off the main integration branch, named `type/short-description` (e.g. `feat/order-refunds`).

## Safety
- Never `git push --force` to a shared branch, and never rewrite already-shared history, without explicit confirmation from the user.
