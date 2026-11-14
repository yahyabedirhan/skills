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

### Roadmap

[Only in roadmap mode.] The issue tracker holds only the agent specs and tickets, and the roadmap and the notes hold the rest of the planning. Before you plan, start, deliver or settle work, read `docs/agents/roadmap.md`.

### Notes

[Only in roadmap mode.] The project's history and thinking live in the notes. Before you need that history, or write a note, read `docs/agents/notes.md`.

### Issue tracker

[one-line summary of where issues are tracked]. See `docs/agents/issue-tracker.md`.

### Triage labels

[one-line summary of the label vocabulary]. See `docs/agents/triage-labels.md`.

### Domain docs

[one-line summary of layout: "single-context" or "multi-context"]. See `docs/agents/domain.md`.

### Releases

[one-line summary: where the version lives and where it publishes]. Before a release, and after merging a version bump, follow `docs/agents/releasing.md`.
```

## Environment defaults

Optional, and only for a role every contributor uses the same way, such as a worktree tool the project's scripts assume. A tool one person prefers belongs in their own global environment defaults. `/set-up-machine`'s `references/global-instructions.md` > 'Roles' lists the roles.

## Roadmap mode

In roadmap mode, the `## Agent skills` block names every file of the `docs/agents/` set: the `### Roadmap` sub-block for `docs/agents/roadmap.md`, the `### Notes` sub-block for `docs/agents/notes.md`, and the issue tracker, triage labels, domain docs and releases sub-blocks, whether or not `triage` is installed.
