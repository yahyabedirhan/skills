# Firstmate and the Treehouse author's other agent tools

Facts for [Research: the Treehouse creator's agent tools - Firstmate and related repositories (#75)](https://github.com/yahyabedirhan/skills/issues/75), under [Spec: research cloud agents: what agents on a server or in the cloud can do, and how to delegate to them (#45)](https://github.com/yahyabedirhan/skills/issues/45). Researched on 2026-09-29. It builds on [herdr-vps.md](herdr-vps.md) (how the Mac reaches Herdr on the VPS) and [harness-capabilities.md](harness-capabilities.md) (what each harness allows), and doesn't repeat them.

The centre is [Firstmate](https://github.com/kunchenguid/firstmate) ("Talk to one agent. Ship with a crew."), read in full at the level of its contract and its main scripts, with most attention on how it delegates work to agents it doesn't run itself, local or remote. The author's other repositories get a short note each.

Sources and tags:

- **[src]** Firstmate's own repository, read at commit [`260c4f08`](https://github.com/kunchenguid/firstmate/tree/260c4f089449c33f08c31df714ca9cfe2a25b50a) (2026-09-29). A path such as `bin/fm-spawn.sh` means that file at that commit; a script's "header" is its leading comment block, which Firstmate treats as the contract for that script.
- **[other]** another repository of the author, at the commit named in its section.
- **[post]** the author's own public writing. `kun`'s `OPINIONS.md` is an automated daily distillation of his posts, not his own words, so it is tagged **[post, distilled]**.
- Nothing was installed or run. Every statement about behaviour comes from documentation, code or tests, not from a live run; the repository's own tests are cited where they pin a behaviour. Where even that is thin, the claim says **unverified**.

---

## How Firstmate delegates (walkthrough)

Firstmate is not an app. It is "an agent distro": a cloned repository whose `AGENTS.md`, skills and `bin/` scripts turn any supported terminal agent started inside it into the **first mate**, the one agent the human (the **captain**) talks to (`README.md`, "What it is"). Everything below is that agent following `AGENTS.md` and calling the scripts.

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

1. **Intake.** The first mate resolves the project, classifies the work as **ship** (a project change) or **scout** (a report at `data/<id>/report.md`, never a PR), resolves the project's **delivery mode** (`no-mistakes`, `direct-PR` or `local-only`) and its **`yolo`** merge posture, and files a backlog item (`AGENTS.md` §7 "Intake and authority"; `data/backlog.md` through `tasks-axi`, §10). It dispatches independent tasks at once, with no concurrency cap: file overlap is "a risk signal rather than an automatic reason to wait" (§7).
2. **Brief.** `bin/fm-brief.sh` scaffolds `data/<id>/brief.md`. The first mate fills two parts: `## Captain's intent` (the captain's own words, which reviewers treat as acceptance criteria) and `## Firstmate spec` (build instructions only). The rest is generated: a worktree-isolation check ("run `pwd -P` and `git rev-parse --show-toplevel` … If the top-level path is the primary checkout … STOP"), the branch to create, rules, the status protocol, the steering-inbox protocol and a mode-specific **definition of done** with a machine-readable `Delivery contract: mode=<mode>` line that `fm-spawn.sh` checks against the flags it gets (`bin/fm-brief.sh` lines 615–664; `bin/fm-dod-lib.sh`).
3. **Spawn.** `bin/fm-spawn.sh <id> <project> --mode … --yolo …` creates an endpoint in the selected **runtime backend** (tmux by default; Herdr, zellij, cmux, Orca), types `treehouse get` into the new pane's shell and waits until the pane's cwd is a distinct worktree, records it in `state/<id>.meta`, and starts the chosen harness in it with the brief (`bin/fm-spawn.sh` header and lines 4220–4240). Claude workers start with `--dangerously-skip-permissions` (or `--permission-mode auto` when configured) plus an `--append-system-prompt` that tells them the brief and inbox are first-party instructions and everything else is untrusted (`bin/fm-spawn.sh` lines 1982–1998; `.agents/skills/harness-adapters/references/harness/claude.md`). Claude's folder-trust dialog is avoided by writing `hasTrustDialogAccepted` for the worktree into `~/.claude.json` before launch (`bin/fm-claude-trust.sh`, same reference).
4. **Status back.** The worker appends sparse one-line events, `echo "{state} [at=<epoch>]: {one short line}" >> state/<id>.status`, only at phase changes and for `needs-decision`, `blocked`, `paused`, `done` and `failed` (`bin/fm-brief.sh` lines 341–346, 635–656). A decision stays open until a `resolved` line with its key lands (same lines).
5. **Watch.** `bin/fm-watch.sh` is a bash loop (poll `FM_POLL` 15 s, heartbeat 600 s backing off to 7200 s, stale escalation after 240 s, lines 268–330) that classifies events in bash and writes actionable ones to a durable queue `state/.wake-queue`; it wakes the first mate only then (`docs/architecture.md`, "Event-driven supervision"). On a Claude primary the tracked `Stop` hook `bin/fm-claude-stop-autoarm.sh` (with `asyncRewake: true`) re-arms the watcher at every turn end and wakes the session with exit code 2; a second `Stop` hook, `bin/fm-turnend-guard.sh`, blocks a turn end while work is under way and no watcher is alive (`.claude/settings.json`; `docs/supervision-protocols/claude.md`; `docs/turnend-guard.md`).
6. **Answer.** `bin/fm-send.sh <id> '<text>'` writes the message as a durable numbered file in the worker's steering inbox and rings a constant one-line "doorbell" into its terminal; the worker reads the file and acknowledges by moving it to `handled/`. The watcher re-rings an unacknowledged message and escalates a stuck one. `--resolve-key` closes the matching open decision at answer time (`bin/fm-send.sh` header; `AGENTS.md` §7 "Dispatch and supervision handoff"). Interrupt, exit and relaunch go through `bin/fm-control.sh`, never as typed text (`docs/agent-control.md`).
7. **Recover.** A dead or stuck worker is relaunched into its **recorded worktree** with the same brief plus a progress note; the brief on disk, not the harness's private session, is the durable instruction (`docs/agent-control.md` "Transactional relaunch"; `.agents/skills/stuck-crewmate-recovery/SKILL.md`). A restart of the first mate itself is "a non-event": `bin/fm-session-start.sh` reconciles from disk and the live backend (`AGENTS.md` §3, §5; `VISION.md` "A restart is a non-event").
8. **Land.** `no-mistakes` workers run the no-mistakes pipeline (review, tests, docs, push, PR, CI) and report `done: PR <url> checks green`; `direct-PR` workers push and open a ready PR themselves; `local-only` workers stop on a clean branch (`bin/fm-brief.sh` header; `.agents/skills/ship-landing/SKILL.md`). Only the captain's explicit word (or a standing per-project `yolo`) merges, always through `bin/fm-pr-merge.sh`, which reads the PR live (open, not draft, mergeable, every check green at the current head) and merges with `gh pr merge --match-head-commit` (`docs/architecture.md` "Delivery modes are explicit per task"). `bin/fm-teardown.sh` refuses to return a worktree with uncommitted or unlanded work (`AGENTS.md` hard rule 3).
9. **Report.** The first mate tells the captain outcomes, not mechanics, with the PR's full URL, and escalates only reviews, findings, real blockers, destructive actions and credentials (`AGENTS.md` §9).

---

## Where crew agents run

| Placement | What runs there | How it's started | Source |
|---|---|---|---|
| **Local pane** (the default) | One crewmate per task, in a tab or window of the primary's machine | `bin/fm-spawn.sh` in tmux, Herdr, zellij, cmux or Orca | `docs/architecture.md` "Runtime session backends" |
| **Local secondmate** | A whole second Firstmate home (own `FM_HOME`, backlog, projects, crew) on the same machine, for a scope such as one project area | `bin/fm-brief.sh --secondmate`, `bin/fm-home-seed.sh`, `bin/fm-spawn.sh <id> --secondmate` | `docs/architecture.md` "Optional secondmates" |
| **Remote secondmate** | A whole home on another SSH-reachable host; the primary routes and supervises, the remote home runs its own crew | `bin/fm-remote-home-seed.sh`, then `bin/fm-spawn.sh <id> --secondmate` | `docs/remote-secondmates.md` |
| **Grok Bot + Cursor cloud agents** | A separate Firstmate charter for xAI's hosted Grok Bot: bots on a persistent cloud VM, project work on ephemeral Cursor cloud agents | Tell a Grok Bot to follow the installer | `GROK_BOT.md`; [grok-ship](#grok-ship) |

What does **not** exist:

- **No single remote worker.** "Firstmate does not support placing an individual worker remotely or failing a remote route over to a local replacement" (`docs/remote-secondmates.md`, intro). Off the machine, the unit is a whole home.
- **No hosted cloud-agent backend** for the terminal distro. There is no backend for Claude Code on the web, Codex cloud, Cursor background agents or Copilot's agent; a search of the repository's `.md` and `.sh` files for "cloud" finds only `GROK_BOT.md` and two unrelated test lines. The Codex desktop app is explicitly "not a selectable Firstmate runtime backend" because Firstmate has "no supported shell-callable bridge" to its threads (`docs/codex-app-backend.md`).
- **No phone channel.** The away mode (`/afk`) announces "hold-for-return only … there is no phone channel" (`.agents/skills/afk/SKILL.md`).

Running the **primary itself** on a server (clone Firstmate on a Linux box, start the agent in Herdr or tmux there, attach over SSH) needs nothing special: the README lists macOS and Linux and "clone the repo, run your agent in it, and that is it" (`VISION.md` "Scope"). No document describes that setup as its own mode, so how well it works there is **unverified**.

### Remote secondmates in depth

This is Firstmate's answer to "run agents on another machine", and the closest match to this repo's plan of an orchestrator on the VPS ([#13](https://github.com/yahyabedirhan/skills/issues/13)). All from `docs/remote-secondmates.md` unless noted.

- **What's remote.** The whole home: its Firstmate code clone, its `FM_HOME`, its project clones (cloned on the host from origin URLs, never copied from the primary), its backlog and its workers. The primary keeps only a route in `data/secondmates.md` (`host:`, `root:`, `home:`) and the charter brief.
- **Setup on the host.** An SSH alias with public-key auth, strict host keys, no agent forwarding, ideally a dedicated account; a Firstmate clone; a symlink of `bin/fm-remote-entrypoint.sh` into `~/.local/bin`. Required tools: `git`, `jq`, `herdr`, `tasks-axi`, `treehouse`, and at least one of `claude`, `codex`, `opencode`, `pi`, `pi-signed`, `grok` or `kimi`, each signed in on that host ("Required remote tools", "What the remote account must provide").
- **One command surface.** Every call goes through `bin/fm-on.sh <id|alias> <fm-command> …`, which accepts only tracked `bin/fm-*.sh` scripts as encoded argv (never a shell string), disables agent forwarding and `SendEnv`, arms SSH keepalives, and returns ssh's exit status unchanged (`bin/fm-on.sh` header). After bootstrap, commands run through an account-owned **job worker** (a LaunchAgent on macOS, a plain worker on Linux) rather than in the SSH process or a pane ("The remote job worker").
- **The PATH problem, solved once.** Remote jobs never run a login shell, so `~/.profile` and `~/.zshrc` don't apply; the worker builds `PATH` by filesystem discovery (`~/.local/bin`, nvm default, asdf, mise, Nix, Homebrew, system) ("Non-interactive tool contract"). This is the same gap [herdr-vps.md](herdr-vps.md) found on the VPS (`herdr` and `claude` only on the login-shell `PATH`).
- **Readiness doctor.** `bin/fm-remote-doctor.sh` is "the single owner of what ready means". Read-only by default; each gap is tagged `fixable:` or `human:` with an `action:` line; `--fix` repairs only the automatable gaps (starts the worker, wrappers for version-managed tools) and never installs a package. Provisioning runs check → fix → check again, and the second read decides ("Readiness, repair, and the human steps", "The seed's readiness gate").
- **Where the agent runs.** Always on Herdr, in a dedicated Herdr session named `fm-remote`, one `2ndmate-<id>` workspace per secondmate; "`fm-remote` is reserved for remote fleet work", and the user's own `default` session is left alone ("Where the remote agent runs"). On macOS a guard makes sure the `fm-remote` server is born in the GUI login session so panes can read the login keychain; without it, Claude panes report "Login expired" ("How the Herdr launch agent starts its server").
- **Routed requests.** `FM_HOME=<primary> bin/fm-send.sh fm-<id> '<request>'` writes a durable record into the remote home's inbox (`state/parent-route/<id>.inbox`) and rings a doorbell; exit 0 means the record exists. A lost transport is retried once; later, only the exact resend command `fm-send` prints (carrying `FM_PENDING_REPLY_EXISTING_CORR=<id>`) is safe, because it deduplicates onto the same record ("Send a routed request", "Retries and safe resends").
- **Replies.** The remote home appends to `state/parent-replies.status`; a process-event listener on the primary does a cursor-anchored delta read over `fm-on.sh` and mirrors new lines into the primary's status channel, fetching a document only when a line carries a structured `report=data/….md` pointer ("Replies and the parent channel", "How remote lines are mirrored"). The primary never reads the secondmate's chat (`AGENTS.md` §7).
- **Unreachable is unknown, not dead.** SSH exit 255 "always means transport failure or unknown remote completion"; the route and pending requests are kept, and "an unavailable remote home is projected as unknown and is never replaced by a local second mate" ("SSH exit 255 and unavailable homes").
- **Handing over queued work.** `bin/fm-backlog-handoff.sh <id> <item>…` moves backlog items into an outbox, copies it to the host and ingests it there atomically ("Backlog handoff").
- **Keeping the host current.** Session start and every launch converge the remote home on the primary's default-branch commit; `bin/fm-config-push.sh` pushes an allowlist of inherited settings ("Sync, update, and retirement").
- **Retirement.** `bin/fm-teardown.sh <id>` runs on the host and refuses while the remote home has child work, an unsent outbox or an unresolved reply ("Retire a remote second mate").
- **What's proven.** The deterministic suite runs against fixtures; a real-host run "is still an operator-run smoke test and is not claimed by the repository tests" ("Verification").

### GitHub access

The primary needs `gh` authenticated with `gh auth login` (`README.md` "Requirements"; `docs/configuration.md` "Toolchain"). Crew agents run in the same account and machine, so they use the same `gh` login; the brief tells them to use `gh-axi` for GitHub (`bin/fm-brief.sh` line 634). A remote host must provide "credentials that work on that host" (`docs/remote-secondmates.md`). Branches are `fm/<id>` by default, overridable per project (`README.md` "Features"). Unless a home opts in with `config/keep-ai-trailers`, workers' AI co-author trailers are stripped by a `commit-msg` hook (`docs/configuration.md` "Commit attribution"), which conflicts with this repo's rule of ending commits with attribution lines.

---

## The same questions as the other research tickets

| Question | Firstmate's answer | Source |
|---|---|---|
| **Environment** | Wherever the clone runs: macOS or Linux, a terminal multiplexer, one worktree per task from Treehouse (or Orca). Remote: a whole home on an SSH host, on Herdr. No hosted sandbox. | `README.md`; `docs/remote-secondmates.md` |
| **Starting it** | `git clone` + start a verified harness in the clone (`claude`, `grok --trust`, `pi`, `omp`, `codex`, `opencode`, `cursor-agent --trust`). The first mate starts crew with `bin/fm-spawn.sh`. | `README.md` "Install and launch" |
| **Handover** | A generated brief file, delivered as the launch prompt (Claude: a one-line "doorbell" naming the brief record, because Claude strips invisible characters from the launch argument). | `bin/fm-brief.sh`; `bin/fm-spawn.sh` lines 1993–1998 |
| **Watch** | Zero-token bash watcher + durable wake queue; harness hooks re-arm it and block a "blind" turn end; `bin/fm-peek.sh` reads a pane's tail; `bin/fm-crew-state.sh` gives current state. | `docs/architecture.md`; `docs/turnend-guard.md` |
| **Answer** | `bin/fm-send.sh`: durable inbox file + doorbell, acknowledged by the worker moving the file; decisions closed by key. | `bin/fm-send.sh` header |
| **Notify** | The captain hears in the primary's chat. For away mode, escalations wait for the return; only a wedged away supervisor raises an OS alarm (`osascript`, `herdr notification show`, or a `command:` hook "allowing delivery to a phone or pager service"). Optional Relay answers mentions on X and Discord. | `docs/wedge-alarm.md`; `.agents/skills/afk/SKILL.md`; `docs/configuration.md` "Relay" |
| **Continue** | Relaunch in the recorded worktree from the brief on disk; the first mate itself restarts from disk; `/updatefirstmate` updates and restarts every live mate. | `docs/agent-control.md`; `AGENTS.md` §5, §12 |
| **GitHub** | The machine's `gh` login; per-task branch; PR per ship task; merge only on the captain's word via a guarded script. | above |
| **Harnesses** | Crew: `claude`, `codex`, `opencode`, `pi`, `pi-signed`, `grok`, `kimi`, `cursor`, `omp`, plus `muse`, `gemini`, `rovo`, `agy`, `devin` for crewmates and scouts only. Each needs a verified adapter record before it may be dispatched. | `AGENTS.md` §4; `.agents/skills/harness-adapters/` |
| **Cost** | Free (MIT); spends the captain's own subscriptions. Optional dispatch profiles pick harness, model and effort per task from `quota-axi` data; it "never downgrades the intelligence doing the work without the captain's standing, explicit permission". | `AGENTS.md` §4; `VISION.md`; `docs/architecture.md` "Dispatch profiles" |

---

## Mapped against this repo's workflow

This repo's path today: a thinking session writes a spec and tickets; **handover** / **handover-to-herdr** start an orchestrator in a new Herdr tab with a one-line prompt and don't wait on it; **orchestrate-effort** / **orchestrating** delegate each ticket to an in-process sub-agent in its own git worktree, cherry-pick each delegate's single commit onto the effort branch, and deliver one pull request; the maintainer is told at two moments by `osascript` (see `skills/`).

| Mechanism | Firstmate | This repo | Verdict | What it would replace or add |
|---|---|---|---|---|
| Who delegates | One long-lived first mate per machine, for every project; secondmates per domain | One orchestrator per effort, started by a handover | **Leave** the structure | Ours fits one effort, one PR; a standing first mate is a different product |
| Delegate type | Visible terminal agents with on-disk state; a PreToolUse guard **denies** the primary the harness's sub-agent tool, after sub-agent workers died with a restarted primary and left no record (`docs/subagent-guard.md`) | In-process sub-agents | **Borrow the lesson** | For long or remote efforts, delegate to Herdr tabs with a status file instead of sub-agents. Feeds [#15](https://github.com/yahyabedirhan/skills/issues/15) (an effort surviving its orchestrator) |
| Brief | Generated scaffold: intent + spec + isolation check + status protocol + inbox + definition of done, with a machine-checked mode line | "Point, don't restate": paths to the ticket, spec and handoff plus review depth and report shape | **Borrow** two parts | Add a worktree-isolation check (`pwd -P` / `git rev-parse --show-toplevel`) and a status-line protocol to the delegate brief and the handoff; keep pointing rather than pasting |
| Starting a session | `fm-spawn.sh`: new tab, `treehouse get` inside the pane, harness launched with the brief | `handover-to-herdr`: `herdr worktree open` / `tab create`, `herdr agent start`, one-line `agent prompt` | **Borrow** the trust pre-registration | Replaces handover-to-herdr's "ask the maintainer to accept the trust dialog" step (`bin/fm-claude-trust.sh` writes `hasTrustDialogAccepted` in `~/.claude.json`). It's a config write, so it needs the maintainer's go-ahead first |
| Status back | Append-only `state/<id>.status` with fixed verbs; a decision is open until a keyed `resolved` line | Sub-agent's final report; Herdr's `agent_status` for tabs | **Adopt** for off-Mac agents | A status file in the worktree (or `.scratch/`) that the Mac can read over `ssh` is the cheapest "see each other's state" for [#16](https://github.com/yahyabedirhan/skills/issues/16); Herdr's `idle/working/blocked/done` says whether the agent is busy, not what it needs |
| Watching | Bash watcher, zero tokens, durable wake queue, Stop-hook re-arm, turn-end guard | Fire-and-forget; the orchestrator waits on sub-agent notifications | **Borrow the idea, leave the machinery** | `herdr agent wait <pane> --until done --until blocked` over SSH plus the status file gives most of it; Firstmate's watcher is ~3,200 lines of bash tied to its layout |
| Answering | Durable inbox files + a constant doorbell line; acked by moving the file | `SendMessage` to sub-agents; `herdr agent prompt` (a paste) for tabs | **Borrow** for remote | Replaces pasting prompts over SSH, which has remote-shell quoting problems ([herdr-vps.md](herdr-vps.md)) and no receipt |
| Notifying | Chat; OS alarm only for a wedged away supervisor; `command:` channel for a phone | `osascript` at delivery and when blocked | **Leave** (ours already covers it); **borrow** `command:` as the shape for a VPS notification | A VPS orchestrator could run a configured command instead of `osascript`, which doesn't exist on Linux |
| Recovery / continue | Relaunch into the recorded worktree from the brief plus a progress note; restart reconciles from disk | Handoff document + new session | **Borrow** | "The brief on disk is the instruction, not the harness session" is the rule [#15](https://github.com/yahyabedirhan/skills/issues/15) needs; our handoff already plays that role for the orchestrator but not for its delegates |
| Results | PR per ship task; three delivery modes; `no-mistakes` pipeline; scout = report, never a PR | One commit per ticket, cherry-picked, one PR per effort; research tickets write files | **Leave** | Our effort-level PR is deliberate; the scout/ship split already exists as research vs build tickets |
| Merging | Only on the captain's word; `fm-pr-merge.sh` checks live green at the head and merges with `--match-head-commit` | **close-effort** merges after "go" | **Borrow** `--match-head-commit` | One flag in close-effort's merge step: the merge fails if the branch moved after the maintainer reviewed it |
| Cleanup | `fm-teardown.sh` refuses unlanded or uncommitted work; never `--force` without explicit discard authority | "Move, never `rm -rf`"; `treehouse destroy` refuses unlanded work | **Already aligned** | Nothing |
| Remote machine | Remote secondmate: whole home on an SSH host, dedicated Herdr session, job worker, doctor, never fail over to local | Planned: hand an orchestrator to the VPS ([#13](https://github.com/yahyabedirhan/skills/issues/13)) | **Borrow** four ideas | (1) a read-only readiness check with `fixable`/`human` gaps before handing over; (2) a dedicated Herdr session for agent work, separate from `default`; (3) "unreachable is unknown, never failover"; (4) the unit sent off the Mac is a whole orchestrator with its own worktrees, not single workers |
| Hosted cloud agents | Only via the Grok Bot template (Cursor cloud agents, adversarial review from the bot VM before a PR) | Under research in the sibling tickets | **Borrow the pattern** | An orchestrator that sends work to a hosted agent and reviews the pushed branch itself through `gh` before any PR |
| Model and quota choice | Dispatch profiles + `quota-axi` | Fixed default agent in the global instructions | **Leave for now** | Worth a look only if several subscriptions are in play |
| Adopting Firstmate itself | — | — | **Leave**, trial optional | It would replace orchestrate-effort, handover and close-effort with its own contract, bypass-permission workers, AI-trailer stripping and one PR per task. A trial in a throwaway clone is the only way to judge it, and needs installs (proposed below) |

---

## GROK_BOT.md: Firstmate on a hosted bot

`GROK_BOT.md` is a separate, 31-line charter for xAI's Grok Bot. There, crewmates are "persistent and role-based" bots with charters; the first mate "delegate[s] by messaging a crewmate; it wakes, does the work, and messages you back", marks every task with a short id and expects "empty, none, and 'nothing happened'" to be reported against it. Code goes through a per-project crewmate that "drive[s] the code work with cursor cloud agents", and the first mate "never call[s] a cursor cloud agent" itself. Secrets are per bot and given by the captain "on a secure card", never pasted in chat. [src: `GROK_BOT.md`]

The full pack is [grok-ship](#grok-ship), now superseded by the Grok Bot template it points to.

---

## The author's other repositories

Only where they bear on agents off the local machine.

### gnhf

[gnhf](https://github.com/kunchenguid/gnhf) ("good night, have fun"), read at `8913e1c5`, v0.1.50 (2026-09-25). One command runs a coding agent in a loop, non-interactively, until a stop condition or a cap (`--max-iterations`, `--max-tokens`, `--stop-when`): each successful iteration is one commit and a note in `notes.md`; a failed one is rolled back with `git reset --hard`; three consecutive failures abort. It waits out an exhausted usage window rather than failing, keeps the machine awake (`caffeinate`, `systemd-inhibit`), can run several loops at once with `--worktree`, and can push after each iteration (`--push`). Agents: `claude`, `codex`, `copilot`, `pi`, `cursor`, `rovodev`, `opencode`, and any ACP target. Its bundled skill has a "Companion" mode where the outer agent steers and reviews the run and must not trust the worker's success summary without fresh verification. [other: `README.md`; `skills/gnhf/SKILL.md`] It is the simplest thing that runs unattended on the VPS: a one-command loop with a commit trail. **Borrow the idea** for overnight, measurable tasks on the VPS; installing it is a proposed experiment.

### grok-ship

[grok-ship](https://github.com/kunchenguid/grok-ship), read at `87825cca` (2026-09-06), marked superseded by the Grok Bot template. It names "three computers": the user's (bots never execute there), "the shared Grok Bot computer: a persistent cloud VM that runs all agents", and "Cursor cloud agents: ephemeral cloud VMs that spin up on demand for project work" (`GROK_SHIP.md`). A per-project crewmate launches a Cursor cloud agent for each task; for a ship, the agent pushes a branch, then "a fresh adversarial-review subagent" reads that branch through the forge CLI from the bot VM ("The subagent cannot see the cloud agent VM"), findings go back to the same cloud agent until clean, then the crewmate opens the PR, watches checks and never merges without the captain's word relayed by the first mate (`GROK_BOT_CREWMATE.md`). The backlog is a local sqlite database on the bot VM. This is the author's one fully cloud design and the direct template for "delegate to a hosted agent, review its branch from elsewhere". **Borrow the pattern.**

### no-mistakes

[no-mistakes](https://github.com/kunchenguid/no-mistakes), read at `0df084a4`, pre-release v1.85.2 (2026-09-29). A local git remote: `git push no-mistakes` runs review, tests, docs, lint in a disposable worktree, then pushes, opens the PR and watches CI, auto-fixing what's safe and escalating the rest. It is Firstmate's strictest delivery mode. It runs where the push happens, so an agent on the VPS could use it there. **Leave**: this repo's review step is **code-review** at delivery, and adding a second pipeline is a separate decision.

### treehouse

[treehouse](https://github.com/kunchenguid/treehouse), read at `c0992810` (v3.1.0, 2026-09-26). Already this repo's worktree tool (the **treehouse** skill). Two facts matter off the Mac: it supports Linux, and Firstmate requires it on a remote host (`docs/remote-secondmates.md`); the VPS lacks it today ([herdr-vps.md](herdr-vps.md)). Firstmate uses the plain `treehouse get` subshell per task and a durable `--lease` only for secondmate homes (`docs/architecture.md` "Optional secondmates"). **Adopt** on the VPS if an orchestrator runs there (already an open question in herdr-vps.md).

### kun

[kun](https://github.com/kunchenguid/kun), read at `115447ec` (2026-09-29). A thin skill that fetches the author's distilled opinions and tool list; a Grok Bot automation refreshes those files daily, so it is itself an example of a scheduled hosted agent writing to a repository. The distilled opinions bear on this effort [post, distilled: `OPINIONS.md`]: he prefers "owning always-on personal hardware over renting equivalent VPS capacity" for sustained agent work and would "rather keep agents off publicly exposed servers", treating renting as the fit "for bursty or heavily fluctuating" load (line 88); remote development is "excellent for non-GUI work" (line 131); overnight agents suit "measurable optimization tasks where progress can be verified" (line 100); and he suggests "one firstmate that absorbs everything until it is overloaded, then spawning second mates" (line 63). **Leave** as a tool; the opinions go to the sizing ticket as one practitioner's view.

### The `*-axi` tools

Agent-shaped CLIs built on the [AXI](https://github.com/kunchenguid/axi) principles (token-efficient TOON output, next-step hints). Firstmate requires `gh-axi`, `chrome-devtools-axi`, `tasks-axi` and `quota-axi` (`docs/configuration.md` "Toolchain").

- [quota-axi](https://github.com/kunchenguid/quota-axi) (`02396ae3`, v0.1.55): reads the local quota windows of Claude, Codex, Cursor, Copilot, Grok and others in one call; "data only: it never routes"; it runs "on the machine that holds the credentials" and needs a one-time macOS Keychain grant for Claude. Useful to decide whether local, VPS or cloud work fits the remaining quota. **Leave for now.**
- [chrome-devtools-axi](https://github.com/kunchenguid/chrome-devtools-axi) (`c6d60d4d`, v0.1.35): wraps `chrome-devtools-mcp` around headless Chrome with a bridge server. A candidate for browser work on a VPS with no display; whether it runs there is **unverified**. **Leave**, note for the VPS ticket.
- [tasks-axi](https://github.com/kunchenguid/tasks-axi) (`9401ff89`, v0.2.6): backlog edits on a Markdown file; GitHub, Jira and Linear backends are "planned". **Leave**: this repo's tracker is GitHub issues.
- [gh-axi](https://github.com/kunchenguid/gh-axi) (`d221ffab`, v0.1.35): `gh` with compact output. **Leave**; `gh` works.
- `compact-adviser`, `lavish-axi` and the rest don't bear on agents off the machine.

[dotfiles](https://github.com/kunchenguid/dotfiles) (`9a4a6387`) is a nix-darwin Mac setup (one shared `AGENTS.md` for Claude, Codex and opencode, `herdr` in its Homebrew list) with nothing about remote or cloud agents, so it is skipped.

---

## The contract a delegate backend must meet

Firstmate's rejection of the Codex app as a backend states a test that fits any cloud agent this effort compares. A backend must (`docs/codex-app-backend.md`, "Acceptance contract"):

1. Create a task endpoint and return a durable id.
2. Send the initial instructions and later messages to it.
3. Read enough live state or transcript to supervise it.
4. Stop that exact endpoint.
5. Let it append lifecycle lines to the status channel; "a visible thread that cannot report into Firstmate's normal lifecycle is not a complete backend."

The synthesis ([#74](https://github.com/yahyabedirhan/skills/issues/74)) can score Claude Code cloud sessions, Codex cloud, Cursor background agents, Copilot's agent and the VPS against these five.

---

## Open questions

- TODO: Is a Firstmate primary run on a Linux server, attached over SSH, a supported shape? No document covers it (only remote secondmates). Needs a trial.
- TODO: Would a remote secondmate on the VPS work with this setup's Herdr 0.9.0? Firstmate asks for Herdr protocol 14 or newer and 0.8.0 for its default presentation (`docs/herdr-backend.md`), so the version looks fine, but the VPS lacks `jq`, `treehouse` and `tasks-axi` ([herdr-vps.md](herdr-vps.md)), which the doctor requires. Proposed experiment, needs installs and the maintainer's go-ahead: in a throwaway account on the VPS, clone Firstmate, run `bin/fm-remote-doctor.sh` read-only, and record its `fixable`/`human` gaps. Nothing else.
- TODO: Proposed experiment for adopting Firstmate as a whole: a throwaway clone on the Mac, Claude Code as primary, the Herdr backend, one scout task against this public repo. Needs `no-mistakes`, `gh-axi`, `chrome-devtools-axi`, `tasks-axi` and `quota-axi` installed; its workers run with bypassed permissions and strip AI trailers unless `config/keep-ai-trailers` is set, which conflicts with this repo's rules.
- TODO: Does a Grok Bot or a Cursor cloud agent fit here? Both need sign-ups; out of scope for this effort, left for the other-providers ticket.
- Unverified: how Firstmate's Claude workers, launched with `--dangerously-skip-permissions`, interact with the maintainer's global deny rules ([harness-capabilities.md](harness-capabilities.md)); this file doesn't settle it.
- Unverified: whether `chrome-devtools-axi` runs headless on the VPS.

---

## Exploration log

Every action taken for this file. All on the maintainer's Mac, read-only unless stated. Nothing ran on the VPS; nothing was installed, signed up for or paid for; none of the author's tools were run.

| # | Action | Where | Changed |
|---|---|---|---|
| 1 | `gh issue view 75`, `gh issue view 45`; read the effort handoff and this repo's orchestrate-effort, orchestrating, handover, handover-to-herdr and treehouse skills | Mac, this worktree | Nothing |
| 2 | `git merge --ff-only` of this worktree's branch onto the effort branch tip `8413cf7` (the worktree had been created from an older `main`) | Mac, this worktree | Moved this worktree's branch forward; no commits lost |
| 3 | `gh repo list kunchenguid` | Mac | Nothing |
| 4 | Read Firstmate at `260c4f08` from a read-only local clone the maintainer provided: `README.md`, `VISION.md`, `AGENTS.md`, `GROK_BOT.md`, `CLAUDE.md`, `.claude/settings.json`; `docs/architecture.md`, `remote-secondmates.md`, `herdr-backend.md`, `configuration.md` (toolchain, harness support, account pin, commit attribution, relay, supervision host, inbox), `supervision-protocols/claude.md`, `turnend-guard.md`, `wedge-alarm.md`, `subagent-guard.md`, `codex-app-backend.md`, `agent-control.md`, `voice-relay.md`; skills `harness-adapters` (router, dispatch, control-and-recovery, claude, devin), `afk`, `ship-landing`, `stuck-crewmate-recovery`; script headers and selected lines of `fm-spawn.sh`, `fm-brief.sh`, `fm-dod-lib.sh`, `fm-send.sh`, `fm-peek.sh`, `fm-on.sh`, `fm-watch.sh`, `fm-teardown.sh`; `grep` for "cloud", "teleport", notification channels | Mac, read-only clone | Nothing |
| 5 | Read gnhf (`8913e1c5`) and treehouse (`c0992810`) READMEs, gnhf's skill and changelog, treehouse's changelog, from read-only local clones | Mac | Nothing |
| 6 | A script in the session scratchpad ran `gh api repos/kunchenguid/<repo>/commits/HEAD`, `gh release list` and `gh api …/readme` for grok-ship, no-mistakes, dotfiles, kun, quota-axi, chrome-devtools-axi, tasks-axi, gh-axi, axi, compact-adviser, lavish-axi | Mac | Wrote README copies to the session scratchpad (outside the repo) |
| 7 | `gh api` for grok-ship's file tree, `GROK_SHIP.md`, `GROK_BOT_CREWMATE.md`; kun's `OPINIONS.md` and `TOOLS.md` | Mac | Copies in the session scratchpad |
| 8 | One web search for the author's posts on Firstmate, and one fetch of his Substack note on it (nothing citable beyond "clone the repo, run your agent in it") | Web | Nothing |
| 9 | Wrote this file and committed it | Mac, this worktree | This file |
