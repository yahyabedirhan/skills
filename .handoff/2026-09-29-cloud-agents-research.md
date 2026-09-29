# Handoff: cloud-agents research

- **Effort:** `cloud-agents`, now **research only**: no skill, instruction or machine changes.
- **Worktree:** `~/.treehouse/skills-22e236/4/skills` (Treehouse lease `cloud-agents`)
- **Branch:** `skills/cloud-agents`, stacked on `skills/environment` (the pull request "Every harness and project is set up and audited from the skills" #66). The pull request targets `skills/environment` until #66 merges, then `main`; if #66 changes, rebase onto it.
- **Spec:** [#45 Spec: research cloud agents: what agents on a server or in the cloud can do, and how to delegate to them](https://github.com/yahyabedirhan/skills/issues/45): read it first; it holds the decisions, rules and privacy line.
- **Tickets** (label `effort:cloud-agents`, sub-issues of #45):
  - Parallel, no blockers: #69 Research: Claude Code's cloud agents - environment, capabilities and limits; #70 Research: other hosted cloud coding agents - Codex, Cursor, Copilot and more; #71 Research: what an agent on the VPS can do compared with the Mac; #72 Research: VPS sizing and cheaper or better places to run agents; #73 Research: delegating to, watching and hearing back from agents off the Mac
  - After all five: #74 Research: synthesis - capability matrix, decisions and next steps for cloud agents
  - Blocked by #74, **not built**: #13, #15, #16 (the old build tickets). #74 comments on each to re-scope them.
- **The thinking session** that wrote this can't be reached: the maintainer is AFK. Decide open questions yourself within the spec, and list them in the pull request.
- **Previous handoff:** [.handoff/2026-09-29-cloud-agents.md](2026-09-29-cloud-agents.md) (how this effort was started; its build-oriented plan is superseded by the spec).

## What the maintainer decided (2026-09-29)

- Research first; what gets built is decided from the pull request. Deliverable is **one pull request** with every finding committed under `docs/research/` (no git-ignored results; scratch may live in `.scratch/`).
- Run the tickets with parallel sub-agents, as many at once as possible.
- Cover widely adopted cloud agents beyond Claude Code, Codex, Cursor, Copilot, opencode and Grok.
- **Documentation first.** Herdr's official docs are good; exploring Herdr's capabilities further is welcome.
- **Safe zone for probes, stated strongly:** nothing destructive. On the VPS: read-only commands, plus throwaway Herdr workspaces or tabs closed afterwards; no installs, config changes, resizing or deletions. At most two small Claude Code cloud sessions against this public repo, on a throwaway branch removed afterwards. No sign-ups or payments. Be ready to show everything done: every file ends with an exploration log.
- **Privacy:** platform and tool names are fine (Hetzner, Herdr, Claude Code, Codex, Cursor). Never the VPS's name or label, host, IP, usernames, home paths, or private repositories: in files, issues, commit messages or the pull request. Tell each sub-agent this, and check it before pushing.

## Facts already found (don't re-check)

- The VPS is a saved Herdr machine on the Mac; `herdr machine list --json` gives its SSH target, and `ssh -o BatchMode=yes <target>` works with no prompt. Both machines run Herdr **0.9.0** (0.9.1 adds `herdr --machine`).
- Over non-interactive SSH, tools are only on the login-shell `PATH`: wrap commands in `bash -lc '…'`.
- VPS today: Ubuntu x86_64 on a small Hetzner instance; has `claude`, `gh`, `git`, `node` (nvm), `swift`; lacks `codex`, `opencode`, `cursor-agent`, `treehouse`, `jq`, `tailscale`, `notify-send`, and the shared `~/.config/agents/AGENTS.md`. Its installed skills are an older set (no `herdr`, `handover`, `set-up-machine`). Its skills repo clone is on `main`, main checkout only.
- `docs/research/herdr-vps.md` and `docs/research/harness-capabilities.md` already cover much of #71 and #73: build on them.
- A first research sub-agent on cloud options was started and stopped before it wrote anything; nothing to recover.

## Notes for #73 (this run as material for #15)

This effort was started by the environment effort's orchestrator handing a new effort, stacked on its own unmerged branch, to a thinking session in a new Herdr workspace. It worked. The maintainer then redirected the thinking session mid-start (stopped a research agent, cut grilling to one round, changed the effort to research). The handoff it received described a build plan that the grilling replaced.

## Suggested skills

- **orchestrate-with-handoff** / **orchestrating**: run the tickets, delegate to sub-agents.
- **research**: each ticket's file (primary sources, captured in the repo).
- **show-me**: the synthesis's matrix and the pull request's outline.
- **to-pr**: open the pull request.
- **herdr**: the Herdr CLI contract, for probes.
