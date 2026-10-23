# Decisions: maintain-environment

The decisions behind the `maintain-environment` skill, named `maintain-skills` until 2026-09-29. This file is for maintaining it and is never installed. Entries follow the shape in [index.md](index.md).

## 2026-09-28: every new skill gets a prompt audit from a fresh sub-agent

- **Status:** accepted
- **Context:** The author's context is anchored on what it meant to write. A sub-agent reads only what is on disk.
- **Options:** The author audits its own skill: it reads what it meant, not what is there.
- **Choice and why:** A fresh sub-agent runs the bundled `claude-api` skill's `prompt-audit` subcommand, the same audit that `/doctor prompt-audit <path>` hands off to. The check then follows Anthropic's current prompting guidance rather than a rubric kept here. The auditor reports and does not edit. The author applies the accepted fixes.
- **Consequences:** The audit later covered every skill change; see [2026-10-09: every skill change gets a fresh sub-agent audit](#2026-10-09-every-skill-change-gets-a-fresh-sub-agent-audit).

## 2026-09-28: efficiency analysis is a disclosed reference, run only on request

- **Status:** accepted
- **Context:** The user asks for an efficiency analysis when a new skill's cost matters.
- **Options:** Run it by default: it would spend a session's tokens measuring tokens.
- **Choice and why:** Run it only on request. `scripts/session-usage.py` makes the numbers repeatable from the transcript instead of estimated.
- **Consequences:** None.

## 2026-09-28: cost is judged per task, not per token

- **Status:** accepted
- **Context:** A stronger model that finishes in fewer calls is usually cheaper overall.
- **Options:** Recommend a smaller model by default.
- **Choice and why:** Judge cost per task. The measured lever in the first analysis, a company briefing video, was context re-reads: calls times context size. Running heavy phases in a fresh sub-agent cut it.
- **Consequences:** The analysis does not recommend a smaller model by default.

## 2026-09-28: changes to the skills repo ship as pull requests

- **Status:** accepted
- **Context:** A push to `main` publishes before anyone reviews it. A new skill and its prompt-audit fixes once landed that way, in one unreviewed commit.
- **Options:** Push to `main`.
- **Choice and why:** Each repo-changing operation ends with a branch, a commit and a pull request opened through `to-pr`. One section, *Shipping to the skills repo*, holds the steps, and the three operations point at it.
- **Consequences:** None.

## 2026-09-28: branch names are skill/topic

- **Status:** accepted
- **Context:** A list of open branches should read by skill.
- **Options:** None considered.
- **Choice and why:** Name a branch `<skill>/<topic>`, or `skills/<topic>` when a change spans skills. The prefix names what the branch changes.
- **Consequences:** None.

## 2026-09-28: the merge is the user's, or the agent's when the user asks

- **Status:** accepted
- **Context:** Opening the pull request is part of the operation.
- **Options:** None considered.
- **Choice and why:** The agent merges only on request.
- **Consequences:** None.

## 2026-09-28: installs and updates run after the merge

- **Status:** accepted
- **Context:** `npx skills` installs from the default branch.
- **Options:** A trial install from a branch.
- **Choice and why:** No trial install. The session told "merged" or "merge it" runs `npx skills update`, or the install, in every scope that holds the skill.
- **Consequences:** None.

## 2026-09-28: an audited skill's pull request summarises the audit

- **Status:** accepted
- **Context:** `to-pr` limits the body to its template, with 1-3 bullets for *Special things to note*, so the full findings can't live there.
- **Options:** The full findings in the pull request: they don't fit the template.
- **Choice and why:** The findings, the fixes applied, and why any finding was left go in the skill's `docs/decisions/` entry. The description summarises them under *Special things to note* and links that entry.
- **Consequences:** The decision record keeps the audit with the skill's other decisions.

## 2026-09-29: maintain-skills becomes maintain-environment

- **Status:** accepted
- **Context:** Permissions, global instructions, project instructions and skills all need a home and a way to reach every harness and machine. Skills were only one of them.
- **Options:** None considered.
- **Choice and why:** The skill owns change across the whole environment. The skill folder and this record were renamed, so their history follows.
- **Consequences:** Older entries keep the old name as history.

## 2026-09-29: SKILL.md is a short router over three references

- **Status:** replaced by [2026-09-30: the layers, the team test and the parameter convention sit in SKILL.md](#2026-09-30-the-layers-the-team-test-and-the-parameter-convention-sit-in-skillmd)
- **Context:** The skill now covers three kinds of work.
- **Options:** None considered.
- **Choice and why:** `SKILL.md` routes to three references: "where things go" (the layering model and the team test), "carrying a change" (how a change reaches every harness, machine and install, and naming what to rerun), and "skill operations". A change loads only the reference it needs.
- **Consequences:** A rule change never loads the `npx skills` detail, and a skill install never loads the layering model.

## 2026-09-29: skill operations carry the old SKILL.md body unchanged

- **Status:** accepted
- **Context:** The rename replaced the old `SKILL.md`.
- **Options:** None considered.
- **Choice and why:** Only the frontmatter and title gave way to the router. The operations, scopes, shipping steps and audits read as before.
- **Consequences:** `efficiency-analysis.md` and its script stay beside them.

## 2026-09-29: setting up belongs to set-up-machine and set-up-project

- **Status:** accepted
- **Context:** The rule table, harness adapters and project templates live in those skills.
- **Options:** Repeat how to set up here: it would drift.
- **Choice and why:** This skill names them. "Carrying a change" says which to rerun and where.
- **Consequences:** None.

## 2026-09-29: a skill names an environment value as a parameter

- **Status:** replaced by [2026-09-30: a Parameters line is one line](#2026-09-30-a-parameters-line-is-one-line)
- **Context:** Skills need values from the environment, such as the session host. The maintainer settled the convention.
- **Options:** None considered.
- **Choice and why:** A skill that needs such a value has one `## Parameters` section in its `SKILL.md`, never in a reference, and only where needed. Each parameter is a `<kebab-case>` placeholder named after its Defaults role, with a one-line meaning and its fallback. The body and references use only the placeholder. Values come from "the Defaults table in the environment's instructions", never "global instructions": a project's `AGENTS.md` may hold its own table that overrides the global one, and the agent has both in context. The section's lead sentence says so once.
- **Consequences:** `skill-operations.md`'s Parameters section moved into `SKILL.md`. The convention lives beside the team test in `where-things-go.md`.

## 2026-09-29: a script lists the skill lines that name a default tool

- **Status:** replaced by [2026-09-30: the team-test audit is a grep](#2026-09-30-the-team-test-audit-is-a-grep)
- **Context:** The team test tolerates naming a default tool, but each case needs a look.
- **Options:** None considered.
- **Choice and why:** `scripts/default_tools.py` reads the tool roles (`session-host`, `worktree-tool`, `notification-method`) from the Defaults table, or takes `--tool`. It greps the Markdown and YAML an agent loads, and skips each tool's own how-to skill (a folder whose name contains the tool's name). It exits 0 and never blocks. The agent judges each hit a default to rewrite or a mention to keep.
- **Consequences:** It lives with the team test in `where-things-go.md`, since that is the rule it checks.

## 2026-09-29: the agent to start and the skills repo aren't scanned

- **Status:** replaced by [2026-09-30: the team-test audit is a grep](#2026-09-30-the-team-test-audit-is-a-grep)
- **Context:** Harness names appear in skills for good reasons, such as the harness adapters and Codex's `$skill` syntax.
- **Options:** Scan the agent to start: it would report noise.
- **Choice and why:** The default-tools script skips those roles.
- **Consequences:** None.

## 2026-09-29: the audit flags "Defaults table" and "global instructions" outside Parameters

- **Status:** replaced by [2026-09-30: the team-test audit is a grep](#2026-09-30-the-team-test-audit-is-a-grep)
- **Context:** Those phrases in a skill's body mean it reads the table inline instead of through a placeholder.
- **Options:** None considered.
- **Choice and why:** The audit flags them.
- **Consequences:** **set-up-machine** and **maintain-environment** are exempt, since the global file and the layers are what they describe.

## 2026-09-30: a Parameters line is one line

- **Status:** replaced by [2026-09-30: a Parameters line says what the role is, with examples](#2026-09-30-a-parameters-line-says-what-the-role-is-with-examples)
- **Context:** This replaces [2026-09-29: a skill names an environment value as a parameter](#2026-09-29-a-skill-names-an-environment-value-as-a-parameter) (#83).
- **Options:** None considered.
- **Choice and why:** A `## Parameters` line holds the placeholder, what it is, and what happens when it's unset. It describes no mechanism.
- **Consequences:** None.

## 2026-09-30: the how-to skill naming convention is gone

- **Status:** replaced by [2026-09-30: a Parameters line says what the role is, with examples](#2026-09-30-a-parameters-line-says-what-the-role-is-with-examples)
- **Context:** Skills built a tool's skill name from a convention, such as `handover-to-<session-host>` or a worktree tool's skill "named for the tool" (#83).
- **Options:** None considered.
- **Choice and why:** A skill routes to a tool's skill by name. The default-tools audit treats a line that names the tool's skill as routing, not a default.
- **Consequences:** None.

## 2026-09-30: an undeclared placeholder becomes plain words

- **Status:** accepted
- **Context:** Some skills used placeholders they didn't declare (#83).
- **Options:** None considered.
- **Choice and why:** Replace each undeclared placeholder with plain words.
- **Consequences:** None.

## 2026-09-30: a Parameters line says what the role is, with examples

- **Status:** accepted
- **Context:** This replaces two points of the #83 entries: [a Parameters line is one line](#2026-09-30-a-parameters-line-is-one-line) and [the how-to skill naming convention is gone](#2026-09-30-the-how-to-skill-naming-convention-is-gone).
- **Options:** None considered.
- **Choice and why:** A Parameters line says what the role is, with examples, and nothing else. What to do when a role has no tool lives only in `/set-up-machine`'s roles table. No skill routes to a tool's skill, since the tool's own skill says in its description when to use it.
- **Consequences:** None.

## 2026-09-30: the layers, the team test and the parameter convention sit in SKILL.md

- **Status:** accepted
- **Context:** This replaces [2026-09-29: SKILL.md is a short router over three references](#2026-09-29-skillmd-is-a-short-router-over-three-references). Every change reads the environment layers, the team test and the parameter convention.
- **Options:** None considered.
- **Choice and why:** Put them in `SKILL.md`.
- **Consequences:** None.

## 2026-09-30: the team-test audit is a grep

- **Status:** accepted
- **Context:** This replaces the default-tools script and its scan rules from 2026-09-29.
- **Options:** None considered.
- **Choice and why:** The team-test audit is a grep, described in the skill.
- **Consequences:** `effort-workflow.md` records the script's removal.

## 2026-09-30: a new skill's auditor reports by default

- **Status:** accepted
- **Context:** The #66 review had auditors make their own fixes, because the maintainer asked for it.
- **Options:** Auditors fix by default.
- **Choice and why:** Without that request, the auditor reports, and the author reviews the findings and applies the ones it accepts. The auditor fixes only when the user says so.
- **Consequences:** None.

## 2026-10-01: a fork is upgraded like a dependency

- **Status:** accepted
- **Context:** Before #105, the skill knew only how to fork. The upgrade steps lived only in that issue.
- **Options:** None considered.
- **Choice and why:** Upgrade a fork from upstream's latest version, with the fork's own changes re-applied on top.
- **Consequences:** The steps now sit in *Upgrade a fork* in `skill-operations.md`.

## 2026-10-01: an upgrade keeps the fork's choice of who can invoke it

- **Status:** accepted
- **Context:** The maintainer forked several upstream skills mainly to drop `disable-model-invocation`, so agents could load them. Upstream can set it again later: humanlayer/skills did in `bba9d13` for `show-me`, which would break `orchestrate-effort` (#105).
- **Options:** None considered.
- **Choice and why:** The upgrade step keeps the fork's setting, and names both places it lives: `SKILL.md` and `agents/openai.yaml`.
- **Consequences:** None.

## 2026-10-01: personal changes go to the personal repository

- **Status:** accepted
- **Context:** Spec #111 made the personal repository the source and the machine's files the output. An edit to the shared file's generated parts or to a harness's settings would be lost on the next run (#115).
- **Options:** Edit the machine's files directly: the next run overwrites them.
- **Choice and why:** A personal preference, an environment default or a personal permission is made in the user's personal repository, then `/set-up-machine` runs again. The skill points at `/set-up-machine`'s `references/personal-repository.md` for which file each kind goes in, so the layout has one source.
- **Consequences:** Which file each change goes in later moved to this skill's `references/workstation.md`; see [2026-10-09: this skill owns the workstation repo](#2026-10-09-this-skill-owns-the-workstation-repo).

## 2026-10-01: the team test chooses between the skills repo and the personal repository

- **Status:** accepted
- **Context:** A change can go public or stay personal (#115).
- **Options:** None considered.
- **Choice and why:** What anybody could use goes in a skill or the rule table. What holds only for this user goes in their repository.
- **Consequences:** None.

## 2026-10-01: a missing pointer is set up through /set-up-machine first

- **Status:** replaced by [2026-10-09: a missing pointer no longer sends every change through /set-up-machine](#2026-10-09-a-missing-pointer-no-longer-sends-every-change-through-set-up-machine)
- **Context:** `/set-up-machine` owns the pointer and asks the user once (#115).
- **Options:** This skill writes the pointer itself.
- **Choice and why:** This skill never writes the pointer. A missing pointer is set up through `/set-up-machine` first.
- **Consequences:** None.

## 2026-10-01: with no personal repository, a personal instruction goes in the shared file

- **Status:** accepted
- **Context:** A pointer may record no personal repository (#115).
- **Options:** Write a personal permission into a harness's settings: every audit would flag it.
- **Choice and why:** A personal instruction goes in the shared file, which is its source on such a machine, as `/set-up-machine` allows. A personal permission has no home without the repository, so the skill offers to set one up.
- **Consequences:** None.

## 2026-10-01: the user commits and pushes in their personal repository

- **Status:** accepted
- **Context:** The personal repository is private and the user's (#115).
- **Options:** None considered.
- **Choice and why:** The user commits and pushes.
- **Consequences:** Other machines get the change only after the push, a pull into their clone and a rerun of `/set-up-machine`.

## 2026-10-09: a change to the workflow or environment is checked against the user's principles

- **Status:** accepted
- **Context:** The user keeps principles for how they work with agents.
- **Options:** A fixed path to the principles: the public skill would know the workstation repo's layout.
- **Choice and why:** The skill finds the principles through the workstation repo's own `AGENTS.md`. The public skill knows the workstation repo only by its role and its `agents/` contract.
- **Consequences:** Routine changes, such as installing a skill, need only the team test.

## 2026-10-09: a change to the global instructions is shown as the whole file and waits for approval

- **Status:** accepted
- **Context:** Global instructions shape every agent, so the user wants to know every line of them.
- **Options:**
  - A diff alone: it hides how a new line reads beside the rest.
  - Wait "after they have read it": an agent can see an approval but not a read.
- **Choice and why:** Show the whole resulting file, with each changed line marked, and wait for the user's approval.
- **Consequences:** For a personal change, the user commits, not the agent.

## 2026-10-09: the global instruction layer names the working agreement and the glossary

- **Status:** accepted
- **Context:** `/set-up-machine` gave the shared file a new shape (see its decision record, 2026-10-09).
- **Options:** None considered.
- **Choice and why:** The layer's description follows the new shape.
- **Consequences:** None.

## 2026-10-09: the workstation repo is a parameter

- **Status:** accepted
- **Context:** The skill found the workstation repo only through `/set-up-machine`'s pointer, `~/.config/agents/source.md`, and declared no parameter for it. Someone who installs the public skills cannot see the user's repository.
- **Options:** Keep finding it only through the pointer.
- **Choice and why:** `<workstation-repo>` and `<path-to-workstation-repo>` are parameters, next to `<skills-repo>`. The skills name it as a parameter, say what it holds, work without one, and say how to start one.
- **Consequences:** None.

## 2026-10-09: this skill owns the workstation repo

- **Status:** accepted
- **Context:** Both this skill and `/set-up-machine` describe the workstation repo.
- **Options:** None considered.
- **Choice and why:** This skill owns it, and `/set-up-machine` reads it. The new `references/workstation.md` says what the repository is for, its starting layout, how to start one, and which file each personal change goes in. `/set-up-machine`'s reference keeps the pointer and the exact `agents/` format.
- **Consequences:** Each reference links to the other instead of repeating it.

## 2026-10-09: the starting layout is small

- **Status:** accepted
- **Context:** A new workstation repo needs a starting layout.
- **Options:** None considered.
- **Choice and why:** It has a `README.md`, an `AGENTS.md` that names what a maintainer reads first, and the `agents/` files. A principles file, decision records and a full glossary are optional.
- **Consequences:** Decision records may hold undecided entries.

## 2026-10-09: a new workstation repo leaves agents/instructions.md to /set-up-machine

- **Status:** accepted
- **Context:** `/set-up-machine` already creates the file from the shared file's personal parts when it is missing.
- **Options:** None considered.
- **Choice and why:** This skill doesn't create the file. One place then describes that copy.
- **Consequences:** The user approves the copy in the same diff that writes the pointer.

## 2026-10-09: a missing pointer no longer sends every change through /set-up-machine

- **Status:** accepted
- **Context:** This replaces [2026-10-01: a missing pointer is set up through /set-up-machine first](#2026-10-01-a-missing-pointer-is-set-up-through-set-up-machine-first).
- **Options:** None considered.
- **Choice and why:** Without a workstation repo, the skill offers to start one. With one but no pointer on this machine, `/set-up-machine` writes the pointer.
- **Consequences:** None.

## 2026-10-09: every instruction and skill change is written with /writing-for-agents

- **Status:** accepted
- **Context:** Global instructions and skills are read by agents on every run, so the same levers apply to each.
- **Options:** Only a new project skill.
- **Choice and why:** Write every instruction and skill change with `/writing-for-agents`.
- **Consequences:** None.

## 2026-10-09: every skill change gets a fresh sub-agent audit

- **Status:** accepted
- **Context:** This extends [2026-09-28: every new skill gets a prompt audit from a fresh sub-agent](#2026-09-28-every-new-skill-gets-a-prompt-audit-from-a-fresh-sub-agent) beyond a new or forked skill.
- **Options:** Only a new or forked skill.
- **Choice and why:** Audit every skill change. The author reads what it meant to write; the auditor reads what is on disk. The audit uses claude-api's `prompt-audit` where the harness has it, and `/writing-for-agents` where it doesn't.
- **Consequences:** None.

## 2026-10-11: a document that only some runs need lives in references/

- **Status:** accepted
- **Context:** Two places for reference files let an agent add a harness in the wrong place (#201).
- **Options:** None considered.
- **Choice and why:** The skill body keeps the steps every run needs. Skill operations and efficiency analysis moved to `references/`, with their words unchanged.
- **Consequences:** None.

## 2026-10-11: a new harness is one harness setup in /set-up-machine

- **Status:** accepted
- **Context:** An agent could add a harness in a second registration list (#201).
- **Options:** None considered.
- **Choice and why:** `references/harness-setup.md` states that a new harness is one harness setup, and the agent adds no second registration list. The file points at `/set-up-machine`'s `scripts/setupmachine/harness_setups/__init__.py`, which owns the harness setup contract. This file names no file layout.
- **Consequences:** The name is "harness setup", because a Pi package is already an installable package.

## 2026-10-11: references/harness-setup.md defines the words in its own rule

- **Status:** accepted
- **Context:** The bare rule named a registration list, and did not say what that list is (#201).
- **Options:** None considered.
- **Choice and why:** The reference says who would write a second list, and why one harness setup is enough.
- **Consequences:** None.

## 2026-10-12: route each change to a source and its guide

- **Status:** accepted
- **Context:** The skill repeated the workstation layout, the setup file formats and the delivery rules, so every change to the workstation repo or to set-up-machine needed an edit here too.
- **Options:** Keep the full layer table and workstation reference: it drifts each time either source changes.
- **Choice and why:** One table names each change's source and that source's guide: the workstation repo's `DESIGN.md`, a skill's design in `docs/design/`, or a project's `AGENTS.md`. The skill repeats nothing a guide says.
- **Consequences:** A change to the workstation layout or to set-up-machine needs no edit here.

### References
- [Spec: Give each environment skill one job and a readable verifier (#213)](https://github.com/yahyabedirhan/skills/issues/213): the redesign these entries come from.

## 2026-10-12: delete the harness-setup reference

- **Status:** accepted
- **Context:** `references/harness-setup.md` told an agent how to add a harness to set-up-machine, with the rule "add no second registration list". The maintainer could not tell why this skill held that rule.
- **Options:** Rewrite it in plainer words: it would still repeat set-up-machine's own design.
- **Choice and why:** Delete it. Adding a harness belongs to set-up-machine's design in `docs/design/set-up-machine.md`.
- **Consequences:** None open.

### References
- [Spec: Give each environment skill one job and a readable verifier (#213)](https://github.com/yahyabedirhan/skills/issues/213): the redesign these entries come from.

## 2026-10-12: the workstation reference covers only starting a repo

- **Status:** accepted
- **Context:** `references/workstation.md` listed which file each personal change goes in, which the workstation repo's own `DESIGN.md` also says.
- **Options:** None considered.
- **Choice and why:** Keep what the repo is for, a minimal starting layout and how to start one. After that, the repo's `DESIGN.md` is the guide, and set-up-machine's `references/workstation.md` defines the `setup/` formats.
- **Consequences:** None open.

### References
- [Spec: Give each environment skill one job and a readable verifier (#213)](https://github.com/yahyabedirhan/skills/issues/213): the redesign these entries come from.

## 2026-10-23: each fork's full list of changes lives in FORKS.md

- **Status:** accepted
- **Context:** The README's skills table carried each fork's full list of changes in its Origin column, which made the rows hard to read. The fork steps in `references/skill-operations.md` read that column when a fork is upgraded.
- **Options:** Drop the lists from the README and rely on git history, or move them to one page in `docs/`.
- **Choice and why:** Move them to `FORKS.md`, one entry per fork with its upstream, commit, licence and licence file, and every change. The README row keeps only the upstream link and the commit pin, with one sentence on what changed that links the entry. The licences of sources the README credits without forking also live there, and the README's License section points to the page. An upgrade still has one written list to check against.
- **Consequences:** A fork change updates its entry in `FORKS.md` in the same pull request.
