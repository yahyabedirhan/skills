# Handoff: skill-maintenance

- **Effort:** `skill-maintenance`
- **Worktree:** `~/.treehouse/skills-22e236/1/skills` (Treehouse lease `skill-maintenance`)
- **Branch:** `skills/skill-maintenance`, from `main`
- **Tracker:** GitHub issues in `yahyabedirhan/skills`, label `effort:skill-maintenance`
- **Spec:** [#41](https://github.com/yahyabedirhan/skills/issues/41). Read it first: its *Decisions* section is settled.
- **Tickets**, in order (sub-issues of #41):
  1. [#36](https://github.com/yahyabedirhan/skills/issues/36) `maintain-skills` opens a pull request instead of pushing to `main`. Read its comments: they carry decisions that change the body.
  2. [#39](https://github.com/yahyabedirhan/skills/issues/39) `to-pr` reports links to each changed file's final version and its diff
  3. [#29](https://github.com/yahyabedirhan/skills/issues/29) `skill-recap`: recap how a session used its skills (a new skill, plus the repo's tracker setup for `to-tickets`)
  - #30 is closed as superseded; don't build it.
- **Thinking session:** a Claude Code desktop-app session in the main checkout on `main`. It is **not** a Herdr tab and can't receive messages. Don't try to reach it.

## What the builder should know

- **Deliver one pull request** for the whole effort, through **to-pr**, into `main`. Don't merge it. The maintainer merges it or asks an agent to.
- **Decide open questions yourself** and list each decision in the pull request's reviewer notes. Stop and ask in this tab only when you can't continue.
- **After the merge** (not your job unless the maintainer asks you there): `npx skills update` for the changed skills, `npx skills add` for `skill-recap`, and removing the override paragraph from the maintainer's global `~/.claude/CLAUDE.md`. Don't edit files outside this worktree during the build.
- **Keep the scope tight.** #39 is a few lines in `to-pr`'s final report: per changed file, a link to the file at the head commit and one to its diff, shown in chat after the pull request is opened or updated. No previews and no description changes.
- **`skill-recap` states a purpose, not a checklist.** See #29. It ends with findings and a verdict, and never files anything. It points the user at `/to-tickets`, which only the user can start, for filing into the skills repo.
- **This repo is public.** No personal information and no details of private repositories go into files, issues or the pull request. Examples in `skill-recap` stay generic.
- **New skill hygiene** (from `maintain-skills`): a README row, a dated entry in `docs/decisions/`, and the prompt audit by a fresh sub-agent. Put the audit's findings, and what was applied, in the pull request description.
- **`to-pr` saves its description under `.humanlayer/`.** Leave that folder untracked; #24 replaces it later. Say so in the final report.
- **Shell gotchas:** in zsh, `echo =====` fails ("===== not found"), so use `echo ---`. Run commit and push as their own commands, never chained with deletions.

## How the maintainer works

- Quality over speed: finish properly (stale references, README, decision records, pull request description) rather than stop at "works".
- Facts are the agent's job, decisions are the maintainer's. Look things up instead of asking.
- Refer to issues by name as well as number; the maintainer doesn't keep issue numbers in mind.
- Reports are short, with the smallest visual that makes the point (the **show-me** skill).
