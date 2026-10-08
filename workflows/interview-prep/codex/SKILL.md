---
name: interview-prep
description: "Build a study plan and drill concepts for an upcoming interview (as opposed to /mock-interview, which runs a live Q&A session)."
---

# $interview-prep
Build a study plan and drill concepts for an upcoming interview (as opposed to $mock-interview, which runs a live Q&A session).

## Steps
1. Ask for the target role/level/company if not given (e.g. "mid-level backend, fintech company, interview in 3 weeks") — proceed with reasonable defaults if the user doesn't know yet.
2. Hand off to the `interview-coach` subagent.
3. Identify which tracks are relevant (backend, frontend, system design, devops) and pull the topic checklist from the matching interview-prep-* skill(s).
4. Produce a prioritized, time-boxed study plan (what to review first, given the timeline), not just an undifferentiated topic dump.
5. Offer to explain any concept in depth, review the user's own answers/resume/project descriptions, or hand off to `$mock-interview` for live practice once they've studied the material.
