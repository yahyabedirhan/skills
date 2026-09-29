# What an agent on the VPS can do compared with the Mac

Facts for [Research: what an agent on the VPS can do compared with the Mac (#71)](https://github.com/yahyabedirhan/skills/issues/71), under [Spec: research cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45). Researched 2026-09-29. It extends [Herdr across the Mac and the VPS](herdr-vps.md) (the machine model, the SSH command reference, safe-handover checks, VPS to Mac) and doesn't repeat it; the harness facts behind the environment section are in [What each harness can and can't do](harness-capabilities.md).

Evidence tags:

- **[vps]** a read-only command run on the VPS on 2026-09-29, over `ssh -o BatchMode=yes <vps-host>` into a login shell (see the Exploration log).
- **[mac]** a read-only command run on the Mac on 2026-09-29.
- **[probe]** the one throwaway Herdr workspace opened on the VPS and closed again (Exploration log, step 6).
- **[doc]** official documentation, linked inline. Herdr docs are cited by file name at a release tag, under `https://raw.githubusercontent.com/herdrdev/herdr/<tag>/docs/next/website/src/content/docs/`; release notes at `https://github.com/herdrdev/herdr/releases/tag/<tag>`.
- **Unverified** marks a claim with no primary source or probe behind it.

Versions seen: Herdr 0.9.0 client and server on both machines [mac, vps]; Herdr's latest release is **0.9.2, published 2026-09-29** ([releases](https://github.com/herdrdev/herdr/releases)). Claude Code 2.1.284 on the Mac, 2.1.283 on the VPS [mac, vps].

## At a glance

| Capability | Mac | VPS today | What closes the gap |
|---|---|---|---|
| Machine | macOS 26.5, arm64, 11 cores, 18 GB [mac] | Ubuntu 26.04 LTS x86_64 on a small Hetzner instance: 2 vCPU, 3.8 GB RAM (about 2.4 GB available), 26 GB disk free [vps] | Sizing is [VPS sizing](cloud-agents-vps-sizing.md) (#72). |
| Headless browser | Google Chrome and Safari installed; Playwright browser cache present [mac] | **Can't run one.** Playwright's `chromium_headless_shell-1243` is cached (266 MB), but its binary is missing 15 shared libraries (`libnss3`, `libatk-1.0`, `libgbm`, `libX11`, `libasound`, …) [vps]. No Chrome, Chromium, Firefox or Xvfb; `apt` offers `chromium-browser` only as a snap shim [vps]. | Either `npx playwright install-deps chromium` (apt as root, [Playwright: browsers](https://playwright.dev/docs/browsers#install-system-dependencies)), or run the browser in Docker, which the user can already use: `mcr.microsoft.com/playwright:<version>-resolute` is the Ubuntu 26.04 image, run with `--init --ipc=host` ([Playwright: Docker](https://playwright.dev/docs/docker)). Both are installs: proposed experiments. |
| Desktop browser / browser extension | Chrome, which Claude Code can drive through the Claude in Chrome extension (unverified here beyond the tool being offered to Mac sessions) | None: no display (`DISPLAY` and `WAYLAND_DISPLAY` unset) [vps] | Not worth closing on a server; use headless. |
| Web access | Yes | **Yes**, outbound HTTPS works: `example.com`, `api.github.com`, `registry.npmjs.org` answer 200 [vps] | Nothing. |
| Running scripts | bash, zsh, Python, Node, Docker, … [mac] | bash, Python 3.14, Node 24 with npm, pnpm and npx (nvm), Swift, Docker 29 (user is in the `docker` group), curl, wget, tmux [vps]. Missing: `jq`, `rg`, `fd`, Go, Rust, Bun, Deno [vps] | Install what a project needs; `jq` matters because skills and prior research parse Herdr's JSON with it (Python works as a stand-in, see the Exploration log). |
| File system | Home folder, local disk | Own home folder, 26 GB free, open-file limit 1024 [vps]. The user is in the `sudo` group [vps], so root is possible with a password (not tried). | Nothing for normal work. |
| Git and worktrees | git, `treehouse` for pooled worktrees [mac] | git 2.53, `user.name`/`email` set [vps]. Every repo is a main checkout with no extra worktrees [vps]. **No `treehouse`** [vps]. | Install treehouse (needs Go, also missing) or allow `git worktree add` / `herdr worktree create` on the VPS only (open since [herdr-vps.md](herdr-vps.md#open-questions)). |
| GitHub auth | `gh` logged in | **Yes**: `gh` 2.46 logged in, git protocol SSH; `ssh -T git@github.com` authenticates [vps] | Nothing. Pushes and pull requests work as on the Mac (not tried: they'd be writes). |
| Harnesses | Claude Code, Codex, opencode, Cursor CLI [mac] | **Claude Code only.** No `codex`, `opencode`, `cursor-agent`, `gemini`, `copilot`, `amp`, `grok` [vps] | Install the preferred agent, or fall back to `claude` (issue #13 already proposes that). |
| Herdr | 0.9.0 client and server | 0.9.0 server, running, 5 workspaces, 1 idle Claude Code agent; no saved machines of its own [vps] | Upgrade both to 0.9.2 for `--machine` forwarding and `machine status` (see *Herdr across machines*). |
| Agents see they're in Herdr | `HERDR_ENV=1` in panes | `HERDR_ENV=1` in a new pane, and `claude`, `herdr`, `gh`, `node` are all on its `PATH` [probe] | Nothing: the gap noted in herdr-vps.md (tools only on the login-shell `PATH`) affects SSH commands, not Herdr panes. |
| Skills | The repo's current skills | An older set: 13 in `~/.claude/skills`, 12 in `~/.agents/skills`; no `herdr`, `handover`, `handover-to-herdr`, `set-up-machine` [vps]. Its skills clone is on `main` at an older commit, clean, behind `origin/main` [vps]. | Pull the clone and reinstall with `npx skills`; set-up-machine installs the skills repo itself once #66 merges (see *The environment*). |
| Rule table, pre-tool hook, memory off | Not applied yet either: no `~/.config/agents/` on the Mac [mac] (set-up-machine is on the unmerged PR #66) | Hand-written: `~/.claude/settings.json` has 30 deny rules, no `PreToolUse` hook, `autoMemoryEnabled` unset (so memory is on), and 4 project memory folders exist [vps]. No `~/.config/agents/`, no `~/.claude/CLAUDE.md` [vps]. | Run set-up-machine on the VPS after #66 merges (see *The environment*). |
| Notifications | `osascript` (proven, issue #9); Herdr toasts off (`delivery = "off"`) [mac] | No `notify-send`, no display [vps]. `herdr notification show` on the VPS returned `shown` [probe], where it showed is unknown. Claude Code has mobile push on (`agentPushNotifEnabled: true`) [vps], which works only while Remote Control is connected ([docs](https://code.claude.com/docs/en/remote-control#mobile-push-notifications)). | Claude Code Remote Control plus push from the VPS, or a Mac-side watcher (`agent wait` over SSH or `--machine`, then `osascript`). See *Notifications*. |
| Reach the other machine | Mac → VPS over SSH, no prompt | VPS → Mac: not possible (herdr-vps.md) | Unchanged; herdr-vps.md lists the options. |

## Capabilities in detail

### Headless browser

- The cached headless shell was downloaded by a Playwright install on 2026-09-23 (`~/.cache/ms-playwright/chromium_headless_shell-1243`, plus `ffmpeg-1011`) [vps]. No system dependencies were installed with it: `ldd` on `chrome-headless-shell` lists 15 libraries `not found` [vps]. The package list shows only `libxkbcommon0` of the usual set [vps].
- Playwright's own fix is `npx playwright install-deps` or `install --with-deps`, which runs the system package manager and "will attempt to become a root" ([Playwright: browsers](https://playwright.dev/docs/browsers#install-system-dependencies)). `--only-shell` keeps the download to the headless shell, enough for headless use ([same page](https://playwright.dev/docs/browsers#chromium-headless-shell)).
- The no-root route is Docker: the user is in the `docker` group and Docker 29 runs two containers already [vps]. Playwright's official image comes in an Ubuntu 26.04 variant (`:v<version>-resolute`); Playwright advises `--ipc=host` ("Without it, Chromium can run out of memory and crash") and `--init`, and can serve browsers to a client on the host with `run-server --port 3000` ([Playwright: Docker](https://playwright.dev/docs/docker)). Pulling the image is an install, so it's a proposed experiment.
- Memory: about 2.4 GB is available [vps]. How many browsers fit next to agents is in [VPS sizing](cloud-agents-vps-sizing.md).
- **Correction to [VPS sizing](cloud-agents-vps-sizing.md):** its hardware table says the cached headless shell means "a headless browser needs no install to try". The `ldd` check above shows it can't start without the missing system libraries (or a container), so trying one does need an install.

### Web access, scripts and file system

- Outbound HTTPS works to the web, GitHub and npm [vps]. `api.anthropic.com` answers (404 on its root), so the harness reaches its API [vps].
- Scripts: see the table. Node, npm, pnpm and npx come from nvm, which `~/.bashrc` loads above its interactive guard, and `~/.local/bin` is added by `~/.profile` and `~/.bashrc` [vps]; a login or interactive shell gets both. That is why `bash -lc` is needed over plain SSH (the handoff's finding) and why a Herdr pane has everything [probe].
- The login shell is bash [vps]. User systemd runs, with lingering off (`Linger=no`) [vps], so a user service would stop at logout; Herdr's own server already survives, running for weeks [vps].

### Git, worktrees and GitHub

- `gh auth status` shows one logged-in account, git protocol SSH; `ssh -T git@github.com` authenticates as that account [vps]. The identity is the same account as on the Mac (unverified beyond the user name matching).
- Five repos, each a main checkout only (`git worktree list` has one line each) [vps]. The skills clone is clean, on `main`, behind `origin/main` (its `HEAD` differs from `git ls-remote origin refs/heads/main`) [vps]; the check from herdr-vps.md's *Safe-handover checks* is what showed it.
- No worktree tool: see the table. Herdr's own `worktree create` exists on 0.9.0 and is forwarded by `--machine` from 0.9.1 (`cli-reference.mdx` at v0.9.1, "Saved SSH machines" [doc]).

### Harnesses

- Only Claude Code is installed [vps]. Its settings carry a `SessionStart` hook that reports agent state to Herdr (`~/.claude/hooks/herdr-agent-state.sh`), two plugins, and `remote.defaultEnvironmentId`, the default cloud environment for `claude --cloud` ([settings reference](https://code.claude.com/docs/en/settings-reference)) [vps].
- `claude --help` on the VPS offers `--bg` background sessions, `--remote-control` and `--teleport` [vps]. Those belong to ticket #69 (Claude Code in the cloud) and #73 (delegating and watching); here they matter only as what the VPS's Claude Code can do: Remote Control lets the maintainer drive a VPS session from claude.ai or the phone, and "To keep a session running on a remote machine after you disconnect from SSH, start it inside `tmux` or `screen`", or a Herdr pane ([Remote Control](https://code.claude.com/docs/en/remote-control#limitations)). Not tried: starting one registers a session with Anthropic.

## Herdr across machines

What Herdr's releases after 0.9.0 offer for driving one machine from another, and whether it was tried here. "Tried" means run in this research on the VPS; everything forwarded needs an upgrade, which the safe zone forbids.

| Feature | Since | Source | Tried |
|---|---|---|---|
| Saved machines: `machine add/list/rename/disable/enable/remove`; a profile holds id, label, SSH target, session, enabled | 0.9.0 | `connecting-machines.mdx` at v0.9.0 [doc] | `machine list --json` read on both [mac, vps] (the VPS has none) |
| **CLI forwarding** `herdr --machine <label-or-id> …`: `workspace`, `worktree`, `tab`, `pane`, `notification`, `agent` (not `attach`), `api snapshot`, `status server`, `server stop/reload-config`, plugin commands; JSON over non-interactive SSH, "API payloads are not interpolated into the SSH shell command"; "No open TUI is required"; never falls back to Local; needs the new version on both ends | 0.9.1 | [v0.9.1 notes](https://github.com/herdrdev/herdr/releases/tag/v0.9.1); `cli-reference.mdx` at v0.9.2, "Saved SSH machines" [doc] | No (0.9.0 on both; herdr-vps.md recorded `unknown option: --machine`) |
| `--machine` rules: selector is an enabled profile ID or a unique, case-sensitive label, "not an arbitrary SSH hostname"; `--current` "cannot refer to the caller's local pane"; remote worktree paths must be absolute or `~/…`; one machine per call, no combined listings | 0.9.1 | `cli-reference.mdx` at v0.9.2 [doc] | No |
| Fewer SSH connections for repeated `--machine` commands; remote OS and binary path cached per machine | 0.9.2 | [v0.9.2 notes](https://github.com/herdrdev/herdr/releases/tag/v0.9.2); `connecting-machines.mdx` at v0.9.2, "Updates and saved data" [doc] | No |
| `herdr machine status [<label-or-id>] [--json]`: "fresh, noninteractive checks"; `reachable` means the remote server is available now | 0.9.2 | [v0.9.2 notes](https://github.com/herdrdev/herdr/releases/tag/v0.9.2); `connecting-machines.mdx` at v0.9.2, "Recovering SSH authentication" [doc] | No |
| `herdr machine reconnect`: finishes SSH authentication (MFA included) in a terminal; never installs or updates; open clients recheck failed machines every 30 s | 0.9.2 | same | No |
| Interactive `machine add` discovers running remote sessions; `--label` optional (defaults to the SSH host) | 0.9.2 | same | No (would change the Mac's catalog) |
| Remote attach `herdr --remote <target>`: the remote server owns the panes, the local client draws; the command Herdr points to for setup that needs a prompt | before 0.9.0 | `persistence-remote.mdx`; `connecting-machines.mdx` at v0.9.2, "Connection problems" [doc] | No (interactive) |
| Cross-machine visibility in one window: non-selected machines keep sending workspace info, agent states and notifications | 0.9.0 | `connecting-machines.mdx` [doc] | Seen before (herdr-vps.md) |
| `notification show` through the server's `[ui.toast]` delivery (`off`, `herdr`, `terminal` "also works over SSH", `system`); terminal and system "best-effort through the current foreground attached Herdr client" | 0.9.0 | `configuration.mdx`, `socket-api.mdx` at v0.9.2 [doc] | **Yes** on the VPS: returned `shown` [probe]; see *Notifications* |
| SSH agent forwarding survives reconnects: panes get a stable agent address (needs an updated **server**; `ForwardAgent yes` is the user's to set) | 0.9.1–0.9.2 | `connecting-machines.mdx` at v0.9.2, "Connection problems"; v0.9.2 notes [doc] | No |
| SSH compression; only changed rows sent for scrolling output | 0.9.2 | v0.9.2 notes [doc] | No |
| New panes set `TERM_PROGRAM=herdr` and drop inherited Claude Code, Codex and terminal session markers | 0.9.2 | v0.9.2 notes; `cli-reference.mdx` at v0.9.2 [doc] | Consistent: a 0.9.0 pane had `TERM_PROGRAM` unset [probe] |
| Agents may report their own resume command, so any agent can be restored after a server restart | 0.9.2 | v0.9.2 notes; `add-herdr-support.mdx` [doc] | No |
| On Linux with logind, Herdr saves the layout before host shutdown; 48 layout snapshots kept | 0.9.2 | `session-state.mdx` at v0.9.2 [doc] | No |
| `pane split` with no target splits the calling pane inside Herdr; `--current` errors without `HERDR_PANE_ID` | 0.9.1 | `cli-reference.mdx` at v0.9.2 [doc] | No |
| `herdr update` lists running servers still on the old version and reminds you to update saved SSH machines ("Run `herdr update` on each machine") | 0.9.2 | `install.mdx` at v0.9.2 [doc] | No |

### What an upgrade to 0.9.2 would change

- **One command shape for the VPS.** `herdr --machine "<vps-label>" agent list` replaces `ssh <vps-host> "bash -lc 'herdr …'"`: no login-shell wrapper, no full path, no remote-shell quoting of prompts, no host in skill text (the label or profile ID comes from `herdr machine list --json`). It answers #13's and #16's "where is the host named" question with Herdr's own catalog.
- **A readiness check without a TUI**: `herdr machine status "<vps-label>" --json` before any handover.
- **What it doesn't change**: IDs and agent names stay per server; `--current` still can't point across machines; one machine per call. VPS to Mac still needs SSH into the Mac.
- **Cost**: updating a running server asks before stopping it and its pane processes (default No); live handoff is experimental ([connecting-machines.mdx at v0.9.2, "Updates and saved data"](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.2/docs/next/website/src/content/docs/connecting-machines.mdx)). The VPS has an idle Claude Code agent in a pane that a restart would end [vps].

### What can be probed now, on 0.9.0

With throwaway workspaces, over `ssh … bash -lc 'herdr …'`: creating and closing a workspace, running a command in its pane and reading its output, `notification show` (done here, step 6), and `agent start --kind claude` in a throwaway pane (not done: it starts a Claude Code session; proposed below). Everything in the table marked 0.9.1 or 0.9.2 needs the upgrade first.

## Notifications

- The VPS has no desktop notifier and no display [vps], so the Mac's `osascript` route (issue #9) can't run there.
- **Herdr**: the VPS has no `~/.config/herdr/config.toml` [vps], and Herdr 0.9.0's config reference gives `ui.toast.delivery` a default of `"off"` (`docs/versions/0.9.0/website/src/data/config-reference.json` at v0.9.2 [doc]). herdr-vps.md therefore predicted `disabled`. Yet `herdr notification show "probe-71"` on the VPS returned `{"shown":true,"reason":"shown"}` [probe], and the server log records the request as `ok` [vps]. Where it appeared is unknown: the Mac's own config has `delivery = "off"` [mac]. **Unverified**; it contradicts the documented default.
- **Claude Code**: mobile push is on in the VPS's settings [vps]; pushes need an active Remote Control connection, and Claude decides when to push (task done, or a decision needed), with two `/config` toggles ([Remote Control: mobile push](https://code.claude.com/docs/en/remote-control#mobile-push-notifications)). This is the one route that reaches the maintainer from the VPS with no Mac involved.
- **Mac-side watcher**: a Mac agent can wait on a VPS agent (`agent wait <pane> --until done` over SSH, or with `--machine` after the upgrade) and raise `osascript` itself (herdr-vps.md; not tested).

## The environment on the VPS

How the skills, the rule table, the pre-tool hook, memory-off and the shared global instructions would reach the VPS the same way as the Mac: through **set-up-machine**, which "runs on macOS and Linux" and needs only Python 3.9+ (`skills/set-up-machine/SKILL.md` on the effort branch).

What the VPS has for it:

- Python 3.14 [vps]: enough.
- `npx` (for the `skills` CLI) from nvm, on the login and interactive `PATH` only [vps]. Run set-up-machine from a Herdr pane or a login shell.
- Claude Code is the only harness [vps], so the plan would cover Claude Code alone; set-up-machine finds a harness by its config folder or its program on `PATH` (`SKILL.md`).
- `~/.agents/.skill-lock.json` exists [vps], so the `skills` CLI has installed here before.

What's missing today:

1. **set-up-machine isn't on `main`.** It arrives with the open PR #66 ("Every harness and project is set up and audited from the skills"). Until it merges, neither machine has it applied: no `~/.config/agents/` on the Mac either [mac].
2. **The VPS's skills clone is behind `origin/main`** and its installed skills are an older set [vps].
3. **Hand-made rules and memory.** 30 deny rules in `~/.claude/settings.json`, no pre-tool hook, memory on with 4 memory folders [vps]. set-up-machine's plan would list the table's rules as `added` or `present`, the hand-made ones it doesn't know as `extra` (kept), memory as off, and each memory file as `removed`, backed up first (`SKILL.md`, steps 3–4). Moving any memory worth keeping comes first.
4. **No shared global instructions**: no `~/.config/agents/AGENTS.md` and no `~/.claude/CLAUDE.md` [vps], so a VPS agent today gets no personal instructions at all.

The **Linux container check** (`scripts/tests/linux/run.sh`) builds a Debian bookworm image from `node:22-bookworm` with all four harnesses installed the official way and never logged in, installs the skills from the repo with `npx skills add … -g -a claude-code codex opencode cursor`, then runs plan, apply, plan and the rule probes in a throwaway container (`run.sh`, `in-container.sh`, `Dockerfile` on the effort branch). It proves the scripts on Linux. How the VPS differs from that image: Ubuntu 26.04 instead of Debian 12, Node 24 from nvm instead of a system Node on `PATH`, only Claude Code installed, an existing hand-made setup rather than a fresh home, and a real login. The check can run on the VPS itself (Docker is there), but building the image downloads packages: a proposed experiment.

The steps, once #66 merges (not run: each writes):

```bash
git -C <skills-clone> pull --ff-only
npx skills add yahyabedirhan/skills -g --skill '*'          # or let set-up-machine's plan install it
python3 ~/.agents/skills/set-up-machine/scripts/set_up_machine.py plan
python3 ~/.agents/skills/set-up-machine/scripts/set_up_machine.py apply --plan-id <id>   # after the maintainer approves
python3 ~/.agents/skills/set-up-machine/scripts/set_up_machine.py plan                    # audit: "No changes."
```

The `--home <dir>` option runs plan against a copy of a home folder and starts no harness (`SKILL.md`), so a read-only dry run on a scratch copy is possible before the real one. Copying the home is itself a write under `~`, so it too waits for a go-ahead.

## Permissions on the other machine

The line locally is: read freely, ask before anything that closes, stops, messages or removes. It carries over unchanged. The three blocked build tickets (#13, #15, #16) each state part of it; together:

| Action on the other machine | Examples | Without asking? |
|---|---|---|
| Read Herdr state | `workspace list`, `tab list`, `pane list`, `agent list`, `agent get`, `agent read`, `api snapshot`, `status`, `machine list`, `machine status` (0.9.2) | **Yes** (#16) |
| Read git state | `git status`, `git log`, `git worktree list`, `git ls-remote`, `git fetch` (updates remote-tracking refs only; #16 counts it as a read) | **Yes** (#16) |
| Start what the maintainer chose | a workspace, a tab and an orchestrator for a handover to the VPS the maintainer picked | **Yes, as that step** (#13) |
| Throwaway items of one's own | a workspace or tab it created, then closed | Yes, when named so no other agent touches it (this research's `probe-71-` prefix) |
| Message a running agent | `agent prompt`, `agent send-keys` to an agent it didn't start | **Ask** (#13, #16) |
| Close or stop | `workspace close`, `tab close`, `pane close`, `agent` stop keys, `server stop` (forwarded by `--machine` from 0.9.1) | **Ask** (#16) |
| Remove | a worktree, a branch, a machine profile (`machine remove/disable`) | **Ask** (#13, #16) |
| Change the machine | install, update or restart Herdr, `machine add`, config edits, set-up-machine's apply | **Ask** (#13; the spec's safe zone) |

Questions carried from the build tickets, with what this research adds:

- **Where the host is named** (#13, #16): Herdr's catalog already holds it; after the upgrade, skills name the machine by its label through `--machine` and never see the host.
- **Is the old orchestrator idle, is its branch pushed** (#15, #16): herdr-vps.md's safe-handover checks work over SSH today [vps: the `ls-remote` comparison ran]; they become `--machine` calls after the upgrade.
- **The preferred agent may be missing** (#13): only Claude Code is on the VPS [vps]; a handover falls back to `claude`.
- **The toolchain may be missing** (#13): Swift is now present [vps] (#13 recorded it missing); `jq`, `treehouse`, Go and Rust aren't.
- **Notifications from a VPS orchestrator** (#13): see *Notifications*; no route is proven yet.
- **A gap in the rules**: `herdr --machine <vps> server stop` stops the remote server and every agent in it, from one local command. No row in set-up-machine's `rules.json` mentions `herdr` today; a row for `herdr … server stop` (and `workspace close --group`) at `ask` would hold the line mechanically. Proposed below.

## Where the desktop app fits

- **Driving Herdr from the desktop app.** A desktop-app session runs outside any Herdr pane, so `HERDR_ENV` is unset; the `herdr` CLI still reaches the Mac's server through its socket. The repo's **handover-to-herdr** already relaxes the gate this way: "Check that `herdr status` reaches a server; `HERDR_ENV` only says whether this session runs in a pane", with explicit IDs, `--no-focus` and never `--current` (`skills/handover-to-herdr/SKILL.md`). Herdr's own skill keeps the stricter rule: stop unless `HERDR_ENV=1` (`agent-skill.mdx` at v0.9.2 [doc]).
- **How the gate relaxes for the VPS.** From the desktop app (or any caller outside Herdr), the VPS is reached today with `ssh … bash -lc 'herdr …'`, whose readiness check is `herdr status` on the VPS. After the upgrade, `--machine` "does not need an open TUI" and "`--current` cannot refer to the caller's local pane" ([cli-reference.mdx at v0.9.2](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.2/docs/next/website/src/content/docs/cli-reference.mdx)), so the check becomes `herdr machine status "<vps-label>" --json` reporting reachable, plus the same targeting rules. `HERDR_ENV` isn't part of either.
- **Desktop SSH sessions.** The desktop app can run Claude Code on a Linux or macOS machine over SSH with the app as the interface; it "installs Claude Code on the remote machine automatically the first time", and the session "reads `~/.claude/skills/` from the remote host's home directory" ([desktop: SSH sessions](https://code.claude.com/docs/en/desktop#ssh-sessions)). So a desktop SSH session on the VPS gets the VPS's skills and settings, not the Mac's, which is one more reason to set the VPS up with set-up-machine. Such a session isn't in a Herdr pane on the VPS, so Herdr doesn't list it as an agent (unverified; it follows from Herdr detecting agents per pane). Not tried: adding a connection changes the app's config.
- **Remote Control** makes the reverse true: a Claude Code session in a VPS Herdr pane can be steered from claude.ai/code or the phone ([Remote Control](https://code.claude.com/docs/en/remote-control)).

## Open questions

Each is a proposed experiment that needs something the safe zone forbids, or the maintainer.

- **Upgrade both machines to Herdr 0.9.2** (`herdr update` on each; the VPS server restart ends its panes, so pick a moment with no agent working). Then run `herdr --machine "<vps-label>" agent list`, `machine status --json`, and a `probe-` workspace create, `pane run`, `pane read` and close through `--machine`, and record the output shapes for #13 and #16.
- **Where did the VPS notification go?** Repeat `herdr notification show "probe" --body test` on the VPS while the maintainer watches the Mac window, once with the VPS selected and once with Local selected, and read `ui.toast.delivery` from the VPS server's effective config if Herdr exposes it. Settles whether 0.9.0's default is really `off`.
- **Headless browser in Docker**: pull `mcr.microsoft.com/playwright:<version>-resolute` on the VPS and run one headless page load with `--init --ipc=host`; record memory use next to a running Claude Code agent. Or, with root, `npx playwright install-deps chromium` and rerun `ldd`. #72 needs the memory figure.
- **`agent start --kind claude` in a throwaway VPS pane**, then `agent get` and exit: confirms Herdr detects Claude Code there (the pane's `PATH` already has `claude` [probe]). Starts a session, so it waits for a go-ahead.
- **Claude Code Remote Control and push from the VPS**: start `claude --remote-control` in a throwaway Herdr pane on the VPS, ask for "notify me when done", and see whether the phone gets a push. Registers a session with Anthropic.
- **set-up-machine on the VPS** after #66 merges: pull the skills clone, run plan (read-only apart from briefly starting Claude Code to list its tools) and show the maintainer the diff; apply only on approval. Decide first which of the 4 memory folders to keep.
- **Worktree tool on the VPS** (from herdr-vps.md): install treehouse (and Go), or allow `herdr worktree create` / `git worktree add` there.
- **A rule-table row for disruptive Herdr commands** (`herdr … server stop`, `workspace close --group`, and their `--machine` forms) at `ask`, since `--machine` makes them one local command away. A change to #66's table, for the maintainer.
- **Desktop app SSH session to the VPS**: add the connection in the app and check what it installs, which settings and skills load, and whether Herdr sees it.

## Exploration log

Every command or action run for this research, in order. Host names, the SSH target, user name, machine ID, private repository names and workspace labels are left out of this log and the file; `<vps-host>` stands for the target from `herdr machine list --json`. Scratch files lived in the session's scratchpad outside the repo.

| # | Where | What | Changed |
|---|---|---|---|
| 1 | Mac | `gh issue view 71`, `45`, `13`, `15`, `16`; `git show skills/cloud-agents:<file>` for the handoff, herdr-vps.md, harness-capabilities.md, agent-user-communication.md, the set-up-machine and handover-to-herdr skills and the Linux container check files; `gh pr view 66` | Nothing |
| 2 | Mac → GitHub | `gh release list/view -R herdrdev/herdr` (v0.9.1, v0.9.2); `gh api` tree listing at v0.9.2; `curl` of the Herdr docs listed above at v0.9.0 and v0.9.2, and 0.9.0's `config-reference.json` | Nothing (downloads to the scratchpad) |
| 3 | Mac → web | Fetched Claude Code docs (Remote Control, settings, settings reference, desktop) and Playwright docs (browsers, Docker) | Nothing |
| 4 | Mac | `herdr --version`, `herdr status --json`, `herdr machine list --json`, `herdr agent list` (count only), `grep` of `~/.config/herdr/config.toml` for toast settings; a script of `command -v` checks, `sw_vers`, `sysctl`, `ls` of `/Applications` browsers, the Playwright cache and `~/.config/agents`, `claude --version` | Nothing |
| 5a | VPS | Read-only probe script piped to `ssh -o BatchMode=yes <vps-host> "bash -l -s"`: `uname`, `/etc/os-release`, `nproc`, `free`, `df`, `uptime`, `ulimit`, `id -Gn`, `loginctl show-user -p Linger`, `systemctl --user is-system-running`, `command -v` for tools and harnesses, version flags, `ls` of browser caches, `dpkg -l` and `apt-cache policy` (read), `curl` HEAD-style requests to four HTTPS endpoints, `gh auth status` (account and token redacted in the output), `ssh -T git@github.com` | Nothing. The inner `ssh -T` read the rest of the piped script from stdin and sent it to GitHub's SSH endpoint, which runs no commands; the rest of the script didn't run on the VPS there, so step 5b ran it. |
| 5b | VPS | The rest of the same script: `ls`/`du` of the Playwright cache, `git config --get-regexp` (values redacted), per-repo `git branch --show-current` and `git worktree list`, the skills clone's `git log -1`, `git status --porcelain`, `git rev-parse HEAD`, `git ls-remote origin refs/heads/main`; `ls` of agent config paths; a Python read of `~/.claude/settings.json` (key names, rule counts, hook events, memory key) and of `~/.claude.json` (MCP server names); count of memory folders; `ls` of installed skills; `herdr --version`, `status --json`, `machine list --json`, `session list --json`, `workspace list`, `agent list`; `grep` of shell profiles for `PATH` lines | Nothing |
| 5c | VPS | Second read-only script: `ls` and `ldd` of the cached `chrome-headless-shell`; `ls ~/.npm/_npx`; `docker version`, `docker ps`, `docker images`; a Python read of four settings values and hook commands; `ls -l ~/.claude/.credentials.json` (mode only, not read); `claude --help` filtered; `herdr notification` (help); `DISPLAY` variables; `grep` of `sshd_config` for forwarding settings; `ss -tlnH` | Nothing |
| 6 | VPS (Herdr) | Throwaway probe, one script over SSH: `workspace list` (no `probe-71-` items before); `workspace create --cwd ~ --label probe-71-pane-env --no-focus` → workspace `w9`, pane `w9:p1`; `pane wait-output`; `pane run w9:p1 '<echo HERDR_ENV, TERM_PROGRAM and command -v for five tools>'`; `pane wait-output --match PROBE-DONE` (it matched the typed command line, so the read caught five of the eight output lines); `pane read --source recent-unwrapped`; `notification show "probe-71" --body "throwaway probe, ignore"` → `shown`; `workspace close w9` → `ok`; `workspace list` | Created workspace `w9` (`probe-71-pane-env`) and closed it. The after-list shows only the five pre-existing workspaces, none with the `probe-71-` prefix. One Herdr notification was raised (see *Notifications*). |
| 7 | VPS | `grep` of the Herdr server log for notification lines (last 8 lines), line count; `herdr api snapshot` key names | Nothing |
| 8 | Mac | `grep -c herdr skills/set-up-machine/rules.json` (0); read the sibling research files for overlap | Nothing |
| 9 | Mac | Wrote this file in the worktree and committed it | This file |

Nothing was installed, configured, resized or deleted on either machine, and no existing workspace, tab, pane or agent was touched beyond reading. No Herdr item was created on the Mac.
