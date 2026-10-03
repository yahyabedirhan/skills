# Email setup

Set up the parts in this order, and run each part's check when you finish it.

## 1. Spark CLI

1. The user installs Spark Desktop and signs in to their Gmail account.
2. In Spark: **Settings → AI Agents → Spark CLI Setup**. This puts `spark` on the PATH.
3. In **Settings → AI Agents → Spark CLI Access**, leave the account on **read-only**, the free level.

Check: `spark accounts` lists the account with `(Access: read-only)`, and `spark emails --limit 3` prints three rows. Spark Desktop must be running for either to work.

## 2. Gmail connector

1. The user adds the Gmail connector in Claude: **Settings → Connectors → Gmail**. It is Google's own Gmail MCP server, so no Google Cloud project is needed.
2. On Google's permission screen, tick two of the three boxes:
   - **View your email messages and settings**: read and search.
   - **Read, compose, and send emails from your Gmail account**: labels, archive, and drafts.
   - Leave **Manage drafts and send emails** unticked; it adds nothing the second box lacks, and it is a second send permission.
3. A new session sees the connector's tools as `mcp__<server-id>__<tool>`. The server ID is fixed for that connector; read it from any of its tool names.

Check: `search_threads` with `in:inbox` returns threads.

## 3. Deny and ask rules

The second box lets the token send mail, so permission rules must block sending and make every saved-draft change ask the user. `/set-up-machine` writes them into each harness from its rule table: the deny rows `mail-send` and `mail-destructive`, and the ask rows `mail-draft-write` and `mail-cli-draft`. Run it once the connector is signed in, since it reads the connector's tool names from a session. In Claude Code they become these entries in `~/.claude/settings.json`, with the real server ID:

```json
"deny": [
  "mcp__<server-id>__send_message",
  "mcp__<server-id>__reply",
  "mcp__<server-id>__forward",
  "mcp__<server-id>__trash_message",
  "mcp__<server-id>__trash_thread",
  "mcp__<server-id>__mark_message_spam",
  "mcp__<server-id>__mark_thread_spam",
  "mcp__<server-id>__apply_sensitive_message_label",
  "mcp__<server-id>__apply_sensitive_thread_label",
  "mcp__<server-id>__batch_apply_sensitive_thread_labels"
],
"ask": [
  "mcp__<server-id>__create_draft",
  "mcp__<server-id>__update_draft",
  "mcp__<server-id>__delete_draft",
  "Bash(spark draft *)"
]
```

Claude Code blocks an agent from editing its own permission rules unless the user asked for that exact change, so write them only when the user asks for it; otherwise give the user the lines to paste in. Each harness's reference in `/set-up-machine` says how it carries an ask row and where it can't make the user approve: name those gaps to the user, since there a saved draft stays in chat.

Check in a new session that none of the ten denied tools appears among the connector's available tools, since Claude Code hides denied tools, and that `/permissions` lists the three draft tools and `Bash(spark draft *)` under Ask. A denied tool still available, or a draft tool missing from Ask, means a rule is missing: fix it before using the connector for anything but reading.

## 4. End to end

1. When the user is there to approve, create a Gmail draft to their own address: the harness must ask the user before `create_draft` runs. Once they approve it, delete the draft the same way, which must ask them again. Skip this check when the user isn't there.
2. Archive one handled email the user picks, the way `SKILL.md` marks an email done, then confirm with `spark emails Inbox` about a minute later that Spark no longer lists it.
