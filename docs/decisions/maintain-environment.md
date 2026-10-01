# Decisions: maintain-environment

The decisions behind the `maintain-environment` skill, named `maintain-skills` until 2026-09-29. This file is for maintaining it and is never installed. Add an entry for each new decision: the date, what was decided, and why.

## 2026-09-28

- **Every new skill gets a prompt audit from a fresh sub-agent.** The author's context is anchored on what it meant to write; a sub-agent reads only what is on disk. It runs the bundled `claude-api` skill's `prompt-audit` subcommand, the same audit `/doctor prompt-audit <path>` hands off to, so the check follows Anthropic's current prompting guidance rather than a rubric kept here. The auditor reports and does not edit; the author applies the accepted fixes.
- **Efficiency analysis is a disclosed reference, run only on request.** The user asks for it when introducing a new skill whose cost matters; running it by default would spend a session's tokens measuring tokens. `scripts/session-usage.py` makes the numbers repeatable from the transcript instead of estimated.
- **Cost is judged per task, not per token.** A stronger model that finishes in fewer calls is usually cheaper overall, so the analysis does not recommend down-tiering the model by default. The measured lever in the first analysis (a company briefing video) was context re-reads: calls × context size, cut by running heavy phases in a fresh sub-agent.
- **Changes to the skills repo ship as pull requests, not pushes to `main`.** A push to `main` publishes before anyone reviews it; a new skill and its prompt-audit fixes once landed that way in one unreviewed commit. Each repo-changing operation now ends with a branch, a commit and a pull request opened through `to-pr`, and one section, *Shipping to the skills repo*, holds the steps so the three operations point at it rather than repeat them.
- **Branch names are `<skill>/<topic>`, or `skills/<topic>` when a change spans skills.** The prefix names what the branch changes, so a list of open branches reads by skill.
- **The merge is the user's, or the agent's when the user asks.** Opening the pull request is part of the operation; the agent merges only on request.
- **Installs and updates run after the merge, with no trial install from a branch.** `npx skills` installs from the default branch, so the session told "merged" or "merge it" runs `npx skills update` (or the install) in every scope that holds the skill.
- **An audited skill's pull request summarises the audit; the skill's decision record keeps it in full.** The findings, the fixes applied, and why any finding was left go in the skill's `docs/decisions/` entry; the description summarises them under *Special things to note* and links that entry. `to-pr` limits the body to its template, with 1-3 bullets for *Special things to note*, so the full findings can't live there, and the decision record keeps them with the skill's other decisions.

## 2026-09-29

- **`maintain-skills` becomes `maintain-environment`, and owns change across the whole environment.** Permissions, global instructions, project instructions and skills all need a home and a way to reach every harness and machine; skills were only one of them. The skill folder and this record were renamed so their history follows, and the entries above keep the old name as history.
- **`SKILL.md` is a short router over three references.** "Where things go" (the layering model and the team test), "carrying a change" (how a change reaches every harness, machine and install, and naming what to rerun), and "skill operations". A change loads only the reference it needs, so a rule change never loads the `npx skills` detail and a skill install never loads the layering model.
- **Skill operations carry the old `SKILL.md` body unchanged.** Only the frontmatter and title gave way to the router; the operations, scopes, shipping steps and audits read as before, and `efficiency-analysis.md` and its script stay beside them.
- **Setting up belongs to set-up-machine and set-up-project; this skill names them.** The rule table, harness adapters and project templates live in those skills; "carrying a change" says which to rerun and where, rather than repeating how.

## 2026-09-29: parameters, and the default-tools audit

- **A skill names an environment value as a parameter.** The maintainer settled the convention: a skill that needs a value from the environment has one `## Parameters` section in its `SKILL.md` (never in a reference, and only where needed), each parameter a `<kebab-case>` placeholder named after its Defaults role with a one-line meaning and its fallback, and the body and references use only the placeholder. Values come from "the Defaults table in the environment's instructions", never "global instructions": a project's `AGENTS.md` may hold its own table that overrides the global one for that project, and the agent has both in context. The section's lead sentence says so once. `skill-operations.md`'s Parameters section moved into `SKILL.md` accordingly. The convention lives beside the team test in `where-things-go.md`.
- **A script lists the skill lines that name a default tool; it never blocks.** `scripts/default_tools.py` reads the tool roles (`session-host`, `worktree-tool`, `notification-method`) from the Defaults table, or takes `--tool`, and greps the Markdown and YAML an agent loads, skipping each tool's own how-to skill (a folder whose name contains the tool's name). Naming a default tool is tolerated by the team test, so it exits 0; the agent judges each hit a default to rewrite or a mention to keep. It lives with the team test in `where-things-go.md`, since that is the rule it checks.
- **Agent to start and skills repo aren't scanned.** Harness names appear in skills for good reasons (the harness adapters, Codex's `$skill` syntax), so scanning the agent to start would report noise.
- **The audit also flags "Defaults table" and "global instructions" outside `## Parameters`.** Those phrases in a skill's body mean it reads the table inline instead of through a placeholder. **set-up-machine** and **maintain-environment** are exempt, since the global file and the layers are what they describe.

## 2026-09-30: simpler parameters (#83)

- **A `## Parameters` line is one line:** the placeholder, what it is, and what happens when it's unset. No mechanism.
- **The how-to skill naming convention is gone** (`handover-to-<session-host>`, a worktree tool's skill "named for the tool"). A skill routes to a tool's skill by name, and the default-tools audit treats a line that names the tool's skill as routing, not a default.
- **A placeholder a skill doesn't declare is replaced with plain words.**

## 2026-09-30 (later)

- **A Parameters line says what the role is, with examples, and nothing else.** This supersedes the #83 entry above on two points: what to do when a role has no tool lives only in `/set-up-machine`'s roles table, and no skill routes to a tool's skill, since the tool's own skill says in its description when to use it. The environment layers, the team test and the parameter convention now sit in `SKILL.md`, because every change reads them, and the team-test audit is a grep.
- **A new skill's auditor reports by default, and fixes only when the user says so.** The #66 review had auditors make their own fixes because the maintainer asked for it; without that request, the author reviews the findings and applies the ones it accepts.

## 2026-10-01: upgrading a fork (#105)

- **A fork is upgraded like a dependency, from upstream's latest version, with the fork's own changes re-applied on top.** Before #105 the skill only knew how to fork, so the upgrade steps lived only in that issue. They now sit in *Upgrade a fork* in `skill-operations.md`.
- **An upgrade keeps the fork's choice of who can invoke it.** The maintainer forked several upstream skills mainly to drop `disable-model-invocation`, so agents could load them. Upstream can set it again later: humanlayer/skills did in `bba9d13` for `show-me`, which would break `orchestrate-effort`. The step names both places the setting lives, `SKILL.md` and `agents/openai.yaml`.
