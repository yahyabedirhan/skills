# How Firstmate works: tools, workflows and what to borrow

Facts for [Research: how Firstmate works - tools, workflows and what to borrow (#88)](https://github.com/yahyabedirhan/skills/issues/88), under [Spec: research cloud agents: what agents on a server or in the cloud can do, and how to delegate to them (#45)](https://github.com/yahyabedirhan/skills/issues/45). Researched on 2026-09-30. The maintainer won't adopt Firstmate but wants to understand it well enough to borrow from it ([D13 in cloud-agents.md](cloud-agents.md#d13-adopt-firstmate)).

It builds on [cloud-agents-firstmate.md](cloud-agents-firstmate.md) (#75), which already has Firstmate's contract, a nine-step walkthrough, where crew agents run, remote secondmates in depth, the mapping against this repo, and the author's other tools. None of that is repeated here; this file goes one level down, to every script, every file and every step.

Sources and tags:

- **[src]** Firstmate's repository, read at commit [`eb77f02b`](https://github.com/kunchenguid/firstmate/tree/eb77f02b16aeca9533102070de34b1f8812f4fa2) (2026-09-30), nine commits after the `260c4f08` that #75 read. A path such as `bin/fm-spawn.sh` means that file at that commit; every script name in the tables below links to it. A script's **header** is its leading comment block, which Firstmate treats as that script's contract (`docs/scripts.md`: "the script's own header comment is the authoritative description").
- **[other]** a sibling repository of the same author, at the commit named where it is cited: [treehouse `c0992810`](https://github.com/kunchenguid/treehouse/tree/c099281010efda0bf82bbaf8d882528fcbed6acc), [no-mistakes `bff2d06f`](https://github.com/kunchenguid/no-mistakes/tree/bff2d06f8019720dceb8529fef1f04acf3af4d44), [tasks-axi `9401ff89`](https://github.com/kunchenguid/tasks-axi/tree/9401ff899c0d1d8ae6b4fd8727b9025abda2032c), [quota-axi `02396ae3`](https://github.com/kunchenguid/quota-axi/tree/02396ae3d8fb43239983d0aaf4d07fa079cc7326), [gh-axi `d221ffab`](https://github.com/kunchenguid/gh-axi/tree/d221ffabfe106e2c7a5998bde30bf58528678d22), [chrome-devtools-axi `069a7535`](https://github.com/kunchenguid/chrome-devtools-axi/tree/069a753515c131d7be61a57d21854eeffb9fed27), [lavish-axi `a2a199cd`](https://github.com/kunchenguid/lavish-axi/tree/a2a199cd2275ab4d5cea1b94d42e2479bda36321), [gnhf `8913e1c5`](https://github.com/kunchenguid/gnhf/tree/8913e1c53d296ade5118ab567614636b7529efd6).
- Nothing was installed or run. Every statement comes from code, docs or tests; **unverified** marks what none of them pins.

What changed since #75's commit: the supervision host is now on by default for a Claude primary ([#6124](https://github.com/kunchenguid/firstmate/pull/6124)), its opt-out is inherited by secondmates, and the rest is fixes and CI (`git log 260c4f08..eb77f02b`). The first of these changes one step of #75's walkthrough; see [2.6](#26-the-watcher-and-the-wake-queue).

---

## Short answer

- **The core concepts, in one line:** one supervising agent (the **first mate**) never writes to a project; it writes a **brief** file, spawns a **crewmate** agent in its own terminal tab and disposable worktree, and then talks to it only through files: the crewmate appends one-line events to `state/<id>.status`, the first mate writes numbered messages into `state/<id>.inbox/`, and a zero-token bash **watcher** turns status changes into a durable **wake queue** that wakes the first mate only when something needs it.
- **The main workflow, in one line:** intake (ship or scout, delivery mode, merge posture) → `fm-brief.sh` → `fm-spawn.sh` (backend tab + `treehouse get` + harness launch + `state/<id>.meta` + backlog In flight) → worker loop with sparse status lines → watcher wakes → `fm-send.sh` answers → worker opens a PR → `fm-pr-check.sh` arms a merge poll → captain says merge → `fm-pr-merge.sh` (live checks, `--match-head-commit`) → `fm-teardown.sh` (proves landed, returns the worktree, closes the backlog item).
- **Size.** `bin/` holds 207 files plus 7 backend adapters, about 111,000 lines, mostly bash; `tests/` holds 255 entries. `docs/scripts.md` catalogues 160 of the 214; the other 54 (hook transports, remote-home internals, per-harness helpers, CI installers) are catalogued here from their headers.
- **The durable-file design is the lesson, not the size.** Everything that must survive a crash is a file with one owner script: the brief (the instruction), the meta record (where the work is), the status log (events), the inbox (steering), the wake queue (what still needs handling), the backlog (what the work is). Conversation memory is never authoritative ("A restart must be a non-event", `AGENTS.md` §5).
- **Scripts publish outcomes, not the model.** Wherever a model forgot to report (a secondmate that finished work but never told its parent, four times on 2026-09-02), Firstmate moved the report into the script that records the fact (`bin/fm-parent-channel-lib.sh` header). The same pattern runs through backlog transitions (spawn and teardown move the item themselves) and merge outcomes.
- **Supervision is now two LLMs on a Claude primary.** Since `eb77f02b`'s parent #6124, a headless Claude engine session (`sonnet` by default) handles routine wakes beside the captain's chat and wakes the main session only for what needs it (`docs/supervision-host.md`, `docs/configuration.md` "Supervision host").
- **Top borrow items** (ranked table in [section 3](#3-what-to-borrow)): a worktree-isolation assertion in delegate briefs (**orchestrate-effort**, **implement**); a guarded merge with live checks and `--match-head-commit` (**close-effort**); a status-file protocol with fixed verbs and keyed decisions (**orchestrating**, #16); relaunch from the brief on disk plus a one-owner lock per branch (#15); a durable inbox plus a one-line doorbell for steering a session on another machine (**handover-to-herdr**, #13, #16).
- **Don't borrow:** the watcher and supervision-host machinery, bypass-permission workers, AI-trailer stripping, one PR per task, and the dispatch-profile/quota routing. Firstmate's own contract warns against the same thing: "Do not build wrappers, control planes, policy layers, custom verifiers, or automation unless the direct path exposes a concrete blocker" (`AGENTS.md` §7).

---

## 1. Tools

### 1.1 How the pieces connect

```text
 captain ── chat ──► FIRST MATE (primary agent in the Firstmate clone; AGENTS.md is its job description)
                       │  session start: fm-session-start.sh = fm-lock + fm-bootstrap + fm-wake-drain (+ fm-startup-network, detached)
                       │  intake: data/projects.md ─ fm-project-mode.sh ─► mode, yolo, branch prefix
                       │          data/backlog.md  ─ fm-tasks-axi.sh (tasks-axi) ─► Queued item
                       │          config/crew-dispatch.json + quota-axi (+ opt-in fm-dispatch-resolve.sh) ─► harness/model/effort
                       │  brief:  fm-brief.sh ─► data/<id>/brief.md   (fm-dod-lib.sh renders "Definition of done")
                       │  spawn:  fm-spawn.sh ─► fm-backend.sh ─► backends/{tmux,herdr,zellij,cmux,orca}.sh
                       │            ├─ types `treehouse get` in the new pane, waits for an isolated worktree
                       │            ├─ fm-claude-trust.sh (~/.claude.json), worker hooks, state/<id>.git-hooks/
                       │            ├─ data/<id>/launch-brief.md + fm-operational-input.sh record (doorbell)
                       │            ├─ state/<id>.meta, state/<id>.busy-state, backlog ─► In flight
                       │            └─ harness CLI (claude/codex/opencode/pi/grok/…) started with the brief
                       ▼
 ┌──────── CREWMATE (one per task, own tab, own treehouse worktree, branch fm/<id>) ─────────────────┐
 │ echo "<verb> [at=<epoch>]: …" >> state/<id>.status    verbs: working needs-decision blocked       │
 │                                                       paused done failed resolved note            │
 │ reads state/<id>.inbox/NNN.msg, acks by mv → handled/                                             │
 │ Stop hook: touch state/<id>.turn-ended; fm-busy-event.sh apply … idle                             │
 │ delivers: no-mistakes pipeline │ push + gh-axi PR │ clean local branch                            │
 └──────────┬─────────────────────────────────────────────────────────────────────▲────────────────┘
            │ status lines, turn-ended, busy-state, pane text, PR state            │ fm-send.sh (inbox + doorbell)
            ▼                                                                       │ fm-control.sh interrupt|exit|relaunch
 WATCHER  fm-watch.sh (bash, 15 s poll) ─ fm-classify-lib.sh ─► state/.wake-queue ─► exits with one reason line
            │   also runs state/<id>.check.sh (fm-pr-poll.sh merge polls, Relay, mail, custom checks)
            │   and fm-inactive-reconcile.sh, fm-procevent.sh reconcile, secondmate liveness
            ▼
 ARM OWNER (per harness): Claude Stop hook fm-claude-stop-autoarm.sh ─► fm-supervision-host.sh park
            │   (headless engine handles routine wakes)  or  fm-watch-arm.sh ─► fm-watch.sh
            ▼   exit 2 rewakes the primary
 FIRST MATE: fm-wake-drain.sh (presents queue, OPEN DECISIONS, UNREAD STATUS) ─► act ─► --ack-through N
            ├─ answer: fm-send.sh --resolve-key   ├─ escalate: captain chat / fm-captain-hold.sh hold
            ├─ PR ready: fm-pr-check.sh (pr=, pr_head=, arms state/<id>.check.sh)
            ├─ merge: fm-pr-merge.sh (gh pr merge --match-head-commit) │ fm-merge-local.sh (local-only)
            └─ cleanup: fm-teardown.sh (landed proof, backend close, treehouse return, backlog Done, fleet-sync)

 SECONDMATE = a whole second home (own data/ state/ config/ projects/), same scripts, own crew.
   local: fm-home-seed.sh + fm-spawn.sh --secondmate   remote: fm-remote-home-seed.sh ─► fm-on.sh ─ssh─►
   fm-remote-entrypoint.sh ─► remote job worker ─► fm-remote-secondmate-control.sh (Herdr session fm-remote)
   replies: remote state/parent-replies.status ◄─ fm-remote-delta-read.sh ◄─ fm-procevent-remote-reply.sh
```

### 1.2 Required external tools

Firstmate splits its toolchain into a universal list, a per-backend delta, and feature-only tools (`docs/configuration.md` "Toolchain"; `fm_backend_required_tools` in `bin/fm-backend.sh`). `bin/fm-bootstrap.sh` prints `MISSING: <tool> (install: <command>)` for each gap and installs only after the captain says go.

| Tool | Required when | Why Firstmate needs it | Called from |
|---|---|---|---|
| `git`, `node` | Always | Worktrees, branches, landed-work proofs; `node` runs the `.mjs` policy parsers and extension host | Everywhere; `fm-arm-command-policy.mjs`, `fm-extension.mjs` |
| `gh` (authenticated) | Always | PR reads, merges, check states; `NEEDS_GH_AUTH` blocks | `fm-pr-merge.sh`, `fm-pr-state.sh`, `fm-teardown.sh`, `fm-contributions.sh` |
| [no-mistakes](https://github.com/kunchenguid/no-mistakes) ≥ 1.46.0 | Always (the strictest delivery mode) | "A local git proxy in front of your real remote": review, test, docs, lint in a disposable worktree, then push, PR, CI watch, auto-fixing safe findings and escalating the rest [other: `README.md`] | The worker (`no-mistakes axi run/respond/status`); `fm-crew-state.sh` and `fm-teardown.sh` through `fm-nm-run-lib.sh` |
| [gh-axi](https://github.com/kunchenguid/gh-axi) | Always | Token-cheap GitHub for workers: the brief says "Use gh-axi for GitHub operations"; workers open and check PRs with it (`gh-axi pr view`, `pr ready`) | Worker brief (`bin/fm-brief.sh`); `fm-pr-merge.sh` as a read-back fallback |
| [chrome-devtools-axi](https://github.com/kunchenguid/chrome-devtools-axi) | Always | Browser work for workers ("chrome-devtools-axi for browser operations" in every brief) | Worker brief |
| [tasks-axi](https://github.com/kunchenguid/tasks-axi) | Always (unless `config/backlog-backend=manual`) | The backlog: "edits a hand-editable `backlog.md` in place with a byte-exact round-trip", with dependencies, holds and `mv` between backlogs [other: `README.md`]; spawn runs `tasks-axi start`, teardown `done`/`reopen` | `fm-tasks-axi.sh`, `fm-backlog-transition-lib.sh`, `fm-captain-hold.sh`, `fm-backlog-handoff.sh` |
| [quota-axi](https://github.com/kunchenguid/quota-axi) | Always | Reads every provider's quota windows; "data only: it never routes"; its `spendPriority` is "THE quota-perspective ranker" for profile arrays (`.agents/skills/quota-array-dispatch/SKILL.md`) | The first mate at intake; `fm-quota-choose.sh`, `fm-procevent-quota.sh` |
| [lavish-axi](https://github.com/kunchenguid/lavish-axi) | Optional (presentation) | HTML boards for multi-option decisions and reports; absent gives `PRESENTATION_UNAVAILABLE` and plain text | `fm-bearings-board.sh`, `fm-procevent-lavish.sh` |
| [treehouse](https://github.com/kunchenguid/treehouse) | tmux, herdr, zellij, cmux backends | The worktree provider: spawn types `treehouse get` into the task pane (a subshell whose lifetime holds the slot), teardown runs `treehouse return --force`; secondmate homes use `treehouse get --lease` | `fm-spawn.sh` line 4221, `fm-teardown.sh` lines 1786–1846, `fm-home-seed.sh` |
| `tmux` | Default backend | Reference session provider: one window per task | `backends/tmux.sh`, `fm-tmux-lib.sh` |
| `herdr` (+ `jq`) | `herdr` backend; always on a remote host | Verified backend with its own CI lane: one workspace per home, one tab per task; push events over its socket (`pane.agent_status_changed`) | `backends/herdr.sh`, `backends/herdr-eventwait.py` |
| `zellij`, `cmux` (+ `jq`) | Experimental backends | Session providers only; worktrees still from treehouse | `backends/zellij.sh`, `backends/cmux.sh` |
| `orca` | Experimental backend | Owns both the worktree and the terminal, so no treehouse | `backends/orca.sh` |
| `jq` | JSON backends, `config/crew-dispatch.json`, Relay, merge checks | Parsing backend and forge JSON | Many |
| `glab`, `gerrit-axi` | A GitLab or Gerrit project | GitLab merges (`glab`), Gerrit publish and watch (`gerrit-axi`; Firstmate never submits a Gerrit change) | `fm-pr-merge.sh`, `fm-pr-poll.sh`, worker brief |
| `curl` | Relay, typed dispatch | HTTP to the relay and to `api.typesafe.ai` | `fm-x-*.sh`, `fm-dispatch-resolve.sh` |
| `lsof`, `perl`, `python3` | Specific features | `lsof` proves a git lock abandoned (`fm-lock-lib.sh`); `perl` is a timeout fallback and the extension capture; `python3` runs mail, voice and the Kimi TOML check | Named scripts |
| Harness CLIs | At least one verified | `claude`, `codex`, `opencode`, `pi`, `pi-signed`, `grok`, `kimi`, `cursor-agent`, `omp`; plus `gemini`, `muse`, `rovo`, `agy`, `devin` for crew only (`AGENTS.md` §4) | `fm-spawn.sh` `launch_template()` |
| `shellcheck`, `actionlint` | Developing Firstmate | Pinned lint | `fm-lint.sh`, `fm-lint-workflows.sh` |
| [gnhf](https://github.com/kunchenguid/gnhf) | Never | Not referenced anywhere in the repository (a full-text search for `gnhf` finds nothing); it is a separate tool | None |

The `*-axi` tools matter to Firstmate for one reason: they turn operations the model would otherwise write out (a backlog rewrite, a PR listing) into one short command with a compact answer, which is how a long-lived supervisor keeps its context small (`tasks-axi` README, "Why").

### 1.3 Hooks it installs

Two kinds: **primary hooks**, tracked in the Firstmate clone and active for whichever harness runs the first mate there; and **worker hooks**, written per task by `fm-spawn.sh` and removed by `fm-teardown.sh`.

| Where | Event | Runs | What it does |
|---|---|---|---|
| `.claude/settings.json` | `SessionStart` | `fm-sessionstart-run.sh` | Runs the session-start digest before the first turn |
| | `PreToolUse` (Bash) | `fm-arm-pretool-check.sh --claude`, `fm-cd-pretool-check.sh --claude` | Denies a malformed watcher arm; denies a persistent `cd projects/<clone>` in the primary shell |
| | `PreToolUse` (`.*`) | `fm-subagent-pretool-check.sh --claude` | Denies the harness's own sub-agent and background-work tools in the primary (`docs/subagent-guard.md`) |
| | `UserPromptSubmit` | `fm-host-mirror.sh hook claude` | Mirrors the captain's words to the supervision host's engine |
| | `Stop` | `fm-turnend-guard.sh --claude`; `fm-claude-stop-autoarm.sh` (`asyncRewake: true`, 8 h timeout); `fm-host-mirror.sh` | Blocks a turn end while work runs with no watcher; re-arms the watcher or parks the supervision host and rewakes the session with exit 2; mirrors the reply |
| `.cursor/hooks.json` | `sessionStart`, `stop`, `preToolUse` (Shell), `beforeSubmitPrompt`, `afterAgentResponse` | `fm-sessionstart-cursor.sh`, `fm-turnend-guard-cursor.sh`, the two pretool checks, `fm-host-mirror.sh` | Same roles; Cursor's `stop` hook parks in the foreground because exit 2 is a no-op there |
| `.codex/hooks.json` | `SessionStart`, `PreToolUse` (Bash), `Stop` | `fm-sessionstart-run.sh`, the pretool checks, `fm-turnend-guard.sh` | Same roles; Codex supervision uses `fm-watch-checkpoint.sh` in the foreground |
| `.opencode/plugins/` | plugin events | `fm-primary-{turnend-guard,pretool-check,cd-check,watch-arm,sessionstart-nudge}.js` | Same roles as JavaScript plugins |
| `.pi/extensions/` | extension events | `fm-primary-pi-watch.ts`, `fm-primary-turnend-guard.ts`, `fm-branch-supervision.ts`, `fm-calm.ts` | Pi re-arm, turn-end guard, the in-process supervision branch, presentation |
| `.omp/extensions/`, `.omp/fm-worker-overlay.yml` | extension events | `fm-primary-omp-watch.ts`, `fm-primary-turnend-guard.ts` | Same, for Oh My Pi |
| `.grok/hooks/*.json` | Grok hook events | cd check, session-start nudge, turn-end guard (`fm-turnend-guard-grok.sh`), pretool check | Same, for Grok |
| `.claude/mods/firstmate-calm/` | Claude Code mod | presentation plugin | "Calm" display mode; inert unless `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` |
| `<worktree>/.claude/settings.local.json` (per task, Claude) | `UserPromptSubmit`, `Stop`, `StopFailure`, `SessionEnd` | `fm-busy-event.sh apply … busy|idle`; `touch state/<id>.turn-ended` | Semantic busy state and the turn-end signal the watcher reads (`fm-spawn.sh` lines 4459–4479); excluded from git |
| `state/<id>.git-hooks/` (per task) | git `commit-msg` + wrappers for every client hook | `fm-git-strip-ai-trailers.sh` | Strips AI co-author trailers unless `config/keep-ai-trailers`; wrappers still run the project's own hooks; set through `GIT_CONFIG_*` env, never the project's config |
| `claude --settings '{…}'` (per launch) | n/a | inline settings | `feedbackDrafts: off`, attribution off (unless keep-trailers), `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION=false` |
| `~/.grok/hooks/`, `~/.kimi-code/config.toml` (global, marker-delimited) | Grok and Kimi turn end | a Firstmate hook plus a per-task pointer file in the worktree | Turn-end signal for harnesses without per-project hooks (`fm-kimi-turnend-hook.sh`) |
| `state/<id>.gemini-settings.json`, `state/<id>.devin-config.json` | Gemini, Devin | per-task config passed by env or `--config` | Busy and turn-end hooks without touching user or project config |
| Codex launch | `notify=` | `touch <turn-ended>` | Turn-end signal |
| Remote host LaunchAgents | login | `dev.firstmate.remote-job`, `dev.firstmate.herdr.fm-remote` | The remote job worker and the `fm-remote` Herdr server, installed by `fm-remote-doctor.sh --fix` |

### 1.4 The files on disk

`docs/configuration.md` "Operational home layout and state" owns the top level; `.agents/skills/operational-home-layout/SKILL.md` lists every child. A **home** (`FM_HOME`) is four gitignored directories next to the tracked code; a secondmate has its own home.

```text
<Firstmate clone>          tracked: AGENTS.md, bin/, .agents/skills/, docs/, hooks per harness
.env                       optional secrets: Relay token, mail, TYPESAFE_API_KEY
config/                    local choices: crew-harness, secondmate-harness, backend, crew-dispatch.json,
                           claude-permission-mode, claude-account, keep-ai-trailers, supervision-host(-off),
                           brief-include.md, launch-env-allowlist, fleet-ledger, … (inherited ones pushed to secondmates)
data/                      durable private records
  projects.md              registry: project → delivery mode, yolo, branch prefix, forge
  secondmates.md           routing table: id → home (and host/root for remote)
  backlog.md               tasks-axi backlog: In flight / Queued / Done
  captain.md, captain-shared.md, learnings.md   preferences and curated facts
  <id>/brief.md            the brief (or a secondmate's charter); survives teardown
  <id>/launch-brief.md     the brief plus the current worker-role overlay, rendered at each launch
  <id>/report.md           a scout's deliverable; survives teardown
  <id>/nm-<run>-findings.txt   no-mistakes ask-user findings, verbatim, for a decision
projects/<repo>            clones; read-only to the first mate
state/                     runtime records
  <id>.meta                where the task is: window, worktree, project, harness, kind, mode, yolo, branch,
                           model, effort, backend + backend ids, busy_gen, spawn_gen, pr=, pr_head=, …
  <id>.status              append-only events from the worker ("a wake event, not current-state truth")
  <id>.inbox/NNN.msg       steering messages; <id>.inbox/handled/ = acknowledged; .ring-state = re-ring ladder
  <id>.turn-ended, <id>.busy-state, <id>.busy-gen     turn-end signal; semantic busy record and its generation
  <id>.check.sh, .check-trust, .pr-poll*, .merge-authority, .pr-poll-merge-notified   merge poll and merge records
  <id>.backlog-close       the pending backlog transition, written before the meta is removed (crash replay)
  <id>.control-relaunch    relaunch transaction journal
  .wake-queue              durable queue: epoch<TAB>seq<TAB>kind<TAB>key<TAB>payload, kept until acknowledged
  .lock, .lock-session     the per-home session lock (one live first mate per home)
  .last-watcher-beat       watcher liveness beacon; .watch.lock, .wake-queue.lock
  .afk, .afk-contract      away or quiet posture
  .lease-<id>              which supervision actor (main or branch) may change a task right now
  inbox/, procevent/, pending-replies/, parent-route/, x-*/, public-followup/   side channels (sections 2.12, 1.5 L)
.no-mistakes/              local validation state
```

The **handled/ convention** is the acknowledgement for both steering (`state/<id>.inbox/handled/`) and captain notes (`state/inbox/handled/`): moving the file is the receipt, and the absence of the move is what the watcher re-rings and escalates (`bin/fm-task-inbox-lib.sh` header).

### 1.5 Every script in `bin/`

One row per file, grouped by job. **Inputs** are the arguments from the header's usage; **Reads / writes** names the main files; **Called by** comes from the header plus a search of `bin/`, the hook files and `.agents/skills/` for the file's name, so a caller listed there may be a mention in a comment rather than a call (the column is best-effort, **unverified** per row). "FM" means the first mate running the script by hand, as its contract or a skill tells it to.

#### A. Session start, locks and guards

| Script | What it does | Inputs | Reads / writes | Called by |
|---|---|---|---|---|
| [fm-session-start.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-session-start.sh) | One ordered session-start digest (BOOTSTRAP, WAKE QUEUE, READ-ONCE CONTRACT, FLEET STATE, NETWORK CHECKS, CONTEXT, NEXT STEP) instead of six-plus reads | none | Runs `fm-lock`, `fm-bootstrap` (detect-only), `fm-wake-drain`, `fm-startup-network`; reads `data/*.md`, `state/*.meta`, `state/*.status` | FM (`AGENTS.md` §3), `fm-sessionstart-run.sh` |
| [fm-sessionstart-run.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-sessionstart-run.sh) | Session-open hook entry: full digest, context re-emit, or nothing, by open source | `--source`, or hook JSON on stdin | Prints the digest into model context | Claude, Codex, Pi, omp session-start hooks |
| [fm-sessionstart-nudge.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-sessionstart-nudge.sh) | Prints a one-line "run session start" nudge when this session has no lock | none | `state/.lock` | OpenCode, Grok hooks; `fm-sessionstart-run.sh` |
| [fm-sessionstart-cursor.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-sessionstart-cursor.sh) | Cursor transport for the session-start run tier | `--source` | Prints JSON `additional_context` | `.cursor/hooks.json` |
| [fm-bootstrap.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-bootstrap.sh) | Toolchain and fleet diagnostics (`MISSING:`, `TANGLE:`, `FLEET_SYNC:`, `SECONDMATE_*:`), locked sweeps, backlog-close replay, approved installs | none, or `install <tools>` | All homes' records; runs fleet sync, secondmate sync/liveness, handoff delivery | `fm-session-start.sh`, `fm-startup-network.sh`, FM |
| [fm-startup-network.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-startup-network.sh) | Runs every network check (gh auth, fleet sync fetch, remote probes) off the digest's blocking path; reports inline or as a `check: startup-network` wake | `report` | `state/.startup-network.*` | `fm-session-start.sh`, FM |
| [fm-lock.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-lock.sh) | Acquire or inspect the per-home session lock (anchor pid of the harness process, plus trusted Claude session id) | none, `status` | `state/.lock`, `state/.lock-session` | `fm-session-start.sh`, Claude Stop hook |
| [fm-session-lock-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-session-lock-lib.sh) | Which harness process holds the lock, and whether this process is in that session | sourced | `state/.lock*` | `fm-lock.sh`, `fm-claude-stop-autoarm.sh`, `fm-inbox.sh` |
| [fm-herdr-session-cleanup.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-herdr-session-cleanup.sh) | Closes stale restored-shell Herdr presentation panes at locked session start, under strict identity proofs | none | `state/*.herdr-presentation` | `fm-session-start.sh` |
| [fm-supervision-instructions.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-supervision-instructions.sh) | Renders the harness-specific supervision block (or a one-line repair) from `docs/supervision-protocols/` | harness | reads protocol docs | `fm-session-start.sh`, guards |
| [fm-guard.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-guard.sh) | Loud banner when the primary checkout is on a feature branch or supervision is unhealthy | none | `state/.last-watcher-beat`, lock | Supervision scripts, `fm-wake-drain.sh` |
| [fm-tangle-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-tangle-lib.sh) | Detects a named non-default branch in the primary checkout (a worker branched in the wrong place) | sourced | git | `fm-guard.sh`, `fm-bootstrap.sh` |
| [fm-primary-scope-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-primary-scope-lib.sh) | "Is this a genuine primary home?" predicate so hooks stay inert in worker worktrees | sourced | `.fm-secondmate-home` marker | Hook entry scripts |
| [fm-startup-memory-budget.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-startup-memory-budget.sh) | Reads and reports the budget for always-loaded memory files | `read`, `report` | `config/startup-memory-budget`, `data/captain*.md`, `data/learnings.md` | `/stow` skill, `fm-stow-cascade.sh` |
| [fm-startup-memory-budget-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-startup-memory-budget-lib.sh) | Budget parsing, default publication, token estimate | sourced | same | `fm-bootstrap.sh`, the script above |
| [fm-tool-update-check.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-tool-update-check.sh) | Watcher check: "update available" or "update installed but not in effect" for watched tools | `check`, `arm`, `disarm` | `config/watched-tools.json`, `state/tool-updates.check.sh` | Watcher (after `arm`) |
| [fm-ensure-agents-md.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-ensure-agents-md.sh) | Manual project init: AGENTS.md skeleton and a two-line `@AGENTS.md` CLAUDE.md pointer | project dir | project `AGENTS.md`, `CLAUDE.md` | FM at project add (never workers) |
| [fm-timing-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-timing-lib.sh) | Per-step elapsed-time records for the deferred network stage, inert unless asked | sourced | `FM_TIMING_LOG` | `fm-startup-network.sh`, `fm-bootstrap.sh`, `fm-fleet-sync.sh` |

#### B. Intake, projects, briefs, backlog and decisions

| Script | What it does | Inputs | Reads / writes | Called by |
|---|---|---|---|---|
| [fm-project-mode.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-project-mode.sh) | Prints a project's registered `<mode> <yolo>`, or its branch prefix, or forge | project, `--branch-prefix`, `--forge` | `data/projects.md` | FM at intake; `fm-spawn.sh`, `fm-fleet-sync.sh`, seeds, `fm-promote.sh` |
| [fm-forge-detect.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-forge-detect.sh) | Proposes `forge=gerrit` or `none` from a clone's git config; never records it | clone dir | clone `.git/config` | FM at project add |
| [fm-project-origin-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-project-origin-lib.sh) | Validates an origin URL handed between homes (structure only, no forge allowlist) | sourced | none | Remote seed and provision |
| [fm-brief.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-brief.sh) | Scaffolds a ship, scout, secondmate-charter or Herdr-lab brief with `{TASK}` / `{FIRSTMATE_SPEC}` placeholders; refuses to overwrite | `<id> <repo> --mode …` / `--scout` / `--secondmate` | writes `data/<id>/brief.md`; reads `config/brief-include.md` | FM |
| [fm-brief-heading-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-brief-heading-lib.sh) | The one reader of a brief's `# Task` subsections | sourced | brief | `fm-dod-lib.sh`, `fm-dispatch-resolve.sh`, spawn |
| [fm-dod-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-dod-lib.sh) | Renders each mode's "Definition of done" and rule 1; the named-head gate that accepts a ship `done:` only when its commit is reachable outside the worker's copy; the no-mistakes `--intent` contract | sourced | brief, git | `fm-brief.sh`, `fm-promote.sh`, `fm-crew-state.sh`, `fm-pr-check.sh` |
| [fm-promote.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-promote.sh) | Promotes a scout to a ship in place (same pane, worktree, context): flips `kind=`, writes ship instructions, prints the `fm-send` to deliver them | `<id> --mode … --yolo …` | `state/<id>.meta`, `data/<id>/ship-instructions.md`, `brief.md` | FM (`scout-completion` skill) |
| [fm-tasks-axi.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-tasks-axi.sh) | Runs `tasks-axi` against this home's backlog from any directory | tasks-axi args | `data/backlog.md` | FM for every backlog read or write |
| [fm-tasks-axi-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-tasks-axi-lib.sh) | Backlog backend selection and the tasks-axi compatibility probe | sourced | `.tasks.toml`, `config/backlog-backend` | Bootstrap, teardown, handoff |
| [fm-backlog-transition-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-backlog-transition-lib.sh) | The invariant "meta exists ⇔ backlog item In flight": spawn runs `tasks-axi start`, teardown `done` or `reopen`, bootstrap replays a crash | sourced | `state/<id>.meta`, `state/<id>.backlog-close`, backlog | `fm-spawn.sh`, `fm-teardown.sh`, `fm-bootstrap.sh`, merges |
| [fm-captain-hold.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-captain-hold.sh) | A decision is a backlog task held for the captain: `hold`, `answer` (records his exact words, `--release` frees work), `complete` gate, `bind` a captured-answer source, `reconcile` | subcommand, task id, `--reason`, `--until` | backlog, `state/decision-bindings/`, `state/reconcile-requests/` | FM; `fm-send.sh --resolve-key`; board adapters; merges check `open` |
| [fm-decision-hold.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-decision-hold.sh) | One-release shim mapping the retired decision commands onto `fm-captain-hold.sh` | old subcommands | same | Old briefs |
| [fm-landed-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-landed-lib.sh) | The one rule for "Recently Landed": merged PRs, completed scouts, local-only merges | sourced (jq defs) | backlog rows | Snapshots |

#### C. Dispatch, harnesses and quota

| Script | What it does | Inputs | Reads / writes | Called by |
|---|---|---|---|---|
| [fm-harness.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-harness.sh) | Detects the running harness; resolves crew and secondmate harness, model, effort; validates `ultra` | none, `crew`, `secondmate`, `ancestry` | `config/crew-harness`, `config/secondmate-harness` | `fm-spawn.sh`, `fm-control.sh`, session start |
| [fm-dispatch-resolve.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-dispatch-resolve.sh) | Opt-in: sends the brief's intent and spec plus each dispatch rule's `when` to typesafe.ai's "System One" model and maps the answer to a profile | `<brief> [--project]` | `.env` `TYPESAFE_API_KEY`, `config/crew-dispatch.json` | FM at intake (`AGENTS.md` §4) |
| [fm-quota-choose.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-quota-choose.sh) | Picks the first `harness:model` candidate with known positive quota from one captured snapshot | `--snapshot`, `--candidate …` | quota-axi TOON/JSON | Workers, FM |
| [fm-quota-axi-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-quota-axi-lib.sh) | quota-axi version floor and snapshot schema checks | sourced | none | Bootstrap, the two above |
| [fm-vendor-auth-probe.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-vendor-auth-probe.sh) | One bounded, fixed-argv authentication probe of a vendor CLI; reports a fact, never a verdict | vendor name | none | FM (`quota-array-dispatch`) |
| [fm-worker-account-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-worker-account-lib.sh) | Opt-in per-home worker account pin (`CLAUDE_CONFIG_DIR`, `PI_CODING_AGENT_DIR`) and its sign-in check | sourced | `config/claude-account`, `config/pi-account` | `fm-spawn.sh`, `fm-control.sh` |
| [fm-env-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-env-lib.sh) | One `.env` key reader | sourced | `.env` | Relay, dispatch resolver |
| [fm-cursor-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-cursor-lib.sh) | Cursor executable and process identity (the generic `agent` alias is not trusted by name) | sourced | none | Spawn, harness, busy, tmux |
| [fm-gemini-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-gemini-lib.sh) | Gemini process identity from argv (it runs as `node`) | sourced | none | tmux backend, harness |
| [fm-agent-process-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-agent-process-lib.sh) | Backend-neutral "which process name is a harness" classifier | sourced | none | tmux and Herdr backends |
| [fm-claude-trust.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-claude-trust.sh) | Pre-registers Claude's folder trust for the task worktree (and carries forward CLAUDE.md-import consent only if already given) so the worker doesn't wedge on the dialog | `<worktree> <project>` / `--secondmate-home` / `--lab-home` | `${CLAUDE_CONFIG_DIR:-$HOME}/.claude.json` | `fm-spawn.sh` |
| [fm-agy-trust.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-agy-trust.sh) | Same for Antigravity CLI | `<worktree> <project>` | `~/.gemini/antigravity-cli/settings.json` | `fm-spawn.sh` |
| [fm-devin-config.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-devin-config.sh) | Private per-task Devin config with Firstmate's hooks, Claude-hook reading and attribution off | `<state> <id> <gen>` | `state/<id>.devin-config.json` | `fm-spawn.sh` |
| [fm-kimi-turnend-hook.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-kimi-turnend-hook.sh) | Installs or removes a marker-delimited Kimi Stop hook region | `install`, `remove` | `~/.kimi-code/config.toml` | `fm-spawn.sh` |
| [fm-git-strip-ai-trailers.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-git-strip-ai-trailers.sh) | commit-msg hook that strips AI co-author trailers; `install` builds the per-task hooks dir | `<msgfile>` / `install <dir> <worktree>` | `state/<id>.git-hooks/` | `fm-spawn.sh`; git |
| [fm-trace-context-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-trace-context-lib.sh) | Opt-in W3C `TRACEPARENT` per task, injected into the pane and recorded in meta | sourced | `config/trace-context`, meta | `fm-spawn.sh` |

#### D. Spawn, backends and pane state

| Script | What it does | Inputs | Reads / writes | Called by |
|---|---|---|---|---|
| [fm-spawn.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-spawn.sh) | Spawns a crewmate, scout, `id=repo` batch or secondmate: backend endpoint, isolated worktree, trust, hooks, launch brief, meta, backlog In flight, harness launch; `--relaunch` reuses the recorded worktree (5,479 lines) | `<id> <project> --mode --yolo [--harness --model --effort --backend --branch-prefix]`, `--scout`, `--secondmate`, `--relaunch` | writes `state/<id>.meta`, `.busy-*`, `.git-hooks/`, `data/<id>/launch-brief.md`, worktree `.claude/settings.local.json`; reads brief, `config/*` | FM; `fm-control.sh relaunch` |
| [fm-backend.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-backend.sh) | Backend selection (`FM_BACKEND` → `config/backend` → auto-detect → tmux), meta helpers, selector resolution, dispatch to adapters | sourced | meta | Spawn, send, peek, watch, teardown, control |
| [backends/tmux.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/backends/tmux.sh) | Reference adapter: one window per task | sourced | tmux | `fm-backend.sh` |
| [backends/herdr.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/backends/herdr.sh) | Verified adapter: one workspace per home, one tab per task, optional disposable "presentation" workspaces, push transitions (4,063 lines) | sourced | Herdr socket, `state/<id>.herdr-presentation` | `fm-backend.sh` |
| [backends/herdr-eventwait.py](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/backends/herdr-eventwait.py) | Raw socket subscriber for `pane.agent_status_changed`, one line per event | session, panes | Herdr socket | `backends/herdr.sh` |
| [backends/herdr-workspace-move.py](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/backends/herdr-workspace-move.py) | One scoped `workspace.move` request (orders presentation workspaces) | socket, ids | Herdr socket | `backends/herdr.sh` |
| [backends/zellij.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/backends/zellij.sh) | Experimental adapter: one shared session, one tab per task, home-scoped titles | sourced | zellij | `fm-backend.sh` |
| [backends/cmux.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/backends/cmux.sh) | Experimental macOS GUI adapter: one workspace per task | sourced | cmux socket, `config/cmux-socket-password` | `fm-backend.sh` |
| [backends/orca.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/backends/orca.sh) | Experimental adapter owning worktree and terminal | sourced | orca | `fm-backend.sh` |
| [fm-backend-hometag-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-backend-hometag-lib.sh) | Per-installation tag in tab titles so two homes' task ids can't collide in one namespace | sourced | none | zellij, cmux |
| [fm-composer-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-composer-lib.sh) | The one classifier of each harness's input box (`empty`/`pending`/`unknown`) from a captured screen, so a send never types over a draft | sourced | pane captures | Every backend, spawn, send, daemon |
| [fm-tmux-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-tmux-lib.sh) | tmux capture, busy read, verified submit (type once, retry Enter) | sourced | tmux | tmux backend, send, daemon |
| [fm-transition-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-transition-lib.sh) | Normalized agent-state transition record and the status → action policy table | sourced | none | Herdr push path |
| [fm-push-transition-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-push-transition-lib.sh) | The watcher's handler for a pushed transition, split out for tests | sourced | none | `fm-watch.sh` |
| [fm-busy-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-busy-lib.sh) | Semantic busy-state contract: `busy`/`idle`/`unknown` from harness hooks, with a generation token; missing data is `unknown`, never idle | sourced | `state/<id>.busy-state`, `.busy-gen` | Watcher, crew-state, control, daemon |
| [fm-busy-event.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-busy-event.sh) | The only writer of that record: `arm` a generation, `apply` an event | `arm <state> <id>`, `apply … --gen --source --event` | same | Worker hooks, `fm-spawn.sh`, `fm-control.sh` |
| [fm-operational-input.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-operational-input.sh) | The typed wire form for machine-made input (`U+2063 FIRSTMATE_OP: v1 <kind>: …`); for harnesses that strip invisible characters (Claude), writes a record and types only a constant ASCII doorbell naming it | `record <kind>`, `encode`, `parse` | a record under state | Spawn (launch brief), send, daemon, host mirror |
| [fm-marker-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-marker-lib.sh) | Compatibility entry for the from-firstmate marker | sourced | none | Send, brief, teardown |

#### E. Steering, control and current state

| Script | What it does | Inputs | Reads / writes | Called by |
|---|---|---|---|---|
| [fm-send.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-send.sh) | The data plane: writes a durable numbered inbox record and rings a one-line doorbell; `--resolve-key` closes an open decision; typed plane for `/skill` invocations and keys; routes remote secondmates through `fm-on.sh` | `<target> [--resolve-key k] [--fire-and-forget id] <text>`, `--key` | `state/<id>.inbox/`, `state/<id>.status`, `state/pending-replies/` | FM; bootstrap nudges |
| [fm-task-inbox-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-task-inbox-lib.sh) | Owns the inbox record format, sequence, dedup, `handled/`, the doorbell text and the re-ring ladder | sourced | `state/<id>.inbox/`, `.ring-state` | Send, watch, brief, remote control |
| [fm-control.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-control.sh) | The control plane: `interrupt`, `exit`, transactional `relaunch` (checkpoint, note, stop, `fm-spawn --relaunch`, rollback) for an exact task id | `<id> interrupt|exit|relaunch [--harness --model --effort] --note` | meta, `state/<id>.control-relaunch`, brief | FM (`stuck-crewmate-recovery`) |
| [fm-control-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-control-lib.sh) | Verb allowlist, per-harness interrupt and exit mechanics, per-backend capability, endpoint-absence proof | sourced | none | `fm-control.sh`, spawn, send |
| [fm-peek.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-peek.sh) | Bounded tail of a task's pane (remote over `fm-on.sh`) | `<target> [lines]` | pane | FM |
| [fm-crew-state.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-crew-state.sh) | One deterministic current-state line, `state: <working|parked|done|blocked|paused|failed|unknown> · source: <run-step|pane|status-log|remote-endpoint|none> · <detail>`, reconciling the stale status log with the no-mistakes run and the pane | `<id>` | meta, status, no-mistakes, pane, forge (bounded) | FM; watcher; reconcile |
| [fm-lease.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-lease.sh) | Claim, release, check, sweep a per-task lease between the two supervision actors (main, branch) | `claim|release|check <task> [--actor]` | `state/.lease-<task>` | Supervision branch, host |
| [fm-lease-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-lease-lib.sh) | The lease contract; guarded scripts refuse the other actor | sourced | same | Send, control, merges, teardown |

#### F. Supervision: watcher, wake queue, guards and the supervision host

| Script | What it does | Inputs | Reads / writes | Called by |
|---|---|---|---|---|
| [fm-watch.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-watch.sh) | The zero-token watcher: polls every 15 s, absorbs benign wakes, queues actionable ones (`signal:`, `stale:`, `check:`, `heartbeat`) and exits with one reason line (3,230 lines) | env tuning (`FM_POLL`, `FM_HEARTBEAT`, …) | all `state/<id>.*`, `state/.wake-queue`, `.last-watcher-beat`; runs `*.check.sh` | `fm-watch-arm.sh`, host, daemon |
| [fm-watch-arm.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-watch-arm.sh) | Home-scoped (re-)arm that forks the watcher as a tracked child and verifies it is alive; never with shell `&` | none | `.watch.lock`, beacon | Arm owners per harness |
| [fm-watch-checkpoint.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-watch-checkpoint.sh) | One bounded foreground watcher cycle for Codex-style supervision | none | same | Codex primary |
| [fm-wake-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-wake-lib.sh) | Durable wake queue, recovery generations, portable locks, watcher health | sourced | `state/.wake-queue`, `.watcher-down` | Most supervision scripts |
| [fm-wake-drain.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-wake-drain.sh) | Presents queued wakes, OPEN DECISIONS, UNREAD STATUS, RECORD DIVERGENCE, branch outcomes; prints `WAKE_ACK_REQUIRED`; `--ack-through N --recovery-generation G` acknowledges after handling | none / `--ack-through` | queue, status cursors | FM at every wake |
| [fm-wake-grant.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-wake-grant.sh) | Serializes which wake rows the supervision branch may claim | subcommands | `.branch-eligible-rows`, `.main-eligible-rows` | Pi branch, supervision host |
| [fm-classify-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-classify-lib.sh) | The wake classifier and status vocabulary: captain-relevant verbs, `paused:` vs `blocked:`, keyed open/resolved decisions, unread status | sourced | status files, cursors | Watcher, daemon, drain, brief |
| [fm-line-cap-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-line-cap-lib.sh) | One per-line cap for status lines shown in digests | sourced | none | Drain, session start |
| [fm-supervision-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-supervision-lib.sh) | "Does this home need supervision, and is the beacon fresh?" | sourced | `.last-watcher-beat` | Guards |
| [fm-claude-stop-autoarm.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-claude-stop-autoarm.sh) | Claude primary Stop hook (`asyncRewake`): at every turn end, re-arms the watcher or parks the supervision host, and rewakes the session with exit 2 on an actionable close | hook payload | lock, `.claude-autoarm*` | `.claude/settings.json` |
| [fm-turnend-guard.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-turnend-guard.sh) | Blocks a primary turn end while work runs and no watcher is alive ("no turn ends blind") | `--claude` etc. | beacon, meta | Claude, Codex, OpenCode, Pi hooks |
| [fm-turnend-guard-cursor.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-turnend-guard-cursor.sh) | Cursor stop hook: parks the watcher in the foreground and returns its wake as a follow-up | hook payload | `.cursor-park-owner` | `.cursor/hooks.json` |
| [fm-turnend-guard-grok.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-turnend-guard-grok.sh) | Grok Stop adapter for the same guard | hook payload | none | `.grok/hooks/` |
| [fm-hook-host-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-hook-host-lib.sh) | "Which harness sent this hook payload?" so Claude-shaped hooks stand down under Cursor | sourced | payload | Hook entries |
| [fm-arm-pretool-check.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-arm-pretool-check.sh) | PreToolUse transport: denies a watcher arm not run as its own tracked background call | payload or `--command` | none | All primary hooks |
| [fm-arm-command-policy.mjs](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-arm-command-policy.mjs) | Lexical shell parser and the arm policy (never runs the command) | command | none | The two pretool checks |
| [fm-cd-pretool-check.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-cd-pretool-check.sh) | PreToolUse transport: denies a persistent `cd` of the primary shell into a project clone | payload or `--command` | none | All primary hooks |
| [fm-cd-command-policy.mjs](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-cd-command-policy.mjs) | The cd-guard policy on the shared parser | command | none | `fm-cd-pretool-check.sh` |
| [fm-subagent-pretool-check.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-subagent-pretool-check.sh) | Denies the primary's own delegation tools, which leave no meta, no brief, and die with the session | payload | none | `.claude/settings.json` (`.*` matcher) |
| [fm-check-register.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-check-register.sh) | Binds a custom watcher check to its current bytes (hash) | `<id>` | `state/<id>.check.sh`, `.check-trust` | FM, mail/tool checks |
| [fm-check-unregister.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-check-unregister.sh) | Retires a custom check and its binding | `<id>` | same | FM |
| [fm-check-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-check-lib.sh) | Validates registrations; runs checks from private hashed snapshots | sourced | same | Watcher |
| [fm-inactive-reconcile.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-inactive-reconcile.sh) | On every poll: publishes a child's terminal `done:`/`failed:` upstream (secondmate homes); flags suspicious inactive outcomes | `scan`, `report`, `acknowledge` | status, `state/terminal-outcomes/` | Watcher, startup network |
| [fm-supervision-host.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-supervision-host.sh) | Owns the watcher cycle for a non-Pi primary and runs a headless engine session that handles routine wakes; returns to main only when needed | `park [--restart]` | `state/.supervision-host*` | Arm owners (default on Claude) |
| [fm-supervision-engine-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-supervision-engine-lib.sh) | Home gate for the host and one engine turn (Claude engine, `sonnet` default) | sourced / `enabled` | `config/supervision-host(-off)` | Host, instructions |
| [fm-host-mirror.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-host-mirror.sh) | Carries what the captain and main said to the host's engine at each attended wake | `hook <harness>` | mirror file and cursor | Claude, Cursor hooks |
| [fm-branch-prompt.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-branch-prompt.sh) | The supervision branch's byte-stable system prompt (kept identical for prompt caching) | none | tracked files only | Pi branch, host |
| [fm-branch-dispatch.mjs](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-branch-dispatch.mjs) | Which queued rows the branch may claim, for a non-Pi host | `scope`, `offer` | queue | Host |
| [fm-branch-outcome.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-branch-outcome.sh) | Append-only outcome store of what the branch handled, with a read cursor | subcommands | `state/branch-outcomes.jsonl` | Branch, drain, session start |
| [fm-branch-report.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-branch-report.sh) | The branch's report command off Pi: records one handled event, scoped to the claimed tasks | `--task --verdict --summary` | outcome store | Host engine |
| [fm-supervise-daemon.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-supervise-daemon.sh) | Away-mode sub-supervisor: wraps the watcher, self-handles routine wakes in bash, injects batched digests into the captain pane | env | `state/.subsuper-*`, `.afk` | `/afk` launcher |
| [fm-supervisor-target-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-supervisor-target-lib.sh) | Finds the captain's pane for injection | sourced | env | Daemon, afk launcher |

#### G. Away and quiet modes

| Script | What it does | Inputs | Reads / writes | Called by |
|---|---|---|---|---|
| [fm-afk-contract.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-afk-contract.sh) | The away/quiet record: the captain's away words verbatim, read-back, archive, cross-subsystem lock ("no phone channel") | subcommands | `state/.afk-contract`, `state/afk-contracts/` | Afk launcher, merges |
| [fm-afk-launch.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-afk-launch.sh) | `/afk` entry and exit; launches the daemon in a hidden tracked terminal where one runs | `enter`, `start`, `stop` | same | `/afk`, `/quiet` skills |
| [fm-afk-start.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-afk-start.sh) | Common daemon entry in the foreground | none | `state/.afk`, daemon lock | Afk launcher |
| [fm-afk-return.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-afk-return.sh) | Return brief from durable records (what was done under the away words, what waits) and the catch-up gate | `begin`, `check`, `guard` | outcome store, backlog, status | `/afk` skill |

#### H. Delivery, merge and teardown

| Script | What it does | Inputs | Reads / writes | Called by |
|---|---|---|---|---|
| [fm-nm-run-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-nm-run-lib.sh) | Attributes a no-mistakes run to a task by branch and head; bounded calls | sourced | `no-mistakes axi status` | Crew-state, teardown, dod |
| [fm-gate-refuse-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-gate-refuse-lib.sh) | Refuses fleet commands from inside a no-mistakes gate agent (which would otherwise load Firstmate's AGENTS.md and act as captain) | sourced | `NO_MISTAKES_GATE`, git common dir | Spawn, send, teardown, control |
| [fm-lab-home.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-lab-home.sh) | Mints a marked disposable home a gate agent may drive | `create`, `tmux-dir`, `teardown` | lab dir | Tests, labs |
| [fm-review-diff.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-review-diff.sh) | Diff of a task's branch or freshly fetched PR head against the real base | `<id> [--stat]` | meta, git | FM |
| [fm-pr-check.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-pr-check.sh) | Records `pr=` and `pr_head=` for a ready PR, refuses drafts and unreachable heads, arms the static merge poll | `<id> <pr-url>` | meta, `state/<id>.pr-poll*`, `.check.sh` | FM (`ship-landing`) |
| [fm-pr-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-pr-lib.sh) | Canonical PR identity (provider, host, path, number) and atomic poll artifacts | sourced | poll files | PR scripts |
| [fm-pr-poll.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-pr-poll.sh) | Byte-static watcher program: one `merged` line for a merged PR, silence otherwise (even on error) | sidecar | `gh`/`glab`/`gerrit-axi` | Watcher via `state/<id>.check.sh` |
| [fm-pr-state.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-pr-state.sh) | Read-only: one line per blocker it can see on a GitHub PR | `<pr-url>` | GitHub | FM |
| [fm-pr-reviewers.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-pr-reviewers.sh) | Read-only: suggests reviewers from recent authors of the changed files | `<pr-url>` | GitHub | FM |
| [fm-pr-merge.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-pr-merge.sh) | The only PR merge path: live checks (open, not draft, mergeable, every check green at the current head, every required check reported), `--squash` default, `--match-head-commit`, read-back, merge authority recorded | `<id> <pr-url> [-- method] [--allow-red name]` | meta, `state/<id>.merge-authority`, backlog hold | FM after the captain's word or `yolo` |
| [fm-merge-authority-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-merge-authority-lib.sh) | Persists whether a merge ran attended or away | sourced | `state/<id>.merge-authority` | `fm-pr-merge.sh`, watcher |
| [fm-merge-outcome-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-merge-outcome-lib.sh) | Publishes a confirmed merge: wake queue in a main home, parent channel in a secondmate home | sourced | queue, parent channel | Merge, watcher |
| [fm-merge-local.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-merge-local.sh) | `local-only` landing: fast-forwards the project's default branch to the task branch after approval; refuses divergence | `<id>` | project clone, meta | FM |
| [fm-teardown.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-teardown.sh) | Fail-closed cleanup: proves work landed (remote-reachable, merged PR head, or content in default), closes the endpoint, `treehouse return --force`, clears state, backlog Done, fleet sync (3,847 lines) | `<id> [--force]` | everything for the task; keeps `data/<id>/` | FM (`ship-landing`) |
| [fm-lock-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-lock-lib.sh) | "Is this git lock provably abandoned?" (lsof + age) | sourced | lock files | Teardown, fleet sync |
| [fm-fleet-sync.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-fleet-sync.sh) | Fast-forwards clones' default branch, prunes merged branches, reports `STUCK:` instead of forcing | `[project]` | `projects/*` | Bootstrap, teardown |
| [fm-ff-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-ff-lib.sh) | Guarded fast-forward for Firstmate's own checkouts and secondmate homes | sourced | git | Update, spawn, bootstrap |
| [fm-contributions.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-contributions.sh) | Watches owned PRs and issues (checks, reviews, maintainer signals) and wakes on changes | `snapshot`, `poll`, `verdict`, `ack`, `arm` | `data/<id>/contributions.json` | Watcher check, `bearings` |
| [fm-contributions.jq](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-contributions.jq) | Projection used by the script above | jq | none | `fm-contributions.sh` |
| [fm-fleet-ledger.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-fleet-ledger.sh) | Opt-in JSONL activity ledger outside tools can follow (dispatched, appended, pr_ready, merged, cleaned_up) | event args | `state/fleet-ledger.jsonl` | Brief's status command, spawn, watch, merges, teardown |

#### I. Fleet views

| Script | What it does | Inputs | Reads / writes | Called by |
|---|---|---|---|---|
| [fm-fleet-snapshot.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-fleet-snapshot.sh) | Canonical JSON snapshot (`fm-fleet-snapshot.v1`) of backlog, tasks, decisions, secondmates; caches remote ledgers | `--json` | all records; `state/secondmate-summary-cache/` | Heartbeat review, views |
| [fm-fleet-view.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-fleet-view.sh) | Markdown rendering of the snapshot | none | none | FM |
| [fm-bearings-snapshot.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-bearings-snapshot.sh) | Compact TOON "pick up where I left off" projection; `--include-prs` adds live GitHub | flags | snapshot | `/bearings` skill |
| [fm-bearings-board.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-bearings-board.sh) | Builds and arms the interactive Lavish fleet board, bound to the captain-hold answer intake | `build <json>`, `path` | board HTML | `/bearings lavish` |
| [fm-home-summary-refresh.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-home-summary-refresh.sh) | Atomically publishes this home's summary ledger for a parent to read | `[--best-effort]` | `state/home-summary.json` | Watcher, spawn, teardown |

#### J. Secondmates, local and remote

| Script | What it does | Inputs | Reads / writes | Called by |
|---|---|---|---|---|
| [fm-home-seed.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-home-seed.sh) | Provisions a local secondmate home (`treehouse get --lease` or a path), clones projects, writes charter and markers, transactionally | `<id> <home|-> {projects|--no-projects}` | new home, `data/secondmates.md` | FM (`secondmate-provisioning`) |
| [fm-secondmate-charter-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-secondmate-charter-lib.sh) | Pulls summary and scope from a filled charter | sourced | charter | Seeds |
| [fm-secondmate-registry-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-secondmate-registry-lib.sh) | Parser for `data/secondmates.md` records (local and remote) | sourced | registry | Many |
| [fm-secondmate-parent-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-secondmate-parent-lib.sh) | Parses the home's parent binding (local path or remote) | sourced | `.fm-secondmate-parent` | Parent channel, teardown |
| [fm-parent-channel-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-parent-channel-lib.sh) | Where a secondmate's captain-facing lines go, and appending one at most once; scripts publish outcomes so delivery never depends on the model | sourced | parent status file | Reconcile, PR check, hold, merge, teardown |
| [fm-secondmate-report.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-secondmate-report.sh) | Optional helper: append a `corr=`-tagged reply to the parent channel | `<verb> <corr> <note>` / `--doc` | parent channel | Secondmate agent |
| [fm-pending-reply-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-pending-reply-lib.sh) | Parent-side expectation per routed request: correlation id, one automatic recovery ask, one escalation | sourced | `state/pending-replies/` | `fm-send.sh`, remote reply |
| [fm-secondmate-liveness-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-secondmate-liveness-lib.sh) | Probes a secondmate endpoint (`alive/dead/missing/ambiguous/unreadable/unverified`); relaunches only on dead or missing | sourced | meta, backend | Bootstrap, watcher |
| [fm-secondmate-reconcile.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-secondmate-reconcile.sh) | Backstop: asks a mismatched secondmate to fix its own books, once per cooldown | `request`, `notify`, … | `state/reconcile-notify/` | Watcher, bootstrap |
| [fm-secondmate-nudge-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-secondmate-nudge-lib.sh) | Durable "re-read your config" nudge markers | sourced | markers | Bootstrap, config push |
| [fm-secondmate-restart.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-secondmate-restart.sh) | Asks each mate to persist open work, then relaunches it onto new instructions | `<id>…` | backlog, meta | `/updatefirstmate` |
| [fm-secondmate-restart-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-secondmate-restart-lib.sh) | Which mates can be restarted safely | sourced | meta | Update, restart |
| [fm-config-push.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-config-push.sh) | Pushes inherited config to live secondmates mid-session and nudges a re-read | none | `config/*` in each home | FM |
| [fm-config-inherit-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-config-inherit-lib.sh) | The allowlist of inherited config items and their propagation | sourced | `config/*`, `data/captain-shared.md` | Bootstrap, spawn, push |
| [fm-backlog-handoff.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-backlog-handoff.sh) | Moves Queued items to a secondmate's backlog (`tasks-axi mv`), via an outbox for remote ones | `<id> <item>…` | both backlogs, `state/handoff/` | FM |
| [fm-backlog-receive.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-backlog-receive.sh) | Idempotently ingests a delivered outbox on the remote host | outbox, bytes, sha, generation | backlog | Remote host via `fm-on.sh` |
| [fm-stow-cascade.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-stow-cascade.sh) | Lists each secondmate's memory budget and how to reach it, for `/stow` | none | registry | `/stow` |
| [fm-update.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-update.sh) | Self-update: fast-forwards Firstmate and every secondmate home, classifies mates for restart | none | git | `/updatefirstmate` |
| [fm-remote-home-seed.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-home-seed.sh) | Registers and provisions a whole home on an SSH host after a readiness gate | `<id> <alias> <root> <home> {project=origin…}` | registry; remote via `fm-on.sh` | FM |
| [fm-remote-home-provision.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-home-provision.sh) | On the host: clones code and projects from origins, publishes charter and markers | manifest on stdin | remote home | Remote entrypoint |
| [fm-remote-readiness-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-readiness-lib.sh) | Check → `--fix` → check again; the last read is the verdict | sourced | none | Seed, spawn, bootstrap |
| [fm-remote-doctor.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-doctor.sh) | "The single owner of what ready means" on a host: job worker, Herdr, launch agents, PATH, tools; gaps tagged `fixable:` or `human:` | `[--fix]` via `fm-on.sh` | LaunchAgents, `~/.firstmate/remote-job` | Readiness lib |
| [fm-on.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-on.sh) | Runs one tracked `bin/fm-*.sh` in a remote home: NUL-encoded argv, no agent forwarding, ssh exit status unchanged (255 = unknown) | `<id|alias> <fm-command> …` | none | Every remote operation |
| [fm-remote-entrypoint.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-entrypoint.sh) | Fixed SSH entry on the host: validates the command, stages it for the job worker | protocol + argv | job queue | `fm-on.sh` |
| [fm-remote-job-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-job-lib.sh) | The per-account job queue, record format, FIFO, PATH built by filesystem discovery | sourced | `~/.firstmate/remote-job` | Entrypoint, worker, doctor |
| [fm-remote-job-worker.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-job-worker.sh) | Long-lived worker that runs staged jobs under `env -i` with a 360 s default timeout | none | job queue | LaunchAgent or Linux supervisor |
| [fm-remote-job-reap-orphans.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-job-reap-orphans.sh) | Stops workers whose code root is gone | `[--dry-run]` | processes | Teardown, doctor |
| [fm-remote-file.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-file.sh) | Path-confined `get`, and `put` only for a backlog outbox | `get|put …` | remote home | Handoff, snapshot, reply relay |
| [fm-remote-delta-read.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-delta-read.sh) | Blocking, non-destructive read of new lines in a remote append-only log, with a prefix hash for continuity | `<log> <offset> <sha> [wait]` | remote log | Remote reply adapter |
| [fm-remote-inherit-push.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-inherit-push.sh) | Pushes the inherited allowlist to one remote route | `<id> <generation>` | none | Bootstrap, config push |
| [fm-remote-inherit.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-inherit.sh) | Applies one inherited item on the host | `put|absent …` | remote `config/` | Push above |
| [fm-remote-secondmate-control.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-secondmate-control.sh) | Host-local lifecycle for a remote mate: `launch`, `relaunch`, `state`, `send`, `capture`, `sync`, `update`, `retire`; always Herdr session `fm-remote` | verb + id | remote home, Herdr | `fm-on.sh` from spawn, send, peek, crew-state |
| [fm-remote-secondmate-relaunch.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-secondmate-relaunch.sh) | Relaunches a remote mate on a new runtime and updates the parent's record from what the host confirms | `<id> <harness> <model> <effort>` | local meta | FM |
| [fm-remote-herdr-guard.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-herdr-guard.sh) | macOS launchd target that makes the login session own the `fm-remote` Herdr server (so panes can read the keychain) | `<herdr> <session>` | Herdr socket | LaunchAgent |
| [fm-remote-herdr-owner-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-remote-herdr-owner-lib.sh) | Who owns a Herdr socket, and was it born in the login session | sourced | processes | Guard, doctor |

#### K. Process-to-event sources and extensions

| Script | What it does | Inputs | Reads / writes | Called by |
|---|---|---|---|---|
| [fm-procevent.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-procevent.sh) | Generic runner: supervises a registered long-polling child outside the agent's turn and turns its result into a durable `check` wake | `register`, `start`, `reconcile`, `handled`, `retire`, … | `state/procevent/`, `state/procevent-inbox/` | Watcher, adapters, FM |
| [fm-procevent-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-procevent-lib.sh) | Identity, ownership, capture and publication rules for that runner | sourced | same | Runner, adapters |
| [fm-procevent-quota.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-procevent-quota.sh) | Wakes when a provider's quota drops below a threshold or runs out | `arm [--threshold]` | quota-axi | FM |
| [fm-procevent-when.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-procevent-when.sh) | Condition → action, fired at most once, both argv hash-bound | `arm <name> --condition … --action …` | `state/when/` | FM |
| [fm-procevent-lavish.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-procevent-lavish.sh) | Lavish board adapter: captured feedback and answers become wakes | `arm <html>`, `read`, … | board results | Board, scouts |
| [fm-procevent-remote-reply.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-procevent-remote-reply.sh) | Mirrors a remote home's `state/parent-replies.status` into the parent through cursor-anchored delta reads | `arm <id>`, `handle`, … | remote log, local status | Spawn, bootstrap |
| [fm-procevent-extension-capture.pl](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-procevent-extension-capture.pl) | Perl capture helper for extension-backed sources | internal | inbox fds | `fm-procevent.sh` |
| [fm-extension.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-extension.sh) | Shell entry for extension binding, local and over `fm-on.sh` | args | none | FM |
| [fm-extension.mjs](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-extension.mjs) | Binds trusted external process-event adapter packages into a content-addressed store | `bind`, `list`, `verify`, … | `data/extensions/`, `config/extensions.d/` | Extension shell entry |
| [fm-extension-launch-barrier.mjs](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-extension-launch-barrier.mjs) | Publishes an invocation's process group before package code runs | internal | none | `fm-extension.mjs` |

#### L. Captain side channels: inbox, mail, voice, Relay

| Script | What it does | Inputs | Reads / writes | Called by |
|---|---|---|---|---|
| [fm-inbox.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-inbox.sh) | The captain's out-of-band surface: `note` (durable, one `check` wake), `say` (speech), `status` (records only), `ask` (side question), `reply`, `drain --ack` | subcommand | `state/inbox/` | Captain, voice relay, FM |
| [fm-mail.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-mail.sh) | Read unseen IMAP mail, send one SMTP message, or `poll` into wakes | `read`, `send`, `poll` | `.env`, `state/.mail-*` | FM, mail check |
| [fm-mail.py](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-mail.py) | The IMAP/SMTP engine (never marks mail seen) | subcommand | env | `fm-mail.sh` |
| [fm-mail-check.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-mail-check.sh) | Registers mail polling as a watcher check | `arm`, `disarm`, `check` | `state/mail.check.sh` | FM |
| [fm-voice-relay.py](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-voice-relay.py) | On the desktop: holds an AWS Bedrock speech session, answers from records, queues real work to `fm-inbox.sh` | SSH stream | records | Voice client over SSH |
| [fm-voice-client.py](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-voice-client.py) | On the laptop: capture and playback over SSH (audio devices unverified) | none | audio | Captain |
| [fm_voice_frame.py](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm_voice_frame.py) | Wire framing shared by both ends | module | none | Voice pair |
| [fm_voice_records.py](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm_voice_records.py) | What the voice agent may read, and the handover that queues work | module | records | Voice relay |
| [fm-x-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-x-lib.sh) | Relay config and reply context (mentions on X and Discord via a paired relay) | sourced | `.env`, `state/x-context/` | Relay scripts |
| [fm-x-poll.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-x-poll.sh) | One relay poll: a new mention becomes a wake | none | `state/x-inbox/` | Watcher check |
| [fm-x-reply.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-x-reply.sh) | Posts (or dry-runs) a reply | `<request_id> <text|--text-file>` | relay | `fmx-respond` skill |
| [fm-x-dismiss.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-x-dismiss.sh) | Drops a mention without replying | `<request_id>` | relay | FM |
| [fm-x-link.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-x-link.sh) | Links a spawned task to its mention for follow-ups | `<id> <request_id>` | meta | FM |
| [fm-x-followup.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-x-followup.sh) | Up to three public follow-ups in seven days | `--check`, `--clear`, post | meta | FM |
| [fm-public-followup.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-public-followup.sh) | Keeps a promised public reply across restarts from disk only | subcommands | `state/public-followup/` | Session start, teardown |
| [fm-public-followup-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-public-followup-lib.sh) | Its gate and private transport | sourced | same | Above |
| [fm-public-followup-emit.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-public-followup-emit.sh) | A worker reports one typed terminal result for a public promise | flags | owning home's inbox | Workers, teardown |
| [fm-public-followup-collect.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-public-followup-collect.sh) | Pulls results staged in a remote home | `drain`, `drop` | remote outbox | Owning home via `fm-on.sh` |

#### M. Development, CI, labs and small libraries

| Script | What it does | Inputs | Reads / writes | Called by |
|---|---|---|---|---|
| [fm-test-run.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-test-run.sh) | Behavior-test runner: selection, lanes, concurrency, coverage guard; refuses to run in the primary checkout from a worker | `--all`, `--family`, `--changed`, … | `tests/` | Contributors, CI, no-mistakes |
| [fm-test-isolation-proof.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-test-isolation-proof.sh) | Proves which tests are safe to run concurrently | `--pool`, `--jobs` | tests | CI |
| [fm-lint.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-lint.sh) | The one lint definition (pinned ShellCheck), plus workflow lint | paths or none | repo | CI, no-mistakes |
| [fm-lint-workflows.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-lint-workflows.sh) | Pinned actionlint over `.github/workflows` | paths | workflows | `fm-lint.sh` |
| [fm-doc-audience-check.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-doc-audience-check.sh) | Validates the documentation audience inventory | `--root` | `docs/documentation-audiences.json` | CI |
| [fm-install-herdr.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-install-herdr.sh) | CI's pinned Herdr (v0.7.4, protocol 16) with SHA-256 check | dest dir | binary | CI |
| [fm-install-treehouse.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-install-treehouse.sh) | CI's pinned Treehouse (v2.0.1) | dest dir | binary | CI |
| [fm-install-shellcheck.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-install-shellcheck.sh) | CI's pinned ShellCheck | dest dir | binary | CI |
| [fm-install-actionlint.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-install-actionlint.sh) | CI's pinned actionlint | dest dir | binary | CI |
| [fm-herdr-ci-cleanup.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-herdr-ci-cleanup.sh) | Removes only job-owned `fm-lab-*` Herdr sessions | `snapshot`, `teardown` | Herdr | CI |
| [fm-herdr-lab.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-herdr-lab.sh) | An isolated, never-`default` Herdr session for tasks that test Herdr itself | `name`, `provision`, `run`, `teardown` | Herdr | Workers with `--herdr-lab` briefs |
| [fm-herdr-lab-viewer.py](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-herdr-lab-viewer.py) | A real foreground Herdr client on a sized pty, for lab teardown tests | session | pty | `fm-herdr-lab.sh viewer` |
| [fm-live-lab.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-live-lab.sh) | Disposable live supervision lab (real primary, optional mate and worker) | `up`, `check`, `say`, `down` | lab root | Contributors |
| [fm-jev-mem-guard.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-jev-mem-guard.sh) | Wrapper for the memory guard below | args | none | Manual (no caller found) |
| [fm-jev-mem-guard.py](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-jev-mem-guard.py) | Host memory and swap thrash guard for many agents (`/proc/meminfo`, Linux) | thresholds | `/proc` | The wrapper |
| [fm-timeout-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-timeout-lib.sh) | One hard-bounded command runner (`timeout`, `gtimeout`, perl or bash) | sourced | none | Many |
| [fm-path-lib.sh](https://github.com/kunchenguid/firstmate/blob/eb77f02b/bin/fm-path-lib.sh) | Fork-free `dirname`/`basename` | sourced | none | Teardown, wake lib |

---

## 2. Workflows

Each flow is the numbered sequence the first mate follows, with the script or file that does each step. `AGENTS.md` sections are cited as §n; skills are under `.agents/skills/`.

### 2.1 Intake and triage

1. **Resolve the project** against `data/projects.md`, work under way, and the code; one confident match proceeds, otherwise one question (§7 "Intake and authority").
2. **Route**: to a secondmate whose registered scope fits (never by clone list), else the main home; `local-only` work stays in the main home (§7).
3. **Consult evidence first**: an existing report may already answer it; a diagnostic request is "evidence, not authorization to change code" (§7).
4. **Classify** the deliverable: **ship** (default; a project change) or **scout** (knowledge in `data/<id>/report.md`, never a PR), used only when the captain asks for a separate report or uncertainty could change what to build (§7). A scout can later be promoted in place with `fm-promote.sh`.
5. **Resolve the delivery mode** for a ship: the captain's current instruction, else the registry's standing posture from `bin/fm-project-mode.sh <project>` (`<mode> <yolo>`). Modes: `no-mistakes` (full pipeline to a PR), `direct-PR` (worker pushes and opens the PR), `local-only` (clean local branch, guarded fast-forward). A `no-mistakes-prod-only` project resolves per task: internal tooling ships `direct-PR`, product-facing or uncertain work ships `no-mistakes`. Unregistered projects default to `no-mistakes` with `yolo` off (§7).
6. **Resolve the merge posture** (`yolo`): off means the captain approves every merge; on means the first mate merges green, in-scope work itself. Mode and `yolo` are orthogonal; `yolo` never allows a red merge (§7 "Selected delivery path").
7. **Resolve the branch prefix** (`fm-project-mode.sh --branch-prefix`, default `fm/`).
8. **Pick harness, model and effort** (section 2.13).
9. **File the backlog item** with `bin/fm-tasks-axi.sh add …` in the owning home, recording mode, `yolo` and any deviation reason in its note (§7, §10).
10. **Dispatch independent work at once**, with no concurrency cap; same-file overlap is not a reason to wait (§7).

### 2.2 Brief generation

1. `bin/fm-brief.sh <id> <repo> --mode <mode> [--branch-prefix p] [--forge gerrit]` (or `--scout`, or `--secondmate`) scaffolds `data/<id>/brief.md`; it refuses an existing brief and a `--yolo` flag ("yolo never reaches the worker").
2. The scaffold for a ship has: `# Task` with `## Captain's intent` (`{TASK}`) and `## Firstmate spec` (`{FIRSTMATE_SPEC}`); `# Setup` with the isolation assertion (`pwd -P` and `git rev-parse --show-toplevel` must be the disposable worktree, else `blocked: launched in primary checkout` and stop) and the first action `git checkout -b fm/<id> --`; `# Rules` (rule 1 per mode, stay in the worktree, `gh-axi`, the status protocol, `blocked` after the same obstacle twice, `needs-decision` for human calls, a ban on administering shared infrastructure); `# Firstmate instruction inbox`; `# Project memory` (edit a project's AGENTS.md only to correct wrong facts); `# Definition of done` from `fm-dod-lib.sh`, opening with the machine-read line `Delivery contract: mode=<mode>` and `Ship branch: fm/<id>`; then `config/brief-include.md` verbatim if present (`bin/fm-brief.sh` lines 560–670).
3. The first mate fills the two placeholders: intent is the captain's own words plus the context needed to read them ("the reviewer treats that subsection as acceptance criteria"), with no speaker labels; spec is only the build instructions the ask needs, naming what is out of scope (§11).
4. At spawn, `fm-spawn.sh` refuses leftover placeholders, an empty or half-filled Task, a `## Captain's intent` line that opens with "Captain", and a `Delivery contract` line that disagrees with `--mode` or the registered forge (header, lines 5–24).
5. At spawn, the brief is rendered into `data/<id>/launch-brief.md` with the current worker-role overlay first (`fm_brief_worker_role` from `fm-dod-lib.sh`), so a relaunch always reads the current contract.

### 2.3 Spawn

`bin/fm-spawn.sh <id> projects/<repo> --mode <m> --yolo <on|off> [--harness h --model m --effort e] [--backend b]`, in order (header lines 1–330 and body):

1. Validate flags and brief (2.2 step 4); refuse `--yolo on` for a Gerrit project; print a notice when the mode is less rigorous than the registry's.
2. Take locks: the task-id lock, the per-home task-set lock, and the project-identity lock in the root home (so two spawns can't take the same Treehouse slot).
3. Resolve the backend (`FM_BACKEND` → `config/backend` → auto-detect `$TMUX`/`HERDR_ENV`/cmux → tmux) and create the endpoint: a tmux window, a Herdr tab in the launching home's own workspace (resolved from the launcher's pane, never a label), a zellij tab, a cmux workspace, or an Orca worktree+terminal.
4. Type `treehouse get` into the new pane (line 4221) and poll the pane's cwd until it is a git worktree root distinct from the project and its primary checkout; a pane that never gets there refuses. Write the slot's owner claim.
5. Require a clean worktree; fetch origin and reset to the remote default branch tip; refuse on an unreachable origin or dirty slot.
6. Wire the harness: `fm-claude-trust.sh` (Claude), `fm-agy-trust.sh`, Devin/Gemini/Kimi/Grok configs; the worker hooks in `<worktree>/.claude/settings.local.json`; `state/<id>.git-hooks/` for trailer stripping; `fm-busy-event.sh arm` for a fresh busy generation.
7. Export into the pane: `GOTMPDIR`, `COMPACT_ADVISER_DISABLE=1`, `FM_TASK_ID=<id>`, optional `TRACEPARENT`; optionally clear the environment to `config/launch-env-allowlist` plus a fixed floor.
8. Publish `state/<id>.meta` atomically (`window=`, `endpoint_task_id=`, `worktree=`, `project=`, `harness=`, `kind=`, `mode=`, `yolo=`, `branch=`, `tasktmp=`, `model=`, `effort=`, `busy_gen=`, `spawn_gen=`, `backend=` and the backend's ids; lines 4869–4905), and move the backlog item to In flight in the same step (`tasks-axi start`, `fm-backlog-transition-lib.sh`).
9. Launch the harness from a never-reused 0600 command file (the pane gets a short `source` line, avoiding the terminal's ~1,024-byte input limit). Claude gets `--dangerously-skip-permissions` (or `--permission-mode auto`), `--settings '{"feedbackDrafts":"off",…}'`, and an `--append-system-prompt` that makes the launch brief and inbox first-party and everything else untrusted (line 1991); its first message is a one-line doorbell naming the launch-brief record, written by `fm-operational-input.sh record launch-brief` because Claude strips invisible characters.
10. The first mate then confirms the worker is processing the brief and handles any dialog through `harness-adapters` (§7 "Dispatch").

### 2.4 The crewmate's working loop and status protocol

1. Run the isolation check; on failure append `blocked` and stop.
2. `git checkout -b fm/<id> --`; for `no-mistakes`, `no-mistakes doctor` then `init` if needed.
3. Work. Append a status line only for a phase change a supervisor would act on, as `echo "{state} [at=<epoch>]: {one short line}" >> state/<id>.status` (plus the opt-in fleet ledger append). "Each append wakes firstmate, so report sparingly … No step-by-step FYI progress lines; firstmate reads your pane for that."
4. Verbs: `working`, `needs-decision`, `blocked`, `paused` (a declared wait expected to clear on its own, including its own backgrounded pipeline call, optionally `until <UTC>`), `done`, `failed`; plus `resolved [key=…]` to close a decision or blocker, and `note` for pipeline-fix summaries. A mid-task `working:` is non-terminal: "do not end the turn after it".
5. A decision stays open until a `resolved` line with its exact key lands; a later `done` or `working` never closes it (`bin/fm-classify-lib.sh` owns the semantics).
6. At natural checkpoints, and whenever the doorbell rings, process `state/<id>.inbox/*.msg` in order and `mv` each to `handled/`.
7. Each harness turn end fires the worker hooks: `touch state/<id>.turn-ended`, busy → idle.
8. The status log is an event log, not current state; `fm-crew-state.sh` gives current state (a resumed worker writes nothing when it resumes).

### 2.5 Steering: inbox, doorbell and control

1. `FM_HOME=<home> bin/fm-send.sh <id> '<text>'` (FM_HOME is mandatory: "a steer must not silently resolve against the wrong home").
2. `fm-task-inbox-lib.sh` writes the next sequenced record `state/<id>.inbox/NNN.msg` (multi-line is fine); exit 0 means the record exists, which *is* the delivery.
3. It rings the doorbell, best-effort: one constant line typed into the pane, `: Firstmate instruction waiting: list '<inbox>'/*.msg and, in numeric order, read and act on each, then mv each handled file to '<inbox>'/handled/.` The leading `: ` is a shell no-op, so typing it into a dead pane's shell runs nothing. It skips the ring if the composer holds someone else's draft.
4. With `--resolve-key <k>`, the same call appends the `resolved [key=k]` line, closing the open decision at answer time, and feeds `fm-captain-hold.sh answers`.
5. The watcher re-rings an unacknowledged record once per grace period, up to a cap, then escalates `stale: <window> (unread firstmate instruction: …)`; a positively dead endpoint skips the ladder and goes to recovery.
6. For a remote secondmate the record is written in the remote home's inbox over `fm-on.sh`, idempotently; after a lost transport only the printed `FM_PENDING_REPLY_EXISTING_CORR=<id>` resend is safe.
7. Lifecycle never goes through `fm-send`: `bin/fm-control.sh <id> interrupt|exit|relaunch` is the control plane, with per-harness mechanics (Claude: one Escape, `/exit`) and a verified postcondition ("a marked `/quit` arrives as ordinary chat … the agent reasons ABOUT instead of executing", `bin/fm-control-lib.sh`).

### 2.6 The watcher and the wake queue

1. At every turn end of the primary, the **arm owner** starts or attaches to one watcher cycle: on Claude the Stop hook `fm-claude-stop-autoarm.sh` (or, since #6124, `fm-supervision-host.sh park` in its place); on Pi, omp and OpenCode their extension or plugin; on Cursor the stop hook parks in the foreground; Codex runs `fm-watch-checkpoint.sh` (`docs/watcher-continuity.md` "Ownership").
2. `fm-watch.sh` loops every `FM_POLL`=15 s, touching `state/.last-watcher-beat`. Per task it reads new status bytes, `turn-ended`, the busy record, pane hashes; every `FM_CHECK_INTERVAL`=300 s it runs registered `state/*.check.sh` (merge polls, Relay, mail, custom); heartbeat every 600 s backing off to 7,200 s (lines 268–345).
3. It classifies in bash (`fm-classify-lib.sh`). **Absorbed**: a no-verb signal from a provably working crew, a provably working stale pane (until `FM_STALE_ESCALATE_SECS`=240 s), a declared `paused:` wait (resurfaces every 4 h, `FM_PAUSE_RESURFACE_SECS`=14,400). **Actionable**: a captain-relevant status (`needs-decision`, `blocked`, `done`, `failed`), a no-verb signal without evidence of work, a stale pane not provably working, a wedge escalation (with `demand-deep-inspection` after repeats), an unread inbox record past the ladder, check output, a heartbeat backstop hit.
4. It appends each actionable wake to `state/.wake-queue` (`epoch seq kind key payload`) under a lock, then exits with one reason line (`signal: …`, `stale: …`, `check: …`, `heartbeat`). One reason closes one cycle.
5. The arm owner delivers the close: the Claude hook exits 2, which rewakes the session.
6. On a Claude primary with the **supervision host** (default now), the host's headless engine (a separate Claude session, `sonnet` by default, byte-stable prompt from `fm-branch-prompt.sh`) takes the wake first. For routine outcomes it acts through the same guarded scripts, records one row in `state/branch-outcomes.jsonl` through `fm-branch-report.sh`, and never wakes main; only captain-relevant events reach main. A per-task lease (`fm-lease.sh`) stops the engine and main from changing the same task at once (`docs/supervision-host.md`, `docs/configuration.md` "Supervision host").
7. Main runs `bin/fm-wake-drain.sh` before anything else: it presents claimed rows, OPEN DECISIONS, UNREAD STATUS, RECORD DIVERGENCE and new branch outcomes, and prints `WAKE_ACK_REQUIRED` (§8).
8. Main handles each wake (§8: `signal` → read events; `stale` → inspect, maybe `stuck-crewmate-recovery`; `check` → act on the result; `heartbeat` → whole-fleet review from `fm-fleet-snapshot.sh`).
9. Only after handling, main runs `fm-wake-drain.sh --ack-through <seq> --recovery-generation <g>`. An interruption before the ack leaves the rows for idempotent re-handling (at-least-once).
10. Guards keep this honest: `fm-turnend-guard.sh` blocks a turn end with work under way and no live watcher; `fm-arm-pretool-check.sh` denies an arm run with shell `&` ("That exact mistake silently took supervision down for ~30 minutes", `bin/fm-watch-arm.sh` header); `fm-guard.sh` prints a banner on a stale beacon.

### 2.7 Decisions and escalation to the captain

1. A worker appends `needs-decision [at=…] [key=<k>]: <options>` and stops; for a no-mistakes ask-user gate it writes every finding verbatim to `data/<id>/nm-<run>-findings.txt` and uses key `nm-<run>-<step>` (`fm_ask_user_escalation_block`).
2. The watcher surfaces it; the drain lists it under OPEN DECISIONS until a matching `resolved` line lands.
3. The first mate decides what it can: `ask-user-authority` says decide a finding "unambiguous toward the accepted design" (restoring accepted behavior, completing an approved design, an in-scope bug fix, however hard), and escalate only a contract expansion (new guarantee, subsystem, threat model, framework), an unsettled product call, a same-theme finding accreting machinery, or anything destructive, irreversible or security-sensitive. Labels such as "security" or "required" are evidence, not authority. Finding authority is not `yolo`.
4. To escalate, it holds the gating backlog item for the captain: `bin/fm-captain-hold.sh hold <id> --reason "<question and options>" [--until <date>]` (a decision is "simply a task waiting on the captain", §10), and writes one concise, evidence-first message: the requirement, the proposed expansion, the smallest compliant alternative, consequences both ways, a recommendation (`ask-user-authority` "Captain-facing escalation"). Several options may go on a Lavish board (`fm-bearings-board.sh`).
5. The captain answers in chat (or on the board). `fm-captain-hold.sh answer <id>` records his exact words; `--release` frees gated work.
6. The first mate sends the decision to the same worker with `fm-send.sh --resolve-key <k>`, naming the step, action, finding ids and the exact `no-mistakes axi respond` command; the worker never answers its own finding and never passes `--yes` (`validation-supervision`).
7. The captain hears outcomes, not mechanics: no "watcher", "worktree", "brief" or "task id" in chat; the final message of every turn must stand alone with every PR's full URL (§9).

### 2.8 Delivery

| Mode | Worker's last steps (from `fm_dod_block`) | Ready signal | First mate's side |
|---|---|---|---|
| `no-mistakes` | Commit; `done: {summary}` (the pipeline handoff, ungated); the first mate tells it to run `/no-mistakes`; it drives `no-mistakes axi run --intent <captain's intent only>`, backgrounded, reattaching after any timeout ("A killed or timed-out call is never evidence the daemon died"); answers gates; after CI green, checks the PR isn't a draft | `done: PR <url> checks green`, accepted only when HEAD is the commit the run pushed | Triggers validation on the same worker; judges by `fm-crew-state.sh`, never by the last status line; `fm-pr-check.sh` |
| `direct-PR` | Commit, push `fm/<id>`, open a ready PR with `gh-axi`, confirm `draft: no` | `done: PR <url>`, accepted only when HEAD is pushed to the PR branch | `fm-pr-check.sh`; no separate reviewer is added ("follow the faster path without adding an independent reviewer", §7) |
| `local-only` | Commit on `fm/<id>`, keep it a fast-forward of `main` (rebase if needed), no push | `done: ready in branch fm/<id>`, accepted when the head is on the shared local branch | Captain approves; `fm-merge-local.sh` |
| Gerrit variants | `gerrit-axi publish --squash`; no-mistakes skips push, pr, ci and the worker recovers the pipeline's fix commits before publishing | `done: PR <change url> published for review` | A human submits; Firstmate never does |

Then (`ship-landing`):

1. `fm-crew-state.sh <id>` reports `done` only when `fm-dod-lib.sh`'s named-head gate accepts; otherwise `blocked`, which means "steer the worker on the commit the refusal names", not a stuck worker.
2. `bin/fm-pr-check.sh <id> <url>` (URL copied from the worker's line, never assembled) records `pr=` and `pr_head=`, refuses a draft, writes a private sidecar, and arms `state/<id>.check.sh` whose bytes are exactly `fm-pr-poll.sh`.
3. The captain gets the full PR URL, a short outcome and, for no-mistakes, the risk level.

### 2.9 Merge

1. Authority: the captain's explicit word, or standing `yolo` on for that project; red merges need a current instruction naming the check (§7).
2. If the item is held for the captain, record his approval first: `fm-captain-hold.sh answer <id> --release` (`fm-pr-merge.sh` refuses a still-held row).
3. `bin/fm-pr-merge.sh <id> <url>`: records metadata through `fm-pr-check.sh`; reads live state (open, not draft, mergeable, no conflicts, every unwaived check green at the exact current head, every required check reported); merges with `gh pr merge --squash` by default and `--match-head-commit <verified head>` so a push after the read fails the merge; reads back that the PR is merged or queued; persists `state/<id>.merge-authority`; publishes the outcome (`fm-merge-outcome-lib.sh`).
4. Independently, the armed poll sees the merge within one check interval and queues a `check:` wake; duplicates are suppressed by `state/<id>.pr-poll-merge-notified`.
5. `local-only`: `bin/fm-merge-local.sh <id>` fast-forwards the project's default branch, refusing divergence.
6. After an autonomous merge, one line to the captain with the full URL (§7).

### 2.10 Teardown

`bin/fm-teardown.sh <id>` (header lines 1–110):

1. Refuse while the task has uncommitted work or work not landed. Landed = reachable from a remote-tracking branch; or a merged PR whose head contains the local work (the squash-merge case); or content already in the up-to-date default branch; `local-only` also accepts the local default branch. A scout needs its report and a passed decision-completion gate instead.
2. Verify the slot is still this task's (owner claim, no other record naming the path), so a reassigned slot is never reset under another worker.
3. Stop a parked no-mistakes run it owns; close the endpoint through the backend, refusing if the close can't be proven.
4. Write `state/<id>.backlog-close` (the intended transition), remove `state/<id>.meta` and volatile state (status cursors, inbox, hooks dir, check files, busy files), and run `tasks-axi done` (or `reopen` with the deliverable if the row is still an open captain call); a crash between the halves is replayed by the next session start.
5. `treehouse return --force <worktree>` with a bounded retry on a transient lock.
6. `fm-fleet-sync.sh <project>` refreshes the clone. `data/<id>/` stays (brief, report).
7. `--force` exists only with the captain's explicit authority to discard that work (§1 hard rule 3).
8. Re-evaluate queued work whose blockers have cleared (`ship-landing`).

### 2.11 Crash and restart recovery

1. **The first mate restarts**: the new session runs `fm-session-start.sh` once. `fm-lock.sh` takes the home lock or leaves the session read-only ("A lock-refused session must not spawn, steer, merge, drain …", §3). The digest shows the unacknowledged wake queue and every task's meta and status tail; `fm-bootstrap.sh` replays any `state/<id>.backlog-close`; network checks run detached and report later.
2. **Reconcile, don't reinvent**: only this home's recorded direct reports, only their recorded backend inventory, never a sweep of shared names (§5). A secondmate reconciles its own home and goes idle.
3. **A dead or stuck worker** (`stuck-crewmate-recovery`): read `fm-crew-state.sh` first (a live no-mistakes run stays authoritative even with a dead pane); then peek and check the unread inbox; answer a question the brief answers; interrupt and redirect a looping worker; relaunch a wedged one with `fm-control.sh <id> relaunch --note '<progress>'`; after a second failed relaunch, report failed with the preserved work.
4. **Relaunch is a transaction** (`docs/agent-control.md`): resolve the profile (a ship keeps its recorded harness); checkpoint the worktree head and dirty state; append the note to the instructions ("the replacement inherits the local copy but none of the conversation"); stop the old agent with `exit`; `fm-spawn.sh --relaunch` into the same worktree, adopting the endpoint or, on Herdr only, rebinding a proven-gone pane; journal in `state/<id>.control-relaunch`, rolled back on failure. tmux can't prove a missing window gone, so it refuses rather than risk two workers on one worktree.
5. **The watcher dies**: guards notice the stale beacon; a recovery episode (`state/.watcher-down`) is announced once and retired only by the drain's generation-bound ack (`docs/watcher-continuity.md`).
6. **Principle**: "durable state and live backend inventory, not conversation memory, are authoritative" (§5).

### 2.12 Remote secondmates, at the script level

The concept is in [#75](cloud-agents-firstmate.md#remote-secondmates-in-depth); here is the call chain.

1. **Seed**: `fm-remote-home-seed.sh <id> <alias> <root> <home> <project>=<origin>…` → readiness gate (`fm-remote-readiness-lib.sh`: doctor, `--fix`, doctor) → `fm-on.sh <id> fm-remote-home-provision.sh < manifest` → the host clones Firstmate and each project from its origin, writes `.fm-secondmate-parent` then `.fm-secondmate-home` last → the parent records `host:`, `root:`, `home:` in `data/secondmates.md`.
2. **Every call**: `fm-on.sh` → `ssh <alias> fm-remote-entrypoint.sh <base64 NUL argv>` → the entrypoint validates a tracked `bin/fm-*.sh` and stages a job in `~/.firstmate/remote-job` → the account's job worker runs it under `env -i` with a discovered PATH → stdout, stderr and exit relayed back; 255 = unknown completion.
3. **Launch**: `fm-spawn.sh <id> --secondmate` → sync the remote home to the parent's commit (`fm-remote-secondmate-control.sh sync`) → push inherited config (`fm-remote-inherit-push.sh`) → `fm-remote-secondmate-control.sh launch <id> <harness> … herdr` in Herdr session `fm-remote` → the parent writes `state/<id>.meta` with `remote_host=` and arms `fm-procevent-remote-reply.sh`.
4. **Request**: `fm-send.sh fm-<id> '<request>'` → `fm-pending-reply-lib.sh` records an expectation with a correlation id → the record lands in the remote inbox (`state/parent-route/<id>.inbox`) and the host rings its pane.
5. **Reply**: the remote mate appends `done corr=<id> …` (or runs `fm-secondmate-report.sh`) to its `state/parent-replies.status`; the parent's reply source does blocking delta reads (`fm-remote-delta-read.sh`, prefix hash for continuity) and mirrors new lines into the local status, fetching a document only through a `report=` pointer (`fm-remote-file.sh get`). A missed correlated reply triggers one automatic re-ask, then one escalation.
6. **Look**: `fm-peek.sh` and `fm-crew-state.sh` route to `fm-remote-secondmate-control.sh capture|state` over `fm-on.sh`; an unreachable host reads `unknown-remote`, never dead.
7. **Queue**: `fm-backlog-handoff.sh <id> <items>` → outbox → `fm-remote-file.sh put` → `fm-backlog-receive.sh` on the host.
8. **Retire**: `fm-teardown.sh <id>` → `fm-remote-secondmate-control.sh retire`, refusing while the home has work, an unsent outbox or an unresolved reply.

### 2.13 Quota and dispatch profiles

1. Without `config/crew-dispatch.json`: the crew harness from `config/crew-harness`, else the first mate's own (`fm-harness.sh crew`).
2. With it: the first mate matches the task against each rule's natural-language `when` by judgment ("shell scripts do not match the natural-language rules"), then passes concrete `--harness --model --effort`; `fm-spawn.sh` refuses a crew spawn without an explicit harness while the file exists (`docs/configuration.md` "Crew dispatch profiles").
3. A rule's `use` may be an array; then `quota-array-dispatch`: run `quota-axi` once (TOON), evaluate every candidate's eligibility (catalog, provider, auth, runway), rank by `spendPriority`, never silently downgrade the reasoning class, and account for every candidate in the decision.
4. Optional: `bin/fm-dispatch-resolve.sh <brief>` sends the brief's intent and spec to typesafe.ai's model when `TYPESAFE_API_KEY` is set; `clear` gives a profile, anything else falls back to step 2–3.
5. Effort fallback when unset: low for well-understood explicit work, xhigh for ambiguous investigation or design, never max without the captain's preference (§4).
6. Mid-task, `fm-procevent-quota.sh arm` can wake the first mate when a provider drops below a threshold.
7. Secondmates inherit the dispatch file, so their crews follow the same rules.

### 2.14 Worked example: one ship task, end to end

The captain types "the login page redirects to / instead of /dashboard after sign-in; fix it in acme-web". Assume: Claude primary on the Herdr backend, `acme-web` registered `direct-PR`, `yolo` off, no dispatch file. The task id the first mate picks is `login-redirect-k3`.

| # | Actor | Action | Script | Files touched |
|---|---|---|---|---|
| 1 | FM | Resolves the project, classifies ship, reads posture | `fm-project-mode.sh acme-web` → `direct-PR off`; `--branch-prefix` → `fm/` | reads `data/projects.md` |
| 2 | FM | Files the work item | `fm-tasks-axi.sh add login-redirect-k3 …` | `data/backlog.md` (Queued) |
| 3 | FM | Scaffolds and fills the brief | `fm-brief.sh login-redirect-k3 acme-web --mode direct-PR` | writes `data/login-redirect-k3/brief.md`; intent = the captain's sentence; spec = "fix the post-sign-in redirect; add a test; nothing else" |
| 4 | FM | Spawns | `fm-spawn.sh login-redirect-k3 projects/acme-web --mode direct-PR --yolo off` | new Herdr tab; pane runs `treehouse get` → a pool slot; `~/.claude.json` trust entry; `<slot>/.claude/settings.local.json`; `state/login-redirect-k3.git-hooks/`; `.busy-state`/`.busy-gen`; `data/login-redirect-k3/launch-brief.md`; `state/login-redirect-k3.meta` (`kind=ship mode=direct-PR yolo=off branch=fm/login-redirect-k3 harness=claude backend=herdr herdr_*…`); backlog → In flight; `claude --dangerously-skip-permissions …` with the launch doorbell |
| 5 | FM | Confirms the worker started; ends its turn | Stop hook → `fm-claude-stop-autoarm.sh` → `fm-supervision-host.sh park` (watcher inside) | `state/.last-watcher-beat` every 15 s |
| 6 | Worker | Isolation check, branch, reproduce | `pwd -P`, `git checkout -b fm/login-redirect-k3 --` | appends `working [at=…]: reproduced; redirect set in auth/callback.ts` |
| 7 | Watcher | Absorbs it: `working` is not a captain-relevant verb and the crew is provably busy | `fm-classify-lib.sh` | none queued |
| 8 | Worker | Finds two plausible targets (`/dashboard` or the `?next=` param) | none | appends `needs-decision [at=…] [key=redirect-target]: honor ?next= or always /dashboard?`; turn ends → `touch state/login-redirect-k3.turn-ended` |
| 9 | Watcher | Actionable signal | `fm-watch.sh` | appends a row to `state/.wake-queue`; closes with `signal: state/login-redirect-k3.status` |
| 10 | Host engine | Captain-relevant (a product call), so hands it to main (which rows the engine claims is owned by `.pi/extensions/lib/fm-branch-dispatch.ts`; this hand-off is **unverified**) | `fm-branch-report.sh --verdict captain` | `state/branch-outcomes.jsonl`; hook exits 2, main wakes |
| 11 | FM | Drains | `fm-wake-drain.sh` | shows OPEN DECISIONS: `login-redirect-k3 redirect-target` |
| 12 | FM | Escalates (a product call) | `fm-captain-hold.sh hold login-redirect-k3 --reason "…"` | backlog row held; chat: "Captain, the login fix needs one call: …, I recommend honoring `?next=` with `/dashboard` as the default." |
| 13 | Captain | "honor next, default dashboard" | | |
| 14 | FM | Records and relays | `fm-captain-hold.sh answer login-redirect-k3 --release …`; `fm-send.sh login-redirect-k3 --resolve-key redirect-target 'Honor ?next=, default /dashboard.'`; `fm-wake-drain.sh --ack-through <seq> …` | backlog answer recorded; `state/login-redirect-k3.inbox/001.msg`; `resolved [key=redirect-target]` appended; doorbell typed |
| 15 | Worker | Reads, acts, acks | `ls …inbox/*.msg`; `mv …/001.msg …/handled/` | inbox handled |
| 16 | Worker | Commits, pushes, opens a ready PR | `git push`, `gh-axi pr create`, `gh-axi pr view 42` → `draft: no` | appends `done [at=…]: PR https://github.com/acme/acme-web/pull/42` |
| 17 | FM | Wakes, checks current state, registers the PR | `fm-crew-state.sh login-redirect-k3` → `state: done …`; `fm-pr-check.sh login-redirect-k3 <url>` | meta `pr=`, `pr_head=`; `state/login-redirect-k3.pr-poll`, `.check.sh` |
| 18 | FM | Asks for the merge | chat with the full URL | backlog row held for the merge call (per `captain-hold-lifecycle`; whether every ready PR is held is **unverified**) |
| 19 | Captain | "merge" | | |
| 20 | FM | Releases, merges | `fm-captain-hold.sh answer … --release`; `fm-pr-merge.sh login-redirect-k3 <url>` → live checks → `gh pr merge 42 --squash --match-head-commit <sha>` → read back | `state/login-redirect-k3.merge-authority` (`attended`); merge outcome wake; fleet ledger `merged` if enabled |
| 21 | Watcher | The poll also sees it | `state/…check.sh` = `fm-pr-poll.sh` → `merged` | duplicate suppressed by `.pr-poll-merge-notified` |
| 22 | FM | Cleans up | `fm-teardown.sh login-redirect-k3` → merged PR head contains the local work → close the Herdr tab → `treehouse return --force <slot>` → `tasks-axi done` → `fm-fleet-sync.sh projects/acme-web` | meta, status, inbox, hooks and poll files removed; `data/login-redirect-k3/` kept; backlog Done with the PR link |
| 23 | FM | One line to the captain | chat | "Captain, the login redirect fix is merged: https://github.com/acme/acme-web/pull/42." |

---

## 3. What to borrow

Ranked by value for the least change. "Lands in" is a skill in this repo's [`skills/`](../../skills) or an open build ticket: [#13](https://github.com/yahyabedirhan/skills/issues/13) *A thinking session on the Mac can hand over to an orchestrator on the VPS*, [#15](https://github.com/yahyabedirhan/skills/issues/15) *An unfinished effort can be handed to a new orchestrator*, [#16](https://github.com/yahyabedirhan/skills/issues/16) *Agents on the Mac and the VPS can see each other's state*. Items 1–4, 6–8, 12 and 17 were already named in #75 and D13; this table adds the concrete change and the rest.

| # | Idea | Firstmate source | Lands in | What would change | Effort | Risk |
|---|---|---|---|---|---|---|
| 1 | **Worktree-isolation assertion** as the delegate's first step: `pwd -P` and `git rev-parse --show-toplevel` must be the delegate's worktree, else stop and report | `bin/fm-brief.sh` "# Setup"; §11 | **orchestrate-effort** step 4 (what the brief gives) and **implement** | One line in the brief and one in implement: "Before anything else, confirm you are in your own worktree; if not, stop and report." | S | Low |
| 2 | **Guarded merge**: read the PR live (open, not draft, mergeable, every check green at the current head, required checks reported), then merge with `--match-head-commit <head>` | `bin/fm-pr-merge.sh` header | **close-effort** step 2 | Replace "once its checks pass" with the fuller check and add `--match-head-commit` to its `gh pr merge`; a push after "go" then fails the merge instead of landing unreviewed commits | S | Low |
| 3 | **Status-file protocol**: sparse one-line events with fixed verbs (`working`, `needs-decision`, `blocked`, `paused … until`, `done`, `failed`, `resolved [key=…]`); a decision stays open until its keyed `resolved` | `bin/fm-brief.sh` rules 4–6; `bin/fm-classify-lib.sh` | **orchestrating** (a delegate that runs in a Herdr tab or on the VPS, not a sub-agent) and #16 | A `.scratch/<ticket>.status` (or a tracked path the remote reads over SSH) that the orchestrator reads, with the verb list in the brief; `paused` vs `blocked` tells "waiting on CI" from "needs me" | M | Low: a file; Medium if it grows machinery |
| 4 | **The brief on disk is the instruction; relaunch = same worktree + same brief + a progress note** | `docs/agent-control.md` "Transactional relaunch"; `stuck-crewmate-recovery` | #15, **handover**, **orchestrate-with-handoff** | A continue mode that reuses the existing worktree and branch, appends a dated "progress so far" section to the handoff, and starts the new orchestrator on it; never a fresh worktree while the old one is unaccounted for | M | Medium |
| 5 | **One owner per branch**: a lock naming the live session, and a new session stays read-only until it can take it | `bin/fm-lock.sh` (per-home session lock); §3 "lock-refused" | #15 (the "two orchestrators on one branch" question), **orchestrate-with-handoff** step 1 | Write `.scratch/orchestrator.lock` (host, harness pane or session id, time) at start; a continuing orchestrator checks it (and the other machine's Herdr agent status, #16) before committing | M | Medium: stale locks need a liveness check |
| 6 | **Durable inbox + one-line doorbell** for steering a session on another machine; the receiver acks by moving the file to `handled/`; an unacked message is re-rung, then escalated | `bin/fm-task-inbox-lib.sh`; `bin/fm-send.sh` | **handover-to-herdr**, #13, #16 | For a VPS orchestrator, write the message into its worktree's `.scratch/inbox/NNN.md` over SSH and send a constant one-line `herdr agent prompt` pointing at it; replaces multi-line pastes and remote-shell quoting ([herdr-vps.md](herdr-vps.md)) and gives a receipt | M | Medium |
| 7 | **Readiness check before handing off a machine**: read-only by default, each gap tagged `fixable` or `human` with the exact action, `--fix` only for automatable gaps, then check again and trust only the second read | `bin/fm-remote-doctor.sh`; `bin/fm-remote-readiness-lib.sh` | #13; **set-up-machine** / **maintain-environment** | A `check` step before the VPS handover that lists missing `treehouse`, `jq`, the agent CLI, login-shell-only PATH entries, with `human:` lines for the maintainer | M | Low (read-only) |
| 8 | **Unreachable is unknown, never dead or failed-over**: SSH exit 255 means "completion unknown"; keep the route, reconcile later | `bin/fm-on.sh`; `docs/remote-secondmates.md` | #16, #13 | One rule in the remote-check instructions: a failed SSH read reports "can't see the VPS right now", never "it stopped", and never starts a local replacement | S | Low |
| 9 | **Decide-or-escalate policy for review findings**: decide what is unambiguous toward accepted intent; escalate only a contract expansion, an unsettled product call, a same-theme finding accreting machinery, or destructive/security-sensitive work; labels are evidence, not authority | `.agents/skills/ask-user-authority/SKILL.md` | **orchestrating** "Talking to the user" | Add the four escalation triggers and the five-part escalation (requirement, expansion, smallest alternative, consequences, recommendation) beside the existing question shape | S | Low |
| 10 | **Stuck-delegate ladder**: peek → answer from the brief → interrupt and redirect → relaunch with a progress note → report failed after a second relaunch; "a low context reading is not wedging" | `stuck-crewmate-recovery` "Live-endpoint escalation" | **orchestrating** | A short section for Herdr-tab delegates; sub-agents have no equivalent today | S | Low |
| 11 | **Keep the maintainer's own words separate from the orchestrator's instructions**: intent verbatim (acceptance criteria), spec separate, and a mid-task ask appended to the intent verbatim | `bin/fm-brief.sh` `# Task`; §7, §11 | **handoff** and **to-tickets** | The handoff gets a "Maintainer's words" section quoted exactly; reviewers read it as acceptance criteria | S | Low |
| 12 | **A dedicated Herdr session for agent work** on a shared machine, separate from `default` | `docs/remote-secondmates.md` "Where the remote agent runs"; `fm-remote-secondmate-control.sh` | #13, **handover-to-herdr** | VPS orchestrators open in their own named session, so the maintainer's own tabs are never touched | S | Low |
| 13 | **PATH built by discovery for non-login SSH** (`~/.local/bin`, nvm, asdf, mise, Nix, Homebrew) | `bin/fm-remote-job-lib.sh` | #13 | The VPS handover runs remote commands with that PATH (or `bash -lc`) instead of assuming login-shell tools | S | Low |
| 14 | **"Done" means a pushed head**: a remote delegate's done is accepted only when its commit is reachable outside its own copy | `bin/fm-dod-lib.sh` named-head gate | #13, #15, **close-effort** | Before trusting "done" from the VPS, check `git branch -r --contains <sha>` after `git fetch`; the #16 scenario (unpushed work left on the VPS) is exactly this | S | Low |
| 15 | **Scripts write the outcomes the model might forget**: the facts (PR ready, merged, failed) are published by the step that records them, not by a reminder | `bin/fm-parent-channel-lib.sh` header | #16 | When a skill's step opens or merges a PR, the same step appends a line to the status file, so the Mac can read it even if the orchestrator never says it | M | Low |
| 16 | **One current-state line** reconciling the event log with the live evidence (no-mistakes run, pane, git) | `bin/fm-crew-state.sh` | #16 | A small read-only helper or skill step: `state: working|blocked|done|unknown · source: … · detail` for a remote orchestrator | M | Medium: scope creep |
| 17 | **Trust pre-registration** for a new worktree (`hasTrustDialogAccepted` in `~/.claude.json`) | `bin/fm-claude-trust.sh` | **handover-to-herdr** step 4 | Removes "ask the maintainer to accept the trust prompt"; needs the maintainer's explicit go-ahead because it writes Claude's config | S | Medium (config write) |
| 18 | **Opt-in activity ledger** (JSONL: dispatched, appended, pr_ready, merged, cleaned_up) | `bin/fm-fleet-ledger.sh`; `docs/fleet-ledger.md` | #16 | An append-only `.scratch/effort-ledger.jsonl` another machine or a dashboard can follow | S | Low |

### Don't borrow, and why

- **Adopting Firstmate itself.** It would replace **orchestrate-effort**, **handover** and **close-effort** with its own contract and one PR per task (D13, #75).
- **The watcher, wake queue and supervision host as machinery.** About 3,200 lines for the watcher alone, a durable queue with generation-bound acks, per-harness arm owners, and now a second LLM session. Firstmate needs it because one first mate supervises many projects for days; one orchestrator per effort can wait on `herdr agent wait` plus a status file (items 3, 6).
- **Bypass-permission workers.** Claude workers start with `--dangerously-skip-permissions` by default; this repo's rules keep permission checks, and a refused step stays refused: **close-effort** runs each commit, push and deletion as its own call and keeps whatever it can't prove merged.
- **AI-trailer stripping.** `fm-git-strip-ai-trailers.sh` removes co-author lines by default; this repo's commits end with attribution lines.
- **One PR per task and three delivery modes.** This repo's effort-level PR with cherry-picked ticket commits is deliberate (#75 mapping).
- **Dispatch profiles, quota routing and the typesafe.ai resolver.** Worth it only with several paid subscriptions to balance; the resolver also sends each brief's text to a third-party API.
- **no-mistakes as a second pipeline.** **code-review** at delivery already covers it (#75).
- **Denying sub-agents to the orchestrator.** Firstmate bans them because they die with the primary and leave no record; for a local effort, sub-agents in worktrees are this repo's design. The lesson applies only to long or remote efforts (items 3–6).
- **Relay, mail, voice, Lavish boards, the backlog on a Markdown file, the nautical persona.** Side features with no bearing on this repo's workflow; the tracker here is GitHub issues.
- **The size itself.** 214 scripts each owning one contract is how Firstmate stays correct across 14 harnesses and 5 backends; this repo runs one harness and one backend, and Firstmate's own §7 says to start with "the simplest direct end-to-end path".

---

## Open questions

- Unverified: whether the first mate holds every ready PR as a captain-held backlog item, or only when a decision is pending. `fm-pr-merge.sh` refuses a still-held row, and the watcher reads a hold "once firstmate handed the work to the captain" (`docs/architecture.md` "Event-driven supervision"), but no script forces the hold at PR-ready time.
- Unverified: the exact order inside `fm-spawn.sh` between publishing the meta, `tasks-axi start` and delivering the launch doorbell; the header says the backlog move happens "when meta is published" and the code has the launch after (lines ~4869, ~4995, ~5075), but this file didn't trace every branch.
- Unverified: how much the supervision host costs in tokens per day on a Claude primary; the docs cite a byte-stable prompt for caching (`docs/pi-supervision-branch.md` "Cost model"), not a measured figure for the host.
- The "Called by" column in section 1.5 comes from text references (a search of `bin/`, hooks and skills for each file name) plus headers, so some callers are mentions in comments. Tracing real call sites would need reading every call, which this file didn't do.
- TODO: proposed experiment for items 3 and 6 together (needs nothing installed): in a throwaway Herdr tab, start a Claude session with a one-paragraph brief that names a status file and an inbox folder in `.scratch/`, send one steer by file plus a one-line `herdr agent prompt`, and record whether it acknowledges by moving the file. Minutes; no config change.
- TODO: items 5 and 17 touch shared state (a lock the maintainer may need to clear by hand; Claude's `~/.claude.json`), so each needs the maintainer's go-ahead before it lands in a skill.

---

## Exploration log

Every action taken for this file. All on the maintainer's Mac, read-only unless stated. Nothing ran on the VPS; nothing was installed; none of Firstmate's scripts or the sibling tools were run.

| # | Where | Action | What it changed |
|---|---|---|---|
| 1 | This worktree | `gh issue view 88`; read `docs/research/cloud-agents-firstmate.md`, `cloud-agents.md` (D13) and `cloud-agents-session-workflow.md` for style; `gh issue view 13`, `15`, `16` | Nothing |
| 2 | This worktree | Read `SKILL.md` of orchestrate-effort, orchestrating (+ `lifecycle.md`), implement, handover, handover-to-herdr, close-effort, to-tickets, orchestrate-with-handoff, treehouse; listed `skills/` | Nothing |
| 3 | Local clone of Firstmate | `git pull` (from `260c4f08` to `eb77f02b`, 9 commits); `git log 260c4f08..HEAD` | Updated the read-only clone outside the repo |
| 4 | Local clone of Firstmate | Read `AGENTS.md` in full; `docs/scripts.md`; `docs/configuration.md` (home layout, toolchain, supervision host, dispatch profiles, installed hooks); `docs/architecture.md` headings; `docs/agent-control.md` "Transactional relaunch"; `docs/watcher-continuity.md` outline; `docs/supervision-host.md` intro; `.claude/settings.json`, `.cursor/hooks.json`, `.codex/hooks.json`; listed `.opencode`, `.pi`, `.omp`, `.grok`, `.claude/mods` | Nothing |
| 5 | Local clone of Firstmate | Skills: operational-home-layout, ship-landing, stuck-crewmate-recovery, validation-supervision, ask-user-authority, captain-hold-lifecycle, harness-adapters (+ `claude.md`, `dispatch.md`), quota-array-dispatch | Nothing |
| 6 | Local clone of Firstmate | A shell loop in the session scratchpad dumped every `bin/` file's header (4,226 lines) and a second loop listed, for each file, which scripts, hook files and skills mention its name; read both; read bodies of `fm-brief.sh` (template), `fm-dod-lib.sh` (definitions of done), `fm-spawn.sh` (header, meta block, Claude hooks, launch templates), `fm-watch.sh` (reason lines, timing constants), `fm-send.sh` and `fm-task-inbox-lib.sh` (doorbell, ladder), `fm-crew-state.sh`, `fm-teardown.sh` and `fm-pr-merge.sh` headers | Two files in the session scratchpad (outside the repo) |
| 7 | Local clone of Firstmate | `grep -r gnhf` over the repository (no match); counted `bin/` (214 files) and `tests/` (255); found the 54 scripts missing from `docs/scripts.md` | Nothing |
| 8 | Local clones next to Firstmate | `git pull` in gnhf, treehouse, lavish-axi (already current); `git clone --depth 1` of no-mistakes, tasks-axi, quota-axi, gh-axi, chrome-devtools-axi from github.com/kunchenguid; read the READMEs of no-mistakes, tasks-axi, lavish-axi and treehouse's CLI reference | Five new read-only clones outside the repo |
| 9 | This worktree | Wrote this file | This file |
| 10 | This worktree, 2026-09-30 | After "Every harness and project is set up and audited from the skills" (#66) merged into `main`: reread orchestrate-effort, close-effort and handover-to-herdr on `main`; renumbered the "Lands in" steps of items 1, 2 and 17 and reworded the close-effort line under *Don't borrow*. None of the 18 items has landed in a skill yet | This file |
