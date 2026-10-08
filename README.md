# ai-agent-kit

One canonical set of agent/skill/workflow definitions for **Claude Code**,
**Google Antigravity**, **opencode**, and **Codex** — edit a role once, re-run `install.sh`,
and the selected tools pick it up. Codex is initially opt-in. This supersedes the two earlier, separately-maintained kits
(`antigravity-global-agent-kit` and `claude-code-review-agents`) — see "Migrating from the old
kits" below.

## What's in here

```
ai-agent-kit/
├── AGENTS.md              canonical rules content (installed to CLAUDE.md / GEMINI.md / AGENTS.md)
├── agents/<role>/
│   ├── PROMPT.md           shared system-prompt body (edit this for behavior changes)
│   ├── DESCRIPTION.txt     shared one-line description (edit this for routing/trigger changes)
│   ├── metadata.json       adapter settings, skill associations, and Codex permission intent
│   ├── claude-code.md      generated: PROMPT.md + Claude Code frontmatter
│   ├── antigravity.md      generated: PROMPT.md + Antigravity frontmatter
│   ├── opencode.md         generated: PROMPT.md + opencode frontmatter
│   └── codex.toml          generated: native Codex custom agent
├── skills/<name>/SKILL.md  shared skill files, copied verbatim to selected tools
├── workflows/<name>/
│   ├── BODY.md             shared workflow body
│   ├── metadata.json       adapter settings and workflow description
│   ├── claude-code.md       -> installed as a /slash command
│   ├── antigravity.md       -> installed as a /slash command
│   ├── opencode.md          -> installed as a /slash command
│   └── codex/              -> generated explicit workflow skill with agents/openai.yaml
├── scripts/build_kit.py    deterministic generator for all four tools
├── scripts/codex_install.py Codex installation and ownership tracking
├── tests/                 generator and isolated installer tests
├── install.sh
└── uninstall.sh
```

**14 agents**: architect, backend-engineer-java, backend-engineer-node, frontend-engineer,
database-engineer, devops-gcp, qa-test-engineer, code-reviewer, java-code-reviewer,
frontend-code-reviewer, system-design-reviewer, security-auditor, interview-coach,
interview-questioner.

**18 skills** covering Spring Boot, Node/Express, Next.js/React, relational/Mongo/Redis schema
design, REST API design, testing strategy, GCP deployment, code/system-design/security review
checklists, JSON localization editing, and interview prep for backend/frontend/system-design/devops tracks.

`json-localization-editor` reviews and edits user-facing text in JSON locale and content
files. It includes extraction and validation helpers, uses portable skill-relative paths,
and preserves JSON structure, placeholders, and technical values. This is the imported,
renamed version of the global Claude skill `json-localization-review`; the original global
copy is left in place. Invoke it by name in any supported tool, or as
`$json-localization-editor` in Codex. It edits and validates by default and reports
suggestions when explicitly asked for a review only.

**6 workflows**: `/new-feature`, `/code-review`, `/system-design-review`,
`/deploy-gcp`, `/interview-prep`, `/mock-interview` in existing tools; Codex exposes
the same names as explicitly invoked skills such as `$new-feature`.

## Install

```bash
./install.sh                          # Claude, Antigravity, opencode (existing default)
./install.sh --only claude,opencode   # a subset
./install.sh --dry-run                # preview, no changes
./install.sh --only codex --dry-run   # preview Codex destinations
./install.sh --only codex             # opt-in Codex support
./install.sh --only claude,antigravity,opencode,codex # all four
```

Requires Bash and Python 3.11 or newer; there are no third-party Python dependencies.
This is a **global** install — every project using the selected tool can discover the
installed definitions. Installation renders fresh adapters from the canonical sources
into temporary staging, so editing a shared prompt and reinstalling is sufficient.

Where things land:

| | Claude Code | Antigravity | opencode | Codex |
|---|---|---|---|---|
| Agents | `~/.claude/agents/<role>.md` | `~/.gemini/config/agents/<role>.md` | `~/.config/opencode/agents/<role>.md` | `~/.codex/agents/<role>.toml` |
| Skills | `~/.claude/skills/<name>/` | `~/.gemini/antigravity/skills/<name>/` | `~/.config/opencode/skills/<name>/` | `~/.agents/skills/<name>/` |
| Workflows | `~/.claude/commands/<name>.md` | `~/.gemini/antigravity/global_workflows/<name>.md` | `~/.config/opencode/command/<name>.md` | `~/.agents/skills/<name>/` (workflow skills) |
| Rules | `~/.claude/CLAUDE.md` | `~/.gemini/GEMINI.md` | `~/.config/opencode/AGENTS.md` | `~/.codex/AGENTS.md` |

Codex agent, rules, and manifest paths respect `CODEX_HOME` when set. Personal skills
remain under `~/.agents/skills`; changing `CODEX_HOME` does not relocate them. That skills
directory is shared with other compatible tools, so these skills may also be discovered there.
The installer leaves Codex's `config.toml`, model selection, and authentication untouched.

