---
name: set-up-project
description: Set up or audit a project for coding agents - the machine checked first with set-up-machine, AGENTS.md as the one rules file with CLAUDE.md importing it, the issue tracker, triage labels and domain docs, the folder standard's .gitignore, and project harness files kept allow-only. Use for a new or existing project, to audit a project's agent setup, or when a skill finds no issue tracker configured.
---

# Set up project

Scaffold and audit the per-repo configuration the skills assume:

- **Rules file**: `AGENTS.md`, which every harness reads; `CLAUDE.md` holds only `@AGENTS.md`, since Claude Code skips a project's `AGENTS.md` when a `CLAUDE.md` exists
- **Issue tracker**: where issues live (GitHub by default; local markdown is also supported out of the box)
- **Triage labels**: the strings used for the five canonical triage roles
- **Domain docs**: where `GLOSSARY.md` and ADRs live, and the consumer rules for reading them
- **Folder standard**: the `.gitignore` lines of [orchestrating/folders.md](../orchestrating/folders.md)
- **Allow-only project permissions**: the global rules are the machine's safety rails, and a project's own harness files only add convenience. The **audit** flags every project file that weakens a global rule.

`scripts/set_up_project.py` does the deterministic part: it checks the machine through **set-up-machine** (installed beside this skill; it reads that skill's rule table), writes `AGENTS.md`, `CLAUDE.md` and the `.gitignore` lines after one approval, and audits. The rest is prompt-driven: explore, present what you found, confirm with the user, then write.

## Process

### 1. Plan

Run `python3 <this skill>/scripts/set_up_project.py plan --project <repo root>`. It writes nothing.

- **Exit 3: the machine differs** from set-up-machine's table, and the output is set-up-machine's plan. Show it to the user unedited, ask for one approval of the whole diff (set-up-machine's SKILL.md, step 3, explains its lines), run the apply command printed under it, then run this step again.
- Otherwise the output is the project plan: `added` and `updated` files, `todo` lines for the steps below, and the audit's lines per harness file.

Done when you hold a project plan whose first section reads `Machine  set-up-machine reports no changes`.

### 2. Explore

Look at the current repo to understand its starting state. Read whatever exists; don't assume:

- `git remote -v` and `.git/config`: is this a GitHub repo? Which one?
- `AGENTS.md` and `CLAUDE.md` at the repo root: does either exist? Is there already an `## Agent skills` or `## Defaults` section in either?
- `GLOSSARY.md` and `GLOSSARY-MAP.md` at the repo root
- `docs/adr/` and any `src/*/docs/adr/` directories
- `docs/agents/`: does this skill's prior output already exist?
- `.efforts/`: a sign that a local-markdown issue tracker is already in use
- Is the `triage` skill installed? (a `triage` skill folder alongside this one, or `triage` in your available skills.) This decides whether Section B runs at all.
- Monorepo signals: a `pnpm-workspace.yaml`, a `workspaces` field in `package.json`, or a populated `packages/*` with its own `src/`. These are present only in a genuinely large multi-package repo; their absence means single-context, which is almost every repo.
- A tool the project's own docs require for a role skills name (a worktree tool in a `docs/worktrees.md`, a session host its scripts assume). This decides whether Section D runs.

### 3. Present findings and ask

Summarise what's present and what's missing. Then take the sections in order. One section, one answer, then the next.

Lead each section with the recommended answer so the user can accept it in a word. Give a one-line explainer only when the choice genuinely branches; skip the section entirely when exploration already settled it (Section B when `triage` isn't installed, Section C when there's no monorepo, Section D when the project names no tool for a role).

**Section A: Issue tracker.**

> Explainer: The "issue tracker" is where issues live for this repo. Skills like `to-tickets`, `triage`, and `to-spec` read from and write to it. They need to know whether to call `gh issue create`, write a markdown file under `.efforts/`, or follow some other workflow you describe. Pick the place you actually track work for this repo.

Default posture: these skills were designed for GitHub. If a `git remote` points at GitHub, propose that. If a `git remote` points at GitLab (`gitlab.com` or a self-hosted host), propose GitLab. Otherwise (or if the user prefers), offer:

- **GitHub**: issues live in the repo's GitHub Issues (uses the `gh` CLI)
- **GitLab**: issues live in the repo's GitLab Issues (uses the [`glab`](https://gitlab.com/gitlab-org/cli) CLI)
- **Local markdown**: issues live as files under `.efforts/<effort>/` in this repo (good for solo projects or repos without a remote)
- **Other** (Jira, Linear, etc.): ask the user to describe the workflow in one paragraph; the skill will record it as freeform prose

Record the choice in `docs/agents/issue-tracker.md`. The GitHub and GitLab templates carry a "PRs as a request surface" flag, defaulted **off**. Leave it off and don't raise it: a user who wants external PRs in the triage queue can flip the flag in the file later.

**Section B: Triage label vocabulary.** Skip this section entirely if the `triage` skill isn't installed (exploration told you), since an uninstalled skill needs no labels.

If it is installed, ask exactly one question:

> Do you want to keep the default triage labels? (recommended: **yes**)

The defaults are the five canonical roles, each label string equal to its name: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. On **yes**, write them as-is. Only if the user says no, usually because their tracker already uses other names (e.g. `bug:triage` for `needs-triage`), collect the overrides so `triage` applies existing labels instead of creating duplicates.

**Section C: Domain docs.** Default to **single-context** (one `GLOSSARY.md` + `docs/adr/` at the repo root). This fits almost every repo; write it without asking.

Offer **multi-context** (a root `GLOSSARY-MAP.md` pointing to per-context `GLOSSARY.md` files) only when exploration found monorepo signals. Then confirm which layout they want.

**Section D: Project defaults.** Recommend **none**. Ask only when exploration found a tool the project requires for a role: then propose a `## Defaults` row for it, which overrides the user's global row for this project. [agents-md.md](agents-md.md), *The Defaults table*, says what may go there.

### 4. Confirm and write

Show the user a draft of:

- The `## Agent skills` block to add to `AGENTS.md`, and any `## Defaults` rows
- The contents of `docs/agents/issue-tracker.md`, `docs/agents/domain.md`, and `docs/agents/triage-labels.md` (the last only when `triage` is installed)
- The plan's `added` and `updated` lines, and each `CLAUDE.md` line the plan lists as `todo`, with where it goes in `AGENTS.md`

Let them edit, then take one approval for all of it. Then write:

1. Run the apply command the plan printed. It creates `AGENTS.md` (or moves a lone `CLAUDE.md`'s lines into it), makes `CLAUDE.md` import it, and adds the `.gitignore` lines.
2. Edit `AGENTS.md`, never `CLAUDE.md`, starting from [agents-md.md](agents-md.md) when it's new. Move each `CLAUDE.md` line the plan listed into it, so `CLAUDE.md` is left holding `@AGENTS.md` alone.
3. If an `## Agent skills` block already exists, update its contents in place rather than appending a duplicate. Don't overwrite user edits to the surrounding sections. The block is in [agents-md.md](agents-md.md). Include the `### Triage labels` sub-block, and write `docs/agents/triage-labels.md`, only when `triage` is installed and Section B ran. When it isn't, both are omitted.
4. Write the docs files using the seed templates in this skill folder as a starting point:
   - [issue-tracker-github.md](./issue-tracker-github.md): GitHub issue tracker
   - [issue-tracker-gitlab.md](./issue-tracker-gitlab.md): GitLab issue tracker
   - [issue-tracker-local.md](./issue-tracker-local.md): local-markdown issue tracker
   - [triage-labels.md](./triage-labels.md): label mapping (only if `triage` is installed)
   - [domain.md](./domain.md): domain doc consumer rules + layout

   For "other" issue trackers, write `docs/agents/issue-tracker.md` from scratch using the user's description.

Done when every `todo` line of the plan is written.

### 5. Audit

Run the plan again. Its `Audit:` line and harness sections judge each project file against the global rules; [references/project-files.md](references/project-files.md) has the facts behind every line and how to fix one. Read it before explaining a `weakens` or `gap` line.

- `weakens`: a global rule is weaker in some harness. Explain which and why, and propose the fix: remove the entry, or narrow it to the project's own commands. The file is the project's, so change it only on the user's approval.
- `overlaps`: an allow that covers a rule's command while the rule still holds. Propose narrowing it.
- `extra` and `gap`: name each in the report.

Done when the plan ends `No changes.` and `Audit: passed.`, or the user has chosen to keep a `weakens` entry: then the audit stays failed, and the report names that entry.

### 6. Done

Tell the user the setup is complete, what the audit found, and which skills will now read from these files. Mention they can edit `AGENTS.md` and `docs/agents/*.md` directly later; re-running this skill audits the project again, and switches issue trackers when they want to. Leave the commit to the user or the skill that called this one.
