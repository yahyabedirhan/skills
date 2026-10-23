# Forks

This page lists every skill here that started as a copy of someone else's skill, with the upstream commit it was copied from and everything the fork changes.
Read it before you upgrade a fork, and update it in the same pull request as a fork's change.
The README's [Origin column](GLOSSARY.md#forks) keeps the upstream link and the commit pin, and links each fork's entry here.
This page also holds each fork's license, and the license of each source the README credits without forking it.
Each license file stays in its skill's folder.

## handoff

Fork of `handoff` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`d81f3a1`](https://github.com/mattpocock/skills/tree/d81f3a183412/skills/productivity/handoff).
License: MIT, see [`skills/handoff/LICENSE.mattpocock`](skills/handoff/LICENSE.mattpocock).

Changes:

- Agents can load it.
- It saves to the repository's handoff folder, `.handoff/<date>-<topic>.md`, instead of a temp folder.

## implement

Fork of `implement` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`d81f3a1`](https://github.com/mattpocock/skills/tree/d81f3a183412/skills/engineering/implement).
License: MIT, see [`skills/implement/LICENSE.mattpocock`](skills/implement/LICENSE.mattpocock).

Changes:

- Agents can load it, so an orchestrator's sub-agents can use it.
- It commits only when the delegating agent doesn't.
- It reviews at the depth the delegating agent sets.
- It runs typechecking only where the project has a typechecker.
- With no one to agree tdd seams with, it chooses them and names them in its report.
- It stops what it started before reporting.
- It moves what it no longer needs into `.scratch/` instead of running `rm -rf`.

## to-spec

Fork of `to-spec` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`d81f3a1`](https://github.com/mattpocock/skills/tree/d81f3a183412/skills/engineering/to-spec).
License: MIT, see [`skills/to-spec/LICENSE.mattpocock`](skills/to-spec/LICENSE.mattpocock).

Changes:

- Agents can load it, so a thinking session runs it itself.
- With no tracker configured, it runs set-up-project instead of telling you to run `setup-matt-pocock-skills`.
- A local tracker keeps the spec in `.efforts/<effort>/` instead of `.scratch/`.

## to-tickets

Fork of `to-tickets` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`d81f3a1`](https://github.com/mattpocock/skills/tree/d81f3a183412/skills/engineering/to-tickets).
License: MIT, see [`skills/to-tickets/LICENSE.mattpocock`](skills/to-tickets/LICENSE.mattpocock).

Changes:

- Agents can load it, so a thinking session runs it itself.
- With no tracker configured, it runs set-up-project instead of telling you to run `setup-matt-pocock-skills`.
- A local tracker keeps the tickets in `.efforts/<effort>/issues/` instead of `.scratch/`.
- Tickets are named by title, never by a number alone.

## to-pr

Fork of `visual-pr` from [humanlayer/skills](https://github.com/humanlayer/skills) at [`4e39d8f`](https://github.com/humanlayer/skills/tree/4e39d8fe020f/plugins/visual-pr/skills/visual-pr).
License: MIT, see [`skills/to-pr/LICENSE.humanlayer`](skills/to-pr/LICENSE.humanlayer).

Changes:

- It is renamed and has a real trigger description.
- It has no Mermaid views.
- The description source is saved to `.scratch/`, as the folder standard says, instead of `.humanlayer/`.
- Issues are named by title, never by a number alone.
- The final report has review links for each changed file.
- A last section, 'Things to be aware of', holds decisions made alone, surprises, what's left out and follow-ups.
- It writes "Refs", not "Closes", for a ticket waiting for the maintainer's QA.

## show-me

Fork of `show-me` from [humanlayer/skills](https://github.com/humanlayer/skills) at [`ca7c808`](https://github.com/humanlayer/skills/tree/ca7c808/plugins/show-me/skills/show-me).
License: MIT, see [`skills/show-me/LICENSE.humanlayer`](skills/show-me/LICENSE.humanlayer).

Changes:

- It has no Mermaid views, so every view renders as plain text.
- Agents can still load it, where upstream made it user-invocable only in `bba9d13`, because `orchestrate-effort` uses it to show the plan.

## set-up-project

Fork of `setup-matt-pocock-skills` from [mattpocock/skills](https://github.com/mattpocock/skills) at [`d81f3a1`](https://github.com/mattpocock/skills/tree/d81f3a183412/skills/engineering/setup-matt-pocock-skills).
License: MIT, see [`skills/set-up-project/LICENSE.mattpocock`](skills/set-up-project/LICENSE.mattpocock).

Changes:

- Agents can load it.
- It checks the machine first.
- `AGENTS.md` is always the rules file, with `CLAUDE.md` as `@AGENTS.md`, instead of editing whichever exists.
- It offers optional project environment defaults.
- It adds the folder standard's `.gitignore` lines.
- A local tracker keeps issues in `.efforts/<effort>/` instead of `.scratch/`, and says how a ticket is picked up and marked done when the project has no spec or triage labels.
- The GitHub template adds effort labels and names issues by title.
- It proposes a `git mv` of an old `CONTEXT.md` or `CONTEXT-MAP.md` to its `GLOSSARY` name.
- For a project that releases, it writes a short release page, `docs/agents/releasing.md`, from its seed and any shared release rules. The page holds only what the project does, and leaves the rest to the shared rules.
- It audits each harness's project files against set-up-machine's rule table.

## Credited sources

These skills are not forks, but they credit someone else's work.

### email

The daily workflows adapt the read-only recipes in [readdle/spark-cli-skills](https://github.com/readdle/spark-cli-skills) at [`507d26e`](https://github.com/readdle/spark-cli-skills/tree/507d26e/skills).
No text is copied.
License: MIT.
