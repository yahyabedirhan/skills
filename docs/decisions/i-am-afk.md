# Decisions: i-am-afk and i-am-back

This page records the decisions behind the [`i-am-afk`](../../skills/i-am-afk/SKILL.md) and [`i-am-back`](../../skills/i-am-back/SKILL.md) skills.
It is for maintaining the skills and is never installed.
Entries follow the shape in [index.md](index.md).

## 2026-10-10: two skills, one pair

- **Status:** accepted
- **Context:** The maintainer's north star asks to gather the parts that need the user into a few sessions, with long autonomous stretches between them. Nothing marked where such a stretch starts and ends.
- **Options:** None considered.
- **Choice and why:** `/i-am-afk` starts a long autonomous stretch, and `/i-am-back` ends it with an interactive review.
- **Consequences:** The two skills share their closing report.

## 2026-10-10: user-invoked only

- **Status:** accepted
- **Context:** Only the user knows when they leave or return.
- **Options:** None considered.
- **Choice and why:** Set `disable-model-invocation: true` for Claude Code, and ship `agents/openai.yaml` with `allow_implicit_invocation: false` for Codex.
- **Consequences:** The skills cost no context until the user types them.

## 2026-10-10: in the user's own voice, and short

- **Status:** accepted
- **Context:** The maintainer asked for no detailed procedure.
- **Options:** None considered.
- **Choice and why:** Each skill is a message from the user to the agents, close to the words the user dictated.
- **Consequences:** The skills hold no steps.

## 2026-10-10: a costly choice becomes a plan, not a ban

- **Status:** accepted
- **Context:** The first draft said "leave hard-to-reverse actions for me".
- **Options:** The ban: the north star says safety is enforced by guardrails.
- **Choice and why:** A choice costly to undo comes to the user as one plan: the decisions, the trade-offs and the agent's pick. The agent continues with the work the choice doesn't block.
- **Consequences:** None beyond the plan.

## 2026-10-10: a step only the user can do comes with why and what it unlocks

- **Status:** accepted
- **Context:** Some steps need the user, such as a login or an approval.
- **Options:** None considered.
- **Choice and why:** Follow the north star's rule: give the step, why, and what it unlocks.
- **Consequences:** None.

## 2026-10-10: one report, the same in both skills

- **Status:** accepted
- **Context:** The agents may finish before the user returns.
- **Options:** None considered.
- **Choice and why:** Both skills end with the same six headings: What is done, What is not done yet, Decisions agents made, Things you should know, Decisions waiting for you, Next steps. The user gets the same report either way, and the fixed names keep it the same every time.
- **Consequences:** None.

## 2026-10-10: a prompt audit instead of evals

- **Status:** accepted
- **Context:** The skills are a few lines each.
- **Options:** Evals: too heavy for a few lines.
- **Choice and why:** A fresh sub-agent ran `/claude-api`'s `prompt-audit` on both folders, against `/writing-for-agents` and `skill-writing.md`. It found no pressure language, no dated patterns and no procedure. Its findings:
  1. (medium) `i-am-afk`: "Do everything you can do without me" repeated "keep working on your own". Applied: the line is removed.
  2. (medium) `i-am-afk`: the closing list asked only for a recommendation, while the bullet above asked for a plan with trade-offs. Applied: the list now asks for "the plans for the decisions I need to make".
  3. (low) `i-am-afk`: "needs me by nature" was a vague test. Applied: "a step only I can do".
  4. (medium) `i-am-back`: "show them" in the description read as showing the agents. Applied: "show the user".
  5. (low) `i-am-back`: "What you did" and "What is done" overlap. Left at first, because the user asked for both. Later solved by the shared report, which has only "What is done".
- **Consequences:** The auditor noted that sending a message to other people is now only implied by "costly to undo". It proposed no change, and none was made: the user's guardrails and global rules cover it.
