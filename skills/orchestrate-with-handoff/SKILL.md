---
name: orchestrate-with-handoff
description: Pick up an effort from a thinking session's handoff document and orchestrate it to a pull request.
argument-hint: "Path to the handoff document"
disable-model-invocation: true
---

# Orchestrate With Handoff

A thinking session ended with a **handoff**: a document that names the effort's spec and tickets, says what the builder should know that they don't, and names the thinking session itself. Start from it.

1. Read the handoff in full. Confirm you are in the worktree and on the branch it names; if not, say so and stop, because the effort's work lives there.
2. Note the thinking session it names. When a question comes up that the spec, tickets, and handoff don't answer, look there before asking the user.
3. Run the **orchestrate-effort** skill on the effort folder the handoff names, carrying the handoff's notes into the plan.
