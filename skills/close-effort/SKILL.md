---
name: close-effort
description: Close an effort after its pull request is approved - merge it, run the post-merge follow-ups, carry unfinished work into next-effort tickets, close the tracker, and free the branches and worktrees proven merged. Use when the maintainer says an effort's pull request is good, that it merged, or to merge it.
argument-hint: "The pull request (optional: defaults to the current branch's)"
---

# Close Effort

The maintainer's only step after delivery is approving the pull request. Everything after that is yours, whether you are the orchestrator that delivered it or a session told the pull request merged or to merge it. Run every command yourself and hand the maintainer nothing to paste, except where `<session-host>` is unset.

The close is done when:

- the pull request is merged, and its merge is checked;
- every post-merge follow-up has run, with its result in the report;
- every unfinished item is done, carried over as a next-effort ticket, or a QA ticket waiting on the maintainer;
- the tracker is closed;
- nothing exists only inside this session: it is committed and pushed, in a ticket, or saved in a handoff, so another session can continue where this one stopped;
- every branch and worktree proven merged is freed, this session's own worktree last.

Workspaces and agent sessions stay open; the maintainer closes them.

Before you run a step, read its entry in [commands.md](commands.md), which says what each command is for and when an alternative fits.

## Order

Run the steps in the order that fits, with three rules:

- Read *Things to be aware of* in step 3 before any follow-up or cleanup.
- Copy the files worth keeping out of a worktree in step 6 before removing it.
- Free this session's own worktree last, from outside it, in step 8.

## Proven merged, or kept

Delete a branch or remove a worktree only when its work is **proven merged**. Three proofs count:

- **Reachable**: the branch's tip is an ancestor of the default branch. A merge commit or a fast-forward leaves it so.
- **Matched by patch**: each of its commits has an identical patch on the default branch, as happens when commits are rebased or cherry-picked unchanged.
- **In the merged pull request's head**: the pull request is merged, and the branch's tip is its head or an ancestor of it. A delegate branch left over from the build counts when its ticket's commit is in that head and the branch holds nothing else.

A squash merge, or a commit changed while it was integrated, fails the first two proofs; only the merged pull request's head proves it.

A worktree also needs to be clean after step 6, with no agent still working in it. Keep anything you can't prove or couldn't remove, and name it in the report with the reason. The one exception is the close's own follow-up worktree: its pushed branch is the proof, as step 4 says.

## Parameters

Each parameter comes from the Defaults table, where a project's row overrides the global one, and is unset when it has no row or its row says `none`.

- `<worktree-tool>`: the tool that makes and frees worktrees. When it is Treehouse, use the **treehouse** skill. Unset, use git.
- `<session-host>`: where the effort's agent sessions run. When it is Herdr, use the **handover-to-herdr** skill's `closing-an-effort.md` to find the agents still working and to free this session's worktree from a shell in the main checkout; that shell's output is its report, and your report names where it runs. Unset, freeing this session's own worktree is the maintainer's one step: end the report with the command, to run once this session is closed.

## 1. Find the effort

Start from the argument, or else the current branch, and find the pull request, its branch, and the effort's name, which is in its `effort:<effort>` label or the handoff. Then gather what the effort left behind:

- its spec, its tickets and its handoff in `.handoff/`; a local tracker keeps the tickets in `.efforts/<effort>/`;
- its worktrees, sub-agent worktrees under `.claude/worktrees/` included;
- its branches: the effort branch, sub-agent branches, and any prototype branch the spec or handoff names;
- the agents in `<session-host>` still working in one of those worktrees.

Done when you hold that list, and know whether this session runs inside one of the effort's worktrees.

## 2. Merge

When the pull request already merged, only check the merge. Otherwise merge it once its checks pass. When the spec says "QA: blocking", every QA ticket must be closed first; a QA ticket still open blocks the merge, so tell the maintainer which one, and stop.

Merge with the method the project's instructions name, else the one the repo usually uses, and leave the branches for step 7.

Then check the merge broke nothing. The default branch's CI must pass on the merge commit. After a squash or a rebase, anything pinned to a branch commit must still resolve, such as an image URL that carries a commit SHA. A red run or a broken pin becomes the first item for step 4.

Done when the pull request is merged and its merge is checked.

## 3. Read *Things to be aware of*

The last section of the pull request's description, *Things to be aware of*, comes from the **to-pr** skill's template. It holds what the delivering agent flagged beyond the change itself, under **Decided alone**, **Surprises**, **Not in this PR** and **Follow-ups**. Route each item to one of:

