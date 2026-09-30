---
name: treehouse
description: Lease, list, return and destroy git worktrees with `treehouse`'s pre-warmed pool. Use when the project's worktree tool is `treehouse`, or when another skill says to make or remove a worktree with it.
---

# Treehouse

`treehouse` keeps a pool of pre-warmed git worktrees, with dependencies already installed, so a new worktree is ready in seconds. Create, return and remove the worktree with `treehouse`; create and switch the branch inside it with git. Return a worktree to the pool rather than destroying it, so the next effort finds one ready; destroy only one the pool shouldn't keep.

| Need | Command | Notes |
|---|---|---|
| A durable worktree for an effort | `treehouse get --lease --lease-holder <effort>` | Prints only the path. `--json` adds the lease identity. A leased worktree is never handed out again or pruned until returned. |
| See the pool | `treehouse status` | |
| Give a worktree back, keeping it in the pool | `treehouse return <path>` | Kills every process still running in the worktree, including this session if it runs there. With untracked files it asks before deleting them; with no terminal to answer, it prints `Aborted`, keeps the worktree leased and still exits 0, so check its output. `--force` deletes the untracked files without asking. |
| Remove a worktree for good | `treehouse destroy <path> --include-leased --yes` | Without `--yes`, it only lists what it would remove. It removes a leased worktree only when you name its exact path, so `--all` never removes one. It skips a worktree with unlanded work unless you pass `--include-unlanded`, which deletes that work, and one with a process running in it unless you pass `--include-in-use`, which ends the process first. |

## A worktree on a new branch

A leased worktree starts on a detached HEAD. Create the effort's branch in it from the remote default branch:

```bash
treehouse get --lease --lease-holder <effort>                      # prints the worktree path
git -C <path> switch --no-track -c <branch> origin/<default-branch>
```

`get --lease` fetches origin first, so the remote default branch is current. `--no-track` leaves the branch without an upstream until its first push, because a branch that tracked the default branch would make a bare `git push` push to the default branch.

## Gotchas

- `return` keeps ignored files, even with `--force`, and the next effort that leases the worktree finds them, such as an old `.scratch/` or build output. Copy out what's worth keeping, and clear the rest before returning.
- `destroy` removes everything in the worktree, ignored files included, without warning. Copy out anything worth keeping first.
- `destroy` treats any shell or agent running in the worktree as a live process. Close whatever runs there first, such as its terminal or agent workspace, or pass `--include-in-use` when ending it is fine.
- These facts are from `treehouse` v2.3.0; check them again after an update.
