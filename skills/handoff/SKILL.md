---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up. Use when asked for a handoff, or when another skill says to write one.
argument-hint: "What will the next session be used for?"
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save it as `<handoff-folder>/<topic-or-project>.md`, never committed. The agent that takes the work over deletes it once the work is done.

## Parameters

- `<handoff-folder>`: the folder handoffs are saved in, as the environment defaults name it, such as a folder outside every repository. With no default, use `.handoff/` in the repository and keep it out of git.
- `<topic-or-project>`: the name of the topic or the project the next session works on.

Include a "suggested skills" section in the document, naming which skills the next agent should call the Skill tool for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
