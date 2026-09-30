# Commands for closing an effort

The pitfalls behind the git and gh commands that **close-effort** runs to merge an effort's pull request and free its branches and worktrees. Run each commit, push and deletion as its own call, so a refused one stops only itself.

## Find the pull request

From a checkout that isn't on the effort's branch, list pull requests by head branch with `gh pr list --head` and `--state all`; without `--state all`, a merged pull request doesn't show.

## Merge

Merge with `gh pr merge` and the project's method, and leave out `--delete-branch`: it deletes branches before they are proven merged, and switches the current checkout to the default branch.

## The follow-up branch

Make its worktree with `git worktree add --no-track -b`, from the remote default branch. `--no-track` leaves the branch without an upstream until its first push, since a branch that tracks the default branch makes a bare `git push` target it.

## Label the next effort

`gh issue create --label` fails when the label doesn't exist yet, so create the next effort's `effort:` label first with `gh label create`.

## Files only in a worktree

`git status --ignored` also lists ignored files, marked `!!`, which plain `git status` hides and removing the worktree deletes.

## Prove merged

Run `git fetch --prune` first, so the remote default branch is current and deleted remote branches drop out.

- **Reachable**: `git merge-base --is-ancestor`, with the branch and the remote default branch, succeeds. It is the cheapest proof, so try it first.
- **Matched by patch**: `git cherry`, with the remote default branch and the branch, prints no `+` line. A `+` proves nothing either way, because a squash merge or a changed commit leaves one.
- **In the merged pull request's head**: `gh pr view` with `--json state,headRefOid` shows `MERGED`, and `git merge-base --is-ancestor`, with the branch and that head commit, succeeds. When the head commit is missing locally, fetch the pull request's head from GitHub first. A leftover delegate branch counts when `git log --grep` finds its ticket's commit in that head, and the branch holds nothing beyond that one commit.

## Free worktrees and branches

- Remove a worktree without `--force`: a worktree that needs `--force` isn't clean, so it isn't proven.
- `git branch -d` fits the reachable proof, since git deletes only a branch it sees as merged. Use `git branch -D` when only the patch match or the merged pull request's head proves it.
- Before deleting a remote branch, check it still exists with `git ls-remote --heads origin`: a repo that deletes head branches on merge may already have deleted it.
