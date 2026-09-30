# Closing an effort in Herdr

The Herdr commands for **close-effort**'s session host steps. The rules of *Herdr from anywhere* in `SKILL.md` hold for each: check `herdr status` first, target explicit IDs from Herdr's JSON, pass `--no-focus`, never `--current`.

## Find the effort's workspaces and agents (step 1)

`herdr workspace list` and `herdr agent list`. This session's workspace is `$HERDR_WORKSPACE_ID`, or, from outside a pane, the workspace whose `checkout_path` is this session's worktree.

## Ask the delivering orchestrator (step 3)

```bash
herdr agent prompt <name> '<question>' --wait --timeout 600000
herdr agent read <name> --source recent-unwrapped --lines 80
```

A timeout counts as no reply.

## Close the effort's workspaces (step 8)

`herdr workspace close <workspace_id>` for each one this session doesn't run in. An agent `working` in it, per `herdr agent list`, keeps it open.

## Return this session's worktree from outside it (step 9)

Open a tab in the repository's main-checkout workspace (the one whose `repo_root` is the repository and whose `is_linked_worktree` is false), label it, and run the command in its root pane:

```bash
herdr tab create --workspace <repo workspace_id> --cwd <main checkout> --no-focus
herdr tab rename <tab_id> "shell · Close · <effort>"
herdr pane run <pane_id> 'sleep 30; <return command>; herdr workspace close <this workspace_id>; git worktree list'
```
