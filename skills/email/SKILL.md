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

Read mail with the Spark CLI, and make every change to mail through the Gmail connector. Leave what to do with an email, and when, to the user.

## Safety

Go no further than a draft: the user reviews and sends every email themselves.

- **Gmail, allowed:** `search_threads`, `get_thread`, `get_message`, `list_labels`, `label_*` and `unlabel_*`, `update_message_labels`, `create_label`, `update_label`, the undo tools (`untrash_*`, `unmark_*_spam`), and the draft tools (`create_draft`, `update_draft`, `get_draft`, `list_drafts`, `delete_draft`). `delete_label` removes a label from every email, so call it only after the user says to.
- **Gmail, denied** by Claude Code permission rules: `send_message` (which also sends existing drafts), `reply`, `forward`, `trash_message`, `trash_thread`, `mark_message_spam`, `mark_thread_spam`, and `apply_sensitive_message_label`, `apply_sensitive_thread_label`, `batch_apply_sensitive_thread_labels` (these three can trash or spam). Claude Code hides a denied tool, so it does not show up to be called.
- Google's permission that allows archiving also allows sending, so only those deny rules stop a send. If any denied tool can be called, the setup is incomplete: tell the user, and use the connector only for reading until the deny rules are fixed.
- **Spark calendar:** the calendar can be read-write even when mail is read-only, and `spark event` with `--add` or `--remove` sends invitation or cancellation emails. Create, change or RSVP to an event only when the user asks for that exact change.

## The two tools

- **Spark CLI (`spark`)** is Readdle's CLI over Spark Desktop's local copy of the mail. It answers in about 0.1 s with compact tables, so use it for listing, searching and reading mail, Spark's categories (priority, personal, invitation, notification, newsletter), pins, calendar events, availability and contacts. It needs Spark Desktop running. Its mail access is read-only, the free level; its mail write commands need a paid level.
- **The Gmail connector** is Google's Gmail MCP server (`gmailmcp.googleapis.com`), connected as a Claude connector, with tools named `mcp__<server-id>__<tool>`. It takes about 1 s a call and returns JSON three to four times Spark's size, so use it for every change to mail: mark done, labels, star, drafts. It needs the connector signed in.

## How Spark's view maps to Gmail

- **Done** is removing the `INBOX` label, which archives the email. Spark shows the change within about a minute.
- **Pin** is the `STARRED` label; Spark's `is:pinned` and `is:starred` return the same emails.
- **Labels** are Gmail labels; Spark shows them as folders.
- **Spark's categories** are Spark's own, so no Gmail tool changes them.
- **Date groups** such as Today, Last week or a month come from each email's date.

## Flow

Read `command-reference.md` before the first call. When setting either tool up, checking the deny rules, or when a call fails on sign-in or permission, follow `setup.md`.

1. **Find** the mail with Spark.
2. **Find it again in Gmail** before changing it, because the two tools number messages differently. When more than one thread matches, narrow the search or ask the user which one they mean.
3. **Act** through Gmail: mark done, pin or unpin, label, or draft a reply. A draft reply ends with its `viewUrl`, where the user reviews and sends it.
4. **Check** that each change took.

## References

- [command-reference.md](command-reference.md): the commands and tool calls behind each action, and how to keep them cheap.
- [setup.md](setup.md): setting up Spark and the Gmail connector, the deny rules, and checking each part.
