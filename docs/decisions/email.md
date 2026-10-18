# Decisions: email

The decisions behind the `email` skill. This file is for maintaining it and is never installed. Read it before changing the skill. Entries follow the shape in [index.md](index.md).

## 2026-09-28: Spark reads, Gmail acts

- **Status:** accepted
- **Context:** The skill can work mail through the Spark CLI or the Gmail connector. Both were measured on the same mailbox.
- **Options:**
  - Gmail for everything: it answered in about 1 s, with JSON three to four times the size.
  - Spark for everything: its free access level is read-only, and its write level costs $20 a month.
- **Choice and why:** Every read goes to Spark and every change to Gmail. Spark answered in 0.03 to 0.5 s with compact tables.
- **Consequences:** The skill needs both tools, and maps Spark results to Gmail actions.

## 2026-09-28: Google's Gmail MCP server through the Claude connector

- **Status:** accepted
- **Context:** The skill needs a Gmail server, and the user prefers official servers.
- **Options:** A self-hosted server, such as the open-source `workspace-mcp` or Google's server directly while it is a Workspace developer preview: each needs a Google Cloud project and a weekly re-login in testing mode.
- **Choice and why:** Use Google's own Gmail MCP server through the Claude connector. It needs no Google Cloud project.
- **Consequences:** The skill depends on the Claude connector.

## 2026-09-28: Claude Code deny rules block sending

- **Status:** accepted
- **Context:** Archiving needs the `gmail.modify` permission. Google documents that it also allows sending, so no Google permission set allows archive without send.
- **Options:** Rely on Google's permissions: they can't separate the two.
- **Choice and why:** Claude Code deny rules block sending. Trash and spam are denied too, so agents only read, archive, label and draft. The skill lists the denied tools and how to check that they are refused.
- **Consequences:** The block holds only in harnesses that enforce the deny rules.

## 2026-09-28: grant boxes 1 and 3 on Google's permission screen

- **Status:** accepted
- **Context:** Google's permission screen offers a separate "Manage drafts and send emails" box.
- **Options:** Grant that box too: drafting doesn't need it.
- **Choice and why:** Grant boxes 1 and 3 only. A test created and deleted a draft without the extra box.
- **Consequences:** None beyond the narrower grant.

## 2026-09-28: one skill instead of Readdle's recipes

