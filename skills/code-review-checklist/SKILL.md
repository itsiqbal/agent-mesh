---
name: code-review-checklist
description: General code-quality review checklist — correctness, readability, maintainability, design, and performance — independent of language. Use when reviewing any diff, PR, or code file, alongside the stack-specific convention skill.
---
# Code Review Checklist

## Correctness
- Does the code do what it claims? Are edge cases (empty input, null, concurrent access, network failure) handled?
- Any off-by-one errors, incorrect boundary conditions, or unhandled exceptions?

## Readability
- Names describe intent, not implementation; functions do one thing; nesting depth is reasonable.
- No dead code, commented-out blocks, or leftover debug statements.

## Maintainability & design
- Does the change fit the existing architecture, or does it introduce a parallel/inconsistent pattern?
- Is duplication being introduced that should be a shared function/module?
- Are dependencies/coupling reasonable — does this class/function know more than it needs to?

## Error handling
- Errors are caught at the right layer and surfaced meaningfully, not swallowed silently or logged-and-ignored.

## Performance
- Any obvious N+1 queries, unnecessary loops over large collections, or unbounded memory growth introduced?

## Tests
- Is the change covered by a test that would fail if the change were reverted? If not, flag it and suggest routing to qa-test-engineer.

## How to give feedback
- Group findings as Blocking / Should-fix / Nit. Every finding gets a concrete suggested fix, not just a description of the problem.
- Call out good patterns too, briefly — a review isn't only a list of problems.
