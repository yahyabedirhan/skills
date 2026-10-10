# Decisions: i-am-afk and i-am-back

The decisions behind the `i-am-afk` and `i-am-back` skills. This file is for maintaining them and is never installed. Add an entry for each new decision: the date, what was decided, and why.

## 2026-10-10

- **Two skills, one pair.** `/i-am-afk` starts a long autonomous stretch, and `/i-am-back` ends it with an interactive review. They follow the autonomy spectrum in the maintainer's north star: gather the parts that need the user into a few sessions, with long autonomous stretches between them.
- **User-invoked only.** Only the user knows when they leave or return. `disable-model-invocation: true` for Claude Code, and `agents/openai.yaml` with `allow_implicit_invocation: false` for Codex. They cost no context until the user types them.
- **In the user's own voice, and short.** Each skill is a message from the user to the agents, close to the words the user dictated. The maintainer asked for no detailed procedure.
- **A costly choice becomes a plan, not a ban.** The first draft said "leave hard-to-reverse actions for me". The north star says safety is enforced by guardrails, and a choice costly to undo comes to the user as one plan: the decisions, the trade-offs and the agent's pick. The skill now asks for that plan, and the agent continues with the work it doesn't block.
- **A step only the user can do comes with why and what it unlocks.** This follows the north star's rule for steps that need the user, such as a login or an approval.
- **One list, the same in both skills.** Both end with the same six headings: What is done, What is not done yet, Decisions agents made, Things you should know, Decisions waiting for you, Next steps. When the agents finish before the user returns, the user gets the same report as from `/i-am-back`. The fixed names keep the report the same every time.
- **No evals.** The skills are a few lines each, so a prompt audit stood in for evals.

### Prompt audit

A fresh sub-agent ran `/claude-api`'s `prompt-audit` on both folders, against `/writing-for-agents` and `skill-writing.md`. It found no pressure language, no dated patterns and no procedure. Its findings:

1. (medium) `i-am-afk`: "Do everything you can do without me" repeated "keep working on your own". Applied: the line is removed.
2. (medium) `i-am-afk`: the closing list asked only for a recommendation, while the bullet above asked for a plan with trade-offs. Applied: the list now asks for "the plans for the decisions I need to make".
3. (low) `i-am-afk`: "needs me by nature" was a vague test. Applied: "a step only I can do".
4. (medium) `i-am-back`: "show them" in the description read as showing the agents. Applied: "show the user".
5. (low) `i-am-back`: "What you did" and "What is done" overlap. Left at first, because the user asked for both. Later solved by the shared list, which has only "What is done".

The auditor also noted that sending a message to other people is now only implied by "costly to undo". It proposed no change, and none was made: the user's guardrails and global rules cover it.
