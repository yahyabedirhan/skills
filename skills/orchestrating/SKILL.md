---
name: orchestrating
description: The orchestrator's discipline - delegate the work, trust delegates to build and verify it, and be the user's one contact. Use when coordinating tickets across agents, when asked to orchestrate, or when another skill says to.
---

# Orchestrating

An **orchestrator** gets an effort built without building it. It reads the plan, hands each piece to a **delegate**, commits what comes back, and keeps the user informed. Its own context stays on coordination, so it stays sharp for the whole effort while each delegate starts fresh on one ticket.

## The discipline

- **Delegate.** A ticket goes to a delegate, even a small one. The orchestrator's own work is coordination: reading, dispatching, committing, and talking to the user.
- **Point, don't restate.** A delegate gets paths to the ticket and the spec, not a paraphrase of them. The documents are the source of truth.
- **Trust the delegate.** A delegate builds, tests, and reviews its own ticket. Read its report against the ticket's acceptance criteria, and send back only what the report shows is missing or failing; don't redo its checks.
- **One contact.** Delegates never talk to the user. Their questions come to the orchestrator, which answers what the documents settle and brings the rest to the user with exactly what they need to decide.
- **Keep moving.** While one ticket waits on the user, run another that isn't blocked.

A delegate is a sub-agent unless the skill that started the orchestration says otherwise. A sub-agent's own sub-agents report to the orchestrator, not to it, so tell delegates to run reviews synchronously in their own context.

## Where orchestrating sits

Read [lifecycle.md](lifecycle.md) before orchestrating: it is the path of an effort from an idea to a merged pull request, and it places your part within it.
