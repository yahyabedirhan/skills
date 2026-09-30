# User QA

How to hand a ticket to the user for QA. A project's instructions say how a build reaches the user, for example through an install, a dev server or a preview link. Once a batch is integrated and its build reaches the user, give them each ticket in it that adds or changes something they can use, to try in the real app.

## The QA ticket

The ticket stays open and assigned to the user. On a local tracker, its status says it waits for their QA. It gets a "Ready for you to try" comment with:

- the build and how to reach it;
- how to use the feature;
- numbered try-this steps, with known risks marked;
- what to do when done: close the ticket if it's good, or comment with the step number and what they saw.

Commits and the pull request say "Refs #n" for the ticket, never "Closes #n", so the merge doesn't close it before the user has tried it.
