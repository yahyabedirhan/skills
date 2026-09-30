# Change propagation

How a change reaches every place it applies: every harness on every machine, every install of a skill, every project it touches. A change is done only when it has reached all of them.

## Propagation paths

Make a change at its source, the place [environment-layers.md](environment-layers.md) chooses, then carry it from there as this table says.

| Change | Source | How it reaches everywhere |
|---|---|---|
| A permission (deny, ask, allow-and-report) | A row in `/set-up-machine`'s rule table, in the skills repo | Ship it to the skills repo; after the merge, update the installed skills and rerun `/set-up-machine` on each machine. |
| A global instruction | The shared global instructions file, from `/set-up-machine`'s global instructions reference | Rerun `/set-up-machine` on each machine; every harness reads the one shared file. |
| A project instruction or project permission | The project's `AGENTS.md` and allow-only project settings | Commit it in the project. For a standard every project shares, change `/set-up-project` instead and rerun it in each project. |
| A skill | Its source repo | Ship it (see [skill-operations.md](skill-operations.md), *Shipping to the skills repo*); after the merge, `npx skills update <name>` in every scope that installs it, on every machine. |
| A local skill | The project's `.agents/skills/` | Commit it with the project. |

Treat a change to a set-up skill itself, such as a new harness reference, a new rule in the table or a new project template, as a skill change first; then rerun that set-up skill wherever it applies.

## Outstanding steps

When a change can't be carried from this session (another machine, another project, a step that waits for a merge), end by naming each remaining step: which set-up skill (`/set-up-machine` or `/set-up-project`) or which `npx skills update`, and where it runs (this machine, each other machine, each project). Done when every place the change applies is either updated or named in that list.
