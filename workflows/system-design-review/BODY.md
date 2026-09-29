# /system-design-review
Review a system design document or architecture proposal.

## Steps
1. Read the design doc / proposal (or ask the user to paste it / point to the file if it isn't already in context).
2. Hand off to the `system-design-reviewer` subagent.
3. Work through the system-design-review-checklist skill: requirements, scale/capacity, reliability, consistency, trade-offs, security/operability.
4. Separate findings into "must address before building" vs "worth discussing, not blocking".
5. Propose concrete alternatives for anything flagged as a problem, not just criticism.
6. If the proposal is actually a plan for a feature that's about to be built (not a standalone design doc), suggest folding the findings back into the `architect` agent's implementation plan before work starts.
