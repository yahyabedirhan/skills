---
name: close-effort
description: Close an effort after its pull request is approved - merge it, run the post-merge follow-ups, carry unfinished work into next-effort tickets, close the tracker, and free the branches and worktrees proven merged. Use when the maintainer says an effort's pull request is good, that it merged, or to merge it.
argument-hint: "The pull request (optional: defaults to the current branch's)"
---

# Close Effort

Approving the pull request is the maintainer's last step. Everything after it is yours, so run every command yourself rather than handing the maintainer commands to paste. Leave workspaces and agent sessions open; the maintainer closes them.

## Parameters

- `<worktree-tool>`: the tool that makes and frees worktrees, e.g. `treehouse`, or plain git worktrees.
- `<session-host>`: where agent sessions run, e.g. `herdr`, Claude Code Desktop, Codex Desktop.

## Flow

Run each commit, push and deletion as its own call, so a refused one stops only itself.

1. **Find the effort:** the pull request, its branch, spec, tickets and handoff, and the worktrees and branches the build left behind.
   - **From a checkout that isn't on the effort's branch:** list pull requests by head branch with `gh pr list --head` and `--state all`, since without `--state all` a merged pull request doesn't show.
2. **Merge** the pull request once its checks pass, and check that the default branch's CI passes after the merge. Merge with `gh pr merge` and the project's usual method, and leave out `--delete-branch`: it deletes branches before they are proven merged, and switches the current checkout to the default branch.
   - **When the spec says "QA: blocking":** wait until every QA ticket is closed, and tell the maintainer which ones are still open.
   - **After a squash or a rebase:** check that anything pinned to one of the branch's commits, such as an image URL with a commit SHA, still resolves, since the default branch doesn't hold those commits.
3. **Read the pull request's description and the handoff** for what the delivery left open: follow-ups, checks it skipped and decisions for the maintainer. Run the skipped checks now.
4. **Run the post-merge follow-ups,** such as installing what changed or trying what could only be tried after the merge.
5. **Carry unfinished work over** as tickets in the next effort, labelled for it and linked back to where each came from, and close the spec and every ticket the merge finished. `gh issue create --label` fails when the label doesn't exist yet, so create the next effort's `effort:` label first with `gh label create`.
   - **When it isn't clear which effort is next:** ask the maintainer.
   - **For QA tickets:** leave them open for the maintainer, with a comment on how to reach the build.
   - **When a "closes" keyword missed a ticket the merge finished:** close it by hand.
6. **Save what exists only in a worktree or this session.** Removing a worktree deletes its ignored and untracked files, so list them with `git status --ignored` and copy out what's worth keeping. Save them where `/orchestrating`'s `folder-standard.md` puts each kind, and copy editor settings like `.vscode/` to the main checkout. Commit and push this session's work, and put what it knows that isn't written down in a ticket or a handoff.
   - **When the close changes tracked files, such as done marks or saved files:** put the changes on a small follow-up branch, and open its pull request with `/to-pr`, like any other change. Leave the maintainer's main checkout on its branch, since they may be working there. Pull in the main checkout only when it is clean and already on the default branch; otherwise work from the remote default branch. Make the follow-up worktree with `<worktree-tool>`, from the remote default branch, and free it once its branch is pushed.
7. **Free the branches and worktrees whose work is proven merged,** and keep anything you can't prove, naming it in the report. Run `git fetch --prune` first, so the remote default branch is current. Three proofs count:
   - **Reachable:** `git merge-base --is-ancestor` with the branch and the remote default branch succeeds, as after a merge commit or a fast-forward. It is the cheapest, so try it first.
   - **Matched by patch:** `git cherry` with the remote default branch and the branch prints no `+` line, as after a rebase or an unchanged cherry-pick. A `+` proves nothing either way.
   - **In the merged pull request's head:** `gh pr view --json state,headRefOid` shows `MERGED`, and the branch's tip is that head or an ancestor of it. A leftover delegate branch counts when its ticket's commit is in that head and the branch holds nothing else. A squash merge, or a commit changed while it was integrated, fails the first two proofs; only this one proves it.

   Free worktrees before their branches, since git won't delete a branch a worktree has checked out. Remove a worktree without `--force`, because a worktree that needs it isn't clean. Delete a local branch with `git branch -d` after the reachable proof, and with `git branch -D` when only the other two prove it.
   - **When an agent is still working in a worktree:** leave that worktree.
   - **Before deleting a remote branch:** check it still exists with `git ls-remote --heads origin`, since the repo may have deleted it on merge.
8. **Report** what merged, what closed, what carried over and what waits on the maintainer. Then free this session's own worktree from outside it, through `<session-host>`, as your last action: freeing it ends this session.
   - **When this session runs outside the effort's worktrees:** the report ends the close.
