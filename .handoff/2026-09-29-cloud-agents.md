# Handoff: cloud-agents

- **Effort:** `cloud-agents`
- **Worktree:** this one, `~/.treehouse/skills-22e236/4/skills` (Treehouse lease `cloud-agents`)
- **Branch:** `skills/cloud-agents`, stacked on `skills/environment` at `9bf6c8c`, **not** `main`
- **Tracker:** GitHub issues in `yahyabedirhan/skills`, label `effort:cloud-agents` (see `docs/agents/issue-tracker.md`)
- **Handing session:** the orchestrator of the "environment" effort, in its own worktree (`~/.treehouse/skills-22e236/3/skills`). It stays busy with that effort; don't message it or touch its branch.

## The idea, as the maintainer gave it

A thinking session about what the maintainer wants for **cloud agents**, starting a new effort: delegating efforts to agents beyond the local machine (the VPS and cloud agents). After the thinking session, it hands over to an orchestrator.

The starting point is the existing spec and its tickets. Treat them as input to grill, not as settled; the spec calls itself "exploratory, and not started":

- [Spec: delegate efforts to agents beyond the local machine: the VPS and cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45): its "Questions to explore" are the first grilling round's material
- [A thinking session on the Mac can hand over to an orchestrator on the VPS (#13)](https://github.com/yahyabedirhan/skills/issues/13)
- [An unfinished effort can be handed to a new orchestrator (#15)](https://github.com/yahyabedirhan/skills/issues/15)
- [Agents on the Mac and the VPS can see each other's state (#16)](https://github.com/yahyabedirhan/skills/issues/16)
- [Hand a new effort from a Claude Code desktop session to a Herdr orchestrator (#22)](https://github.com/yahyabedirhan/skills/issues/22) is closed; the effort workflow covered it.

This handover is itself the first run of a new flow: an orchestrator session handing a *new* effort, stacked on its own unmerged branch, to a thinking session in a new Herdr workspace. What worked and what didn't is material for #15.

## Why the branch is stacked

The base is [Every harness and project is set up and audited from the skills (#66)](https://github.com/yahyabedirhan/skills/pull/66), open and under the maintainer's review. It changes what this effort builds on:

- **set-up-machine** sets up a fresh Linux machine the same way as the Mac. It includes a reusable Docker check in `skills/set-up-machine/scripts/tests/linux/`, and a Linux fix: a harness counts as found when its program is on PATH. The same rule table, pre-tool hook and memory-off apply on every machine. The shared global instructions live at `~/.config/agents/AGENTS.md`.
- **Skills name roles, not tools.** They read `<session-host>`, `<worktree-tool>`, `<agent-to-start>` and `<notification-method>` from a `## Parameters` section. The value comes from the Defaults table in the environment's instructions, where a project's table overrides the global one. So a VPS can name a different host or tool without editing any skill. The convention is in `skills/maintain-environment/where-things-go.md`.
- **Rewritten skills this effort will touch:** handover, handover-to-herdr (which now also holds `closing-an-effort.md`), close-effort and init-effort. Treehouse moved into its own `treehouse` skill. Build on these versions, not `main`'s.
- **set-up-project** is the new project entry point; to-spec and to-tickets point at it.
- **Research already on this branch:**
  - `docs/research/herdr-vps.md`: earlier VPS research.
  - `docs/research/harness-capabilities.md`: what Claude Code, Codex, opencode and Cursor can express.
  - `docs/research/auto-mode-semantic-guard.md`: auto mode as a guard.

If #66 changes during review, rebase this branch onto it. Once #66 merges, this effort's pull request targets `main`.

## What the thinking session should know

- **The installed skills are `main`'s,** not this branch's, until #66 merges and they're reinstalled. The installed handover still says "a Herdr tab by default", and set-up-machine and set-up-project aren't installed yet. Read this branch's skill files when the design depends on them.
- **Out of scope in #66, and a natural fit here:**
  - Provisioning the VPS itself: the server, SSH, users.
  - Real logged-in harness sessions on Linux. The container check ran without a login.
- **Codex runs every command through `<shell> -lc`.** Its `workspace-write` sandbox keeps `.git` read-only in `codex exec`. This matters for unattended runs.
- **Never `rm -rf`.** Move what's no longer needed into `.scratch/`. Run each commit and each push as its own command.
- **This repo is public:** no personal information, and no details of private projects, in files, issues or the pull request.
- **Name issues and pull requests by title,** with the number after.

## How the maintainer works

- Facts are the agent's job, decisions are the maintainer's. Look things up instead of asking.
- Harness compliance is non-negotiable. When in doubt, research until certain.
- Reports are short, with the smallest visual that makes the point (**show-me**).
- The maintainer reviews the grilling's result as it happens and gives feedback once they see the output. Don't over-decide up front.
