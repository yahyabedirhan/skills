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
