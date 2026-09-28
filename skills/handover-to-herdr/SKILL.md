---
name: handover-to-herdr
description: Start a new session in its own Herdr tab and send it a starting prompt - open the worktree as a workspace, label the tab, start the agent, confirm it's working. Use when handing over through Herdr, or when another skill says to.
argument-hint: "Worktree path, topic, role, and the starting prompt"
---

# Handover To Herdr

The Herdr mechanism of a **handover** (the **handover** skill owns the flow and has already written the handoff and the starting prompt). It takes four inputs: the **worktree** path, the **topic** (the effort's name, or what the work is), the new session's **role** (`Orchestrator`, `Thinking`, or another one-word role), and the **starting prompt**.

Check that `herdr status` reaches a server. If it doesn't, say so and hand back to **handover**, whose fallback is a pasted prompt. The **herdr** skill has the full CLI contract; this skill carries the commands a handover needs. Most commands return JSON: read IDs from it (`w1` workspace, `w1:t1` tab, `w1:p1` pane).

## 1. Open a tab in the worktree's workspace

- When `herdr workspace list` shows a workspace whose `worktree.checkout_path` is the worktree, add a tab to it: `herdr tab create --workspace <workspace_id> --cwd <worktree> --no-focus`. It returns the tab and its root pane.
- Otherwise open the worktree as a new workspace: `herdr worktree open --path <worktree> --label <topic> --no-focus`. It returns the workspace, its first tab and its root pane.

The worktree comes from the project's worktree tool, never from `herdr worktree create`, which puts it outside the tool's reach.

## 2. Label the tab

`herdr tab rename <tab_id> "<topic> · <role> · <harness>"`, with the harness short: `CC` for Claude Code, `Codex`, `OpenCode`, `Cursor`, or the harness's own name.

## 3. Start the agent

Start the maintainer's preferred agent (from their instructions, with the flags they give; default `claude`) in the tab's root pane, named `<topic>-<role>` in lowercase:

```bash
herdr agent start <name> --kind <kind> --pane <pane_id> -- <agent flags>
```

## 4. Send the starting prompt and confirm

```bash
herdr agent prompt <name> '<starting prompt>'
herdr agent wait <name> --until working --timeout 60000
```

Once it is `working`, tell the maintainer the workspace and tab where it runs.

When this session runs in a Herdr tab and its own work is done, append ` [settled]` to its tab's label: the marker tells the maintainer the tab is only a record now.
