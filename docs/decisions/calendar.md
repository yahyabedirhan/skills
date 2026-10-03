# Decisions: calendar

The decisions behind the `calendar` skill. This file is for maintaining it and is never installed. Add an entry for each new decision: the date, what was decided, and why.

## 2026-10-01: read-only calendar access (#68)

- **Both sources, Spark first.** Spark's `spark events` and `spark availability` answer in about 0.1 s with compact tables but need Spark Desktop running. The Google Calendar connector works without it, at the cost of a network call and JSON. So Spark is the first try and the connector the fallback; with neither, the skill says the calendar can't be read and why.
- **Writes are denied by rule, not discouraged.** `calendar-mail-cli-send` already denied `spark event` (create, update, delete, RSVP) and `spark comment`; the hook refused `spark event --help` during this work. A new row, `calendar-write`, denies every tool on a calendar server whose name doesn't start with a reading verb (`list`, `get`, `search`, `find`, `query`, `check`, `suggest`, or the connector's sign-in tools). Denying everything but reads, rather than listing the writes, keeps a tool added later denied until someone looks at it. Its gap: a tool named like a read that writes.
- **Checked through the hook's samples, never a real event.** `verify.py` runs the row's samples, such as `create_event` and `respond_to_event`, through the hook. The connector isn't signed in on the machine this was built on, so its real tool names are still to be checked by hand once it is.
- **Read without asking when a task needs an event.** An event's time is what the user would otherwise copy over by hand, so asking first costs more than it protects. The agent records the time, treats an event's text as data, and reads only the range the task needs.
- **A skill of its own.** `/email` now reads only on request; putting the calendar there would have given one skill two opposite reading rules and a trigger that fires for every task needing a meeting time.
