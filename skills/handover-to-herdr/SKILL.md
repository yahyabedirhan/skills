---
name: handover-to-herdr
description: Start a new agent session in its own Herdr tab, send it its starting prompt and confirm it's working; also free a closing effort's own worktree from a Herdr tab outside it. Use when a handover, a new effort or an effort's close runs through Herdr, or when another skill says to.
argument-hint: "Worktree path, topic, role, and the starting prompt"
---

# Handover To Herdr

This skill opens a new agent session in a Herdr tab and sends it its starting prompt. The skill that calls it, `/handover` or `/init-effort`, has already written the handoff and the prompt and decides what the new session does; this skill only starts that session in Herdr.

It takes four inputs:

- the **worktree** path;
- the **topic**: the effort's name, or what the work is;
- the new session's **role**: `Orchestrator`, `Thinking`, or another one-word role;
- the **starting prompt**.

Closing an effort needs two more Herdr steps: finding the agents still working, and freeing the closing session's own worktree from outside it. When `/close-effort` calls this skill for those, read [closing-an-effort.md](closing-an-effort.md).

## Parameters

- `<agent-to-start>`: the command that starts the new agent. Default: this session's harness.

## Herdr from anywhere

`/herdr` has the full Herdr CLI contract, but it stops outside a Herdr pane. This skill also runs from outside one, such as a desktop-app session, because the `herdr` CLI reaches the server either way. Two rules replace `/herdr`'s `HERDR_ENV` check for every command in this skill, `closing-an-effort.md` included:

- Check that `herdr status` reaches a server; `HERDR_ENV` only says whether this session runs in a pane. If it doesn't reach one, say so and hand back to the calling skill.
- Target explicit IDs read from Herdr's JSON, such as `w1` for a workspace, `w1:t1` for a tab and `w1:p1` for a pane. Pass `--no-focus` wherever a command takes it, and never use `--current`. That keeps every command off the pane the maintainer is using.

## 1. Open a tab in the worktree's workspace

`herdr workspace list` shows each workspace's `worktree`, with its `checkout_path`, `repo_root` and `is_linked_worktree`.

- When a workspace's `checkout_path` is the worktree, add a tab to it: `herdr tab create --workspace <workspace_id> --cwd <worktree> --no-focus`. It returns the tab and its root pane.
- Otherwise open the worktree from the repository's own workspace, the one whose `repo_root` is the repository and whose `is_linked_worktree` is false:

  ```bash
  herdr worktree open --workspace <repo workspace_id> --path <worktree> --label <topic> --no-focus
  ```

  It returns the workspace, its first tab and its root pane. Always pass `--workspace`: without it, a call from outside a pane can fail with `linked_worktree_source`. When the repository has no workspace, create one first with `herdr workspace create --cwd <main checkout> --label <repo> --no-focus`; a plain workspace on the main checkout works as the source.

The worktree comes from the project's worktree tool, never from `herdr worktree create`, which puts it outside the tool's reach.

Done when you hold the tab's ID and its root pane's ID.

## 2. Label the tab

`herdr tab rename <tab_id> "<harness> · <role> · <topic>"`, with the harness short: `CC` for Claude Code, `Codex`, `OpenCode`, `Cursor`, or the harness's own name.

## 3. Start the agent

Start `<agent-to-start>`, with its flags, in the tab's root pane, named `<topic>-<role>` in lowercase:

```bash
herdr agent start <name> --kind <kind> --pane <pane_id> -- <agent flags>
```

`agent_not_ready` means the agent is blocked at a screen during startup. Read it with `herdr agent read <name> --source visible`. A new worktree path usually shows the harness's "trust this folder?" prompt: that is a security decision, so ask the maintainer to accept it in the tab, then `herdr agent wait <name> --until idle`. Show any other blocking screen to the maintainer the same way.

Done when `agent start` succeeds, or the wait reaches `idle`.

## 4. Send the starting prompt and confirm

Send the starting prompt exactly as the calling skill wrote it, one line, in single quotes so the shell leaves a Codex `$skill` alone:

```bash
herdr agent prompt <name> '<starting prompt>'
herdr agent wait <name> --until working --timeout 60000
```

Leave `--wait` off the prompt: it waits for the agent to settle, and a long run times out first.

If the wait times out, look before acting. `herdr agent get <name>` shows the agent's state, and `herdr agent read <name> --source visible` shows its screen; leave `--lines` off, because it fails while the agent works. The prompt may have arrived even so, so resend it only when the screen shows it didn't.

When this session runs in a Herdr tab and its own work is done, put `[settled] ` at the start of its tab's label; `$HERDR_TAB_ID` names that tab. The marker tells the maintainer the tab is only a record now.

The handover is done once the new agent is `working`. Give the calling skill the workspace and tab where it runs; the calling skill tells the maintainer.
