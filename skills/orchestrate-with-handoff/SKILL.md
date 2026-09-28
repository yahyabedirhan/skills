---
name: orchestrate-with-handoff
description: Pick up an effort from a handoff document and orchestrate it to a pull request.
argument-hint: "Path to the handoff document"
disable-model-invocation: true
---

# Orchestrate With Handoff

Another session handed this effort over with a **handoff**: a document that names the effort's spec and tickets, the worktree and branch, and what the builder should know that they don't. Start from it.

Receiving the handover is the maintainer's go-ahead: start work without asking for one, and ask the maintainer only for inputs only they have.

1. Read the handoff in full. Confirm you are in the worktree and on the branch it names; if not, say so and stop, because the effort's work lives there.
2. Note whether the handing session is reachable; the handoff says. When a question comes up that the spec, tickets, and handoff don't answer, look in that session if you can read it; otherwise decide it yourself and record the decision for the pull request.
3. Run the **orchestrate-effort** skill on the effort the handoff names, carrying the handoff's notes into the plan.
