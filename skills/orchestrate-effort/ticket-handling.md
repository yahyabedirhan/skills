# Ticket handling

How to brief a delegate, integrate its work and hand a ticket to the user for QA.

## Delegate briefs

### What goes in

- The paths to the ticket, the spec and the handoff.
- The ticket's review depth.
- The shared resources it leaves to you.
- The report you want back: its commit, the files it changed, the evidence for each acceptance criterion, proof that no temporary verification code is left, anything left running, and any open question.

### What stays out

Recipes and conventions the repository already documents, its commit rules included. The delegate reads them there.

### Verification

Have the delegate verify in the real app, with real screenshots and clicks, rather than with off-screen renders. Off-screen renders cost time, and have missed a bug that the first real-screen check caught.

When the real app is a shared resource, have the delegate verify what it can in its worktree, and run the real-app check yourself once per batch at integration.

## Batch integration

### Landing each ticket

Cherry-pick the delegate's commit onto the effort branch with `--no-commit`, tick its criteria, and commit it as the ticket's own commit. Then run the tests, the install and the real-app check once for the whole batch, and push.

### Ticking criteria

A criterion shown only outside the checkout, such as on a copy of the branch, in another environment or after an install, stays unticked with a one-line note saying where it was shown and what confirms it; the ticket stays open until it is confirmed.

- **Local tracker:** the ticked boxes and the done status go in the ticket's own commit, with its code.
- **Hosted tracker:** tick the issue's checklist the same way once the commit is pushed, and close the issue once every box is ticked. A ticket that goes to the user for QA stays open.

### Removing delegate worktrees

Right after the push, remove each integrated delegate's worktree and its branch. The ticket's commit on the pushed effort branch is the proof its work landed. Git can't show the delegate's branch as merged, because the cherry-pick, with its ticked criteria, no longer matches the delegate's commit by patch.

If a permission check refuses a removal, leave that worktree or branch for `/close-effort`.

## User QA
A project's instructions say how a build reaches the user, for example through an install, a dev server or a preview link. Once a batch is integrated and its build reaches the user, give them each ticket in it that adds or changes something they can use, to try in the real app.

### The QA ticket

The ticket stays open and assigned to the user. On a local tracker, its status says it waits for their QA. It gets a "Ready for you to try" comment with:

- the build and how to reach it;
- how to use the feature;
- numbered try-this steps, with known risks marked;
- what to do when done: close the ticket if it's good, or comment with the step number and what they saw.

Commits and the pull request say "Refs #n" for the ticket, never "Closes #n", so the merge doesn't close it before the user has tried it.

### Blocking QA

When the spec says "QA: blocking", the pull request waits until the user closes each QA ticket; say so in the pull request.
