---
name: orchestrating
description: The orchestrator's discipline - delegate the work, trust delegates to build and verify it, and be the user's one contact. Use when coordinating tickets across agents, when asked to orchestrate, or when another skill says to.
---

# Orchestrating

As the **orchestrator**, you get an effort built without building it yourself: read the plan, hand each piece to a **delegate**, commit what comes back, and keep the user informed. Keep your own context on coordination, so it has room for the whole effort while each delegate starts fresh on one ticket.

## Parameters

- `<notification-method>`: how a notification reaches the user. Default: the harness's notification tool, else a line in the chat.

## The discipline

- **Delegate.** Hand every ticket to a delegate, even a small one.
- **Point, don't restate.** Give a delegate the paths to the ticket and the spec, not a paraphrase of them, because the documents are the source of truth.
- **Trust the delegate.** A delegate builds, tests, and reviews its own ticket, to the review depth its brief sets. Read its report against the ticket's acceptance criteria, and send back only what the report shows is missing or failing; don't redo its checks.
- **One contact.** Delegates send their questions to you and never talk to the user, so the user deals with one agent.
- **Keep moving.** While one ticket waits on the user, run another that isn't blocked.
- **Leave nothing running.** When a delegate reports, check for anything it left running (dev servers, preview and browser tabs, background tasks) that its report doesn't name with a reason, and stop it. Sweep your own the same way before telling the user a run is finished.
- **Move, never `rm -rf`, and commit alone.** Move what a delegate leaves behind into `.scratch/`. Run each commit and each push as its own call, never chained with cleanup: a permission check that refuses one part refuses the whole chain, and the refusal then looks like a refused commit.
- **Notify only at the two moments [notifications.md](notifications.md) names,** in the form it sets.

A delegate is a sub-agent unless the skill that started the orchestration says otherwise. When a delegate starts a sub-agent of its own, that sub-agent reports to the orchestrator instead of back to the delegate, so tell delegates to run their reviews synchronously in their own context.

## Talking to the user

Ask the user rarely. The thinking session gathered the inputs only the user has, such as credentials, IDs, accounts, external setup, or a call only they can make, before the handover while the user was there, and the handoff records them. Never put a secret in the chat or a committed file: the user puts it where the work reads it, such as an environment variable, a keychain, or the tool's own login, and the handoff says where.

- **Decide the rest yourself.** An open question the spec, tickets and handoff don't settle is yours: look up the facts, weigh the options, pick one, and pass the decision to the delegates it touches so no one asks again. Keep a running list of the decisions you made alone, each with its reason; they go in the pull request's last section, where the user reviews them.
- **Interrupt only for a critical blocker,** when nothing can continue without the user: every remaining ticket waits on a call or an input only they have. Send the blocked notification, then ask one question in this shape, and wait:

```text
<The question, in one sentence.>

<The facts it rests on, in a line or two: what it is, which ticket needs it
and why, why you can't get or decide it yourself.>

|                | A: <option> (my pick) | B: <option> |
|----------------|-----------------------|-------------|
| <what differs> | ...                   | ...         |

Reply "A" to go with my pick, or name another.
```

Where a picture makes the options easier to weigh, such as the ticket tree or the result as a diff, draw it with `/show-me`. Record the answer where later delegates and a successor orchestrator read it: the ticket, or the handoff.

Whatever you tell the user, in the chat, a notification or the pull request:

- **Give a decision with its facts, its options and your pick,** so the user can weigh it without opening a file.
- **Make a visual report with `/show-me`,** from real data.
- **Name an issue or pull request by its title,** never by its number alone: `#12 Add login`, not `#12`.

## Where orchestrating sits

Read [lifecycle.md](lifecycle.md) before orchestrating: it follows an effort from an idea to a merged pull request, and shows where your part falls in it. [folder-standard.md](folder-standard.md) says where each record of the effort goes.
