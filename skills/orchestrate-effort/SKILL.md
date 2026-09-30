---
name: orchestrate-effort
description: Build an effort by orchestrating sub-agents, and deliver a pull request. Use when asked to build or orchestrate an effort from its spec and tickets.
argument-hint: "Path to the effort folder, or to the spec and tickets"
---

# Orchestrate Effort

Build one effort from its spec and tickets, as its orchestrator, following `/orchestrating`. Work in the current checkout: the effort's worktree and branch were chosen when it started.

## 1. Read the effort

The argument points at the effort folder or at the spec and tickets. With no argument, ask for one. Read the spec, the handoff and every ticket in full, and treat the design as settled: where they leave a question open, decide it yourself within that design rather than redesigning. With no tickets, tell the user so and stop: the tickets come from `/to-tickets`, in a session they run or ask for.

Before any ticket runs, commit whatever is uncommitted in the worktree in a commit of its own, and push. Each ticket then starts from a clean worktree, so no delegate finds files it may not touch and has to work around them.

Done when you know each ticket's blockers and acceptance criteria, you have found in the handoff any input a ticket needs that only the user can give, and `git status` shows a clean worktree.

## 2. Show the plan

Use `/show-me` to show the user the ticket order as a tree: blockers first, which tickets run in parallel, which use an input from the user, and each ticket's review depth. Show it and go on to the next step without waiting for a reply: the plan informs the user and asks them nothing.

- **Parallel by default.** Unblocked tickets run at the same time. Serialise only the step that uses a shared resource, such as an installed app, a single real UI, a port or a database, not the whole ticket. Overlapping files are no reason to serialise: conflicts are cheap to resolve at integration.
- **Review depth.** Choose it per ticket. Give a large or risky ticket its own `/code-review`. A small, low-risk ticket gets none of its own, because the one review of the whole branch at delivery covers it.

## 3. Run the tickets

Delegate each unblocked ticket to a sub-agent with `/implement`, in its own git worktree, where it makes one commit and doesn't push.

- **Put in the brief** the paths to the ticket, the spec and the handoff; the review depth; the shared resources it leaves to you; and the report you want back. That report gives its commit, the files it changed, the evidence for each acceptance criterion, proof that no temporary verification code is left, anything left running, and any open question.
- **Leave out of the brief** recipes and conventions the repository already documents, its commit rules included, since the delegate reads them there.

Have delegates verify in the real app, with real screenshots and clicks, wherever the machine allows it, rather than with off-screen renders, which cost time and have missed a bug the first real-screen check caught. When the real app is a shared resource, have the delegate verify what it can in its worktree, and run the real-app check once per batch at integration.

Note each delegate's duration as its report arrives, so a slow ticket shows up early.

**Done** means every criterion ticked on evidence: tick a box only where the report shows evidence for it. A criterion shown only outside the checkout, such as on a copy of the branch, in another environment or after an install, stays unticked with a one-line note saying where it was shown and what confirms it; the ticket stays open until it is confirmed.

- **Local tracker:** the ticked boxes and the done status go in the ticket's own commit, with its code.
- **Hosted tracker:** tick the issue's checklist the same way once the commit is pushed, and close the issue once every box is ticked, except a ticket that goes to the user for QA, which stays open.

**Integrate** each batch of reports: cherry-pick each delegate's commit onto the effort branch with `--no-commit`, tick its criteria, and commit it as the ticket's own commit. Then run the tests, the install and the real-app check once for the batch, and push. Right after the push, remove each integrated delegate's worktree and its branch. The ticket's commit on the pushed effort branch is the proof its work landed: git can't show the delegate's branch as merged, because the cherry-pick, with its ticked criteria, no longer matches the delegate's commit by patch. If a permission check refuses a removal, leave that worktree or branch for `/close-effort`. Then tell the user in a line what landed.

**QA** runs only in a project whose instructions opt in to it and say how a build reaches the user, for example through an install, a dev server or a preview link. Once a batch is integrated and its build reaches the user, give them each ticket in it that adds or changes something they can use, to try in the real app:

- The ticket stays open and assigned to the user, and on a local tracker its status says it waits for their QA. It gets a "Ready for you to try" comment: the build and how to reach it, how to use the feature, numbered try-this steps with known risks marked, and what to do when done, which is to close the ticket if it's good or to comment with the step number and what they saw.
- Commits and the pull request say "Refs #n" for it, never "Closes #n", so the merge doesn't close it before the user has tried it.
- **Non-blocking by default:** the merge doesn't wait for QA. Only when the spec says "QA: blocking" does the pull request wait until the user closes each of these tickets; say so in the pull request.

Done when every ticket is committed and pushed, with its criteria ticked or noted, or deferred by the user.

## 4. Deliver

Delegate the final review to a sub-agent: the full checks and `/code-review` over the whole branch against its base. Delegate the fixes for what it finds the same way you delegated tickets, then commit them. Open the pull request with `/to-pr`, and put in its description your running list of decisions and the surprises and skipped checks delegates reported. Besides the diff, the description is the only report the user reads, so put in it everything you learned during the build; whatever you leave out stays behind in this session.

Done when `git status` shows a clean worktree: anything it still shows is effort work to commit and push, or a file you leave out on purpose.

Report the pull request, each ticket's commit, anything deferred, the tickets waiting for the user's QA and whether the merge waits for them, and the `git status` result: clean, or each file left out with its reason. Besides any QA, the user's only step is to review and approve the pull request. List what you will do once told, as your own steps: merge the pull request, run the effort's post-merge follow-ups such as installs or updates, try what can only be tried after the merge and report the result, and close the effort with `/close-effort`.
