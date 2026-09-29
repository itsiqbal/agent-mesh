---
description: Run a live mock technical interview session.
---

# /mock-interview
Run a live mock technical interview session.

## Steps
1. Ask the user which track (backend, frontend, system design, devops, or behavioral) and level (junior/mid/senior) they want, unless they already said.
2. Hand off to the `interview-questioner` subagent for the session itself.
3. Ask exactly one question at a time; wait for the user's answer before giving feedback or moving on — never dump the next question or the model answer early.
4. After each answer, give brief, honest feedback (what was solid, what was missing) referencing the matching interview-prep-* skill, then ask if they want to continue.
5. At the end of the session (or whenever the user stops), give a short summary: strengths, gaps to focus on, and 2-3 concrete next study steps. Suggest the `interview-coach` agent or `/interview-prep` for building out a fuller study plan around those gaps.
