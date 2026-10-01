# AGENTS.md template

The project's one rules file. Every harness reads it. Claude Code reads it through `CLAUDE.md`, which is either the line `@AGENTS.md` or a symlink to this file. It holds everything a teammate or contributor needs to work on the project, and nothing personal: this person's own workflow stays in their global instructions. Keep only the sections that apply.

```markdown
# Agent instructions

[What a teammate needs here: the project's commands, conventions, and where things live.]

## Environment defaults

This project's tools for the roles skills name; each row overrides the global one.

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

## Environment defaults

Optional, and only for a role every contributor uses the same way (a worktree tool the project's scripts assume). A tool one person prefers belongs in their own global environment defaults. The roles are in `/set-up-machine`'s `references/global-instructions.md`.
