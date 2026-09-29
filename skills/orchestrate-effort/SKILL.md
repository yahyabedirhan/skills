---
name: orchestrate-effort
description: Build an effort from its spec and tickets by orchestrating sub-agents, and deliver a pull request. Use when asked to build or orchestrate an effort from its spec and tickets.
argument-hint: "Path to the effort folder, or to the spec and tickets"
---

# Orchestrate Effort

Build one effort from its spec and tickets, as its orchestrator, following the **orchestrating** skill. Work in the current checkout: the effort's worktree and branch were chosen when it started.

## 1. Read the effort

The argument points at the **effort folder** (`.efforts/<effort>/` on a local tracker, holding `spec.md` and `issues/`, per the folder standard in the **orchestrating** skill's `folders.md`) or at the spec and tickets directly. With no argument, ask for one. Read the spec, the handoff and every ticket in full, and treat the design as settled: decide a real gap yourself rather than redesigning, and record the decision (the **orchestrating** skill's *Talking to the user*). With no tickets, tell the user so and stop: the tickets come from the **to-tickets** skill, in a session they run or ask for.

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
- **Hosted tracker** (GitHub, Linear): tick the issue's checklist the same way once the commit is pushed, and close the issue only when every box is ticked, unless it goes to the user for QA.

**Integrate** each batch of reports: cherry-pick each delegate's commit onto the effort branch with `--no-commit`, tick its criteria, and commit it as the ticket's own commit following the repository's conventions. Resolve conflicts as they come. Then run the tests, the install and the real-app check once for the batch, and push. Right after the push, remove each integrated delegate's worktree and its branch (`git worktree remove <path>`, then `git branch -D <branch>`): the ticket's commit on the pushed effort branch is the proof its work landed, since a cherry-pick with ticked criteria no longer matches the delegate's commit by patch. A removal a permission check refuses stays for **close-effort**. Then tell the user in a line what landed.

**QA**, only in a project whose instructions opt in to it, naming how a build reaches the user (an install, a dev server, a preview link). A ticket that adds or changes something the user can use goes to them to try in the real app once its batch is integrated and the build reaches them:

- The ticket stays open, assigned to the user (on a local tracker, its status says it waits for their QA), with a "Ready for you to try" comment: the build and how to reach it, how to use the feature, numbered try-this steps with known risks marked, and what to do when done (close the ticket if it's good, or comment with the step number and what they saw).
- Commits and the pull request say "Refs #n" for it, never "Closes #n", so the merge doesn't close it before the user has tried it.
- **Non-blocking by default:** the merge doesn't wait for QA. Only when the spec says "QA: blocking" does the pull request wait until the user closes each of these tickets; say so in the pull request.

Done when every ticket is committed and pushed, with its criteria ticked or noted, or deferred by the user.

## 4. Deliver

Delegate the final review to a sub-agent: the full checks and **code-review** over the whole branch against its base. Delegate the fixes for what it finds the same way you delegated tickets, then commit them. Open the pull request with the **to-pr** skill, and fill its last section, *Things to be aware of*, from your running list (the **orchestrating** skill's *Talking to the user*): every decision you made alone with its reason, the surprises and skipped checks delegates reported, what the effort leaves out, and each follow-up marked as a ticket, a todo for the user, or nothing needed. It is the only report-back the user reads besides the diff, so nothing you learned during the build is left only in this session.

Leave the worktree clean, and check it with `git status`. Delivery itself writes nothing to commit: **to-pr** saves the description's source in the ignored `.scratch/` (the **orchestrating** skill's `folders.md`), and so does a rerun that rewrites it. Anything `git status` still shows is effort work to commit and push, or a file you leave out on purpose.

Report the pull request, each ticket's commit, anything deferred, the tickets waiting for the user's QA (and whether the merge waits for them), and the `git status` result: clean, or each file left out with its reason. Besides any QA, the user's only step is to review the pull request and say "go". List what you will do once told, as your own steps: merge the pull request, run the effort's post-merge follow-ups (such as installs or updates), try what can only be tried after the merge and report the result, and close the effort with the **close-effort** skill. Last, send the "done" notification, following the **orchestrating** skill's `notify.md`.
