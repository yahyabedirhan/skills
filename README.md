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

| Plugin | Skills | Install |
|---|---|---|
| effort-workflow | The [effort workflow](#effort-workflow) family; installs `show-me` with it | `claude plugin install effort-workflow@yahyabedirhan-skills` |
| show-me | show-me | `claude plugin install show-me@yahyabedirhan-skills` |
| low-level-design | low-level-design | `claude plugin install low-level-design@yahyabedirhan-skills` |
| system-design | system-design | `claude plugin install system-design@yahyabedirhan-skills` |
| email | email | `claude plugin install email@yahyabedirhan-skills` |
| wispr-flow-dictionary | wispr-flow-dictionary | `claude plugin install wispr-flow-dictionary@yahyabedirhan-skills` |

A plugin's skills run as `/<plugin>:<skill>` or by their bare name, such as `/to-pr`. The [Agent setup](#agent-setup) skills aren't plugins: `set-up-machine` wires a hook to its installed path, which a plugin update would move.

Install a skill one way or the other, not both. Claude Code loads it twice, and the bare name runs the `npx skills` copy, so plugin updates go unseen. To switch to the plugin, first remove the copy with `npx skills remove <skill-name>` (add `-g` for a global install).

## Skills

The Origin column names the upstream commit each fork was copied from, so a later upstream change can be diffed against it.

### Effort workflow

| Skill | What it does | Origin |
|---|---|---|
| [init-effort](skills/init-effort/SKILL.md) | Starts an effort on its own branch and worktree (with your worktree tool, else `git worktree add`), or a brand-new project in its own GitHub repo, and starts its thinking session in your session host, else here or through a pasted prompt. | Original. |
| [orchestrating](skills/orchestrating/SKILL.md) | The orchestrator's discipline: delegate, trust delegates, be the user's one contact, deciding what it can and asking only for a critical blocker. Holds the effort lifecycle and when to notify. | Original. |
| [orchestrate-effort](skills/orchestrate-effort/SKILL.md) | Builds an effort from its spec and tickets through sub-agents and opens the pull request. | Original. |
| [handoff](skills/handoff/SKILL.md) | Writes a handoff document in the repository for another session to pick up, and leaves it for the caller to commit. | Fork of `handoff` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`d81f3a1`](https://github.com/mattpocock/skills/tree/d81f3a183412/skills/productivity/handoff) (MIT, see `skills/handoff/LICENSE.mattpocock`). Changes: agents can load it, and it saves to the repository's handoff folder (`.handoff/<date>-<topic>.md`) instead of a temp folder. |
| [handover](skills/handover/SKILL.md) | Hands work over to a new session outside this one: gets the work and its handoff ready, writes a one-line starting prompt, starts the session and confirms it started. | Original. |
| [handover-to-herdr](skills/handover-to-herdr/SKILL.md) | Starts a new agent session in a labelled `herdr` tab, sends it its starting prompt and confirms it's working, for handover and init-effort. It also resolves live session identities, checks occupants and marks a settled session's tab while keeping topology open. Works from inside or outside a `herdr` pane. | Original. |
| [treehouse](skills/treehouse/SKILL.md) | Leases, lists, returns and destroys worktrees from `treehouse`'s pre-warmed pool, with the gotchas, for the skills that make or free worktrees when `treehouse` is your worktree tool. | Original. |
| [orchestrate-with-handoff](skills/orchestrate-with-handoff/SKILL.md) | Picks up an effort from a handoff and runs orchestrate-effort. | Original. |
| [implement](skills/implement/SKILL.md) | Builds work from a spec or tickets with tdd and code-review. | Fork of `implement` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`d81f3a1`](https://github.com/mattpocock/skills/tree/d81f3a183412/skills/engineering/implement) (MIT, see `skills/implement/LICENSE.mattpocock`). Changes: agents can load it, so an orchestrator's sub-agents can use it, it commits only when the delegating agent doesn't, it reviews at the depth the delegating agent sets, it runs typechecking only where the project has a typechecker, with no one to agree tdd seams with it chooses them and names them in its report, it stops what it started before reporting, and it moves what it no longer needs into `.scratch/` instead of running `rm -rf`. |
| [to-spec](skills/to-spec/SKILL.md) | Turns the current conversation into a spec and publishes it to the project's tracker, or to `.efforts/<effort>/spec.md` on a local one. | Fork of `to-spec` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`d81f3a1`](https://github.com/mattpocock/skills/tree/d81f3a183412/skills/engineering/to-spec) (MIT, see `skills/to-spec/LICENSE.mattpocock`). Changes: agents can load it, so a thinking session runs it itself; with no tracker configured it runs set-up-project instead of telling you to run `setup-matt-pocock-skills`; and a local tracker keeps the spec in `.efforts/<effort>/` instead of `.scratch/`. |
| [to-tickets](skills/to-tickets/SKILL.md) | Breaks a plan, spec or conversation into tracer-bullet tickets, each naming what blocks it, and publishes them to the project's tracker, or to `.efforts/<effort>/issues/` on a local one. | Fork of `to-tickets` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`d81f3a1`](https://github.com/mattpocock/skills/tree/d81f3a183412/skills/engineering/to-tickets) (MIT, see `skills/to-tickets/LICENSE.mattpocock`). Changes: agents can load it, so a thinking session runs it itself; with no tracker configured it runs set-up-project instead of telling you to run `setup-matt-pocock-skills`; a local tracker keeps the tickets in `.efforts/<effort>/issues/` instead of `.scratch/`; and tickets are named by title, never by a number alone. |
| [to-pr](skills/to-pr/SKILL.md) | Opens a pull request or rewrites its description: a one-sentence why, reviewer notes, and a visual change outline. | Fork of `visual-pr` from [humanlayer/skills](https://github.com/humanlayer/skills) at [`4e39d8f`](https://github.com/humanlayer/skills/tree/4e39d8fe020f/plugins/visual-pr/skills/visual-pr) (MIT, see `skills/to-pr/LICENSE.humanlayer`). Changes: renamed, a real trigger description, no Mermaid views, the description source saved to `.scratch/` per the folder standard instead of `.humanlayer/`, issues named by title, never by a number alone, review links per changed file in the final report, and a last section, *Things to be aware of*, for decisions made alone, surprises, what's left out and follow-ups, and "Refs", not "Closes", for a ticket waiting for the maintainer's QA. |
| [settle-effort](skills/settle-effort/SKILL.md) | Settles an effort after you approve its pull request: merges it, runs the post-merge follow-ups, carries unfinished work into next-effort tickets and closes the spec and tickets, then settles the session with settle-session. Replaces `close-effort`. | Original. |
| [settle-session](skills/settle-session/SKILL.md) | Settles any session, effort or not, when you say "settle": finishes its work, commits and pushes everything, writes down what it knows in the tracker, a pull request or a handoff, gets every open thread done, filed or decided by you, and releases only clean, unoccupied worktrees proven merged before deleting their branches. The caller session, occupied worktrees and terminal topology stay open. | Original. |

### Design frameworks

| Skill | What it does | Origin |
|---|---|---|
| [low-level-design](skills/low-level-design/SKILL.md) | Designs, explains or redesigns code at the level of modules, classes, files and folders, with reference documents for the principles, OOP concepts and patterns. | Original. Distils Hello Interview's low-level design lessons, cited at the end of each document. |
| [system-design](skills/system-design/SKILL.md) | Designs, explains or redesigns a system at the level of services, data stores, APIs and scale, with reference documents for the core concepts. | Original. Distils Hello Interview's system design lessons, cited at the end of each document. |

### Communication style

| Skill | What it does | Origin |
|---|---|---|
| [show-me](skills/show-me/SKILL.md) | Explains the current topic visually with pseudocode, call trees, file trees, `diff` blocks, or one focused HTML file. | Fork of `show-me` from [humanlayer/skills](https://github.com/humanlayer/skills) at [`ca7c808`](https://github.com/humanlayer/skills/tree/ca7c808/plugins/show-me/skills/show-me) (MIT, see `skills/show-me/LICENSE.humanlayer`). Changes: no Mermaid views, so every view renders as plain text; agents can still load it, where upstream made it user-invocable only in `bba9d13`, because `orchestrate-effort` uses it to show the plan. |
| [show-me-artifact](skills/show-me-artifact/SKILL.md) | Publishes a visual report or a set of decisions as a private Claude artifact, a hosted page read later or on another device, with show-me's principles: one page per topic, self-contained decision cards with a marked recommendation, and a data file plus generator when the page is republished to the same URL. Claude only; elsewhere it falls back to show-me's local HTML file. | Original. Builds on show-me, which it loads for the principles. |

### Agent setup

| Skill | What it does | Origin |
|---|---|---|
| [maintain-environment](skills/maintain-environment/SKILL.md) | Changes what your agents run with: decides whether a change is a permission, a global instruction, a project instruction or a skill, and carries it to every harness, machine and install. Its skill operations install, move, update, fork, publish, remove and audit skills with `npx skills`, upgrade a fork from upstream's latest version while keeping its changes, prompt-audit each new skill in a fresh sub-agent, and measure a skill's run cost on request. | Original. Replaces `maintain-skills`. |
| [set-up-machine](skills/set-up-machine/SKILL.md) | Sets up and audits a machine's agent harnesses from one rule table: one shared global instructions file every harness reads, the global rules each harness enforces, and a pre-tool hook that catches what native rules miss. The agent follows a reference per harness, shows one diff (added, tightened, gaps, extra rules found), applies it on one approval after backing up each file, never removes or loosens a rule the table didn't produce, and runs a verify script. Keeps harness memory off. Covers Claude Code, Codex, opencode and Cursor. | Original. |
| [set-up-project](skills/set-up-project/SKILL.md) | Sets up and audits a project for your agents, after checking the machine with set-up-machine (and running it, on one approval, when the machine differs): `AGENTS.md` as the one rules file with `CLAUDE.md` importing it, the issue tracker, triage labels and domain docs, the folder standard's `.gitignore`, and an audit that flags any project harness file (Claude Code, Codex, opencode, Cursor) weakening a global rule. | Fork of `setup-matt-pocock-skills` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`d81f3a1`](https://github.com/mattpocock/skills/tree/d81f3a183412/skills/engineering/setup-matt-pocock-skills) (MIT, see `skills/set-up-project/LICENSE.mattpocock`). Changes: agents can load it; it checks the machine first; `AGENTS.md` is always the rules file, with `CLAUDE.md` as `@AGENTS.md`, instead of editing whichever exists; optional project environment defaults; the folder standard's `.gitignore` lines; a local tracker keeps issues in `.efforts/<effort>/` instead of `.scratch/`, and says how a ticket is picked up and marked done when the project has no spec or triage labels; the GitHub template adds effort labels and names issues by title; it proposes a `git mv` of an old `CONTEXT.md` or `CONTEXT-MAP.md` to its `GLOSSARY` name; and an audit of each harness's project files against set-up-machine's rule table. |
| [skill-recap](skills/skill-recap/SKILL.md) | Recaps how a session and its sub-agents used their skills, or a scope you name, and ends with findings and a verdict. You start it with `/skill-recap` (Codex: `$skill-recap`) and file them with [to-tickets](skills/to-tickets/SKILL.md). | Original. |

### Daily workflows

| Skill | What it does | Origin |
|---|---|---|
| [calendar](skills/calendar/SKILL.md) | Reads your calendar when a task needs an event: lists events for a date range and checks free time through the Spark CLI, or the Google Calendar connector when Spark Desktop is closed. Every calendar write is denied by a permission rule; creating, changing and answering events stays with you. | Original. |
| [email](skills/email/SKILL.md) | Reads and tidies your email when you ask for an email task: Spark CLI for fast reading, the Gmail connector for marking done, labels and pins. A plain draft stays in chat; a draft saved in Gmail or Spark needs you to name the tool and approve each write. Sending, trash and spam are denied. Includes setup and checks. | Original. The daily workflows adapt the read-only recipes in [readdle/spark-cli-skills](https://github.com/readdle/spark-cli-skills) at [`507d26e`](https://github.com/readdle/spark-cli-skills/tree/507d26e/skills) (MIT); no text copied. |
| [make-explainer](skills/make-explainer/SKILL.md) | Makes a narrated explainer video about the project you're in, with the local [explainer studio](https://github.com/yahyabedirhan/explainer-studio): Remotion and Kokoro, no paid APIs. The project is only read; the video is made and kept in the studio, and you approve the script before any animation. | Original. |
| [wispr-flow-dictionary](skills/wispr-flow-dictionary/SKILL.md) | Tunes the Wispr Flow dictionary from your real dictation history: finds the names, products and commands it mishears, fixes them with backups and undo, and shows whether each fix held. macOS. | Original. The snippet finder and quit-write-relaunch flow follow ideas from [glebis/claude-skills](https://github.com/glebis/claude-skills) (`wispr-analytics`, `wispr-fix`); no code copied. |

## How the skills work

### Effort workflow

An **effort** (a feature, a new app, a refactor) goes from an idea to a merged pull request in one worktree on one branch. A thinking session decides what to build, and a fresh orchestrator builds it, so the builder starts from conclusions instead of debate.

```text
START      init-effort                                   worktree and branch (or a new repo), decided once
             the session host, this session, or paste    starts the thinking session
THINKING   grilling, to-spec, to-tickets                 leaves a spec, tickets and a handoff
HANDOVER   handover                                      ready, prompt, mechanism, started
             handoff                                     writes the handoff in the repo
             the session host, this session, or paste    starts a fresh orchestrator
BUILD      orchestrate-with-handoff → orchestrate-effort
             orchestrating                               the orchestrator's discipline
             implement                                   each ticket, built by a sub-agent
             show-me                                     shows the plan
             to-pr                                       last step: opens the pull request
SETTLE     settle-effort                                 after you approve: merge, follow up, carry over
             settle-session                              leaves nothing hanging, frees what merged
```

Install the family together with `show-me` and these skills from [mattpocock/skills](https://github.com/mattpocock/skills): `grilling`, `prototype`, `tdd` and `code-review`, with `set-up-project` and `set-up-machine` from [Agent setup](#agent-setup) to set each project up. Leave out that repo's `handoff`, `implement`, `to-spec`, `to-tickets` and `setup-matt-pocock-skills`, which the forks here replace, and its `implement-spec` and `pr`, which `orchestrate-effort` and `to-pr` replace. The full path is in [the effort lifecycle](skills/orchestrating/SKILL.md#effort-lifecycle), and where each record goes (spec, tickets, handoff, notes) in the [folder standard](skills/orchestrating/folder-standard.md).

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

How an agent shows its thinking so a reader takes it in quickly. `show-me` picks the smallest view that makes the point, in plain text that reads the same in a terminal, an editor, or on GitHub, and `show-me-artifact` publishes a larger report the same way as a private Claude artifact.

```text
show-me            explains the current topic
  pseudocode · call tree · file tree · diff block · one focused HTML page
show-me-artifact   a report or decision set to read later, as a hosted page
  status first · progress · item tree · tables · decision cards → republished to the same URL
```

### Agent setup

What your agents run with (permissions, instructions and skills), kept in order across every harness and machine. `set-up-machine` sets up and audits each machine's harnesses from one rule table, `set-up-project` each project on top of it, `maintain-environment` decides where a change belongs and carries it from its source to every harness and install, and `skill-recap` looks back over a session for what its skills should change.

```text
where       permission · global instruction · project AGENTS.md · skill · skill reference (no memory)
carry       rerun set-up-machine or set-up-project where the change applies
source      your skills repo, or someone else's
  ↓ npx skills add / update / remove
installs    global (~/.agents/skills) or one project (.agents/skills)
operations  install, update, move, remove, fork, publish
audits      which skills you use, a fresh prompt audit, a run's cost
recap       /skill-recap: how a session used its skills → findings → /to-tickets
```

`set-up-machine` does the same for the rules and instructions every harness runs with. The rule table and the shared global instructions file are declared once; each harness gets its native entries from them:

```text
rules.json                      each global rule once: level, reason, instruction, samples
  ↓ inspect + references        the agent reads each harness's files and its reference
  ↓ one diff, one approval      added, tightened, gaps, extra rules; each file backed up, then written
  ↓ verify.py                   the samples against the hook and Codex's checker; every hook wired
~/.config/agents/AGENTS.md      the shared global instructions: environment defaults, rule lines, personal workflow
~/.config/agents/source.md      the pointer to your workstation repo, where your environment defaults, workflow and personal permissions come from
pre_tool_hook.py                runs before every tool call; reads a command as the shell runs it
Claude Code   ~/.claude/        settings.json: deny and ask entries, the hook, auto memory off; CLAUDE.md imports the shared file
Codex         ~/.codex/         rules/set-up-machine.rules, hooks.json, AGENTS.md → shared file, memories off in config.toml
opencode      ~/.config/opencode/  opencode.json permissions, plugins/set-up-machine.js runs the hook, AGENTS.md → shared file
Cursor        ~/.cursor/        cli-config.json permissions, hooks.json, rules/global-instructions.mdc copies the shared file
~/.agents/skills                your skills repo (the skills-repo environment default), installed globally
run again                       the audit: a diff that changes nothing
```

`set-up-project` does it for one project, on top of the machine. Global rules are the safety rails; a project's own harness files only add allows:

```text
verify.py                       set-up-machine's check first; a machine that fails is set up before the project
  explore, ask, one approval    tracker, triage labels, domain docs, optional environment defaults
  write                         AGENTS.md, CLAUDE.md as @AGENTS.md, .gitignore, docs/agents/
audit                           any project harness file that weakens a global rule
```

### Daily workflows

Everyday tasks outside the code that an agent can take over safely. Each skill changes only what you approve, with sending, deleting and other risky actions left to you.

`email` reads mail only for an email task you asked for, fast with the Spark CLI, and makes every change through the Gmail connector. It archives freely and makes any other change only when you ask. A draft you ask for is written in chat; one saved in Gmail or Spark needs you to name the tool and approve each write in the harness. Permission rules deny sending, trash and spam.

```text
read     Spark CLI, for an email task you asked for: inbox by category, threads, pins, contacts
act      Gmail connector: mark done (archive), labels, pins (stars), saved drafts on approval
how      which tool for which job; what to do and when stays with you
setup    setup.md: both tools, the deny and ask rules, and checks
```

`calendar` reads events and free time whenever a task needs them, with Spark first and the Google Calendar connector when Spark Desktop is closed. It never changes the calendar: permission rules deny every connector write and `spark event`.

`wispr-flow-dictionary` keeps [Wispr Flow](https://wisprflow.ai)'s dictionary accurate for technical vocabulary, where dictation mishears product names, company names and commands. It reads Wispr Flow's local database and writes only its `Dictionary` table, after a backup.

```text
find    terms, formatter swaps and counts over any window (30m, 3h, 2d)
fix     a plain word first; a rule only when a mistake returns; snippets for text you repeat
        every write backs up first, can be undone, and can relaunch the app
check   counts the misheard form since its word was added, to see whether a fix held
```

## Adding a skill

Add its row to its family's table under [Skills](#skills), and fold it into that family's section under [How the skills work](#how-the-skills-work). Prefer an existing family; start a new one only when a skill fits none. A new family gets its own subsection and table under Skills, a line in the list at the top, and a section under [How the skills work](#how-the-skills-work), in the same shape as the others: two sentences and one outline.

## Decision records

`docs/decisions/` records why a skill or workflow is shaped the way it is, one dated entry per decision. Read it before changing the skills it covers. It is not installed. `docs/decisions/skill-writing.md` holds the rules for writing any skill here.

## Research

`docs/research/` holds the fact-finding behind open issues: how the harnesses, `herdr`, git and GitHub actually behave, with sources and test notes. Each issue links the notes it relies on. It is not installed.

## License

MIT, see [`LICENSE`](LICENSE). Forked skills keep their upstream license next to their `SKILL.md`.
