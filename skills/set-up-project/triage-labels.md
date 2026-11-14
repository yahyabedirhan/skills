# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

Edit the right-hand column to match whatever vocabulary you actually use.

## Roadmap mode

_For `/set-up-project`: in roadmap mode, write this section in place of everything above it, whether or not `triage` is installed. Remove it otherwise._

Triage happens in Linear, so GitHub issues carry only the labels agents use:

| Label | Meaning |
| ----- | ------- |
| `ready-for-agent` | A spec or ticket that is fully specified and ready for an agent |
| `wontfix` | Will not be actioned |
| `effort:<name>` | Part of the effort `<name>` |

The roles `needs-triage`, `needs-info` and `ready-for-human` have no GitHub label here. Do that work in Linear, as `docs/agents/roadmap.md` says.
