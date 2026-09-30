---
name: treehouse
description: Lease, list, return and destroy git worktrees with Treehouse's pre-warmed pool. Use when the worktree-tool default is Treehouse, or when another skill says to make or remove a worktree with it.
---

# Treehouse

`treehouse` keeps a pool of pre-warmed git worktrees, with dependencies already installed, so a new worktree is ready in seconds. It owns the worktree's life; git owns the branch inside it. These are its everyday commands and gotchas; `treehouse <command> --help` has the rest.

| Need | Command | Notes |
|---|---|---|
| A durable worktree for an effort | `treehouse get --lease --lease-holder <effort>` | Prints only the path. `--json` adds the lease identity. A leased worktree is never handed out again or pruned until returned. |
| See the pool | `treehouse status` | `--json` for scripts. |
| Give a worktree back, keeping it in the pool | `treehouse return <path>` | Terminates lingering processes, this session's too when it runs there. `--force` cleans and resets without prompting. |
| Remove a worktree for good | `treehouse destroy <path> --include-leased --yes` | A dry run without `--yes`. A leased worktree goes only when its exact path is named; `--all` never removes it. Refuses unlanded work unless `--include-unlanded` (data loss). |

## A worktree on a new branch

A leased worktree comes detached; put the effort's branch in it:

```bash
treehouse get --lease --lease-holder <effort>                      # prints the worktree path
git -C <path> switch --no-track -c <branch> origin/<default-branch>
```

`get --lease` fetches origin first, so the remote default branch is current. `--no-track` leaves the branch without an upstream until its first push, because a branch that tracks the default branch makes a bare `git push` target it.

## Gotchas

- `return` deletes the worktree's ignored and untracked files without asking, and `destroy` removes ignored folders such as `.scratch/` or build output without warning, since they don't count as unfinished work. Copy out anything worth keeping first.
- `destroy` treats any shell or agent running in the worktree as a live process and skips the worktree. Close whatever runs there first, such as its terminal or agent workspace.
