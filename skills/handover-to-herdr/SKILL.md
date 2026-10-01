---
name: handover-to-herdr
description: Start a new agent session in its own `herdr` workspace and tab, send it its starting prompt and confirm it's working. Use when a handover, a new effort or a session's settle runs through `herdr`.
argument-hint: "Worktree path, topic, role, and the starting prompt"
---

# Handover To Herdr

Open a new agent session in a `herdr` tab and send it its starting prompt. The calling skill, `/handover` or `/init-effort`, requires a written handoff document and the prompt and decides what the new session does. It hands over four inputs: the worktree path; the topic, which is the effort's name or what the work is; the new session's role, such as `orchestrator`, `thinking` or another one-word role; and the starting prompt.

Run this skill from inside a `herdr` pane or from outside one, such as a desktop-app session. Target explicit IDs read from `herdr`'s JSON, pass `--no-focus` wherever a command takes it, and never use `--current`, so that no command lands on the pane the maintainer is using.

## Parameters

- `<worktree-tool>`: the tool that makes and frees worktrees, e.g. `treehouse`, or plain git worktrees.
- `<agent>`: the command that starts a new agent session, e.g. `claude` or `codex`, with its flags.

## Steps

When `/settle-session` calls this skill, read `settle-commands.md` instead of these steps.

1. Check that `herdr status` reaches a server. Don't go by `HERDR_ENV=1`, which `/herdr` requires: it only says this session runs in a pane.
   - **If no server answers:** say so and hand back to the calling skill, which then works as if there were no session host.
2. Open a tab in the workspace whose checkout is the worktree, or open the worktree as a new workspace from the repository's own workspace. `herdr workspace list` shows each workspace's `worktree`, with its `checkout_path`, `repo_root` and `is_linked_worktree`. Make the worktree with `<worktree-tool>`, never with `herdr worktree create`.
   - **When a workspace's `checkout_path` is the worktree:** add a tab to it with `herdr tab create --workspace <workspace_id> --cwd <worktree> --no-focus`. It returns the tab and its root pane.
   - **Otherwise:** open the worktree from the repository's own workspace, the one whose `repo_root` is the repository and whose `is_linked_worktree` is false:

     ```bash
     herdr worktree open --workspace <repo workspace_id> --path <worktree> --label <topic> --no-focus
     ```

     It returns the workspace, its first tab and its root pane. Always pass `--workspace`, because without it a call from outside a pane can fail with `linked_worktree_source`.
   - **When the repository has no workspace:** create one first with `herdr workspace create --cwd <main checkout> --label <repo> --no-focus`. A plain workspace on the main checkout works as the source.
3. Label the tab `<harness> · <role> · <topic>` with `herdr tab rename <tab_id> "<harness> · <role> · <topic>"`, so the maintainer can tell what runs in it. Write the harness in short form: `CC` for Claude Code, `Codex`, `OpenCode`, `Cursor`, or the harness's own name.
4. Start `<agent>` in the tab's root pane as an agent named `<topic>-<role>` in lowercase:

   ```bash
   herdr agent start <name> --kind <kind> --pane <pane_id> -- <agent flags>
   ```

   - **When a startup screen blocks it,** which `agent_not_ready` reports: read the screen with `herdr agent read <name> --source visible`, show it to the maintainer and let them decide. A new worktree path usually shows the harness's "trust this folder?" prompt, which is a security decision, so ask the maintainer to accept it in the tab. Then run `herdr agent wait <name> --until idle`.
5. Send the starting prompt exactly as the calling skill wrote it, and confirm the new agent is working. Send it on one line, since `herdr agent prompt` sends it as a paste. A multi-line paste doesn't start a skill. Put it in single quotes, so the shell doesn't expand a Codex `$skill` reference, and write each `'` inside it as `'\''`, so an apostrophe doesn't end the string:

   ```bash
   herdr agent prompt <name> '<starting prompt>'
   herdr agent wait <name> --until working --timeout 60000
   ```

   Leave `--wait` off the prompt: it waits until the agent goes idle again, and a long run times out before that.
   - **If the wait times out:** check the agent before you resend anything. `herdr agent get <name>` shows its state, and `herdr agent read <name> --source visible` shows its screen; leave `--lines` off, because it fails while the agent works. The prompt may have arrived anyway, so resend it only when the screen shows it didn't.
6. Once this session's own work is done, mark its tab settled as `settle-commands.md`'s Settled marker section says.
7. Give the calling skill the workspace and tab where the new agent runs, so it can tell the maintainer.


## References

- [settle-commands.md](settle-commands.md): the `herdr` commands a settle needs: finding the agents still working, marking the session settled, and freeing the settling session's own worktree from outside it.
