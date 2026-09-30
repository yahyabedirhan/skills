# Closing an effort in Herdr

Use these Herdr commands when closing an effort: to find the agents still working, and to free this session's own worktree.

## Find the agents still working

Run `herdr agent list` for each agent's state and pane, and `herdr workspace list` for the worktree behind each workspace; read the two together to see which worktree each agent works in. Leave this session out: its workspace is `$HERDR_WORKSPACE_ID`, or, from outside a pane, the workspace whose `checkout_path` is this session's worktree.

## Free this session's worktree from outside it

Open a tab in the repository's own workspace, the one whose `repo_root` is the repository and whose `is_linked_worktree` is false. Label it, and run the command in its root pane:

```bash
herdr tab create --workspace <repo workspace_id> --cwd <main checkout> --no-focus
herdr tab rename <tab_id> "shell · Close · <effort>"
herdr pane run <pane_id> 'sleep 30; <free command>; git worktree list'
```

`<free command>` is the project's worktree tool command that frees this session's worktree. The pause lets this session finish its report before the command stops it.
