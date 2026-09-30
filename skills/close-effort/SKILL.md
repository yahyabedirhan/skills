---
name: close-effort
description: Close an effort after its pull request is approved - merge it, run the post-merge follow-ups, carry unfinished work into next-effort tickets, close the tracker, and free the branches and worktrees proven merged. Use when the maintainer says an effort's pull request is good, that it merged, or to merge it.
argument-hint: "The pull request (optional: defaults to the current branch's)"
---

# Close Effort

Approving the pull request is the maintainer's last step. Everything after it is yours, so run every command yourself rather than handing the maintainer commands to paste. Leave workspaces and agent sessions open; the maintainer closes them.

## Parameters

- `<worktree-tool>`: the tool that makes and frees worktrees. When it is Treehouse, use `/treehouse`, and return worktrees to its pool rather than destroying them, so the next effort finds one ready. Default: `git worktree add` and `git worktree remove`.
- `<session-host>`: where the effort's agent sessions run. When it is Herdr, use `/handover-to-herdr`'s `close-effort-commands.md`. Default: end the report with the command that frees this session's worktree, for the maintainer to run once this session is closed.

## Flow

1. **Find the effort:** the pull request, its branch, spec, tickets and handoff, and the worktrees and branches the build left behind.
2. **Merge** the pull request once its checks pass, and check the merge broke nothing.
3. **Read the pull request's description and the handoff** for what the delivery left open: follow-ups, checks it skipped, which you run now, and decisions for the maintainer.
4. **Run the post-merge follow-ups,** such as installing what changed or trying what could only be tried after the merge.
5. **Carry unfinished work over** into tickets for the next effort, and close the tracker.
6. **Save what exists only in a worktree or this session,** so another session could continue from the repository and the tracker alone.
7. **Free the branches and worktrees whose work is proven merged.**
8. **Report** what merged, what closed, what carried over and what waits on the maintainer. Then free this session's own worktree from outside it, through `<session-host>`, as your last action: freeing it ends this session.

## References

Read each when its step comes up:

- [merge-checks.md](merge-checks.md): finding the pull request, blocking QA, the merge method, and checking the merge.
- [follow-up-changes.md](follow-up-changes.md): where the close's own changes go without moving the maintainer's checkout.
- [tracker-closing.md](tracker-closing.md): carrying work over, QA tickets, and closing tickets.
- [unsaved-work.md](unsaved-work.md): what removing a worktree deletes, and what this session still holds.
- [branch-cleanup.md](branch-cleanup.md): proving work merged, and freeing worktrees and branches.
