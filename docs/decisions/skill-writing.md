# Decisions: skill writing

How the skills in this repo are written, and why. The rules below came from reviewing #66 one skill at a time on 2026-09-30, starting with `close-effort` and spreading to every skill the maintainer authored; the forks keep their upstream wording. The decisions that belong to one skill family stay in that family's record, such as `effort-workflow.md`; this file holds what applies to every skill. Read it before writing or changing a skill. Entries follow the shape in [index.md](index.md).

## 2026-09-30: SKILL.md says what to do, a reference says how

- **Status:** replaced by [2026-09-30: a reference is only for what some runs need](#2026-09-30-a-reference-is-only-for-what-some-runs-need)
- **Context:** A first try split `close-effort` into five topic references, which felt like too many.
- **Options:** Topic references: too many files.
- **Choice and why:** The main file holds the maintainer's preferences, a short numbered flow, and the rules about what each step must achieve, even when a rule is a restriction. Commands, their pitfalls, detailed procedures and tool specifics go in a reference beside it. What versus how brought four of the five references back.
- **Consequences:** None.

## 2026-09-30: keep references few

- **Status:** accepted
- **Context:** Small references add files to open without adding much.
- **Options:** None considered.
- **Choice and why:** Create a reference only for real "how" detail, and fold a small one back into the flow.
- **Consequences:** A short skill needs no reference.

## 2026-09-30: a reference is only for what some runs need

- **Status:** accepted
- **Context:** This replaces what versus how as the test for moving something out, from [2026-09-30: SKILL.md says what to do, a reference says how](#2026-09-30-skillmd-says-what-to-do-a-reference-says-how). A reference the agent must always open is a detour, and one it skips is lost.
- **Options:** None considered.
- **Choice and why:** When every run must read a file, its content goes in `SKILL.md`, however much "how" it holds.
- **Consequences:** Handover's readiness checklist and close-effort's commands came back into their skills.

## 2026-09-30: a step says what always happens, with its special cases under it

- **Status:** accepted
- **Context:** Special cases inside a step hide the usual path.
- **Options:** None considered.
- **Choice and why:** Put each special case under its step as an indented bullet that opens with its condition in bold ("**When the spec says "QA: blocking":** …").
- **Consequences:** A reader sees the usual path at a glance, and reads a case only when it applies.

## 2026-09-30: the body says when to read a file, a closing section says what it is

- **Status:** accepted
- **Context:** Skills pointed at their files from different places.
- **Options:** None considered.
- **Choice and why:** A skill with supporting files ends with `## References`, and one with scripts with `## Scripts`: one line per file on what it covers. The instruction to read a file sits in the step that needs it, such as "Read `user-qa.md` before the first one" in `/orchestrate-effort`'s QA step.
- **Consequences:** None.

## 2026-09-30: name a reference by its topic

- **Status:** accepted
- **Context:** Names like `where-things-go.md` and `carrying-a-change.md` read like headings in a narrative.
- **Options:** None considered.
- **Choice and why:** Name a reference by its topic, as a noun phrase: `user-qa.md`, `settle-commands.md`. Its `# Title` matches the name.
- **Consequences:** None.

## 2026-09-30: a skill's folder holds only what runs the skill

- **Status:** accepted
- **Context:** `MAINTAINING.md` files inside two skills were copied into every install.
- **Options:** None considered.
- **Choice and why:** Notes for whoever maintains a skill, such as how to add a lesson, go in its record in `docs/decisions/`, which is never installed.
- **Consequences:** None.

## 2026-09-30: the design skills keep their framework in SKILL.md

- **Status:** accepted
- **Context:** `/system-design` and `/low-level-design` follow a delivery framework, as the Hello Interview lesson lays it out.
- **Options:** None considered.
- **Choice and why:** They carry the framework in `SKILL.md`, because the framework is the skill.
- **Consequences:** They are the exception to the reference rules above.

## 2026-09-30: instruct, don't describe

- **Status:** accepted
- **Context:** A description leaves the agent to work out what to do.
- **Options:** None considered.
- **Choice and why:** Write instructions: "Write each rule in one place only", not "every rule has one home".
- **Consequences:** None.

## 2026-09-30: give the reason beside the rule

- **Status:** accepted
- **Context:** A rule can't foresee every case.
- **Options:** None considered.
- **Choice and why:** Give the reason beside the rule: "Leave the main checkout on its branch, since the maintainer may be working there." The reason lets the agent handle the case the rule didn't foresee.
- **Consequences:** None.

## 2026-09-30: plain words, not metaphors or coined terms

- **Status:** accepted
- **Context:** Phrases like "owns the shape", "stays warm", "the handing session" and "only a record now" needed decoding.
- **Options:** None considered.
- **Choice and why:** Write what each phrase means.
- **Consequences:** None.

## 2026-09-30: spell out vague criteria and orderings

- **Status:** accepted
- **Context:** "Who needs it and how hard it must hold" and "pick the first layer that fits" left the agent to guess.
- **Options:** None considered.
- **Choice and why:** Spell them out. The first became two plain questions. The second became "the table runs from enforced to guidance; go down it".
- **Consequences:** None.

## 2026-09-30: whole sentences, not parenthetical asides

- **Status:** accepted
- **Context:** A sentence that carries several asides reads like patches on patches.
- **Options:** None considered.
- **Choice and why:** Write whole sentences.
- **Consequences:** None.

## 2026-09-30: name another skill by its slash command

- **Status:** accepted
- **Context:** Bold looked the same for a skill and a key term.
- **Options:** Bold skill names.
- **Choice and why:** Name a skill by its slash command (`/to-tickets`), and a CLI as code (`treehouse`, `herdr`).
- **Consequences:** A starting prompt meant to be pasted is the exception: it names skills in words, so it works in every harness.

## 2026-09-30: plain words over defined variables

- **Status:** accepted
- **Context:** Each defined variable is one more thing to resolve.
- **Options:** None considered.
- **Choice and why:** Write "the default branch", not a `<default>` defined once and used below.
- **Consequences:** Placeholders are for parameters and literal templates only.

## 2026-09-30: one meaning in one place

- **Status:** accepted
- **Context:** A rule repeated in two skills drifts.
- **Options:** None considered.
- **Choice and why:** Keep each meaning in one place. Each role's meaning and fallback live only in `/set-up-machine`'s roles table. A skill's Parameters section has one line per role ("`<session-host>`: where agent sessions run, e.g. `herdr`, Claude Code Desktop, Codex Desktop.").
- **Consequences:** None.

## 2026-09-30: nothing the model already knows

- **Status:** accepted
- **Context:** Skills explained what `git fetch` does, how `gh` lists issues, and that a worktree needs a branch.
- **Options:** None considered.
- **Choice and why:** Leave out what the model already knows.
- **Consequences:** None.

## 2026-09-30: nothing the agent already has in view

- **Status:** accepted
- **Context:** Skills pointed at their own Parameters section or at the Defaults table.
- **Options:** None considered.
- **Choice and why:** Leave such pointers out. When the table is in context, the pointer adds nothing. When it isn't, the pointer points at nothing.
- **Consequences:** None.

## 2026-09-30: no hidden dependency on another skill's insides

- **Status:** accepted
- **Context:** `close-effort` named `to-pr`'s *Things to be aware of* section, so renaming the section would have broken it.
- **Options:** None considered.
- **Choice and why:** `close-effort` now reads the pull request's description. A skill names another skill's file only when it must, and then fully.
- **Consequences:** None.

## 2026-09-30: each file reads on its own

- **Status:** accepted
- **Context:** A bare "(step 8)" in a reference makes sense only beside another file.
- **Options:** None considered.
- **Choice and why:** Write each file so it reads on its own.
- **Consequences:** None.

## 2026-09-30: no trigger keyword

- **Status:** accepted
- **Context:** "When the maintainer says go" waited for a literal word.
- **Options:** None considered.
- **Choice and why:** Describe the event: "when the maintainer approves the pull request".
- **Consequences:** `effort-workflow.md` records a deliberate exception for the settle skills.

## 2026-09-30: no over-enforcement

- **Status:** accepted
- **Context:** Skills restated what they already said or what the model does anyway.
- **Options:** None considered.
- **Choice and why:** Remove a "Done when" line that restates its step, an ordering rule the flow's order already implies, and a restriction the model follows anyway.
- **Consequences:** None.

## 2026-09-30: a skill keeps the lessons from real sessions

- **Status:** accepted
- **Context:** Real sessions found failures that the model can't know about.
- **Options:** None considered.
- **Choice and why:** Keep each lesson in a line with its reason. Examples: a squash merge fails the reachability proof; removing a worktree deletes its untracked files; freeing your own worktree ends your session; a multi-line prompt arrives as pasted text.
- **Consequences:** None.

## 2026-09-30: a skill keeps the maintainer's preferences, stated as outcomes

- **Status:** accepted
- **Context:** The maintainer's preferences shape how a skill ends.
- **Options:** None considered.
- **Choice and why:** State them as outcomes: after approval the agent does everything and hands over nothing to paste; the main checkout stays on its branch; workspaces stay open.
- **Consequences:** None.

## 2026-09-30: a skill keeps its parameters

- **Status:** accepted
- **Context:** A teammate may use other tools.
- **Options:** None considered.
- **Choice and why:** Keep the parameters, so a teammate with other tools can use the skill.
- **Consequences:** None.

## 2026-09-30: discuss, record, then change

- **Status:** accepted
- **Context:** An earlier session started rewriting before the maintainer asked, and was stopped.
- **Options:** None considered.
- **Choice and why:** Each piece of feedback was agreed in conversation, recorded on #83, and only then applied.
- **Consequences:** None.

## 2026-09-30: an example first, then the rule

- **Status:** accepted
- **Context:** The rewrite had to apply the same style across every skill.
- **Options:** A list of rules alone.
- **Choice and why:** The maintainer approved one before/after sentence with the reasons it was better, and sub-agents applied that to every skill. The example did more than a list of rules would have.
- **Consequences:** None.

## 2026-09-30: one fresh sub-agent per skill

- **Status:** accepted
- **Context:** An author auditing their own text reads what they meant, not what is on disk. The first pass did exactly that, and missed a stale reason and a dropped leading word.
- **Options:** The author audits.
- **Choice and why:** One fresh sub-agent per skill audits against `writing-for-agents` and the prompt-audit guide. Each sub-agent edits only its own folder and commits nothing.
- **Consequences:** The coordinator can review, run a consistency pass and commit each skill separately.

## 2026-09-30: check what sub-agents return

- **Status:** accepted
- **Context:** Sub-agents put back pointers the maintainer had removed, reordered a step so it read backwards, and wrote "Default: none;".
- **Options:** None considered.
- **Choice and why:** Run a pass over the combined result. It caught each of these.
- **Consequences:** None.

## 2026-09-30: ask before generalising a rule

- **Status:** accepted
- **Context:** "Don't point at the user's instructions" was extended from the Defaults-table rule by analogy. The maintainer never held it.
- **Options:** None considered.
- **Choice and why:** Ask the maintainer before extending a rule. The extended rule was dropped.
- **Consequences:** None.

## 2026-09-30: prefer text to scripts when upkeep outweighs value

- **Status:** accepted
- **Context:** The team-test audit script and its tests were 270 lines.
- **Options:** Keep the script.
- **Choice and why:** Replace it with a grep described in `/maintain-environment`.
- **Consequences:** None.

## 2026-09-30: run each commit and push as its own call, and remove files with git rm

- **Status:** accepted
- **Context:** The coordinator once ran eight commits in one shell loop, and once ran `rm -f` on untracked files after copying their text.
- **Options:** None considered.
- **Choice and why:** Run each commit and each push as its own call, and remove files with `git rm`.
- **Consequences:** None.

## 2026-09-30: fold before auditing

- **Status:** accepted
- **Context:** The second audit round needed auditors to read each skill as an agent would.
- **Options:** Audit before the fold.
- **Choice and why:** Must-read references went into `SKILL.md` first. Then a fresh sub-agent per skill ran the prompt audit and made its own fixes, with this file as the rules that win a conflict.
- **Consequences:** None.

## 2026-09-30: audits check facts, not only wording

- **Status:** accepted
- **Context:** The second round found a wrong signal in `/wispr-flow-dictionary` by reading its script, a quoting bug in `/handover-to-herdr`, a status clash in `/orchestrate-effort`, and a way around `/email`'s deny rules.
- **Options:** None considered.
- **Choice and why:** Tell an auditor to check a skill's commands against their source.
- **Consequences:** None.

## 2026-10-01: keep permission handling concise in the global instructions

- **Status:** accepted
- **Context:** The global instructions are loaded in every session. Enforcement configuration and hook rejections already carry command inventories, reasons and alternatives.
- **Options:** None considered.
- **Choice and why:** The shared global instructions carry general rejection handling, a fallback learned from common failures, and a short secrets guardrail.
- **Consequences:** Add examples only when observed failures justify their context cost.

## 2026-10-01: group the personal workflow and shorten role fallbacks

- **Status:** accepted
- **Context:** The global instructions are loaded in every session.
- **Options:** None considered.
- **Choice and why:** Use topic headings and concise rules, without changing their meaning. A fallback states what to do when a role has no tool, and omits the explanation of the tool or risk.
- **Consequences:** None.
