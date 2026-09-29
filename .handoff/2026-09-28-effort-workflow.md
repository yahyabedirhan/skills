# Handoff: effort-workflow

- **Effort:** `effort-workflow`
- **Worktree:** `~/.treehouse/skills-22e236/2/skills` (Treehouse lease `effort-workflow`)
- **Branch:** `skills/effort-workflow`, from `origin/main`
- **Tracker:** GitHub issues in `yahyabedirhan/skills`, label `effort:effort-workflow`
- **Spec:** [#44](https://github.com/yahyabedirhan/skills/issues/44). Read it first and in full. Its *Decisions* section and its skills table are settled. **Where a ticket's body disagrees with the spec, the spec wins**, and after it the ticket's "Decisions from grilling" comment dated 2026-09-28.
- **Tickets:** the 19 sub-issues of #44, in the spec's table. Read every ticket's body and all of its comments: several were retitled or reshaped in the comments.
- **Thinking session:** a Claude Code desktop-app session in the main checkout on `main`. It is not a Herdr tab and can't receive messages. Don't try to reach it.

## What the builder should know

- **One pull request** for the whole effort, through **to-pr**, into `main`. Don't merge it. The maintainer reviews it and says "go".
- **Another pull request is open:** [#43](https://github.com/yahyabedirhan/skills/pull/43) (the `skill-maintenance` effort) changes `to-pr`, `maintain-skills`, the `README.md`, and adds `AGENTS.md`, `CLAUDE.md` and the `skill-recap` skill. This branch starts from `main` without it. Before opening the pull request, check whether #43 has merged. If it has, rebase onto `main` and resolve the conflicts, keeping both efforts' changes. If it hasn't, say so in the pull request, and name the files both touch.
- **Start with the renames and invocation** (#11, #10, #17): every other change edits the files they rename or retire. Then #24 before #14 and #21.
- **Forks** (`to-spec`, `to-tickets`, `handoff`) follow `maintain-skills`' *Fork someone else's skill* steps: the upstream licence beside the copy, the upstream commit in the README row, and only the intended change. The installed copies are in `~/.agents/skills/<name>/`, and `npx skills` records their source in `~/.agents/.skill-lock.json`.
- **New skills** (`handover`, `handover-to-herdr`, `close-effort`) and forks get a README row, a dated entry in `docs/decisions/effort-workflow.md`, and the prompt audit from `maintain-skills` (*Auditing a new skill*). Put the audit's findings and what was applied in the pull request.
- **Retired skills** (`init-effort-with-herdr`, `orchestrate-with-herdr`) are removed from the repo and README, and every reference to them is updated. The global uninstall happens after the merge, not now.
- **The public repo rule:** no personal information and no details of private repositories in files, issues or the pull request. Examples stay generic.
- **Don't edit anything outside this worktree.** The maintainer's global instructions were already updated in the thinking session: Herdr from anywhere with explicit IDs, and how notifications are sent.
- **Decide open questions yourself.** List the decisions in the pull request. Interrupt only for a critical blocker, in this tab.
- **Shell gotchas:** in zsh, `echo =====` fails, so use `echo ---`. Run commit and push as their own commands.

## After the merge (not yours unless the maintainer asks you here)

`npx skills update` for the changed skills; `npx skills add` for the new skills and forks; `npx skills remove -g` for `init-effort-with-herdr`, `orchestrate-with-herdr`, and the upstream `to-spec`, `to-tickets` and `handoff` once their forks are installed; then close the effort.