The rules file is injected as a marked block (`<!-- BEGIN ai-agent-kit -->` ... `<!-- END ai-agent-kit -->`)
so it won't clobber anything else you've already got in `CLAUDE.md`/`GEMINI.md`/`AGENTS.md` —
For Claude Code, Antigravity, and opencode, existing content is backed up to
`<file>.pre-ai-agent-kit.bak` the first time the script touches that file. Codex tracks
ownership through its manifest and preserves content outside the block without a backup
file. Subsequent installs replace only the managed block.

Note on opencode: it already auto-reads `~/.claude/skills/` as a fallback, so if you only
install the Claude Code target, opencode will still see the skills. The installer copies them
to `~/.config/opencode/skills/` explicitly too, so opencode works even if you skip Claude Code.

## Uninstall

```bash
./uninstall.sh
./uninstall.sh --only antigravity
./uninstall.sh --only codex --dry-run
./uninstall.sh --only codex
```

The default targets remain Claude, Antigravity, and opencode. Codex removal uses an
installation manifest to remove only owned, unmodified files and its unmodified rules
block. It preserves user edits, added files inside skill directories, and unrelated rules.
The existing tools retain their previous overwrite/removal behavior.

## Editing an agent or skill

1. Edit `agents/<role>/PROMPT.md` (behavior) and/or `agents/<role>/DESCRIPTION.txt` (routing/trigger)
   — or a skill's `skills/<name>/SKILL.md`, or a workflow's `workflows/<name>/BODY.md`.
2. Run `python3 scripts/build_kit.py` to refresh the checked-in generated adapters.
3. Run `python3 scripts/build_kit.py --check` and `python3 -m unittest discover -s tests`.
4. Re-run `./install.sh --only <targets>`.

To add an agent, create a directory with `PROMPT.md`, `DESCRIPTION.txt`, and
`metadata.json`, following an existing role. To add a workflow, create `BODY.md` and
`metadata.json`, following an existing workflow. Run the generator; it discovers source
directories automatically. Edit canonical sources rather than generated adapters.

## Using the agents

Once installed, ask for a role by name so the tool can delegate to it — e.g. "use the
architect agent to plan this" or "run code-reviewer on this diff." The `code-reviewer` agent
also supports a branch-diff mode: give it a source and target branch (e.g. "review
feature/checkout against release/2.4") and it'll `git diff <target>...<source>`, route changed
files to the right stack checklist, and report Blocking/Should-fix/Nit findings with concrete
fixes. `java-code-reviewer` and `frontend-code-reviewer` do the same branch-diff workflow with a
deeper, stack-specific checklist — use them for a Java-only or frontend-only repo, or when you
want closer scrutiny than the general reviewer on one part of the stack.

## Using Codex

After `./install.sh --only codex`, start a new Codex session. Ask for a role by name:

```text
Use the architect agent to plan this feature before writing code.
Use code-reviewer to review feature/checkout against release/2.4.
$new-feature Add pagination to the orders endpoint.
$mock-interview Run a senior backend mock interview.
```

In CLI and IDE sessions, use `/skills` or `$` to select a skill. The workflow skills
disable implicit invocation in `agents/openai.yaml`; mention them explicitly. Ordinary
convention and checklist skills remain available for automatic matching.

Codex agents inherit the session's model and reasoning settings. Planning and review
roles specify a read-only sandbox; implementation roles inherit the parent sandbox.
Live parent permission overrides can affect spawned agents. Claude model names, tool
allowlists, and skill preloading are not copied as Codex settings: generated role
instructions instead tell Codex to read the associated skills. The kit does not enable
disabled subagents or alter your approval policy.

Codex installation checks destinations before writing. It refuses unmanaged name
collisions and edits to previously managed files; review or move those files before
reinstalling. Its manifest records installed file hashes, including artifacts removed
or renamed in later kit versions, in `$CODEX_HOME/.ai-agent-kit-manifest.json` (default
`~/.codex/.ai-agent-kit-manifest.json`). Uninstall preserves modified files and user additions.
Use the same `CODEX_HOME` and personal home directory when updating or uninstalling.

This integration targets local Codex clients. A global home-directory install does
not configure a remote Codex Cloud environment. Agent and skill behavior follows the
[official custom-agent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[skill documentation](https://learn.chatgpt.com/docs/build-skills), and
[instruction precedence](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Validation

```bash
python3 scripts/build_kit.py --check
python3 -m unittest discover -s tests
bash -n install.sh uninstall.sh
```

Tests use isolated temporary directories rather than your installed tool configuration.
The optional offline smoke test was verified with Codex CLI 0.161.0: it confirms global
rules, ordinary skills, and all six workflow skills through local CLI/app-server discovery.
Native agent TOML generation and installation are tested; runtime delegation and explicit
workflow execution have not been exercised by this offline check. No minimum supported
CLI version is established; use a release supporting the documented standalone agent format.
For a manual smoke test, start a new Codex session, confirm the global engineering rules
are loaded, select `testing-strategy`, invoke `$new-feature` with a planning-only request,
and ask it to delegate to `architect`. File generation alone does not verify a client can
execute a delegated task.

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
nothing is lost, it's unified into one source that also covers opencode and Codex.
