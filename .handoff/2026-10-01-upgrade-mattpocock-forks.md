# Handoff: upgrade the mattpocock/skills forks

## Where things are

- **Worktree:** `~/.treehouse/skills-22e236/1/skills`, leased from `treehouse` with lease holder `upgrade-mattpocock-forks`.
- **Branch:** `chore/upgrade-mattpocock-forks`, cut from `origin/main`.
- **The work:** [#105 Upgrade the mattpocock/skills forks to upstream's latest, including the GLOSSARY.md rename](https://github.com/yahyabedirhan/skills/issues/105). It holds what to do, the forks and their Origin commits, what's in and out of scope, and the acceptance criteria. It's a single ticket, not an effort with a spec, labelled `effort:skill-maintenance`.

## How we got here

A session in another project re-ran `set-up-project`'s audit and found two names in use. `set-up-project` writes `GLOSSARY.md`, while `domain-modeling` and the other installed upstream skills still read `CONTEXT.md`. Upstream renamed it on 2026-09-17, and the installed copies came from before that. The maintainer chose `GLOSSARY.md`, upstream's name. They also asked that the forks be upgraded the way you'd upgrade a dependency: upstream's newest version is the source of truth, and this repo's changes are re-applied on top.

## What to do next

1. Clone or update upstream in the maintainer's folder for open-source clones; a clone fetched on 2026-10-01 is already there. In anything committed, cite upstream by repository and commit, never by a local path.
2. Work through #105's *How to upgrade each fork* for `handoff`, `implement`, `to-spec`, `to-tickets` and `set-up-project`. Use one commit per fork, so the maintainer can follow each one.
3. Do #105's *Also in scope* items: update the installed non-forked upstream skills, make sure no skill names `CONTEXT.md` any more, have `set-up-project` propose renaming an old `CONTEXT.md`, and bring the README's install advice up to date.
4. Install the upgraded forks on this machine, and check the acceptance criteria.
5. Open the pull request with `to-pr`. Its body names #105 and lists every upstream change you took or left out, with the reason for each one left out. Then tell the maintainer it's ready. They merge it themselves, so don't merge.

## Decisions already made

- `GLOSSARY.md` / `GLOSSARY-MAP.md` is the name. Don't ask about this again.
- Upstream is the base. Where an upstream change conflicts with one of ours, keep ours and say so in the pull request, unless upstream now does the same thing better.
- The humanlayer forks (`to-pr`, `show-me`) are out of scope. If they're behind upstream, open a follow-up ticket.
- Other projects rename their own `CONTEXT.md` themselves. Shipyard is being renamed by the session that handed over.

## Open questions

You can't reach the session that handed over. Decide open questions yourself, and list each one in the pull request's *Things to be aware of*. Stop and ask the maintainer only for a decision that would change the scope of #105.

## Suggested skills

- `maintain-environment`: forking, updating and installing skills with `npx skills`, and the prompt audit of each changed skill
- `writing-for-agents`: editing each `SKILL.md`
- `to-pr`: the pull request
- `code-review`: reviewing the branch against #105 before opening the pull request
