# Handoff: environment

- **Effort:** `environment`
- **Worktree:** this one, `~/.treehouse/skills-22e236/3/skills` (Treehouse lease `environment`)
- **Branch:** `skills/environment`, from `main` at the merge of "The effort workflow runs end to end on one machine"
- **Tracker:** GitHub issues in `yahyabedirhan/skills`, label `effort:environment` (see `docs/agents/issue-tracker.md`)
- **Spec:** [Spec: every harness and project is set up and audited from the skills (#49)](https://github.com/yahyabedirhan/skills/issues/49). Read it first. Every decision in it was settled with the maintainer over six grilling rounds; don't reopen them.
- **Tickets:** #50 to #63, each with its blocked-by links set natively on GitHub (the issue page's *Relationships*) and repeated in its body. `gh issue list --label effort:environment`.
- **Thinking session:** a Claude Code tab in this repo's Herdr workspace, next to yours. It handed over and is done; don't message it. Decide open questions yourself, as the **orchestrating** skill says, and list them under *Things to be aware of* in the pull request.

## The ticket graph, for parallel delegation

```text
start now:  #50 Settle what each harness can and can't do
            #51 maintain-environment replaces maintain-skills
            #52 set-up-machine sets up and audits rm -rf on Claude Code
#52 → #53 The full rule table on Claude Code
#53 → #54 Basic hook script, wired into Claude Code
#50 + #53 → #58 Global instructions hold only your workflow, and memory is off
#50 + #54 → #55 Codex · #56 opencode · #57 Cursor          (three in parallel)
#58 → #59 Effort skills name roles, not your tools
#55 + #56 + #57 → #60 set-up-project sets up and audits a project
#55..#58 → #61 A fresh Linux machine passes set-up-machine
#59 + #60 → #62 The team test passes
#63 Set up and audit this repo with set-up-project   ← after the merge; leave it open
```

The rollout issues in the other repositories (shipyard, sand, scoop, workstation, and one private project) are **outside this effort's pull request**. Don't touch them. They run after the merge.

## What the builder should know

- **Live machine configs are the maintainer's.** Several tickets change real harness files on this machine: the global instructions, the permission files, the hooks and the memory settings. set-up-machine's design already shows a diff and applies it on one approval. Keep it that way in every test run: copy each file into `.scratch/` before the first apply, and treat the maintainer's approval of that diff as the input you need from them (**orchestrating**'s question shape). Never change them silently, and never remove or loosen an entry the skill didn't write.
- **Research draft:** a first pass at #50 lives on this machine in the main checkout's gitignored `.scratch/harness-research-draft.md`. The #50 delegate builds on it. The committed research doc keeps only facts about the harnesses, never observations of this machine: its paths, account or connector IDs, or which folders it trusts. See #50's comment.
- **Docker is installed** on this machine, for #61's throwaway Linux container.
- **The maintainer's global Claude instructions file** is rewritten in #58, following the spec's rule for what global instructions may hold. Until then, leave it alone. It still names `maintain-skills`, which #51 renames.
- **Retired skills are still installed:** `init-effort-with-herdr` and `orchestrate-with-herdr`, plus the old effort's worktree. The maintainer asked not to clean these up yet. Ignore them; closing the previous effort isn't part of this one.
- **No QA hand-off:** this repo's instructions don't opt in to QA by the maintainer.
- **This repo is public.** No personal information and no details of the private project go into files, issues or the pull request.
- **Never `rm -rf`.** Move what's no longer needed into `.scratch/` (the folder standard). Run each commit and each push as its own command.
- **Deliver one pull request** for the effort through **to-pr**, and say "Refs #63" for the rollout ticket, since it runs after the merge.

## How the maintainer works

- Harness compliance is non-negotiable; a skill that names a default tool is tolerated. When in doubt, research until certain, never guess what a harness can do.
- Facts are the agent's job, decisions are the maintainer's. Look things up instead of asking.
- Name issues and pull requests by their title, with the number after; the maintainer doesn't keep numbers in mind.
- Reports are short, with the smallest visual that makes the point (**show-me**).

## Suggested skills

- **orchestrate-with-handoff**, which runs **orchestrate-effort**, with **orchestrating** for the discipline.
- **implement** for every delegate.
- **research** for #50.
- **writing-for-agents** for every new or changed skill.
- **maintain-skills** for installs and the new-skill prompt audit, until #51 replaces it with maintain-environment.
- **to-pr** to deliver.
