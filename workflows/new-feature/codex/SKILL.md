---
name: new-feature
description: "A repeatable flow for building a new feature end-to-end."
---

# $new-feature
A repeatable flow for building a new feature end-to-end.

## Steps
1. Ask the `architect` subagent for a short implementation plan (approach, affected services, schema changes, task breakdown) before writing any code.
2. Confirm the plan with the user if it involves a new external dependency, a schema change, or touches more than one service.
3. Implement the backend piece via `backend-engineer-java` or `backend-engineer-node` (whichever the plan calls for), and the frontend piece via `frontend-engineer`, delegating database changes to `database-engineer`.
4. Write tests alongside the implementation (see the testing-strategy skill) — don't defer all testing to the end.
5. Run `security-auditor` if the feature touches auth, payments, or user-submitted data.
6. Run `qa-test-engineer` to confirm test coverage and run the full suite.
7. Summarize what changed, how it was tested, and any follow-up work left out of scope.
