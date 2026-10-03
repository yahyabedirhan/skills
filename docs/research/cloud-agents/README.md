# Cloud agents: what each place can do, and what to decide next

The synthesis for [Research: synthesis - capability matrix, decisions and next steps for cloud agents (#74)](https://github.com/yahyabedirhan/skills/issues/74), under [Spec: research cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45). **Read this file first.** Written 2026-09-29. It puts the research side by side. It also lists:

- the decisions left for the maintainer
- the experiments that the research couldn't run safely
- how the three blocked build tickets change

Every fact here comes from one of the research files below. Each matrix cell links the file (and section) behind it. This file adds no new probes.

Updates:

- **2026-09-29**, for [#78](https://github.com/yahyabedirhan/skills/issues/78). Its cloud session tested Claude Code's cloud from inside (the **sp**, **wf** and **ma** files).
- **2026-09-30**, for the maintainer's answers and the follow-up research (#86-#88).
- **2026-09-30 again**, after "Every harness and project is set up and audited from the skills" (#66) merged into `main`. set-up-machine is on `main` and applied on the Mac. Now an agent runs it from per-harness references, with no plan/apply script.
- **2026-10-03**, with what has happened since:
  - Herdr 0.9.3 everywhere
  - the new netcup VPS set up
  - two real efforts handed to a VPS by hand
  - shipyard's remote pings
  - close-effort renamed settle-effort
  - the maintainer's answers on D7, D8, D9 and D13

  Each changed fact carries an **Update 3 Oct** note. The findings of 29-30 September stay as they were.

Words used here:

- **Effort**: one piece of work with its own branch and pull request, built from a spec and tickets.
- **Orchestrator**: the agent session that runs an effort and gives its tickets to other agents.
- **Delegate**: an agent that takes one ticket, not a whole effort.
- **Handover**: one session gives an effort to a new session, through a handoff file that it commits and pushes.

| Short name | File | Ticket |
|---|---|---|
| **cc** | [claude-code.md](claude-code.md): Claude Code's cloud sessions, routines, projects | #69 |
| **op** | [other-providers.md](other-providers.md): Codex, Cursor, Copilot, and the rest | #70 |
| **vps** | [vps.md](vps.md): the VPS compared with the Mac, Herdr across machines | #71 |
| **siz** | [vps-sizing.md](vps-sizing.md): VPS sizing and other providers | #72 |
| **del** | [delegation.md](delegation.md): handing over, watching, answering, notifying, continuing | #73 |
| **fm** | [firstmate.md](firstmate.md): Firstmate and the Treehouse author's other tools | #75 |
| **hv** | [herdr-vps.md](../herdr-vps.md): the earlier Herdr-and-VPS research | — |
| **sp** | [session-probe.md](session-probe.md): first-hand probes from inside a Claude Code cloud session | #78 |
| **wf** | [session-workflow.md](session-workflow.md): how skills reach a cloud session, and the effort workflow there | #78 |
| **ma** | [managed-agents.md](managed-agents.md): Managed Agents on the Claude Platform vs Claude Code cloud sessions | #78 |
| **vp** | [vps-providers.md](vps-providers.md): VPS options to switch to, shared vs dedicated, latency | #86 |
| **co** | [costs.md](costs.md): what delegating costs on each hosted agent, and which ticket goes where | #87 |
| **fd** | [firstmate-deep-dive.md](firstmate-deep-dive.md): Firstmate's tools, workflows and a ranked borrow list | #88 |

## The short version

- **The Mac stays home.** It is the only place with every harness, current skills, Treehouse, a browser and a working notification. Nothing researched beats it for an orchestrated effort today.
- **The VPS runs an orchestrator like the Mac does, but the handover is by hand.** On 2026-09-29 it was one upgrade away. **Update 3 Oct:**
  - Herdr 0.9.3 runs on the Mac and both VPSes. `herdr --machine <label>` drives workspaces, panes, agents and plugins.
  - The new netcup VPS 1000 has about 8 GB, 4 vCPU, Debian 13, zram and swap. It has the current skills and global instructions from set-up-machine. It also has Treehouse, Go, Docker and a headless Chromium.
  - It is about 2.8x slower than the Mac in a benchmark.
  - The maintainer handed two real efforts (shipyard 0.0.5 and 0.0.6) from the Mac to a VPS orchestrator by hand. Both merged.
  - A VPS agent reaches the Mac with `shipyard ping`.
  - What's missing: a skill that does the handover (#16 → #13 → #15), and a route to the phone.
- **Claude Code's cloud sessions are good for tasks, and close to ready for efforts.** Tests from inside ([sp][sp-short]) show that they:
  - run with the laptop closed
  - cost only plan usage (the promo credit is live and spent first)
  - push their own branch, or a new one that they name
  - open pull requests
  - have a headless Chromium and a WebSearch that works

  This repo's skills don't load there by default. But skills installed into the VM's home load at once, so an environment setup script can carry them ([wf][wf-short]).

  What still causes problems:
  - Background work dies when Anthropic reclaims an idle VM.
  - Sub-agents can't nest.
  - `gh` is missing, and GitHub GraphQL is blocked.
  - A permission prompt can stall a session that nobody watches.
  - `claude --cloud "<task>"` prints the session URL and exits. Untested: whether it runs from an agent's shell without a terminal. The agent-side starts are a routine, or the in-session `create_session` tool.
- **The other hosted agents are delegates, not orchestrators.** Codex, Cursor and Copilot each take one prompt on one branch and return a pull request or a diff. A shell can start and watch all three. Only Cursor takes follow-ups through an API. None loads this repo's skills as they are. Only Cursor carries anything personal (account User Rules and a `~/.cursor/skills` sync) ([op §2][op2]). None is worth a sign-up before the maintainer tries Claude Code's cloud.
- **Managed Agents is a developer API, not a better cloud session.** It bills API tokens plus session-hours on top of the plan. It drops `CLAUDE.md`, skills, hooks and the Agent tool. Don't adopt it for efforts. Its one draw is a self-hosted sandbox on the VPS from an individual plan. That is worth a trial with a budget cap only if it becomes important ([ma][ma-fit]).
- **Firstmate is a source of ideas, not something to adopt.** Its best ideas for this setup:
  - a durable status file per worker
  - a readiness check before work goes to another machine
  - "unreachable is unknown, never fail over"
  - an orchestrator's delegates must not die with it

Recommended direction, in order:

1. Upgrade Herdr and set up the VPS environment (decisions D1-D3).
2. Build #16 and then #13 on `herdr --machine`.
3. Try the cloud setup script that carries the skills (E16) before any decision about cloud orchestration. E1 and E2 are done.
4. Fix the delegate-worktree base now (D8).

**Update 3 Oct:** the first step is done (D2, D3, D4). Next steps:

- On the VPS: small fixes (#150, #151, #148, the Herdr server start at boot), then #16 → #13 → #15, then QA.
- In the cloud: E16, two or three tickets in cloud sessions, one effort that the maintainer watches, and #80.
- The D8 fix is decided but not built yet.

## Capability matrix

Columns:

- **Mac**: the maintainer's Mac today.
- **VPS today**: the small Hetzner VPS as found on 2026-09-29.
- **VPS upgraded**: the same VPS after the proposed changes. These are Herdr 0.9.2 on both ends, set-up-machine applied, `jq` and a worktree tool installed, the Playwright system libraries or Docker image, and optionally a rescale to CX33. **The research expected everything in this column from the docs, but didn't try it.** **Update 3 Oct:** tried, on a new machine instead of a rescale. The netcup VPS 1000, set up on 2026-10-02, matches this column: Herdr 0.9.3, set-up-machine applied and `verify.py` passed, Treehouse and Go, zram and swap, headless Chromium, Docker. Two efforts ran there. Notes in the cells below mark where it differs.
- **Claude Code cloud**: a cloud session (Claude Code on the web, `claude --cloud`, routines, projects).
- **Other hosted**: Codex cloud, Cursor Cloud Agents, GitHub Copilot cloud agent (op §6 has the smaller ones).
- **Firstmate**: where it applies. Firstmate runs where it is cloned (Mac or Linux). So most rows describe what it adds on top of that machine.

### Machine and tools

| | Mac | VPS today | VPS upgraded | Claude Code cloud | Other hosted | Firstmate |
|---|---|---|---|---|---|---|
| **Environment** | macOS, arm64, 11 cores, 18 GB ([vps][vps-glance]) | Ubuntu 26.04, 2 vCPU, 3.8 GB (2.4 free), no swap. CX23 ([vps][vps-glance], [siz][siz-today]) | Same box. CX33 gives 4 vCPU / 8 GB. Swap proposed ([siz][siz-rec]) | A fresh Ubuntu 24.04 Firecracker VM per session, 4 vCPU / 15.7 GiB / 30 GB writable, root. Reclaimed when idle ([cc §2][cc2], [sp §10][sp10]) | Codex: container, size unpublished. Cursor: Ubuntu VM with desktop. Copilot: Actions runner, 59-min cap ([op][op-cmp]) | Wherever it's cloned. Off the machine, a whole "secondmate" home on an SSH host ([fm][fm-where]) |
| **Tools** | All four harnesses, Treehouse, Docker ([vps][vps-glance]) | Claude Code only. Node, Python, Swift, Docker. No `jq`, `rg`, Treehouse ([vps][vps-glance]) | Add `jq`, Treehouse (needs Go), and the preferred agent if not `claude` ([vps][vps-env]) | Broad toolchain, but `gh` missing. More by a root setup script, cached. No Herdr or Treehouse ([cc §3][cc3]) | Setup script, Dockerfile or `copilot-setup-steps.yml` ([op §1][op1], [§2][op2], [§3][op3]) | Needs `git`, `jq`, `herdr`, `treehouse`, `tasks-axi` and more on each host ([fm][fm-remote]) |
| **Web** | Yes ([vps][vps-glance]) | Yes: HTTPS to web, GitHub, npm ([vps][vps-web]) | Yes ([vps][vps-web]) | Allowlist ("Trusted") by default. Full or Custom per environment. WebFetch obeys the allowlist. WebSearch works ([cc §4][cc4], [sp §2][sp2]) | Codex: off by default. Cursor: on. Copilot: firewall allowlist ([op][op-cmp]) | The host's ([fm][fm-qs]) |
| **Browser** | Chrome, Safari, Playwright ([vps][vps-glance]) | **No**: the cached headless shell lacks 15 system libraries. No display ([vps][vps-browser]) | Headless, after `playwright install-deps` (root) or the Playwright Docker image ([vps][vps-browser]) | Headless Chromium pre-installed. Trust the proxy CA. Allowlisted hosts only ([sp §1][sp1]) | Cursor: full desktop and computer use. Copilot: Playwright MCP on by default. Codex: none documented ([op §2][op2], [§3][op3], [§1][op1]) | Requires `chrome-devtools-axi`. Headless on a server unverified ([fm][fm-axi]) |
| **File system** | Home folder ([vps][vps-glance]) | Own home, 26 GB free. `sudo` with a password ([vps][vps-glance]) | Same ([vps][vps-glance]) | Ephemeral VM. Only pushed work and the conversation persist ([cc §2][cc2]) | Ephemeral per task. Cursor keeps snapshots ([op §2][op2]) | The host's. A worktree per task ([fm][fm-walk]) |
| **Herdr** | 0.9.0, VPS saved as a machine ([hv][hv-model]) | 0.9.0. Driven over `ssh … bash -lc 'herdr …'` ([vps][vps-herdr]) | 0.9.2: `herdr --machine <label>`, `machine status`, no shell quotes ([vps][vps-upgrade]). **Update 3 Oct:** 0.9.3 on the Mac and both VPSes. `--machine` works for workspace, pane, agent and plugin commands. After a manual server restart, `machine status` can call a working VPS stopped (#151) | None ([cc §8][cc8]) | None ([del §5][del5]) | One of five backends. Remote homes always run on Herdr ([fm][fm-remote]) |
| **Git worktrees** | Treehouse ([vps][vps-glance]) | Plain git only. No Treehouse ([vps][vps-git]) | Treehouse, or `git worktree add` / `herdr worktree create` ([vps][vps-git]) | Plain `git worktree` works. Parallel work is sub-agents or projects ([cc §8][cc8], [sp §6][sp6]) | One branch per task ([op][op-cmp]) | `treehouse get` per task ([fm][fm-walk]) |

### The work itself

| | Mac | VPS today | VPS upgraded | Claude Code cloud | Other hosted | Firstmate |
|---|---|---|---|---|---|---|
| **GitHub push and PR** | `gh` ([del §1][del1]) | Yes: `gh` logged in, SSH auth works. Writes not tried ([vps][vps-git]) | Yes ([vps][vps-git]) | Push to the checked-out branch: its own `claude/…`, or a new one it names (an existing branch: untested). Create PR or the GitHub MCP tools. GraphQL blocked, REST for the attached repo only ([cc §6][cc6], [sp §4][sp4]) | All push and open PRs. Codex from the web, Cursor `cursor/…` or a given branch, Copilot one `copilot/…` PR ([op][op-cmp]) | The host's `gh`. Branch `fm/<id>`. A PR per task. Guarded merge ([fm][fm-gh]) |
| **Loads skills and instructions** | Current skills and global instructions ([vps][vps-glance]) | Older skill set. No global instructions. Hand-made deny rules, memory on ([vps][vps-env]) | Current skills, shared `AGENTS.md`, rule table, hook, memory off ([vps][vps-env]) | Repo `CLAUDE.md` and `.claude/skills`, claude.ai-enabled skills. **Not** the laptop's `~/.claude`. This repo's `skills/` doesn't load by default, but skills installed into the VM's `~/.claude/skills` load ([cc §5][cc5], [wf §1][wf1]) | Repo `AGENTS.md` everywhere. This repo's skills as they are: nowhere. Only Cursor carries anything personal: account User Rules and a `~/.cursor/skills` sync ([op][op-cmp], [op §2][op2]) | Its own `AGENTS.md` and skills replace ours ([fm][fm-map]) |
| **Orchestration with sub-agents** | Yes. The baseline ([del §1][del1]) | Old `orchestrate-effort` installed. `handover`, `close-effort` (now `settle-effort`) missing. RAM fits one or two agents ([del §3.1][del31], [siz][siz-tiers]) | As the Mac. CX33 fits two or three agents ([siz][siz-tiers]) | Sub-agents work, one level deep. Idle expiry kills background work. Projects run parallel threads ([cc §8][cc8], [wf §3][wf3]) | Task-sized. Cursor has sub-agents. Codex and Copilot unverified. Copilot capped at 59 min ([op][op-cmp]) | Forbids harness sub-agents. It uses visible workers with state on disk instead ([fm][fm-map]) |

### Delegating and hearing back

| | Mac | VPS today | VPS upgraded | Claude Code cloud | Other hosted | Firstmate |
|---|---|---|---|---|---|---|
| **Started by a local agent** | handover-to-herdr ([del §2][del2]) | `herdr` over SSH. Workspace create and close probed ([del §3.1][del31]) | `herdr --machine … agent start/prompt` ([del §3.1][del31]) | `claude --cloud` from an agent's shell: untested (in a terminal it prints a URL and exits). A routine's API trigger. `create_session` from inside a cloud session, untested ([cc §7][cc7], [del §4.1][del41]) | Yes: `codex cloud exec`, Cursor `POST /v1/agents`, `gh agent-task create` ([op][op-cmp]) | `fm-spawn.sh`. Remote through `fm-on.sh` over SSH ([fm][fm-remote]) |
| **Watched and answered** | Herdr sidebar. `agent read/prompt` ([del §2][del2]) | The Mac window shows its agent states. `agent read/prompt` over SSH ([del §3.2][del32]) | Same through `--machine`. Remote Control messages both ways, untested ([del §3.2][del32]) | claude.ai and phone. `claude -p "<msg>" --cloud <id>` sends. No CLI status read. From inside a cloud session, `list_sessions`/`get_session` read every session, Remote Control ones too ([cc §9][cc9]) | A shell can watch all of them. Answers: by API only in Cursor, by `@copilot` PR comment in Copilot, on the web or by `@codex` PR comment in Codex ([op][op-cmp]) | A watcher that spends no tokens. A durable inbox with receipts ([fm][fm-walk]) |
| **Notifications** | `osascript` ([del §2][del2]) | None proven: no `osascript` or `notify-send`. A Herdr notification "shown" in an unknown place ([vps][vps-notif]) | Remote Control push, or a Mac-side `agent wait` watcher. Both untested ([del §3.3][del33]). **Update 3 Oct:** `shipyard ping` from a VPS agent shows in the Mac's shipyard menu bar, tested from both VPSes. A blocked VPS agent shows red in the Mac's Herdr sidebar. Remote Control (E5) untested | Desktop and project notifications. A `PushNotification` tool exists, phone delivery untested. The PR is the done signal ([cc §9][cc9], [del §4.3][del43]) | Cursor: iOS push. Copilot: GitHub review request. Codex: unverified ([op][op-cmp], [del §2][del2]) | In the first mate's chat. A `command:` hook for a phone. No phone channel ([fm][fm-qs]) |
| **Moving back** | Same branch or stacked ([del §2][del2]) | Git plus safe-handover checks over SSH. VPS to Mac impossible ([hv][hv-checks], [hv][hv-back]) | Same checks through `--machine` ([vps][vps-perm]) | `claude --teleport` copies it. The docs don't say that the cloud session stops. Assume it may still run until E12 settles it ([cc §10][cc10], [del §4.4][del44]) | Codex `apply`. Check out the branch ([op][op-cmp]) | Relaunch from the brief on disk ([fm][fm-qs]) |
| **Cost** | Owned. Plan usage ([siz][siz-sum]) | €5.99/month plus plan usage ([siz][siz-sum]) | CX33 €8.99/month (+€3). Hetzner may refuse the rescale for now ([siz][siz-avail]). **Update 3 Oct:** not offered. A netcup VPS 1000 on a monthly term instead (D4) | Plan usage, no VM charge. A one-time $100 / $250 promo credit, live and spent first. Its rate-limit window (`resetsAt`) resets 5 November. That is a window reset, not a refill ([cc §11][cc11]) | Codex in Plus $20. Cursor Pro $20 plus API prices. Copilot Pro $10 plus AI credits ([op][op-cmp]) | Free. Spends the owner's subscriptions ([fm][fm-qs]) |

[cc2]: claude-code.md#2-environment
[cc3]: claude-code.md#3-tools-and-commands
[cc4]: claude-code.md#4-web-and-browser
[cc5]: claude-code.md#5-what-loads
[cc6]: claude-code.md#6-github
[cc7]: claude-code.md#7-starting-it
[cc8]: claude-code.md#8-long-work
[cc9]: claude-code.md#9-watching-and-answering
[cc10]: claude-code.md#10-moving-it
[cc11]: claude-code.md#11-cost-and-limits
[sp-short]: session-probe.md#short-answer
[sp1]: session-probe.md#1-headless-browser
[sp2]: session-probe.md#2-webfetch-and-websearch
[sp4]: session-probe.md#4-github-proxy
[sp6]: session-probe.md#6-worktrees
[sp10]: session-probe.md#10-disk
[sp-oq]: session-probe.md#answers-to-69s-open-questions
[wf-short]: session-workflow.md#short-answer
[wf1]: session-workflow.md#1-the-layers-in-a-cloud-session
[wf2]: session-workflow.md#2-carrying-the-skills-and-global-instructions-into-cloud-sessions
[wf3]: session-workflow.md#3-the-effort-workflow-in-a-cloud-session
[wf4]: session-workflow.md#4-suggestions
[wf-oq]: session-workflow.md#open-questions
[ma-fit]: managed-agents.md#5-fit-for-this-maintainer
[op-cmp]: other-providers.md#comparison
[op1]: other-providers.md#1-openai-codex-cloud
[op2]: other-providers.md#2-cursor-cloud-agents-and-the-agent-cli
[op3]: other-providers.md#3-github-copilot-cloud-agent-formerly-coding-agent
[vps-glance]: vps.md#at-a-glance
[vps-browser]: vps.md#headless-browser
[vps-web]: vps.md#web-access-scripts-and-file-system
[vps-git]: vps.md#git-worktrees-and-github
[vps-herdr]: vps.md#herdr-across-machines
[vps-upgrade]: vps.md#what-an-upgrade-to-092-would-change
[vps-notif]: vps.md#notifications
[vps-env]: vps.md#the-environment-on-the-vps
[vps-perm]: vps.md#permissions-on-the-other-machine
[siz-sum]: vps-sizing.md#summary
[siz-today]: vps-sizing.md#the-vps-today-vps
[siz-tiers]: vps-sizing.md#2-workload-to-smallest-tier
[siz-avail]: vps-sizing.md#availability-what-not-available-means
[siz-rec]: vps-sizing.md#6-recommendation-per-workload
[del1]: delegation.md#1-todays-flow-and-the-steps-that-depend-on-where-the-agent-runs
[del2]: delegation.md#2-the-options-side-by-side
[del31]: delegation.md#31-handing-over-through-herdr-13s-path
[del32]: delegation.md#32-watching-and-answering
[del33]: delegation.md#33-notifying
[del41]: delegation.md#41-handing-over
[del43]: delegation.md#43-notifying
[del44]: delegation.md#44-continuing-and-keeping-two-orchestrators-off-one-branch
[del5]: delegation.md#5-other-hosted-agents-for-delegation-only
[fm-walk]: firstmate.md#how-firstmate-delegates-walkthrough
[fm-where]: firstmate.md#where-crew-agents-run
[fm-remote]: firstmate.md#remote-secondmates-in-depth
[fm-gh]: firstmate.md#github-access
[fm-qs]: firstmate.md#the-same-questions-as-the-other-research-tickets
[fm-map]: firstmate.md#mapped-against-this-repos-workflow
[fm-axi]: firstmate.md#the--axi-tools
[hv-model]: herdr-vps.md#the-machine-model
[hv-checks]: herdr-vps.md#safe-handover-checks
[hv-back]: herdr-vps.md#vps-to-mac

## What each can do that the others can't

- **Mac:** a working notification (`osascript`), a desktop browser that the agent can drive, every harness, and the maintainer at the keyboard for trust prompts and approvals ([vps][vps-glance]).
- **VPS:** it runs this repo's own skills and Herdr with the laptop closed. The maintainer controls the machine and can install anything on it, for a flat monthly price ([vps][vps-glance], [siz][siz-sum]). **Update 3 Oct:** now proven twice. The maintainer handed over two shipyard efforts by hand, and both merged.
- **Claude Code cloud** ([cc §2][cc2], [cc §11][cc11], [sp §1][sp1]):
  - a bigger machine than the VPS (15.7 GiB) per session
  - many sessions in parallel
  - no machine to maintain
  - reachable from the phone
  - a headless browser out of the box
  - a one-time promo credit, already in use

  Projects add a coordinator with parallel threads that auto-fix their own PRs ([cc §8][cc8]).
- **Other hosted** ([op][op-cmp]):
  - Cursor drives a full desktop and takes API follow-ups.
  - Copilot lives inside GitHub (assign an issue, get a PR). Under GitHub's general rule, it uses free Actions minutes on a public repo.
  - Codex applies a finished diff straight into a local tree.
  - Cursor's My Machines can also run a cloud agent's tool calls on the VPS ([op §2][op2]).
- **Firstmate:** it survives its own restart and the death of its workers, because the brief and the status live on disk. It also has a real remote protocol: routed requests with receipts, and a readiness doctor ([fm][fm-walk], [fm][fm-remote]).

## Decisions for the maintainer

Each has options and a recommendation. "E" numbers point to the proposed experiments below.

### D1. Where does an orchestrated effort run?

- **Options:**
  - (a) the Mac only
  - (b) the Mac, or the VPS when the laptop will be closed
  - (c) Claude Code cloud sessions for whole efforts
  - (d) the Mac or the VPS orchestrates, and hosted agents take single tickets
- **Recommendation: (b) now, (d) later.** The VPS is the only place off the Mac where this repo's skills, Herdr and the effort workflow run unchanged ([del §2][del2]).
  - Cloud orchestration waits on E16 and E17. E1 showed two things: the skills can get into the VM, and a session can push a named branch. But other things still block it ([cc §8][cc8], [wf §3][wf3], [wf §4][wf4]):
    - Nobody has set up the carrier yet.
    - Idle expiry kills sub-agents.
    - Sub-agents can't nest.
    - Permission prompts stall a run that nobody watches.
    - An agent-side start is untested.
  - The first cloud shape to try, once E16 works, is a single-session effort: think and build in one cloud session that the maintainer watches.
  - Hosted agents as delegates wait until the maintainer chooses one (D7).

### D2. Upgrade Herdr to 0.9.2 on both machines?

- **Options:**
  - (a) upgrade both now
  - (b) stay on 0.9.0 and build on `ssh … bash -lc 'herdr …'`
  - (c) wait for a later release
- **Recommendation: (a), at a quiet moment (E3).** `herdr --machine` removes the login-shell wrapper and the remote-shell quotes. It keeps the host out of skill text. 0.9.2 adds `machine status` for a readiness check ([vps][vps-upgrade]). The cost is a VPS server restart that ends its idle agent pane. Herdr 0.9.2 came out on 2026-09-29.
- **Update 3 Oct: done.** Herdr 0.9.3 runs on the Mac and on both VPSes (E3). The saved machines have the labels `netcup-vps` and `hetzner-vps`. `herdr --machine <label>` works for workspace, pane, agent and plugin commands. Known bug: after a manual server restart, `herdr machine status` reports `hetzner-vps` "stopped or incompatible", but `--machine` still works (#151).

### D3. Set up the VPS environment the same way as the Mac?

- **Options:**
  - (a) run set-up-machine on the VPS (on `main` since #66 merged), and install `jq` and a worktree tool
  - (b) keep the hand-made VPS setup
  - (c) reinstall the VPS from scratch
- **Recommendation: (a) (E6, E8).** Without it, a VPS orchestrator has old skills, no global instructions and memory on. It also can't run `handover` or `close-effort` (now `settle-effort`) ([vps][vps-env], [del §3.1][del31]).
  - Decide first which of the 4 memory folders to keep. The diff removes memory files (backed up). In the same approval, it can carry what's worth keeping into the shared file.
  - For the worktree tool, install Treehouse (and Go). Don't make a special case for `git worktree add` on the VPS. Firstmate also requires Treehouse on a remote host ([fm][fm-remote]).
- **Update 3 Oct: done on the new netcup VPS** (E6, E8).
  - set-up-machine ran with the sandbox off, and `verify.py` passed.
  - Treehouse, Go, `gh` and Docker are installed. The maintainer did the logins in Herdr tabs.
  - The remote setup now lives in the skill on `main`. [`new-remote-machine.md`](../../../skills/set-up-machine/references/new-remote-machine.md) covers a fresh machine's base: user, SSH with keys only, firewall, updates, swap, PATH, browser. [`remote-machine.md`](../../../skills/set-up-machine/references/remote-machine.md) covers any remote machine.
  - Sudo steps go through a Herdr tab where the maintainer types the password (#148, not yet in the skills).

### D4. Resize the VPS?

- **Options:**
  - (a) stay on CX23
  - (b) add 2-4 GB of swap
  - (c) rescale to CX33 with "CPU and RAM only" (+€3/month, reversible)
  - (d) burst: create a big server from a snapshot and delete it after
  - (e) move provider
- **Recommendation: (a) plus (b) now. (c) when a browser or a second agent runs there.**
  - One agent fits with 2.4 GB spare. But with no swap, an out-of-memory spike kills processes ([siz][siz-rec]).
  - Hetzner's "not available" mark is a temporary restriction on new servers and rescales, per customer and per location. It doesn't affect the running CX23. So a refused rescale costs only a retry another day ([siz][siz-avail]).
  - Don't move provider: Hetzner CX is the cheapest per GB of everything compared ([siz][siz-sum]).
- **Update 3 Oct: decided and done** (see the follow-up research below). The maintainer ordered a netcup VPS 1000 (about 8 GB, 4 vCPU, Debian 13, monthly term) and set it up on 2026-10-02. It has a hardened base, zram and swap, Node, Claude Code, Codex, Herdr, Go, Treehouse, `gh`, Docker and headless Chromium. It is about 2.8x slower than the Mac in a benchmark. Another place tracks the retirement of the Hetzner VPS.

### D5. A headless browser on the VPS?

- **Options:**
  - (a) `npx playwright install-deps chromium` as root
  - (b) the Playwright Docker image, which the user can already run
  - (c) none: keep browser work on the Mac
- **Recommendation: (c) until a task needs it, then (b) (E7).** Docker needs no root and leaves the system untouched. Measure its memory next to an agent before you rely on it on CX23 ([vps][vps-browser]).
- **Update 3 Oct: done on the netcup VPS.** A headless Chromium is installed (item 4 after the steps in [`new-remote-machine.md`](../../../skills/set-up-machine/references/new-remote-machine.md)). In the trial, the machine peaked at about 4.4 of 7.8 GB (E7, partly).

### D6. How do skills and instructions reach a Claude Code cloud session?

This repo keeps its skills in `skills/`, not `.claude/skills/`. Cloud sessions don't load the laptop's `~/.claude/skills` or `~/.claude/CLAUDE.md`. So `/orchestrate-with-handoff` doesn't resolve in a fresh cloud session ([cc §5][cc5], [del §4.1][del41]). The VM's own `~/.claude/skills` does load, even mid-session ([wf §1][wf1]).

- **Options:**
  - (a) Enable the skills on the claude.ai account. They load in every cloud session, but someone must keep them in sync by hand.
  - (b) Commit a `.claude/skills/` in this repo. Only sessions on this repo get them. Other projects don't.
  - (c) Let the cloud environment's setup script (or a SessionStart hook in this repo) install the skills and global instructions into the VM's home. This gives one source of truth for every repo on that environment. Skills placed there load. A `~/.claude/CLAUDE.md` written there is untested.
  - (d) Don't carry skills: the handover brief carries the rules the session needs.
- **Recommendation: (c), now the likely answer. Confirm it in E16.** Keep (a) only for skills that must also reach Cowork. Don't restructure the repo for (b).
  - [wf §2][wf2] has the setup script (pinned `npx skills add … -g -a claude-code`, `gh`, a cloud copy of the global instructions) and a SessionStart hook for this repo.
  - Until E16 passes, use cloud sessions only with self-contained briefs (d).
  - The same unknown is open for Codex and Copilot too: "does the cloud agent read a home folder the setup script filled?" ([op][op-oq]).

### D7. Which hosted agent, if any, for single-ticket delegation?

- **Options:**
  - (a) Claude Code cloud only
  - (b) add Copilot: $10/month, lives in GitHub, 59-minute cap, no control from a shell. Answer by `@copilot` PR comment.
  - (c) add Cursor: $20 plus API prices. Best API, user-skill sync and account User Rules, browser.
  - (d) add Codex: in ChatGPT Plus, no follow-ups from a shell. Answer on the web or by `@codex` PR comment.
  - (e) none
- **Recommendation: (a) first. (b) if a second is wanted.**
  - (a) needs no sign-up, and the promo credit, already live, can cover a first try ([cc §11][cc11]).
  - Copilot is the cheapest trial and fits a public repo ([op §3][op3]). Cursor is the strongest delegate, but it bills model use at API prices ([op §2][op2]).
  - Whichever one you use, the delegate brief must carry the rules. Read the result back as a branch through `gh`, as Firstmate's Grok Bot pattern does ([fm][fm-map]).
  - Score any candidate against Firstmate's five-point backend contract ([fm][fm-contract]).
- **Update 3 Oct: decided.** "Claude plan only for now": no Copilot, no Jules. E13 is dropped.

### D8. What does an orchestrator delegate to, and from which base?

Two findings come from this effort's own run:

1. Harness sub-agent worktrees started from an old `main`, not the stacked effort branch. Every delegate had to fast-forward itself ([del §7][del7]).
2. Firstmate forbids its orchestrator the harness's sub-agent tool. The reason: sub-agent workers died with a restarted orchestrator and left no record ([fm][fm-map]).

- **Options:**
  - (a) keep in-process sub-agents, and pass the effort branch as the base explicitly
  - (b) for efforts off the Mac, delegate to Herdr tabs with a status file
  - (c) move to Firstmate's model everywhere
- **Recommendation: (a) now, as a small fix to the orchestrating skills. (b) as part of #15 for VPS efforts.**
  - Sub-agents are fine on the Mac. There the orchestrator rarely restarts, and it commits each ticket.
  - Every stacked effort needs the base-branch fix today.
  - Not landed yet: on `main` (2026-09-30), orchestrate-effort's step 4 still starts each delegate "in its own git worktree", with no base named.
- **Update 3 Oct: decided, (a).** A delegate's worktree branches from the effort's own base, and stays on top of it. That base may be `main` or another branch (a stacked effort). The fix to **orchestrate-effort** and **implement** is not built yet. A new ticket carries it.

### D9. How does done-or-blocked reach the maintainer from off the Mac?

- **Options:**
  - (a) Claude Code Remote Control push from the VPS session
  - (b) a Mac-side watcher (`herdr agent wait … --until done --until blocked`, then `osascript`)
  - (c) Herdr's toast delivery on the Mac client
  - (d) GitHub notifications on the pull request
- **Recommendation: (a) for the VPS once E5 proves it, with (b) as the fallback. (d) for cloud sessions.**
  - (a) is the only route that needs no Mac online ([del §3.3][del33]). (b) lives only as long as the session that watches.
  - For cloud sessions, the docs describe nothing else ([del §4.3][del43]). A cloud session's main loop has a `PushNotification` tool. E19 tests its phone delivery.
  - New: from inside a cloud session, `list_sessions` shows every session's state, with a needs-action flag. That includes Remote Control sessions on the Mac or VPS. So a cloud orchestrator can see a blocked local one, and the reverse ([cc §9][cc9]).
  - E4 settles (c). Its documented default is `off`, but a VPS probe returned `shown` ([del §3.3][del33]).
- **Update 3 Oct: still open, asked again plainly.** When an orchestrator finishes or is blocked somewhere other than the Mac, what replaces the macOS banner (`osascript`)? The routes as of today:

  | From | Route | Status |
  |---|---|---|
  | VPS | `shipyard ping`. The Mac's shipyard menu-bar app polls it through the herdr-shipyard plugin (`herdr --machine X plugin action invoke list`, read from `plugin log list`) | Works. Tested from both VPSes on 3 Oct. A click can't switch the Mac's Herdr window to that machine (shipyard #152). No Linux release yet, so someone builds the CLI by hand on each VPS (shipyard #147) |
  | VPS | Herdr sidebar state on the Mac (a blocked agent shows red) | Works, but only if the maintainer looks |
  | VPS | Herdr toast, `herdr notification show` | Untested (E4). Toast delivery is off on the Mac |
  | Cloud session | Phone push, the `PushNotification` tool | The tool said sent. Arrival unchecked (#80, E19) |
  | Any | The GitHub pull request | Always. Signals done only |

  Proposed answer for the maintainer to confirm: `shipyard ping` for the VPS, phone push for cloud sessions once #80 confirms it, and GitHub as the fallback. That also settles #144: `notification-method` on a VPS is `shipyard ping`.

### D10. Does the VPS need to reach the Mac?

- **Options:**
  - (a) no, the Mac always checks
  - (b) Claude Code cross-session messaging over Remote Control (text only, both directions, no inbound access)
  - (c) SSH into the Mac (Remote Login plus Tailscale or a reverse tunnel)
- **Recommendation: (a), plus (b) where a VPS agent must ask the Mac something (E5).** (c) opens the Mac to inbound access for little gain ([hv][hv-back], [del][del16]).

### D11. Guard disruptive remote Herdr commands in the rule table?

- **Options:**
  - (a) add rows at `ask` to set-up-machine's `rules.json` for `herdr … server stop` and `workspace close --group` (and their `--machine` forms)
  - (b) rely on the skills' wording
- **Recommendation: (a),** as new rows in the rule table. `--machine` makes a stop of every agent on the VPS one local command ([vps][vps-perm]).

### D12. The promo credit and the one unused cloud session

- **Options:**
  - (a) spend it on the cloud experiments (E16, E17) before it expires
  - (b) leave it
- **Recommendation: (a).** The credit is live and in use. #78's cloud session drew on a promotional rate-limit pool. The window of that pool resets (`resetsAt`) on 5 November (midnight PST). That is a window reset, not a refill. Inferred: it matches the reported 4 November expiry ([cc §11][cc11]). E1 has used the session it needed. Read the remaining balance at claude.ai/settings/usage.

### D13. Adopt Firstmate?

- **Options:**
  - (a) adopt it
  - (b) borrow ideas
  - (c) ignore it
- **Recommendation: (b).** Adoption would replace the effort workflow, run workers with bypassed permissions and strip AI trailers ([fm][fm-map]). Borrow these ([fm][fm-map]):
  - the status-file protocol (for #16)
  - a readiness check with `fixable`/`human` gaps and "unreachable is unknown" (for #13)
  - relaunch from a brief on disk (for #15)
  - a worktree-isolation check in delegate briefs
  - `--match-head-commit` in settle-effort's merge (close-effort until its rename)
- **Update 3 Oct: still open.** The maintainer will pick from the 18 ranked ideas in [fd §3](firstmate-deep-dive.md#3-what-to-borrow). The guide's D13 card lists them one line each. The top two are small: a worktree-isolation check in delegate briefs (**orchestrate-effort**, **implement**) and `--match-head-commit` in **settle-effort**'s merge.

[op-oq]: other-providers.md#open-questions
[fm-contract]: firstmate.md#the-contract-a-delegate-backend-must-meet
[del7]: delegation.md#7-how-this-effort-itself-was-handed-over-material-for-15
[del16]: delegation.md#agents-on-the-mac-and-the-vps-can-see-each-others-state-16

### The maintainer's answers (2026-09-30)

| | Answer | Status |
|---|---|---|
| D1 | The Mac for now. Test the VPS and cloud sessions **at the same time**, the cloud first while the promo credit lasts | Changed |
| D2 | Yes | Agreed |
| D3 | Yes. Which memory folders to keep is still to pick | Agreed |
| D4 | Hetzner won't rescale now. Open to a pricier tier or another European provider. Needs its own research: providers, latency, shared against dedicated vCPU | Open |
| D5 | A headless browser on the VPS from day zero, in the environment | Changed |
| D6 | The setup script or SessionStart hook installs the global skills and instructions | Agreed |
| D7 | Yes to hosted agents for single tickets. Wants pros, cons and costs per agent before a choice of tickets | Open |
| D8 | Needed a plain explanation. Plan: keep effort #45 open, close the research tickets, open action items | Open |
| D9 | Needed a plain explanation. #80 tests phone push from a cloud session again | Open |
| D10 | Fire and forget is the flow, but keep the channel two-way where it exists | Changed |
| D11 | No guard rules. Agents work freely across the Mac and the VPS | Changed |
| D12 | Yes. The maintainer confirmed on the usage page that the promo credit paid for #78's session | Agreed |
| D13 | Don't adopt. Understand its concepts and pick what to borrow | Open |

### Decision status (2026-10-03)

| | Status | Where it stands |
|---|---|---|
| D1 | Changed | Two tracks. The VPS track's setup is done, and two efforts ran there by hand |
| D2 | Done | Herdr 0.9.3 on the Mac and both VPSes. #151 open |
| D3 | Done | set-up-machine applied on the netcup VPS, `verify.py` passed |
| D4 | Done | netcup VPS 1000, set up 2026-10-02. Another place tracks the retirement of Hetzner |
| D5 | Done | Headless Chromium on the netcup VPS |
| D6 | Agreed | Waits on E16 |
| D7 | Decided 3 Oct | Claude plan only for now. No Copilot or Jules |
| D8 | Decided 3 Oct | Branch from the effort's own base and stay on it. Fix not built (new ticket) |
| D9 | Open | Proposed: `shipyard ping` for the VPS, phone push for cloud once #80 confirms, GitHub as fallback. Settles #144 |
| D10 | Changed | Remote Control (E5) untested. `shipyard ping` gives a one-way VPS → Mac signal |
| D11 | Changed | No guard rules. Still open: whether the wider ask-first line loosens |
| D12 | Agreed | Spend the credit on the cloud track |
| D13 | Open | The maintainer picks from the 18 ranked ideas |

### Follow-up research on the open decisions (2026-09-30)

- **D4, decided 2026-10-02:** netcup VPS 1000 G12.5 on a 1-month term, for 3 agents, CPU speed first.
  - The maintainer set it up the same day (set-up-machine applied, Herdr 0.9.3).
  - A trial against the Mac on real repos showed: 2.5-3x slower, CPU-bound, peak 4.4 GB of 7.8 GB, steal under 1.3%.
  - Kept. The next step is VPS 2000 in place. The machine record is in the personal repository.
- **D4, redone 2026-10-02 ([vm](vps-math.md)).**
  - The maintainer found that the CX23 can't run one agent with tests, a browser test or anything in parallel.
  - The rescale dialog offers CPX12 and up, not CX33.
  - Budget: $10-15, up to about $25.
  - Five parallel agents with 3 test runs and 2 browsers need about 12 GB, so 16 GB. The recommendation is now **netcup VPS 2000 G12.5** (8 vCores, 16 GB, €22.62 net, $25.56, on 12 months). Or VPS 1000 (8 GB, $13.76) if $15 is the ceiling.
  - Earlier ([vp](vps-providers.md#5-ranked-shortlist), #86): Hetzner CX and CAX are still not orderable. The recommendation was **netcup Root Server RS 2000** (8 dedicated EPYC cores, 16 GB, 256 GB NVMe, €34.20 net a month on 12 months, 30-day money-back), with the CX23 kept alongside for 2-4 weeks. Fallbacks: netcup VPS 2000 (€22.62) and OVHcloud VPS-4 (€23.49, no term).
  - Latency from the Mac is 54-102 ms across providers. That is too close to choose on.
- **D7 ([co](costs.md#short-answer), #87).**
  - Metered vendors charge Claude Opus at Anthropic's list price. So a ticket costs about the same everywhere (estimates: $1 small, $4 medium, $28 for a five-ticket effort).
  - The Claude plan turns that into $0 cash inside its windows.
  - Keep the plan and the VPS. Add Copilot Pro ($10) only for a second delegate. Try Jules's free tier. Skip the rest for now.
  - The promo credit's claim date (7 October) and expiry (4 November) come from press reports only.
- **D13 ([fd](firstmate-deep-dive.md#3-what-to-borrow), #88).** 18 ideas ranked. The first two are small skill changes: a worktree-isolation check in delegate briefs (**orchestrate-effort**, **implement**), and a guarded merge with `--match-head-commit` (**close-effort**, since renamed **settle-effort**).

## Proposed experiments

These are what the research couldn't settle inside the spec's safe zone. Each needs the maintainer, or the maintainer's go-ahead.

**Update 3 Oct, where each stands:**

| Status | Experiments |
|---|---|
| Done | E1, E2; E3 (Herdr 0.9.3, apart from #151); E6 (on the netcup VPS); E8 (Treehouse and Go on the netcup VPS); E9 (swap, now in [`new-remote-machine.md`](../../../skills/set-up-machine/references/new-remote-machine.md)) |
| Partly | E7: headless Chromium installed on the netcup VPS. Trial peak about 4.4 of 7.8 GB. No measurement next to a browser yet |
| Obsolete or dropped | E10 (moved to netcup instead of a rescale); E13 (dropped by D7) |
| QA left | E19 (#80), E4, E12, E18 |
| Build or setup left | E16 (the cloud setup script, key for the cloud track), E17, E20, E5, E11; E14 and E15 optional |

| # | Experiment | Settles | Cost | Risk | Source |
|---|---|---|---|---|---|
| E1 | **Done by #78** ([sp][sp-oq]). The maintainer's `claude --cloud "say hi"` gave the session. It answered VM size and user, session ID output, browser, WebFetch/WebSearch, skills and `AGENTS.md` loading, push to a new branch, and REST through the proxy. Left open: phone push (E19), push to an existing branch (E20), setup-script loading (E16). The original plan: **the one remaining cloud probe, run by the maintainer in a real terminal.** On a throwaway `probe/…` branch of this public repo, run `claude --cloud "<read-only probe prompt>"` (the prompt is in cc's Exploration log, row 11). Note what the CLI prints. The session pushes results to the probe branch. Then delete the branch. Add: list skills, try a push to a second branch, "notify me when done", `gh api …/issues/45/sub_issues`. To test D6 (c), first give the environment a setup script that installs the skills into the VM's home | VM size and user, session ID output, browser, WebFetch/WebSearch under Trusted, skills and `AGENTS.md` loading, push to another branch, phone push, REST through the proxy | One small session of plan usage or promo credit | Low: public repo, throwaway branch, read-only prompt | [cc open questions][cc-oq] |
| E2 | **Done by #78**: `list_sessions` inside the cloud session shows no session from probe 1. `get_session` shows the promo credit in use ([cc open questions][cc-oq]). Left: read the balance. The original: check claude.ai for a session from probe 1 (it exited 1, cause unknown) and archive it. Read the promo credit's balance and terms | Whether probe 1 created a session; D12 | None | None | [cc §7][cc7] |
| E3 | Upgrade Herdr to 0.9.2 on both machines. Run a `probe-` workspace create, `pane run`, `pane read`, close and `agent list` again through `--machine`. Record `machine status --json` | D2; the command shapes that #13 and #16 use | Minutes | The VPS server restart ends its panes (one idle agent today). Live handoff is experimental | [vps][vps-upgrade], [del open questions][del-oq] |
| E4 | With the maintainer at the Mac: `herdr notification show` on the VPS with the Mac window on Local, then on the VPS, then with `delivery = "system"` on the Mac | Where a VPS notification appears; D9 (c) | Minutes | None | [vps][vps-notif] |
| E5 | `claude --remote-control` in a throwaway VPS Herdr tab, and a Mac session on Remote Control. Check `ListAgents`, `SendMessage` both ways, `isolatePeerMachines`, and a phone push on "notify me when done" | D9 (a), D10 (b) | Minutes | One-time Remote Control consent on the VPS (a config change). Registers a session with Anthropic | [del][del16], [del §3.3][del33] |
| E6 | set-up-machine on the VPS, now that #66 has merged. Pull the clone. Have a VPS agent run the skill to its one diff, and show it. Write on approval. Check with `verify.py` | D3 | Minutes | Removes memory files (backed up). Hand-made rules stay, as `stricter` or `extra`. Pick memory to keep first | [vps][vps-env] |
| E7 | Pull the Playwright Docker image (`…-resolute`) on the VPS. Load one page headless with `--init --ipc=host`. Record memory next to a running agent | D5; replaces the sizing estimates | A multi-GB image on a disk with 26 GB free | Low. No root, removable | [vps][vps-browser], [siz][siz-rec] |
| E8 | Install `jq`, Go and Treehouse on the VPS | D3's worktree tool | Minutes | Low | [vps][vps-git] |
| E9 | Add 2-4 GB of swap on the VPS | D4 (b) | Disk space | Low. A system config change | [siz open questions][siz-oq] |
| E10 | Rescale CX23 → CX33 "CPU and RAM only", time the downtime, rescale back | D4 (c) | A few cents plus minutes of downtime | Hetzner may refuse it while its restriction lasts. The server stays as it was | [siz][siz-avail] |
| E11 | A routine with an API trigger, whose prompt runs a handoff. Fire it from a local agent. Read the session URL | Whether an agent can hand an effort to the cloud with nobody present | One routine run of plan usage. Counts toward the daily run cap | Low. You make the token on the web | [cc §7][cc7], [del §4.1][del41] |
| E12 | After a `claude --teleport`, check whether the cloud original keeps running, and archive it | How #15 keeps two orchestrators off one branch | None | None | [del open questions][del-oq] |
| E13 | Hosted trials, only if D7 picks one: a Copilot task on a throwaway branch (`gh agent-task create`), a Codex environment whose setup script installs skills, a Cursor API agent | D7; user skills and notifications for each | $10-20 a month and a sign-up each. Cursor adds API prices | Low on a public repo | [op open questions][op-oq] |
| E14 | Firstmate's `fm-remote-doctor.sh`, read-only, on the VPS in a throwaway account | How far the VPS is from a Firstmate remote home | Installs Firstmate's tools | Low in a separate account | [fm open questions][fm-oq] |
| E15 | Desktop app SSH session to the VPS: what it installs, which settings and skills load, whether Herdr sees it | Whether the desktop app is a way onto the VPS | Minutes | Changes the app's config | [vps][vps-desktop] |
| E16 | A personal cloud environment with the setup script from [wf §2][wf2], pinned to a commit with the whole effort family. Start one session. Check `/skills`, and quote a rule line from the global instructions | D6 (c); whether a `~/.claude/CLAUDE.md` that the script writes loads | Minutes on claude.ai, one small session | Low. A bad script fails the start | [wf §4][wf4] |
| E17 | One `create_session` child from a cloud session, on a throwaway branch of this repo with `outcome_branch` set. Does it get the environment's skills, push there, and show in `list_sessions`? Then archive it | An agent-side cloud start; a `handover-to-claude-code-cloud` skill; D1 | One session of plan usage | Low on a public repo and throwaway branch | [wf §4][wf4] |
| E18 | Leave a probe session idle. Note when a reopen gives a fresh VM, and whether setup-script files survive | Idle expiry; how long a cloud orchestrator may wait on a question | None | None | [cc open questions][cc-oq], [wf open questions][wf-oq] |
| E19 | Ask a cloud session's main loop to "notify me when done", and watch the phone | D9 for cloud sessions | None | None | [cc open questions][cc-oq] |
| E20 | A cloud session on a throwaway `probe/…` branch pushed from the Mac, asked to push a commit to it | Whether a cloud orchestrator can continue an effort branch made elsewhere (#15) | One small session | Low. Throwaway branch | [cc open questions][cc-oq] |

[cc-oq]: claude-code.md#open-questions
[del-oq]: delegation.md#open-questions
[siz-oq]: vps-sizing.md#open-questions
[fm-oq]: firstmate.md#open-questions
[vps-desktop]: vps.md#where-the-desktop-app-fits

## The three build tickets, re-scoped

Each ticket has the full re-scope comment. In short:

- **[A thinking session on the Mac can hand over to an orchestrator on the VPS (#13)](https://github.com/yahyabedirhan/skills/issues/13).**
  - The shape is settled. **handover-to-herdr** gets a target machine (Local or a saved Herdr machine's label). The VPS's own environment defaults name its worktree tool and agent. The host comes from Herdr's catalog.
  - Build it on `herdr --machine` after D2, with the VPS set up by D3. Notifications follow D9.
  - A handover to a Claude Code cloud session is out of its scope. No agent-side start is proven yet (see D1, E11, E17).
  - **Update 3 Oct:** D2 and D3 are done. The maintainer handed two shipyard efforts to a VPS orchestrator by hand, and both merged: 0.0.5 to the Hetzner VPS (Herdr 0.9.0, over SSH) and 0.0.6 to the netcup VPS (Herdr 0.9.3, mostly `herdr --machine`). #13 automates these manual steps:
    1. Push the handoff.
    2. Install the toolchain (sudo in a Herdr tab where the maintainer types the password, #148).
    3. Lease a worktree with `treehouse`.
    4. Run `herdr --machine X workspace create`, `worktree open`, `agent start --kind claude`.
    5. The maintainer accepts the trust prompt.
    6. Run `agent prompt "/orchestrate-with-handoff <path>"`.
    7. Run `agent wait --until working`.

    No skill does this yet. Build order: #16 → #13 → #15.
- **[An unfinished effort can be handed to a new orchestrator (#15)](https://github.com/yahyabedirhan/skills/issues/15).**
  - Detection and the same-branch or stacked question are settled. The file lists the checks per place that "the old side is idle and pushed".
  - New scope from this run: a continuation checks for a newer handoff, and delegates must branch from the effort branch (D8).
  - Cloud continuations stay open until E12 and E20. (E1 showed that a session can push a new branch that it names.)
- **[Agents on the Mac and the VPS can see each other's state (#16)](https://github.com/yahyabedirhan/skills/issues/16).**
  - Settled: every read works over SSH today, and through `--machine` after D2. The permission table is in [vps][vps-perm].
  - New: a status file per remote orchestrator (from Firstmate), and Remote Control messages for the reverse direction (E5).
  - It can land first, and #13 and #15 build on it.
  - **Update 3 Oct:** the reverse direction has a working signal outside the skills: `shipyard ping` from a VPS agent, which the Mac's shipyard app shows (D9).

## The spec's decisions, as the research left them

- **Research only** held: the research changed no skill, instruction or machine. The only writes outside this repository were:
  - throwaway Herdr workspaces on the VPS (closed)
  - two `herdr notification show` calls on the VPS ([vps][vps-log], [del][del-log])
  - two throwaway probe branches (deleted) ([cc][cc-log])
  - scratch files on the Mac (fetched docs and a scratch SSH config alias, all outside the repo, not committed)
- **Safe probes:** the VPS probes stayed read-only, apart from the throwaway workspaces and the two notifications. The spec allowed two cloud sessions:
  - The first probe exited 1, with no evidence of a session.
  - The agent's local permission check refused the second before anything ran.

  So the first pass had **no first-hand facts about the cloud VM**, and E1 handed the one unused session to the maintainer. **Update (#78):** the maintainer started it with `claude --cloud "say hi"`. The first-hand facts now live in [sp][sp-short] and [wf][wf-short].
- **Twelve research files, this synthesis and the guide** (`guide.html`) are under `docs/research/`. Each research file has an exploration log. Six come from the first pass, three from #78's cloud session and three from #86-#88. The maintainer added the Firstmate ticket (#75) mid-effort.
- **The build tickets** stay blocked. They now wait on the decisions and experiments above, not on research.
- **Update 3 Oct:** the research stayed read-only. But the maintainer's own setup work has changed the machines since: Herdr 0.9.3 everywhere, a new netcup VPS set up with set-up-machine, and shipyard's remote pings. Tickets to file once this PR merges:
  - the D8 base-branch fix
  - the Firstmate borrowings, once picked (D13)
  - the cloud track (E16 onwards)

## Corrections made while writing this synthesis

- **Starting a cloud session from an agent.** [delegation.md](delegation.md) presented `claude --cloud "<one-line prompt>"` as the handover's start. But the create form needs an interactive terminal, and `-p` rejects it with a task ([cc §7][cc7], checked against the `headless` and `claude-code-on-the-web` docs). That file's table row, its sections 4.1 and 4.4, and its #15 summary now say so. Then #78 found that the create form prints the session URL and exits in a real terminal. Whether it runs from an agent's shell stays untested, and both files now say that.
- **Herdr's toast default.** [delegation.md](delegation.md) read the `delivery = "herdr"` example on the 0.9.2 configuration page as a contradiction of a default of `off`. The config reference at `v0.9.2` gives `ui.toast.delivery` a default of `"off"` for both 0.9.0 and the current docs. So the example shows how to turn it on. Nothing explains the VPS probe's `shown` yet, as [vps.md](vps.md#notifications) says.
- **A routine's fire response** returns `claude_code_session_id` as well as `claude_code_session_url` (the `routines` doc's example). [claude-code.md](claude-code.md#7-starting-it) listed only the URL.
- **From #78's first-hand probes** (all now in [claude-code.md](claude-code.md)):
  - `claude --cloud "<task>"` prints the session URL and exits, with no live checklist.
  - A headless Chromium is pre-installed.
  - A blocked host gets a plain 403 with the reason in the body, and no `x-deny-reason`.
  - GitHub GraphQL is blocked entirely.
  - A session can push a new branch that it names, not only `claude/…`.
  - The docs' "`~/.claude/*` doesn't load" means the laptop's files.
- The files already had these corrections, and this synthesis confirms them:
  - The VPS's cached headless browser can't start without 15 system libraries ([vps][vps-browser], [siz][siz-today]).
  - Swift is on the VPS, although #13 recorded it missing ([vps][vps-perm]).

[vps-log]: vps.md#exploration-log
[del-log]: delegation.md#exploration-log
[cc-log]: claude-code.md#exploration-log

## Exploration log

All on the maintainer's Mac on 2026-09-29, in this ticket's worktree or the session's scratch folder. Nothing ran on the VPS. This research started no cloud session and installed nothing.

| # | Action | Changed |
|---|---|---|
| 1 | `git merge --ff-only skills/cloud-agents` (the worktree had started from an older `main`) | This worktree's branch only |
| 2 | `gh issue view` for #74, #45, #13, #15, #16, #75, with comments; read the effort handoff and every file named at the top | Nothing |
| 3 | `curl` of Herdr's `configuration.mdx` and both `config-reference.json` files at `v0.9.2`, and of Claude Code's `routines`, `claude-code-on-the-web` and `headless` pages in Markdown, to resolve the claims the files disagreed on | Copies in the scratch folder only |
| 4 | Checked the repository layout (`skills/`, no `.claude/`) and the orchestrating skill's delegate rule | Nothing |
| 5 | Wrote this file; corrected `delegation.md` and `claude-code.md` as listed above; one commit | These files |
| 6 | Cloud session (#78, integration): read the three #78 files and the orchestrator's own session probes. Updated the file table, the short version, the matrix's Claude Code cloud cells, D1, D6, D7, D9, D12. Marked E1 and E2 done, added E16 to E20 and a Managed Agents bullet, and noted the #78 corrections | This file only |
| 7 | Mac, 2026-09-30 | After #66 merged into `main`: read set-up-machine, orchestrate-effort and close-effort there, and checked the Mac's `~/.config/agents/`. Updated the note at the top, the short version, the "VPS upgraded" column, D3, D8, D11, E6 and #13's re-scope | This file only |
| 8 | Mac, 2026-10-03 | After `main` was merged in: read `new-remote-machine.md`, `remote-machine.md` and settle-effort there, and `gh issue view` for #13, #15, #16, #80, #144, #148, #150, #151 and shipyard #147, #152. Applied the facts that the maintainer verified that day as **Update 3 Oct** notes: the short version, the "VPS upgraded" column, D2-D5, D7-D9, D13, the decision status, the experiment status and the build tickets | This file and the guide |
