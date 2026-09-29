# skills

[![skills.sh](https://skills.sh/b/yahyabedirhan/skills)](https://skills.sh/yahyabedirhan/skills)

Agent skills I use across projects: my own, and forks of other people's that I've changed. They work with Claude Code, Codex, and any agent the [`skills` CLI](https://github.com/vercel-labs/skills) supports.

They come in five families. Each family's skills are listed under [Skills](#skills) and explained under [How the skills work](#how-the-skills-work):

- **[Effort workflow](#effort-workflow)**: take a feature from an idea to a merged pull request.
- **[Design frameworks](#design-frameworks)**: design or explain code and systems step by step.
- **[Communication style](#communication-style)**: how an agent explains and reports its work.
- **[Agent setup](#agent-setup)**: install, maintain and audit what your agents run with.
- **[Daily workflows](#daily-workflows)**: everyday tasks outside the code, such as email and dictation.

## Install

Install any skill by its name from [Skills](#skills):

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

### Effort workflow

| Skill | What it does | Origin |
|---|---|---|
| [init-effort](skills/init-effort/SKILL.md) | Starts an effort on its own branch and worktree (Treehouse by default, or the project's own tool), or a brand-new project in its own GitHub repo, and starts its thinking session, in a Herdr tab by default. | Original. |
| [orchestrating](skills/orchestrating/SKILL.md) | The orchestrator's discipline: delegate, trust delegates, be the user's one contact, deciding what it can and asking only for a critical blocker. Holds the effort lifecycle and when to notify. | Original. |
| [orchestrate-effort](skills/orchestrate-effort/SKILL.md) | Builds an effort from its spec and tickets through sub-agents and opens the pull request. | Original. |
| [handoff](skills/handoff/SKILL.md) | Writes a handoff document in the repository for another session to pick up, and leaves it for the caller to commit. | Fork of `handoff` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`d28dfdc`](https://github.com/mattpocock/skills/tree/d28dfdc39bea/skills/productivity/handoff) (MIT, see `skills/handoff/LICENSE.mattpocock`). Changes: agents can load it, and it saves to the repository's handoff folder (`.handoff/<date>-<topic>.md`) instead of a temp folder. |
| [handover](skills/handover/SKILL.md) | Hands work over to a new session outside this one: a readiness checklist, the starting prompt, a mechanism to start it, and a check that it started. | Original. |
| [handover-to-herdr](skills/handover-to-herdr/SKILL.md) | The Herdr mechanism of a handover, from inside or outside a Herdr pane (such as a desktop-app session): opens the worktree as a workspace, starts the agent in a labelled tab, sends the prompt, and confirms it's working. | Original. |
| [orchestrate-with-handoff](skills/orchestrate-with-handoff/SKILL.md) | Picks up an effort from a handoff and runs orchestrate-effort. | Original. |
| [implement](skills/implement/SKILL.md) | Builds work from a spec or tickets with tdd and code-review. | Fork of `implement` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`697d4ce`](https://github.com/mattpocock/skills/tree/697d4ce9742d/skills/engineering/implement) (MIT, see `skills/implement/LICENSE.mattpocock`). Changes: agents can load it, so an orchestrator's sub-agents can use it, it commits only when the delegating agent doesn't, it reviews at the depth the delegating agent sets, and it stops what it started before reporting. |
| [to-spec](skills/to-spec/SKILL.md) | Turns the current conversation into a spec and publishes it to the project's tracker, or to `.efforts/<effort>/spec.md` on a local one. | Fork of `to-spec` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`5c89081`](https://github.com/mattpocock/skills/tree/5c89081d4bbe/skills/engineering/to-spec) (MIT, see `skills/to-spec/LICENSE.mattpocock`). Changes: agents can load it, so a thinking session runs it itself, and a local tracker keeps the spec in `.efforts/<effort>/` instead of `.scratch/`. |
| [to-tickets](skills/to-tickets/SKILL.md) | Breaks a plan, spec or conversation into tracer-bullet tickets, each naming what blocks it, and publishes them to the project's tracker, or to `.efforts/<effort>/issues/` on a local one. | Fork of `to-tickets` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`5c89081`](https://github.com/mattpocock/skills/tree/5c89081d4bbe/skills/engineering/to-tickets) (MIT, see `skills/to-tickets/LICENSE.mattpocock`). Changes: agents can load it, so a thinking session runs it itself; a local tracker keeps the tickets in `.efforts/<effort>/issues/` instead of `.scratch/`; and tickets are named by title, never by a number alone. |
| [to-pr](skills/to-pr/SKILL.md) | Opens a pull request or rewrites its description: a one-sentence why, reviewer notes, and a visual change outline. | Fork of `visual-pr` from [humanlayer/skills](https://github.com/humanlayer/skills) at [`4e39d8f`](https://github.com/humanlayer/skills/tree/4e39d8fe020f/plugins/visual-pr/skills/visual-pr) (MIT, see `skills/to-pr/LICENSE.humanlayer`). Changes: renamed, a real trigger description, no Mermaid views, the description source saved to `.scratch/` per the folder standard instead of `.humanlayer/`, issues named by title, never by a number alone, and a last section, *Things to be aware of*, for decisions made alone, surprises, what's left out and follow-ups, and "Refs", not "Closes", for a ticket waiting for the maintainer's QA. |
| [close-effort](skills/close-effort/SKILL.md) | Closes an effort once you say its pull request is good, or that it merged: merges it, runs the post-merge follow-ups, carries unfinished work into next-effort tickets, closes the tracker, and removes only branches and worktrees proven merged, then its own worktree from a Herdr tab. | Original. |

### Design frameworks

| Skill | What it does | Origin |
|---|---|---|
| [low-level-design](skills/low-level-design/SKILL.md) | Designs, explains or redesigns code at the level of modules, classes, files and folders, with reference documents for the principles, OOP concepts and patterns. | Original. Distils Hello Interview's low-level design lessons, cited at the end of each document. |
| [system-design](skills/system-design/SKILL.md) | Designs, explains or redesigns a system at the level of services, data stores, APIs and scale, with reference documents for the core concepts. | Original. Distils Hello Interview's system design lessons, cited at the end of each document. |

### Communication style

| Skill | What it does | Origin |
|---|---|---|
| [show-me](skills/show-me/SKILL.md) | Explains the current topic visually with pseudocode, call trees, file trees, `diff` blocks, or one focused HTML file. | Fork of `show-me` from [humanlayer/skills](https://github.com/humanlayer/skills) at [`6ab9013`](https://github.com/humanlayer/skills/tree/6ab9013a10c2/plugins/show-me/skills/show-me) (MIT, see `skills/show-me/LICENSE.humanlayer`). Changes: no Mermaid views, so every view renders as plain text. |

### Agent setup

| Skill | What it does | Origin |
|---|---|---|
| [maintain-skills](skills/maintain-skills/SKILL.md) | Installs, moves, updates, forks, publishes, removes, and audits skills across global scope, project scope, and your own skills repo with `npx skills`; prompt-audits each new skill in a fresh sub-agent and measures a skill's run cost on request. | Original. |

### Daily workflows

| Skill | What it does | Origin |
|---|---|---|
| [email](skills/email/SKILL.md) | Reads and tidies your email: Spark CLI for fast reading, the Gmail connector for marking done, labels, pins and drafts, with sending, trash and spam denied. Includes setup and checks. | Original. The daily workflows adapt the read-only recipes in [readdle/spark-cli-skills](https://github.com/readdle/spark-cli-skills) at [`507d26e`](https://github.com/readdle/spark-cli-skills/tree/507d26e/skills) (MIT); no text copied. |
| [wispr-flow-dictionary](skills/wispr-flow-dictionary/SKILL.md) | Tunes the Wispr Flow dictionary from your real dictation history: finds the names, products and commands it mishears, fixes them with backups and undo, and shows whether each fix held. macOS. | Original. The snippet finder and quit-write-relaunch flow follow ideas from [glebis/claude-skills](https://github.com/glebis/claude-skills) (`wispr-analytics`, `wispr-fix`); no code copied. |

## How the skills work

### Effort workflow

An **effort** (a feature, a new app, a refactor) goes from an idea to a merged pull request in one worktree on one branch. A thinking session decides what to build, and a fresh orchestrator builds it, so the builder starts from conclusions instead of debate.

```text
START      init-effort                                   worktree and branch (or a new repo), decided once
             handover-to-herdr, or a pasted prompt       starts the thinking session
THINKING   grilling, to-spec, to-tickets                 leaves a spec, tickets and a handoff
HANDOVER   handover                                      ready, prompt, mechanism, started
             handoff                                     writes the handoff in the repo
             handover-to-herdr, or a pasted prompt       starts a fresh orchestrator
BUILD      orchestrate-with-handoff → orchestrate-effort
             orchestrating                               the orchestrator's discipline
             implement                                   each ticket, built by a sub-agent
             show-me                                     shows the plan
             to-pr                                       last step: opens the pull request
CLOSE      close-effort                                  after your "go": merge, follow up, carry over, clean up
```

Install the family together with `show-me` and [mattpocock/skills](https://github.com/mattpocock/skills). The full path is in [lifecycle.md](skills/orchestrating/lifecycle.md), and where each record goes (spec, tickets, handoff, notes) in the [folder standard](skills/orchestrating/folders.md).

### Design frameworks

Each skill runs a design session through a delivery framework, whether you are designing something new, explaining existing work, redesigning it, or deciding one question. It starts simple and adds only what a requirement proves necessary.

```text
low-level-design   code: modules, classes, files, folders
  requirements → entities and relationships → class design → implementation → extensibility
system-design      systems: services, data stores, APIs, scale
  requirements → core entities → API → data flow → high-level design → deep dives
```

The documents in each skill's `references/` hold the principles, patterns and concepts, loaded only when a step needs them.

### Communication style

How an agent shows its thinking so a reader takes it in quickly. `show-me` picks the smallest view that makes the point, in plain text that reads the same in a terminal, an editor, or on GitHub.

```text
show-me   explains the current topic
  pseudocode · call tree · file tree · diff block · one focused HTML page
```

### Agent setup

What your agents run with, kept in order across Claude Code and Codex. Today that is skills: `maintain-skills` keeps every change flowing from a skill's source to its installs.

```text
source      your skills repo, or someone else's
  ↓ npx skills add / update / remove
installs    global (~/.agents/skills) or one project (.agents/skills)
operations  install, update, move, remove, fork, publish
audits      which skills you use, a fresh prompt audit, a run's cost
```

### Daily workflows

Everyday tasks outside the code that an agent can take over safely. Each skill reads freely and changes only what you approve, with sending, deleting and other risky actions left to you.

`email` reads mail fast with the Spark CLI and makes every change through the Gmail connector. Drafts are as far as it goes: Claude Code permission rules deny sending, trash and spam.

```text
read     Spark CLI: inbox by category, threads, pins, calendar, contacts
act      Gmail connector: mark done (archive), labels, pins (stars), drafts
how      which tool for which job; what to do and when stays with you
setup    setup.md: both tools, the deny rules, and checks
```

`wispr-flow-dictionary` keeps [Wispr Flow](https://wisprflow.ai)'s dictionary accurate for technical vocabulary, where dictation mishears product names, company names and commands. It reads Wispr Flow's local database and writes only its `Dictionary` table, after a backup.

```text
find    terms, formatter swaps and counts over any window (30m, 3h, 2d)
fix     a plain word first; a rule only when a mistake returns; snippets for text you repeat
        every write backs up first, can be undone, and can relaunch the app
check   each count shows the mistakes made since the entry was added
```

## Adding a skill

Add its row to its family's table under [Skills](#skills), and fold it into that family's section under [How the skills work](#how-the-skills-work). Prefer an existing family; start a new one only when a skill fits none. A new family gets its own subsection and table under Skills, a line in the list at the top, and a section under [How the skills work](#how-the-skills-work), in the same shape as the others: two sentences and one outline.

## Decision records

`docs/decisions/` records why a skill or workflow is shaped the way it is, one dated entry per decision. Read it before changing the skills it covers. It is not installed.

## Research

`docs/research/` holds the fact-finding behind open issues: how the harnesses, Herdr, git and GitHub actually behave, with sources and test notes. Each issue links the notes it relies on. It is not installed.
