# Cloud agents: what each place can do, and what to decide next

The synthesis for [Research: synthesis - capability matrix, decisions and next steps for cloud agents (#74)](https://github.com/yahyabedirhan/skills/issues/74), under [Spec: research cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45). **Read this file first.** It puts the research side by side, lists the decisions left for the maintainer, the experiments the research couldn't run safely, and how the three blocked build tickets change. Written 2026-09-29.

Every fact here comes from one of the research files below; each matrix cell links the file (and section) behind it. Nothing new was probed for this file.

| Short name | File | Ticket |
|---|---|---|
| **cc** | [cloud-agents-claude-code.md](cloud-agents-claude-code.md): Claude Code's cloud sessions, routines, projects | #69 |
| **op** | [cloud-agents-other-providers.md](cloud-agents-other-providers.md): Codex, Cursor, Copilot, and the rest | #70 |
| **vps** | [cloud-agents-vps.md](cloud-agents-vps.md): the VPS compared with the Mac, Herdr across machines | #71 |
| **siz** | [cloud-agents-vps-sizing.md](cloud-agents-vps-sizing.md): VPS sizing and other providers | #72 |
| **del** | [cloud-agents-delegation.md](cloud-agents-delegation.md): handing over, watching, answering, notifying, continuing | #73 |
| **fm** | [cloud-agents-firstmate.md](cloud-agents-firstmate.md): Firstmate and the Treehouse author's other tools | #75 |
| **hv** | [herdr-vps.md](herdr-vps.md): the earlier Herdr-and-VPS research | — |

## The short version

- **The Mac stays home.** It is the only place with every harness, current skills, Treehouse, a browser and a working notification. Nothing researched beats it for an orchestrated effort today.
- **The VPS is one upgrade away from running an orchestrator like the Mac does.** Web, GitHub and Claude Code already work there. What's missing is small: Herdr 0.9.2 on both machines (for `herdr --machine`), the current skills and global instructions (set-up-machine, once #66 merges), a worktree tool, and a notification route. A browser needs an install. RAM (3.8 GB, no swap) limits it to one or two agents.
- **Claude Code's cloud sessions are good for tasks, not yet for efforts.** They run with the laptop closed, cost only plan usage (plus a one-time promo credit to claim, terms unverified), and push branches and open pull requests. But this repo's skills and the maintainer's global instructions don't load there as things stand, background work dies when an idle VM is reclaimed, and **a local agent can't start one with `claude --cloud`**: that command needs an interactive terminal. The maintainer can, or an agent can fire a routine.
- **The other hosted agents are delegates, not orchestrators.** Codex, Cursor and Copilot each take one prompt on one branch and return a pull request or a diff. All three can be started and watched from a shell; only Cursor takes follow-ups through an API. None loads this repo's skills as they are; only Cursor carries anything personal (account User Rules and a `~/.cursor/skills` sync) ([op §2][op2]). None is worth a sign-up before Claude Code's cloud has been tried.
- **Firstmate is worth borrowing from, not adopting.** Its best ideas for this setup: a durable status file per worker, a readiness check before handing work to another machine, "unreachable is unknown, never fail over", and not letting an orchestrator's delegates die with it.

Recommended direction, in order: upgrade Herdr and set up the VPS environment (decisions D1-D3), build #16 and then #13 on `herdr --machine`, run the one allowed cloud probe from a real terminal (experiment E1) before deciding anything about cloud orchestration, and fix the delegate-worktree base now (D8).

## Capability matrix

Columns:

- **Mac**: the maintainer's Mac today.
- **VPS today**: the small Hetzner VPS as found on 2026-09-29.
- **VPS upgraded**: the same VPS after the proposed changes: Herdr 0.9.2 on both ends, set-up-machine applied (after #66 merges), `jq` and a worktree tool installed, the Playwright system libraries or Docker image, and optionally a rescale to CX33. **Everything in this column is expected from the docs, not tried.**
- **Claude Code cloud**: a cloud session (Claude Code on the web, `claude --cloud`, routines, projects).
- **Other hosted**: Codex cloud, Cursor Cloud Agents, GitHub Copilot cloud agent (the smaller ones are in op §6).
- **Firstmate**: where it applies. Firstmate runs where it is cloned (Mac or Linux), so most rows describe what it adds on top of that machine.

### Machine and tools

| | Mac | VPS today | VPS upgraded | Claude Code cloud | Other hosted | Firstmate |
|---|---|---|---|---|---|---|
| **Environment** | macOS, arm64, 11 cores, 18 GB ([vps][vps-glance]) | Ubuntu 26.04, 2 vCPU, 3.8 GB (2.4 free), no swap; CX23 ([vps][vps-glance], [siz][siz-today]) | Same box; CX33 gives 4 vCPU / 8 GB; swap proposed ([siz][siz-rec]) | Fresh Ubuntu 24.04 VM per session, about 4 vCPU / 16 GB / 30 GB; reclaimed when idle ([cc §2][cc2]) | Codex: container, size unpublished. Cursor: Ubuntu VM with desktop. Copilot: Actions runner, 59-min cap ([op][op-cmp]) | Wherever it's cloned; off the machine, a whole "secondmate" home on an SSH host ([fm][fm-where]) |
| **Tools** | All four harnesses, Treehouse, Docker ([vps][vps-glance]) | Claude Code only; Node, Python, Swift, Docker; no `jq`, `rg`, Treehouse ([vps][vps-glance]) | Add `jq`, Treehouse (needs Go), the preferred agent if not `claude` ([vps][vps-env]) | Broad toolchain; more by a root setup script, cached; no Herdr or Treehouse ([cc §3][cc3]) | Setup script, Dockerfile or `copilot-setup-steps.yml` ([op §1][op1], [§2][op2], [§3][op3]) | Needs `git`, `jq`, `herdr`, `treehouse`, `tasks-axi` and more on each host ([fm][fm-remote]) |
| **Web** | Yes ([vps][vps-glance]) | Yes: HTTPS to web, GitHub, npm ([vps][vps-web]) | Yes ([vps][vps-web]) | Allowlist ("Trusted") by default; Full or Custom per environment ([cc §4][cc4]) | Codex: off by default. Cursor: on. Copilot: firewall allowlist ([op][op-cmp]) | The host's ([fm][fm-qs]) |
| **Browser** | Chrome, Safari, Playwright ([vps][vps-glance]) | **No**: cached headless shell lacks 15 system libraries; no display ([vps][vps-browser]) | Headless, after `playwright install-deps` (root) or the Playwright Docker image ([vps][vps-browser]) | None documented beyond `chromedriver`; unverified ([cc §4][cc4]) | Cursor: full desktop and computer use. Copilot: Playwright MCP on by default. Codex: none documented ([op §2][op2], [§3][op3], [§1][op1]) | Requires `chrome-devtools-axi`; headless on a server unverified ([fm][fm-axi]) |
| **File system** | Home folder ([vps][vps-glance]) | Own home, 26 GB free; `sudo` with a password ([vps][vps-glance]) | Same ([vps][vps-glance]) | Ephemeral VM; only pushed work and the conversation persist ([cc §2][cc2]) | Ephemeral per task; Cursor keeps snapshots ([op §2][op2]) | The host's; worktree per task ([fm][fm-walk]) |
| **Herdr** | 0.9.0, VPS saved as a machine ([hv][hv-model]) | 0.9.0; driven over `ssh … bash -lc 'herdr …'` ([vps][vps-herdr]) | 0.9.2: `herdr --machine <label>`, `machine status`, no shell quoting ([vps][vps-upgrade]) | None ([cc §8][cc8]) | None ([del §5][del5]) | One of five backends; remote homes always run on Herdr ([fm][fm-remote]) |
| **Git worktrees** | Treehouse ([vps][vps-glance]) | Plain git only; no Treehouse ([vps][vps-git]) | Treehouse, or `git worktree add` / `herdr worktree create` ([vps][vps-git]) | Plain `git worktree`; parallelism is sub-agents or projects ([cc §8][cc8]) | One branch per task ([op][op-cmp]) | `treehouse get` per task ([fm][fm-walk]) |

### The work itself

| | Mac | VPS today | VPS upgraded | Claude Code cloud | Other hosted | Firstmate |
|---|---|---|---|---|---|---|
| **GitHub push and PR** | `gh` ([del §1][del1]) | Yes: `gh` logged in, SSH auth works; writes not tried ([vps][vps-git]) | Yes ([vps][vps-git]) | Push only to the session's branch; Create PR button; PR GraphQL only through the proxy ([cc §6][cc6]) | All push and open PRs: Codex from the web, Cursor `cursor/…` or a given branch, Copilot one `copilot/…` PR ([op][op-cmp]) | The host's `gh`; branch `fm/<id>`; PR per task; guarded merge ([fm][fm-gh]) |
| **Loads skills and instructions** | Current skills and global instructions ([vps][vps-glance]) | Older skill set; no global instructions; hand-made deny rules, memory on ([vps][vps-env]) | Current skills, shared `AGENTS.md`, rule table, hook, memory off ([vps][vps-env]) | Repo `CLAUDE.md` and `.claude/skills`, claude.ai-enabled skills; **not** `~/.claude`. This repo's `skills/` isn't loaded ([cc §5][cc5]) | Repo `AGENTS.md` everywhere; this repo's skills as they are nowhere; only Cursor carries anything personal: account User Rules and a `~/.cursor/skills` sync ([op][op-cmp], [op §2][op2]) | Its own `AGENTS.md` and skills replace ours ([fm][fm-map]) |
| **Orchestration with sub-agents** | Yes; the baseline ([del §1][del1]) | Old `orchestrate-effort` installed; `handover`, `close-effort` missing; RAM fits one or two agents ([del §3.1][del31], [siz][siz-tiers]) | As the Mac; CX33 fits two or three agents ([siz][siz-tiers]) | Sub-agents work; idle expiry kills background work; projects run parallel threads ([cc §8][cc8]) | Task-sized. Cursor has sub-agents; Codex and Copilot unverified; Copilot capped at 59 min ([op][op-cmp]) | Forbids harness sub-agents: visible workers with on-disk state instead ([fm][fm-map]) |

### Delegating and hearing back

| | Mac | VPS today | VPS upgraded | Claude Code cloud | Other hosted | Firstmate |
|---|---|---|---|---|---|---|
| **Started by a local agent** | handover-to-herdr ([del §2][del2]) | `herdr` over SSH; workspace create and close probed ([del §3.1][del31]) | `herdr --machine … agent start/prompt` ([del §3.1][del31]) | **Not with `claude --cloud`** (interactive only); a routine's API trigger; or the maintainer in a terminal ([cc §7][cc7], [del §4.1][del41]) | Yes: `codex cloud exec`, Cursor `POST /v1/agents`, `gh agent-task create` ([op][op-cmp]) | `fm-spawn.sh`; remote through `fm-on.sh` over SSH ([fm][fm-remote]) |
| **Watched and answered** | Herdr sidebar; `agent read/prompt` ([del §2][del2]) | Mac window shows its agent states; `agent read/prompt` over SSH ([del §3.2][del32]) | Same through `--machine`; Remote Control messaging both ways, untested ([del §3.2][del32]) | claude.ai and phone; `claude -p "<msg>" --cloud <id>` sends; no CLI status read ([cc §9][cc9]) | All watchable from a shell; answer by API only in Cursor, by `@copilot` PR comment in Copilot, web or `@codex` PR comment in Codex ([op][op-cmp]) | Zero-token watcher; durable inbox with receipts ([fm][fm-walk]) |
| **Notifications** | `osascript` ([del §2][del2]) | None proven: no `osascript` or `notify-send`; a Herdr notification "shown" somewhere unknown ([vps][vps-notif]) | Remote Control push, or a Mac-side `agent wait` watcher; both untested ([del §3.3][del33]) | Desktop and project notifications; phone push unverified; the PR is the done signal ([cc §9][cc9], [del §4.3][del43]) | Cursor: iOS push. Copilot: GitHub review request. Codex: unverified ([op][op-cmp], [del §2][del2]) | In the first mate's chat; a `command:` hook for a phone; no phone channel ([fm][fm-qs]) |
| **Moving back** | Same branch or stacked ([del §2][del2]) | Git plus safe-handover checks over SSH; VPS to Mac impossible ([hv][hv-checks], [hv][hv-back]) | Same checks through `--machine` ([vps][vps-perm]) | `claude --teleport` copies it; the docs don't say the cloud session stops; assume it may still be running until E12 settles it ([cc §10][cc10], [del §4.4][del44]) | Codex `apply`; check out the branch ([op][op-cmp]) | Relaunch from the brief on disk ([fm][fm-qs]) |
| **Cost** | Owned; plan usage ([siz][siz-sum]) | €5.99/month plus plan usage ([siz][siz-sum]) | CX33 €8.99/month (+€3), a rescale Hetzner may refuse for now ([siz][siz-avail]) | Plan usage, no VM charge; one-time $100 / $250 promo credit, terms unverified ([cc §11][cc11]) | Codex in Plus $20; Cursor Pro $20 plus API prices; Copilot Pro $10 plus AI credits ([op][op-cmp]) | Free; spends the owner's subscriptions ([fm][fm-qs]) |

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
- **Claude Code cloud:** a bigger machine than the VPS (16 GB) per session, many sessions in parallel, no machine to maintain, reachable from the phone, and a one-time promo credit to claim (terms unverified) ([cc §2][cc2], [cc §11][cc11]). Projects add a coordinator with parallel threads that auto-fix their own PRs ([cc §8][cc8]).
- **Other hosted:** Cursor drives a full desktop and takes API follow-ups; Copilot lives inside GitHub (assign an issue, get a PR) and, under GitHub's general rule, uses free Actions minutes on a public repo; Codex applies a finished diff straight into a local tree ([op][op-cmp]). Cursor's My Machines can also run a cloud agent's tool calls on the VPS ([op §2][op2]).
- **Firstmate:** survives its own restart and its workers' deaths, because the brief and the status live on disk, and it has a real remote protocol (routed requests with receipts, a readiness doctor) ([fm][fm-walk], [fm][fm-remote]).

## Decisions for the maintainer

Each has options and a recommendation. "E" numbers point to the proposed experiments below.

### D1. Where does an orchestrated effort run?

- **Options:** (a) the Mac only; (b) the Mac, or the VPS when the laptop will be closed; (c) Claude Code cloud sessions for whole efforts; (d) the Mac or the VPS orchestrates, and hosted agents take single tickets.
- **Recommendation: (b) now, (d) later.** The VPS is the only off-Mac place where this repo's skills, Herdr and the effort workflow run unchanged ([del §2][del2]). Cloud orchestration waits on E1, because skills don't load there yet, idle expiry kills sub-agents, and an agent can't start a session ([cc §5][cc5], [cc §8][cc8], [cc §7][cc7]). Hosted agents as delegates wait until one is chosen (D7).

### D2. Upgrade Herdr to 0.9.2 on both machines?

- **Options:** (a) upgrade both now; (b) stay on 0.9.0 and build on `ssh … bash -lc 'herdr …'`; (c) wait for a later release.
- **Recommendation: (a), at a quiet moment (E3).** `herdr --machine` removes the login-shell wrapper and remote-shell quoting, keeps the host out of skill text, and 0.9.2 adds `machine status` for a readiness check ([vps][vps-upgrade]). The cost is a VPS server restart that ends its idle agent pane. Herdr 0.9.2 was released on 2026-09-29.

### D3. Set up the VPS environment the same way as the Mac?

- **Options:** (a) run set-up-machine on the VPS once #66 merges, plus install `jq` and a worktree tool; (b) keep the hand-made VPS setup; (c) reinstall the VPS from scratch.
- **Recommendation: (a) (E6, E8).** Without it a VPS orchestrator has old skills, no global instructions, memory on, and can't run `handover` or `close-effort` ([vps][vps-env], [del §3.1][del31]). Decide first which of the 4 memory folders to keep, since the plan removes memory files (backed up). For the worktree tool, install Treehouse (and Go) rather than special-casing `git worktree add` on the VPS; Firstmate also requires Treehouse on a remote host ([fm][fm-remote]).

### D4. Resize the VPS?

- **Options:** (a) stay on CX23; (b) add 2-4 GB of swap; (c) rescale to CX33 with "CPU and RAM only" (+€3/month, reversible); (d) burst: create a big server from a snapshot and delete it after; (e) move provider.
- **Recommendation: (a) plus (b) now; (c) when a browser or a second agent runs there.** One agent fits with 2.4 GB spare, but with no swap an out-of-memory spike kills processes ([siz][siz-rec]). Hetzner's "not available" mark is a temporary per-customer, per-location restriction on new servers and rescales; the running CX23 is unaffected, so a refused rescale costs only a retry another day ([siz][siz-avail]). Don't move provider: Hetzner CX is the cheapest per GB of everything compared ([siz][siz-sum]).

### D5. A headless browser on the VPS?

- **Options:** (a) `npx playwright install-deps chromium` as root; (b) the Playwright Docker image, which the user can already run; (c) none: keep browser work on the Mac.
- **Recommendation: (c) until a task needs it, then (b) (E7).** Docker needs no root and leaves the system untouched; measure its memory next to an agent before relying on it on CX23 ([vps][vps-browser]).

### D6. How do skills and instructions reach a Claude Code cloud session?

This repo keeps its skills in `skills/`, not `.claude/skills/`, and cloud sessions don't load `~/.claude/skills` or `~/.claude/CLAUDE.md`, so `/orchestrate-with-handoff` doesn't resolve in the cloud today ([cc §5][cc5], [del §4.1][del41]).

- **Options:** (a) enable the skills on the claude.ai account (they load in every cloud session; kept in sync by hand); (b) commit a `.claude/skills/` in this repo (only sessions on this repo get them; other projects don't); (c) have the cloud environment's setup script install the skills and global instructions into the VM's home (one source of truth, every repo on that environment; unverified that skills placed there by the script load); (d) don't carry skills: the handover brief carries the rules the session needs.
- **Recommendation: test (c) and (a) in E1, pick the one that works; don't restructure the repo for (b).** Until then, use cloud sessions only with self-contained briefs (d). The same unknown ("does the cloud agent read a home folder the setup script filled?") is open for Codex and Copilot too ([op][op-oq]).

### D7. Which hosted agent, if any, for single-ticket delegation?

- **Options:** (a) Claude Code cloud only; (b) add Copilot ($10/month, lives in GitHub, 59-minute cap, no shell steering; answer by `@copilot` PR comment); (c) add Cursor ($20 plus API prices, best API, user-skill sync and account User Rules, browser); (d) add Codex (in ChatGPT Plus, no shell follow-ups; answer on the web or by `@codex` PR comment); (e) none.
- **Recommendation: (a) first; (b) if a second is wanted.** It needs no sign-up, and a one-time promo credit to claim (terms unverified) could cover a first try ([cc §11][cc11]). Copilot is the cheapest trial and fits a public repo ([op §3][op3]); Cursor is the strongest delegate but bills model use at API prices ([op §2][op2]). Whichever is used, the delegate brief must carry the rules, and the result is read back as a branch through `gh`, as Firstmate's Grok Bot pattern does ([fm][fm-map]). Score any candidate against Firstmate's five-point backend contract ([fm][fm-contract]).

### D8. What does an orchestrator delegate to, and from which base?

Two findings from running this effort: harness sub-agent worktrees were created from an old `main`, not the stacked effort branch, and every delegate had to fast-forward itself ([del §7][del7]); and Firstmate forbids its orchestrator the harness's sub-agent tool because sub-agent workers died with a restarted orchestrator and left no record ([fm][fm-map]).

- **Options:** (a) keep in-process sub-agents and pass the effort branch as the base explicitly; (b) for efforts off the Mac, delegate to Herdr tabs with a status file; (c) move to Firstmate's model everywhere.
- **Recommendation: (a) now, as a small fix to the orchestrating skills; (b) as part of #15 for VPS efforts.** Sub-agents are fine on the Mac, where the orchestrator rarely restarts and each ticket is committed; the base branch fix is needed by every stacked effort today.

### D9. How does done-or-blocked reach the maintainer from off the Mac?

- **Options:** (a) Claude Code Remote Control push from the VPS session; (b) a Mac-side watcher (`herdr agent wait … --until done --until blocked`, then `osascript`); (c) Herdr's toast delivery on the Mac client; (d) GitHub notifications on the pull request.
- **Recommendation: (a) for the VPS once E5 proves it, with (b) as the fallback; (d) for cloud sessions.** (a) is the only route that needs no Mac online ([del §3.3][del33]); (b) lives only as long as the watching session. For cloud sessions nothing else is documented ([del §4.3][del43]). E4 settles (c), whose documented default is `off` although a VPS probe returned `shown` ([del §3.3][del33]).

### D10. Does the VPS need to reach the Mac?

- **Options:** (a) no, the Mac always checks; (b) Claude Code cross-session messaging over Remote Control (text only, both directions, no inbound access); (c) SSH into the Mac (Remote Login plus Tailscale or a reverse tunnel).
- **Recommendation: (a), plus (b) where a VPS agent must ask the Mac something (E5).** (c) opens the Mac to inbound access for little gain ([hv][hv-back], [del][del16]).

### D11. Guard disruptive remote Herdr commands in the rule table?

- **Options:** (a) add rows at `ask` for `herdr … server stop` and `workspace close --group` (and their `--machine` forms) to set-up-machine's `rules.json`; (b) rely on the skills' wording.
- **Recommendation: (a),** in a follow-up to #66: `--machine` makes stopping every agent on the VPS one local command ([vps][vps-perm]).

### D12. The promo credit and the one unused cloud session

- **Options:** (a) claim the credit and spend part of it on E1 now; (b) leave it.
- **Recommendation: (a).** The credit is announced as $100 on Pro and $250 on Max, spent before plan usage, with a claim deadline of 7 October reported only in search excerpts ([cc §11][cc11]). Check the terms on claude.ai before relying on the dates.

### D13. Adopt Firstmate?

- **Options:** (a) adopt it; (b) borrow ideas; (c) ignore it.
- **Recommendation: (b).** Adopting it would replace the effort workflow, run workers with bypassed permissions and strip AI trailers ([fm][fm-map]). Borrow: the status-file protocol (for #16), a readiness check with `fixable`/`human` gaps and "unreachable is unknown" (for #13), relaunch from a brief on disk (for #15), a worktree-isolation check in delegate briefs, and `--match-head-commit` in close-effort's merge ([fm][fm-map]).

[op-oq]: cloud-agents-other-providers.md#open-questions
[fm-contract]: cloud-agents-firstmate.md#the-contract-a-delegate-backend-must-meet
[del7]: cloud-agents-delegation.md#7-how-this-effort-itself-was-handed-over-material-for-15
[del16]: cloud-agents-delegation.md#agents-on-the-mac-and-the-vps-can-see-each-others-state-16

## Proposed experiments

What the research couldn't settle inside the spec's safe zone. Each needs the maintainer, or their go-ahead.

| # | Experiment | Settles | Cost | Risk | Source |
|---|---|---|---|---|---|
| E1 | **The one remaining cloud probe, run by the maintainer in a real terminal.** On a throwaway `probe/…` branch of this public repo, `claude --cloud "<read-only probe prompt>"` (the prompt is in cc's Exploration log, row 11). Note what the CLI prints; results pushed to the probe branch; then delete the branch. Add: list skills, try a push to a second branch, "notify me when done", `gh api …/issues/45/sub_issues`. To test D6 (c), give the environment a setup script that installs the skills into the VM's home first | VM size and user, session ID output, browser, WebFetch/WebSearch under Trusted, skills and `AGENTS.md` loading, push to another branch, phone push, REST through the proxy | One small session of plan usage or promo credit | Low: public repo, throwaway branch, read-only prompt | [cc open questions][cc-oq] |
| E2 | Check claude.ai for a session from probe 1 (it exited 1, cause unknown) and archive it; read the promo credit's balance and terms | Whether probe 1 created a session; D12 | None | None | [cc §7][cc7] |
| E3 | Upgrade Herdr to 0.9.2 on both machines; rerun a `probe-` workspace create, `pane run`, `pane read`, close and `agent list` through `--machine`; record `machine status --json` | D2; the command shapes #13 and #16 use | Minutes | The VPS server restart ends its panes (one idle agent today); live handoff is experimental | [vps][vps-upgrade], [del open questions][del-oq] |
| E4 | With the maintainer at the Mac: `herdr notification show` on the VPS with the Mac window on Local, then on the VPS, then with `delivery = "system"` on the Mac | Where a VPS notification appears; D9 (c) | Minutes | None | [vps][vps-notif] |
| E5 | `claude --remote-control` in a throwaway VPS Herdr tab; a Mac session on Remote Control; check `ListAgents`, `SendMessage` both ways, `isolatePeerMachines`, and a phone push on "notify me when done" | D9 (a), D10 (b) | Minutes | One-time Remote Control consent on the VPS (a config change); registers a session with Anthropic | [del][del16], [del §3.3][del33] |
| E6 | set-up-machine on the VPS after #66 merges: pull the clone, `plan`, show the diff, `apply` on approval | D3 | Minutes | Removes memory files (backed up) and rewrites hand-made rules: pick memory to keep first | [vps][vps-env] |
| E7 | Pull the Playwright Docker image (`…-resolute`) on the VPS, load one page headless with `--init --ipc=host`, record memory next to a running agent | D5; replaces the sizing estimates | A multi-GB image on a 26 GB-free disk | Low; no root, removable | [vps][vps-browser], [siz][siz-rec] |
| E8 | Install `jq`, Go and Treehouse on the VPS | D3's worktree tool | Minutes | Low | [vps][vps-git] |
| E9 | Add 2-4 GB of swap on the VPS | D4 (b) | Disk space | Low; a system config change | [siz open questions][siz-oq] |
| E10 | Rescale CX23 → CX33 "CPU and RAM only", time the downtime, rescale back | D4 (c) | A few cents plus minutes of downtime | May be refused while Hetzner's restriction lasts; the server stays as it was | [siz][siz-avail] |
| E11 | A routine with an API trigger whose prompt runs a handoff; fire it from a local agent; read the session URL | Whether an agent can hand an effort to the cloud unattended | One routine run of plan usage; counts toward the daily run cap | Low; the token is made on the web | [cc §7][cc7], [del §4.1][del41] |
| E12 | After a `claude --teleport`, check whether the cloud original keeps running, and archive it | How #15 keeps two orchestrators off one branch | None | None | [del open questions][del-oq] |
| E13 | Hosted trials, only if D7 picks one: a Copilot task on a throwaway branch (`gh agent-task create`), a Codex environment whose setup script installs skills, a Cursor API agent | D7; user skills and notifications for each | $10-20 a month and a sign-up each; Cursor adds API prices | Low on a public repo | [op open questions][op-oq] |
| E14 | Firstmate's `fm-remote-doctor.sh` read-only on the VPS in a throwaway account | How far the VPS is from a Firstmate remote home | Installs Firstmate's tools | Low in a separate account | [fm open questions][fm-oq] |
| E15 | Desktop app SSH session to the VPS: what it installs, which settings and skills load, whether Herdr sees it | Whether the desktop app is a way onto the VPS | Minutes | Changes the app's config | [vps][vps-desktop] |

[cc-oq]: cloud-agents-claude-code.md#open-questions
[del-oq]: cloud-agents-delegation.md#open-questions
[siz-oq]: cloud-agents-vps-sizing.md#open-questions
[fm-oq]: cloud-agents-firstmate.md#open-questions
[vps-desktop]: cloud-agents-vps.md#where-the-desktop-app-fits

## The three build tickets, re-scoped

The full re-scoping comments are posted on each ticket; in short:

- **[A thinking session on the Mac can hand over to an orchestrator on the VPS (#13)](https://github.com/yahyabedirhan/skills/issues/13).** The shape is settled: **handover-to-herdr** gains a target machine (Local or a saved Herdr machine's label), and the VPS's own Defaults table names its worktree tool and agent. The host comes from Herdr's catalog. Build it on `herdr --machine` after D2, with the VPS set up by D3; notifications follow D9. Handing over to a Claude Code cloud session is out of its scope: an agent can't start one with `claude --cloud` (see D1, E11).
- **[An unfinished effort can be handed to a new orchestrator (#15)](https://github.com/yahyabedirhan/skills/issues/15).** Detection and the same-branch or stacked question are settled; the per-place "old side is idle and pushed" checks are listed. New scope from this run: a continuation checks for a newer handoff, and delegates must branch from the effort branch (D8). Cloud continuations stay open until E1 and E12.
- **[Agents on the Mac and the VPS can see each other's state (#16)](https://github.com/yahyabedirhan/skills/issues/16).** Settled: every read works over SSH today and through `--machine` after D2; the permission table is in [vps][vps-perm]. New: a status file per remote orchestrator (from Firstmate), and Remote Control messaging for the reverse direction (E5). It can land first, and #13 and #15 build on it.

## The spec's decisions, as the research left them

- **Research only** held: no skill, instruction or machine was changed. The only writes outside this repository were throwaway Herdr workspaces on the VPS (closed), two `herdr notification show` calls on the VPS ([vps][vps-log], [del][del-log]), two throwaway probe branches (deleted) ([cc][cc-log]), a cloud session that probe 1 may have created (E2 checks), and scratch files on the Mac (fetched docs and a scratch SSH config alias, all outside the repo, not committed).
- **Safe probes:** the VPS probes stayed read-only apart from the throwaway workspaces and the two notifications. Of the two allowed cloud sessions, the first probe exited 1 without evidence of a session; the second was refused by the agent's local permission check before anything ran. So there are **no first-hand facts about the cloud VM**, and one allowed session is unused: E1 hands it to the maintainer.
- **Six research files and this synthesis** are under `docs/research/`, each with an exploration log. The Firstmate ticket (#75) was added mid-effort by the maintainer.
- **The build tickets** stay blocked, now on the decisions and experiments above rather than on research.

## Corrections made while writing this synthesis

- **Starting a cloud session from an agent.** [cloud-agents-delegation.md](cloud-agents-delegation.md) presented `claude --cloud "<one-line prompt>"` as the handover's start. The create form needs an interactive terminal and `-p` rejects it with a task ([cc §7][cc7], checked against the `headless` and `claude-code-on-the-web` docs); that file's table row, its section 4.1 and 4.4, and its #15 summary now say so.
- **Herdr's toast default.** [cloud-agents-delegation.md](cloud-agents-delegation.md) read the 0.9.2 configuration page's `delivery = "herdr"` example as contradicting a default of `off`. The config reference at `v0.9.2` gives `ui.toast.delivery` a default of `"off"` for both 0.9.0 and the current docs, so the example is how to turn it on; the VPS probe's `shown` stays unexplained, as [cloud-agents-vps.md](cloud-agents-vps.md#notifications) says.
- **A routine's fire response** returns `claude_code_session_id` as well as `claude_code_session_url` (the `routines` doc's example); [cloud-agents-claude-code.md](cloud-agents-claude-code.md#7-starting-it) listed only the URL.
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
