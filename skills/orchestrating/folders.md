# Folder Standard

Where agents keep their records in a project. Every skill that writes one points here instead of restating paths.

```text
<repo>/
├── .handoff/<date>-<topic>.md     tracked   session → session
├── .efforts/<effort>/             tracked   local-tracker projects only: spec.md, issues/
├── docs/agents/issue-tracker.md   tracked   which tracker the repo uses
├── docs/assets/<topic>/           tracked   screenshots worth keeping
└── .scratch/                      ignored   agent notes, logs, temp files, PR description source
    .claude/worktrees/             ignored
```

- **`.handoff/`**: one handoff per session that hands over, named `<date>-<topic>.md` (the topic is the effort's name when there is one). It is committed with the work it describes, so a fresh worktree sees it. A project that names its own handoff folder in its instructions uses that one.
- **`.efforts/<effort>/`**: only on a local-files tracker. `spec.md` and `issues/<NN>-<slug>.md`, written by `to-spec` and `to-tickets`. With a hosted tracker (GitHub, Linear) the spec and tickets live there, and a project has no `.efforts/`. Without an effort, `<effort>` is a short slug for the feature.
- **`docs/agents/issue-tracker.md`**: says which tracker the repo uses and how to reach it, so a skill knows whether to publish to the tracker or to `.efforts/`.
- **`docs/assets/<topic>/`**: screenshots and other images worth keeping, such as ones a pull request or a doc links to.
- **`.scratch/`**: the agent's own notes area, always gitignored: notes, logs, temporary files, and the source of a pull request's description (`.scratch/pr-<number>/description.md`, beside any `show-me-*.html` made for it). GitHub holds the description itself, and the pull request's last section carries what the agent wants the maintainer to know, so nothing here needs keeping. Before a worktree is removed, copy anything worth keeping out of it (to `docs/assets/`, a handoff, or the tracker).
- **Nothing is deleted with `rm -rf`.** What's no longer needed (a delegate's temporary folder, an old log, a throwaway script) moves into `.scratch/` with `mv`, where git ignores it and a mistake can be undone; a tracked file goes with `git rm`, so its history keeps it. Permission checks refuse `rm -rf`, and a refused command bundled with a commit reads as a refused commit.
- **Decision records** stay wherever each project keeps them.

There is no `tmp/`, no `.prs/` and no vendor-named folder: one ignored folder holds everything temporary.

## Setting up a project

Add both ignored paths to `.gitignore`:

```gitignore
.scratch/
.claude/worktrees/
```

Write `docs/agents/issue-tracker.md` when the project has none.

## Migrating an existing project

Move each old folder with `git mv`, so its history follows, and commit the move on its own:

| Old | New |
|---|---|
| `.scratch/<effort>/` holding tracked `spec.md` and `issues/` | `.efforts/<effort>/` |
| `to-pr`'s old description folder (`tasks/<slug>/` under a vendor-named dot folder) | the description is on GitHub; keep any image worth keeping in `docs/assets/<topic>/`, then `git rm` the rest |
| `tmp/` | `.scratch/` |

Then add the `.gitignore` lines above. Nothing is lost: every tracked record moves, lives on GitHub, or stays readable in git history.
