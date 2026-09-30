---
name: close-effort
description: Close an effort after its pull request is approved - merge it, run the post-merge follow-ups, carry unfinished work into next-effort tickets, close the tracker, and free the branches and worktrees proven merged. Use when the maintainer says an effort's pull request is good, that it merged, or to merge it.
argument-hint: "The pull request (optional: defaults to the current branch's)"
---

# Close Effort

Approving the pull request is the maintainer's last step. Everything after it is yours, so run every command yourself rather than handing the maintainer commands to paste. Leave workspaces and agent sessions open; the maintainer closes them.

[command-reference.md](command-reference.md) holds the git and gh commands for these steps, with their pitfalls and the three ways to prove work merged. Read it before running them.

## Parameters

- `<worktree-tool>`: the tool that makes and frees worktrees, e.g. Treehouse, or plain git worktrees.
- `<session-host>`: where agent sessions run, e.g. Herdr, Claude Code Desktop, Codex Desktop.

## Flow

1. **Find the effort:** the pull request, its branch, spec, tickets and handoff, and the worktrees and branches the build left behind.
2. **Merge** the pull request once its checks pass. When the spec says "QA: blocking", wait until every QA ticket is closed, and tell the maintainer which ones are still open. After the merge, check that the default branch's CI passes, and that anything pinned to a branch commit still resolves after a squash or rebase.
3. **Read the pull request's description and the handoff** for what the delivery left open: follow-ups, checks it skipped, which you run now, and decisions for the maintainer.
4. **Run the post-merge follow-ups,** such as installing what changed or trying what could only be tried after the merge.
5. **Carry unfinished work over** as tickets in the next effort, labelled for it and linked back to where each came from; ask the maintainer which effort is next when it isn't clear. Leave QA tickets open for the maintainer, with a comment on how to reach the build. Close the spec and every ticket the merge finished, including any a "closes" keyword missed.
6. **Save what exists only in a worktree or this session.** Removing a worktree deletes its ignored and untracked files, so copy out what's worth keeping. Commit and push this session's work, and put what it knows that isn't written down in a ticket or a handoff.
7. **Free the branches and worktrees whose work is proven merged,** and keep anything you can't prove, naming it in the report. Leave a worktree where an agent is still working.
8. **Report** what merged, what closed, what carried over and what waits on the maintainer. Then free this session's own worktree from outside it, through `<session-host>`, as your last action: freeing it ends this session.

The close's own changes to tracked files, such as done marks or saved files, go through a pull request like any other change. Put them on a small follow-up branch, and leave the maintainer's main checkout on its branch, since they may be working there. Once that branch is pushed, free its worktree.
