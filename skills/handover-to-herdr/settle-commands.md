# Settle commands

The `herdr` commands for settling a session that runs in `herdr`: finding the agents still working, marking the session settled, and freeing the session's own worktree from outside it.

## Active agents

Run `herdr agent list` for each agent's state and pane, and `herdr workspace list` for the worktree behind each workspace; read the two together to see which worktree each agent works in. Leave this session out: its workspace is `$HERDR_WORKSPACE_ID`, or, from outside a pane, the workspace whose `checkout_path` is this session's worktree.

## Settled marker

When this session runs in a `herdr` tab, put `[settled] ` at the start of that tab's label with `herdr tab rename "$HERDR_TAB_ID" "[settled] <current label>"`; `herdr tab get "$HERDR_TAB_ID"` shows the current label. The marker tells the user nothing more will happen in the tab, which stays only so its history can be read.

## Worktree release from outside the session

Open a tab in the repository's own workspace, the one whose `repo_root` is the repository and whose `is_linked_worktree` is false. Label it, and run the commands in its root pane:

```bash
herdr tab create --workspace <repo workspace_id> --cwd <main checkout> --label "shell · Settle · <topic>" --no-focus
herdr pane run <pane_id> 'sleep 30; <free command>; git branch -d <branch>; git worktree list'
```

`<free command>` is the project's worktree tool command that frees this session's worktree, and `<branch>` is its branch. Use `git branch -D` when only the patch or pull-request proof showed the branch merged. The pause gives this session time to finish its last message before freeing its worktree ends it.
