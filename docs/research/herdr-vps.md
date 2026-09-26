# Herdr across the Mac and the VPS

> Moved from the job-search vault's `.scratch/skill-improvements/research/` on 2026-09-26. Paths under `tmp/`, `~/.claude/` and the vault point at the user's machine and are not in this repo. The VPS host, user and machine ID are redacted.

Facts for issues [#13](https://github.com/yahyabedirhan/skills/issues/13), [#15](https://github.com/yahyabedirhan/skills/issues/15) and [#16](https://github.com/yahyabedirhan/skills/issues/16): how an agent on the Mac reaches Herdr, git and tools on the VPS, what the reverse direction looks like, and what can be checked before handing work from one machine to the other. Researched on 2026-09-25 against Herdr 0.9.0 on both machines. How a handover prompt gets into an agent tab is covered elsewhere.

Sources are cited inline. `[mac]` and `[vps]` mark command output captured on that machine on 2026-09-25; `ssh vps` stands for `ssh <vps-user>@<vps-host>` (see "Finding the host"). Herdr docs are cited at the `v0.9.0` tag unless marked 0.9.1, under `https://raw.githubusercontent.com/herdrdev/herdr/<tag>/docs/next/website/src/content/docs/`.

## The machine model

- **One server per machine.** Each machine runs its own Herdr server with its own sessions, workspaces and pane processes. A saved machine is only a connection profile in the Mac client; it "targets one remote session" and is "not a cross-machine pane inventory" (`connecting-machines.mdx`; herdr skill).
- **What is saved.** `herdr machine list --json` [mac] returns one profile: id `<machine-id>`, label `Yahya's VPS`, target `<vps-user>@<vps-host>`, session `default`, enabled. The VPS has no saved machines of its own (`herdr machine list --json` [vps] returns `[]`).
- **How the window attaches.** The Mac's Herdr window connects to the VPS server over SSH in the background. The selected machine gets keyboard input and streams its screens; other machines keep sending workspace info, agent states and notifications without screens. A lost connection shows dimmed cached state (`connecting-machines.mdx`). The Mac client log shows the endpoint as `ssh:<profile-id>` with frequent `connection was lost` / `health check timed out` reconnects (`~/.config/herdr/herdr-client.log` [mac]). `herdr --remote <target>` is the older single-machine attach, where the remote server owns the panes and the local client draws the UI (`persistence-remote.mdx`).
- **What runs where.** Panes, agents, git checkouts and tools all live on the VPS. The Mac only draws. Herdr "does not copy local command plugins, configuration, executables, or secrets onto SSH hosts" (`connecting-machines.mdx`).
- **The API is a local Unix socket only.** Mac: `~/.config/herdr/herdr.sock`; VPS: `~/.config/herdr/herdr.sock` (`herdr status --json` on each). There is no TCP listener; `HERDR_SOCKET_PATH` overrides the socket path (`cli-reference.mdx`, Environment variables). So in 0.9.0 the only way for a Mac agent to drive the VPS server is `ssh vps ~/.local/bin/herdr …`.
- **Selecting the VPS in the window changes nothing for agents.** CLI commands in a pane "still use that pane's inherited session and socket" (`connecting-machines.mdx`; herdr skill).
- **IDs and names are per server.** Workspace, tab and pane IDs and agent names "are scoped to one server. Two machines may both contain `w1:p1` or an agent named `reviewer`" (`connecting-machines.mdx`). Every remote command must look its IDs up on the VPS first. `--current` and `$HERDR_PANE_ID` from a Mac pane mean nothing there.
- **0.9.1 adds CLI forwarding.** Herdr 0.9.1 (released 2026-09-16) adds a global prefix `herdr --machine <label-or-id> …` that sends `workspace`, `worktree`, `tab`, `pane`, `notification`, `agent` (not `attach`), `api snapshot` and `status server` to a saved machine as JSON over non-interactive SSH, with no open window and no shell interpolation of payloads. It needs 0.9.1 on both ends and never falls back to Local (release notes `https://github.com/herdrdev/herdr/releases/tag/v0.9.1`; `v0.9.1/.../cli-reference.mdx`, "Saved SSH machines"). On 0.9.0 it fails: `herdr --machine x agent list` prints `unknown option: --machine` [mac].

## Mac to VPS: command reference

Verified on 2026-09-25 [mac → vps]: plain `ssh vps` with no password prompt (`-o BatchMode=yes` succeeds). **`herdr` is not on the non-interactive SSH `PATH`**: `command -v herdr` and `command -v claude` print nothing over `ssh vps '…'`, while `bash -lc 'command -v herdr'` finds `~/.local/bin/herdr` [vps]. Use the full path `~/.local/bin/herdr`, or wrap in `bash -lc`.

Read-only (run and verified):

| Goal | Command |
| --- | --- |
| Server version and socket | `ssh vps '~/.local/bin/herdr status --json'` |
| Sessions | `ssh vps '~/.local/bin/herdr session list --json'` |
| Workspaces | `ssh vps '~/.local/bin/herdr workspace list'` |
| Tabs in a workspace | `ssh vps '~/.local/bin/herdr tab list --workspace w6'` |
| Panes (with cwd) | `ssh vps '~/.local/bin/herdr pane list --workspace w6'` |
| Agents and their status | `ssh vps '~/.local/bin/herdr agent list'` |
| One agent | `ssh vps '~/.local/bin/herdr agent get w6:p2'` |
| An agent's recent output | `ssh vps '~/.local/bin/herdr agent read w6:p2 --source recent-unwrapped --lines 120'` |
| Full live state | `ssh vps '~/.local/bin/herdr api snapshot'` (from `herdr api --help`; not run) |

All list/get commands return JSON. `agent list` gives, per agent: `agent` (kind), `agent_status` (`idle`, `working`, `blocked`, `done`, `unknown`), `pane_id`, `tab_id`, `workspace_id`, `cwd`, `terminal_title` and the agent's native session id [vps]. On 2026-09-25 the VPS had workspaces `w5` "~ ROOT", `w7` "~ VPS MAINTAINER", `w6` "shipyard" (tabs `w6:t1` "CLI", `w6:t2` "Orchestrator"), `w4` "job-search", `w2` "tarmy-empire", and one agent: `claude` in `w6:p2`, `idle`, cwd `~/Developer/yahyabedirhan/shipyard`, unnamed [vps].

Writes (syntax from `herdr <cmd> --help` [mac]; **not run**, per the research rules):

| Goal | Command |
| --- | --- |
| Create a workspace | `ssh vps '~/.local/bin/herdr workspace create --cwd <abs-path> --label <text> --no-focus'` → read `.result.workspace`, `.result.tab`, `.result.root_pane` |
| Open an existing git worktree as a workspace | `ssh vps '~/.local/bin/herdr worktree open --cwd <repo> --path <worktree> --label <text> --no-focus'` |
| Create a tab | `ssh vps '~/.local/bin/herdr tab create --workspace <wN> --cwd <abs-path> --label <text> --no-focus'` → `.result.tab`, `.result.root_pane` |
| Rename a tab | `ssh vps '~/.local/bin/herdr tab rename <tab-id> <label>'` |
| Start an agent in a shell pane | `ssh vps '~/.local/bin/herdr agent start <name> --kind claude --pane <pane-id> [-- <agent-args>]'` (kinds include `claude`, `codex`, `opencode`, `cursor`; default timeout 30000 ms) |
| Send a prompt | `ssh vps '~/.local/bin/herdr agent prompt <name-or-pane> <text> --wait --timeout <ms>'` |
| Wait for a state | `ssh vps '~/.local/bin/herdr agent wait <target> --until working --timeout <ms>'` |

Notes for writes:

- `<name>` must match `[a-z][a-z0-9_-]{0,31}` and be unique among live agents on that server (herdr skill).
- A prompt or path passed through `ssh vps '…'` goes through the remote shell. Quote it for the remote side (for example `printf %q` locally), or pipe a script over stdin. The 0.9.1 `--machine` path avoids this.
- `claude` is found in a login shell on the VPS, and Herdr panes start interactive shells, so `agent start --kind claude` should find it. Unverified until tried.

## VPS to Mac

Not possible today. What exists:

- The Mac's SSH server is not listening: `nc -z 127.0.0.1 22` exits 1 [mac], so Remote Login is off.
- No Tailscale on either machine (`which tailscale` [mac] and `command -v tailscale` [vps] both empty; no Tailscale app in `/Applications` [mac]). The Mac has Cloudflare WARP and OrbStack installed [mac], neither set up as a path in.
- The VPS has no `~/.ssh/config` and no saved Herdr machines [vps].
- The Mac's Herdr socket is local only, like the VPS's.

What it would take (none set up):

1. **Mac always checks.** Keep the Mac as the one that looks at the VPS, never the reverse. Needs nothing.
2. **SSH into the Mac.** Turn on Remote Login on the Mac, give it an address the VPS can reach (Tailscale on both, or a reverse tunnel the Mac opens with `ssh -R 2222:localhost:22 vps`), authorize the VPS's key `~/.ssh/id_ed25519.pub` on the Mac, then `herdr machine add` on the VPS or plain `ssh mac ~/.local/bin/herdr …`.
3. **Forward only the Herdr socket.** OpenSSH can forward a Unix socket (`ssh -R ~/.herdr-mac.sock:~/.config/herdr/herdr.sock vps`), and the VPS could point `HERDR_SOCKET_PATH` at it. This needs no Mac sshd, but it lives only as long as the Mac holds the SSH connection open, and it gives the VPS full control of the Mac's Herdr. Unverified: Herdr docs do not describe it.

## Finding the host

- **Herdr's catalog.** `herdr machine list --json` [mac] returns `id`, `label`, `target`, `session`, `enabled`, `selected`. The file behind it is `~/.local/state/herdr/client/endpoints.json` (`{"version":1,"ssh":[…]}`) [mac]. Profiles hold only id, label, SSH target, remote session and enabled state; no credentials (`connecting-machines.mdx`). A skill can read the target with `herdr machine list --json | jq -r '.[] | select(.label=="Yahya'"'"'s VPS") | .target'` rather than hard-coding it. Prefer the CLI over the file; the file format is not documented as stable.
- **SSH config.** `~/.ssh/config` [mac] only contains OrbStack's `Include ~/.orbstack/ssh/config`. There is no alias for the VPS; the target is the raw `<vps-user>@<vps-host>`. Adding a `Host vps` alias is an option, but Herdr's profile would still hold whatever target it was added with.
- **Herdr config.** `~/.config/herdr/config.toml` [mac] holds UI settings only, not machines.

## Worktrees and tooling on the VPS

Repos under `~/Developer/yahyabedirhan/` [vps], all cloned over SSH from `git@github.com:yahyabedirhan/<repo>.git`:

| Repo | VPS path | Branch on 2026-09-25 | Worktrees |
| --- | --- | --- | --- |
| job-search (this vault) | `~/Developer/yahyabedirhan/job-search` | `master` | main checkout only |
| shipyard | `~/Developer/yahyabedirhan/shipyard` | `build/shipyard-core-0.0.x` | main checkout only |
| skills | `~/Developer/yahyabedirhan/skills` | `main` | main checkout only |
| steal | `~/Developer/yahyabedirhan/steal` | `main` | main checkout only |

Also `~/Developer/open-source/ghbar` [vps]. Paths differ from the Mac: the vault is at `~/Documents/Vault/job-search` on the Mac and `~/Developer/yahyabedirhan/job-search` on the VPS; `tarmy-empire`, `sand` and `workstation` exist on the Mac but not in the VPS's `~/Developer/yahyabedirhan` [mac, vps]. Map repos by their `origin` URL, not by path.

Tools (`command -v` over plain SSH, then `bash -lc` [vps]):

| Tool | VPS |
| --- | --- |
| `git` | `/usr/bin/git`; user.name/email set |
| `gh` | `/usr/bin/gh`, logged in as `yahyabedirhan`, git protocol ssh |
| `claude` | `~/.local/bin/claude` (login shell only) |
| `herdr` | `~/.local/bin/herdr` 0.9.0 (login shell only) |
| `swift` | `~/.local/share/swiftly/bin/swift` (login shell only; issue [#13](https://github.com/yahyabedirhan/skills/issues/13) reported it missing) |
| `node`, `pnpm` | via nvm, Node 24.21.0 |
| `codex`, `opencode`, `cursor-agent` | missing |
| `treehouse` | missing (no binary, no `~/.config/treehouse`) |

On the Mac `treehouse` is at `~/go/bin/treehouse` [mac], and `init-effort-with-herdr` forbids `git worktree add` and `herdr worktree create` in favour of it (`~/.agents/skills/init-effort-with-herdr/SKILL.md`). That rule cannot hold on the VPS until treehouse is installed there. Skills installed on the VPS (`~/.claude/skills`, `~/.agents/skills` [vps]) include `init-effort-with-herdr`, `orchestrate-with-herdr` and `orchestrating` but **not** `herdr`.

Getting a pushed branch into a worktree on the VPS without treehouse (not run):

```bash
ssh vps 'git -C ~/Developer/yahyabedirhan/<repo> fetch origin <branch> &&
  git -C ~/Developer/yahyabedirhan/<repo> worktree add ~/Developer/worktrees/<repo>/<effort> <branch>'
ssh vps '~/.local/bin/herdr worktree open --cwd ~/Developer/yahyabedirhan/<repo> --path ~/Developer/worktrees/<repo>/<effort> --label <effort> --no-focus'
```

`git worktree add <path> <branch>` creates a local branch tracking `origin/<branch>` when only the remote branch exists. `herdr worktree create --cwd <repo> --branch <name> --base <ref> --path <path>` does both steps in one, but puts the worktree outside any pool (`herdr worktree create --help` [mac]). The worktree folder is a suggestion; nothing on the VPS defines one yet.

## Safe-handover checks

Read-only checks to run from the Mac before starting a second orchestrator on the same branch:

1. **Find the agent in that checkout.** `ssh vps '~/.local/bin/herdr agent list'` and match `cwd` against the worktree path. Agent names may be unset (the shipyard orchestrator had none [vps]), so match on `cwd` and `workspace_id`, not on a name.
2. **Its state.** `agent_status` of `idle` or `done` means ready for input, `working` means busy, `blocked` means waiting on an approval or question (herdr skill). `unknown` does not prove it stopped. No agent in the pane list for that cwd means none is running there.
3. **What it last said.** `ssh vps '~/.local/bin/herdr agent read <pane> --source recent-unwrapped --lines 60'`. On 2026-09-25 this showed the shipyard orchestrator reporting commit `0646a5a` pushed and a clean tree [vps].
4. **Clean tree.** `ssh vps 'git -C <worktree> status --porcelain'` is empty.
5. **Nothing unpushed.** Compare local `HEAD` with the live remote, not the cached tracking ref:

   ```bash
   ssh vps 'cd <worktree> && git rev-parse HEAD && git ls-remote origin refs/heads/<branch>'
   ```

   Equal SHAs mean pushed. If they differ, `git log @{u}..HEAD` only shows commits missing from the last fetch. A `git fetch origin <branch>` first makes it exact; it updates remote-tracking refs only (issue [#16](https://github.com/yahyabedirhan/skills/issues/16) counts it as a read). Worked example [vps]: the shipyard checkout was at `0646a5a`, `git status -sb` showed it level with `origin/build/shipyard-core-0.0.x`, yet `git ls-remote` returned `d831d00` because the Mac had pushed since. The VPS checkout was behind, not ahead, and had no unpushed work. `git status` alone would have claimed it was up to date.
6. **Other checkouts of the branch.** `ssh vps 'git -C <repo> worktree list'` shows every worktree and its branch.

Stopping the old agent, closing its workspace, or removing its worktree are writes and stay behind an explicit ask (issues [#13](https://github.com/yahyabedirhan/skills/issues/13) and [#16](https://github.com/yahyabedirhan/skills/issues/16)).

## Notifications

- **Herdr's command.** `herdr notification show <title> [--body TEXT] [--position …] [--sound none|done|request]` sends through the server's `[ui.toast]` delivery: `herdr` (in-app toast), `terminal` (outer terminal notification, "also works over SSH"), `system` (the OS notification service), or `off` (`cli-reference.mdx`, `configuration.mdx`). The response says `shown`, `disabled`, `rate_limited`, `no_foreground_client` or `busy`; terminal and system delivery are "best-effort through the current foreground attached Herdr client" (`socket-api.mdx`).
- **Defaults make it silent today.** `ui.toast.delivery` defaults to `off` (`config-reference.json`). The VPS has no `~/.config/herdr/config.toml` [vps], so it runs on that default and a `notification show` run on the VPS should return `disabled`. The Mac's config sets `delivery = "off"` and `[ui.sound] enabled = false` [mac] as well.
- **Agent state still crosses over.** The Mac window keeps receiving the VPS's agent states and notifications while another machine is selected (`connecting-machines.mdx`), so a VPS orchestrator going `done` or `blocked` shows in the Mac's sidebar and agent list with no setup.
- **Issue [#9](https://github.com/yahyabedirhan/skills/issues/9)'s `osascript` route does not work from the VPS**: it is Linux, and `notify-send` is missing too [vps]. Unverified: whether a `terminal` or `system` notification raised on the VPS server is shown by the Mac client when it is connected as a saved machine rather than attached with `herdr --remote`. Test: set `delivery = "terminal"` in the VPS config, run `herdr server reload-config` there, run `herdr notification show test` on the VPS with the Mac window on Local, then on the VPS, and record the `reason` and what appears.
- **A Mac-side alternative.** A Mac agent can watch the VPS with `ssh vps '~/.local/bin/herdr agent wait <pane> --until done --until blocked'` and raise the notification itself with `osascript`. Not tested.

## Open questions

- TODO: Upgrade both machines to Herdr 0.9.1 so skills can use `herdr --machine "Yahya's VPS" …` instead of `ssh` plus a full path and remote-shell quoting. Needs the user's go-ahead; updating a server asks before stopping its panes.
- TODO: Decide the worktree tool on the VPS: install treehouse there, or allow `git worktree add` on the VPS only, and pick the worktree root folder.
- TODO: Decide whether to add a `Host vps` alias in `~/.ssh/config` on the Mac, or read the target from `herdr machine list --json` every time.
- TODO: Run the notification test above to learn whether a VPS-side notification can reach the Mac, and which `delivery` value issue [#9](https://github.com/yahyabedirhan/skills/issues/9) should use.
- TODO: Confirm `herdr agent start --kind claude` finds `claude` in a new VPS pane (it is only on the login-shell `PATH`).
- TODO: Decide whether VPS to Mac is needed at all; if so, pick Remote Login plus Tailscale, or a reverse tunnel.
- TODO: Install the `herdr` skill on the VPS if VPS agents are to drive Herdr (it is missing from `~/.claude/skills` and `~/.agents/skills` there).
- TODO: Pull the vault on the VPS before an effort starts there: its `master` was at `bca4a0cc` while the Mac's was at `17fd65e8` [vps, mac].
