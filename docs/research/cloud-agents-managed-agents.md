# Managed Agents on the Claude Platform vs Claude Code cloud sessions

Facts for [Research: Claude Code cloud sessions tested from inside one (#78)](https://github.com/yahyabedirhan/skills/issues/78), under [Spec: research cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45). Anthropic sells two things that both run Claude "in the cloud, in a sandbox, in a session": **Claude Managed Agents** on the Claude Platform (the API) and **Claude Code cloud sessions** on claude.ai (`claude --cloud`, claude.ai/code, routines, projects). This page explains what Managed Agents is, how it differs, and whether it helps a maintainer who wants to delegate coding efforts off the Mac. Researched 2026-09-29 from inside a Claude Code cloud session (Claude Code 2.1.285).

It builds on [Claude Code in the cloud](cloud-agents-claude-code.md) (the Claude Code side in detail) and doesn't repeat it.

Evidence tags:

- **[doc ma:&lt;page&gt;, "&lt;section&gt;"]** Managed Agents docs, all under `https://platform.claude.com/docs/en/managed-agents/`: [overview](https://platform.claude.com/docs/en/managed-agents/overview), [quickstart](https://platform.claude.com/docs/en/managed-agents/quickstart), [environments](https://platform.claude.com/docs/en/managed-agents/environments), [cloud-sandboxes-reference](https://platform.claude.com/docs/en/managed-agents/cloud-sandboxes-reference), [self-hosted-sandboxes](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes), [self-hosted-sandboxes-security](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes-security), [sessions](https://platform.claude.com/docs/en/managed-agents/sessions), [session-operations](https://platform.claude.com/docs/en/managed-agents/session-operations), [events-and-streaming](https://platform.claude.com/docs/en/managed-agents/events-and-streaming), [reference](https://platform.claude.com/docs/en/managed-agents/reference), [agent-setup](https://platform.claude.com/docs/en/managed-agents/agent-setup), [tools](https://platform.claude.com/docs/en/managed-agents/tools), [permission-policies](https://platform.claude.com/docs/en/managed-agents/permission-policies), [skills](https://platform.claude.com/docs/en/managed-agents/skills), [github](https://platform.claude.com/docs/en/managed-agents/github), [files](https://platform.claude.com/docs/en/managed-agents/files), [memory](https://platform.claude.com/docs/en/managed-agents/memory), [multiagent-orchestration](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration), [scheduled-deployments](https://platform.claude.com/docs/en/managed-agents/scheduled-deployments), [webhooks](https://platform.claude.com/docs/en/managed-agents/webhooks), [budgets](https://platform.claude.com/docs/en/managed-agents/budgets), [onboarding](https://platform.claude.com/docs/en/managed-agents/onboarding), [migration](https://platform.claude.com/docs/en/managed-agents/migration), [vaults](https://platform.claude.com/docs/en/managed-agents/vaults).
- **[doc pricing, "&lt;section&gt;"]** [platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing).
- **[doc routines-fire, "&lt;section&gt;"]** [platform.claude.com/docs/en/api/claude-code/routines-fire](https://platform.claude.com/docs/en/api/claude-code/routines-fire), the Claude Code routine API documented on the Platform site.
- **[doc cc:&lt;page&gt;]** Claude Code docs under `https://code.claude.com/docs/en/`: [claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web) ("cloud"), [cloud-environments](https://code.claude.com/docs/en/cloud-environments) ("env"), [self-hosted-environments](https://code.claude.com/docs/en/self-hosted-environments) ("self-hosted"), [routines](https://code.claude.com/docs/en/routines), [claude-projects](https://code.claude.com/docs/en/claude-projects) ("projects"), [costs](https://code.claude.com/docs/en/costs).
- **[probe]** read-only checks made inside this cloud session; see the Exploration log.
- **Unverified** marks a claim with no primary source.

All Managed Agents pages carry `status: beta` and the beta header `managed-agents-2026-04-01` [doc ma:overview, "Beta access"].

## Short answer

- **Managed Agents is a developer API for building your own agent product.** You create agents, environments and sessions with an API key, send events, and pay API token rates plus $0.08 per running session-hour [doc ma:overview; doc pricing, "Claude Managed Agents pricing"].
- **Claude Code cloud sessions are an end-user product.** You sign in to claude.ai, start a session from the web, phone, Desktop or `claude --cloud`, and it draws on your Pro/Max plan with no separate VM charge [doc cc:cloud, "Limitations"].
- **They are different harnesses.** In a cloud session the Claude Code CLI itself runs inside the VM [probe]. In Managed Agents the agent loop runs on Anthropic's side and only tool calls run in the sandbox [doc ma:self-hosted-sandboxes, intro].
- **Is Claude Code's cloud built on Managed Agents?** No doc says so. Unverified. They share vocabulary, a sandbox image and a queue-and-worker design, but the harness, IDs, mounts and billing differ (section 4).
- **For this maintainer:** keep delegating through Claude Code (cloud sessions, routines, projects, or Claude Code on the VPS). Managed Agents is worth trying only as a small, budget-capped experiment: a self-hosted sandbox on the VPS driven by the `ant` CLI. That's the one way an individual plan can run Anthropic-orchestrated sessions on the VPS. Claude Code's own self-hosted environments are Team and Enterprise only (section 5).

## 1. Who each is for

| | Managed Agents | Claude Code cloud sessions |
|---|---|---|
| **Audience** | Developers building agents on the Claude API: "Pre-built, configurable agent harness that runs in managed infrastructure", "Best for long-running tasks and asynchronous work" [doc ma:overview]. Partners are told their product must "not appear to be Claude Code" [doc ma:reference, "Branding guidelines"] | A person doing their own coding work: "A Claude Code session that runs on cloud infrastructure instead of on your machine" [doc cc:cloud] |
| **Sign-in** | A Claude Console account and an API key (`x-api-key`) [doc ma:quickstart, "Prerequisites"]. "Enabled by default for all API accounts" [doc ma:overview, "Beta access"] | A claude.ai sign-in. Not available with a Console API key or through Bedrock, Vertex or Foundry [doc cc:cloud] |
| **Billing** | Tokens at API list rates (caching multipliers apply, no Batch discount), web search $10 per 1,000, plus session runtime at $0.08 per session-hour, counted only while `running` [doc pricing, "Claude Managed Agents pricing"] | Plan usage: "share rate limits with all other Claude and Claude Code usage … no separate compute charge for the cloud VM" [doc cc:cloud, "Limitations"]; usage credits past the limit [doc cc:costs] |
| **Where to watch** | Console session viewer (Developers and Admins), or `ant beta:sessions connect` in a terminal [doc ma:events-and-streaming, "Console observability"] | claude.ai/code, the mobile app, Desktop [doc cc:cloud] |

The Platform docs draw the same line for routines. The routine `/fire` endpoint "belongs to the Claude Code product surface": it uses a per-routine bearer token from claude.ai rather than an API key, has no SDK, and bills "Claude Code subscription usage on claude.ai" rather than "Claude Platform usage" [doc routines-fire, "Differences from the Claude Platform"]. So a Pro/Max plan does not pay for Managed Agents. It needs a separate Console organization with its own API billing.

## 2. The object model

### Objects

| Object | What it is | Lifetime |
|---|---|---|
| **Agent** | "The model, system prompt, tools, MCP servers, and skills", plus optional `multiagent` coordinator settings. Versioned: each change makes a new version, and sessions can pin a version [doc ma:agent-setup, "Agent configuration fields"; "Agent lifecycle"] | Until archived (existing sessions continue) |
| **Environment** | "Configuration for where sessions run: an Anthropic-managed cloud sandbox, or a self-hosted sandbox on your own infrastructure" [doc ma:overview, "Core concepts"]. Type `cloud` or `self_hosted` | "Persist until explicitly archived or deleted"; not versioned [doc ma:environments, "Environment lifecycle"] |
| **Session** | "A running agent instance within an environment". Created from an agent and an environment, then driven by events. Per-session overrides of `model`, `system`, `tools`, `mcp_servers`, `skills` [doc ma:sessions] | History kept until deleted; statuses `idle`, `running`, `rescheduling`, `terminated`; "A session that finishes its work goes `idle`, not `terminated`" [doc ma:session-operations, "Session statuses"] |
| **Sandbox** | "Each session gets its own isolated sandbox (a fresh Linux container)"; sessions sharing an environment "do not share filesystem state" [doc ma:environments] | Checkpointed when idle, kept for 30 days from sandbox creation; after that a resumed session gets a fresh sandbox [doc ma:events-and-streaming, "Resuming an idle session"] |
| **Events** | User, system, agent, session and span events, `{domain}.{action}` names [doc ma:reference, "Event types"] | Persisted server-side with the session |
| **Around them** | Memory stores (mounted at `/mnt/memory/`, versioned, shared across sessions), vaults (MCP OAuth credentials), files (Files API), scheduled deployments (cron), webhooks, budgets, outcomes [doc ma:memory; ma:vaults; ma:files; ma:scheduled-deployments; ma:webhooks; ma:budgets] | Independent of sessions: deleting a session doesn't touch them [doc ma:session-operations, "Deleting a session"] |

### Cloud sandbox

- **Machine.** "Isolated Linux containers on Anthropic-managed infrastructure": Ubuntu 24.04, x86_64, memory "Up to 8 GB", disk "Up to 10 GB". CPU is not stated [doc ma:cloud-sandboxes-reference, "Sandbox specifications"]. A Claude Code cloud VM is about 4 vCPU / 16 GB / 30 GB [doc cc:env, "Resource limits"].
- **Pre-installed.** Python 3.10-3.13, Node 20-22, Go 1.24/1.25, Rust, Java 21, Ruby, PHP 8.3, GCC/Clang, PostgreSQL 16 and Redis 7 (not running), git, jq, yq, tmux, rg, `docker` ("limited availability"), ffmpeg, pandoc, LibreOffice, TeX Live, and Playwright with Chromium at `/opt/pw-browsers` [doc ma:cloud-sandboxes-reference]. `gh` is not listed.
- **Adding packages.** A `packages` field per environment (apt, cargo, gem, go, npm, pip), "cached across sessions that share the same environment" [doc ma:environments, "Packages"]. There is no free-form setup script, unlike Claude Code's environment setup script [doc cc:env, "Setup scripts"].
- **Network.** `unrestricted` (the API default: everything except "a general safety blocklist") or `limited` (only `allowed_hosts`, plus optional package registries and MCP servers). Sandboxes made through Claude Studio default to `limited`. `web_search` and `web_fetch` run on Anthropic's servers and are restricted per tool, not by the environment [doc ma:environments, "Networking"; ma:cloud-sandboxes-reference]. The docs warn that access "is granted per host, not per operation", so an allowed host can be used to exfiltrate [doc ma:environments, "Networking"].
- **Files in.** Uploaded files mount read-only under `/mnt/session/uploads/`. Files the agent writes to `/mnt/session/outputs/` come back through the Files API [doc ma:files, "File paths"].
- **Repos in.** A `github_repository` session resource with an HTTPS URL, a GitHub token, an optional `mount_path` under `/workspace` and a branch or commit. Repos are cached across sessions. Repos are fixed for the session's lifetime; tokens can be rotated [doc ma:github]. Pushing and PRs go through the GitHub MCP server (`api.githubcopilot.com/mcp/`) declared on the agent, with a fine-grained token [doc ma:github, "Creating pull requests"; "Token permissions"]. There is no git proxy that hides the token, unlike Claude Code's [doc cc:env, "GitHub proxy"].

### Self-hosted sandbox

- **What moves.** "Self-hosted sandboxes keep the orchestration on Anthropic's side but move tool execution into infrastructure you control". Tool inputs and outputs still go to Anthropic. Skills and memory are copied into your sandbox [doc ma:self-hosted-sandboxes, intro].
- **Worker.** A process on your host claims work items from the environment's queue. It can be always-on (`ant beta:worker poll`, outbound HTTPS only) or webhook-triggered (SDK only). It runs tools in-process or starts one container per session (`--on-work ./spawn.sh` with `ant beta:worker run` as the image entrypoint) [doc ma:self-hosted-sandboxes, "Environment worker"; "Run a worker"]. Needs "A Linux host with `/bin/bash`", the `ant` CLI or the Python/TypeScript/Go SDK, and an environment key generated in the Console only [doc ma:self-hosted-sandboxes, "Before you begin"].
- **Tools.** The worker implements the standard toolset (`bash`, `read`, `write`, `edit`, `glob`, `grep`). The workdir confinement "is a guardrail for the file tools only, not a sandbox; it does not constrain `bash`" [doc ma:self-hosted-sandboxes, "SDK helpers"]. Custom tools and wrapped private MCP servers can be served from the worker (SDK worker only) [doc ma:self-hosted-sandboxes, "Serve custom tools from your sandbox"].
- **Repos and files.** "Anthropic doesn't mount files or GitHub repositories into self-hosted sandboxes". A session with a `file` or `github_repository` resource is rejected with a 400. You pass references in session `metadata`, and your spawn script fetches them [doc ma:self-hosted-sandboxes, "Start a session"]. Repo skill discovery from `.claude/skills` therefore doesn't run there [doc ma:skills, "Load skills from a GitHub repository"].
- **Your job.** Image hardening, egress rules, key storage and rotation, log retention [doc ma:self-hosted-sandboxes-security, "What you own"].
- **Availability.** The docs name no plan restriction for self-hosted sandboxes beyond API access (memory stores on self-hosted sandboxes may need enabling) [doc ma:self-hosted-sandboxes, "Troubleshoot memory mounts"]. Whether session runtime is billed for self-hosted sessions isn't stated; the pricing page names no exemption. Unverified.

### Tools, skills, instructions

- **Built-in toolset** `agent_toolset_20260401`: `bash`, `read`, `write`, `edit`, `glob`, `grep`, `web_fetch`, `web_search`; plus MCP toolsets and custom tools [doc ma:tools, "Available tools"]. Permission policies are `always_allow` (the agent toolset's default), `always_ask` (the MCP default) or `auto` (server-evaluated) [doc ma:permission-policies, "Permission policy types"]. That is a smaller surface than Claude Code's: no Agent/Task tool (multiagent is configured on the agent instead), no Skill tool, no hooks, no slash commands.
- **Instructions.** "`system_prompt` … and the `CLAUDE.md` hierarchy" map to "A single `system` string on the Agent" [doc ma:migration, "From the Claude Agent SDK"]. No repo `CLAUDE.md` or `AGENTS.md` is loaded automatically (inferred; the docs name no such loading). `system.message` events can add guidance mid-session on newer models [doc ma:session-operations, "Updating the agent configuration"].
- **Skills.** Attach Anthropic skills (`pptx`, `xlsx`, `docx`, `pdf`) or custom skills uploaded to the workspace, up to 500 per session. Or mount a repo whose root `.claude/skills/<name>/SKILL.md` is discovered at session start, cloud sandboxes only [doc ma:skills]. This repo keeps its skills under `skills/`, so they would need uploading, or a `.claude/skills` copy in the target repo.
- **Multiagent.** A coordinator agent delegates to other agents, each in its own "session thread" with its own context. All threads share one sandbox and filesystem [doc ma:multiagent-orchestration, "How it works"]. This is closest to the effort workflow's orchestrator and sub-agents, but everything runs in one sandbox, not one per ticket.

### Limits

Create endpoints 300 per minute, read endpoints 1,200 per minute per organization, plus the usage-tier limits [doc ma:reference, "Rate limits"]. Up to 50 `initial_events`, request body under 32 MB [doc ma:sessions, "Seed the session with initial events"]. Tool output over 100,000 characters is spilled to a file [doc ma:tools]. Not eligible for Zero Data Retention [doc ma:overview, "Beta access"].

## 3. Start, steer, watch, read back

| Step | Managed Agents | Claude Code |
|---|---|---|
| **Start** | `POST /v1/sessions` with `agent` and `environment_id`, and optionally `initial_events` to start work in one call, `resources` (repos, files, memory), `vault_ids`, `budget` [doc ma:sessions]. CLI: `ant beta:sessions create`. Non-interactive by design | `claude --cloud "task"` from the maintainer's terminal printed `Created cloud session: <title>`, a `View:` URL and a `Resume with: claude --teleport session_<id>` line, then exited [probe, brief]. Or web, mobile, Desktop [doc cc:cloud] |
| **Start on a schedule or hook** | Scheduled deployments (cron with timezone, minute granularity) plus a manual `run` endpoint [doc ma:scheduled-deployments] | Routines: schedule (hourly minimum), GitHub events, or `POST …/v1/claude_code/routines/<id>/fire` with a per-routine token; returns a session ID and URL [doc routines-fire; doc cc:routines] |
| **Steer** | `POST /v1/sessions/{id}/events` with `user.message`; `user.interrupt` stops a turn; `user.tool_confirmation` answers `always_ask` tools; `system.message` adds guidance; `tools` and `mcp_servers` can be replaced while idle [doc ma:events-and-streaming; ma:session-operations] | Type in the session UI; `claude -p "msg" --cloud <id>` posts one message [doc cc:cloud, "Send follow-ups from the CLI"] |
| **Watch live** | SSE at `GET /v1/sessions/{id}/events/stream`, per-thread streams for multiagent, optional token deltas [doc ma:events-and-streaming, "Event deltas"]. `session.status_idle` carries a `stop_reason` (`end_turn`, `requires_action`, `budget_reached`) | claude.ai/code, mobile, Desktop. No documented terminal stream [doc cc:cloud] |
| **Notify** | Webhooks for session, vault and agent events (`session.status_idled`, `session.status_terminated`, `session.budget_reached` …): up to three attempts, not a durable log [doc ma:webhooks, "Delivery behavior"] | Desktop notifications for projects; phone push for Remote Control. Plain cloud sessions: unverified [doc cc:projects; see cloud-agents-claude-code.md §9] |
| **Read back** | `GET /v1/sessions/{id}/events` lists the full persisted history; `session.usage` events carry cumulative cost; `GET /v1/files?scope_id=<session>` lists outputs [doc ma:sessions; ma:files] | `claude --teleport <id>` copies the conversation locally; otherwise the UI and GitHub (branch, PR, `Claude-Session` trailer) [doc cc:cloud] |
| **Stop / clean up** | Archive (read-only), delete (removes events and sandbox) [doc ma:session-operations] | Archive in the UI; VM reclaimed after idle [doc cc:cloud] |
| **Cap spend** | `budget.max_list_cost` per session (hard ceiling at list price; the session pauses at `budget_reached`) [doc ma:sessions, "Set a session budget"] | Plan limits; usage credits [doc cc:costs] |

**What a cloud session has instead.** The main session here has a "Claude Code Remote" MCP server with `create_session`, `list_sessions`, `get_session`, `interrupt_session`, `archive_session`, `set_session_title`/`set_session_tags`, routine tools (`create_trigger`, `fire_trigger`, `list_triggers` …), `send_later`, `subscribe_pr_activity`, `watch_url`, `add_repo` and `list_environments` [probe, brief]. They map roughly onto Managed Agents calls: create, retrieve, `user.interrupt`, archive, scheduled deployments, webhooks. The difference is that they act on claude.ai sessions as the signed-in user, billed to the plan, and they have no call that returns the event history. So the Claude Code cloud already gives an agent inside a session the start, interrupt and schedule half of Managed Agents' control surface. It lacks the read-back half (event list, SSE, usage and cost per session).

## 4. Is Claude Code's cloud built on Managed Agents?

**Unverified.** No page read says so, on either docs site. The Platform site documents the routine API as "the Claude Code product surface", separate from "Claude Platform APIs" [doc routines-fire]. The Managed Agents migration page talks about moving from the Claude Agent SDK, not from Claude Code on the web [doc ma:migration].

Evidence for a shared base:

- **Same sandbox image, or close to it.** Both are Ubuntu 24.04 x86_64 with the same language set, Postgres 16 and Redis 7 not running, and Playwright with Chromium at `/opt/pw-browsers` via `PLAYWRIGHT_BROWSERS_PATH` [doc ma:cloud-sandboxes-reference]. This VM has exactly that path and variable [probe, brief], and the Claude Code docs name no browser [doc cc:env].
- **Same vocabulary.** "Environment" is the unit in both. Claude Code's environment IDs use the `env_` prefix (the Remote MCP `create_session` tool describes "a tagged ID starting with 'env_' (or 'ccpool_' for self-hosted pools)"), as do Managed Agents' (`ANTHROPIC_ENVIRONMENT_ID="env_..."`) [doc ma:self-hosted-sandboxes, "Generate an environment key"]. Both call the self-hosted credential an "environment key" [doc cc:self-hosted, "Key concepts"].
- **Same self-hosted design.** In both, the control plane puts a session on an environment's queue, and a worker or runner you run claims it by outbound polling with a lease [doc cc:self-hosted, "Session lifecycle"; doc ma:self-hosted-sandboxes, "Environment worker"].
- **Same beta date.** The beta headers are `managed-agents-2026-04-01` and `experimental-cc-routine-2026-04-01`. The routine `/fire` endpoint now accepts requests with or without its beta header ("the endpoint accepts requests with and without it") [doc routines-fire, "Headers"].

Evidence against, or at least for a different harness on top:

- **Where the loop runs.** In this VM the process tree is `process_api` (PID 1, `--firecracker-init`) → `sh` → `/opt/env-runner/environment-manager task-run --session cse_<id> …` → `/opt/claude-code/bin/claude` [probe]. The Claude Code CLI runs inside the VM. Claude Code's self-hosted runner likewise "spawns a child Claude Code process" [doc cc:self-hosted, "Session lifecycle"]. A Managed Agents sandbox only executes tool calls, and "orchestration [stays] on Anthropic's side" [doc ma:self-hosted-sandboxes].
- **Different IDs and mounts.** Managed Agents sessions are `sesn_…` [doc ma:files], and its sandboxes use `/workspace`, `/mnt/session/uploads`, `/mnt/session/outputs` and `/mnt/memory`. Claude Code sessions are `session_…` in URLs and `cse_…` in `CLAUDE_CODE_REMOTE_SESSION_ID`. This VM has none of the Managed Agents paths; it has `/mnt/user-data`, `/mnt/skills`, `/mnt/attach` and `/mnt/sandboxing` [probe].
- **Different sizes.** 4 vCPU / 16 GB / 30 GB here against "up to 8 GB" / "up to 10 GB" [doc cc:env; doc ma:cloud-sandboxes-reference].
- **Different auth, billing, git.** claude.ai OAuth and plan usage with a git proxy, against an API key, token billing and a GitHub token passed in the request.

The best reading: both probably sit on the same sandbox platform and image, with separate products on top. Claude Code runs its own CLI in the VM; Managed Agents runs a hosted loop that calls into a sandbox. That's an inference from the evidence above, not a documented fact.

## 5. Fit for this maintainer

The setup: an individual Pro/Max plan, a Mac, a small Hetzner VPS, and an effort workflow (thinking session → orchestrator → sub-agents → PR) whose skills live in `skills/` of a public repo and assume Claude Code (the Skill and Agent tools, `gh`, Herdr, treehouse).

**What Managed Agents would add:**

- A real API to start, stream, read back and cost-cap sessions from a script, with webhooks. Claude Code has no documented way to read a cloud session's transcript from outside [cloud-agents-claude-code.md §9].
- **A self-hosted sandbox on the VPS.** This works on any API account, needs only outbound HTTPS, and is the only Anthropic-orchestrated way to run sessions on the VPS from an individual plan. Claude Code's self-hosted environments are "public beta on Team and Enterprise plans" [doc cc:self-hosted, "Availability and limitations"].
- 30-day sandbox checkpoints on idle, instead of a VM reclaimed after an unstated idle period [doc ma:events-and-streaming; doc cc:cloud, "Environment expired"].
- Hard per-session budgets.

**What it would cost the maintainer:**

- **Money on top of the plan.** An illustrative estimate, not a measurement: one sub-agent ticket on Opus 5.5 reading 3M cached tokens ($0.20/MTok), writing 0.3M uncached or cache-write tokens ($4-5/MTok) and 60k output tokens ($20/MTok) costs about $3.30, plus $0.08 per running hour [doc pricing, "Model pricing"; "Claude Managed Agents pricing"]. A six-ticket effort with an orchestrator is plausibly $20-40 in API spend. On Claude Code the same work draws on the plan the maintainer already pays for.
- **Losing Claude Code.** There is no `CLAUDE.md`/`AGENTS.md` loading, no Skill or Agent tool, no hooks and no slash commands. Skills only arrive by upload or from `.claude/skills` at a mounted repo's root, and mounting doesn't work on self-hosted sandboxes. The skills here would need rewriting around a coordinator agent config and plain bash.
- **GitHub by hand.** A fine-grained PAT in each session request plus the GitHub MCP server through a vault. On self-hosted sandboxes, a spawn script also has to clone the repo from session `metadata`. `gh` isn't pre-installed.
- **Operating a worker.** An `ant beta:worker poll` service on the VPS, an environment key made in the Console, Docker for per-session isolation (the in-process worker gives `bash` the VPS user's full reach), and egress rules [doc ma:self-hosted-sandboxes-security].

**What it would take, minimally (not done here):** a Console account with API credits; one agent (Opus or Sonnet, a system prompt carrying the relevant `AGENTS.md` rules, the agent toolset with `bash` on `always_ask` or `auto`); one `self_hosted` environment plus an environment key; `ant beta:worker poll --on-work ./spawn.sh` on the VPS, where `spawn.sh` clones the branch named in session `metadata` into a per-session Docker volume; then `ant beta:sessions create … --metadata '{"branch": "…"}'` with a `budget` of a few dollars and an `initial_events` message, watched with `ant beta:sessions connect`.

**Recommendation.** Don't adopt Managed Agents for the effort workflow. It is a developer platform billed per token, and it discards the Claude Code features the workflow is built on, while the Pro/Max plan already covers Claude Code cloud sessions, routines (with an HTTP `/fire`), projects, and Claude Code run directly on the VPS. Revisit it in two cases: if the maintainer wants a programmatic, observable fleet (a script that starts N sessions, streams them and reads back cost), or if running Anthropic-orchestrated sessions on the VPS becomes important while Claude Code self-hosting stays Team-only. Then run one budget-capped self-hosted experiment as above before porting any skill.

## 6. Side by side

| | Managed Agents | Claude Code cloud session |
|---|---|---|
| **Audience** | Developers building agent products on the API [doc ma:overview] | Individual coders and teams on claude.ai plans [doc cc:cloud] |
| **Sign-in** | Console API key; environment key for self-hosted workers [doc ma:quickstart; ma:self-hosted-sandboxes] | claude.ai account; no API key [doc cc:cloud] |
| **Start** | `POST /v1/sessions` (+`initial_events`), `ant`, SDKs, Console test runner, scheduled deployments [doc ma:sessions; ma:onboarding; ma:scheduled-deployments] | Web, mobile, Desktop, `claude --cloud "task"` (terminal), routines (schedule, GitHub, `/fire`), projects [doc cc:cloud; cc:routines] |
| **Billing** | API tokens + $0.08 per running session-hour; web search $10/1k [doc pricing] | Plan usage, no VM charge; usage credits past the limit [doc cc:cloud; cc:costs] |
| **Harness** | Anthropic-hosted agent loop; tools execute in the sandbox [doc ma:self-hosted-sandboxes] | Claude Code CLI running inside the VM [probe] |
| **VM / sandbox** | Container, Ubuntu 24.04, up to 8 GB RAM / 10 GB disk; `packages` per environment [doc ma:cloud-sandboxes-reference; ma:environments] | VM, Ubuntu 24.04, ~4 vCPU / 16 GB / 30 GB; setup script, cached snapshot [doc cc:env] |
| **Network** | `unrestricted` (API default) or `limited` allowlist; web tools filtered per tool [doc ma:environments] | None / Trusted (default) / Full / Custom; GitHub, connectors, Anthropic API always reachable [doc cc:env] |
| **GitHub** | `github_repository` resource with your token; GitHub MCP for PRs; no git proxy; not on self-hosted [doc ma:github; ma:self-hosted-sandboxes] | GitHub App or `/web-setup`; git proxy keeps the token out; push to the checked-out branch (its own `claude/…` or a new one it names); GraphQL blocked; Create PR [doc cc:env; cc:cloud; probe, see [cloud-agents-session-probe.md §4](cloud-agents-session-probe.md#4-github-proxy)] |
| **Skills / instructions** | One `system` string; uploaded or Anthropic skills; repo `.claude/skills` on cloud only; no CLAUDE.md [doc ma:migration; ma:skills] | Repo `CLAUDE.md`, `.claude/` skills, agents, rules; claude.ai account skills; hooks with one repo [doc cc:env] |
| **Sub-agents** | Multiagent coordinator and threads in one sandbox [doc ma:multiagent-orchestration] | Agent tool subagents; projects for parallel threads on separate VMs [doc cc:cloud; cc:projects] |
| **Persistence** | History until deleted; sandbox checkpointed on idle, kept 30 days; memory stores across sessions; outputs via Files API [doc ma:events-and-streaming; ma:memory; ma:files] | Conversation on claude.ai; VM reclaimed after idle, files lost unless pushed; environment cache ~7 days [doc cc:cloud; cc:env] |
| **Steering** | Events API: `user.message`, `user.interrupt`, tool confirmations, `system.message`; tool updates while idle [doc ma:events-and-streaming] | Type in UI; `claude -p "msg" --cloud <id>`; Remote MCP `interrupt_session` [doc cc:cloud; probe] |
| **Watching / read-back** | SSE stream, full event list, usage and cost events, Console viewer, `ant beta:sessions connect` [doc ma:events-and-streaming] | UI only; `--teleport` copies it locally; no transcript API [doc cc:cloud] |
| **Notifications** | Webhooks (best effort, three attempts) [doc ma:webhooks] | Desktop (projects), phone push (Remote Control); plain sessions unverified [doc cc:projects] |
| **Spend cap** | Per-session `budget` [doc ma:budgets] | Plan windows [doc cc:costs] |
| **Self-hosting** | Any API account: `self_hosted` environment + `ant`/SDK worker on your Linux host; you mount repos and files [doc ma:self-hosted-sandboxes] | Team/Enterprise public beta: runners that spawn Claude Code; GitHub checkout by the runner [doc cc:self-hosted] |
| **Status** | Beta [doc ma:overview] | Cloud sessions not marked beta in the pages read; routines research preview; projects public beta [doc cc:routines; cc:projects] |

## Open questions

| Question | Why open | Proposed experiment |
|---|---|---|
| Is session runtime ($0.08/h) billed for self-hosted sessions? | Pricing names no exemption | Ask support, or run one short self-hosted session and read `session.usage` |
| Is Claude Code's cloud built on the Managed Agents platform? | No doc; shared image and vocabulary, different harness | Ask Anthropic; compare `check-tools` output here with a Managed Agents cloud session's |
| Can a Pro/Max user's Console organization be separate from, or linked to, the claude.ai account, and are there any credits for new API accounts? | Not covered in the pages read | Maintainer checks platform.claude.com billing |
| How many vCPUs does a Managed Agents cloud sandbox get? | Only memory and disk are stated | `nproc` in a test session |
| Does the `auto` permission policy behave like Claude Code's auto mode? | Both are server-evaluated; not compared in the docs | Read the permission-policies `auto` section against Claude Code's auto-mode docs |
| Could a Managed Agents coordinator run this repo's effort workflow with skills uploaded as custom skills? | Skills assume the Agent and Skill tools, `gh`, Herdr | One budget-capped trial ticket on a self-hosted VPS sandbox |

## Exploration log

All on 2026-09-29, inside this Claude Code cloud session.

| # | Where | Command or action | What it changed |
|---|---|---|---|
| 1 | Cloud VM | Read `.scratch/cloud-session/brief.md` and `docs/research/cloud-agents-claude-code.md` | Nothing |
| 2 | Cloud VM → platform.claude.com | `curl -sS https://platform.claude.com/docs/en/managed-agents/<page>.md` for environments, cloud-sandboxes-reference, self-hosted-sandboxes, sessions and overview. **All returned 200 through the session proxy**, so WebFetch wasn't needed (`platform.claude.com` is on the Trusted list [doc cc:env, "Default allowed domains"]) | Files in `.scratch/cloud-session/ma/` (ignored by git) |
| 3 | Cloud VM → platform.claude.com | `curl` of `llms.txt`, then the quickstart, github, files, agent-setup, tools, skills, session-operations, events-and-streaming, reference, scheduled-deployments, webhooks, budgets, multiagent-orchestration, permission-policies, self-hosted-sandboxes-security, memory, onboarding, vaults and migration pages, `about-claude/pricing.md` and `api/claude-code/routines-fire.md` (all 200) | Same scratch folder |
| 4 | Cloud VM → code.claude.com | `curl` of the `.md` form of claude-code-on-the-web, cloud-environments, self-hosted-environments, routines and costs (200) | Same scratch folder |
| 5 | Cloud VM | `ps -eo pid,ppid,comm`, `readlink /proc/<pid>/exe` and the environment manager's command line (IDs redacted), `ls` of `/mnt/*`, `/workspace`, `/mnt/session/outputs`, `/mnt/memory`, `/opt/pw-browsers`; names only of `CLAUDE*`/`CCR*`/`ANTHROPIC*` env vars; the first four characters of the session ID variable | Nothing |
| 6 | Cloud VM | Wrote this file | This file only; no commit |
| 7 | Cloud VM (integration) | Aligned the Start and GitHub rows with the first-hand probes (the create form's output; push to a new named branch; GraphQL blocked) | This file only |
