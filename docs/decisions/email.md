# Decisions: email

The decisions behind the `email` skill. This file is for maintaining it and is never installed. Add an entry for each new decision: the date, what was decided, and why.

## 2026-09-28

- **Spark reads, Gmail acts.** Measured on the same mailbox, the Spark CLI answered in 0.03 to 0.5 s with compact tables, and the Gmail connector in about 1 s with JSON three to four times the size. Spark's free access level is read-only; its write level costs $20 a month. So every read goes to Spark and every change to Gmail.
- **Google's own Gmail MCP server, through the Claude connector, not a self-hosted one.** The user prefers official servers. The connector needs no Google Cloud project, while self-hosted options (the open-source `workspace-mcp`, or Google's server directly while it is a Workspace developer preview) need one plus a weekly re-login in testing mode.
- **Sending is blocked by Claude Code deny rules, not by Google.** Archiving needs the `gmail.modify` permission, which Google documents as also allowing sending, so no Google permission set allows archive without send. The skill lists the denied tools and how to check they are refused. Trash and spam are denied too, so agents only read, archive, label and draft.
- **Permissions: boxes 1 and 3 on Google's screen.** Drafting works without the separate "Manage drafts and send emails" box, tested with a draft created and deleted.
- **One skill instead of Readdle's recipes.** `readdle/spark-cli-skills` has 34 skills; 16 recipes need the paid access level, several target teams, and `use-spark` costs about 13,600 tokens to load. The read-only recipes (morning standup, inbox by category, end of day) became a few lines of daily workflows here. For the full command reference the skill points at `spark <command> --help` and `spark skill`, which the CLI prints on demand.
- **`spark search <topic>` only when bodies are needed.** One topic search returned 365 KB (about 91,000 tokens) because it includes full bodies; the list mode with `--filter` returned the same hits in about 1 KB.
- **Prompt audit before publishing (maintain-skills' audit step).** A fresh sub-agent ran the `claude-api` prompt audit. It found two more trash-or-spam tools (`apply_sensitive_*_label`, `batch_apply_sensitive_thread_labels`), now denied. It found that `spark event --add/--remove` sends invitation emails while the calendar can be read-write, so calendar changes happen only on the user's explicit request. And `delete_label` waits for the user's go-ahead. The deny-rule check no longer calls a sending tool, because Claude Code hides denied tools; it checks the tool list instead. The description gained calendar, availability and contacts, since `use-spark` covered them and is removed. The workflow "Morning brief" became "Start of day" so it doesn't collide with the built-in `morning` skill.

## 2026-09-28 (later)

- **The skill says how, never when.** Workflows in a tool skill (start of day, triage, end of day) framed actions like archiving as routine, and a project rule could then turn them into actions nobody asked for. The skill now covers only how to read with Spark, how to act with Gmail, and which to pick. The mechanics (read, mark done, pin, label, draft a reply) stay; deciding what to do with an email belongs to the user or to project instructions. The safety facts stay: denied tools, `spark event` sending invitations, and `delete_label` touching every email.

## 2026-09-30

- **Archiving is the only change made without asking.** Every other write, such as a pin, a label, a draft, an undo or a calendar event, waits until the user asks for that exact change, or agrees when the agent names it. The Gmail tools table now says which tools read freely, which archive freely, and which wait for the user. The maintainer asked for it: a draft written unasked is still a change in their mailbox.
- **The skill uses tables and lists, not packed sentences.** The allowed and denied tools, the two tools and the Spark-to-Gmail mapping each became a table or a list, instead of one sentence carrying a dozen names.
