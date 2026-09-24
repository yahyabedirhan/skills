---
name: init-effort-with-herdr
description: Start a new effort in a Treehouse worktree opened as a Herdr workspace, and launch its thinking agent there. For terminal setups running Herdr and Treehouse.
argument-hint: "The idea, in a sentence or a paragraph"
disable-model-invocation: true
---

# Init Effort With Herdr

The Herdr path's start: the same start as **init-effort**, with the setup automated.

- **`treehouse` owns the worktree**: it leases pre-warmed worktrees from a pool and refuses to destroy unfinished work. Its daily operations are in [treehouse.md](treehouse.md).
- **Git owns the branch**, created inside the worktree.
- **`herdr` owns the view and the sessions**: a workspace per worktree, a tab per agent. Its daily operations are in [herdr.md](herdr.md).

Create worktrees only with `treehouse`: `git worktree add` and `herdr worktree create` put them outside the pool, where nothing tracks or cleans them.

## Before you start

Check that this session runs inside Herdr (`HERDR_ENV=1`) and that `treehouse` is installed. If either fails, say so, suggest `/init-effort <idea>`, and stop.

## 1. Name the effort

Propose a kebab-case **effort name** and a branch named the project's way (by default `<area>/<effort>`), and confirm both with the user.

## 2. Set up the worktree and workspace

```bash
treehouse get --lease --lease-holder <effort>                      # prints the worktree path
git -C <path> switch --no-track -c <branch> origin/<default-branch>
herdr worktree open --path <path> --label <effort> --no-focus
```

## 3. Launch the thinking agent

In the new workspace's first tab: start the user's preferred agent (from their instructions; default `claude`) named after the effort, label the tab `<effort> · Thinking · <harness>` (see Tab names below), and send it:

```text
/grill-with-docs <the idea>

This is effort <effort> on branch <branch>, in worktree <path>. Think it through here:
grilling, a prototype if a question needs one, then /to-spec and /to-tickets.
When the tickets are written, run /orchestrate-with-herdr to hand over.
```

Tell the user the workspace and tab where the thinking runs, and stop: this session's part is done.

## Tab names

An effort's tabs are labelled `<effort> · <role> · <harness>`, so the user can tell them apart at a glance: the role is `Thinking` or `Orchestrator`, and the harness is short: `CC` for Claude Code, `Codex`, `OpenCode`, `Cursor`, or the harness's own name. When a tab already has a label, append ` · <role> · <harness>` to it instead of replacing it.

## After the pull request merges

When the user says the pull request merged, close the effort:

1. Close the effort's Herdr workspace (`herdr workspace close`).
2. Copy anything worth keeping from the worktree's ignored folders to the main checkout.
3. `treehouse destroy <path> --include-leased --yes`
4. In the main checkout: `git switch <default-branch> && git pull --prune`, then `git branch -d <branch>`. After a squash merge `-d` refuses; confirm with the user before `-D`.
