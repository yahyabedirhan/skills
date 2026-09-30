# Closing an effort in Herdr

The Herdr commands for **close-effort**'s session host steps. The rules of *Herdr from anywhere* in `SKILL.md` hold for each: check `herdr status` first, target explicit IDs from Herdr's JSON, pass `--no-focus`, never `--current`.

## Find the agents still working (step 1)

`herdr agent list` shows each agent's state and pane, and `herdr workspace list` shows the worktree behind each workspace; together they show which worktree each agent works in. An agent other than this session that is `working` in one of the effort's worktrees keeps that worktree. This session's workspace is `$HERDR_WORKSPACE_ID`, or, from outside a pane, the workspace whose `checkout_path` is this session's worktree.

## Free this session's worktree from outside it (step 8)

Open a tab in the repository's own workspace, found as in step 1 of `SKILL.md`, label it, and run the command in its root pane:

```bash
herdr tab create --workspace <repo workspace_id> --cwd <main checkout> --no-focus
herdr tab rename <tab_id> "shell · Close · <effort>"
herdr pane run <pane_id> 'sleep 30; <free command>; git worktree list'
```

`<free command>` is the worktree tool's, from close-effort's `commands.md`. The pause lets the report finish first.
