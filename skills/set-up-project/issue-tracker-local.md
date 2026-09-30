# Issue tracker: Local Markdown

Issues and specs for this repo live as markdown files in `.efforts/`, tracked in git.

## Conventions

- One effort per directory: `.efforts/<effort>/` (`<effort>` is the effort's name, or a short slug for the feature when there is no effort)
- The spec is `.efforts/<effort>/spec.md`, when the work has one; a small ticket may have none, and is then its own spec
- Implementation issues are one file per ticket at `.efforts/<effort>/issues/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file
- Triage state is recorded as a `Status:` line near the top of each issue file: the role strings in `triage-labels.md` when the project has one, else the role names themselves (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`)
- A finished ticket gets its criteria ticked and `Status: done`, in the same commit as its work
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "pick up the next ticket"

Take the lowest-numbered ticket with `Status: ready-for-agent` whose "Blocked by" tickets are all `done`.

## When a skill says "publish to the issue tracker"

Create a new file under `.efforts/<effort>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `.efforts/<effort>/map.md` (the Notes / Decisions-so-far / Fog body).
- **Child ticket**: `.efforts/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved`.
- **Frontier**: scan `.efforts/<effort>/issues/` for files that are open, unblocked, and unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.
