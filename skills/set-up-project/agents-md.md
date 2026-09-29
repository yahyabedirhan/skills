# AGENTS.md template

The project's one rules file. Every harness reads it (Claude Code through `CLAUDE.md`'s `@AGENTS.md`), so it holds everything a teammate or contributor needs to work on the project, and nothing personal: this person's own workflow stays in their global instructions. Keep only the sections that apply.

```markdown
# Agent instructions

[What a teammate needs here: the project's commands, conventions, and where things live.]

## Defaults

This project's own values for the roles skills name. Each row overrides the global instructions' row of the same role, for this project only; a role left out keeps the global value.

| Role | Default |
|---|---|
| worktree-tool | [the tool, and where the project documents it] |

## Agent skills

### Issue tracker

[one-line summary of where issues are tracked]. See `docs/agents/issue-tracker.md`.

### Triage labels

[one-line summary of the label vocabulary]. See `docs/agents/triage-labels.md`.

### Domain docs

[one-line summary of layout: "single-context" or "multi-context"]. See `docs/agents/domain.md`.
```

## The Defaults table

Optional, and only for a role every contributor to this project uses the same way: a worktree tool the project's scripts assume, a session host its docs describe. A tool one person prefers belongs in that person's global Defaults, never here. The roles and what each names are in **set-up-machine**'s `references/global-instructions.md` (*The Defaults roles*); a new role is a new row there first.
