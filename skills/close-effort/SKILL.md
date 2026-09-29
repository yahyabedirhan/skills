---
name: close-effort
description: Close an effort after its pull request is approved - merge it, run the post-merge follow-ups, carry unfinished work into next-effort tickets, close the tracker, and clean up branches, worktrees and the Herdr workspace. Use when the maintainer says an effort's pull request is good ("go"), that it merged, or to merge it.
argument-hint: "The pull request (optional: defaults to the current branch's)"
---

# Close Effort

The maintainer's only step after delivery is reviewing the pull request and saying "go". Everything after that is yours, whether you are the orchestrator that delivered it or any session told the pull request merged or to merge it: merge, follow up, carry over, clean up, report. Run every command yourself. The one step that can fall to the maintainer is returning the worktree this session runs in, and only when Herdr isn't there (step 9).

Two rules hold for every destructive step (deleting a branch, removing a worktree):

- **Proven merged, or kept.** Remove a branch or worktree only when its work is **proven merged**: every commit reachable from the default branch (`git merge-base --is-ancestor <branch> origin/<default>`), or, for work that was squashed or cherry-picked with fixes, matched by patch (`git cherry origin/<default> <branch>` prints no `+` line). A worktree must also be clean (`git -C <path> status --short` empty after step 6). Keep anything you can't prove, and name it in the report with what's unproven.
- **A denial is final.** When a permission check refuses a destructive command, add it to the **cleanup script** and carry on; run no variant of the refused command. The script is `.scratch/close-<effort>.sh` in the main checkout: one line per command, each under a comment with its proof (the `git cherry` or ancestor check you ran). Run each commit, push and deletion as its own call, so one refusal stops only itself.

## 1. Find the effort

From the argument, or the current branch: the pull request (`gh pr view [<n>] --json number,url,state,headRefName,baseRefName,mergeCommit,body`), its branch, and the effort's name (its label `effort:<effort>`, or the handoff). Then gather what the effort left behind:

- its spec, its tickets (`gh issue list --label effort:<effort> --state all`, or `.efforts/<effort>/` on a local tracker) and its handoff in `.handoff/`;
- its worktrees, from the project's worktree tool (named in its instructions; Treehouse by default, `treehouse status`, see the **init-effort** skill's `treehouse.md`) and `git worktree list`, including sub-agent worktrees under `.claude/worktrees/`;
- its branches: the effort branch, sub-agent branches, and any prototype branch the spec or handoff names;
- its Herdr workspaces and agents, when `herdr status` reaches a server (`herdr workspace list`, `herdr agent list`), and which one this session runs in (`$HERDR_WORKSPACE_ID`, or the workspace whose `checkout_path` is this session's worktree).

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

When the description has no such section (an older effort) and the delivering orchestrator still runs in a Herdr tab, ask it once: `herdr agent prompt <name> 'Reply with the four lines of Things to be aware of for this pull request: Decided alone, Surprises, Not in this PR, Follow-ups.' --wait`. Otherwise take the items from the handoff and tickets yourself.

Done when every item has a route and each skipped check has run.

## 4. Follow up and carry over

In the main checkout, bring the default branch up to date (`git switch <default>`, `git pull --prune`). Then:

1. **Run the post-merge follow-ups**: what the handoff, the spec or the last section says happens after the merge, such as installing or updating what changed, removing a setting the change replaced, publishing a draft release (then check its tag is on the merge commit and its assets are attached), or trying what can only be tried once merged. Report each result.
2. **Audit what's unfinished**: the effort's open tickets, the items routed to a ticket in step 3, review findings deferred at delivery, a red run or broken pin from step 2, stale docs or assets.
3. **Carry each unfinished item over** as a ticket in the **next effort**: labelled `effort:<next>` (create the label when it's missing), linked back to where it came from. The next effort is the project's open spec or grilling ticket for its next round of work; when that isn't obvious, ask the maintainer which one, in the **orchestrating** skill's question shape.

**QA tickets** left open for the maintainer (the default, non-blocking QA: the pull request said "Refs", not "Closes", so the merge left them open) stay open and assigned to them. Comment on each that the work is now on the default branch and how to reach the build, and list them in the report. They aren't unfinished work: the maintainer closes them or gives feedback.

Done when every item is done, carried over as a linked next-effort ticket, or a QA ticket waiting on the maintainer; nothing is dropped.

## 5. Close the tracker

Close the spec and every ticket the merge finished, including ones whose "closes" didn't fire (a ticket named only in a commit, or a base that isn't the default branch). A criterion that could only be shown after the merge gets checked and ticked now. Close each carried-over ticket too, with a comment linking the next-effort ticket that continues it. On a local tracker, mark them done in `.efforts/<effort>/` and commit that on the default branch, as its own call.

Done when the effort's only open tickets are QA tickets waiting on the maintainer.

## 6. Keep what's worth keeping

`treehouse return` deletes a worktree's ignored and untracked files, and `git worktree remove` its ignored ones, without asking. For each worktree you are about to remove, list them (`git -C <path> status --short --ignored`) and copy out anything worth keeping, per the folder standard (the **orchestrating** skill's `folders.md`): screenshots to `docs/assets/<topic>/`, notes to a handoff or the tracker, a useful script to the main checkout's `.scratch/`. Untracked editor settings (`.vscode/`) the maintainer may care about count too: copy them to the main checkout. Commit what lands in tracked folders, as its own call, and push.

