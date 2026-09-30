# Branch cleanup

## Proving work merged

Delete a branch or remove a worktree only when its work is proven merged; keep anything you can't prove, and name it in the report with the reason. Run `git fetch --prune` first, so the remote default branch is current. Three proofs count:

- **Reachable:** `git merge-base --is-ancestor` with the branch and the remote default branch succeeds, as after a merge commit or a fast-forward. It is the cheapest, so try it first.
- **Matched by patch:** `git cherry` with the remote default branch and the branch prints no `+` line, as after a rebase or an unchanged cherry-pick. A `+` proves nothing either way.
- **In the merged pull request's head:** `gh pr view --json state,headRefOid` shows `MERGED`, and the branch's tip is that head or an ancestor of it. A leftover delegate branch counts when its ticket's commit is in that head and the branch holds nothing else.

A squash merge, or a commit changed while it was integrated, fails the first two proofs; only the merged pull request's head proves it.

## Freeing worktrees and branches

- Leave a worktree where an agent is still working, since freeing it stops that agent.
- Free worktrees before their branches, with `<worktree-tool>`, since git won't delete a branch a worktree has checked out. Remove one without `--force`: a worktree that needs it isn't clean.
- Delete a local branch with `git branch -d` for the reachable proof, and `git branch -D` when only the other two prove it.
- Before deleting a remote branch, check it still exists with `git ls-remote --heads origin`; the repo may have deleted it on merge.
- Run each deletion as its own call, so a refused one stops only itself.
- Free this session's own worktree last, from outside it, after the report.
