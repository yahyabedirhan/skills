---
name: close-effort
description: Close an effort after its pull request is approved - merge it, run the post-merge follow-ups, carry unfinished work into next-effort tickets, close the tracker, and free the branches and worktrees proven merged. Use when the maintainer says an effort's pull request is good, that it merged, or to merge it.
argument-hint: "The pull request (optional: defaults to the current branch's)"
---

# Close Effort

The maintainer's only step after delivery is approving the pull request. Everything after that is yours, whether you are the orchestrator that delivered it or any session told the pull request merged or to merge it. Run every command yourself and hand the maintainer nothing to paste; the one exception is freeing this session's own worktree when there is no session host (step 8).

The close is done when:

- the pull request is merged, and its merge is checked;
- every unfinished item is done, carried over as a next-effort ticket, or a QA ticket waiting on the maintainer;
- the tracker is closed;
- nothing exists only inside this session: it is committed and pushed, in a ticket, or saved in a handoff, so another session can continue where this one stopped;
- every branch and worktree proven merged is freed, this session's own worktree last.

Workspaces and agent sessions stay open; the maintainer closes them.

The commands for each step are in [commands.md](commands.md), each with what it's for, its alternatives and when to use it.

## Order

Run the steps in the order that fits, with three rules:

- Read *Things to be aware of* (step 3) before any follow-up or cleanup.
- Copy out the files worth keeping from a worktree (step 6) before removing it.
- Free this session's own worktree last, from outside it (step 8).

## Proven merged, or kept

Delete a branch or remove a worktree only when its work is **proven merged**, by one of:

- **Reachable**: the branch's tip is an ancestor of the default branch (a merge commit, or a fast-forward).
- **Matched by patch**: each of its commits has an identical patch on the default branch (rebased, or cherry-picked unchanged).
- **In the merged pull request's head**: the pull request is merged and the branch's tip is its head or an ancestor of it. A delegate branch left over from the build counts when its ticket's commit is in that head and the branch holds nothing else.

A squash merge, or a commit changed while it was integrated, fails the first two; only the merged pull request's head proves it. The decision record once got this wrong.

A worktree must also be clean after step 6, and no agent may still be working in it. Keep anything you can't prove or couldn't remove, and name it in the report with why.

## Parameters

From the Defaults table (a project's row overrides the global one). Unset: no row, or `none`.

- `<worktree-tool>`: how worktrees are made and freed. When it is Treehouse, the **treehouse** skill has its commands. Unset: git.
- `<session-host>`: where the effort's agent sessions run. When it is Herdr, the **handover-to-herdr** skill's `closing-an-effort.md` has its commands. Unset: step 8 falls to the maintainer.

## 1. Find the effort

From the argument, or the current branch: the pull request, its branch, and the effort's name (its label `effort:<effort>`, or the handoff). Then gather what the effort left behind:

- its spec, its tickets (on the tracker, or `.efforts/<effort>/` on a local one) and its handoff in `.handoff/`;
- its worktrees, including sub-agent worktrees under `.claude/worktrees/`;
- its branches: the effort branch, sub-agent branches, and any prototype branch the spec or handoff names;
- the agents in the session host still working in one of those worktrees.

Done when you hold that list, and know whether this session runs inside one of the effort's worktrees.

## 2. Merge

When the pull request already merged, only check the merge. Otherwise merge it when:

- its checks pass;
- when the spec says "QA: blocking", every QA ticket is closed. A QA ticket still open blocks the merge: tell the maintainer which one, and stop.

Merge with the project's method (its instructions, else the repo's usual one), and leave the branches for step 7.

Then check the merge broke nothing: the default branch's CI on the merge commit, and, after a squash or rebase, that anything pinned to a branch commit (such as an image URL with a commit SHA) still resolves. A red run or a broken pin is the first item for step 4.

Done when the pull request is merged and its merge is checked.

## 3. Read *Things to be aware of*

Read the pull request description's last section, *Things to be aware of* (the **to-pr** skill's template): what the delivering agent flagged outside "what changed", under **Decided alone**, **Surprises**, **Not in this PR** and **Follow-ups**. Route each item to one of:

- **a check you run now**: a cheap check it says was skipped (a test suite not rerun after a fix); run it on the updated default branch;
- **a ticket**, carried over in step 4 (a follow-up already marked as a ticket is carried over as it says);
- **a todo for the maintainer**, for the report;
- **nothing needed**.

When the description has no such section (an older effort), take the items from the handoff and tickets.

