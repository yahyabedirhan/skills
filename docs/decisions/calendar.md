# Decisions: calendar

The decisions behind the `calendar` skill. This file is for maintaining it and is never installed. Read it before changing the skill. Entries follow the shape in [index.md](index.md).

## 2026-10-01: Spark first, the Google Calendar connector as fallback

- **Status:** accepted
- **Context:** The calendar skill (#68) needs a source to read events from.
- **Options:**
  - Spark only: it needs Spark Desktop running.
  - The Google Calendar connector only: it costs a network call and returns JSON.
- **Choice and why:** Use both, Spark first. `spark events` and `spark availability` answer in about 0.1 s with compact tables. The connector works without Spark Desktop.
- **Consequences:** With neither source, the skill says that the calendar can't be read and why.

## 2026-10-01: calendar writes are denied by rule

- **Status:** accepted
- **Context:** The skill is read-only, and an agent must not create, change or answer an event. `calendar-mail-cli-send` already denied `spark event` (create, update, delete, RSVP) and `spark comment`. The hook refused `spark event --help` during this work.
- **Options:**
  - Discourage writes in the skill text: an agent can still make them.
  - List each write tool in a deny rule: a tool added later is allowed until someone notices it.
- **Choice and why:** A new row, `calendar-write`, denies every tool on a calendar server whose name doesn't start with a reading verb (`list`, `get`, `search`, `find`, `query`, `check`, `suggest`, or the connector's sign-in tools). Denying everything but reads keeps a new tool denied until someone looks at it.
- **Consequences:** A tool named like a read that writes is not caught.

## 2026-10-01: the deny rule is checked through the hook's samples

- **Status:** accepted
- **Context:** The `calendar-write` row needs a check, and a check against a real event could change the calendar.
- **Options:** None considered.
- **Choice and why:** `verify.py` runs the row's samples, such as `create_event` and `respond_to_event`, through the hook. No real event is touched.
- **Consequences:** The connector isn't signed in on the machine this was built on. Its real tool names are still to be checked by hand once it is.

## 2026-10-01: read the calendar without asking when a task needs an event

- **Status:** accepted
- **Context:** A task often needs an event's time, which the user would otherwise copy over by hand.
- **Options:** Ask before each read: it costs the user more than it protects.
- **Choice and why:** Read without asking. The agent records the time, treats an event's text as data, and reads only the range the task needs.
- **Consequences:** Calendar reads happen without a prompt for any task that needs one.

## 2026-10-01: the calendar is a skill of its own

- **Status:** accepted
- **Context:** `/email` now reads mail only on request, and the calendar needs a home.
- **Options:** Put the calendar in `/email`: one skill would carry two opposite reading rules, and its trigger would fire for every task that needs a meeting time.
- **Choice and why:** Give the calendar its own skill, so each skill has one reading rule.
- **Consequences:** `/email` and `/calendar` are separate, with opposite rules for reading.
