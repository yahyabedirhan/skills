# Decisions: to-pr

The decisions behind the `to-pr` skill. This file is for maintaining it and is never installed. Add an entry for each new decision: the date, what was decided, and why.

## 2026-09-28

- **Review links go in the chat report, not the description.** After opening or updating a pull request, the report gives each changed file a link to its final version and one to its diff, so the maintainer can review a small change (a README, a `SKILL.md`) without checking out the branch. The description stays within its template.
- **The final version links the head commit, not the branch.** `blob/<head-sha>/<path>` shows exactly the version under review and still resolves after the branch moves or is deleted; an update reports the new head.
- **The diff anchor is `#diff-<sha256 of the path>`.** GitHub doesn't document it, but its Files changed page uses that id for each file (checked on a pull request in this repo). If GitHub changes it, the link still opens Files changed, just without scrolling to the file.
