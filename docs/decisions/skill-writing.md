# Decisions: skill writing

How the skills in this repo are written, and why. The rules below came from reviewing #66 one skill at a time on 2026-09-30, starting with `close-effort` and spreading to every skill the maintainer authored; the forks keep their upstream wording. The decisions that belong to one skill family stay in that family's record, such as `effort-workflow.md`; this file holds what applies to every skill. Read it before writing or changing a skill, and add a dated entry for each new decision.

## 2026-09-30: the shape of a skill

- **`SKILL.md` says what to do; a reference says how.** The main file holds the maintainer's preferences, a short numbered flow, and the rules about what each step must achieve, even when a rule is a restriction. Commands, their pitfalls, detailed procedures and tool specifics go in a reference beside it. A first try split `close-effort` into five topic references, which felt like too many; what versus how is the test that brought four of them back.
- **Keep references few.** Create one only for real "how" detail, and fold a small one back into the flow. A short skill needs none.
- **A reference is only for what some runs need.** When every run must read a file, its content goes in `SKILL.md`, however much "how" it holds: a reference the agent must always open is a detour, and one it skips is lost. This supersedes what-versus-how as the test for moving something out. Handover's readiness checklist and close-effort's commands came back into their skills for this reason.
- **A step says what always happens; its special cases sit under it** as indented bullets, each opening with its condition in bold ("**When the spec says "QA: blocking":** …"). A reader sees the usual path at a glance and reads a case only when it applies.
- **The body says when to read a file; a closing section says what it is.** A skill with supporting files ends with `## References`, and one with scripts with `## Scripts`: one line per file on what it covers. The instruction to read it ("Read `user-qa.md` before the first one", in `/orchestrate-effort`'s QA step) sits in the step that needs it.
- **Name a reference by its topic,** as a noun phrase: `user-qa.md`, `close-effort-commands.md`, not `where-things-go.md` or `carrying-a-change.md`. Its `# Title` matches the name.
- **A skill's folder holds only what runs the skill.** Notes for whoever maintains it, such as how to add a lesson, go in its record in `docs/decisions/`, which is never installed. `MAINTAINING.md` files inside two skills were copied into every install until they moved.
- **The design skills are the exception.** `/system-design` and `/low-level-design` carry their delivery framework in `SKILL.md`, as the Hello Interview lesson lays it out, because the framework is the skill.

## 2026-09-30: the language

- **Instruct; don't describe.** "Write each rule in one place only", not "every rule has one home". A description leaves the agent to work out what to do.
- **Give the reason beside the rule.** "Leave the main checkout on its branch, since the maintainer may be working there." The reason lets the agent handle the case the rule didn't foresee.
- **Plain words, not metaphors or coined terms.** "Owns the shape", "stays warm", "the handing session" and "only a record now" each became what they meant.
- **Spell out vague criteria and orderings.** "Who needs it and how hard it must hold" became two plain questions; "pick the first layer that fits" became "the table runs from enforced to guidance; go down it".
- **Whole sentences, not parenthetical asides.** A sentence carrying several asides reads like patches on patches.
- **Name another skill by its slash command** (`/to-tickets`), and a CLI as code (`treehouse`, `herdr`). Bold looked the same for a skill and a key term. A starting prompt meant to be pasted is the exception: it names skills in words, so it works in every harness.
- **Plain words over defined variables.** "The default branch", not a `<default>` defined once and used below. Placeholders are for parameters and literal templates only.

## 2026-09-30: what a skill leaves out

- **DRY: one meaning in one place.** A rule repeated in two skills drifts. Each role's meaning and fallback live only in `/set-up-machine`'s roles table; a skill's Parameters section has one line per role ("`<session-host>`: where agent sessions run, e.g. `herdr`, Claude Code Desktop, Codex Desktop.").
- **Nothing the model already knows.** What `git fetch` does, how `gh` lists issues, that a worktree needs a branch.
- **Nothing the agent already has in view.** No pointer to a skill's own Parameters section or to the Defaults table: when the table is in context the pointer adds nothing, and when it isn't the pointer points at nothing.
- **No hidden dependency on another skill's insides.** `close-effort` named `to-pr`'s *Things to be aware of* section, so renaming the section would have broken it; it now reads the pull request's description. A skill names another skill's file only when it must, and then fully.
- **Each file reads on its own.** No bare "(step 8)" in a reference that only makes sense beside another file.
- **No trigger keyword.** "When the maintainer says go" became "when the maintainer approves the pull request".
- **No over-enforcement.** A "Done when" line that restates its step, an ordering rule the flow's order already implies, and a restriction the model follows anyway all went.

## 2026-09-30: what a skill keeps

- **Lessons from real sessions**, each in a line with its reason: a squash merge fails the reachability proof, removing a worktree deletes its untracked files, freeing your own worktree ends your session, a multi-line prompt arrives as pasted text.
- **The maintainer's preferences**, stated as outcomes: after approval the agent does everything and hands over nothing to paste; the main checkout stays on its branch; workspaces stay open.
- **Parameters,** so a teammate with other tools can use the skill.

## 2026-09-30: how the rewrite was run

- **Discuss, record, then change.** Each piece of feedback was agreed in conversation, recorded on #83, and only then applied. An earlier session started rewriting before the maintainer asked and was stopped.
- **An example first, then the rule.** The maintainer approved one before/after sentence with the reasons it was better, and sub-agents applied that to every skill. The example did more than a list of rules would have.
- **One fresh sub-agent per skill, audited against `writing-for-agents` and the prompt-audit guide.** An author auditing their own text reads what they meant, not what is on disk; the first pass did exactly that and missed a stale reason and a dropped leading word. Each sub-agent edited only its own folder and committed nothing, so the coordinator could review, run a consistency pass and commit each skill separately.
- **Check what sub-agents return.** They put back pointers the maintainer had removed, reordered a step so it read backwards, and wrote "Default: none;". A pass over the combined result caught each.
- **Ask before generalising a rule.** "Don't point at the user's instructions" was extended from the Defaults-table rule by analogy; the maintainer never held it, and it was dropped.
- **Prefer text to scripts when upkeep outweighs value.** The team-test audit script and its tests, 270 lines, were replaced by a grep described in `/maintain-environment`.
- **Run each commit and push as its own call, and remove files with `git rm`.** The coordinator slipped on both once: eight commits in one shell loop, and an `rm -f` on untracked files after copying their text.

## 2026-09-30: the second audit round

- **Fold before auditing.** Must-read references went into `SKILL.md` first, then a fresh sub-agent per skill ran the prompt audit and made its own fixes, with this file as the rules that win a conflict. Auditing after the fold meant the auditors read each skill as an agent would.
- **Audits catch facts, not only wording.** This round found a wrong signal in `/wispr-flow-dictionary` by reading its script, a quoting bug in `/handover-to-herdr`, a status clash in `/orchestrate-effort`, and a way around `/email`'s deny rules. Tell an auditor to check a skill's commands against their source.
