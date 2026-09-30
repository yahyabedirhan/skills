---
name: orchestrate-effort
description: Build an effort by orchestrating sub-agents, and deliver a pull request. Use when asked to build or orchestrate an effort from its spec and tickets.
argument-hint: "Path to the effort folder, or to the spec and tickets"
---

# Orchestrate Effort

Build one effort from its spec and tickets, as its orchestrator, following `/orchestrating`. Work in the current checkout: the effort's worktree and branch were chosen when it started.

## 1. Read the effort

The argument points at the effort folder or at the spec and tickets. With no argument, ask for one. Read the spec, the handoff and every ticket in full, and treat the design as settled: fill a real gap with a decision of your own rather than a redesign. With no tickets, tell the user so and stop: the tickets come from `/to-tickets`, in a session they run or ask for.

Before any ticket runs, commit whatever is uncommitted in the worktree in a commit of its own, and push. Tickets start from a clean worktree, so no delegate works around files it may not touch.

Done when you know each ticket's blockers, its acceptance criteria, and any input only the user has that it needs, found in the handoff, and `git status` shows a clean worktree.

## 2. Show the plan

Use `/show-me` to show the user the ticket order as a tree: blockers first, which tickets run in parallel, which use an input from the user, and each ticket's review depth. Show it and carry on: the plan asks nothing.

- **Parallel by default.** Unblocked tickets run at the same time. Serialise only the step that uses a shared resource, such as an installed app, a single real UI, a port or a database, not the whole ticket. Overlapping files are no reason to serialise: conflicts are cheap to resolve at integration.
- **Review depth.** A granular ticket skips `/code-review` and relies on the one branch review at delivery; a large or risky ticket gets its own review. You choose it per ticket.

## 3. Run the tickets

Delegate each unblocked ticket to a sub-agent with `/implement`, in its own git worktree, where it makes one commit and doesn't push.

- **The brief contains** the paths to the ticket, the spec and the handoff; the review depth; the shared resources it leaves to you; and the report you want back. That report gives its commit, the files it changed, the evidence for each acceptance criterion, proof that no temporary verification code is left, anything left running, and any open question.
- **It leaves out** recipes and conventions the repository already documents, its commit rules included.

Verification uses the real app, with real screenshots and clicks, wherever the machine allows it, rather than off-screen renders, which cost time and have missed a bug the first real-screen check caught. When the real app is a shared resource, the delegate verifies what it can in its worktree, and the real-app check runs once per batch at integration.

Note each delegate's duration as its report arrives, so a slow ticket shows up early.

**Done** means every criterion ticked on evidence: tick a box only where the report shows evidence for it. A criterion shown only outside the checkout, such as on a copy of the branch, in another environment or after an install, stays unticked with a one-line note saying where it was shown and what confirms it; the ticket stays open until it is confirmed.

- **Local tracker:** the ticked boxes and the done status go in the ticket's own commit, with its code.
- **Hosted tracker:** tick the issue's checklist the same way once the commit is pushed, and close the issue only when every box is ticked, unless it goes to the user for QA.

**Integrate** each batch of reports: cherry-pick each delegate's commit onto the effort branch with `--no-commit`, tick its criteria, and commit it as the ticket's own commit. Then run the tests, the install and the real-app check once for the batch, and push. Right after the push, remove each integrated delegate's worktree and its branch: the ticket's commit on the pushed effort branch is the proof its work landed, since a cherry-pick with ticked criteria no longer matches the delegate's commit by patch. A removal a permission check refuses stays for `/close-effort`. Then tell the user in a line what landed.

**QA** runs only in a project whose instructions opt in to it and say how a build reaches the user, for example through an install, a dev server or a preview link. A ticket that adds or changes something the user can use goes to them to try in the real app once its batch is integrated and the build reaches them:

- The ticket stays open and assigned to the user, and on a local tracker its status says it waits for their QA. It gets a "Ready for you to try" comment: the build and how to reach it, how to use the feature, numbered try-this steps with known risks marked, and what to do when done, which is to close the ticket if it's good or to comment with the step number and what they saw.
- Commits and the pull request say "Refs #n" for it, never "Closes #n", so the merge doesn't close it before the user has tried it.
- **Non-blocking by default:** the merge doesn't wait for QA. Only when the spec says "QA: blocking" does the pull request wait until the user closes each of these tickets; say so in the pull request.

Done when every ticket is committed and pushed, with its criteria ticked or noted, or deferred by the user.

## 4. Deliver

Delegate the final review to a sub-agent: the full checks and `/code-review` over the whole branch against its base. Delegate the fixes for what it finds the same way you delegated tickets, then commit them. Open the pull request with `/to-pr`, and fill its last section, *Things to be aware of*, from your running list of decisions and from the surprises and skipped checks delegates reported. It is the only report-back the user reads besides the diff, so nothing you learned during the build is left only in this session.

Done when `git status` shows a clean worktree: anything it still shows is effort work to commit and push, or a file you leave out on purpose.

Report the pull request, each ticket's commit, anything deferred, the tickets waiting for the user's QA and whether the merge waits for them, and the `git status` result: clean, or each file left out with its reason. Besides any QA, the user's only step is to review and approve the pull request. List what you will do once told, as your own steps: merge the pull request, run the effort's post-merge follow-ups such as installs or updates, try what can only be tried after the merge and report the result, and close the effort with `/close-effort`.