- **a check you run now**, for a cheap check it says was skipped, such as a test suite not rerun after a fix. Run it on the updated default branch.
- **a ticket**, carried over in step 4. A follow-up already marked as a ticket is carried over as it says.
- **a todo for the maintainer**, for the report.
- **nothing needed**.

When the pull request has no such section, take its items from the handoff and tickets.

Done when every item has a route and each skipped check has run.

## 4. Follow up and carry over

Work from the updated default branch, and leave the maintainer's main checkout on whatever branch it is on. Pull there only when it is clean and already on the default branch.

Everything reaches the default branch through a pull request. The close's own changes to tracked files, such as a local tracker's done marks or files kept in step 6, follow the project's instructions. By default they go on one small **follow-up branch** from the default branch, in its own worktree, with a pull request opened through the **to-pr** skill for the maintainer to review. Changes too small to be worth a pull request are listed in the report instead. The follow-up branch belongs to the close, not the effort. Once it is pushed and its pull request is open, free its worktree to save disk space, and delete its local branch when the remote holds it.

Then:

1. **Run the post-merge follow-ups** that the handoff, the spec or *Things to be aware of* name: installing or updating what changed, removing a setting the change replaced, trying what can only be tried once merged, or publishing a draft release and checking that its tag is on the merge commit and its assets are attached. Report each result.
2. **Audit what's unfinished**: the effort's open tickets, the items step 3 routed to a ticket, review findings deferred at delivery, a red run or broken pin from step 2, and stale docs or assets.
3. **Carry each unfinished item over** as a ticket in the **next effort**, labelled `effort:<next>` and linked back to where it came from. The next effort is the project's open spec or grilling ticket for its next round of work. When that isn't obvious, ask the maintainer which one, in the **orchestrating** skill's question shape.

**QA tickets** are the exception. With the default, non-blocking QA, the pull request said "Refs" rather than "Closes", so the merge left them open. They stay open and assigned to the maintainer, who closes them or gives feedback. Comment on each that the work is now on the default branch and how to reach the build, and list them in the report.

Done when every post-merge follow-up has run and its result is noted for the report, and every item is done, carried over as a linked next-effort ticket, or a QA ticket waiting on the maintainer.

## 5. Close the tracker

Close the spec and every ticket the merge finished. That includes tickets a "closes" keyword should have closed but didn't, because they were named only in a commit or the pull request's base wasn't the default branch. Check and tick each criterion that could only be shown after the merge. Close each carried-over ticket too, with a comment linking the next-effort ticket that continues it. On a local tracker, mark them done in `.efforts/<effort>/` on the follow-up branch.

Done when the effort's only open tickets are QA tickets waiting on the maintainer.

## 6. Leave nothing only here

Removing a worktree deletes its ignored and untracked files without asking. For each worktree you are about to remove, list those files and copy out what's worth keeping, where the **orchestrating** skill's `folders.md` puts it. Editor settings like `.vscode/` count too; copy them to the main checkout.

Then turn to this session itself: its uncommitted or unpushed work, and what it knows that isn't written down, like a decision, a half-done follow-up or an open question for the maintainer. Commit and push the work, and put each open item in a ticket, or in a handoff through the **handoff** skill. Anything that lands in tracked folders goes on the follow-up branch, committed and pushed.

Done when each worktree's untracked and ignored files are copied out or judged throwaway, and another session could continue from the repository and the tracker alone.

## 7. Free branches and worktrees

Fetch and prune first. Then take each sub-agent worktree, each of the effort's other worktrees, leaving this session's for step 8, and each branch; prove it merged, then remove it. Free worktrees with `<worktree-tool>`, then delete local branches, then remote ones.

Done when every proven-merged branch and worktree other than this session's is gone, and the rest is listed with the reason.

## 8. Report, then free your own worktree

Report in the chat, short, with links:

- the pull request, its merge commit, and each post-merge follow-up with its result;
- what closed, and each carried-over ticket by title and link;
- the QA tickets waiting on the maintainer, and the maintainer's todos from step 3;
- what was kept and why, anything not proven merged included;
- the follow-up pull request or handoff, or the changes listed in their place.

Last, when this session runs inside one of the effort's worktrees, free that worktree from outside it. Freeing it stops every process in it, this session included, so it happens after the report, through `<session-host>`, as your last action. When this session runs elsewhere, step 7 already freed the other worktrees, and the report ends the close.

Done when the report is sent and this session's worktree is freed, or its free command ends the report.
