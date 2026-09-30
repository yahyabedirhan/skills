---
name: email
description: >-
  How to work the user's email through the Spark CLI and the Gmail connector:
  which tool to pick, how to list, search and read mail, and how to mark it
  done, label, pin and draft replies. It archives freely, makes any other
  change only when asked, and never sends. Use whenever a task reads or
  changes the user's mail, calendar, availability or contacts, or when this
  email setup needs configuring or checking.
---

# Email

Read mail with the Spark CLI, and make every change to mail through the Gmail connector. Leave what to do with an email, and when, to the user.

## Safety

The user reviews and sends every email themselves, so go no further than a draft.

Archive an email when the task calls for it. Make any other change only after the user asks for that exact change, or after you name it and they agree: a pin, a label, a draft, an undo, or a calendar event.

### Gmail tools

| Tools | Use |
|---|---|
| `search_threads`, `get_thread`, `get_message`, `list_labels`, `get_draft`, `list_drafts` | Read freely. |
| `unlabel_thread` or `update_message_labels` removing `INBOX` | Archive freely. |
| `label_*`, `unlabel_*` and `update_message_labels` for any other label, `create_label`, `update_label` | After the user asks, or agrees when you name it. Never add `TRASH` or `SPAM`, since that trashes or spams the email around the deny rules. |
| `create_draft`, `update_draft`, `delete_draft` | After the user asks, or agrees when you name it. |
| `untrash_*`, `unmark_*_spam` | After the user asks, or agrees when you name it. |
| `delete_label` | Only when the user names that label to delete, since it removes the label from every email. |

Claude Code's permission rules deny the rest, and a denied tool doesn't show up to be called:

- `send_message`, which also sends existing drafts;
- `reply` and `forward`;
- `trash_message` and `trash_thread`;
- `mark_message_spam` and `mark_thread_spam`;
- `apply_sensitive_message_label`, `apply_sensitive_thread_label` and `batch_apply_sensitive_thread_labels`, which can trash or spam.

Google's permission that allows archiving also allows sending, so only those deny rules stop a send.

- **When a denied tool can be called:** the setup is incomplete. Tell the user, and only read until the deny rules are fixed.

### Spark calendar

The calendar can be read-write even when Spark's mail is read-only, and `spark event` with `--add` or `--remove` sends invitation or cancellation emails. Create, change or answer an event only when the user asks for that exact change.

## The two tools

| Tool | Use it for | Speed and size | Needs |
|---|---|---|---|
| Spark CLI, `spark` | Listing, searching and reading mail; Spark's categories, pins, calendar events, availability and contacts | About 0.1 s, compact tables | Spark Desktop running. Mail access is read-only on the free level. |
| Gmail connector, `mcp__<server-id>__<tool>` | Every change to mail | About 1 s, JSON three to four times Spark's size | The connector signed in |

Spark reads Spark Desktop's local copy of the mail. The Gmail connector is Google's Gmail MCP server, `gmailmcp.googleapis.com`, connected as a Claude connector.

## How Spark's view maps to Gmail

| In Spark | In Gmail |
|---|---|
| Done | The `INBOX` label removed, which archives the email. Spark shows it within about a minute. |
| Pin | The `STARRED` label. Spark's `is:pinned` and `is:starred` return the same emails. |
| A folder | A Gmail label. |
| A category: priority, personal, invitation, notification, newsletter | Spark's own; no Gmail tool changes it. |
| Today, Last week, a month | Each email's date. |

## Flow

When setting either tool up, checking the deny rules, or when a call fails on sign-in or permission, follow `setup.md`.

1. **Find** the mail with Spark.

   ```bash
   spark emails Inbox --filter "category:priority is:unread"   # one Spark category
   spark emails --filter "is:pinned"                           # pinned mail
   spark search --filter 'from:<sender> newer_than:7d'         # any Gmail-style query
   spark thread <id>                                           # one email in full
   spark events --today                                        # also --tomorrow
   spark availability --help                                   # free slots across attendees
   ```

   List with `spark emails` or `spark search --filter '<gmail-style query>'`. `spark search <topic>` returns the full bodies of up to 20 matches, often tens of thousands of tokens, so use it only when you need those bodies.
   - **When you need a command's flags:** run `spark <command> --help`. `spark skill` prints the full reference, about 13,000 tokens, so reach for it only when `--help` is not enough.
2. **Find it again in Gmail** before changing it, because the two tools number messages differently. Search with `search_threads`, using `from:` and `subject:` from the Spark row. Pass the view `THREAD_VIEW_METADATA_ONLY` when only the IDs are needed, since it keeps the answer small.
   - **When more than one thread matches:** narrow the search with `after:` and `before:` around the Spark row's date, or ask the user which one they mean.
3. **Act** through Gmail: archive, or make the change the user asked for.

   | Change | Calls |
   |---|---|
   | Mark done | Add `in:inbox` to the search from step 2, then `unlabel_thread` with `["INBOX"]`. `label_thread` with `["INBOX"]` puts it back. |
   | Pin or unpin | `label_thread` or `unlabel_thread` with `["STARRED"]`. |
   | Label | `list_labels` for the label's ID, `create_label` when it does not exist yet, then `label_thread` with that ID. |
   | Draft a reply | Read the thread with `get_thread`, then `create_draft` with `replyToMessageId` set to the last message's `id`. |

   Call `get_thread` with `messageFormat: PLAIN_TEXT`, since it keeps the thread small.
   - **For any change but archiving that the user hasn't asked for:** name it and wait for their answer.
   - **For a draft reply:** end with its `viewUrl`, where the user reviews and sends it.
4. **Check** that each change took.
   - **After marking done:** the `in:inbox` search returns `{}` once the email is archived.

## References

- [setup.md](setup.md): setting up Spark and the Gmail connector, the deny rules, and checking each part.