Done when every item has a route and each skipped check has run.

## 4. Follow up and carry over

Work from the updated default branch and leave the maintainer's main checkout where it is: never switch its branch, and pull only when it is clean and already on the default branch.

Nothing is committed or pushed straight to the default branch. The close's own changes to tracked files (a local tracker's done marks, files kept in step 6) follow the project's instructions. By default they go on one small **follow-up branch** from the default branch, in its own worktree, with a pull request opened through the **to-pr** skill for the maintainer to review. When they are too small to be worth a pull request, list them in the report instead. The follow-up branch and its worktree aren't the effort's: step 7 leaves them.

Then:

1. **Run the post-merge follow-ups**: what the handoff, the spec or the last section says happens after the merge, such as installing or updating what changed, removing a setting the change replaced, publishing a draft release (then check its tag is on the merge commit and its assets are attached), or trying what can only be tried once merged. Report each result.
2. **Audit what's unfinished**: the effort's open tickets, the items routed to a ticket in step 3, review findings deferred at delivery, a red run or broken pin from step 2, stale docs or assets.
3. **Carry each unfinished item over** as a ticket in the **next effort**: labelled `effort:<next>`, linked back to where it came from. The next effort is the project's open spec or grilling ticket for its next round of work; when that isn't obvious, ask the maintainer which one, in the **orchestrating** skill's question shape.

**QA tickets** left open for the maintainer (the default, non-blocking QA: the pull request said "Refs", not "Closes", so the merge left them open) stay open and assigned to them. Comment on each that the work is now on the default branch and how to reach the build, and list them in the report. They aren't unfinished work: the maintainer closes them or gives feedback.

Done when every item is done, carried over as a linked next-effort ticket, or a QA ticket waiting on the maintainer; nothing is dropped.

## 5. Close the tracker

Close the spec and every ticket the merge finished, including ones whose "closes" didn't fire (a ticket named only in a commit, or a base that isn't the default branch). A criterion that could only be shown after the merge gets checked and ticked now. Close each carried-over ticket too, with a comment linking the next-effort ticket that continues it. On a local tracker, mark them done in `.efforts/<effort>/` on the follow-up branch.

Done when the effort's only open tickets are QA tickets waiting on the maintainer.

## 6. Leave nothing only here

Removing a worktree deletes its ignored and untracked files without asking. For each worktree you are about to remove, list them and copy out anything worth keeping, per the folder standard (the **orchestrating** skill's `folders.md`): screenshots to `docs/assets/<topic>/`, notes to a handoff or the tracker, a useful script to the main checkout's `.scratch/`, editor settings (`.vscode/`) to the main checkout.

Then look at this session itself: uncommitted or unpushed work, and what it knows that isn't written down anywhere (a decision, a half-done follow-up, an open question for the maintainer). Commit and push the work; put each open item in a ticket, or in a handoff through the **handoff** skill. What lands in tracked folders goes on the follow-up branch, committed and pushed.

Done when each worktree's untracked and ignored files are copied out or judged throwaway, and another session could continue from the repository and the tracker alone.

## 7. Free branches and worktrees

Fetch and prune, then for each sub-agent worktree, each other worktree of the effort except this session's, and each branch, prove it merged, then remove it: worktrees with the worktree tool (Treehouse's return keeps the worktree in its pool), local branches, then remote branches.

A worktree whose branch has an open pull request stays until its branch is pushed; after that, keep its local branch only when the remote doesn't hold it.

Done when every proven-merged branch and worktree other than this session's is gone, and the rest is listed with why.

## 8. Report, then free your own worktree

Report in the chat, short, with links:

- the pull request and its merge commit, and the post-merge follow-ups with their results;
- what closed, and what carried over (each new ticket by title and link);
- QA tickets waiting on the maintainer, and the maintainer's todos from step 3;
- what was kept and why, including anything not proven merged;
- the follow-up pull request or handoff, or the changes listed in their place.

Last, when this session runs inside one of the effort's worktrees, free it from outside it. Freeing it stops every process there, this session included, so it runs after the report. Skip this when this session runs elsewhere; step 7 freed every worktree.

- **When the session host is Herdr**: through the **handover-to-herdr** skill, open a shell in the repository's main checkout, labelled `shell · Close · <effort>`, and, as your last action, run the free command there after a short pause. The shell's output is its report, and the report above names where it runs. The workspace stays open.
- **Otherwise**, this one step is the maintainer's: end the report with the command, to run once this session is closed.
