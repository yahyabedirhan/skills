---
name: treehouse
description: Lease, list, return and destroy git worktrees with `treehouse`'s pre-warmed pool. Use when the project's worktree tool is `treehouse`, or when another skill says to make or remove a worktree with it.
---

# Treehouse

`treehouse` keeps a pool of pre-warmed git worktrees, with dependencies already installed, so a new worktree is ready in seconds. Create, return and remove the worktree with `treehouse`, and create its branch with `get -b`. Return a worktree to the pool rather than destroying it, so the next effort finds one ready; destroy only one the pool shouldn't keep.

| Need | Command | Notes |
|---|---|---|
| A durable worktree for an effort | `treehouse get --lease --lease-holder <effort> -b <branch>` | Prints only the path. `--json` adds the lease identity. A leased worktree is never handed out again or pruned until returned. |
| See the pool | `treehouse status` | |
| Give a worktree back, keeping it in the pool | `treehouse return <path>` | Kills every process still running in the worktree, including this session if it runs there. With untracked files it asks before deleting them; with no terminal to answer, it keeps the worktree leased and exits 3. `--force` deletes the untracked files without asking. It fails if a process comes back after it ends them, such as an editor's helpers: close the editor first. |
| Remove a worktree for good | `treehouse destroy <path> --include-leased --yes` | Without `--yes`, it only lists what it would remove. It removes a leased worktree only when you name its exact path, so `--all` never removes one. It skips a worktree with unlanded work unless you pass `--include-unlanded`, which deletes that work, and one with a process running in it unless you pass `--include-in-use`, which ends the process first. A named worktree it skips makes it exit 1, naming the flag it needs. |

## A worktree on a new branch

A leased worktree starts on a detached HEAD unless `get` makes its branch. `get --lease` fetches origin first and cuts the worktree from the remote default branch, and `-b <branch>` creates the effort's branch there with no upstream, so a bare `git push` can't push to the default branch before the first `git push -u`. `-b` fails if the branch already exists.

## Gotchas

- `return` keeps ignored files, even with `--force`, and the next effort that leases the worktree finds them, such as an old `.scratch/` or build output. Copy out what's worth keeping, and clear the rest before returning.
- `destroy` removes everything in the worktree, ignored files included, without warning. Copy out anything worth keeping first.
- `destroy` treats any shell or agent running in the worktree as a live process. Close whatever runs there first, such as its terminal or agent workspace, or pass `--include-in-use` when ending it is fine.
- These facts are from `treehouse` v3.1.0, tested on a throwaway pool; check them again after an update.
