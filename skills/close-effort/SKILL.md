---
name: close-effort
description: Close an effort after its pull request is approved - merge it, run the post-merge follow-ups, carry unfinished work into next-effort tickets, close the tracker, and clean up branches, worktrees and the effort's workspaces. Use when the maintainer says an effort's pull request is good ("go"), that it merged, or to merge it.
argument-hint: "The pull request (optional: defaults to the current branch's)"
---

# Close Effort

The maintainer's only step after delivery is reviewing the pull request and saying "go". Everything after that is yours, whether you are the orchestrator that delivered it or any session told the pull request merged or to merge it: merge, follow up, carry over, clean up, report. Run every command yourself. Only two steps can fall to the maintainer: running the cleanup script, when a permission check refused a deletion, and returning the worktree this session runs in, when `<session-host>` is unset (step 9).

Two rules hold for every destructive step (deleting a branch, removing a worktree):

- **Proven merged, or kept.** Remove a branch or worktree only when its work is **proven merged** by one of these:
  - **Reachable**: `git merge-base --is-ancestor <branch> origin/<default>` succeeds (a merge commit, or a fast-forward).
  - **Matched by patch**: `git cherry origin/<default> <branch>` prints no `+` line (commits rebased or cherry-picked unchanged). A squash merge, or a commit changed while it was integrated, leaves `+` lines, so a `+` proves nothing either way.
  - **In the merged pull request's head**: `gh pr view <n> --json state,headRefOid` shows `MERGED`, and the branch's tip is `headRefOid` or its ancestor (`git merge-base --is-ancestor <branch> <headRefOid>`; when that commit is missing locally, `git fetch origin pull/<n>/head` first). This proves the effort branch after a squash merge. A delegate branch left over from the build is proven when its ticket's commit is in that head (`git log <headRefOid> --grep <ticket>` finds it) and the branch holds nothing else (`git log --oneline <headRefOid>..<branch>` shows only the one ticket commit the delegate made).

  A worktree must also be clean (`git -C <path> status --short` empty after step 6). Keep anything you can't prove, and name it in the report with what's unproven.
- **A denial is final.** When a permission check refuses a destructive command, add it to the **cleanup script** and carry on; run no variant of the refused command. The script is `.scratch/close-<effort>.sh` in the main checkout: one line per command, each under a comment with its proof (the check you ran and its result). Run each commit, push and deletion as its own call, so one refusal stops only itself.

## Parameters

Each comes from the Defaults table in the environment's instructions, where a project's table overrides the global one for that project. Unset means no row, or `none`.

- `<worktree-tool>`: how worktrees are made and returned, used through its how-to skill (named for the tool). Unset, or that skill not installed: git (`git worktree list`, `git worktree remove`).
- `<session-host>`: where the effort's agent sessions run, used through its how-to skill `handover-to-<session-host>`. Unset, that skill not installed, or the host out of reach: the host steps below are skipped or fall to the maintainer, as each says.

## 1. Find the effort

From the argument, or the current branch: the pull request (`gh pr view [<n>] --json number,url,state,headRefName,baseRefName,mergeCommit,body`), its branch, and the effort's name (its label `effort:<effort>`, or the handoff). Then gather what the effort left behind:

- its spec, its tickets (`gh issue list --label effort:<effort> --state all`, or `.efforts/<effort>/` on a local tracker) and its handoff in `.handoff/`;
- its worktrees, from `<worktree-tool>` and `git worktree list`, including sub-agent worktrees under `.claude/worktrees/`;
- its branches: the effort branch, sub-agent branches, and any prototype branch the spec or handoff names;
- its workspaces and agents in `<session-host>`, and which workspace this session runs in.

Done when you hold that list, and know whether this session runs inside one of the effort's worktrees.

## 2. Merge

Skip to the check below when the pull request already merged. Otherwise the maintainer's "go" is the approval; merge when:

- its checks pass (`gh pr checks <n>`);
- when the spec says "QA: blocking", every QA ticket is closed. A QA ticket still open blocks the merge: tell the maintainer which one, and stop.

Merge with the project's method (its instructions, else the repo's usual one): `gh pr merge <n> --merge|--squash|--rebase`. Leave the branches for step 7.

Then check the merge broke nothing: the default branch's CI on the merge commit (`gh run list --commit <merge sha>`), and, after a squash or rebase, anything pinned to a branch commit (such as an image URL with a commit SHA) still resolves: each pinned commit is an ancestor of `origin/<default>`. A red run or a broken pin is the first item for step 4.

Done when the pull request is merged and its merge is checked.

## 3. Read *Things to be aware of*

Before any follow-up or cleanup, read the pull request description's last section, *Things to be aware of* (the **to-pr** skill's template): what the delivering agent flagged outside "what changed", under **Decided alone**, **Surprises**, **Not in this PR** and **Follow-ups**. Route each item to one of:

- **a check you run now**: a cheap check it says was skipped (a test suite not rerun after a fix); run it on the updated default branch;
- **a ticket**, carried over in step 4 (a follow-up already marked as a ticket is carried over as it says);
- **a todo for the maintainer**, for the report;
- **nothing needed**.

When the description has no such section (an older effort) and the delivering orchestrator still runs in `<session-host>`, ask it once, through the **handover-to-`<session-host>`** skill: `Reply with the four lines of Things to be aware of for this pull request: Decided alone, Surprises, Not in this PR, Follow-ups.` When no such session runs, the wait times out, or the reply lacks the four lines, take the items from the handoff and tickets yourself.

