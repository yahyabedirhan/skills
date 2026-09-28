# skills

[![skills.sh](https://skills.sh/b/yahyabedirhan/skills)](https://skills.sh/yahyabedirhan/skills)

Agent skills I use across projects: my own, and forks of other people's that I've changed. They work with Claude Code, Codex, and any agent the [`skills` CLI](https://github.com/vercel-labs/skills) supports.

They come in six families, each explained under [How the skills work](#how-the-skills-work):

- **[Effort workflow](#effort-workflow)**: take a feature from an idea to a merged pull request.
- **[Design frameworks](#design-frameworks)**: design or explain code and systems step by step.
- **[Pull requests and explanations](#pull-requests-and-explanations)**: describe changes and show ideas visually.
- **[Skill upkeep](#skill-upkeep)**: install, move, publish and audit skills.
- **[Email](#email)**: read and tidy an inbox, and draft replies without sending.
- **[Dictation](#dictation)**: keep a speech-to-text dictionary accurate.

## Install

Install any skill by its name from the [table](#skills):

```bash
npx skills add yahyabedirhan/skills -s <skill-name>
```

For example `-s to-pr`, `-s system-design`, or `-s wispr-flow-dictionary`. Leave out `-s` to pick from a list, and add `-g` to install for your user rather than the current project. Skills in the same family name each other, so install a family together.

### Claude Code plugins

Some skills are also Claude Code plugins, from this repo's marketplace. Add the marketplace once:

```bash
claude plugin marketplace add yahyabedirhan/skills
```

Then install a plugin by name:

| Plugin | Install |
|---|---|
| wispr-flow-dictionary | `claude plugin install wispr-flow-dictionary@yahyabedirhan-skills` |

Install a skill one way or the other, not both, or Claude Code loads it twice.

## Skills

The Origin column names the upstream commit each fork was copied from, so a later upstream change can be diffed against it.

| Skill | Family | What it does | Origin |
|---|---|---|---|
| [init-effort](skills/init-effort/SKILL.md) | [Effort workflow](#effort-workflow) | Starts an effort on its own branch and worktree, runs its thinking session, and ends with a handover prompt for the orchestrator. | Original. |
| [init-effort-with-herdr](skills/init-effort-with-herdr/SKILL.md) | [Effort workflow](#effort-workflow) | Starts an effort in a Treehouse worktree opened as a Herdr workspace, and launches its thinking agent there. | Original. |
| [orchestrating](skills/orchestrating/SKILL.md) | [Effort workflow](#effort-workflow) | The orchestrator's discipline: delegate, trust delegates, be the user's one contact. Holds the effort lifecycle. | Original. |
| [orchestrate-effort](skills/orchestrate-effort/SKILL.md) | [Effort workflow](#effort-workflow) | Builds an effort from its spec and tickets through sub-agents and opens the pull request. | Original. |
| [orchestrate-with-handoff](skills/orchestrate-with-handoff/SKILL.md) | [Effort workflow](#effort-workflow) | Picks up an effort from a thinking session's handoff and runs orchestrate-effort. | Original. |
| [orchestrate-with-herdr](skills/orchestrate-with-herdr/SKILL.md) | [Effort workflow](#effort-workflow) | Ends a thinking session and starts its orchestrator in a new Herdr tab in the same workspace. | Original. |
| [implement](skills/implement/SKILL.md) | [Effort workflow](#effort-workflow) | Builds work from a spec or tickets with tdd and code-review. | Fork of `implement` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`697d4ce`](https://github.com/mattpocock/skills/tree/697d4ce9742d/skills/engineering/implement) (MIT, see `skills/implement/LICENSE.mattpocock`). Changes: agents can load it, so an orchestrator's sub-agents can use it, and it commits only when the delegating agent doesn't. |
| [low-level-design](skills/low-level-design/SKILL.md) | [Design frameworks](#design-frameworks) | Designs, explains or redesigns code at the level of modules, classes, files and folders, with reference documents for the principles, OOP concepts and patterns. | Original. Distils Hello Interview's low-level design lessons, cited at the end of each document. |
| [system-design](skills/system-design/SKILL.md) | [Design frameworks](#design-frameworks) | Designs, explains or redesigns a system at the level of services, data stores, APIs and scale, with reference documents for the core concepts. | Original. Distils Hello Interview's system design lessons, cited at the end of each document. |
| [to-pr](skills/to-pr/SKILL.md) | [Pull requests and explanations](#pull-requests-and-explanations) | Opens a pull request or rewrites its description: a one-sentence why, reviewer notes, and a visual change outline. | Fork of `visual-pr` from [humanlayer/skills](https://github.com/humanlayer/skills) at [`4e39d8f`](https://github.com/humanlayer/skills/tree/4e39d8fe020f/plugins/visual-pr/skills/visual-pr) (MIT, see `skills/to-pr/LICENSE.humanlayer`). Changes: renamed, a real trigger description, and no Mermaid views. |
| [show-me](skills/show-me/SKILL.md) | [Pull requests and explanations](#pull-requests-and-explanations) | Explains the current topic visually with pseudocode, call trees, file trees, `diff` blocks, or one focused HTML file. | Fork of `show-me` from [humanlayer/skills](https://github.com/humanlayer/skills) at [`6ab9013`](https://github.com/humanlayer/skills/tree/6ab9013a10c2/plugins/show-me/skills/show-me) (MIT, see `skills/show-me/LICENSE.humanlayer`). Changes: no Mermaid views, so every view renders as plain text. |
| [maintain-skills](skills/maintain-skills/SKILL.md) | [Skill upkeep](#skill-upkeep) | Installs, moves, updates, forks, publishes, removes, and audits skills across global scope, project scope, and your own skills repo with `npx skills`; prompt-audits each new skill in a fresh sub-agent and measures a skill's run cost on request. | Original. |
| [email](skills/email/SKILL.md) | [Email](#email) | Reads and tidies your email: Spark CLI for fast reading, the Gmail connector for marking done, labels, pins and drafts, with sending, trash and spam denied. Includes setup and checks. | Original. The daily workflows adapt the read-only recipes in [readdle/spark-cli-skills](https://github.com/readdle/spark-cli-skills) at [`507d26e`](https://github.com/readdle/spark-cli-skills/tree/507d26e/skills) (MIT); no text copied. |
| [wispr-flow-dictionary](skills/wispr-flow-dictionary/SKILL.md) | [Dictation](#dictation) | Tunes the Wispr Flow dictionary from your real dictation history: finds the names, products and commands it mishears, fixes them with backups and undo, and shows whether each fix held. macOS. | Original. The snippet finder and quit-write-relaunch flow follow ideas from [glebis/claude-skills](https://github.com/glebis/claude-skills) (`wispr-analytics`, `wispr-fix`); no code copied. |

## How the skills work

### Effort workflow

An **effort** (a feature, a new app, a refactor) goes from an idea to a merged pull request in one worktree on one branch. A thinking session decides what to build, and a fresh orchestrator builds it, so the builder starts from conclusions instead of debate.

```text
START      init-effort, or init-effort-with-herdr        worktree and branch, decided once
THINKING   mattpocock/skills: grill, spec, tickets       leaves a spec, tickets and a handoff
HANDOVER   orchestrate-with-herdr, or a pasted prompt    starts a fresh orchestrator
BUILD      orchestrate-with-handoff → orchestrate-effort
             orchestrating                               the orchestrator's discipline
             implement                                   each ticket, built by a sub-agent
             show-me, to-pr                              the plan, then the pull request
CLOSE      remove the worktree and branch after the merge
```

Install the family together with `to-pr`, `show-me` and [mattpocock/skills](https://github.com/mattpocock/skills). The full path is in [lifecycle.md](skills/orchestrating/lifecycle.md).

### Design frameworks

Each skill runs a design session through a delivery framework, whether you are designing something new, explaining existing work, redesigning it, or deciding one question. It starts simple and adds only what a requirement proves necessary.

```text
low-level-design   code: modules, classes, files, folders
  requirements → entities and relationships → class design → implementation → extensibility
system-design      systems: services, data stores, APIs, scale
  requirements → core entities → API → data flow → high-level design → deep dives
```

The documents in each skill's `references/` hold the principles, patterns and concepts, loaded only when a step needs them.

### Pull requests and explanations

Two skills turn work into something a reader takes in quickly. Both render as plain text, so they read the same in a terminal, an editor, or on GitHub.

```text
to-pr     opens or rewrites a pull request
  one-sentence why → reviewer notes → visual outline of the change
show-me   explains the current topic
  pseudocode, call tree, file tree, diff block, or one focused HTML page
```

### Skill upkeep

`maintain-skills` keeps every change flowing from a skill's source to its installs, for Claude Code and Codex alike.

```text
source      your skills repo, or someone else's
  ↓ npx skills add / update / remove
installs    global (~/.agents/skills) or one project (.agents/skills)
operations  install, update, move, remove, fork, publish
audits      which skills you use, a fresh prompt audit, a run's cost
```

### Email

`email` splits the job between two tools: the Spark CLI reads mail fast from Spark Desktop's local copy, and the Gmail connector makes every change. Drafts are as far as it goes, because Claude Code permission rules deny sending, trash and spam.

```text
read     Spark CLI: inbox by category, threads, pins, calendar, contacts
act      Gmail connector: mark done (archive), labels, pins (stars), drafts
daily    start of day → triage by category → end of day
setup    setup.md: both tools, the deny rules, and checks
```

### Dictation

`wispr-flow-dictionary` keeps [Wispr Flow](https://wisprflow.ai)'s dictionary accurate for technical vocabulary, where dictation mishears product names, company names and commands, and more so with a non-native accent.

```text
find    terms, formatter swaps and counts over any window (30m, 3h, 2d)
fix     a plain word first; a rule only when a mistake returns; snippets for text you repeat
        every write backs up first, can be undone, and can relaunch the app
check   each count shows the mistakes made since the entry was added
```

It reads Wispr Flow's local database and writes only its `Dictionary` table. For usage analytics, see [`wispr-analytics`](https://skills.sh/glebis/claude-skills/wispr-analytics).

## Adding a skill

Add its row to the [table](#skills) with its family. A skill that starts a new family also gets a line in the list at the top and a section under [How the skills work](#how-the-skills-work), in the same shape as the others: two sentences and one outline.

## Decision records

`docs/decisions/` records why a skill or workflow is shaped the way it is, one dated entry per decision. Read it before changing the skills it covers. It is not installed.

## Research

`docs/research/` holds the fact-finding behind open issues: how the harnesses, Herdr, git and GitHub actually behave, with sources and test notes. Each issue links the notes it relies on. It is not installed.
