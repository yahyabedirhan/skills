# Design: set-up-project

This page explains how [`set-up-project`](../../skills/set-up-project/SKILL.md) is built, for whoever changes it.
A newcomer needs two facts first:

- The **agent** sets up one project's agent files: `AGENTS.md`, `CLAUDE.md`, the issue tracker, triage labels, domain docs, the release page and the `.gitignore` lines.
It explores, presents, takes one approval, then writes.
- Running it again is the **audit**: it reads the project's harness files against set-up-machine's rule table and flags each entry that weakens a global rule.

## Requirements

1. **Machine first.** The machine passes set-up-machine's verifier (exit 0) before the project is set up.
2. **One rules file.** `AGENTS.md` is the rules file. `CLAUDE.md` is `@AGENTS.md` or a link to it.
3. **Skill configuration.** `docs/agents/` holds the issue tracker, the triage labels when `triage` is installed, the domain docs, and the release page when the project releases.
4. **Allow-only.** A project's harness files only add allows. The audit fails on `weakens`.
5. **Out of scope:** the machine's own setup, which set-up-machine does, and the project's code.

## Entities and relationships

- **Project files**: `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/agents/*.md`.
- **Seed templates**: the files beside `SKILL.md` that the agent copies into `docs/agents/`.
- **Project harness files**: `.claude/settings*.json`, `.cursor/cli.json`, `opencode.json`, `.codex/config.toml`.
- **Rule table**: read from the installed set-up-machine skill.
- **Shared release rules**: `setup/releasing.md` in the user's workstation repo, found through the pointer; optional.

```text
set-up-project ──runs──▶ set-up-machine's verify.py (pass: exit 0)
set-up-project ──copies──▶ seed templates ──▶ docs/agents/
set-up-project ──reads──▶ shared release rules ──over──▶ releasing.md seed ──▶ docs/agents/releasing.md
set-up-project ──reads──▶ project harness files ──against──▶ rules.json samples
```

## Class design

```text
skills/set-up-project/
├── SKILL.md                    # check the machine, explore, ask per section, write, audit
├── agents-md.md                # the AGENTS.md seed
├── issue-tracker-*.md          # seed per tracker
├── triage-labels.md, domain.md # seeds
├── releasing.md                # the release page seed: what ships, the release order, the roles
└── references/
    └── project-files.md        # what each harness lets a project file do to a global rule
```

## Implementation (traced)

```text
set-up-project
  1 check     verify.py exits 0, or run set-up-machine first
  2 explore   remote, AGENTS.md, CLAUDE.md, glossary, docs/agents/, triage, monorepo signals, release signals, shared release rules
  3 ask       sections A to E, one answer each
  4 write     one approval for the drafts, then the files
  5 audit     each project harness file against each row's samples → weakens | overlaps | extra | gap
            and the release page against the shared release rules
```

## Extensibility

| Change | What you touch |
|---|---|
| A new issue tracker | one seed template and one option in `SKILL.md` > 'Section A: issue tracker' |
| A new harness | its project files in `references/project-files.md` and in the audit list |
| A new standard file for every project | a draft line in step 4 |
| A new shared release rule | the user's `setup/releasing.md`; the seed only when every user would want it |
