# Cloud agents: what each place can do, and what to decide next

The synthesis for [Research: synthesis - capability matrix, decisions and next steps for cloud agents (#74)](https://github.com/yahyabedirhan/skills/issues/74), under [Spec: research cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45). **Read this file first.** It puts the research side by side, lists the decisions left for the maintainer, the experiments the research couldn't run safely, and how the three blocked build tickets change. Written 2026-09-29.

Every fact here comes from one of the research files below; each matrix cell links the file (and section) behind it. Nothing new was probed for this file. Updated on 2026-09-29 for [#78](https://github.com/yahyabedirhan/skills/issues/78), whose cloud session tested Claude Code's cloud from inside (the **sp**, **wf** and **ma** files). Updated on 2026-09-30 for the maintainer's answers and the follow-up research (#86-#88), and again once "Every harness and project is set up and audited from the skills" (#66) merged into `main`: set-up-machine is on `main` and applied on the Mac, and is now run by an agent from per-harness references, with no plan/apply script.

| Short name | File | Ticket |
|---|---|---|
| **cc** | [cloud-agents-claude-code.md](cloud-agents-claude-code.md): Claude Code's cloud sessions, routines, projects | #69 |
| **op** | [cloud-agents-other-providers.md](cloud-agents-other-providers.md): Codex, Cursor, Copilot, and the rest | #70 |
| **vps** | [cloud-agents-vps.md](cloud-agents-vps.md): the VPS compared with the Mac, Herdr across machines | #71 |
| **siz** | [cloud-agents-vps-sizing.md](cloud-agents-vps-sizing.md): VPS sizing and other providers | #72 |
| **del** | [cloud-agents-delegation.md](cloud-agents-delegation.md): handing over, watching, answering, notifying, continuing | #73 |
| **fm** | [cloud-agents-firstmate.md](cloud-agents-firstmate.md): Firstmate and the Treehouse author's other tools | #75 |
| **hv** | [herdr-vps.md](herdr-vps.md): the earlier Herdr-and-VPS research | — |
| **sp** | [cloud-agents-session-probe.md](cloud-agents-session-probe.md): first-hand probes from inside a Claude Code cloud session | #78 |
| **wf** | [cloud-agents-session-workflow.md](cloud-agents-session-workflow.md): how skills reach a cloud session, and the effort workflow there | #78 |
| **ma** | [cloud-agents-managed-agents.md](cloud-agents-managed-agents.md): Managed Agents on the Claude Platform vs Claude Code cloud sessions | #78 |
| **vp** | [cloud-agents-vps-providers.md](cloud-agents-vps-providers.md): VPS options to switch to, shared vs dedicated, latency | #86 |
| **co** | [cloud-agents-costs.md](cloud-agents-costs.md): what delegating costs on each hosted agent, and which ticket goes where | #87 |
| **fd** | [cloud-agents-firstmate-deep-dive.md](cloud-agents-firstmate-deep-dive.md): Firstmate's tools, workflows and a ranked borrow list | #88 |

## The short version

- **The Mac stays home.** It is the only place with every harness, current skills, Treehouse, a browser and a working notification. Nothing researched beats it for an orchestrated effort today.
- **The VPS is one upgrade away from running an orchestrator like the Mac does.** Web, GitHub and Claude Code already work there. What's missing is small: Herdr 0.9.2 on both machines (for `herdr --machine`), the current skills and global instructions (set-up-machine, on `main` since #66 merged), a worktree tool, and a notification route. A browser needs an install. RAM (3.8 GB, no swap) limits it to one or two agents.
- **Claude Code's cloud sessions are good for tasks, and close to ready for efforts.** Tested from inside ([sp][sp-short]): they run with the laptop closed, cost only plan usage (the promo credit is live and spent first), push their own branch or a new one they name, open pull requests, and have a headless Chromium and working WebSearch. This repo's skills don't load there by default, but skills installed into the VM's home load at once, so an environment setup script can carry them ([wf][wf-short]). What still bites: background work dies when an idle VM is reclaimed, sub-agents can't nest, `gh` is missing and GitHub GraphQL is blocked, and a permission prompt can stall an unattended session. `claude --cloud "<task>"` prints the session URL and exits; whether it runs from an agent's shell without a terminal is untested, and a routine or the in-session `create_session` tool are the agent-side starts.
- **The other hosted agents are delegates, not orchestrators.** Codex, Cursor and Copilot each take one prompt on one branch and return a pull request or a diff. All three can be started and watched from a shell; only Cursor takes follow-ups through an API. None loads this repo's skills as they are; only Cursor carries anything personal (account User Rules and a `~/.cursor/skills` sync) ([op §2][op2]). None is worth a sign-up before Claude Code's cloud has been tried.
- **Managed Agents is a developer API, not a better cloud session.** It bills API tokens plus session-hours on top of the plan and drops `CLAUDE.md`, skills, hooks and the Agent tool. Don't adopt it for efforts; its one draw is a self-hosted sandbox on the VPS from an individual plan, worth a budget-capped trial only if that becomes important ([ma][ma-fit]).
- **Firstmate is worth borrowing from, not adopting.** Its best ideas for this setup: a durable status file per worker, a readiness check before handing work to another machine, "unreachable is unknown, never fail over", and not letting an orchestrator's delegates die with it.

Recommended direction, in order: upgrade Herdr and set up the VPS environment (decisions D1-D3), build #16 and then #13 on `herdr --machine`, try the cloud setup script that carries the skills (E16) before deciding anything about cloud orchestration (E1 and E2 are done), and fix the delegate-worktree base now (D8).

## Capability matrix

Columns:

- **Mac**: the maintainer's Mac today.
- **VPS today**: the small Hetzner VPS as found on 2026-09-29.
- **VPS upgraded**: the same VPS after the proposed changes: Herdr 0.9.2 on both ends, set-up-machine applied, `jq` and a worktree tool installed, the Playwright system libraries or Docker image, and optionally a rescale to CX33. **Everything in this column is expected from the docs, not tried.**
- **Claude Code cloud**: a cloud session (Claude Code on the web, `claude --cloud`, routines, projects).
- **Other hosted**: Codex cloud, Cursor Cloud Agents, GitHub Copilot cloud agent (the smaller ones are in op §6).
- **Firstmate**: where it applies. Firstmate runs where it is cloned (Mac or Linux), so most rows describe what it adds on top of that machine.

### Machine and tools

| | Mac | VPS today | VPS upgraded | Claude Code cloud | Other hosted | Firstmate |
|---|---|---|---|---|---|---|
| **Environment** | macOS, arm64, 11 cores, 18 GB ([vps][vps-glance]) | Ubuntu 26.04, 2 vCPU, 3.8 GB (2.4 free), no swap; CX23 ([vps][vps-glance], [siz][siz-today]) | Same box; CX33 gives 4 vCPU / 8 GB; swap proposed ([siz][siz-rec]) | Fresh Ubuntu 24.04 Firecracker VM per session, 4 vCPU / 15.7 GiB / 30 GB writable, root; reclaimed when idle ([cc §2][cc2], [sp §10][sp10]) | Codex: container, size unpublished. Cursor: Ubuntu VM with desktop. Copilot: Actions runner, 59-min cap ([op][op-cmp]) | Wherever it's cloned; off the machine, a whole "secondmate" home on an SSH host ([fm][fm-where]) |
| **Tools** | All four harnesses, Treehouse, Docker ([vps][vps-glance]) | Claude Code only; Node, Python, Swift, Docker; no `jq`, `rg`, Treehouse ([vps][vps-glance]) | Add `jq`, Treehouse (needs Go), the preferred agent if not `claude` ([vps][vps-env]) | Broad toolchain, but `gh` missing; more by a root setup script, cached; no Herdr or Treehouse ([cc §3][cc3]) | Setup script, Dockerfile or `copilot-setup-steps.yml` ([op §1][op1], [§2][op2], [§3][op3]) | Needs `git`, `jq`, `herdr`, `treehouse`, `tasks-axi` and more on each host ([fm][fm-remote]) |
| **Web** | Yes ([vps][vps-glance]) | Yes: HTTPS to web, GitHub, npm ([vps][vps-web]) | Yes ([vps][vps-web]) | Allowlist ("Trusted") by default; Full or Custom per environment. WebFetch obeys the allowlist; WebSearch works ([cc §4][cc4], [sp §2][sp2]) | Codex: off by default. Cursor: on. Copilot: firewall allowlist ([op][op-cmp]) | The host's ([fm][fm-qs]) |
| **Browser** | Chrome, Safari, Playwright ([vps][vps-glance]) | **No**: cached headless shell lacks 15 system libraries; no display ([vps][vps-browser]) | Headless, after `playwright install-deps` (root) or the Playwright Docker image ([vps][vps-browser]) | Headless Chromium pre-installed; trust the proxy CA; allowlisted hosts only ([sp §1][sp1]) | Cursor: full desktop and computer use. Copilot: Playwright MCP on by default. Codex: none documented ([op §2][op2], [§3][op3], [§1][op1]) | Requires `chrome-devtools-axi`; headless on a server unverified ([fm][fm-axi]) |
| **File system** | Home folder ([vps][vps-glance]) | Own home, 26 GB free; `sudo` with a password ([vps][vps-glance]) | Same ([vps][vps-glance]) | Ephemeral VM; only pushed work and the conversation persist ([cc §2][cc2]) | Ephemeral per task; Cursor keeps snapshots ([op §2][op2]) | The host's; worktree per task ([fm][fm-walk]) |
| **Herdr** | 0.9.0, VPS saved as a machine ([hv][hv-model]) | 0.9.0; driven over `ssh … bash -lc 'herdr …'` ([vps][vps-herdr]) | 0.9.2: `herdr --machine <label>`, `machine status`, no shell quoting ([vps][vps-upgrade]) | None ([cc §8][cc8]) | None ([del §5][del5]) | One of five backends; remote homes always run on Herdr ([fm][fm-remote]) |
| **Git worktrees** | Treehouse ([vps][vps-glance]) | Plain git only; no Treehouse ([vps][vps-git]) | Treehouse, or `git worktree add` / `herdr worktree create` ([vps][vps-git]) | Plain `git worktree` works; parallelism is sub-agents or projects ([cc §8][cc8], [sp §6][sp6]) | One branch per task ([op][op-cmp]) | `treehouse get` per task ([fm][fm-walk]) |

### The work itself

| | Mac | VPS today | VPS upgraded | Claude Code cloud | Other hosted | Firstmate |
|---|---|---|---|---|---|---|
| **GitHub push and PR** | `gh` ([del §1][del1]) | Yes: `gh` logged in, SSH auth works; writes not tried ([vps][vps-git]) | Yes ([vps][vps-git]) | Push to the checked-out branch, its own `claude/…` or a new one it names (an existing branch: untested); Create PR or the GitHub MCP tools; GraphQL blocked, REST for the attached repo only ([cc §6][cc6], [sp §4][sp4]) | All push and open PRs: Codex from the web, Cursor `cursor/…` or a given branch, Copilot one `copilot/…` PR ([op][op-cmp]) | The host's `gh`; branch `fm/<id>`; PR per task; guarded merge ([fm][fm-gh]) |
| **Loads skills and instructions** | Current skills and global instructions ([vps][vps-glance]) | Older skill set; no global instructions; hand-made deny rules, memory on ([vps][vps-env]) | Current skills, shared `AGENTS.md`, rule table, hook, memory off ([vps][vps-env]) | Repo `CLAUDE.md` and `.claude/skills`, claude.ai-enabled skills; **not** the laptop's `~/.claude`. This repo's `skills/` isn't loaded by default, but skills installed into the VM's `~/.claude/skills` load ([cc §5][cc5], [wf §1][wf1]) | Repo `AGENTS.md` everywhere; this repo's skills as they are nowhere; only Cursor carries anything personal: account User Rules and a `~/.cursor/skills` sync ([op][op-cmp], [op §2][op2]) | Its own `AGENTS.md` and skills replace ours ([fm][fm-map]) |
| **Orchestration with sub-agents** | Yes; the baseline ([del §1][del1]) | Old `orchestrate-effort` installed; `handover`, `close-effort` missing; RAM fits one or two agents ([del §3.1][del31], [siz][siz-tiers]) | As the Mac; CX33 fits two or three agents ([siz][siz-tiers]) | Sub-agents work, one level deep; idle expiry kills background work; projects run parallel threads ([cc §8][cc8], [wf §3][wf3]) | Task-sized. Cursor has sub-agents; Codex and Copilot unverified; Copilot capped at 59 min ([op][op-cmp]) | Forbids harness sub-agents: visible workers with on-disk state instead ([fm][fm-map]) |

### Delegating and hearing back

| | Mac | VPS today | VPS upgraded | Claude Code cloud | Other hosted | Firstmate |
|---|---|---|---|---|---|---|
| **Started by a local agent** | handover-to-herdr ([del §2][del2]) | `herdr` over SSH; workspace create and close probed ([del §3.1][del31]) | `herdr --machine … agent start/prompt` ([del §3.1][del31]) | `claude --cloud` from an agent's shell untested (prints a URL and exits in a terminal); a routine's API trigger; `create_session` from inside a cloud session, untested ([cc §7][cc7], [del §4.1][del41]) | Yes: `codex cloud exec`, Cursor `POST /v1/agents`, `gh agent-task create` ([op][op-cmp]) | `fm-spawn.sh`; remote through `fm-on.sh` over SSH ([fm][fm-remote]) |
| **Watched and answered** | Herdr sidebar; `agent read/prompt` ([del §2][del2]) | Mac window shows its agent states; `agent read/prompt` over SSH ([del §3.2][del32]) | Same through `--machine`; Remote Control messaging both ways, untested ([del §3.2][del32]) | claude.ai and phone; `claude -p "<msg>" --cloud <id>` sends; no CLI status read; from inside a cloud session `list_sessions`/`get_session` read every session, Remote Control ones too ([cc §9][cc9]) | All watchable from a shell; answer by API only in Cursor, by `@copilot` PR comment in Copilot, web or `@codex` PR comment in Codex ([op][op-cmp]) | Zero-token watcher; durable inbox with receipts ([fm][fm-walk]) |
| **Notifications** | `osascript` ([del §2][del2]) | None proven: no `osascript` or `notify-send`; a Herdr notification "shown" somewhere unknown ([vps][vps-notif]) | Remote Control push, or a Mac-side `agent wait` watcher; both untested ([del §3.3][del33]) | Desktop and project notifications; a `PushNotification` tool exists, phone delivery untested; the PR is the done signal ([cc §9][cc9], [del §4.3][del43]) | Cursor: iOS push. Copilot: GitHub review request. Codex: unverified ([op][op-cmp], [del §2][del2]) | In the first mate's chat; a `command:` hook for a phone; no phone channel ([fm][fm-qs]) |
| **Moving back** | Same branch or stacked ([del §2][del2]) | Git plus safe-handover checks over SSH; VPS to Mac impossible ([hv][hv-checks], [hv][hv-back]) | Same checks through `--machine` ([vps][vps-perm]) | `claude --teleport` copies it; the docs don't say the cloud session stops; assume it may still be running until E12 settles it ([cc §10][cc10], [del §4.4][del44]) | Codex `apply`; check out the branch ([op][op-cmp]) | Relaunch from the brief on disk ([fm][fm-qs]) |
| **Cost** | Owned; plan usage ([siz][siz-sum]) | €5.99/month plus plan usage ([siz][siz-sum]) | CX33 €8.99/month (+€3), a rescale Hetzner may refuse for now ([siz][siz-avail]) | Plan usage, no VM charge; one-time $100 / $250 promo credit, live and spent first; its rate-limit window (`resetsAt`) resets 5 November, a window reset rather than a refill ([cc §11][cc11]) | Codex in Plus $20; Cursor Pro $20 plus API prices; Copilot Pro $10 plus AI credits ([op][op-cmp]) | Free; spends the owner's subscriptions ([fm][fm-qs]) |

[cc2]: cloud-agents-claude-code.md#2-environment
[cc3]: cloud-agents-claude-code.md#3-tools-and-commands
[cc4]: cloud-agents-claude-code.md#4-web-and-browser
[cc5]: cloud-agents-claude-code.md#5-what-loads
[cc6]: cloud-agents-claude-code.md#6-github
[cc7]: cloud-agents-claude-code.md#7-starting-it
[cc8]: cloud-agents-claude-code.md#8-long-work
[cc9]: cloud-agents-claude-code.md#9-watching-and-answering
[cc10]: cloud-agents-claude-code.md#10-moving-it
[cc11]: cloud-agents-claude-code.md#11-cost-and-limits
[sp-short]: cloud-agents-session-probe.md#short-answer
[sp1]: cloud-agents-session-probe.md#1-headless-browser
[sp2]: cloud-agents-session-probe.md#2-webfetch-and-websearch
[sp4]: cloud-agents-session-probe.md#4-github-proxy
[sp6]: cloud-agents-session-probe.md#6-worktrees
[sp10]: cloud-agents-session-probe.md#10-disk
[sp-oq]: cloud-agents-session-probe.md#answers-to-69s-open-questions
[wf-short]: cloud-agents-session-workflow.md#short-answer
[wf1]: cloud-agents-session-workflow.md#1-the-layers-in-a-cloud-session
[wf2]: cloud-agents-session-workflow.md#2-carrying-the-skills-and-global-instructions-into-cloud-sessions
[wf3]: cloud-agents-session-workflow.md#3-the-effort-workflow-in-a-cloud-session
[wf4]: cloud-agents-session-workflow.md#4-suggestions
[wf-oq]: cloud-agents-session-workflow.md#open-questions
[ma-fit]: cloud-agents-managed-agents.md#5-fit-for-this-maintainer
[op-cmp]: cloud-agents-other-providers.md#comparison
[op1]: cloud-agents-other-providers.md#1-openai-codex-cloud
[op2]: cloud-agents-other-providers.md#2-cursor-cloud-agents-and-the-agent-cli
[op3]: cloud-agents-other-providers.md#3-github-copilot-cloud-agent-formerly-coding-agent
[vps-glance]: cloud-agents-vps.md#at-a-glance
[vps-browser]: cloud-agents-vps.md#headless-browser
[vps-web]: cloud-agents-vps.md#web-access-scripts-and-file-system
[vps-git]: cloud-agents-vps.md#git-worktrees-and-github
[vps-herdr]: cloud-agents-vps.md#herdr-across-machines
[vps-upgrade]: cloud-agents-vps.md#what-an-upgrade-to-092-would-change
[vps-notif]: cloud-agents-vps.md#notifications
[vps-env]: cloud-agents-vps.md#the-environment-on-the-vps
[vps-perm]: cloud-agents-vps.md#permissions-on-the-other-machine
[siz-sum]: cloud-agents-vps-sizing.md#summary
[siz-today]: cloud-agents-vps-sizing.md#the-vps-today-vps
[siz-tiers]: cloud-agents-vps-sizing.md#2-workload-to-smallest-tier
[siz-avail]: cloud-agents-vps-sizing.md#availability-what-not-available-means
[siz-rec]: cloud-agents-vps-sizing.md#6-recommendation-per-workload
[del1]: cloud-agents-delegation.md#1-todays-flow-and-the-steps-that-depend-on-where-the-agent-runs
[del2]: cloud-agents-delegation.md#2-the-options-side-by-side
[del31]: cloud-agents-delegation.md#31-handing-over-through-herdr-13s-path
[del32]: cloud-agents-delegation.md#32-watching-and-answering
[del33]: cloud-agents-delegation.md#33-notifying
[del41]: cloud-agents-delegation.md#41-handing-over
[del43]: cloud-agents-delegation.md#43-notifying
[del44]: cloud-agents-delegation.md#44-continuing-and-keeping-two-orchestrators-off-one-branch
[del5]: cloud-agents-delegation.md#5-other-hosted-agents-for-delegation-only
[fm-walk]: cloud-agents-firstmate.md#how-firstmate-delegates-walkthrough
[fm-where]: cloud-agents-firstmate.md#where-crew-agents-run
[fm-remote]: cloud-agents-firstmate.md#remote-secondmates-in-depth
[fm-gh]: cloud-agents-firstmate.md#github-access
[fm-qs]: cloud-agents-firstmate.md#the-same-questions-as-the-other-research-tickets
[fm-map]: cloud-agents-firstmate.md#mapped-against-this-repos-workflow
[fm-axi]: cloud-agents-firstmate.md#the--axi-tools
[hv-model]: herdr-vps.md#the-machine-model
[hv-checks]: herdr-vps.md#safe-handover-checks
[hv-back]: herdr-vps.md#vps-to-mac

## What each can do that the others can't

- **Mac:** a working notification (`osascript`), a desktop browser the agent can drive, every harness, and the maintainer at the keyboard for trust prompts and approvals ([vps][vps-glance]).
- **VPS:** runs this repo's own skills and Herdr with the laptop closed, on a machine the maintainer controls and can install anything on, for a flat €5.99 a month ([vps][vps-glance], [siz][siz-sum]).
- **Claude Code cloud:** a bigger machine than the VPS (15.7 GiB) per session, many sessions in parallel, no machine to maintain, reachable from the phone, a headless browser out of the box, and a one-time promo credit already being spent ([cc §2][cc2], [cc §11][cc11], [sp §1][sp1]). Projects add a coordinator with parallel threads that auto-fix their own PRs ([cc §8][cc8]).
- **Other hosted:** Cursor drives a full desktop and takes API follow-ups; Copilot lives inside GitHub (assign an issue, get a PR) and, under GitHub's general rule, uses free Actions minutes on a public repo; Codex applies a finished diff straight into a local tree ([op][op-cmp]). Cursor's My Machines can also run a cloud agent's tool calls on the VPS ([op §2][op2]).
- **Firstmate:** survives its own restart and its workers' deaths, because the brief and the status live on disk, and it has a real remote protocol (routed requests with receipts, a readiness doctor) ([fm][fm-walk], [fm][fm-remote]).

## Decisions for the maintainer

Each has options and a recommendation. "E" numbers point to the proposed experiments below.

### D1. Where does an orchestrated effort run?

- **Options:** (a) the Mac only; (b) the Mac, or the VPS when the laptop will be closed; (c) Claude Code cloud sessions for whole efforts; (d) the Mac or the VPS orchestrates, and hosted agents take single tickets.
- **Recommendation: (b) now, (d) later.** The VPS is the only off-Mac place where this repo's skills, Herdr and the effort workflow run unchanged ([del §2][del2]). Cloud orchestration waits on E16 and E17: E1 showed skills can be carried into the VM and a session can push a named branch, but the carrier isn't set up yet, idle expiry kills sub-agents, sub-agents can't nest, permission prompts stall an unattended run, and an agent-side start is untested ([cc §8][cc8], [wf §3][wf3], [wf §4][wf4]). A single-session effort (think and build in one cloud session the maintainer watches) is the first cloud shape to try once E16 works. Hosted agents as delegates wait until one is chosen (D7).

### D2. Upgrade Herdr to 0.9.2 on both machines?

- **Options:** (a) upgrade both now; (b) stay on 0.9.0 and build on `ssh … bash -lc 'herdr …'`; (c) wait for a later release.
- **Recommendation: (a), at a quiet moment (E3).** `herdr --machine` removes the login-shell wrapper and remote-shell quoting, keeps the host out of skill text, and 0.9.2 adds `machine status` for a readiness check ([vps][vps-upgrade]). The cost is a VPS server restart that ends its idle agent pane. Herdr 0.9.2 was released on 2026-09-29.

### D3. Set up the VPS environment the same way as the Mac?

- **Options:** (a) run set-up-machine on the VPS (on `main` since #66 merged), plus install `jq` and a worktree tool; (b) keep the hand-made VPS setup; (c) reinstall the VPS from scratch.
- **Recommendation: (a) (E6, E8).** Without it a VPS orchestrator has old skills, no global instructions, memory on, and can't run `handover` or `close-effort` ([vps][vps-env], [del §3.1][del31]). Decide first which of the 4 memory folders to keep, since its diff removes memory files (backed up) and can carry what's worth keeping into the shared file in the same approval. For the worktree tool, install Treehouse (and Go) rather than special-casing `git worktree add` on the VPS; Firstmate also requires Treehouse on a remote host ([fm][fm-remote]).

### D4. Resize the VPS?

- **Options:** (a) stay on CX23; (b) add 2-4 GB of swap; (c) rescale to CX33 with "CPU and RAM only" (+€3/month, reversible); (d) burst: create a big server from a snapshot and delete it after; (e) move provider.
- **Recommendation: (a) plus (b) now; (c) when a browser or a second agent runs there.** One agent fits with 2.4 GB spare, but with no swap an out-of-memory spike kills processes ([siz][siz-rec]). Hetzner's "not available" mark is a temporary per-customer, per-location restriction on new servers and rescales; the running CX23 is unaffected, so a refused rescale costs only a retry another day ([siz][siz-avail]). Don't move provider: Hetzner CX is the cheapest per GB of everything compared ([siz][siz-sum]).

### D5. A headless browser on the VPS?

- **Options:** (a) `npx playwright install-deps chromium` as root; (b) the Playwright Docker image, which the user can already run; (c) none: keep browser work on the Mac.
- **Recommendation: (c) until a task needs it, then (b) (E7).** Docker needs no root and leaves the system untouched; measure its memory next to an agent before relying on it on CX23 ([vps][vps-browser]).

### D6. How do skills and instructions reach a Claude Code cloud session?

This repo keeps its skills in `skills/`, not `.claude/skills/`, and cloud sessions don't load the laptop's `~/.claude/skills` or `~/.claude/CLAUDE.md`, so `/orchestrate-with-handoff` doesn't resolve in a fresh cloud session ([cc §5][cc5], [del §4.1][del41]). The VM's own `~/.claude/skills` does load, even mid-session ([wf §1][wf1]).

- **Options:** (a) enable the skills on the claude.ai account (they load in every cloud session; kept in sync by hand); (b) commit a `.claude/skills/` in this repo (only sessions on this repo get them; other projects don't); (c) have the cloud environment's setup script (or a SessionStart hook in this repo) install the skills and global instructions into the VM's home (one source of truth, every repo on that environment; skills placed there load, a `~/.claude/CLAUDE.md` written there is untested); (d) don't carry skills: the handover brief carries the rules the session needs.
- **Recommendation: (c), now the likely answer; confirm it in E16; keep (a) only for skills that must also reach Cowork; don't restructure the repo for (b).** [wf §2][wf2] has the setup script (pinned `npx skills add … -g -a claude-code`, `gh`, a cloud copy of the global instructions) and a SessionStart hook for this repo. Until E16 passes, use cloud sessions only with self-contained briefs (d). The same unknown ("does the cloud agent read a home folder the setup script filled?") is open for Codex and Copilot too ([op][op-oq]).

### D7. Which hosted agent, if any, for single-ticket delegation?

- **Options:** (a) Claude Code cloud only; (b) add Copilot ($10/month, lives in GitHub, 59-minute cap, no shell steering; answer by `@copilot` PR comment); (c) add Cursor ($20 plus API prices, best API, user-skill sync and account User Rules, browser); (d) add Codex (in ChatGPT Plus, no shell follow-ups; answer on the web or by `@codex` PR comment); (e) none.
- **Recommendation: (a) first; (b) if a second is wanted.** It needs no sign-up, and the promo credit, already live, can cover a first try ([cc §11][cc11]). Copilot is the cheapest trial and fits a public repo ([op §3][op3]); Cursor is the strongest delegate but bills model use at API prices ([op §2][op2]). Whichever is used, the delegate brief must carry the rules, and the result is read back as a branch through `gh`, as Firstmate's Grok Bot pattern does ([fm][fm-map]). Score any candidate against Firstmate's five-point backend contract ([fm][fm-contract]).

### D8. What does an orchestrator delegate to, and from which base?

Two findings from running this effort: harness sub-agent worktrees were created from an old `main`, not the stacked effort branch, and every delegate had to fast-forward itself ([del §7][del7]); and Firstmate forbids its orchestrator the harness's sub-agent tool because sub-agent workers died with a restarted orchestrator and left no record ([fm][fm-map]).

- **Options:** (a) keep in-process sub-agents and pass the effort branch as the base explicitly; (b) for efforts off the Mac, delegate to Herdr tabs with a status file; (c) move to Firstmate's model everywhere.
- **Recommendation: (a) now, as a small fix to the orchestrating skills; (b) as part of #15 for VPS efforts.** Sub-agents are fine on the Mac, where the orchestrator rarely restarts and each ticket is committed; the base branch fix is needed by every stacked effort today. Not landed yet: on `main` (2026-09-30), orchestrate-effort's step 4 still starts each delegate "in its own git worktree" with no base named.

### D9. How does done-or-blocked reach the maintainer from off the Mac?

- **Options:** (a) Claude Code Remote Control push from the VPS session; (b) a Mac-side watcher (`herdr agent wait … --until done --until blocked`, then `osascript`); (c) Herdr's toast delivery on the Mac client; (d) GitHub notifications on the pull request.
- **Recommendation: (a) for the VPS once E5 proves it, with (b) as the fallback; (d) for cloud sessions.** (a) is the only route that needs no Mac online ([del §3.3][del33]); (b) lives only as long as the watching session. For cloud sessions nothing else is documented ([del §4.3][del43]); a cloud session's main loop has a `PushNotification` tool whose phone delivery E19 tests. New: from inside a cloud session, `list_sessions` shows every session's state, Remote Control sessions on the Mac or VPS included, with a needs-action flag, so a cloud orchestrator can see a blocked local one and the reverse ([cc §9][cc9]). E4 settles (c), whose documented default is `off` although a VPS probe returned `shown` ([del §3.3][del33]).

### D10. Does the VPS need to reach the Mac?

- **Options:** (a) no, the Mac always checks; (b) Claude Code cross-session messaging over Remote Control (text only, both directions, no inbound access); (c) SSH into the Mac (Remote Login plus Tailscale or a reverse tunnel).
- **Recommendation: (a), plus (b) where a VPS agent must ask the Mac something (E5).** (c) opens the Mac to inbound access for little gain ([hv][hv-back], [del][del16]).

### D11. Guard disruptive remote Herdr commands in the rule table?

- **Options:** (a) add rows at `ask` for `herdr … server stop` and `workspace close --group` (and their `--machine` forms) to set-up-machine's `rules.json`; (b) rely on the skills' wording.
- **Recommendation: (a),** as new rows in the rule table: `--machine` makes stopping every agent on the VPS one local command ([vps][vps-perm]).

### D12. The promo credit and the one unused cloud session

- **Options:** (a) spend it on the cloud experiments (E16, E17) before it expires; (b) leave it.
- **Recommendation: (a).** The credit is live and in use: #78's cloud session drew on a promotional rate-limit pool whose window resets (`resetsAt`) on 5 November (midnight PST); that is a window reset, not a refill. Inferred: it matches the reported 4 November expiry ([cc §11][cc11]). The session that E1 needed has been used. Read the remaining balance at claude.ai/settings/usage.

### D13. Adopt Firstmate?

- **Options:** (a) adopt it; (b) borrow ideas; (c) ignore it.
- **Recommendation: (b).** Adopting it would replace the effort workflow, run workers with bypassed permissions and strip AI trailers ([fm][fm-map]). Borrow: the status-file protocol (for #16), a readiness check with `fixable`/`human` gaps and "unreachable is unknown" (for #13), relaunch from a brief on disk (for #15), a worktree-isolation check in delegate briefs, and `--match-head-commit` in close-effort's merge ([fm][fm-map]).

[op-oq]: cloud-agents-other-providers.md#open-questions
[fm-contract]: cloud-agents-firstmate.md#the-contract-a-delegate-backend-must-meet
[del7]: cloud-agents-delegation.md#7-how-this-effort-itself-was-handed-over-material-for-15
[del16]: cloud-agents-delegation.md#agents-on-the-mac-and-the-vps-can-see-each-others-state-16

### The maintainer's answers (2026-09-30)

| | Answer | Status |
|---|---|---|
| D1 | The Mac for now; test the VPS and cloud sessions **at the same time**, the cloud first while the promo credit lasts | Changed |
| D2 | Yes | Agreed |
| D3 | Yes; which memory folders to keep is still to pick | Agreed |
| D4 | Hetzner won't rescale now; open to a pricier tier or another European provider. Needs its own research: providers, latency, shared against dedicated vCPU | Open |
| D5 | A headless browser on the VPS from day zero, in the environment | Changed |
| D6 | The setup script or SessionStart hook installs the global skills and instructions | Agreed |
| D7 | Yes to hosted agents for single tickets; wants pros, cons and costs per agent before choosing which tickets | Open |
| D8 | Needed a plain explanation; plan: keep effort #45 open, close the research tickets, open action items | Open |
| D9 | Needed a plain explanation; phone push from a cloud session is re-tested in #80 | Open |
| D10 | Fire and forget is the flow, but keep the channel two-way where it exists | Changed |
| D11 | No guard rules; agents work freely across the Mac and the VPS | Changed |
| D12 | Yes; the maintainer confirmed on the usage page that #78's session was paid from the promo credit | Agreed |
| D13 | Don't adopt; understand its concepts and pick what to borrow | Open |

### Follow-up research on the open decisions (2026-09-30)

- **D4, redone 2026-10-02 ([vm](cloud-agents-vps-math.md)).** The maintainer found the CX23 can't run one agent with tests, a browser test or anything in parallel; the rescale dialog offers CPX12 and up, not CX33; budget $10-15, up to about $25. Five parallel agents with 3 test runs and 2 browsers need about 12 GB, so 16 GB: the recommendation is now **netcup VPS 2000 G12.5** (8 vCores, 16 GB, €22.62 net, $25.56, on 12 months), or VPS 1000 (8 GB, $13.76) if $15 is the ceiling. Earlier ([vp](cloud-agents-vps-providers.md#5-ranked-shortlist), #86): Hetzner CX and CAX are still not orderable. The recommendation was **netcup Root Server RS 2000** (8 dedicated EPYC cores, 16 GB, 256 GB NVMe, €34.20 net a month on 12 months, 30-day money-back), with the CX23 kept alongside for 2-4 weeks. Fallbacks: netcup VPS 2000 (€22.62) and OVHcloud VPS-4 (€23.49, no term). Latency from the Mac is 54-102 ms across providers, too close to choose on.
- **D7 ([co](cloud-agents-costs.md#short-answer), #87).** Metered vendors charge Claude Opus at Anthropic's list price, so a ticket costs about the same everywhere (estimates: $1 small, $4 medium, $28 for a five-ticket effort); the Claude plan turns that into $0 cash inside its windows. Hold the plan and the VPS; add Copilot Pro ($10) only for a second delegate; try Jules's free tier; skip the rest for now. The promo credit's claim date (7 October) and expiry (4 November) come from press reports only.
- **D13 ([fd](cloud-agents-firstmate-deep-dive.md#3-what-to-borrow), #88).** 18 ideas ranked. The first two are small skill changes: a worktree-isolation check in delegate briefs (**orchestrate-effort**, **implement**) and a guarded merge with `--match-head-commit` (**close-effort**).

## Proposed experiments

What the research couldn't settle inside the spec's safe zone. Each needs the maintainer, or their go-ahead.

| # | Experiment | Settles | Cost | Risk | Source |
|---|---|---|---|---|---|
| E1 | **Done by #78** ([sp][sp-oq]): the maintainer's `claude --cloud "say hi"` gave the session, and it answered VM size and user, session ID output, browser, WebFetch/WebSearch, skills and `AGENTS.md` loading, push to a new branch, and REST through the proxy. Left open: phone push (E19), push to an existing branch (E20), setup-script loading (E16). The original plan: **the one remaining cloud probe, run by the maintainer in a real terminal.** On a throwaway `probe/…` branch of this public repo, `claude --cloud "<read-only probe prompt>"` (the prompt is in cc's Exploration log, row 11). Note what the CLI prints; results pushed to the probe branch; then delete the branch. Add: list skills, try a push to a second branch, "notify me when done", `gh api …/issues/45/sub_issues`. To test D6 (c), give the environment a setup script that installs the skills into the VM's home first | VM size and user, session ID output, browser, WebFetch/WebSearch under Trusted, skills and `AGENTS.md` loading, push to another branch, phone push, REST through the proxy | One small session of plan usage or promo credit | Low: public repo, throwaway branch, read-only prompt | [cc open questions][cc-oq] |
| E2 | **Done by #78**: `list_sessions` inside the cloud session shows no session from probe 1, and `get_session` shows the promo credit in use ([cc open questions][cc-oq]). Left: reading the balance. The original: check claude.ai for a session from probe 1 (it exited 1, cause unknown) and archive it; read the promo credit's balance and terms | Whether probe 1 created a session; D12 | None | None | [cc §7][cc7] |
| E3 | Upgrade Herdr to 0.9.2 on both machines; rerun a `probe-` workspace create, `pane run`, `pane read`, close and `agent list` through `--machine`; record `machine status --json` | D2; the command shapes #13 and #16 use | Minutes | The VPS server restart ends its panes (one idle agent today); live handoff is experimental | [vps][vps-upgrade], [del open questions][del-oq] |
| E4 | With the maintainer at the Mac: `herdr notification show` on the VPS with the Mac window on Local, then on the VPS, then with `delivery = "system"` on the Mac | Where a VPS notification appears; D9 (c) | Minutes | None | [vps][vps-notif] |
| E5 | `claude --remote-control` in a throwaway VPS Herdr tab; a Mac session on Remote Control; check `ListAgents`, `SendMessage` both ways, `isolatePeerMachines`, and a phone push on "notify me when done" | D9 (a), D10 (b) | Minutes | One-time Remote Control consent on the VPS (a config change); registers a session with Anthropic | [del][del16], [del §3.3][del33] |
| E6 | set-up-machine on the VPS, now that #66 has merged: pull the clone, have a VPS agent run the skill to its one diff, show it, write on approval, check with `verify.py` | D3 | Minutes | Removes memory files (backed up); hand-made rules stay, as `stricter` or `extra`: pick memory to keep first | [vps][vps-env] |
| E7 | Pull the Playwright Docker image (`…-resolute`) on the VPS, load one page headless with `--init --ipc=host`, record memory next to a running agent | D5; replaces the sizing estimates | A multi-GB image on a 26 GB-free disk | Low; no root, removable | [vps][vps-browser], [siz][siz-rec] |
| E8 | Install `jq`, Go and Treehouse on the VPS | D3's worktree tool | Minutes | Low | [vps][vps-git] |
| E9 | Add 2-4 GB of swap on the VPS | D4 (b) | Disk space | Low; a system config change | [siz open questions][siz-oq] |
| E10 | Rescale CX23 → CX33 "CPU and RAM only", time the downtime, rescale back | D4 (c) | A few cents plus minutes of downtime | May be refused while Hetzner's restriction lasts; the server stays as it was | [siz][siz-avail] |
| E11 | A routine with an API trigger whose prompt runs a handoff; fire it from a local agent; read the session URL | Whether an agent can hand an effort to the cloud unattended | One routine run of plan usage; counts toward the daily run cap | Low; the token is made on the web | [cc §7][cc7], [del §4.1][del41] |
| E12 | After a `claude --teleport`, check whether the cloud original keeps running, and archive it | How #15 keeps two orchestrators off one branch | None | None | [del open questions][del-oq] |
| E13 | Hosted trials, only if D7 picks one: a Copilot task on a throwaway branch (`gh agent-task create`), a Codex environment whose setup script installs skills, a Cursor API agent | D7; user skills and notifications for each | $10-20 a month and a sign-up each; Cursor adds API prices | Low on a public repo | [op open questions][op-oq] |
| E14 | Firstmate's `fm-remote-doctor.sh` read-only on the VPS in a throwaway account | How far the VPS is from a Firstmate remote home | Installs Firstmate's tools | Low in a separate account | [fm open questions][fm-oq] |
| E15 | Desktop app SSH session to the VPS: what it installs, which settings and skills load, whether Herdr sees it | Whether the desktop app is a way onto the VPS | Minutes | Changes the app's config | [vps][vps-desktop] |
| E16 | A personal cloud environment with the setup script from [wf §2][wf2], pinned to a commit with the whole effort family; start one session, check `/skills` and quote a rule line from the global instructions | D6 (c); whether a `~/.claude/CLAUDE.md` written by the script loads | Minutes on claude.ai, one small session | Low; a bad script fails the start | [wf §4][wf4] |
| E17 | One `create_session` child from a cloud session, on a throwaway branch of this repo with `outcome_branch` set: does it get the environment's skills, push there, show in `list_sessions`? Then archive it | An agent-side cloud start; a `handover-to-claude-code-cloud` skill; D1 | One session of plan usage | Low on a public repo and throwaway branch | [wf §4][wf4] |
| E18 | Leave a probe session idle; note when reopening gives a fresh VM, and whether setup-script files survive | Idle expiry; how long a cloud orchestrator may wait on a question | None | None | [cc open questions][cc-oq], [wf open questions][wf-oq] |
| E19 | Ask a cloud session's main loop to "notify me when done" and watch the phone | D9 for cloud sessions | None | None | [cc open questions][cc-oq] |
| E20 | A cloud session on a throwaway `probe/…` branch pushed from the Mac, asked to push a commit to it | Whether a cloud orchestrator can continue an effort branch made elsewhere (#15) | One small session | Low; throwaway branch | [cc open questions][cc-oq] |

[cc-oq]: cloud-agents-claude-code.md#open-questions
[del-oq]: cloud-agents-delegation.md#open-questions
[siz-oq]: cloud-agents-vps-sizing.md#open-questions
[fm-oq]: cloud-agents-firstmate.md#open-questions
[vps-desktop]: cloud-agents-vps.md#where-the-desktop-app-fits

## The three build tickets, re-scoped

The full re-scoping comments are posted on each ticket; in short:

- **[A thinking session on the Mac can hand over to an orchestrator on the VPS (#13)](https://github.com/yahyabedirhan/skills/issues/13).** The shape is settled: **handover-to-herdr** gains a target machine (Local or a saved Herdr machine's label), and the VPS's own environment defaults name its worktree tool and agent. The host comes from Herdr's catalog. Build it on `herdr --machine` after D2, with the VPS set up by D3; notifications follow D9. Handing over to a Claude Code cloud session is out of its scope: no agent-side start is proven yet (see D1, E11, E17).
- **[An unfinished effort can be handed to a new orchestrator (#15)](https://github.com/yahyabedirhan/skills/issues/15).** Detection and the same-branch or stacked question are settled; the per-place "old side is idle and pushed" checks are listed. New scope from this run: a continuation checks for a newer handoff, and delegates must branch from the effort branch (D8). Cloud continuations stay open until E12 and E20 (E1 showed a session can push a new branch it names).
- **[Agents on the Mac and the VPS can see each other's state (#16)](https://github.com/yahyabedirhan/skills/issues/16).** Settled: every read works over SSH today and through `--machine` after D2; the permission table is in [vps][vps-perm]. New: a status file per remote orchestrator (from Firstmate), and Remote Control messaging for the reverse direction (E5). It can land first, and #13 and #15 build on it.

## The spec's decisions, as the research left them

- **Research only** held: no skill, instruction or machine was changed. The only writes outside this repository were throwaway Herdr workspaces on the VPS (closed), two `herdr notification show` calls on the VPS ([vps][vps-log], [del][del-log]), two throwaway probe branches (deleted) ([cc][cc-log]), and scratch files on the Mac (fetched docs and a scratch SSH config alias, all outside the repo, not committed).
- **Safe probes:** the VPS probes stayed read-only apart from the throwaway workspaces and the two notifications. Of the two allowed cloud sessions, the first probe exited 1 without evidence of a session; the second was refused by the agent's local permission check before anything ran. So the first pass had **no first-hand facts about the cloud VM**, and E1 handed the one unused session to the maintainer. **Update (#78):** the maintainer started it with `claude --cloud "say hi"`, and the first-hand facts now live in [sp][sp-short] and [wf][wf-short].
- **Twelve research files, this synthesis and the guide** (`cloud-agents-guide.html`) are under `docs/research/`, each research file with an exploration log: six from the first pass, three from #78's cloud session and three from #86-#88. The Firstmate ticket (#75) was added mid-effort by the maintainer.
- **The build tickets** stay blocked, now on the decisions and experiments above rather than on research.

## Corrections made while writing this synthesis

- **Starting a cloud session from an agent.** [cloud-agents-delegation.md](cloud-agents-delegation.md) presented `claude --cloud "<one-line prompt>"` as the handover's start. The create form needs an interactive terminal and `-p` rejects it with a task ([cc §7][cc7], checked against the `headless` and `claude-code-on-the-web` docs); that file's table row, its section 4.1 and 4.4, and its #15 summary now say so. #78 then found the create form prints the session URL and exits in a real terminal; whether it runs from an agent's shell stays untested, and both files now say that.
- **Herdr's toast default.** [cloud-agents-delegation.md](cloud-agents-delegation.md) read the 0.9.2 configuration page's `delivery = "herdr"` example as contradicting a default of `off`. The config reference at `v0.9.2` gives `ui.toast.delivery` a default of `"off"` for both 0.9.0 and the current docs, so the example is how to turn it on; the VPS probe's `shown` stays unexplained, as [cloud-agents-vps.md](cloud-agents-vps.md#notifications) says.
- **A routine's fire response** returns `claude_code_session_id` as well as `claude_code_session_url` (the `routines` doc's example); [cloud-agents-claude-code.md](cloud-agents-claude-code.md#7-starting-it) listed only the URL.
- **From #78's first-hand probes** (all now in [cloud-agents-claude-code.md](cloud-agents-claude-code.md)): `claude --cloud "<task>"` prints the session URL and exits, with no live checklist; a headless Chromium is pre-installed; a blocked host gets a plain 403 with the reason in the body, no `x-deny-reason`; GitHub GraphQL is blocked entirely; a session can push a new branch it names, not only `claude/…`; the docs' "`~/.claude/*` doesn't load" means the laptop's files.
- Already corrected in the files and confirmed here: the VPS's cached headless browser can't start without 15 system libraries ([vps][vps-browser], [siz][siz-today]); Swift is on the VPS, although #13 recorded it missing ([vps][vps-perm]).

[vps-log]: cloud-agents-vps.md#exploration-log
[del-log]: cloud-agents-delegation.md#exploration-log
[cc-log]: cloud-agents-claude-code.md#exploration-log

## Exploration log

All on the maintainer's Mac on 2026-09-29, in this ticket's worktree or the session's scratch folder. Nothing ran on the VPS, no cloud session was started, and nothing was installed.

| # | Action | Changed |
|---|---|---|
| 1 | `git merge --ff-only skills/cloud-agents` (the worktree had started from an older `main`) | This worktree's branch only |
| 2 | `gh issue view` for #74, #45, #13, #15, #16, #75, with comments; read the effort handoff and every file named at the top | Nothing |
| 3 | `curl` of Herdr's `configuration.mdx` and both `config-reference.json` files at `v0.9.2`, and of Claude Code's `routines`, `claude-code-on-the-web` and `headless` pages in Markdown, to resolve the claims the files disagreed on | Copies in the scratch folder only |
| 4 | Checked the repository layout (`skills/`, no `.claude/`) and the orchestrating skill's delegate rule | Nothing |
| 5 | Wrote this file; corrected `cloud-agents-delegation.md` and `cloud-agents-claude-code.md` as listed above; one commit | These files |
| 6 | Cloud session (#78, integration): read the three #78 files and the orchestrator's own session probes; updated the file table, the short version, the matrix's Claude Code cloud cells, D1, D6, D7, D9, D12, marked E1 and E2 done, added E16 to E20 and a Managed Agents bullet, and noted the #78 corrections | This file only |
| 7 | Mac, 2026-09-30 | After #66 merged into `main`: read set-up-machine, orchestrate-effort and close-effort there, and checked the Mac's `~/.config/agents/`; updated the note at the top, the short version, the "VPS upgraded" column, D3, D8, D11, E6 and #13's re-scope | This file only |
