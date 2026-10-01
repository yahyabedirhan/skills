---
name: settle-effort
description: Settle an effort once its pull request is approved - merge it, run the post-merge follow-ups, carry unfinished work into next-effort tickets, close the spec and tickets, then settle the session. Use when the user says to settle the effort, or when another skill says to.
argument-hint: "The pull request (optional: defaults to the current branch's)"
---

# Settle Effort

Approving the pull request is the user's last step. Everything after it is yours. Do the effort's own steps below, then hand the rest to `/settle-session`.

## Flow

1. **Find the effort:** the pull request, its branch, spec, tickets and handoff, and the worktrees and branches the build left behind, such as delegates' leftovers.
   - **From a checkout that isn't on the effort's branch:** list pull requests by head branch with `gh pr list --head` and `--state all`, since without `--state all` a merged pull request doesn't show.
2. **Merge** the pull request once its checks pass, and check that the default branch's CI passes after the merge. Merge with `gh pr merge` and the project's usual method, and leave out `--delete-branch`: it deletes branches before they are proven merged, and switches the current checkout to the default branch.
   - **When the pull request is already merged:** skip the merge, and still check the default branch's CI and the case below.
   - **When the spec says "QA: blocking":** don't merge until every QA ticket is closed, and tell the user which ones are still open.
   - **After a squash or a rebase:** check that anything pinned to one of the branch's commits, such as an image URL with a commit SHA, still resolves, since the default branch doesn't hold those commits.
3. **Read the pull request's description and the handoff** for what the delivery left open: follow-ups, checks it skipped and decisions for the user. Run the skipped checks now.
4. **Run the post-merge follow-ups,** such as installing what changed or trying what could only be tried after the merge.
5. **Carry unfinished work over** as tickets in the next effort, labelled for it and linked back to where each came from, and close the spec and every ticket the merge finished. `gh issue create --label` fails when the label doesn't exist yet, so create the next effort's `effort:` label first with `gh label create`.
   - **When it isn't clear which effort is next:** ask the user.
   - **For QA tickets:** leave them open for the user, with a comment on how to reach the build.
   - **When a "closes" keyword missed a ticket the merge finished:** close it by hand.
6. **Settle the session** with `/settle-session`, naming the effort's worktrees and branches from step 1, delegates' leftovers included, as the ones to free. Have the report also say what merged, what closed and what carried over.
