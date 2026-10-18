# Decisions: to-pr

The decisions behind the `to-pr` skill. This file is for maintaining it and is never installed. Read it before changing the skill. Entries follow the shape in [index.md](index.md).

## 2026-09-28: review links go in the chat report, not the description

- **Status:** accepted
- **Context:** The maintainer reviews small changes, such as a README or a `SKILL.md`, without checking out the branch.
- **Options:** Put the links in the description: it must stay within its template.
- **Choice and why:** After opening or updating a pull request, the chat report gives each changed file a link to its final version and one to its diff.
- **Consequences:** None.

## 2026-09-28: the final version links the head commit, not the branch

- **Status:** accepted
- **Context:** A branch link changes as the branch moves, and breaks when it is deleted.
- **Options:** Link the branch.
- **Choice and why:** Link `blob/<head-sha>/<path>`. It shows exactly the version under review, and still resolves after the branch moves or is deleted.
- **Consequences:** An update reports the new head.

## 2026-09-28: the diff anchor is #diff-<sha256 of the path>

- **Status:** accepted
- **Context:** A diff link should scroll to its file.
- **Options:** None considered.
- **Choice and why:** GitHub doesn't document the anchor, but its Files changed page uses that id for each file. This was checked on a pull request in this repo.
- **Consequences:** If GitHub changes the id, the link still opens Files changed, without scrolling to the file.
