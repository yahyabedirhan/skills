# Decisions: maintain-skills

The decisions behind the `maintain-skills` skill. This file is for maintaining it and is never installed. Add an entry for each new decision: the date, what was decided, and why.

## 2026-09-28

- **Every new skill gets a prompt audit from a fresh sub-agent.** The author's context is anchored on what it meant to write; a sub-agent reads only what is on disk. It runs the bundled `claude-api` skill's `prompt-audit` subcommand, the same audit `/doctor prompt-audit <path>` hands off to, so the check follows Anthropic's current prompting guidance rather than a rubric kept here. The auditor reports and does not edit; the author applies the accepted fixes.
- **Efficiency analysis is a disclosed reference, run only on request.** The user asks for it when introducing a new skill whose cost matters; running it by default would spend a session's tokens measuring tokens. `scripts/session-usage.py` makes the numbers repeatable from the transcript instead of estimated.
- **Cost is judged per task, not per token.** A stronger model that finishes in fewer calls is usually cheaper overall, so the analysis does not recommend down-tiering the model by default. The measured lever in the first analysis (a company briefing video) was context re-reads: calls × context size, cut by running heavy phases in a fresh sub-agent.
