# Command reference

## Read with Spark

```bash
spark emails Inbox --filter "category:priority is:unread"   # one Spark category
spark emails --filter "is:pinned"                           # pinned mail
spark search --filter 'from:<sender> newer_than:7d'         # any Gmail-style query
spark thread <id>                                           # one email in full
spark events --today                                        # also --tomorrow
spark availability --help                                   # free slots across attendees
```

## Find a Spark result in Gmail

Search with Gmail's `search_threads`, using `from:` and `subject:` from the Spark row. If more than one thread matches, narrow it with `after:` and `before:` around the Spark row's date.

## Change mail with Gmail

- **Mark done.** `search_threads` querying `in:inbox` plus `from:` or `subject:`, with view `THREAD_VIEW_METADATA_ONLY`, then `unlabel_thread` with `["INBOX"]`. The same search returns `{}` once it took. `label_thread` with `["INBOX"]` puts it back.
- **Pin or unpin.** `label_thread` or `unlabel_thread` with `["STARRED"]`.
- **Label.** `list_labels` for the label's ID, `create_label` when it does not exist yet, then `label_thread` with that ID.
- **Draft a reply.** Read the thread with `get_thread`, then `create_draft` with `replyToMessageId` set to the last message's `id`.

## Keep it cheap

- List with `spark emails` or `spark search --filter '<gmail-style query>'`. `spark search <topic>` returns the full bodies of up to 20 matches, often tens of thousands of tokens; use it only when you need those bodies.
- `spark <command> --help` gives any command's flags. `spark skill` prints the full reference, about 13,000 tokens; reach for it only when `--help` is not enough.
- Call `get_thread` with `messageFormat: PLAIN_TEXT`, and `search_threads` with `THREAD_VIEW_METADATA_ONLY` when only the IDs are needed.
