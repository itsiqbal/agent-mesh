# ai-agent-kit

One canonical set of agent/skill/workflow definitions, installed for **Claude Code**,
**Google Antigravity**, and **opencode** at once — edit a role once, re-run `install.sh`,
and all three tools pick it up. This supersedes the two earlier, separately-maintained kits
(`antigravity-global-agent-kit` and `claude-code-review-agents`) — see "Migrating from the old
kits" below.

## What's in here

```
ai-agent-kit/
├── AGENTS.md              canonical rules content (installed to CLAUDE.md / GEMINI.md / AGENTS.md)
├── agents/<role>/
│   ├── PROMPT.md           shared system-prompt body (edit this for behavior changes)
│   ├── DESCRIPTION.txt     shared one-line description (edit this for routing/trigger changes)
│   ├── claude-code.md      generated: PROMPT.md + Claude Code frontmatter
│   ├── antigravity.md      generated: PROMPT.md + Antigravity frontmatter
│   └── opencode.md         generated: PROMPT.md + opencode frontmatter
├── skills/<name>/SKILL.md  shared skill files, copied verbatim to all three tools
├── workflows/<name>/
│   ├── BODY.md             shared workflow body
│   ├── claude-code.md       -> installed as a /slash command
│   ├── antigravity.md       -> installed as a /slash command
│   └── opencode.md          -> installed as a /slash command
├── install.sh
└── uninstall.sh
```

**14 agents**: architect, backend-engineer-java, backend-engineer-node, frontend-engineer,
database-engineer, devops-gcp, qa-test-engineer, code-reviewer, java-code-reviewer,
frontend-code-reviewer, system-design-reviewer, security-auditor, interview-coach,
interview-questioner.

**17 skills** covering Spring Boot, Node/Express, Next.js/React, relational/Mongo/Redis schema
design, REST API design, testing strategy, GCP deployment, code/system-design/security review
checklists, and interview prep for backend/frontend/system-design/devops tracks.

**6 workflows** (slash commands): `/new-feature`, `/code-review`, `/system-design-review`,
`/deploy-gcp`, `/interview-prep`, `/mock-interview`.

## Install

```bash
./install.sh                          # all three tools
./install.sh --only claude,opencode   # a subset
./install.sh --dry-run                # preview, no changes
```

This is a **global** install — it writes to your home directory (`~/.claude/`, `~/.gemini/`,
`~/.config/opencode/`), so every project on this machine picks it up. It's idempotent: re-run
it any time after editing the kit and it will just overwrite the kit-managed files.

Where things land:

| | Claude Code | Antigravity | opencode |
|---|---|---|---|
| Agents | `~/.claude/agents/<role>.md` | `~/.gemini/config/agents/<role>.md` | `~/.config/opencode/agents/<role>.md` |
| Skills | `~/.claude/skills/<name>/` | `~/.gemini/antigravity/skills/<name>/` | `~/.config/opencode/skills/<name>/` |
| Workflows | `~/.claude/commands/<name>.md` | `~/.gemini/antigravity/global_workflows/<name>.md` | `~/.config/opencode/command/<name>.md` |
| Rules | `~/.claude/CLAUDE.md` | `~/.gemini/GEMINI.md` | `~/.config/opencode/AGENTS.md` |

The rules file is injected as a marked block (`<!-- BEGIN ai-agent-kit -->` ... `<!-- END -->`)
so it won't clobber anything else you've already got in `CLAUDE.md`/`GEMINI.md`/`AGENTS.md` —
existing content is backed up to `<file>.pre-ai-agent-kit.bak` the first time the script touches
that file, and only the marked block is replaced on every subsequent run.

Note on opencode: it already auto-reads `~/.claude/skills/` as a fallback, so if you only
install the Claude Code target, opencode will still see the skills. The installer copies them
to `~/.config/opencode/skills/` explicitly too, so opencode works even if you skip Claude Code.

## Uninstall

```bash
./uninstall.sh
./uninstall.sh --only antigravity
```

Removes exactly the files this kit installed and strips the marked rules block back out —
nothing else in `CLAUDE.md`/`GEMINI.md`/`AGENTS.md` is touched.

## Editing an agent or skill

1. Edit `agents/<role>/PROMPT.md` (behavior) and/or `agents/<role>/DESCRIPTION.txt` (routing/trigger)
   — or a skill's `skills/<name>/SKILL.md`, or a workflow's `workflows/<name>/BODY.md`.
2. Re-run `python3 build_unified_kit.py` if you're working from the source repo (this
   regenerates the three per-tool variants from the shared body) — skip this step if you were
   only given this kit as a finished folder, and just edit `claude-code.md` / `antigravity.md` /
   `opencode.md` directly for each tool (they'll drift out of sync with each other, which is
   fine for a one-off tweak, just harder to keep consistent long-term).
3. Re-run `./install.sh`.

To add a brand-new agent: add an entry to `ROLES` (or `EXTRA_REVIEWERS`) in
`build_unified_kit.py`, drop the source `.md` in the antigravity-format `agents/` source
folder (or a Claude-Code-format one, for a role with no antigravity original), and re-run
the generator.

## Using the agents

Once installed, ask for a role by name and the tool routes to it as a subagent — e.g. "use the
architect agent to plan this" or "run code-reviewer on this diff." The `code-reviewer` agent
also supports a branch-diff mode: give it a source and target branch (e.g. "review
feature/checkout against release/2.4") and it'll `git diff <target>...<source>`, route changed
files to the right stack checklist, and report Blocking/Should-fix/Nit findings with concrete
fixes. `java-code-reviewer` and `frontend-code-reviewer` do the same branch-diff workflow with a
deeper, stack-specific checklist — use them for a Java-only or frontend-only repo, or when you
want closer scrutiny than the general reviewer on one part of the stack.

## Migrating from the old kits

If you installed either of the two earlier kits, uninstall them first to avoid duplicate/stale
agent definitions sitting alongside this one:

```bash
# from wherever you unzipped the old kits:
antigravity-global-kit/uninstall.sh
claude-code-review-agents/uninstall.sh
```

Then run this kit's `install.sh`. Everything from both old kits (all 12 original agents, all 17
skills, all 6 workflows, plus the 3 Claude-Code branch-diff reviewers) is carried forward here —
nothing is lost, it's just unified into one source that now also covers opencode.
