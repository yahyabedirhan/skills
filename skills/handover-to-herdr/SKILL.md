---
name: handover-to-herdr
description: Start a new agent session in its own `herdr` tab, send it its starting prompt and confirm it's working; also free a closing effort's own worktree from a `herdr` tab outside it. Use when a handover, a new effort or an effort's close runs through `herdr`, or when another skill says to.
argument-hint: "Worktree path, topic, role, and the starting prompt"
---

# Handover To Herdr

Open a new agent session in a `herdr` tab and send it its starting prompt. The calling skill, `/handover` or `/init-effort`, has already written the handoff and the prompt and decides what the new session does. It hands over four inputs: the worktree path; the topic, which is the effort's name or what the work is; the new session's role, such as `Orchestrator`, `Thinking` or another one-word role; and the starting prompt.

Run this skill from inside a `herdr` pane or from outside one, such as a desktop-app session. `/herdr` requires `HERDR_ENV=1`, which only says this session runs in a pane, so check that `herdr status` reaches a server instead. Target explicit IDs read from `herdr`'s JSON, pass `--no-focus` wherever a command takes it, and never use `--current`, so that no command lands on the pane the maintainer is using.

## Parameters

- `<agent-to-start>`: the command that starts a new agent session, e.g. `claude` or `codex`, with its flags.

## Steps

1. Check that `herdr status` reaches a server.
   - **If it doesn't:** say so and hand back to the calling skill, which then works as if there were no session host.
2. Open a tab in the workspace whose checkout is the worktree, or open the worktree as a new workspace from the repository's own workspace. `herdr workspace list` shows each workspace's `worktree`, with its `checkout_path`, `repo_root` and `is_linked_worktree`. Take the worktree from the project's worktree tool, never from `herdr worktree create`, because the tool can't manage a worktree it didn't create.
   - **When a workspace's `checkout_path` is the worktree:** add a tab to it with `herdr tab create --workspace <workspace_id> --cwd <worktree> --no-focus`. It returns the tab and its root pane.
   - **Otherwise:** open the worktree from the repository's own workspace, the one whose `repo_root` is the repository and whose `is_linked_worktree` is false:

     ```bash
     herdr worktree open --workspace <repo workspace_id> --path <worktree> --label <topic> --no-focus
     ```

     It returns the workspace, its first tab and its root pane. Always pass `--workspace`, because without it a call from outside a pane can fail with `linked_worktree_source`.
   - **When the repository has no workspace:** create one first with `herdr workspace create --cwd <main checkout> --label <repo> --no-focus`. A plain workspace on the main checkout works as the source.
3. Label the tab `<harness> · <role> · <topic>` with `herdr tab rename <tab_id> "<harness> · <role> · <topic>"`, so the maintainer can tell what runs in it. Write the harness in short form: `CC` for Claude Code, `Codex`, `OpenCode`, `Cursor`, or the harness's own name.
4. Start `<agent-to-start>` in the tab's root pane as an agent named `<topic>-<role>` in lowercase:

   ```bash
   herdr agent start <name> --kind <kind> --pane <pane_id> -- <agent flags>
   ```

   - **When a startup screen blocks it,** which `agent_not_ready` reports: read the screen with `herdr agent read <name> --source visible`, show it to the maintainer and let them decide. A new worktree path usually shows the harness's "trust this folder?" prompt, which is a security decision, so ask the maintainer to accept it in the tab. Then run `herdr agent wait <name> --until idle`.
5. Send the starting prompt exactly as the calling skill wrote it, and confirm the new agent is working. Send it on one line and in single quotes, so the shell doesn't expand a Codex `$skill` reference:

   ```bash
   herdr agent prompt <name> '<starting prompt>'
   herdr agent wait <name> --until working --timeout 60000
   ```

   Leave `--wait` off the prompt: it waits until the agent goes idle again, and a long run times out before that.
   - **If the wait times out:** check the agent before you resend anything. `herdr agent get <name>` shows its state, and `herdr agent read <name> --source visible` shows its screen; leave `--lines` off, because it fails while the agent works. The prompt may have arrived anyway, so resend it only when the screen shows it didn't.
6. If this session runs in a `herdr` tab, put `[settled] ` at the start of that tab's label once this session's own work is done. Use the same `herdr tab rename`, with `$HERDR_TAB_ID` as the tab. The marker tells the maintainer nothing more will happen in the tab, which stays only so its history can be read.
7. Give the calling skill the workspace and tab where the new agent runs, so it can tell the maintainer.

When `/close-effort` calls this skill, read `close-effort-commands.md` instead of the steps above.

## References

- [close-effort-commands.md](close-effort-commands.md): the `herdr` commands a close needs: finding the agents still working, and freeing the closing session's own worktree from outside it.
