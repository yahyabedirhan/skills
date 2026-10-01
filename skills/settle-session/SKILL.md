---
name: settle-session
description: Settle a session so nothing depends on it - nothing running, unsaid, undecided or unsaved, and merged branches and worktrees freed. Use when the user says "settle" or "end the session" about this session, or when another skill says to settle. When the user says to settle an effort, use /settle-effort instead.
argument-hint: "Branches and worktrees to free besides this session's own (optional)"
---

# Settle Session

A settled session leaves the environment clean: nothing uncommitted or unpushed, and everything the session knows saved in the issue tracker or the project's files. Another agent can then pick the work up from what is written down, without reading this session, which may then be deleted.

Do every step yourself rather than handing the user commands to paste, except where step 7 says otherwise. Leave workspaces and idle agent sessions open; the user closes them.

## Parameters

- `<worktree-tool>`: the tool that makes and frees worktrees, e.g. `treehouse`, or plain git worktrees.
- `<session-host>`: where agent sessions run, e.g. `herdr`, Claude Code Desktop, Codex Desktop.

## Flow

Run each commit, push and deletion as its own call, so a refused one stops only itself.

1. **Take stock** of what this session touched: the checkouts and worktrees it worked in and their branches, the pull requests and issues it opened, the processes and agents it started, and the threads still open. Add any branches and worktrees the calling skill or the user names.
2. **Nothing running.** Stop what this session started, such as dev servers, watchers, background commands and preview or browser tabs, unless the user wants one kept; name each one kept in the report. Wait for or stop each agent this session started that is still working, and leave idle sessions and their workspaces open.
3. **Nothing unsaid.** Write down what this session learned that lives only in its context: decisions and their reasons, surprises, checks it skipped, what comes next. Put each where an agent that never saw this session will look for it: the issue it belongs to, the pull request's description, or a handoff written with `/handoff`.
4. **Nothing undecided.** Give each leftover thread an outcome: finish it, file it as a ticket, or raise it with the user and record what they decide. Ask while the user is here, and settle only once each question has its answer.
   - **When the user can't be reached,** such as when a handoff says to decide alone: decide it yourself, and record the decision and its reason where step 3 puts what the session knows.
5. **Nothing unsaved.** In each checkout this session worked in, commit and push everything, including the files steps 3 and 4 wrote, until `git status` is clean and the branch matches its remote. Set aside on purpose anything that doesn't belong in a commit, and name it in the report.
   - **In each worktree from step 1 other than the main checkout,** since step 6 or step 7 may free it: list the ignored and untracked files with `git status --ignored` and copy out what's worth keeping, where `/orchestrating`'s `folder-standard.md` puts each kind, since removing a worktree deletes them. Copy editor settings like `.vscode/` to the main checkout, keeping the main checkout's own copy of any file already there.
   - **After an interrupted or rejected commit or push:** check the log before retrying, because it may have landed anyway.
   - **When the changes sit on the default branch or in the user's main checkout:** commit only this session's own changes, on a new branch, and open its pull request with `/to-pr`. Leave the user's other changes where they are, and push nothing to the default branch.
   - **When the work's branch has already merged,** and settling changes tracked files, such as status changes or files copied out of a worktree: put the changes on a small follow-up branch and open its pull request with `/to-pr`. Leave the user's main checkout on its branch, since they may be working there, and pull in it only when it is clean and already on the default branch. Make the follow-up worktree with `<worktree-tool>` from the remote default branch, and free it once its branch is pushed.
6. **Nothing in the way.** Free the branches and worktrees from step 1 whose work is proven merged, and keep each one you can't prove, naming it in the report. Leave out this session's own worktree and its branch, which step 7 frees, and the main checkout and the default branch, which stay. Run `git fetch --prune` first, so the remote default branch is current. Three proofs count:
   - **Reachable:** `git merge-base --is-ancestor` with the branch and the remote default branch succeeds, as after a merge commit or a fast-forward. It is the cheapest, so try it first.
   - **Matched by patch:** `git cherry` with the remote default branch and the branch prints no `+` line, as after a rebase or an unchanged cherry-pick. A `+` proves nothing either way.
   - **In the merged pull request's head:** the hosting service shows the pull request merged, and the branch's tip is its head commit or an ancestor of it. A branch whose commit was integrated into the pull request's branch counts when the head contains that commit, or a commit carrying the same change as `git range-diff` or the diff shows, and the branch holds nothing else; when unsure, keep the branch. A squash merge, or a commit changed while it was integrated, fails the first two proofs; only this one proves it.

   Free worktrees with `<worktree-tool>`, before their branches, since git won't delete a branch a worktree has checked out. Remove a worktree without `--force`, because a worktree that needs it isn't clean. Delete a local branch with `git branch -d` after the reachable proof, and with `git branch -D` when only the other two prove it. Use `git branch -D` too when `-d` refuses a branch the reachable proof passed, since `-d` checks against the branch's upstream or `HEAD`, not the remote default branch.
   - **When an agent is still working in a worktree:** leave that worktree. `<session-host>` shows which agents are still working, and where.
   - **When a freed branch has a remote branch:** delete it too once `git ls-remote --heads origin <branch>` shows it still exists and its tip is the local branch's tip or passes one of the proofs above; the repository may have deleted it on merge. Otherwise keep the remote branch and name it in the report.
7. **Report** what was done, what was filed and where, what was kept and why, and what waits on the user. Then, through `<session-host>`, mark this session as settled where the host labels sessions. When this session's own worktree and branch are proven merged, delete the branch's remote copy as step 6 does. As your last action, free this session's own worktree from outside it, then its branch, under the same proofs as step 6, since freeing the worktree ends this session.
   - **When this session's own worktree isn't proven merged:** keep it and its branch, and name them in the report; the report and the settled mark end the settle.
   - **When this session has no worktree of its own,** such as when it runs in the main checkout: the report and the settled mark end the settle.
   - **When `<session-host>` can't run a command from outside this session:** give the user the commands that free this session's own worktree and branch, to run once the session is closed, and name them in the report.
