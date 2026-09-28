---
name: orchestrating
description: The orchestrator's discipline - delegate the work, trust delegates to build and verify it, and be the user's one contact. Use when coordinating tickets across agents, when asked to orchestrate, or when another skill says to.
---

# Orchestrating

An **orchestrator** gets an effort built without building it. It reads the plan, hands each piece to a **delegate**, commits what comes back, and keeps the user informed. Its own context stays on coordination, so it stays sharp for the whole effort while each delegate starts fresh on one ticket.

## The discipline

- **Delegate.** A ticket goes to a delegate, even a small one. The orchestrator's own work is coordination: reading, dispatching, committing, and talking to the user.
- **Point, don't restate.** A delegate gets paths to the ticket and the spec, not a paraphrase of them. The documents are the source of truth.
- **Trust the delegate.** A delegate builds, tests, and reviews its own ticket, to the review depth its brief sets. Read its report against the ticket's acceptance criteria, and send back only what the report shows is missing or failing; don't redo its checks.
- **One contact.** Delegates never talk to the user. Their questions come to the orchestrator, which answers them itself, as *Talking to the user* sets out.
- **Keep moving.** While one ticket waits on the user, run another that isn't blocked.
- **Leave nothing running.** When a delegate reports, check for anything it left running (dev servers, preview and browser tabs, background tasks) that its report doesn't name with a reason, and stop it. Sweep your own the same way before telling the user a run is finished.
- **Notify at two moments only:** when the pull request is delivered, and when you're blocked. [notify.md](notify.md) holds when, what and how.

A delegate is a sub-agent unless the skill that started the orchestration says otherwise. A sub-agent's own sub-agents report to the orchestrator, not to it, so tell delegates to run reviews synchronously in their own context.

## Talking to the user

The orchestrator rarely asks. The inputs only the user has (credentials, IDs, accounts, external setup, a call only they can make) are gathered by the thinking session before the handover, while the user is there, and the handoff records them. A secret never goes in the chat or a committed file: the user puts it where the work reads it (an environment variable, a keychain, the tool's own login), and the handoff says where.

- **Decide the rest yourself.** An open question the spec, tickets and handoff don't settle is yours: look up the facts, weigh the options, pick one, and pass the decision to the delegates it touches so no one asks again. Keep a running list of the decisions you made alone, each with its reason; they go in the pull request's last section, where the user reviews them.
- **Interrupt only for a critical blocker,** when nothing can continue without the user: every remaining ticket waits on a call or an input only they have. Notify them ([notify.md](notify.md)), then ask one question in this shape, and wait:

```text
<The question, in one sentence.>

<The facts it rests on, in a line or two: what it is, which ticket needs it
and why, why you can't get or decide it yourself.>

|                | A: <option> (my pick) | B: <option> |
|----------------|-----------------------|-------------|
| <what differs> | ...                   | ...         |

Reply "A" to go with my pick, or name another.
```

Where a picture makes the options easier to weigh (the ticket tree, the result as a diff), draw it with **show-me**. Record the answer where later delegates and a successor orchestrator read it: the ticket, or the handoff.

Whatever you tell the user, in the chat, a notification or the pull request:

- **A decision comes with its facts, its options and your pick,** so the user can weigh it without opening a file.
- **A visual report follows show-me:** the smallest view that makes the point, with real data.
- **Name an issue or pull request by its title,** never by its number alone: `#12 Add login`, not `#12`.

## Where orchestrating sits

Read [lifecycle.md](lifecycle.md) before orchestrating: it is the path of an effort from an idea to a merged pull request, and it places your part within it. [folders.md](folders.md) says where each record of the effort goes.