Done when every item has a route and each skipped check has run.

## 4. Follow up and carry over

Work from the updated default branch without moving the maintainer's main checkout: run git there as `git -C <main checkout>`, and never switch its branch. When it is clean and already on the default branch, `git -C <main checkout> pull --prune`; otherwise `git -C <main checkout> fetch --prune`, and work from `origin/<default>`.

Nothing is committed or pushed straight to the default branch. Changes the close makes to tracked files (a local tracker's done marks in step 5, files kept in step 6) follow the project's instructions. By default they go on one small **follow-up branch** from `origin/<default>`, in its own worktree (`<worktree-tool>`, else `git worktree add --no-track -b <effort>-close <path> origin/<default>`), with a pull request opened through the **to-pr** skill for the maintainer to review. When they are too small to be worth a pull request, list them in the report instead. The follow-up branch and its worktree aren't the effort's: step 7 leaves them.

Then:

1. **Run the post-merge follow-ups**: what the handoff, the spec or the last section says happens after the merge, such as installing or updating what changed, removing a setting the change replaced, publishing a draft release (then check its tag is on the merge commit and its assets are attached), or trying what can only be tried once merged. Report each result.
2. **Audit what's unfinished**: the effort's open tickets, the items routed to a ticket in step 3, review findings deferred at delivery, a red run or broken pin from step 2, stale docs or assets.
3. **Carry each unfinished item over** as a ticket in the **next effort**: labelled `effort:<next>` (create the label when it's missing), linked back to where it came from. The next effort is the project's open spec or grilling ticket for its next round of work; when that isn't obvious, ask the maintainer which one, in the **orchestrating** skill's question shape.

**QA tickets** left open for the maintainer (the default, non-blocking QA: the pull request said "Refs", not "Closes", so the merge left them open) stay open and assigned to them. Comment on each that the work is now on the default branch and how to reach the build, and list them in the report. They aren't unfinished work: the maintainer closes them or gives feedback.

Done when every item is done, carried over as a linked next-effort ticket, or a QA ticket waiting on the maintainer; nothing is dropped.

## 5. Close the tracker

Close the spec and every ticket the merge finished, including ones whose "closes" didn't fire (a ticket named only in a commit, or a base that isn't the default branch). A criterion that could only be shown after the merge gets checked and ticked now. Close each carried-over ticket too, with a comment linking the next-effort ticket that continues it. On a local tracker, mark them done in `.efforts/<effort>/` on the follow-up branch (step 4), committed as its own call.

Done when the effort's only open tickets are QA tickets waiting on the maintainer.

## 6. Keep what's worth keeping

Removing a worktree deletes files without asking: `git worktree remove` its ignored ones, and `<worktree-tool>`'s own return what its how-to skill says, often the untracked ones too. For each worktree you are about to remove, list them (`git -C <path> status --short --ignored`) and copy out anything worth keeping, per the folder standard (the **orchestrating** skill's `folders.md`): screenshots to `docs/assets/<topic>/`, notes to a handoff or the tracker, a useful script to the main checkout's `.scratch/`. Untracked editor settings (`.vscode/`) the maintainer may care about count too: copy them to the main checkout. What lands in tracked folders goes on the follow-up branch (step 4): commit it as its own call, and push.

Done when each worktree's untracked and ignored files are copied out or judged throwaway.

## 7. Clean up branches and worktrees

`git fetch --prune`, then for each sub-agent worktree, each other worktree of the effort except this session's, and each branch, prove it merged, then remove it:

- sub-agent worktrees: `git worktree remove <path>`;
- the effort's other worktrees, with `<worktree-tool>`'s return command, or `git worktree remove <path>`;
- local branches: `git branch -d <branch>`, or `git branch -D <branch>` when only the patch match or the merged pull request's head proves it (after a squash, or a cherry-pick);
- remote branches: `git push origin --delete <branch>`.

A worktree whose branch has an open pull request stays until its branch is pushed; after that, keep its local branch only when the remote doesn't hold it.

Done when every proven-merged branch and worktree is gone or in the cleanup script, and the rest is listed with why.

## 8. Close the effort's workspaces

With `<session-host>` set: through the **handover-to-`<session-host>`** skill, close each of the effort's workspaces this session doesn't run in. An agent still working in one keeps its workspace open; name it in the report. Unset, skip this step.

Done when only this session's workspace is left, or a working agent's, named.

## 9. Report, then return your own worktree

Report in the chat, short, with links:

- the pull request and its merge commit, and the post-merge follow-ups with their results;
- what closed, and what carried over (each new ticket by title and link);
- QA tickets waiting on the maintainer, and the maintainer's todos from step 3;
- what was kept and anything not proven merged;
- the follow-up pull request, or the changes listed in its place;
- the cleanup script, when there is one, with the one command that runs it.

Last, when this session runs inside one of the effort's worktrees, return it from outside it: returning it stops every process there, this session included, so it runs after the report. Skip this when this session runs elsewhere; step 7 returned every worktree.

The return command is `<worktree-tool>`'s, or `git worktree remove <path>`.

- **With `<session-host>` set:** through the **handover-to-`<session-host>`** skill, open a shell outside the worktree, in the repository's main checkout, labelled `<effort> · Close · shell`, and, as your last action, run one command there: `sleep 30; <return command>; <close this session's workspace>; git worktree list`. The pause lets the report finish first. The shell's output is its report, and the report above names where it runs.
- **Unset**, this one step is the maintainer's: end the report with the return command, to run once this session is closed.
