# Folder standard

The folders where agents keep their records in a project, what each one holds, and how a project adopts them.

## Layout

```text
<repo>/
├── .handoff/<date>-<topic>.md     tracked   session → session
├── .efforts/<effort>/             tracked   local-tracker projects only: spec.md, issues/
├── docs/agents/issue-tracker.md   tracked   which tracker the repo uses
├── docs/assets/<topic>/           tracked   screenshots worth keeping
├── .scratch/                      ignored   agent notes, logs, temp files, PR description source
└── .claude/worktrees/             ignored
```

There is no `tmp/`, no `.prs/` and no vendor-named folder: one ignored folder holds everything temporary.

## Folder contents

- **`.handoff/`**: one handoff per session that hands over, named `<date>-<topic>.md`, where the topic is the effort's name when there is one. It is committed with the work it describes, so a fresh worktree sees it. A project that names its own handoff folder in its instructions uses that one.
- **`.efforts/<effort>/`**: only on a local-files tracker. `spec.md` and `issues/<NN>-<slug>.md`, written by `/to-spec` and `/to-tickets`. With a hosted tracker, such as GitHub or Linear, the spec and tickets live there, and a project has no `.efforts/`. Without an effort, `<effort>` is a short slug for the feature.
- **`docs/agents/issue-tracker.md`**: says which tracker the repo uses and how to reach it, so a skill knows whether to publish to the tracker or to `.efforts/`.
- **`docs/assets/<topic>/`**: screenshots and other images worth keeping, such as ones a pull request or a doc links to.
- **`.scratch/`**: the agent's own notes area, always gitignored: notes, logs, temporary files, and the source of a pull request's description, at `.scratch/pr-<number>/description.md` beside any `show-me-*.html` made for it. GitHub holds the description itself, so nothing here needs keeping. Before a worktree is removed, copy anything worth keeping out of it, into `docs/assets/`, a handoff or the tracker.
- **Decision records** stay wherever each project keeps them.

## Removal without `rm -rf`

Move what's no longer needed, such as a delegate's temporary folder, an old log or a throwaway script, into `.scratch/` with `mv`, where git ignores it and a mistake can be undone; remove a tracked file with `git rm`, so its history keeps it. Permission checks refuse `rm -rf`.

## Project setup

`/set-up-project` applies this section. It adds both ignored paths to `.gitignore`:

```gitignore
.scratch/
.claude/worktrees/
```

and writes `docs/agents/issue-tracker.md` when the project has none.

## Migration from older layouts

Move each old folder with `git mv`, so its history follows, and commit the move on its own:

| Old | New |
|---|---|
| `.scratch/<effort>/` holding tracked `spec.md` and `issues/` | `.efforts/<effort>/` |
| `/to-pr`'s old description folder, `.humanlayer/tasks/<slug>/` | the description is on GitHub; keep any image worth keeping in `docs/assets/<topic>/`, then `git rm` the rest |
| `tmp/` | `.scratch/` |

Then add the `.gitignore` lines above. Nothing is lost: every tracked record moves, lives on GitHub, or stays readable in git history.
