# Transcript layout

## Claude Code

Claude Code keeps transcripts as files with one JSON object per line, laid out as below. The layout can change between versions, so when a path doesn't resolve, search `~/.claude/projects/` for the session id.

```text
~/.claude/projects/<project>/                 <project>: the session's working directory, with / and . turned into -
  <session-id>.jsonl                          the main session
  <session-id>/subagents/agent-<id>.jsonl     each sub-agent, nested ones included
  <session-id>/subagents/agent-<id>.meta.json its type, task description and spawn depth
```

The current session's id is in the `CLAUDE_CODE_SESSION_ID` environment variable. Skill loads appear as `tool_use` blocks named `Skill`, with the skill in `input.skill`, and as `<command-name>/<name></command-name>` in user messages.

## Other harnesses

Find where the harness stores its sessions and how a skill load shows there. Codex keeps them under `~/.codex/sessions/` and loads a skill by reading its `skills/<name>/SKILL.md`, so a read of that file is the load. A session that edits the skill reads that file too, so tell an edit's read apart from a load.

## Searching

Transcripts run long: search them for what the audit needs, such as skill loads, errors, retries, long runs of tool calls on one problem, and the user's corrections, and read around each hit rather than reading them whole.
