# Herdr: daily operations

`herdr` runs terminals as workspaces, tabs, and panes, and recognizes the coding agents inside them. The effort workflow uses a workspace per worktree and a tab per agent. These are the operations it needs; the **herdr** skill (or `herdr --skill`) has the full contract, and `herdr <group>` prints a group's commands.

Most commands return JSON: read IDs from it rather than predicting them. IDs look like `w1` (workspace), `w1:t1` (tab), and `w1:p1` (pane). Inside a Herdr pane, `HERDR_ENV=1` is set, along with `HERDR_WORKSPACE_ID`, `HERDR_TAB_ID`, and `HERDR_PANE_ID` for the caller.

| Need | Command | Notes |
|---|---|---|
| Open a worktree as a workspace | `herdr worktree open --path <path> --label <effort> --no-focus` | Returns the workspace, its first tab, and its root pane. |
| Name a tab | `herdr tab rename <tab_id> <label>` | This tab: `"$HERDR_TAB_ID"`. |
| Add a tab | `herdr tab create --workspace <id> --cwd <path> --label <label> --no-focus` | Returns the tab and its root pane. |
| List what's running | `herdr tab list --workspace <id>`, `herdr agent list` | |
| Start an agent | `herdr agent start <name> --kind <kind> --pane <pane_id>` | Needs a shell pane at its prompt. Kinds include `claude`, `codex`, `opencode`, `cursor`. Names: lowercase, digits, `-` and `_`, unique. |
| Send it a prompt | `herdr agent prompt <name> "<text>" --wait --timeout 120000` | `--wait` returns once the agent settles; `agent_blocked` means it is waiting at a question or approval: show the user. |
| Wait for a state | `herdr agent wait <name> --until working` | States: `idle`, `working`, `blocked`, `done`, `unknown`. |
| Read its screen | `herdr agent read <name> --source recent --lines 200` | How one session reads another's messages. |
| Close a workspace | `herdr workspace close <workspace_id>` | Do this before destroying its worktree. |

Don't use `herdr worktree create`: it puts worktrees outside the Treehouse pool, where nothing tracks or cleans them. Create worktrees with `treehouse` and open them with `herdr worktree open`.
