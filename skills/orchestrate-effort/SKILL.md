---
name: orchestrate-effort
description: Build an effort by orchestrating sub-agents, and deliver a pull request. Use when asked to build or orchestrate an effort from its spec and tickets.
argument-hint: "Path to the effort folder, or to the spec and tickets"
---

# Orchestrate Effort

Build one effort from its spec and tickets, as its orchestrator, following `/orchestrating`. Work in the current checkout: the effort's worktree and branch were chosen when it started. Treat the design as settled: where the spec, the handoff or a ticket leaves a question open, decide it yourself within that design rather than redesigning. Run tickets in parallel by default, and have them verified in the real app wherever the machine allows it.

## Flow

1. **Read the effort.** The argument points at the effort folder or at the spec and tickets; with no argument, ask for one. Read the spec, the handoff and every ticket in full, for each ticket's blockers, its acceptance criteria and any input only the user can give. With no tickets, tell the user so and stop: the tickets come from `/to-tickets`, in a session they run or ask for.
2. **Start from a clean worktree.** Commit whatever is uncommitted in its own commit and push, so no delegate finds files it may not touch and has to work around them.
3. **Show the plan** with `/show-me`, as a tree: blockers first, which tickets run in parallel, which use an input from the user, and each ticket's review depth. Go on without waiting for a reply: the plan informs the user and asks them nothing.
   - Serialise only the step that uses a shared resource, such as an installed app, a single real UI, a port or a database, not the whole ticket. Overlapping files are no reason to serialise: conflicts are cheap to resolve at integration.
   - Give a large or risky ticket its own `/code-review`. A small, low-risk ticket gets none, because the one review of the whole branch at delivery covers it.
4. **Delegate each unblocked ticket** to a sub-agent with `/implement`, in its own git worktree, where it makes one commit and doesn't push. Note each delegate's duration as its report arrives, so a slow ticket shows up early. Read `ticket-handling.md` before the first delegation.
5. **Integrate each batch of reports:** land each ticket as its own commit on the effort branch, with a criterion ticked only where the report shows evidence for it. Check the batch once, push, and remove the integrated delegates' worktrees and branches. Tell the user in a line what landed.
6. **Hand usable tickets to the user for QA,** only in a project whose instructions opt in to it and say how a build reaches the user. The merge doesn't wait for QA unless the spec says "QA: blocking".

   Repeat steps 4 to 6 until every ticket is committed and pushed, with its criteria ticked or noted, or deferred by the user.
7. **Deliver.** Delegate the final review to a sub-agent: the full checks and `/code-review` over the whole branch against its base. Delegate the fixes for what it finds the same way, then commit them. Open the pull request with `/to-pr`, and put in its description your running list of decisions and the surprises and skipped checks delegates reported. Besides the diff, the description is the only report the user reads, so whatever you learned and leave out of it stays behind in this session. Leave the worktree clean: commit and push any effort work `git status` still shows, or leave a file out on purpose.
8. **Report** the pull request, each ticket's commit, anything deferred, the tickets waiting for the user's QA and whether the merge waits for them, and the `git status` result: clean, or each file left out with its reason. Besides any QA, the user's only step is to review and approve the pull request. List what you will do once told, as your own steps: merge the pull request, run the effort's post-merge follow-ups such as installs or updates, try what can only be tried after the merge and report the result, and close the effort with `/close-effort`.

## References

- [ticket-handling.md](ticket-handling.md): a delegate's brief, integrating a batch and ticking criteria, and handing a ticket to the user for QA.
