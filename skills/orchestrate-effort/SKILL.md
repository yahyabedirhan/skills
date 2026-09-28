---
name: orchestrate-effort
description: Build an effort from its spec and tickets by orchestrating sub-agents, and deliver a pull request. Use when asked to build or orchestrate an effort from its spec and tickets.
argument-hint: "Path to the effort folder, or to the spec and tickets"
---

# Orchestrate Effort

Build one effort from its spec and tickets, as its orchestrator, following the **orchestrating** skill. Work in the current checkout: the effort's worktree and branch were chosen when it started.

## 1. Read the effort

The argument points at the **effort folder** (`.efforts/<effort>/` on a local tracker, holding `spec.md` and `issues/`, per the folder standard in the **orchestrating** skill's `folders.md`) or at the spec and tickets directly. With no argument, ask for one. Read the spec, the handoff and every ticket in full, and treat the design as settled: decide a real gap yourself rather than redesigning, and record the decision (the **orchestrating** skill's *Talking to the user*). With no tickets, tell the user to run `/to-tickets` and stop.

Then check the worktree with `git status`. Uncommitted changes found there go into their own commit, with a message that describes them, before any ticket runs; commit them as their own command, then push. Tickets start from a clean worktree, so no delegate works around files it may not touch.

Done when you know each ticket's blockers, its acceptance criteria, and any input only the user has that it needs, found in the handoff, and `git status` shows a clean worktree. A missing input doesn't stop the run: build everything that doesn't need it, and ask only when nothing else can continue.

## 2. Show the plan

Use the **show-me** skill to show the user the ticket order as a tree: blockers first, which tickets run in parallel, which use an input from the user, and each ticket's review depth. Show it and carry on: the plan asks nothing.

- **Parallel by default.** Unblocked tickets run at the same time, each in its own git worktree. Serialise only the step that uses a shared resource (an installed app, a single real UI, a port, a database), not the whole ticket. Overlapping files are no reason to serialise: conflicts are cheap to resolve at integration.
- **Review depth.** A granular ticket skips **code-review** and relies on the one branch review at delivery; a large or risky ticket gets its own review. You choose per ticket and say so in its brief.

## 3. Run the tickets

Delegate each unblocked ticket to a sub-agent with the **implement** skill, in its own git worktree (the harness's worktree isolation, else `git worktree add`), where it makes one commit and doesn't push. The brief points instead of restating:

- **It contains:** the paths to the ticket, the spec and the handoff; the review depth; the shared resources it leaves to you; and the report you want back: its commit, the files it changed, the evidence for each acceptance criterion (a test name, a run count, a file and line, a command's output), proof that no temporary verification code is left (`git status`, a grep for its marker), anything left running, and any open question.
- **It leaves out:** a paraphrase of the ticket or spec, recipes and conventions the repository already documents, and the repository's commit rules.

Verification checks the real app where the machine allows it (real screenshots and clicks) rather than off-screen renders. When the real app is a shared resource, the delegate verifies what it can in its worktree, and the real-app check runs once per batch at integration.

Note each delegate's duration as its report arrives, so a slow ticket shows up early.

**Done** means every criterion ticked on evidence. Read each report against the ticket's acceptance criteria and tick a box only where the report shows evidence for it. A criterion shown only outside the checkout (on a copy of the branch, in another environment, after an install) stays unticked with a one-line note saying where it was shown and what confirms it; the ticket stays open until it is confirmed.

- **Local tracker:** the ticked boxes and the done status go in the ticket's own commit, with its code.
- **Hosted tracker** (GitHub, Linear): tick the issue's checklist the same way once the commit is pushed, and close the issue only when every box is ticked.

**Integrate** each batch of reports: cherry-pick each delegate's commit onto the effort branch with `--no-commit`, tick its criteria, and commit it as the ticket's own commit following the repository's conventions. Resolve conflicts as they come. Then run the tests, the install and the real-app check once for the batch, push, remove the delegates' worktrees, and tell the user in a line what landed.

Done when every ticket is committed and pushed, with its criteria ticked or noted, or deferred by the user.

## 4. Deliver

Delegate the final review to a sub-agent: the full checks and **code-review** over the whole branch against its base. Delegate the fixes for what it finds the same way you delegated tickets, then commit them. Open the pull request with the **to-pr** skill; the decisions you made alone go in its last section. Report the pull request, each ticket's commit, anything deferred, and what the user does next: review and merge, then close the effort's worktree the way it was created.
