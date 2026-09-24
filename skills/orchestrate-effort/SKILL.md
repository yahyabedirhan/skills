---
name: orchestrate-effort
description: Build an effort from its spec and tickets by orchestrating sub-agents, and deliver a pull request. Use when asked to build or orchestrate an effort from its spec and tickets.
argument-hint: "Path to the effort folder, or to the spec and tickets"
---

# Orchestrate Effort

Build one effort from its spec and tickets, as its orchestrator, following the **orchestrating** skill. Work in the current checkout: the effort's worktree and branch were chosen when it started.

## 1. Read the effort

The argument points at the **effort folder** (such as `.scratch/<effort>/`, holding `spec.md` and `issues/`) or at the spec and tickets directly. With no argument, ask for one. Read the spec and every ticket in full, and treat the design as settled: bring a real gap to the user rather than redesigning. With no tickets, tell the user to run `/to-tickets` and stop.

Done when you know each ticket's blockers, its acceptance criteria, and whether it needs the user.

## 2. Show the plan

Use the **show-me** skill to show the user the ticket order as a tree: blockers first, which tickets run in parallel (only those touching disjoint files), and which need the user and for what.

## 3. Run the tickets

Delegate each unblocked ticket to a sub-agent with the **implement** skill. Point it at the ticket and the spec by path, and tell it that you commit, so it reports instead: the files it changed, the checks and their results, and any open question.

Read each report against the ticket's acceptance criteria. Commit the ticket on its own following the repository's conventions, push, mark it done in the tracker, and tell the user in a line what landed.

Done when every ticket is committed and pushed, or deferred by the user.

## 4. Deliver

Delegate the final review to a sub-agent: the full checks and **code-review** over the whole branch against its base. Delegate the fixes for what it finds the same way you delegated tickets, then commit them. Open the pull request with the **to-pr** skill. Report the pull request, each ticket's commit, anything deferred, and what the user does next: review and merge, then close the effort's worktree the way it was created.
