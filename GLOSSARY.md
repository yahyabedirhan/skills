# Skills repo glossary

This page defines the words this repo uses for its own skills and for maintaining them.
Read it before you add, fork or change a skill here, so a row, a decision record or a pull request uses each word the same way.
It holds only the words that belong to this repo.

## Language

### Skills and families

**Skill family**:
A group of skills that work together and name each other, such as the effort workflow or agent setup.
The README lists each family's skills in one table and explains the family in one section.

**Companion skill**:
A skill from another repo that a family here relies on, so you install it together with the family.

**Original skill**:
A skill written in this repo rather than copied from another one.
Its Origin cell shows the [`yahyabedirhan`](https://www.skills.sh/?q=yahyabedirhan) link.
_Avoid_: own skill, native skill

**Credited source**:
Someone else's work that an original skill draws on without copying its text or code.
The README names it in the skill's row, and [FORKS.md](FORKS.md#credited-sources) names its license.

### Forks

**Fork**:
A skill here that started as a copy of another repo's skill, with this repo's changes on top.
[FORKS.md](FORKS.md) lists every fork and everything it changes.
_Avoid_: port, clone

**Upstream**:
The repo and skill a fork was copied from.

**Origin column**:
The README column that says where each skill comes from: the `yahyabedirhan` link for an original skill, or the upstream and the origin commit for a fork.

**Origin commit**:
The upstream commit a fork was copied from, pinned in its README row and its FORKS.md entry.
Upgrading a fork diffs upstream from this commit.

**License file**:
The upstream license kept beside a fork's `SKILL.md`, named `LICENSE.<upstream>`, such as `LICENSE.mattpocock`.

**Replaced upstream skill**:
An upstream skill that a fork or an original skill here takes the place of, so you leave it out when you install the family.

### Setup and publishing

**Seed template**:
A file beside a skill's `SKILL.md` that the skill copies into a project and fills in, such as [set-up-project](skills/set-up-project/SKILL.md)'s `issue-tracker-github.md`.

**Lock file**:
The `skills-lock.json` file that the `skills` CLI writes for an install, naming where each installed skill came from.

**Marketplace**:
This repo's Claude Code plugin list, in `.claude-plugin/marketplace.json`, from which some skills install as plugins.

### Project modes and planning

**GitHub-only mode**:
The default way a project tracks work: its issue tracker holds every spec, ticket and QA ticket, and the maintainer works on it too.
A project is in this mode when it has no `docs/agents/roadmap.md`.

**Roadmap mode**:
The way a project plans in three layers: Notion holds its history and thinking, Linear holds the roadmap and its status, and GitHub issues hold only the agent specs and tickets.
A project is in this mode when `docs/agents/roadmap.md` exists, and every skill that tracks work reads that file first.
A project moves to it only when the maintainer asks, in one `/set-up-project` run.

**Roadmap issue**:
In roadmap mode, the issue on the roadmap that a change belongs to, which its GitHub spec, tickets and pull request link.
The project's `docs/agents/roadmap.md` maps it, and the other roadmap terms, to Linear.

**Release group**:
A set of changes that ship together as one version: they are tested on beta, then shipped to production.
In roadmap mode, the roadmap holds each group, and unfinished work moves to the next group.
Only a hotfix ships alone.

**Wave**:
A set of an effort's tickets that do not block each other, so agents build them in parallel.
A wave starts when every ticket of the earlier waves is done, so an effort runs as a series of waves.
`/to-tickets` derives the waves from the blocking edges, and `/orchestrate-effort` builds one wave at a time.
_Avoid_: frontier, for this meaning. `/wayfinder` and `/grilling` keep "frontier" for their own, different meaning.
