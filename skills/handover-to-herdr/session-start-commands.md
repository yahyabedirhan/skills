# Session start commands

The `herdr` commands that open a tab, label it, start an agent in it and send the agent its starting prompt, with the pitfalls each one has shown.

## Tab

`herdr workspace list` shows each workspace's `worktree`, with its `checkout_path`, `repo_root` and `is_linked_worktree`.

- When a workspace's `checkout_path` is the worktree, add a tab to it: `herdr tab create --workspace <workspace_id> --cwd <worktree> --no-focus`. It returns the tab and its root pane.
- Otherwise open the worktree from the repository's own workspace, the one whose `repo_root` is the repository and whose `is_linked_worktree` is false:

  ```bash
  herdr worktree open --workspace <repo workspace_id> --path <worktree> --label <topic> --no-focus
  ```

  It returns the workspace, its first tab and its root pane. Always pass `--workspace`, because without it a call from outside a pane can fail with `linked_worktree_source`. When the repository has no workspace, create one first with `herdr workspace create --cwd <main checkout> --label <repo> --no-focus`; a plain workspace on the main checkout works as the source.

Take the worktree from the project's worktree tool, never from `herdr worktree create`, because the tool can't manage a worktree it didn't create.

## Label

Rename the tab with `herdr tab rename <tab_id> "<harness> · <role> · <topic>"`. Write the harness in short form: `CC` for Claude Code, `Codex`, `OpenCode`, `Cursor`, or the harness's own name. The same command, with `$HERDR_TAB_ID` as the tab, adds the `[settled] ` marker to this session's own tab.

## Agent start

Start the agent, with its flags, in the tab's root pane:

```bash
herdr agent start <name> --kind <kind> --pane <pane_id> -- <agent flags>
```

`agent_not_ready` means the agent is blocked at a screen during startup. Read the screen with `herdr agent read <name> --source visible`. A new worktree path usually shows the harness's "trust this folder?" prompt, which is a security decision, so ask the maintainer to accept it in the tab. Then run `herdr agent wait <name> --until idle`.

## Starting prompt

Send the prompt on one line and in single quotes, so the shell doesn't expand a Codex `$skill` reference, then wait for the agent to start working:

```bash
herdr agent prompt <name> '<starting prompt>'
herdr agent wait <name> --until working --timeout 60000
```

Leave `--wait` off the prompt: it waits until the agent goes idle again, and a long run times out before that.

If the wait times out, check the agent before you resend anything. `herdr agent get <name>` shows its state, and `herdr agent read <name> --source visible` shows its screen; leave `--lines` off, because it fails while the agent works. The prompt may have arrived anyway, so resend it only when the screen shows it didn't.
