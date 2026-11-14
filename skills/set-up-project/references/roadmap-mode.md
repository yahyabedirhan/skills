# Roadmap mode

How `/set-up-project` sets up, moves and audits a project in roadmap mode: the notes hold the project's history, the roadmap what to build and its status, and GitHub issues only the agent specs and tickets.

## The docs/agents set

Write and audit these files together, since each one names the others:

- `docs/agents/roadmap.md` from the seed for the roadmap tool, `roadmap-<tool>.md`: today only [../roadmap-linear.md](../roadmap-linear.md).
  Look up each `<slot>` the seed names through the roadmap tool.
  Ask the maintainer only for what you cannot find.
- `docs/agents/notes.md` from the seed for the notes tool, `notes-<tool>.md`: today only [../notes-notion.md](../notes-notion.md).
  Look up its `<slot>` through the notes tool, and ask the maintainer only for what you cannot find.
- `docs/agents/issue-tracker.md` from [../issue-tracker-github.md](../issue-tracker-github.md), with its 'Roadmap mode' section kept and the `QA` prefix removed.
- `docs/agents/triage-labels.md` from the 'Roadmap mode' section of [../triage-labels.md](../triage-labels.md), whether or not `triage` is installed.
- `docs/agents/releasing.md` from [../releasing.md](../releasing.md), with its 'Release groups' section kept.
  Section E runs whenever the project ships to anyone, also before its first release.
- `docs/agents/domain.md` from [../domain.md](../domain.md), with its 'History and current state' section kept.
- The `## Agent skills` block in `AGENTS.md`, with the `### Roadmap` and `### Notes` sub-blocks and a pointer to each file above, as [../agents-md.md](../agents-md.md) > 'Roadmap mode' says.

## Moving a project from GitHub-only mode

Move a project only when the maintainer asks, in one run:

1. Draft the set above, and take the one approval step 4 takes.
2. List the open GitHub issues that no longer belong there: QA tickets, and issues labelled `needs-triage`, `needs-info` or `ready-for-human`.
   Propose a roadmap issue for each, as `docs/agents/roadmap.md` says, and a comment that closes the GitHub issue with a link to it.
3. List the open specs and tickets, and ask which roadmap issue each one serves. Add that link to each description.
4. List the GitHub labels the project no longer uses, and propose to delete each one.

Make the changes from steps 2 to 4 only on the maintainer's approval, since they change the project's issues.

## Audit

The audit keeps the project in roadmap mode. Report each of these:

- A file of the set that is missing.
- A slot in `docs/agents/roadmap.md` or `docs/agents/notes.md` that is still a `<slot>` or an italic note.
- A `docs/agents/issue-tracker.md` with a `QA` prefix, or without its 'Roadmap mode' section.
- A `docs/agents/triage-labels.md` that names other labels than `ready-for-agent`, `wontfix` and `effort:<name>`.
- A `docs/agents/releasing.md` without its 'Release groups' section.
- An `## Agent skills` block without the `### Roadmap` or `### Notes` sub-block, or without a pointer to a file of the set.
- An open GitHub issue titled `QA: ...`, or labelled `needs-triage`, `needs-info` or `ready-for-human`.

Propose the fix that the setup steps above would write.
