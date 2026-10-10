# Firstmate and the Treehouse author's other agent tools

Facts for [Research: the Treehouse creator's agent tools - Firstmate and related repositories (#75)](https://github.com/yahyabedirhan/skills/issues/75). That ticket is part of [Spec: research cloud agents: what agents on a server or in the cloud can do, and how to delegate to them (#45)](https://github.com/yahyabedirhan/skills/issues/45). Researched on 2026-09-29. It builds on two other files and doesn't repeat them:

- [herdr-vps.md](../herdr-vps.md): how the Mac reaches Herdr on the VPS.
- [harness-capabilities.md](../harness-capabilities.md): what each harness allows.

The main subject is [Firstmate](https://github.com/kunchenguid/firstmate) ("Talk to one agent. Ship with a crew."). I read its contract and its main scripts in full. Most attention goes to how it delegates work to agents that it doesn't run itself, local or remote. The author's other repositories get a short note each.

Sources and tags:

- **[src]** Firstmate's own repository, read at commit [`260c4f08`](https://github.com/kunchenguid/firstmate/tree/260c4f089449c33f08c31df714ca9cfe2a25b50a) (2026-09-29). A path such as `bin/fm-spawn.sh` means that file at that commit. A script's "header" is its leading comment block. Firstmate treats the header as the contract for that script.
- **[other]** another repository of the author, at the commit named in its section.
- **[post]** the author's own public writing. `kun`'s `OPINIONS.md` is an automated daily summary of his posts, not his own words. So it has the tag **[post, distilled]**.
- I installed and ran nothing. Every statement about behaviour comes from documentation, code or tests, not from a live run. Where the repository's own tests fix a behaviour, this file cites them. Where even that evidence is thin, the claim says **unverified**.

---

## How Firstmate delegates (walkthrough)

Firstmate is not an app. It is "an agent distro": a repository that you clone. You start any supported terminal agent inside the clone. Its `AGENTS.md`, skills and `bin/` scripts then turn that agent into the **first mate**. The first mate is the one agent that the human (the **captain**) talks to (`README.md`, "What it is"). In all the steps below, that agent follows `AGENTS.md` and calls the scripts.

```text
captain ── chat ──► first mate (primary session in the Firstmate clone; never writes to a project)
                      │ 1. intake: which project, ship or scout, delivery mode, merge posture
                      │ 2. bin/fm-brief.sh  → data/<id>/brief.md (captain's intent + spec + contract)
                      │ 3. bin/fm-spawn.sh  → new tab/window in tmux | Herdr | zellij | cmux | Orca
                      ▼
   ┌──────────────── crewmate pane (one per task) ─────────────────────────────┐
   │ shell types `treehouse get` → disposable worktree of projects/<repo>        │
   │ agent launched with the brief (claude / codex / opencode / pi / grok / …),  │
   │   permissions bypassed, trust dialog pre-registered                        │
   │ works on branch fm/<id>; appends one-line events to state/<id>.status:     │
   │   working · needs-decision · blocked · paused · done · failed              │
   │ reads steering from state/<id>.inbox/NNN.msg, acks by moving to handled/   │
   └───────────────┬───────────────────────────────────────▲────────────────────┘
                   │ status lines, pane content, PR state   │ bin/fm-send.sh (inbox + doorbell)
                   ▼                                        │ bin/fm-control.sh interrupt|exit|relaunch
   bin/fm-watch.sh: bash watcher, no tokens, polls every 15 s; wakes the first mate only on
   an actionable event (decision, blocker, done, stale pane, PR merged, heartbeat)
                   │
                   ▼
   first mate: drains the wake queue → answers (fm-send --resolve-key) or escalates to captain
   ship:  no-mistakes pipeline or direct PR → captain says "merge" → bin/fm-pr-merge.sh
          (or local-only → bin/fm-merge-local.sh) → bin/fm-teardown.sh returns the worktree
   scout: report at data/<id>/report.md → relayed as findings → teardown

   For more scale or another machine: a **secondmate** is a whole second Firstmate home
   (own backlog, projects, crew), local or on an SSH host, reached the same way
   (brief = charter, fm-send = routed request, status file = reply channel).
```

Step by step, with sources:

1. **Intake.** The first mate does these things (`AGENTS.md` §7 "Intake and authority"; `data/backlog.md` through `tasks-axi`, §10):
   - It resolves the project.
   - It classifies the work as **ship** (a project change) or **scout** (a report at `data/<id>/report.md`, never a PR).
   - It resolves the project's **delivery mode** (`no-mistakes`, `direct-PR` or `local-only`) and its **`yolo`** merge posture.
   - It files a backlog item.

   It dispatches independent tasks at once, with no limit on how many run together. File overlap is "a risk signal rather than an automatic reason to wait" (§7).
2. **Brief.** `bin/fm-brief.sh` makes a skeleton of `data/<id>/brief.md`. The first mate fills two parts:
   - `## Captain's intent`: the captain's own words. Reviewers treat them as acceptance criteria.
   - `## Firstmate spec`: build instructions only.

   The script generates the rest (`bin/fm-brief.sh` lines 615–664; `bin/fm-dod-lib.sh`):
   - a check that the worker is in its own worktree ("run `pwd -P` and `git rev-parse --show-toplevel` … If the top-level path is the primary checkout … STOP");
   - the branch to create;
   - rules;
   - the status protocol;
   - the protocol for the steering inbox;
   - a **definition of done** for the mode. It has a machine-readable `Delivery contract: mode=<mode>` line. `fm-spawn.sh` checks this line against the flags that it gets.
3. **Spawn.** `bin/fm-spawn.sh <id> <project> --mode … --yolo …` does these things (`bin/fm-spawn.sh` header and lines 4220–4240):
   - It creates an endpoint in the selected **runtime backend** (tmux by default; Herdr, zellij, cmux, Orca).
   - It types `treehouse get` into the shell of the new pane. It waits until the pane's cwd is a separate worktree.
   - It records that worktree in `state/<id>.meta`.
   - It starts the chosen harness in the worktree with the brief.

   Claude workers start with `--dangerously-skip-permissions` (or `--permission-mode auto` when configured). They also get an `--append-system-prompt`. It tells them that the brief and inbox are first-party instructions and that everything else is untrusted (`bin/fm-spawn.sh` lines 1982–1998; `.agents/skills/harness-adapters/references/harness/claude.md`). Firstmate avoids Claude's folder-trust dialog. Before launch, it writes `hasTrustDialogAccepted` for the worktree into `~/.claude.json` (`bin/fm-claude-trust.sh`, same reference).
4. **Status back.** The worker appends a few one-line events with `echo "{state} [at=<epoch>]: {one short line}" >> state/<id>.status`. It writes them only at phase changes and for `needs-decision`, `blocked`, `paused`, `done` and `failed` (`bin/fm-brief.sh` lines 341–346, 635–656). A decision stays open until a `resolved` line with its key arrives (same lines).
5. **Watch.** `bin/fm-watch.sh` is a bash loop (lines 268–330):
   - It polls every `FM_POLL` 15 s.
   - Its heartbeat is 600 s and backs off to 7200 s.
   - It escalates a stale pane after 240 s.

   It classifies events in bash and writes the actionable ones to a durable queue, `state/.wake-queue`. Only then does it wake the first mate (`docs/architecture.md`, "Event-driven supervision"). Two `Stop` hooks help on a Claude primary (`.claude/settings.json`; `docs/supervision-protocols/claude.md`; `docs/turnend-guard.md`):
   - The tracked hook `bin/fm-claude-stop-autoarm.sh` (with `asyncRewake: true`) re-arms the watcher at every turn end. It wakes the session with exit code 2.
   - `bin/fm-turnend-guard.sh` blocks a turn end while work is under way and no watcher is alive.
6. **Answer.** `bin/fm-send.sh <id> '<text>'` writes the message as a durable numbered file in the worker's steering inbox. Then it rings a constant one-line "doorbell" into the worker's terminal. The worker reads the file and acknowledges it: it moves the file to `handled/`. The watcher re-rings an unacknowledged message and escalates a stuck one. `--resolve-key` closes the matching open decision at answer time (`bin/fm-send.sh` header; `AGENTS.md` §7 "Dispatch and supervision handoff"). Interrupt, exit and relaunch go through `bin/fm-control.sh`, never as typed text (`docs/agent-control.md`).
7. **Recover.** Firstmate relaunches a dead or stuck worker into its **recorded worktree**, with the same brief plus a progress note. The durable instruction is the brief on disk, not the harness's private session (`docs/agent-control.md` "Transactional relaunch"; `.agents/skills/stuck-crewmate-recovery/SKILL.md`). A restart of the first mate itself is "a non-event". `bin/fm-session-start.sh` rebuilds the state from disk and the live backend (`AGENTS.md` §3, §5; `VISION.md` "A restart is a non-event").
8. **Land.** What a worker does depends on the delivery mode (`bin/fm-brief.sh` header; `.agents/skills/ship-landing/SKILL.md`):
   - `no-mistakes` workers run the no-mistakes pipeline (review, tests, docs, push, PR, CI). They report `done: PR <url> checks green`.
   - `direct-PR` workers push and open a ready PR themselves.
   - `local-only` workers stop on a clean branch.

   Only the captain's explicit word (or a standing per-project `yolo`) merges. The merge always goes through `bin/fm-pr-merge.sh`. This script reads the PR live: open, not draft, mergeable, every check green at the current head. Then it merges with `gh pr merge --match-head-commit` (`docs/architecture.md` "Delivery modes are explicit per task"). `bin/fm-teardown.sh` refuses to return a worktree with uncommitted or unlanded work (`AGENTS.md` hard rule 3).
9. **Report.** The first mate tells the captain outcomes, not mechanics, with the PR's full URL (`AGENTS.md` §9). It escalates only these: reviews, findings, real blockers, destructive actions and credentials.

---

## Where crew agents run

| Placement | What runs there | How it's started | Source |
|---|---|---|---|
| **Local pane** (the default) | One crewmate per task, in a tab or window of the primary's machine | `bin/fm-spawn.sh` in tmux, Herdr, zellij, cmux or Orca | `docs/architecture.md` "Runtime session backends" |
| **Local secondmate** | A whole second Firstmate home (own `FM_HOME`, backlog, projects, crew) on the same machine, for a scope such as one project area | `bin/fm-brief.sh --secondmate`, `bin/fm-home-seed.sh`, `bin/fm-spawn.sh <id> --secondmate` | `docs/architecture.md` "Optional secondmates" |
| **Remote secondmate** | A whole home on another host that SSH can reach. The primary routes and supervises. The remote home runs its own crew | `bin/fm-remote-home-seed.sh`, then `bin/fm-spawn.sh <id> --secondmate` | `docs/remote-secondmates.md` |
| **Grok Bot + Cursor cloud agents** | A separate Firstmate charter for xAI's hosted Grok Bot. Bots run on a persistent cloud VM. Project work runs on short-lived Cursor cloud agents | Tell a Grok Bot to follow the installer | `GROK_BOT.md`; [grok-ship](#grok-ship) |

What does **not** exist:

- **No single remote worker.** "Firstmate does not support placing an individual worker remotely or failing a remote route over to a local replacement" (`docs/remote-secondmates.md`, intro). Off the machine, the unit is a whole home.
- **No backend for hosted cloud agents** in the terminal distro. There is no backend for these:
  - Claude Code on the web
  - Codex cloud
  - Cursor background agents
  - Copilot's agent

  I searched the repository's `.md` and `.sh` files for "cloud". The search finds only `GROK_BOT.md` and two unrelated test lines. The Codex desktop app is explicitly "not a selectable Firstmate runtime backend". The reason: Firstmate has "no supported shell-callable bridge" to its threads (`docs/codex-app-backend.md`).
- **No phone channel.** The away mode (`/afk`) announces "hold-for-return only … there is no phone channel" (`.agents/skills/afk/SKILL.md`).

You can also run the **primary itself** on a server. Clone Firstmate on a Linux box, start the agent in Herdr or tmux there, and attach over SSH. This needs nothing special. The README's platform badge lists macOS and Linux. `VISION.md` "Scope" says setup is "clone the repo, run your agent in it, and that is it". No document describes that setup as its own mode. So how well it works there is **unverified**.

### Remote secondmates in depth

This is Firstmate's answer to "run agents on another machine". It is also the closest match to this repo's plan of an orchestrator on the VPS ([#13](https://github.com/yahyabedirhan/skills/issues/13)). All facts come from `docs/remote-secondmates.md` unless noted.

- **What's remote.** The whole home is remote:
  - its Firstmate code clone;
  - its `FM_HOME`;
  - its project clones (cloned on the host from origin URLs, never copied from the primary);
  - its backlog and its workers.

  The primary keeps only two things: a route in `data/secondmates.md` (`host:`, `root:`, `home:`) and the charter brief.
- **Setup on the host.** The host needs these ("Required remote tools", "What the remote account must provide"):
  - an SSH alias with public-key auth, strict host keys and no agent forwarding, ideally on a dedicated account;
  - a Firstmate clone;
  - a symlink of `bin/fm-remote-entrypoint.sh` into `~/.local/bin`;
  - the tools `git`, `jq`, `herdr`, `tasks-axi` and `treehouse`;
  - at least one of `claude`, `codex`, `opencode`, `pi`, `pi-signed`, `grok` or `kimi`, each signed in on that host.
- **One command surface.** Every call goes through `bin/fm-on.sh <id|alias> <fm-command> …`. This script does four things (`bin/fm-on.sh` header):
  - It accepts only tracked `bin/fm-*.sh` scripts as encoded argv, never a shell string.
  - It disables agent forwarding and `SendEnv`.
  - It arms SSH keepalives.
  - It returns ssh's exit status unchanged.

  After bootstrap, commands run through a **job worker** that the account owns. On macOS this is a LaunchAgent, on Linux a plain worker. Commands don't run in the SSH process or in a pane ("The remote job worker").
- **The PATH problem, solved once.** Remote jobs never run a login shell, so `~/.profile` and `~/.zshrc` don't apply. Instead, the worker builds `PATH` from what it finds on the filesystem: `~/.local/bin`, nvm default, asdf, mise, Nix, Homebrew, system ("Non-interactive tool contract"). [herdr-vps.md](../herdr-vps.md) found the same gap on the VPS: `herdr` and `claude` were only on the `PATH` of the login shell.
- **Readiness doctor.** `bin/fm-remote-doctor.sh` is "the single owner of what ready means". It works like this ("Readiness, repair, and the human steps", "The seed's readiness gate"):
  - By default it only reads.
  - It tags each gap `fixable:` or `human:`, with an `action:` line.
  - `--fix` repairs only the gaps that a script can fix: it starts the worker and adds wrappers for version-managed tools. It never installs a package.
  - Setup runs check → fix → check again. The second check decides.
- **Where the agent runs.** It always runs on Herdr, in a dedicated Herdr session named `fm-remote`. Each secondmate gets one `2ndmate-<id>` workspace. "`fm-remote` is reserved for remote fleet work". Firstmate leaves the user's own `default` session alone ("Where the remote agent runs"). On macOS a guard makes sure that the `fm-remote` server starts in the GUI login session. Then panes can read the login keychain. Without the guard, Claude panes report "Login expired" ("How the Herdr launch agent starts its server").
- **Routed requests.** `FM_HOME=<primary> bin/fm-send.sh fm-<id> '<request>'` writes a durable record into the remote home's inbox (`state/parent-route/<id>.inbox`). Then it rings a doorbell. Exit 0 means that the record exists. If the transport fails, `fm-send` retries once. After that, only one resend is safe: the exact command that `fm-send` prints, which carries `FM_PENDING_REPLY_EXISTING_CORR=<id>`. That command lands on the same record, so it makes no duplicate ("Send a routed request", "Retries and safe resends").
- **Replies.** The remote home appends to `state/parent-replies.status`. A process-event listener on the primary reads only the new lines, from a saved cursor, over `fm-on.sh`. It copies those lines into the primary's status channel. It fetches a document only when a line carries a structured `report=data/….md` pointer ("Replies and the parent channel", "How remote lines are mirrored"). The primary never reads the secondmate's chat (`AGENTS.md` §7).
- **Unreachable is unknown, not dead.** SSH exit 255 "always means transport failure or unknown remote completion". Firstmate keeps the route and the pending requests. Also, "an unavailable remote home is projected as unknown and is never replaced by a local second mate" ("SSH exit 255 and unavailable homes").
- **Handing over queued work.** `bin/fm-backlog-handoff.sh <id> <item>…` moves backlog items into an outbox. It copies the outbox to the host and takes it in there in one atomic step ("Backlog handoff").
- **Keeping the host current.** Session start and every launch bring the remote home to the primary's commit on the default branch. `bin/fm-config-push.sh` pushes an allowlist of inherited settings ("Sync, update, and retirement").
- **Retirement.** `bin/fm-teardown.sh <id>` runs on the host. It refuses while the remote home has child work, an unsent outbox or an unresolved reply ("Retire a remote second mate").
- **What's proven.** The deterministic test suite runs against fixtures. A run on a real host "is still an operator-run smoke test and is not claimed by the repository tests" ("Verification").

### GitHub access

The primary needs `gh` authenticated with `gh auth login` (`README.md` "Requirements"; `docs/configuration.md` "Toolchain"). Crew agents run in the same account and on the same machine. So they use the same `gh` login. The brief tells them to use `gh-axi` for GitHub (`bin/fm-brief.sh` line 634). A remote host must provide "credentials that work on that host" (`docs/remote-secondmates.md`). Branches are `fm/<id>` by default, and each project can change this (`README.md` "Features"). A `commit-msg` hook strips the AI co-author trailers from workers' commits, unless a home opts in with `config/keep-ai-trailers` (`docs/configuration.md` "Commit attribution"). This conflicts with this repo's rule to end commits with attribution lines.

---

## The same questions as the other research tickets

| Question | Firstmate's answer | Source |
|---|---|---|
| **Environment** | Wherever the clone runs: macOS or Linux, in a terminal multiplexer. Each task gets one worktree from Treehouse (or Orca). Remote: a whole home on an SSH host, on Herdr. No hosted sandbox. | `README.md`; `docs/remote-secondmates.md` |
| **Starting it** | `git clone` + start a verified harness in the clone (`claude`, `grok --trust`, `pi`, `omp`, `codex`, `opencode`, `cursor-agent --trust`). The first mate starts crew with `bin/fm-spawn.sh`. | `README.md` "Install and launch" |
| **Handover** | A generated brief file, delivered as the launch prompt. Claude gets a one-line "doorbell" that names the brief record instead, because Claude strips invisible characters from the launch argument. | `bin/fm-brief.sh`; `bin/fm-spawn.sh` lines 1993–1998 |
| **Watch** | A bash watcher that uses no tokens, plus a durable wake queue. Harness hooks re-arm the watcher and block a "blind" turn end. `bin/fm-peek.sh` reads the end of a pane. `bin/fm-crew-state.sh` gives the current state. | `docs/architecture.md`; `docs/turnend-guard.md` |
| **Answer** | `bin/fm-send.sh`: a durable inbox file + a doorbell. The worker acknowledges by moving the file. A key closes each decision. | `bin/fm-send.sh` header |
| **Notify** | The captain hears in the primary's chat. In away mode, escalations wait until the captain returns. Only a stuck away supervisor raises an OS alarm: `osascript`, `herdr notification show`, or a `command:` hook "allowing delivery to a phone or pager service". Optional Relay answers mentions on X and Discord. | `docs/wedge-alarm.md`; `.agents/skills/afk/SKILL.md`; `docs/configuration.md` "Relay" |
| **Continue** | Relaunch in the recorded worktree from the brief on disk. The first mate itself restarts from disk. `/updatefirstmate` updates and restarts every live mate. | `docs/agent-control.md`; `AGENTS.md` §5, §12 |
| **GitHub** | The machine's `gh` login. One branch per task. One PR per ship task. A guarded script merges, only on the captain's word. | above |
| **Harnesses** | Crew: `claude`, `codex`, `opencode`, `pi`, `pi-signed`, `grok`, `kimi`, `cursor`, `omp`. Also `muse`, `gemini`, `rovo`, `agy`, `devin` for crewmates and scouts only. The first mate may dispatch a harness only when it has a verified adapter record. | `AGENTS.md` §4; `.agents/skills/harness-adapters/` |
| **Cost** | Free (MIT). It uses the captain's own subscriptions. Optional dispatch profiles pick harness, model and effort per task from `quota-axi` data. Firstmate "never downgrades the intelligence doing the work without the captain's standing, explicit permission". | `AGENTS.md` §4; `VISION.md`; `docs/architecture.md` "Dispatch profiles" |

---

## Mapped against this repo's workflow

This repo's path today (see `skills/`):

1. A thinking session writes a spec and tickets.
2. **handover** / **handover-to-herdr** start an orchestrator in a new Herdr tab with a one-line prompt. They don't wait on it.
3. **orchestrate-effort** / **orchestrating** delegate each ticket to an in-process sub-agent in its own git worktree. They cherry-pick each delegate's single commit onto the effort branch and deliver one pull request.
4. `osascript` tells the maintainer at two moments.

| Mechanism | Firstmate | This repo | Verdict | What it would replace or add |
|---|---|---|---|---|
| Who delegates | One long-lived first mate per machine, for every project. Secondmates per domain | One orchestrator per effort, started by a handover | **Leave** the structure | Ours fits one effort, one PR. A first mate that runs all the time is a different product |
| Delegate type | Visible terminal agents with state on disk. A PreToolUse guard **denies** the primary the harness's sub-agent tool. The reason: sub-agent workers died with a restarted primary and left no record (`docs/subagent-guard.md`) | In-process sub-agents | **Borrow the lesson** | For long or remote efforts, delegate to Herdr tabs with a status file instead of sub-agents. Feeds [#15](https://github.com/yahyabedirhan/skills/issues/15) (an effort that survives its orchestrator) |
| Brief | A generated skeleton: intent + spec + isolation check + status protocol + inbox + definition of done. A machine checks its mode line | "Point, don't restate": paths to the ticket, spec and handoff, plus review depth and report shape | **Borrow** two parts | Add two things to the delegate brief and the handoff: a check that the delegate is in its own worktree (`pwd -P` / `git rev-parse --show-toplevel`), and a protocol for status lines. Keep pointing rather than pasting |
| Starting a session | `fm-spawn.sh`: new tab, `treehouse get` inside the pane, harness launched with the brief | `handover-to-herdr`: `herdr worktree open` / `tab create`, `herdr agent start`, one-line `agent prompt` | **Borrow** the trust pre-registration | Replaces handover-to-herdr's "ask the maintainer to accept the trust dialog" step. `bin/fm-claude-trust.sh` writes `hasTrustDialogAccepted` in `~/.claude.json`. It's a config write, so it needs the maintainer's go-ahead first |
| Status back | Append-only `state/<id>.status` with fixed verbs. A decision is open until a `resolved` line with its key arrives | Sub-agent's final report. Herdr's `agent_status` for tabs | **Adopt** for off-Mac agents | A status file in the worktree (or `.scratch/`) that the Mac can read over `ssh`. It is the cheapest "see each other's state" for [#16](https://github.com/yahyabedirhan/skills/issues/16). Herdr's `idle/working/blocked/done` says whether the agent is busy, not what it needs |
| Watching | Bash watcher that uses zero tokens, durable wake queue, Stop-hook re-arm, turn-end guard | Fire-and-forget. The orchestrator waits on sub-agent notifications | **Borrow the idea, leave the machinery** | `herdr agent wait <pane> --until done --until blocked` over SSH, plus the status file, gives most of it. Firstmate's watcher is ~3,200 lines of bash tied to its layout |
| Answering | Durable inbox files + a constant doorbell line. The worker acknowledges by moving the file | `SendMessage` to sub-agents. `herdr agent prompt` (a paste) for tabs | **Borrow** for remote | Replaces pasting prompts over SSH. A paste has quoting problems in the remote shell ([herdr-vps.md](../herdr-vps.md)) and gives no receipt |
| Notifying | Chat. An OS alarm only for a stuck away supervisor. A `command:` channel for a phone | `osascript` at delivery and when blocked | **Leave** (ours already covers it). **Borrow** `command:` as the shape for a VPS notification | A VPS orchestrator could run a configured command instead of `osascript`. `osascript` doesn't exist on Linux |
| Recovery / continue | Relaunch into the recorded worktree from the brief plus a progress note. A restart rebuilds the state from disk | Handoff document + new session | **Borrow** | [#15](https://github.com/yahyabedirhan/skills/issues/15) needs this rule: "The brief on disk is the instruction, not the harness session". Our handoff already plays that role for the orchestrator, but not for its delegates |
| Results | One PR per ship task. Three delivery modes. The `no-mistakes` pipeline. Scout = report, never a PR | One commit per ticket, cherry-picked. One PR per effort. Research tickets write files | **Leave** | Our one PR per effort is deliberate. The scout/ship split already exists as research vs build tickets |
| Merging | Only on the captain's word. `fm-pr-merge.sh` reads the PR live and confirms that every check is green at the head. Then it merges with `--match-head-commit` | **close-effort** merges after "go" | **Borrow** `--match-head-commit` | One flag in close-effort's merge step. The merge fails if the branch moved after the maintainer reviewed it |
| Cleanup | `fm-teardown.sh` refuses unlanded or uncommitted work. Never `--force` without explicit authority to discard | "Move, never `rm -rf`". `treehouse destroy` refuses unlanded work | **Already aligned** | Nothing |
| Remote machine | Remote secondmate: a whole home on an SSH host, a dedicated Herdr session, a job worker, a doctor. Never fail over to local | Planned: hand an orchestrator to the VPS ([#13](https://github.com/yahyabedirhan/skills/issues/13)) | **Borrow** four ideas | (1) a read-only readiness check with `fixable`/`human` gaps before handing over; (2) a dedicated Herdr session for agent work, separate from `default`; (3) "unreachable is unknown, never failover"; (4) the unit sent off the Mac is a whole orchestrator with its own worktrees, not single workers |
| Hosted cloud agents | Only through the Grok Bot template: Cursor cloud agents, with adversarial review from the bot VM before a PR | Under research in the sibling tickets | **Borrow the pattern** | An orchestrator sends work to a hosted agent. It reviews the pushed branch itself through `gh` before any PR |
| Model and quota choice | Dispatch profiles + `quota-axi` | Fixed default agent in the global instructions | **Leave for now** | Worth a look only if several subscriptions are in play |
| Adopting Firstmate itself | — | — | **Leave**, trial optional | It would replace orchestrate-effort, handover and close-effort. It brings its own contract, workers that bypass permissions, AI-trailer stripping and one PR per task. Only a trial in a throwaway clone can judge it. The trial needs installs (proposed below) |

The author's other tools, judged in [The author's other repositories](#the-authors-other-repositories):

| Tool | Verdict | Why |
|---|---|---|
| [gnhf](#gnhf) | **Borrow the idea** | A one-command loop that runs unattended and leaves a commit trail. It suits overnight, measurable tasks on the VPS. Installing it is a proposed experiment |
| [grok-ship](#grok-ship) | **Borrow the pattern** | The direct template for this: delegate to a hosted agent, then review its pushed branch from elsewhere before a PR |
| [no-mistakes](#no-mistakes) | **Leave** | This repo reviews with **code-review** at delivery. A second pipeline is a separate decision |
| [treehouse](#treehouse) | **Adopt** on the VPS | Already this repo's worktree tool. It supports Linux, and Firstmate requires it on a remote host. Needed if an orchestrator runs on the VPS |
| [kun](#kun) | **Leave** | A skill that fetches the author's opinions and tool list. Nothing to run here |
| [quota-axi](#the--axi-tools) | **Leave for now** | Useful to judge whether work fits the remaining quota. But it must run where the credentials are |
| [chrome-devtools-axi](#the--axi-tools) | **Leave**, note for the VPS | A candidate for headless browser work on the VPS. Whether it runs there is unverified |
| [tasks-axi](#the--axi-tools) | **Leave** | Backlog on a Markdown file. This repo's tracker is GitHub issues |
| [gh-axi](#the--axi-tools) | **Leave** | Compact `gh` output. Plain `gh` works |

---

## GROK_BOT.md: Firstmate on a hosted bot

`GROK_BOT.md` is a separate, 31-line charter for xAI's Grok Bot. There, crewmates are "persistent and role-based" bots with charters. The first mate works like this:

- It "delegate[s] by messaging a crewmate; it wakes, does the work, and messages you back".
- It marks every task with a short id.
- It expects crewmates to report "empty, none, and 'nothing happened'" against that id.

Code goes through a crewmate for each project, which "drive[s] the code work with cursor cloud agents". The first mate "never call[s] a cursor cloud agent" itself. Each bot has its own secrets. The captain gives them "on a secure card" and never pastes them in chat. [src: `GROK_BOT.md`]

The full pack is [grok-ship](#grok-ship), now superseded by the Grok Bot template it points to.

---

## The author's other repositories

Only where they bear on agents off the local machine.

### gnhf

[gnhf](https://github.com/kunchenguid/gnhf) ("good night, have fun"), read at `8913e1c5`, v0.1.50 (2026-09-25). One command runs a coding agent in a loop, with no human input. The loop runs until a stop condition or a limit (`--max-iterations`, `--max-tokens`, `--stop-when`):

- Each successful iteration makes one commit and a note in `notes.md`.
- `git reset --hard` rolls back a failed iteration.
- Three failures in a row stop the run.

Other features:

- When the usage window is used up, it waits instead of failing.
- It keeps the machine awake (`caffeinate`, `systemd-inhibit`).
- It can run several loops at once with `--worktree`.
- It can push after each iteration (`--push`).

Agents: `claude`, `codex`, `copilot`, `pi`, `cursor`, `rovodev`, `opencode`, and any ACP target. Its bundled skill has a "Companion" mode. In this mode the outer agent steers and reviews the run. It must not trust the worker's summary of success without checking again itself. [other: `README.md`; `skills/gnhf/SKILL.md`] It is the simplest thing that runs unattended on the VPS: a one-command loop with a commit trail. **Borrow the idea** for overnight, measurable tasks on the VPS. Installing it is a proposed experiment.

### grok-ship

[grok-ship](https://github.com/kunchenguid/grok-ship), read at `87825cca` (2026-09-06), marked superseded by the Grok Bot template. It names "three computers" (`GROK_SHIP.md`):

- the user's computer (bots never execute there);
- "the shared Grok Bot computer: a persistent cloud VM that runs all agents";
- "Cursor cloud agents: ephemeral cloud VMs that spin up on demand for project work".

A crewmate for each project launches a Cursor cloud agent for each task. A ship task goes like this (`GROK_BOT_CREWMATE.md`):

1. The cloud agent pushes a branch.
2. "a fresh adversarial-review subagent" reads that branch through the forge CLI from the bot VM ("The subagent cannot see the cloud agent VM").
3. The findings go back to the same cloud agent until the review is clean.
4. The crewmate opens the PR and watches the checks.
5. It never merges without the captain's word, which the first mate relays.

The backlog is a local sqlite database on the bot VM. This is the author's one design that runs fully in the cloud. It is the direct template for "delegate to a hosted agent, review its branch from elsewhere". **Borrow the pattern.**

### no-mistakes

[no-mistakes](https://github.com/kunchenguid/no-mistakes), read at `0df084a4`, pre-release v1.85.2 (2026-09-29). A local git remote. `git push no-mistakes` runs review, tests, docs and lint in a disposable worktree. Then it pushes, opens the PR and watches CI. It fixes what is safe to fix and escalates the rest. It is Firstmate's strictest delivery mode. It runs where the push happens, so an agent on the VPS could use it there. **Leave**: this repo's review step is **code-review** at delivery. A second pipeline is a separate decision.

### treehouse

[treehouse](https://github.com/kunchenguid/treehouse), read at `c0992810` (v3.1.0, 2026-09-26). Already this repo's worktree tool (the **treehouse** skill). Two facts matter off the Mac:

- It supports Linux.
- Firstmate requires it on a remote host (`docs/remote-secondmates.md`). The VPS doesn't have it today ([herdr-vps.md](../herdr-vps.md)).

Firstmate uses the plain `treehouse get` subshell for each task. It uses a durable `--lease` only for secondmate homes (`docs/architecture.md` "Optional secondmates"). **Adopt** on the VPS if an orchestrator runs there (already an open question in herdr-vps.md).

### kun

[kun](https://github.com/kunchenguid/kun), read at `115447ec` (2026-09-29). A thin skill that fetches the author's distilled opinions and tool list. A Grok Bot automation refreshes those files every day. So kun is itself an example of a scheduled hosted agent that writes to a repository. The distilled opinions bear on this effort [post, distilled: `OPINIONS.md`]:

- For long-running agent work, he prefers "owning always-on personal hardware over renting equivalent VPS capacity". He would "rather keep agents off publicly exposed servers". He sees renting as the fit "for bursty or heavily fluctuating" load (line 88).
- Remote development is "excellent for non-GUI work" (line 131).
- Overnight agents suit "measurable optimization tasks where progress can be verified" (line 100).
- He suggests "one firstmate that absorbs everything until it is overloaded, then spawning second mates" (line 63).

**Leave** as a tool.

### The `*-axi` tools

Agent-shaped CLIs built on the [AXI](https://github.com/kunchenguid/axi) principles (token-efficient TOON output, next-step hints). Firstmate requires `gh-axi`, `chrome-devtools-axi`, `tasks-axi` and `quota-axi` (`docs/configuration.md` "Toolchain").

- [quota-axi](https://github.com/kunchenguid/quota-axi) (`02396ae3`, v0.1.55): reads the local quota windows of Claude, Codex, Cursor, Copilot, Grok and others in one call. It is "data only: it never routes". It runs "on the machine that holds the credentials". For Claude it needs a one-time macOS Keychain grant. Useful to decide whether local, VPS or cloud work fits the remaining quota. **Leave for now.**
- [chrome-devtools-axi](https://github.com/kunchenguid/chrome-devtools-axi) (`c6d60d4d`, v0.1.35): wraps `chrome-devtools-mcp` around headless Chrome with a bridge server. A candidate for browser work on a VPS with no display. Whether it runs there is **unverified**. **Leave**, note for the VPS ticket.
- [tasks-axi](https://github.com/kunchenguid/tasks-axi) (`9401ff89`, v0.2.6): backlog edits on a Markdown file. GitHub, Jira and Linear backends are "planned". **Leave**: this repo's tracker is GitHub issues.
- [gh-axi](https://github.com/kunchenguid/gh-axi) (`d221ffab`, v0.1.35): `gh` with compact output. **Leave**. `gh` works.
- `compact-adviser`, `lavish-axi` and the rest don't bear on agents off the machine.

[dotfiles](https://github.com/kunchenguid/dotfiles) (`9a4a6387`) is a nix-darwin Mac setup: one shared `AGENTS.md` for Claude, Codex and opencode, and `herdr` in its Homebrew list. It has nothing about remote or cloud agents, so I skipped it.

---

## The contract a delegate backend must meet

Firstmate rejects the Codex app as a backend. Its reasons state a test that fits any cloud agent that this effort compares. A backend must (`docs/codex-app-backend.md`, "Acceptance contract"):

1. Create a task endpoint and return a durable id.
2. Send the initial instructions and later messages to it.
3. Read enough live state or transcript to supervise it.
4. Stop that exact endpoint.
5. Let it append lifecycle lines to the status channel. "a visible thread that cannot report into Firstmate's normal lifecycle is not a complete backend."

The synthesis ([#74](https://github.com/yahyabedirhan/skills/issues/74)) can score these against the five points:

- Claude Code cloud sessions
- Codex cloud
- Cursor background agents
- Copilot's agent
- the VPS

---

## Open questions

- TODO: Is a Firstmate primary run on a Linux server, attached over SSH, a supported shape? No document covers it (only remote secondmates). Needs a trial.
- TODO: Would a remote secondmate on the VPS work with this setup's Herdr 0.9.0? Firstmate asks for Herdr protocol 14 or newer, and 0.8.0 for its default presentation (`docs/herdr-backend.md`). So the version looks fine. But the VPS lacks `jq`, `treehouse` and `tasks-axi` ([herdr-vps.md](../herdr-vps.md)), and the doctor requires them. Proposed experiment (needs installs and the maintainer's go-ahead):
  1. In a throwaway account on the VPS, clone Firstmate.
  2. Run `bin/fm-remote-doctor.sh` read-only.
  3. Record its `fixable`/`human` gaps. Nothing else.
- TODO: Proposed experiment to judge Firstmate as a whole:
  - a throwaway clone on the Mac;
  - Claude Code as primary;
  - the Herdr backend;
  - one scout task against this public repo.

  It needs `no-mistakes`, `gh-axi`, `chrome-devtools-axi`, `tasks-axi` and `quota-axi` installed. Its workers run with bypassed permissions. They strip AI trailers unless `config/keep-ai-trailers` is set. Both conflict with this repo's rules.
- TODO: Does a Grok Bot or a Cursor cloud agent fit here? Both need sign-ups. They are out of scope for this effort and left for the other-providers ticket.
- Unverified: how Firstmate's Claude workers, launched with `--dangerously-skip-permissions`, interact with the maintainer's global deny rules ([harness-capabilities.md](../harness-capabilities.md)). This file doesn't settle it.
- Unverified: whether `chrome-devtools-axi` runs headless on the VPS.

---

## Exploration log

Every action taken for this file. All ran on the maintainer's Mac, read-only unless stated. Nothing ran on the VPS. I installed nothing, signed up for nothing and paid for nothing. I ran none of the author's tools.

| # | Action | Where | Changed |
|---|---|---|---|
| 1 | `gh issue view 75`, `gh issue view 45`. Read the effort handoff and this repo's orchestrate-effort, orchestrating, handover, handover-to-herdr and treehouse skills | Mac, this worktree | Nothing |
| 2 | `git merge --ff-only` of this worktree's branch onto the effort branch tip `8413cf7` (the worktree had been created from an older `main`) | Mac, this worktree | Moved this worktree's branch forward. No commits lost |
| 3 | `gh repo list kunchenguid` | Mac | Nothing |
| 4 | Read Firstmate at `260c4f08` from a read-only local clone that the maintainer provided. Top-level files: `README.md`, `VISION.md`, `AGENTS.md`, `GROK_BOT.md`, `CLAUDE.md`, `.claude/settings.json`. Docs: `docs/architecture.md`, `remote-secondmates.md`, `herdr-backend.md`, `configuration.md` (toolchain, harness support, account pin, commit attribution, relay, supervision host, inbox), `supervision-protocols/claude.md`, `turnend-guard.md`, `wedge-alarm.md`, `subagent-guard.md`, `codex-app-backend.md`, `agent-control.md`, `voice-relay.md`. Skills: `harness-adapters` (router, dispatch, control-and-recovery, claude, devin), `afk`, `ship-landing`, `stuck-crewmate-recovery`. Script headers and selected lines of `fm-spawn.sh`, `fm-brief.sh`, `fm-dod-lib.sh`, `fm-send.sh`, `fm-peek.sh`, `fm-on.sh`, `fm-watch.sh`, `fm-teardown.sh`. `grep` for "cloud", "teleport", notification channels | Mac, read-only clone | Nothing |
| 5 | Read gnhf (`8913e1c5`) and treehouse (`c0992810`) READMEs, gnhf's skill and changelog, treehouse's changelog, from read-only local clones | Mac | Nothing |
| 6 | A script in the session scratchpad ran `gh api repos/kunchenguid/<repo>/commits/HEAD`, `gh release list` and `gh api …/readme` for grok-ship, no-mistakes, dotfiles, kun, quota-axi, chrome-devtools-axi, tasks-axi, gh-axi, axi, compact-adviser, lavish-axi | Mac | Wrote README copies to the session scratchpad (outside the repo) |
| 7 | `gh api` for grok-ship's file tree, `GROK_SHIP.md`, `GROK_BOT_CREWMATE.md`; kun's `OPINIONS.md` and `TOOLS.md` | Mac | Copies in the session scratchpad |
| 8 | One web search for the author's posts on Firstmate. One fetch of his Substack note on it (nothing citable beyond "clone the repo, run your agent in it") | Web | Nothing |
| 9 | Wrote this file and committed it | Mac, this worktree | This file |
