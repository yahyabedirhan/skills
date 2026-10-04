# Issue tracker: Local Markdown

Issues and specs for this repo live as markdown files in `.efforts/`, tracked in git.

## Conventions

- One effort per directory: `.efforts/<effort>/` (`<effort>` is the effort's name, or a short slug for the feature when there is no effort)
- The spec is `.efforts/<effort>/spec.md`, when the work has one; a small ticket may have none, and is then its own spec
- Implementation issues are one file per ticket at `.efforts/<effort>/issues/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file
- Triage state is recorded as a `Status:` line near the top of each issue file: the role strings in `triage-labels.md` when the project has one, else the role names themselves (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`)
- A finished ticket gets its criteria ticked and `Status: done`, in the same commit as its work
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## Title prefixes

The title is the ticket file's `# ` heading, after its `<NN>: ` number. Start every issue title with one prefix, then `: ` and a capitalized title with no trailing period, for example `QA: Verify the panel on a VPS`. When more than one prefix fits, use the first one in this order:

1. `QA`: manual work for the maintainer.
2. `VPS`: work on a remote machine.
3. A harness: `Claude` (claude.ai, cloud sessions and managed agents), `Codex`, `OpenCode`, `Cursor` or `Pi`. Claude Code is the default harness, so it gets no prefix.
4. A semantic prefix from the list below: one area of this project.
5. `Bug`, `Feature`, `Chore` or `Spec`: the kind of work.
6. `Research`: a question to answer before the work starts.

Write each prefix the way its maker writes it. Use a semantic prefix before a generic one when one fits.

### Semantic prefixes

- `<Name>`: <the area it covers>. _(For `/set-up-project`: one line for each area of this project, seeded from its open issue titles.)_

Reuse a prefix from this list before you add a new one. Add a new one when no prefix fits and the issue belongs to one tool, product, skill or workflow. Add it to this list in the same change.

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
