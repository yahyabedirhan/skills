---
name: continue-session
description: Continue another session's work by reading its transcript, without sending it input. Use when the user asks to continue, pick up or take over from another session, named by its session id or by where it sits in the session host.
argument-hint: "<session id> or its place, such as \"top pane\", \"right tab\" or \"another workspace\""
---

# Continue session

Continue another session's work as a **silent reader**: read its transcript, then do the work in this session. The other session often holds a long uncached history, and any input to it re-sends that whole history.

Only read the other session. Send it no text, keys, prompts or messages, and leave it unresumed, since each of those wakes it.

## Parameters

- `<session-host>`: where agent sessions run, e.g. `herdr`, Claude Code Desktop, Codex Desktop.

## 1. Find the session

- **When the user gives a session id:** use it.
- **When the user gives a place,** such as "top pane" or "left tab": resolve it from this session's own place with `<session-host>`'s read-only commands, then read the session id of the agent there. In `herdr`, resolve this pane with `herdr pane current --current`, find the target with `herdr pane neighbor --pane <id> --direction <left|right|up|down>`, `herdr pane list` or `herdr tab list`, and read its `agent_session` from `herdr pane get <pane_id>`.
  - **When the place is a scope,** such as "another workspace": list the agent sessions in it, leave out this session and the shell panes, and pick by title, working directory and status. Ask the user only when more than one still fits.
  - **When the host reports no session id:** take the newest transcript of that pane's harness whose working directory matches the pane's.

## 2. Read the transcript

Find the transcript on disk: Claude Code keeps it at `~/.claude/projects/<project>/<session-id>.jsonl`, with `/` and `.` in the working directory turned into `-`, and Codex under `~/.codex/sessions/`. For another harness, find where it stores its sessions. Search the transcript rather than reading it whole: read the user's requests, the last assistant messages, the latest tool results and any open decision. Then check the working directory's branch, uncommitted changes and pull requests.

Read on until you can state the goal, what is done, what was in progress when it stopped, and the next step.

## 3. Continue

Give the user that recap in a few lines, then continue the work here, in the session's working directory.

- **When the other session is still working:** tell the user and wait for their word, since two sessions editing one worktree overwrite each other.
