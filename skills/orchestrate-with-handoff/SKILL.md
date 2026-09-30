---
name: orchestrate-with-handoff
description: Pick up an effort from a handoff document and orchestrate it to a pull request.
argument-hint: "Path to the handoff document"
disable-model-invocation: true
---

# Orchestrate With Handoff

Receiving the handover is the maintainer's go-ahead, so start work without asking for one.

1. Read the handoff. Confirm you are in the worktree and on the branch it names; if not, say so and stop, because the effort's work lives there.
2. Run `/orchestrate-effort` on the spec and tickets the handoff names, and on the handoff itself.

When the spec, tickets and handoff leave a question open and the handoff says the handing session can be reached, look for the answer in that session before you decide it yourself.