- **Status:** accepted
- **Context:** `readdle/spark-cli-skills` has 34 skills. 16 recipes need the paid access level, several target teams, and `use-spark` costs about 13,600 tokens to load.
- **Options:** Install Readdle's skills: too large and mostly unusable on the free level.
- **Choice and why:** Write one skill. The read-only recipes (morning standup, inbox by category, end of day) became a few lines of daily workflows. For the full command reference, the skill points at `spark <command> --help` and `spark skill`, which the CLI prints on demand.
- **Consequences:** The daily workflows were later removed; see [2026-09-28: the skill says how, never when](#2026-09-28-the-skill-says-how-never-when).

## 2026-09-28: spark search only when bodies are needed

- **Status:** accepted
- **Context:** One `spark search <topic>` returned 365 KB (about 91,000 tokens), because it includes full bodies.
- **Options:** None considered.
- **Choice and why:** Use the list mode with `--filter` by default. It returned the same hits in about 1 KB. Use `spark search` only when the bodies are needed.
- **Consequences:** None beyond the smaller reads.

## 2026-09-28: apply the prompt audit before publishing

- **Status:** accepted
- **Context:** `maintain-skills` asks for a prompt audit of a new skill. A fresh sub-agent ran the `claude-api` prompt audit.
- **Options:** None considered.
- **Choice and why:** Apply its findings:
  - Two more trash-or-spam tools, `apply_sensitive_*_label` and `batch_apply_sensitive_thread_labels`, are now denied.
  - `spark event --add/--remove` sends invitation emails while the calendar can be read-write, so calendar changes happen only on the user's explicit request.
  - `delete_label` waits for the user's go-ahead.
  - The deny-rule check no longer calls a sending tool, because Claude Code hides denied tools. It checks the tool list instead.
  - The description gained calendar, availability and contacts, since `use-spark` covered them and is removed.
  - The workflow "Morning brief" became "Start of day", so it doesn't collide with the built-in `morning` skill.
- **Consequences:** The calendar part later moved to `/calendar`; see [2026-10-01: the calendar moves to /calendar](#2026-10-01-the-calendar-moves-to-calendar).

## 2026-09-28: the skill says how, never when

- **Status:** accepted
- **Context:** This replaces the daily workflows of [2026-09-28: one skill instead of Readdle's recipes](#2026-09-28-one-skill-instead-of-readdles-recipes). Workflows in a tool skill (start of day, triage, end of day) framed actions like archiving as routine. A project rule could then turn them into actions nobody asked for.
- **Options:** Keep the workflows: they invite unasked changes.
- **Choice and why:** The skill covers only how to read with Spark, how to act with Gmail, and which to pick. The mechanics stay: read, mark done, pin, label, draft a reply. Deciding what to do with an email belongs to the user or to project instructions.
- **Consequences:** The safety facts stay: the denied tools, `spark event` sending invitations, and `delete_label` touching every email.

## 2026-09-30: archiving is the only change made without asking

- **Status:** accepted
- **Context:** The skill had no rule for which writes need the user. A draft written unasked is still a change in the user's mailbox.
- **Options:** None considered.
- **Choice and why:** Archive freely. Every other write, such as a pin, a label, a draft, an undo or a calendar event, waits until the user asks for that exact change, or agrees when the agent names it. The maintainer asked for it.
- **Consequences:** The Gmail tools table now says which tools read freely, which archive freely, and which wait for the user.

## 2026-09-30: tables and lists, not packed sentences

- **Status:** accepted
- **Context:** Single sentences carried a dozen tool names each.
- **Options:** None considered.
- **Choice and why:** The allowed and denied tools, the two tools, and the Spark-to-Gmail mapping each became a table or a list. They are easier to scan.
- **Consequences:** None beyond the layout.

## 2026-10-01: mail is read only for an email task the user asked for

- **Status:** accepted
- **Context:** The skill loaded for any task that could use mail (#67).
- **Options:** None considered.
- **Choice and why:** Read mail only for an email task the user asked for. A task that mail would merely help, or a project or skill instruction to check mail, is not a request: the agent says what it would look up and asks. A request covers its own task, not later unrelated ones.
- **Consequences:** The description, the reading rules and the Gmail tools table all say the same.

## 2026-10-01: a plain "draft a mail" is text in chat

- **Status:** accepted
- **Context:** A saved draft is a change in the user's mailbox (#67).
- **Options:** None considered.
- **Choice and why:** A plain request for a draft gives text in chat. A saved draft needs the user to name Gmail or Spark, in any wording, and naming one allows only that draft.
- **Consequences:** A tool that can't save the draft, such as `spark draft` on Spark's free read-only level, is reported, not swapped for the other tool.

## 2026-10-01: every saved-draft write needs the user's own approval

- **Status:** accepted
- **Context:** A draft overwritten by mistake is lost work in the user's mailbox (#67).
- **Options:** Let an automatic reviewer approve: it doesn't count as the user.
- **Choice and why:** New ask rows in `/set-up-machine`'s table, `mail-draft-write` and `mail-cli-draft`, carry `approver: "user"`. The hook refuses them where no one will ask the user.
- **Consequences:** Saved drafts can't be written in unattended runs.

## 2026-10-01: generic facts in the skill, personal rules in the private source

- **Status:** accepted
- **Context:** #67 touched both the skill and the user's private rules.
- **Options:** None considered.
- **Choice and why:** The skill keeps capability facts: Spark reads fastest, and only Gmail writes on Spark's free level. Nothing in the user's private instructions or permission rows needed to change.
- **Consequences:** The private repository got no pull request.

## 2026-10-01: who counts as a caller

- **Status:** accepted
- **Context:** Other skills and tasks may want mail read (#67). No other skill in this repo reads mail.
- **Options:** None considered.
- **Choice and why:** A morning-brief skill the user starts by name counts as the user's request. A project instruction or recurring task that says to check mail doesn't, so the agent asks first.
- **Consequences:** Rules for recurring tasks were deferred by #67 and are left alone.

## 2026-10-01: the end-to-end check runs only with the user present

- **Status:** accepted
- **Context:** The end-to-end check created a draft unattended.
- **Options:** None considered.
- **Choice and why:** The check runs only with the user there to approve each write, as the saved-draft rule requires.
- **Consequences:** The check can't run unattended.

## 2026-10-01: the calendar moves to /calendar

- **Status:** accepted
- **Context:** The calendar's reading rule is the opposite of mail's.
- **Options:** Keep both in this skill: one skill would carry two rules for "may I read?".
- **Choice and why:** Move the calendar to `/calendar`.
- **Consequences:** The calendar's decisions now live in `calendar.md`.
