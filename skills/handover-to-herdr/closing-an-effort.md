# Closing an effort in Herdr

The Herdr commands for **close-effort**'s session host steps. The rules of *Herdr from anywhere* in `SKILL.md` hold for each: check `herdr status` first, target explicit IDs from Herdr's JSON, pass `--no-focus`, never `--current`. The close leaves every workspace open.

## Find the agents still working (step 1)

`herdr workspace list` and `herdr agent list`. An agent `working` in one of the effort's worktrees keeps that worktree. This session's workspace is `$HERDR_WORKSPACE_ID`, or, from outside a pane, the workspace whose `checkout_path` is this session's worktree.

## Free this session's worktree from outside it (step 8)

Open a tab in the repository's main-checkout workspace (the one whose `repo_root` is the repository and whose `is_linked_worktree` is false), label it, and run the command in its root pane:

```bash
herdr tab create --workspace <repo workspace_id> --cwd <main checkout> --no-focus
herdr tab rename <tab_id> "shell · Close · <effort>"
herdr pane run <pane_id> 'sleep 30; <free command>; git worktree list'
```

`<free command>` is the worktree tool's, from close-effort's `commands.md`. The pause lets the report finish first.