Done when each worktree's untracked and ignored files are copied out or judged throwaway.

## 7. Clean up branches and worktrees

`git fetch --prune`, then for each sub-agent worktree, each other worktree of the effort except this session's, and each branch, prove it merged, then remove it:

- sub-agent worktrees: `git worktree remove <path>`;
- the effort's other worktrees, the project's way: `treehouse return <path>`, or `git worktree remove <path>`;
- local branches: `git branch -d <branch>`, or `git branch -D <branch>` when only `git cherry` proves it (after a squash or cherry-pick);
- remote branches: `git push origin --delete <branch>`.

A worktree whose branch has an open pull request stays until its branch is pushed; after that, keep its local branch only when the remote doesn't hold it.

Done when every proven-merged branch and worktree is gone or in the cleanup script, and the rest is listed with why.

## 8. Close the Herdr workspace

When `herdr status` reaches a server: check `herdr agent list` for the effort's agents, and close each of the effort's workspaces this session doesn't run in with `herdr workspace close <workspace_id>`. An agent still `working` in one keeps its workspace open; name it in the report. Target explicit IDs from Herdr's JSON, pass `--no-focus` wherever a command takes it, and never use `--current` (the **handover-to-herdr** skill's *Herdr from anywhere*).

Done when only this session's workspace is left, or a working agent's, named.

## 9. Report, then return your own worktree

Report in the chat, short, with links:

- the pull request and its merge commit, and the post-merge follow-ups with their results;
- what closed, and what carried over (each new ticket by title and link);
- QA tickets waiting on the maintainer, and the maintainer's todos from step 3;
- what was kept and anything not proven merged;
- the cleanup script, when there is one, with the one command that runs it.

Last, when this session runs inside one of the effort's worktrees, return it from outside it: returning it stops every process there, this session included, so it runs after the report. Skip this when this session runs elsewhere; step 7 returned every worktree.

- **With Herdr:** open a tab outside the worktree, in the repository's main-checkout workspace: `herdr tab create --workspace <repo workspace_id> --cwd <main checkout> --no-focus`, rename it `<effort> · Close · shell`, and, as your last action, send one command to its root pane: `herdr pane run <pane_id> 'sleep 30; <return command>; herdr workspace close <this workspace_id>; git worktree list'`. The pause lets the report finish first. The return command is the project's tool's (`treehouse return <path>`, or `git worktree remove <path>`). The tab's output is its report, and the report above names the tab.
- **Without Herdr**, this one step is the maintainer's: end the report with the return command, to run once this session is closed.
