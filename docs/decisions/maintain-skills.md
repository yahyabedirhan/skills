# Decisions: maintain-skills

The decisions behind the `maintain-skills` skill. This file is for maintaining it and is never installed. Add an entry for each new decision: the date, what was decided, and why.

## 2026-09-28

- **Every new skill gets a prompt audit from a fresh sub-agent.** The author's context is anchored on what it meant to write; a sub-agent reads only what is on disk. It runs the bundled `claude-api` skill's `prompt-audit` subcommand, the same audit `/doctor prompt-audit <path>` hands off to, so the check follows Anthropic's current prompting guidance rather than a rubric kept here. The auditor reports and does not edit; the author applies the accepted fixes.
- **Efficiency analysis is a disclosed reference, run only on request.** The user asks for it when introducing a new skill whose cost matters; running it by default would spend a session's tokens measuring tokens. `scripts/session-usage.py` makes the numbers repeatable from the transcript instead of estimated.
- **Cost is judged per task, not per token.** A stronger model that finishes in fewer calls is usually cheaper overall, so the analysis does not recommend down-tiering the model by default. The measured lever in the first analysis (a company briefing video) was context re-reads: calls × context size, cut by running heavy phases in a fresh sub-agent.
- **Changes to the skills repo ship as pull requests, not pushes to `main`.** A push to `main` publishes before anyone reviews it; a new skill and its prompt-audit fixes once landed that way in one unreviewed commit. Each repo-changing operation now ends with a branch, a commit and a pull request opened through `to-pr`, and one section, *Shipping to the skills repo*, holds the steps so the three operations point at it rather than repeat them.
- **Branch names are `<skill>/<topic>`, or `skills/<topic>` when a change spans skills.** The prefix names what the branch changes, so a list of open branches reads by skill.
- **The merge is the user's, or the agent's when the user asks.** Opening the pull request is part of the operation; the agent merges only on request.
- **Installs and updates run after the merge, with no trial install from a branch.** `npx skills` installs from the default branch, so the session told "merged" or "merge it" runs `npx skills update` (or the install) in every scope that holds the skill.
- **An audited skill's pull request description carries the audit.** The findings, the fixes applied, and why any finding was left, so the reviewer sees what the audit changed and why.
