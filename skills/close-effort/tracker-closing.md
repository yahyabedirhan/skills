# Tracker closing

## Carrying work over

Nothing unfinished is dropped: the effort's open tickets, follow-ups from the pull request and the handoff, review findings deferred at delivery, a red run or a broken pin, stale docs.

Carry each item over as a ticket in the next effort, labelled with that effort's `effort:` label and linked back to where it came from. The next effort is the project's open spec or grilling ticket for its next round of work; when that isn't obvious, ask the maintainer. `gh issue create --label` fails when the label doesn't exist yet, so create the label first.

## QA tickets

With the default, non-blocking QA, the pull request said "Refs" rather than "Closes", so the merge left QA tickets open. They aren't unfinished work: leave them open and assigned to the maintainer, comment on each that the work is on the default branch and how to reach the build, and list them in the report.

## Closing tickets

Close the spec and every ticket the merge finished, including any a "closes" keyword missed because the ticket was named only in a commit or the pull request's base wasn't the default branch. Tick each criterion that could only be shown after the merge. Close each carried-over ticket with a link to the ticket that continues it. On a local tracker, mark them done on the follow-up branch.
