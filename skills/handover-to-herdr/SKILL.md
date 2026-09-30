---
name: handover-to-herdr
description: Start a new session in its own Herdr tab and send it a starting prompt - open the worktree as a workspace, label the tab, start the agent, confirm it's working - and close an effort's Herdr workspaces. Use when handing over through Herdr, when closing an effort whose session host is Herdr, or when another skill says to.
argument-hint: "Worktree path, topic, role, and the starting prompt"
---

# Handover To Herdr

The Herdr mechanism of a **handover** (the **handover** skill owns the flow and has already written the handoff and the starting prompt). It takes four inputs: the **worktree** path, the **topic** (the effort's name, or what the work is), the new session's **role** (`Orchestrator`, `Thinking`, or another one-word role), and the **starting prompt**.

When **close-effort** runs with it, read [closing-an-effort.md](closing-an-effort.md) for its commands.

## Parameters

From the Defaults table (a project's row overrides the global one). Unset: no row, or `none`.

- `<agent-to-start>`: the command that starts the new agent. Unset: `claude`.

## Herdr from anywhere

This skill runs from inside a Herdr pane and from outside one, such as a desktop-app session: the `herdr` CLI reaches the server either way.

- Check that `herdr status` reaches a server; `HERDR_ENV` only says whether this session runs in a pane. If it doesn't reach one, say so and hand back to **handover**, whose fallback is the same session.
- Target explicit IDs read from Herdr's JSON (`w1` workspace, `w1:t1` tab, `w1:p1` pane), pass `--no-focus` wherever a command takes it, and never use `--current`. That keeps every command off the pane the maintainer is using.

The **herdr** skill has the full CLI contract but stops outside a pane; these rules replace its `HERDR_ENV` check for the commands below.

## 1. Open a tab in the worktree's workspace

`herdr workspace list` shows each workspace's `worktree` (its `checkout_path`, `repo_root` and `is_linked_worktree`).

- When a workspace's `checkout_path` is the worktree, add a tab to it: `herdr tab create --workspace <workspace_id> --cwd <worktree> --no-focus`. It returns the tab and its root pane.
- Otherwise open the worktree from the repository's own workspace, the one whose `repo_root` is the repository and whose `is_linked_worktree` is false:

  ```bash
  herdr worktree open --workspace <repo workspace_id> --path <worktree> --label <topic> --no-focus
  ```

  It returns the workspace, its first tab and its root pane. Always pass `--workspace`: without it, a call from outside a pane can fail with `linked_worktree_source`. When the repository has no workspace, create one first with `herdr workspace create --cwd <main checkout> --label <repo> --no-focus`; a plain workspace on the main checkout works as the source.

The worktree comes from the project's worktree tool, never from `herdr worktree create`, which puts it outside the tool's reach.

## 2. Label the tab

`herdr tab rename <tab_id> "<harness> · <role> · <topic>"`, with the harness short: `CC` for Claude Code, `Codex`, `OpenCode`, `Cursor`, or the harness's own name.

## 3. Start the agent

Start `<agent-to-start>`, with its flags, in the tab's root pane, named `<topic>-<role>` in lowercase:

```bash
herdr agent start <name> --kind <kind> --pane <pane_id> -- <agent flags>
```

`agent_not_ready` means the agent is blocked at a screen during startup. Read it with `herdr agent read <name> --source visible`. A new worktree path usually shows the harness's "trust this folder?" prompt: that is a security decision, so ask the maintainer to accept it in the tab, then `herdr agent wait <name> --until idle`. Show any other blocking screen to the maintainer the same way.

## 4. Send the starting prompt and confirm

Send the starting prompt exactly as **handover** wrote it, one line, in single quotes so the shell leaves a Codex `$skill` alone:

```bash
herdr agent prompt <name> '<starting prompt>'
herdr agent wait <name> --until working --timeout 60000
```

`agent prompt` delivers the text as a paste: one line runs as a command, while several lines arrive as pasted text and the skill never starts. Leave `--wait` off the prompt: it waits for the agent to settle, and a long run times out first. The handover is fire-and-forget, so `working` is the confirmation.

If the wait times out, look before acting: `herdr agent get <name>`, and `herdr agent read <name> --source visible` (`--lines` fails while the agent works). The prompt may have arrived even so; resend it only when the screen shows it didn't.

Once it is `working`, tell the maintainer the workspace and tab where it runs, and stop.

When this session runs in a Herdr tab and its own work is done, put `[settled] ` at the start of its tab's label (`$HERDR_TAB_ID`): the marker tells the maintainer the tab is only a record now.
