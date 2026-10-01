# Settle commands

The `herdr` commands for settling a session that runs in `herdr`: finding the agents still working, marking the session settled, and freeing the session's own worktree from outside it.

## Active agents

Run `herdr agent list` for each agent's state and pane, and `herdr workspace list` for the worktree behind each workspace; read the two together to see which worktree each agent works in. Leave out only this session's own pane, `$HERDR_PANE_ID`, since other agents may work in other tabs of the same workspace and worktree.

## Settled marker

When this session runs in a `herdr` tab whose label doesn't already start with `[settled]`, put `[settled] ` at the start of that tab's label with `herdr tab rename "$HERDR_TAB_ID" "[settled] <current label>"`; `herdr tab get "$HERDR_TAB_ID"` shows the current label. The marker tells the user nothing more will happen in the tab, which stays only so its history can be read.

## Worktree release from outside the session

Open a labelled tab in the repository's own workspace, the one whose `repo_root` is the repository and whose `is_linked_worktree` is false, and run the commands in the root pane it returns. When the repository has no workspace, create one first with `herdr workspace create --cwd <main checkout> --label <repo> --no-focus`.

```bash
herdr tab create --workspace <repo workspace_id> --cwd <main checkout> --label "shell · Settle · <topic>" --no-focus
herdr pane run <pane_id> 'sleep 30; <free command>; git branch -D <branch>; git worktree list'
```

`<free command>` is the project's worktree tool command that frees this session's worktree, and `<branch>` is its branch. A proof showed the branch merged before the release, so delete it with `-D`: `git branch -d` checks against the main checkout's `HEAD`, not the remote default branch, and can refuse it with no one there to see. The pause gives this session time to finish its last message before freeing its worktree ends it.
