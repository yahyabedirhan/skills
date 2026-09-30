---
name: treehouse
description: Lease, list, return and destroy git worktrees with Treehouse's pre-warmed pool. Use when the project's worktree tool is Treehouse, or when another skill says to make or remove a worktree with it.
---

# Treehouse

`treehouse` keeps a pool of pre-warmed git worktrees, with dependencies already installed, so a new worktree is ready in seconds. Create, return and remove the worktree with `treehouse`; create and switch the branch inside it with git.

| Need | Command | Notes |
|---|---|---|
| A durable worktree for an effort | `treehouse get --lease --lease-holder <effort>` | Prints only the path. `--json` adds the lease identity. A leased worktree is never handed out again or pruned until returned. |
| See the pool | `treehouse status` | |
| Give a worktree back, keeping it in the pool | `treehouse return <path>` | Kills every process still running in the worktree, including this session if it runs there. `--force` cleans and resets without prompting. |
| Remove a worktree for good | `treehouse destroy <path> --include-leased --yes` | Without `--yes`, it only lists what it would remove. It removes a leased worktree only when you name its exact path, so `--all` never removes one. It refuses a worktree with unlanded work unless you pass `--include-unlanded`, which deletes that work. |

## A worktree on a new branch

A leased worktree starts on a detached HEAD. Create the effort's branch in it from the remote default branch:

```bash
treehouse get --lease --lease-holder <effort>                      # prints the worktree path
git -C <path> switch --no-track -c <branch> origin/<default-branch>
```

`get --lease` fetches origin first, so the remote default branch is current. `--no-track` leaves the branch without an upstream until its first push, because a branch that tracked the default branch would make a bare `git push` push to the default branch.

## Gotchas

- `return` deletes the worktree's ignored and untracked files without asking, and `destroy` removes ignored folders such as `.scratch/` or build output without warning, since they don't count as unfinished work. Copy out anything worth keeping first.
- `destroy` treats any shell or agent running in the worktree as a live process and skips the worktree. Close whatever runs there first, such as its terminal or agent workspace.
