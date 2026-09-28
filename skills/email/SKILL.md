---
name: email
description: >-
  How to work the user's email through the Spark CLI and the Gmail connector:
  which tool to pick, how to list, search and read mail, and how to mark it
  done, label, pin and draft replies, never send. Use whenever a task reads or
  changes the user's mail, calendar, availability or contacts, or when this
  email setup needs configuring or checking.
---

# Email

Two tools, one job each: **Spark reads, Gmail acts.** This skill says how to do things with them. What to do with an email, and when, comes from the user or the project's own instructions. Drafts are the furthest any agent goes; the user sends mail themselves. If a denied tool is available at all, the setup is incomplete: say so and use the connector only for reading until it is fixed.

## The two tools

| | Spark CLI (`spark`) | Gmail connector |
|---|---|---|
| What it is | Readdle's CLI over Spark Desktop's local copy of the mail | Google's Gmail MCP server (`gmailmcp.googleapis.com`), connected as a Claude connector; tools are named `mcp__<server-id>__<tool>` |
| Speed and size | about 0.1 s a call, compact tables | about 1 s a call, JSON three to four times the size |
| Use it for | listing, searching and reading mail; Spark's categories (priority, personal, invitation, notification, newsletter); pins; calendar events, availability and contacts | every change to mail: mark done, labels, star, drafts |
| Needs | Spark Desktop running | the connector signed in |

The two tools number messages differently. To act on something found in Spark, find it again with Gmail's `search_threads`, using `from:` and `subject:` from the Spark row. If more than one thread matches, narrow it with `after:` and `before:` around the Spark row's date, or ask.

## What is enabled

- **Spark mail:** read-only, the free access level. Its mail write commands (`spark action`, `spark draft`, `spark contact-action`, `spark comment`) need a paid level; changes go through Gmail instead.
- **Spark calendar:** the calendar can be read-write even when mail is read-only, and `spark event` with `--add` or `--remove` sends invitation or cancellation emails. Read with `spark events` and `spark availability`; create, change or RSVP to an event only when the user asks for that exact change.
- **Gmail, allowed:** `search_threads`, `get_thread`, `get_message`, `list_labels`, `label_*` and `unlabel_*`, `update_message_labels`, `create_label`, `update_label`, the undo tools (`untrash_*`, `unmark_*_spam`), and the draft tools (`create_draft`, `update_draft`, `get_draft`, `list_drafts`, `delete_draft`). `delete_label` removes a label from every email, so it waits for the user's go-ahead.
- **Gmail, denied** by Claude Code permission rules: `send_message` (which also sends existing drafts), `reply`, `forward`, `trash_message`, `trash_thread`, `mark_message_spam`, `mark_thread_spam`, and `apply_sensitive_message_label`, `apply_sensitive_thread_label`, `batch_apply_sensitive_thread_labels` (these three can trash or spam). Claude Code hides a denied tool, so it does not show up to be called.

Google's permission that allows archiving also allows sending, so those deny rules are what stop a send.

## How Spark's view maps to Gmail

- **Done** is removing the `INBOX` label (archive). Spark shows the change within about a minute.
- **Pin** is the `STARRED` label; Spark's `is:pinned` and `is:starred` return the same emails.
- **Labels** are Gmail labels; Spark shows them as folders.
- **Spark's categories** are Spark's own, so no Gmail tool changes them.
- **Date groups** (Today, Last week, a month) come from each email's date.

## How to

**Read**

```bash
spark emails Inbox --filter "category:priority is:unread"   # one Spark category
spark emails --filter "is:pinned"                           # pinned mail
spark search --filter 'from:<sender> newer_than:7d'         # any Gmail-style query
spark thread <id>                                           # one email in full
spark events --today                                        # also --tomorrow
spark availability --help                                   # free slots across attendees
```

**Mark done.** Find the thread with `search_threads` (`in:inbox` plus `from:` or `subject:`, view `THREAD_VIEW_METADATA_ONLY`), then `unlabel_thread` with `["INBOX"]`. Done when the same search returns `{}`. `label_thread` with `["INBOX"]` puts it back.

**Pin or unpin.** `label_thread` or `unlabel_thread` with `["STARRED"]`.

**Label.** `list_labels` for the label's ID, `create_label` when it does not exist yet, then `label_thread` with that ID.

**Draft a reply.** Read the thread with `get_thread`, then `create_draft` with `replyToMessageId` set to the last message's `id`. The draft's `viewUrl` is where the user reviews and sends it.

## Keep it cheap

- List with `spark emails` or `spark search --filter '<gmail-style query>'`. `spark search <topic>` returns the full bodies of up to 20 matches, often tens of thousands of tokens; use it only when those bodies are the point.
- `spark <command> --help` gives any command's flags. `spark skill` prints the full reference (about 13,000 tokens); reach for it only when `--help` is not enough.
- Call `get_thread` with `messageFormat: PLAIN_TEXT`, and `search_threads` with `THREAD_VIEW_METADATA_ONLY` when only the IDs are needed.

## Setup

When setting either tool up, checking the deny rules, or when a call fails on sign-in or permission, follow [setup.md](setup.md).
