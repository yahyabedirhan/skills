# Command reference

The git and gh commands `/close-effort` runs, with their pitfalls. Run each commit, push and deletion as its own call, so a refused one stops only itself.

## Finding the pull request

From a checkout that isn't on the effort's branch, list pull requests by head branch with `gh pr list --head` and `--state all`; without `--state all`, a merged pull request doesn't show.

## Merging

Merge with `gh pr merge` and the project's usual method, and leave out `--delete-branch`: it deletes branches before they are proven merged, and switches the current checkout to the default branch.

## The follow-up branch

Pull in the main checkout only when it is clean and already on the default branch; otherwise work from the remote default branch. Make the follow-up worktree with `git worktree add --no-track -b` from the remote default branch: `--no-track` leaves the branch without an upstream until its first push, since a branch that tracks the default branch makes a bare `git push` target it.

## The next effort's label

`gh issue create --label` fails when the label doesn't exist yet, so create the next effort's `effort:` label first with `gh label create`.

## Ignored files

`git status --ignored` lists ignored files, which plain `git status` hides and removing a worktree deletes. Save them where `/orchestrating`'s `folder-standard.md` puts each kind, and copy editor settings like `.vscode/` to the main checkout.

## Proving work merged

Run `git fetch --prune` first, so the remote default branch is current. Three proofs count:

- **Reachable:** `git merge-base --is-ancestor` with the branch and the remote default branch succeeds, as after a merge commit or a fast-forward. It is the cheapest, so try it first.
- **Matched by patch:** `git cherry` with the remote default branch and the branch prints no `+` line, as after a rebase or an unchanged cherry-pick. A `+` proves nothing either way.
- **In the merged pull request's head:** `gh pr view --json state,headRefOid` shows `MERGED`, and the branch's tip is that head or an ancestor of it. A leftover delegate branch counts when its ticket's commit is in that head and the branch holds nothing else.

A squash merge, or a commit changed while it was integrated, fails the first two proofs; only the merged pull request's head proves it.

## Freeing worktrees and branches

- Free worktrees before their branches, since git won't delete a branch a worktree has checked out. Remove one without `--force`: a worktree that needs it isn't clean.
- Delete a local branch with `git branch -d` for the reachable proof, and `git branch -D` when only the other two prove it.
- Before deleting a remote branch, check it still exists with `git ls-remote --heads origin`; the repo may have deleted it on merge.
