# skills

[![skills.sh](https://skills.sh/b/yahyabedirhan/skills)](https://skills.sh/yahyabedirhan/skills)

Agent skills I use across projects: my own, and forks of other people's that I've changed. They work with Claude Code, Codex, and any agent the [`skills` CLI](https://github.com/vercel-labs/skills) supports.

## Install

One skill (most people want this):

```bash
npx skills add yahyabedirhan/skills -s wispr-flow-dictionary
```

Swap in any name from the table below. Leave out `-s` to pick from the list, and add `-g` to install for your user rather than the current project.

## Skills

The Origin column names the upstream commit each fork was copied from, so a later upstream change can be diffed against it.

| Skill | What it does | Origin |
|---|---|---|
| [to-pr](skills/to-pr/SKILL.md) | Opens a pull request or rewrites its description: a one-sentence why, reviewer notes, and a visual change outline. | Fork of `visual-pr` from [humanlayer/skills](https://github.com/humanlayer/skills) at [`4e39d8f`](https://github.com/humanlayer/skills/tree/4e39d8fe020f/plugins/visual-pr/skills/visual-pr) (MIT, see `skills/to-pr/LICENSE.humanlayer`). Changes: renamed, a real trigger description, and no Mermaid views. |
| [show-me](skills/show-me/SKILL.md) | Explains the current topic visually with pseudocode, call trees, file trees, `diff` blocks, or one focused HTML file. | Fork of `show-me` from [humanlayer/skills](https://github.com/humanlayer/skills) at [`6ab9013`](https://github.com/humanlayer/skills/tree/6ab9013a10c2/plugins/show-me/skills/show-me) (MIT, see `skills/show-me/LICENSE.humanlayer`). Changes: no Mermaid views, so every view renders as plain text. |
| [maintain-skills](skills/maintain-skills/SKILL.md) | Installs, moves, updates, forks, publishes, removes, and audits skills across global scope, project scope, and your own skills repo with `npx skills`; prompt-audits each new skill in a fresh sub-agent and measures a skill's run cost on request. | Original. |
| [init-effort](skills/init-effort/SKILL.md) | Starts an effort on its own branch and worktree, runs its thinking session, and ends with a handover prompt for the orchestrator. | Original. |
| [init-effort-with-herdr](skills/init-effort-with-herdr/SKILL.md) | Starts an effort in a Treehouse worktree opened as a Herdr workspace, and launches its thinking agent there. | Original. |
| [orchestrating](skills/orchestrating/SKILL.md) | The orchestrator's discipline: delegate, trust delegates, be the user's one contact. Holds the effort lifecycle. | Original. |
| [orchestrate-effort](skills/orchestrate-effort/SKILL.md) | Builds an effort from its spec and tickets through sub-agents and opens the pull request. | Original. |
| [orchestrate-with-handoff](skills/orchestrate-with-handoff/SKILL.md) | Picks up an effort from a thinking session's handoff and runs orchestrate-effort. | Original. |
| [orchestrate-with-herdr](skills/orchestrate-with-herdr/SKILL.md) | Ends a thinking session and starts its orchestrator in a new Herdr tab in the same workspace. | Original. |
| [implement](skills/implement/SKILL.md) | Builds work from a spec or tickets with tdd and code-review. | Fork of `implement` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`697d4ce`](https://github.com/mattpocock/skills/tree/697d4ce9742d/skills/engineering/implement) (MIT, see `skills/implement/LICENSE.mattpocock`). Changes: agents can load it, so an orchestrator's sub-agents can use it, and it commits only when the delegating agent doesn't. |
| [low-level-design](skills/low-level-design/SKILL.md) | Designs, explains or redesigns code at the level of modules, classes, files and folders, through the low-level design delivery framework, with reference documents for the principles, OOP concepts and patterns. | Original. Distils Hello Interview's low-level design lessons, cited at the end of each document. |
| [system-design](skills/system-design/SKILL.md) | Designs, explains or redesigns a system at the level of services, data stores, APIs and scale, through the system design delivery framework, with reference documents for the core concepts. | Original. Distils Hello Interview's system design lessons, cited at the end of each document. |
| [wispr-flow-dictionary](skills/wispr-flow-dictionary/SKILL.md) | Tunes the Wispr Flow dictionary from your real dictation history: finds the names, products and commands it mishears, fixes them with backups and undo, and shows whether each fix held. macOS. See [below](#wispr-flow-dictionary). | Original. The snippet finder and quit-write-relaunch flow follow ideas from [glebis/claude-skills](https://github.com/glebis/claude-skills) (`wispr-analytics`, `wispr-fix`); no code copied. |

## wispr-flow-dictionary

Dictation tools mishear the words that matter most in technical work: product names, company names, CLI commands. It gets worse with a non-native accent. Wispr Flow's dictionary fixes that, but only if you know what to add. This skill finds out from your own history and keeps the dictionary tidy over time.

- **Finds mistakes from real use.** Name-like terms, words the formatter swapped (`--diff`), and whole-word counts over any window: `30m`, `3h`, `2d`, `1h30m`.
- **Words first, rules when needed.** It proposes a plain dictionary word, and a replacement rule only when a mistake keeps coming back after its word was added.
- **Checks that fixes work.** Every count shows how often a mistake happened *since* its entry was added.
- **Fixes as you go.** Tell your agent "I said skill, it wrote SQL" and it adds the fix then and there.
- **Safe writes.** Every write backs up the dictionary first, can be undone as a batch, and can quit and relaunch Wispr Flow so the change loads.
- **Snippets.** It finds links and sentences you dictate in full again and again.

**What it touches:** it reads `~/Library/Application Support/Wispr Flow/flow.sqlite` and writes only the `Dictionary` table, after a backup to `~/.local/state/wispr-flow/backups/`. Wispr Flow has no API for this; its remote MCP server covers meetings, not dictation or the dictionary.

**Next to other Wispr Flow skills:** [`wispr-analytics`](https://skills.sh/glebis/claude-skills/wispr-analytics) is the one to use for usage analytics and reflection, and [`wispr-fix`](https://skills.sh/glebis/claude-skills/wispr-fix) queues corrections by hand. This skill does the dictionary loop end to end: find, fix, and check.

## The effort workflow

`init-effort`, `init-effort-with-herdr`, `orchestrating`, `orchestrate-effort`, `orchestrate-with-handoff`, and `orchestrate-with-herdr` take one effort (a feature, a new app, a refactor) from an idea to a merged pull request, building on Matt Pocock's skills for the thinking. The path is in [skills/orchestrating/lifecycle.md](skills/orchestrating/lifecycle.md). Install them together, along with `to-pr`, `show-me`, `implement`, and [mattpocock/skills](https://github.com/mattpocock/skills).

## Decision records

`docs/decisions/` records why a skill or workflow is shaped the way it is, one dated entry per decision. Read it before changing the skills it covers. It is not installed.

## Research

`docs/research/` holds the fact-finding behind open issues: how the harnesses, Herdr, git and GitHub actually behave, with sources and test notes. Each issue links the notes it relies on. It is not installed.
