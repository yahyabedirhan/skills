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

## 3. Deny rules

The second box lets the token send mail, so Claude Code's permission rules must block sending. Add these to `permissions.deny` in the user's `~/.claude/settings.json`, with the real server ID:

```json
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
```

Claude Code blocks an agent from editing its own permission rules unless the user asked for that exact change, so add them only when the user asks for it; otherwise ask the user to paste the lines in. These rules bind only Claude Code, because other agents read their own permission settings. Outside Claude Code, the connector's approval prompts are the only guard against a send, so confirm they are on before relying on them.

Check in a new session: none of the ten denied tools appears among the connector's available tools (Claude Code hides denied tools), or `/permissions` lists all ten. Any of them still available means a rule is missing: fix it before using the connector for anything but reading.

## 4. End to end

1. `create_draft` to the user's own address, then `delete_draft` with the returned `id`. Both succeed.
2. Archive one handled email the way **Mark done** in [SKILL.md](SKILL.md) describes, then confirm with `spark emails Inbox` about a minute later that Spark no longer lists it.
