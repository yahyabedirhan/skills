# Claude Code in the cloud: environment, capabilities and limits

Facts for [Research: Claude Code's cloud agents - environment, capabilities and limits (#69)](https://github.com/yahyabedirhan/skills/issues/69), under [Spec: research cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45). It maps what Anthropic offers for running Claude Code off the Mac: cloud sessions (Claude Code on the web), starting them from the CLI, teleporting them back, routines, projects, and the smaller pieces around them. Researched 2026-09-29 against the docs at `code.claude.com` on that date and Claude Code 2.1.284 on the Mac.

It builds on [What each harness can and can't do](harness-capabilities.md) (how Claude Code loads instructions, permissions and hooks locally) and [Herdr across the Mac and the VPS](herdr-vps.md) (the VPS path). Neither is repeated here.

Evidence tags:

- **[doc]** Claude Code's official documentation, cited by page and section. Pages, all under `https://code.claude.com/docs/en/`: [claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web) ("cloud"), [cloud-environments](https://code.claude.com/docs/en/cloud-environments) ("env"), [web-quickstart](https://code.claude.com/docs/en/web-quickstart) ("quickstart"), [routines](https://code.claude.com/docs/en/routines), [claude-projects](https://code.claude.com/docs/en/claude-projects) ("projects"), [remote-control](https://code.claude.com/docs/en/remote-control), [cross-session-messaging](https://code.claude.com/docs/en/cross-session-messaging) ("messaging"), [mobile](https://code.claude.com/docs/en/mobile), [desktop](https://code.claude.com/docs/en/desktop), [skills](https://code.claude.com/docs/en/skills), [settings](https://code.claude.com/docs/en/settings), [tools-reference](https://code.claude.com/docs/en/tools-reference) ("tools"), [ultrareview](https://code.claude.com/docs/en/ultrareview), [costs](https://code.claude.com/docs/en/costs), [feature-availability](https://code.claude.com/docs/en/feature-availability) ("availability"), [self-hosted-environments](https://code.claude.com/docs/en/self-hosted-environments) ("self-hosted").
- **[changelog]** [`anthropics/claude-code` CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md), read at 2.1.284.
- **[bin]** `claude --help` of the installed 2.1.284, read-only.
- **[announce]** Anthropic's own announcement channel (the `@ClaudeDevs` account on X), seen through search-result excerpts only; the posts themselves returned HTTP 402 to a fetch. Weaker than [doc].
- **[probe]** a hands-on attempt made for this research; see the Exploration log.
- **Unverified** marks a claim with no primary source.

## Short answer

| | Cloud session (web, mobile, Desktop "Cloud", `claude --cloud`) | Routine | Project (threads) | Remote Control (for contrast) |
|---|---|---|---|---|
| **Runs on** | Fresh Anthropic VM per session: Ubuntu 24.04, x86_64, about 4 vCPU / 16 GB / 30 GB [doc env] | A cloud session per run [doc routines] | A cloud session per thread, or a local session on request [doc projects] | Your own machine [doc remote-control] |
| **Lifetime** | Keeps running with the laptop closed; VM reclaimed after an unspecified idle period, reopening restores the conversation but not background work [doc cloud, "Environment expired"] | One session per trigger | Threads auto-resolve after a week idle [doc projects] | As long as the machine and `claude` run |
| **Tools** | Python, Node 20-22, Ruby, PHP, Java, Go, Rust, C/C++, Docker, Postgres, Redis, git, gh, jq, tmux; more via a root setup script, cached as a snapshot [doc env] | Same, from the routine's environment | Same, from the project's environment | Whatever is installed locally |
| **Web** | Allowlist ("Trusted") by default; None / Full / Custom per environment; GitHub, connectors and the Anthropic API always reachable [doc env] | Same | Same | Your network |
| **Browser** | `chromedriver` ships with Node; no browser named in the docs; Claude in Chrome is local only. Unverified | Same | Same | Local Chrome |
| **What loads** | Repo `CLAUDE.md`, `.claude/` skills, agents, commands, rules; repo hooks, permissions and `.mcp.json` only with one repo; claude.ai account skills; **not** `~/.claude/*`, user MCP, or any plugins [doc env, "What carries over"] | Same, plus the routine's connectors | Same, plus project instructions, memory and plugins from project settings | Everything local |
| **GitHub** | Claude GitHub App or `/web-setup` (sends your `gh` token); proxy keeps the token out of the VM; push only to the session's branch; Create PR button [doc cloud; doc env] | Clones default branch, pushes `claude/…` branches [doc routines] | Own branch per thread, opens PRs, auto-fix on [doc projects] | Your git |
| **Start from** | Web, mobile, Desktop, `claude --cloud "task"` in an interactive terminal (`-p` is rejected with a task) [doc cloud; doc headless] | Schedule, API `POST …/fire`, GitHub event, `/schedule`, Run now [doc routines] | Web, Desktop, mobile [doc projects] | `claude remote-control` |
| **Long work** | Subagents yes; agent teams behind an env var [doc cloud] | Autonomous, no permission picker | Built for it: a coordinator plus parallel threads | Local limits |
| **Watch / answer** | claude.ai/code, mobile, Desktop; `claude -p "msg" --cloud <id>` queues a message; `ListAgents`/`SendMessage` reach it only from a Remote Control session [doc cloud; doc messaging] | Run list on claude.ai; `/schedule` reads run logs [doc routines] | Overview pane; Desktop notifications [doc projects] | claude.ai/code, mobile, push |
| **Move it** | `claude --teleport <id>` pulls it to a local checkout (one-way copy); Desktop "Continue in" sends local to cloud [doc cloud; doc desktop] | Open run as a session | "Run a thread on your computer" [doc projects] | Forking one from the Claude app runs the fork on your computer [changelog 2.1.273] |
| **Cost** | Plan usage, no separate VM charge [doc cloud, "Limitations"]; one-time promo credit $100 Pro / $250 Max spent first [announce] | Plan usage plus a daily run cap [doc routines] | Plan usage, "uses them faster"; 200 new threads a day [doc projects] | Plan usage |
| **Plans** | Pro, Max, Team; Enterprise premium seats [doc cloud] | Pro, Max, Team, Enterprise; research preview [doc routines] | Pro and Max, public beta, gradual rollout [doc projects] | Pro, Max; Team/Enterprise admin-enabled [doc availability] |

Cloud sessions need a claude.ai sign-in; they aren't available with a Console API key or through Bedrock, Vertex or Foundry [doc cloud, "Output and errors"; doc availability].

## 1. What there is

- **Cloud session.** "A Claude Code session that runs on cloud infrastructure instead of on your machine", on Anthropic's infrastructure by default, or on an organization's self-hosted environment. Started from the browser (claude.ai/code, "Claude Code on the web"), the mobile app's Code tab, the Desktop app with **Cloud** selected, the terminal with `claude --cloud`, or a routine. "The session keeps running after you close your laptop" [doc cloud, intro].
- **`claude --cloud`.** Creates a cloud session from the terminal. `--remote` is the older, deprecated spelling [doc cloud, "From terminal to cloud"]. The 2.1.284 help reads `--cloud [description|session_id|url]  Create a cloud session with the given description, or attach to an existing one by session ID or claude.ai/code URL` [bin].
- **Teleport.** `claude --teleport [<id>]`, `/teleport`, or `t` in `/tasks` pulls a cloud session into a local checkout [doc cloud, "From cloud to terminal"].
- **Routines.** "A saved Claude Code configuration: a prompt, one or more repositories, and a set of connectors", run by schedule, API call or GitHub event on cloud infrastructure. Research preview [doc routines].
- **Projects.** One coordinating conversation that starts parallel cloud "threads" and tracks them; public beta on Pro and Max, rolling out gradually, not on Team or Enterprise yet [doc projects].
- **Auto-fix.** A cloud session that watches a pull request and pushes fixes for CI failures and review comments; `/autofix-pr` starts one from the terminal. Needs the Claude GitHub App [doc cloud, "Auto-fix pull requests"].
- **Ultrareview.** `/code-review ultra` (or `claude ultrareview`) runs a multi-agent review as a cloud session. Three free runs on Pro and Max, then $5-25 each in usage credits [doc ultrareview, "Pricing and free runs"].
- **Around them, not cloud sessions:** Remote Control (drive a session on your own machine from claude.ai or the phone), Dispatch (message the Desktop app from the phone), channels, Desktop scheduled tasks and `/loop` (local), Claude in Slack / Claude Tag (Slack front end on the same cloud infrastructure), GitHub Actions (Claude Code in CI), and self-hosted environments (cloud sessions on your own runners, Team and Enterprise only, public beta) [doc remote-control, "Remote Control vs cloud sessions"; doc self-hosted, "Availability and limitations"]. A self-hosted runner on the VPS would be the cleanest way to give cloud sessions the VPS's tools, but it isn't available on the maintainer's individual plan.

## 2. Environment

- **Machine.** "Each session gets a fresh virtual machine (VM) running Ubuntu 24.04 on x86_64 … with your repository cloned and common toolchains pre-installed" [doc env, "What's available in cloud sessions"].
- **Resources.** "Approximate resource ceilings that may change over time: 4 vCPUs, 16 GB of RAM, 30 GB of disk". The VM "may stop tasks that need significantly more memory" [doc env, "Resource limits"].
- **User.** Setup scripts "run as root on Ubuntu 24.04, so `apt install` … work[s]" [doc env, "Setup scripts"]. Whether Claude's own commands run as root is unverified.
- **No shell for you.** "You don't get a shell into the session VM. Claude runs every command for you" [doc env, "Run tests, start services, and add packages"].
- **Lifetime.** Sessions persist across devices and keep running with the laptop closed. "Cloud sessions stop after a period of inactivity and the session's VM is reclaimed"; waiting on a connector approval counts as inactive. Reopening "provision[s] a fresh VM with your conversation history restored. Background work that was still running … such as subagents and shell commands, isn't restored" [doc cloud, "Environment expired"]. The idle period isn't stated. A question Claude asks can be answered "up to environment expiry" [doc cloud, "From terminal to cloud"].
- **What persists.** The conversation (on claude.ai), and whatever was pushed to GitHub. Files in the VM don't survive a reclaimed VM (inferred from "fresh VM"). Environment cache: when the setup script finishes in about five minutes, "Anthropic snapshots the filesystem and reuses that snapshot" for later sessions; rebuilt when the script or allowed hosts change or after about seven days. The cache holds files, not running processes [doc env, "Environment caching"].
- **Time limits.** The Bash tool's defaults apply (2 min, up to 10), raisable with `BASH_DEFAULT_TIMEOUT_MS` / `BASH_MAX_TIMEOUT_MS` on the environment; SessionStart hooks 600 s; setup script about 5 min to be cached [doc env, "Time limits"].
- **Context.** Cloud sessions set `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` themselves, so they compact earlier than a local session; `/compact` and `/context` work, `/clear` doesn't [doc cloud, "Manage context"].
- **Session identity.** `CLAUDE_CODE_REMOTE=true` inside the VM; `CLAUDE_CODE_REMOTE_SESSION_ID` holds the session ID. Commits get a `Claude-Session: <url>` trailer and PR bodies a session link unless `attribution.sessionUrl` is `false` [doc env, "Link output back to the session"; "Install dependencies with a SessionStart hook"].

## 3. Tools and commands

- **Pre-installed** (Anthropic-hosted): Python 3 with pip, poetry, uv, black, mypy, pytest, ruff; Node 20/21/22 (22 on `PATH`) with npm, yarn, pnpm, bun, eslint, prettier, chromedriver; Ruby 3.1-3.3; PHP 8.3; OpenJDK 21 with Maven and Gradle; Go; Rust; GCC, Clang, cmake, ninja, conan; docker, dockerd, docker compose; PostgreSQL 16 and Redis 7.0 (not started); git, gh, jq, yq, ripgrep, tmux, vim, nano. A `check-tools` command prints versions [doc env, "Installed tools"].
- **Not there:** anything else, for example .NET, Herdr, treehouse, codex, opencode. Installing is allowed: "Install them with a setup script", or ask Claude mid-session, though mid-session installs "don't carry over to other sessions" [doc env, "Add packages"]. Replacing the base image "isn't supported yet" [doc env, "Limitations in cloud sessions"].
- **Setup script vs SessionStart hook.** The script is per environment, set on claude.ai, runs before Claude starts, cached. A SessionStart hook is committed in the repo and runs on every start and resume, local too, so gate it on `CLAUDE_CODE_REMOTE` [doc env, "Setup scripts vs. SessionStart hooks"].
- **Bun** "has known proxy compatibility issues" behind the security proxy [doc env, "Installed tools"].
- **Slash commands.** Text-output built-ins work; terminal-only ones such as `/plugin` and `/resume` don't; `/model`, `/effort` take an argument; `/schedule` is refused inside a cloud session [doc cloud, "Manage context"; doc routines, "Troubleshooting"].
- **Tools that differ:** `SendUserFile` works in cloud sessions; the LSP tool stays inactive because plugin language servers don't start; `ListAgents`/`SendMessage` exist [doc tools].

## 4. Web and browser

- **Network levels** per environment: **None**, **Trusted** (the default: package registries, GitHub, cloud SDKs and a published allowlist), **Full** (any domain), **Custom** (your list, optionally plus the defaults) [doc env, "Access levels"]. A blocked request gets `403` with `x-deny-reason: host_not_allowed` [doc routines, "Environments and network access"].
- **Always reachable, whatever the level:** GitHub through its own proxy, MCP connectors (their traffic goes through Anthropic's servers), hosts named on API credentials, and the Anthropic API [doc env, "Access levels"].
- **Security proxy.** All outbound traffic goes through an HTTP/HTTPS proxy with rate limiting, content filtering and a DNS-level audit trail [doc env, "Security proxy"].
- **Trusted list** includes `code.claude.com`, `docs.claude.com`, `github.com`, the npm, PyPI, crates, Go, Maven registries, Docker Hub, `ghcr.io`, `*.googleapis.com`, `*.amazonaws.com`, `developer.apple.com`, `swift.org` and more; it doesn't include general sites [doc env, "Default allowed domains"]. So research against arbitrary web pages needs **Full** or **Custom** on the environment.
- **WebSearch** is a server-side tool on the Claude API [doc tools, WebSearch notes], so it should work in a cloud session regardless of the allowlist. Unverified in a cloud session. Whether **WebFetch** in a cloud session goes through the session's allowlist is not stated. Unverified.
- **Browser.** The docs list `chromedriver` with Node but name no Chrome or Chromium binary. Claude in Chrome drives the local Chrome and isn't listed for cloud sessions. Playwright's browser downloads come from hosts outside the Trusted list (unverified which ones). So a headless browser needs at least a setup script, and likely **Custom**/**Full** network. Unverified; this was a planned probe (see Open questions).

## 5. What loads

From the "What carries over from your setup" table [doc env] and [doc settings, "Settings in cloud sessions"]:

| Item | Loads? |
|---|---|
| Repo `CLAUDE.md`, `.claude/rules/` | Yes (part of the clone). `AGENTS.md` follows the local rule in [harness-capabilities.md](harness-capabilities.md) 1.1; this repo's `CLAUDE.md` imports it |
| Repo `.claude/skills/`, `.claude/agents/`, `.claude/commands/` | Yes |
| Repo `.claude/settings.json` hooks, permission rules, `env` | Only in a session with **one** repository |
| Repo `.mcp.json` | Only with one repository |
| Plugins in repo or user settings | **No**. Projects can add plugins in project settings |
| `~/.claude/CLAUDE.md`, `~/.claude/skills/`, agents, commands, user hooks, user settings | **No** ("Live on your machine") |
| User or local MCP servers (`claude mcp add`) | **No**; use `--scope project` and commit `.mcp.json`, or a claude.ai connector |
| Skills enabled on the claude.ai account | **Yes**: "Cloud sessions automatically load skills you enable on claude.ai" [doc skills, "Use skills in Cowork and cloud sessions"] |
| claude.ai connectors | Routines and projects: yes, chosen per routine/project. Plain cloud sessions: how connectors are chosen isn't stated; the docs only mention a session waiting to approve "an MCP connector tool call" [doc cloud, "Environment expired"], and the Desktop "+ Connectors" button isn't offered for cloud sessions [doc desktop]. Unverified |
| Server-managed settings | Yes; device MDM or managed files no |
| Transport env vars (`NODE_EXTRA_CA_CERTS`, mTLS) | Ignored |

**What this means here.** This repo keeps its skills under `skills/`, not `.claude/skills/`, so a cloud session on it gets none of the maintainer's skills from the clone; it gets only what's enabled on the claude.ai account. The global `~/.claude/CLAUDE.md` rules (privacy line, notification command, Herdr rules) don't reach a cloud session at all. Two ways to carry them, both unverified in practice: enable the skills on the claude.ai account, or commit a `.claude/skills/` (and project instructions) in the target repo.

## 6. GitHub

- **Granting access.** Either the **Claude GitHub App** (any public repo, plus private repos it's installed on; needed for auto-fix, GitHub triggers and project threads) or **`/web-setup`**, which sends the local `gh auth token` to Anthropic, stored encrypted; sessions then reach any repo that token can [doc cloud, "GitHub authentication options"; doc quickstart, "Connect from your terminal"]. `/web-setup` warns when the token lacks the `workflow` scope [doc quickstart].
- **Token handling.** In Anthropic-hosted environments, credentials "never enter a session's VM": a GitHub proxy swaps a scoped credential for the real token. `GH_TOKEN`/`GITHUB_TOKEN` read as the placeholder `proxy-injected` unless you set your own [doc env, "GitHub proxy"; "Work with GitHub issues and pull requests"].
- **Branch.** Web/mobile: pick a repository and branch; "each task gets its own session and its own branch" [doc quickstart]. `claude --cloud` clones "your current directory's GitHub remote at your current branch, not your local checkout, so push first" [doc cloud]. Routines start from the default branch and push `claude/`-prefixed branches; a push to another branch is refused if it's protected, has someone else's open PR, or carries others' commits [doc routines, "Repositories and branch permissions"]. Project threads work on a new branch from the default branch [doc projects].
- **Pushing.** "`git push` works only against the session's current working branch" [doc env, "GitHub proxy"]. Whether a session can push to a branch name the prompt chooses (for example an effort branch) is unverified for plain sessions.
- **Pull requests.** **Create PR** in the diff view (full, draft, or GitHub's compose page); the session stays live after [doc quickstart, "Create a pull request"]. Built-in GitHub tools and `gh` work through the proxy, but the proxy serves only "a pinned set of GraphQL operations for pull-request workflows"; Projects v2 and other GraphQL-only APIs are out of reach [doc env, "GitHub proxy"]. Sub-issues and issue relationships are reached through REST in this repo's skills; whether those REST calls pass the proxy is unverified.
- **Repository scope.** API requests reach only repositories attached to the session; a running session can attach another repository [doc env; changelog 2.1.282, 2.1.283].
- **Non-GitHub.** Cloning and PRs need GitHub; `CCR_FORCE_BUNDLE=1` uploads a local bundle (under 100 MB) but can't push back to a non-GitHub remote [doc cloud, "Send local repositories without GitHub"; "Limitations"].
- **Auto-fix replies** on PR threads are posted under your GitHub account, labelled as Claude Code [doc cloud, "How Claude responds to PR activity"].

## 7. Starting it

- **Web / mobile / Desktop:** pick repo, branch, environment and a permission mode (Auto, Accept edits, Plan; no Manual or Bypass), then describe the task [doc quickstart, "Choose a permission mode"; doc mobile].
- **CLI, one line:** `claude --cloud "Fix the flaky test in auth.spec.ts"`; each call is its own parallel session; environment from `/remote-env` [doc cloud, "Run tasks in parallel"; doc env, "Select an environment from the CLI"].
- **What `claude --cloud "<task>"` needs** [doc cloud, "From terminal to cloud", "Send local repositories without GitHub", "Unable to get organization UUID"; doc quickstart, troubleshooting; doc env, "Select an environment from the CLI"; doc [headless](https://code.claude.com/docs/en/headless), "Basic usage"]:
  - **An interactive terminal.** Creating a session is an interactive command: "While the cloud container starts, the CLI shows a live checklist of setup steps … It queues messages you type during provisioning." `-p` doesn't help: "Claude Code rejects … `--cloud` with a task description [under `-p`], with an error naming the conflict." Only the follow-up form, `claude -p "msg" --cloud <session-id>`, is non-interactive. So an agent's non-interactive shell can't start a session with `--cloud` unless it gives the command a pseudo-terminal; the documented non-interactive way to start cloud work is a routine's API trigger (below).
  - **A claude.ai sign-in** (not an API key, not Bedrock/Vertex/Foundry), and the organization policy `allow_remote_sessions` on.
  - **A cloud environment.** One is created automatically if the account has none; "Could not create a cloud environment" or "No cloud environment available" means run `/web-setup` or add one on claude.ai. The CLI uses the `/remote-env` pick (saved as `remote.defaultEnvironmentId` in user settings), else the Anthropic-hosted environment, else the first non-bridge one.
  - **A pushed branch on a GitHub remote.** The VM clones "your current directory's GitHub remote at your current branch", so push first. With no git remote, **or on a GitHub repo the Claude GitHub App isn't installed on (even after `/web-setup`)**, the CLI instead bundles the local repository (all branches' history plus uncommitted changes to tracked files, under 100 MB) and uploads it; such a session can push back to GitHub only if the GitHub connection has push access. So neither the GitHub App nor `/web-setup` is strictly needed to start, but one of them is needed to push.
  - **One repository** per `--cloud` call.
- **How it reports the session.** For the follow-up form the docs show the output (`Sent to cloud session.`, `Session ID: …`, `View: https://claude.ai/code/…`) and a JSON form `{ok, session_id, url}` with `--output-format json`. For the create form they only say it "creates a new cloud session on claude.ai" and to open it there or in the mobile app; how the ID or URL is printed isn't documented, and `--output-format` works only with `-p`, which the create form rejects [doc cloud; bin].
- **[probe]** Two attempts were made from this research's agent shell (see the Exploration log). Probe 1, `claude --cloud "<prompt>" < /dev/null` with no terminal, exited with status 1; its output wasn't read. That fits the docs above: the create form is interactive. Probe 2 wrapped the command in `script` to give it a pseudo-terminal; the agent's local permission check refused to run it, twice, because it can't verify what a `script`-wrapped command runs from an isolated worktree. So probe 2 created no cloud session and there are still no first-hand answers about the VM. Getting them needs the maintainer, or an agent whose permissions allow it, to run the command in a real terminal.
- **Plan locally, execute in the cloud** is the documented pattern: commit a plan, push, then `claude --cloud "Execute the plan in docs/…"` [doc cloud, "Tips for cloud tasks"]. That matches this repo's handoff files.
- **API:** a routine with an API trigger has a per-routine URL and bearer token; `POST https://api.anthropic.com/v1/claude_code/routines/<id>/fire` with header `anthropic-beta: experimental-cc-routine-2026-04-01` and optional `{"text": "…"}` returns `claude_code_session_url`. The `text` arrives wrapped as untrusted data, so the routine's own prompt must say to act on it. Tokens are made on the web only [doc routines, "Add an API trigger"]. There's no documented API to start a plain cloud session.
- **From a local agent's tools:** the `RemoteTrigger` tool (behind `/schedule`) creates, updates, runs and lists routines [doc tools].
- **Requirements:** claude.ai sign-in, not an API key or third-party provider; organization policy `allow_remote_sessions` on [doc cloud, "Output and errors"].

## 8. Long work

- **Subagents** "work the same way they do locally", and repo `.claude/agents/` load [doc cloud, "Manage context"].
- **Agent teams** are off by default; set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` on the environment [doc cloud].
- **Idle expiry** kills background subagents and shell commands on reclaim [doc cloud, "Environment expired"]; a long orchestration that waits on a human answer risks that.
- **Projects** are Anthropic's answer to "run a whole effort": a coordinator conversation (Opus, low effort by default) starts threads (Opus, high effort), each on its own branch, opening PRs and auto-fixing them; an Overview pane groups threads as Ready for review, Waiting on you, Working, Landing, Idle, Resolved. Threads run in auto mode where the model supports it. A thread-count limit you ask for is "a preference rather than a cap"; the hard limit is 200 new threads a day [doc projects, "How a project is organized"; "What draws on your plan"]. In a project with several repositories, repo permission rules and hooks don't apply [doc projects, "What threads pick up from your repositories"].
- **Routines** run autonomously: "there is no permission-mode picker", commands and connector writes run "without stopping for approval" [doc routines, "Create a routine"].
- **Herdr and worktrees.** Herdr isn't pre-installed; plain `git worktree` is available with git. Whether this repo's orchestrating skills (which drive Herdr tabs and treehouse worktrees) could run inside one VM is untested; within one cloud session the parallelism is subagents, and across sessions it's projects or several `--cloud` calls.
- Whether a cloud session can itself run `claude --cloud` to start another cloud session is unverified.

## 9. Watching and answering

- **Where:** the session list at claude.ai/code, the mobile Code tab, the Desktop app; diff view with inline comments; share links (Private/Public on Pro and Max) [doc cloud, "Work with sessions"].
- **Answering:** type in the session; queued messages can be taken back; a question can be answered until the environment expires [doc cloud].
- **From a local agent, send:** `claude -p "message" --cloud <session-id-or-url>` "posts one message and exits"; `--output-format json` gives `{ok, session_id, url}`. It needs no local session state and works from any logged-in machine [doc cloud, "Send follow-ups from the CLI"].
- **From a local agent, list and message:** `ListAgents` shows cloud sessions only "while this session is connected to Remote Control"; `SendMessage` then goes "through Anthropic servers, straight to the cloud session". Without Remote Control a message still goes but carries no reply address [doc messaging, "See which sessions Claude can reach"; "Message sessions on other machines"].
- **From a local agent, read state:** no documented command prints a cloud session's transcript or status to the terminal. `/tasks` lists background sessions and teleports into one; `--teleport` copies the whole conversation locally [doc cloud]. For routines, `/schedule why did my nightly review do nothing` lists runs and reads a run's log (v2.1.227+) [doc routines, "Manage routines from the CLI"]. The `notify_when_idle` subscription works only for sessions on the same machine [doc messaging, "Get a notice when another session goes idle"]. Practical signal today: watch GitHub (the branch, the PR, the `Claude-Session` trailer).
- **Notifications:** projects send Desktop notifications when Claude posts, a thread errors or needs input (Desktop only) [doc projects, "See what needs you in Overview"]. Phone push is documented for Remote Control sessions and Dispatch [doc mobile, "Get push notifications"]; whether a plain cloud session pushes to the phone is unverified. A routine's green status only means no infrastructure error, not success [doc routines, "View and interact with runs"].

## 10. Moving it

- **Cloud to local:** `claude --teleport <id>` from a clean checkout of the same repository (not a fork), same claude.ai account, branch pushed; it fetches the branch and loads the full conversation. The local copy is separate: new work there doesn't appear in the cloud session [doc cloud, "From cloud to terminal"; "Teleport requirements"]. Inside a cloud session `/teleport` prints the exact command (v2.1.223+).
- **Local to cloud:** not from the CLI ("you can't push an existing terminal session to the cloud"). The Desktop app's **Continue in > Claude Code on the Web** pushes the branch, summarizes the conversation and starts a new cloud session; needs a clean tree, not for SSH sessions [doc cloud; doc desktop, "Continue in another surface"]. A cloud session can become a project with **Continue as a project** or **Move to project** [doc projects].
- **Anywhere else:** a routine run is an ordinary session you can open and continue [doc routines]. A project thread can run locally through Remote Control on request [doc projects, "Run a thread on your own computer"].

## 11. Cost and limits

- **Plans:** cloud sessions on Pro, Max, Team, and Enterprise premium or Chat + Claude Code seats; routines on all four; projects Pro and Max only (beta) [doc cloud; doc routines; doc projects; doc availability].
- **Usage:** cloud sessions "share rate limits with all other Claude and Claude Code usage within your account … There is no separate compute charge for the cloud VM" [doc cloud, "Limitations"]. Limits are the plan's five-hour and weekly windows [doc costs; doc projects, "A thread hit the usage limit"]. Project threads that hit a limit wait and continue on their own in the next window; routine-started threads stop instead [doc projects].
- **Routines:** a per-account daily cap on runs (not stated as a number; shown at claude.ai/code/routines), one-off runs exempt; minimum schedule interval one hour; GitHub-event hourly caps during the preview; overage only with usage credits on [doc routines, "Usage and limits"; "Add a schedule trigger"].
- **Usage credits** let work continue past the plan limit at API rates, turned on at claude.ai/settings/usage; `/usage-credits` opens it [doc costs, "Add usage credits to your subscription"].
- **The promo credit.** Anthropic announced cloud sessions leaving research preview with "a one-time credit to try them: $100 on Pro, $250 on Max", which "your cloud sessions spend first, before falling back onto your normal plan usage" [announce: [post 1](https://x.com/ClaudeDevs/status/2102871550974427462), [post 2](https://x.com/ClaudeDevs/status/2102940480736821610)]. Search excerpts also report claiming with `/claim-credit` or the banner at claude.ai/code, a claim deadline of 7 October (11:59 PM PT) and expiry on 4 November. Unverified: no docs or help-center page for these terms was found, and `claim-credit` doesn't appear in the CHANGELOG through 2.1.284.
- **Ultrareview** bills usage credits after three free runs [doc ultrareview].

## Open questions

Each needs a probe or a check the maintainer can do; the last column is the proposed experiment.

| Question | Why open | Proposed experiment |
|---|---|---|
| What does the VM actually report (`uname`, `nproc`, `free`, user, `check-tools`)? | Docs give approximate ceilings only; neither probe produced session output (section 7) | The maintainer runs one `claude --cloud "<read-only probe prompt>"` in a real terminal on the Mac against this repo on a throwaway branch (the prompt described in Exploration log row 11), results pushed to that branch |
| Does the create form print the session ID or URL, and how? | Documented only for `-p … --cloud <id>` | Same run: note the last lines the CLI prints |
| Did probe 1 create a session? | It exited 1 and its output wasn't read | Maintainer checks the session list at claude.ai/code for a 2026-09-29 session naming `probe/cloud-agents-1`, and archives it if present |
| Can a cloud session run a headless browser, and on which network level? | No browser named in docs | Same session: `which chromium google-chrome`, `ls ~/.cache/ms-playwright`; then, on an environment with **Full** network, a setup script that runs `npx playwright install --with-deps chromium` |
| Do WebFetch and WebSearch work under **Trusted**? | Not stated | Same session: WebFetch `https://example.com`, one WebSearch |
| Do skills enabled on the claude.ai account load, and does this repo's `CLAUDE.md` → `AGENTS.md` import load? | Documented, not seen | Same session: ask it to list skills and quote its instructions' first heading |
| How long is the idle expiry? | "A period of inactivity" | Leave a probe session idle and note when reopening provisions a fresh VM |
| Can a plain cloud session push to a branch named in the prompt (an effort branch), not only its own? | "current working branch" only | Start a session on `probe/…` and ask it to push to `probe/…-b`; record the proxy's error |
| Does a plain cloud session send phone push notifications? | Documented only for Remote Control and Dispatch | Ask a session to "notify me when done" and watch the phone |
| Can a cloud session start another cloud session (`claude --cloud` inside the VM)? | Not documented | Ask a probe session to run `claude --cloud --help` only (no launch) and report |
| Promo credit terms and remaining balance | Only announcement excerpts | Maintainer checks claude.ai/code and claude.ai/settings/usage |
| Does the GitHub proxy allow the REST sub-issue calls this repo's skills make? | Proxy scope documented only for PR GraphQL | In a probe session, `gh api repos/yahyabedirhan/skills/issues/45/sub_issues` (read-only) |

### Settled since the first pass

- **Can `claude --cloud "<task>"` start a session from a non-interactive agent shell?** Not as documented: the create form is interactive (live setup checklist, queued typed messages), and `-p` with a task description is rejected. Only `-p "msg" --cloud <session-id>` is non-interactive. A pseudo-terminal wrapper is the untested way round; the documented non-interactive way to start cloud work is a routine's API trigger [doc cloud; doc headless]. See section 7.
- **What does it need?** A claude.ai sign-in, `allow_remote_sessions`, a cloud environment (auto-created, else `/web-setup`), a pushed branch on a GitHub remote, and the GitHub App or a `/web-setup` connection with push access to push back; without the App the local repository is bundled instead of cloned [doc cloud; doc quickstart]. See section 7.

## Exploration log

All on 2026-09-29. "Mac" is the maintainer's Mac, in this ticket's worktree or the agent's scratch folder.

| # | Where | Command or action | What it changed |
|---|---|---|---|
| 1 | Mac | `gh issue view 69`, `gh issue view 45`; read the effort handoff, `harness-capabilities.md`, `herdr-vps.md` | Nothing |
| 2 | Mac (worktree) | `git merge --ff-only skills/cloud-agents` to base the ticket branch on the effort branch (the worktree had started at `main`) | Moved this worktree's branch forward; nothing remote |
| 3 | Mac (scratch) | `curl` of `https://code.claude.com/docs/llms.txt` and the `.md` form of the doc pages cited above; `gh api repos/anthropics/claude-code/contents/CHANGELOG.md` | Files in the agent's scratch folder only |
| 4 | Web | Web searches for the cloud-session credit; a fetch of the `@ClaudeDevs` post (HTTP 402) | Nothing |
| 5 | Mac | `claude --version` (2.1.284), `claude --help` | Nothing |
| 6 | Mac → GitHub | `git ls-remote origin 'refs/heads/probe/*' 'refs/heads/claude/*'` (empty), then `git switch -c probe/cloud-agents-1` at `8413cf7` (the already-public effort branch head) and `git push -u origin probe/cloud-agents-1` | Created the throwaway branch `probe/cloud-agents-1` locally and on GitHub, with no new commits |
| 7 | Mac → Anthropic | Probe 1: `claude --cloud "<read-only probe prompt>" < /dev/null`, run in the background. The prompt asked for the environment commands, tool list, network checks, skill list and one subagent listed under Open questions, and for the results to be committed as `probe/report-1.md` and pushed to `probe/cloud-agents-1`, with no code changes, installs or PR | Exited with status 1. Reading its captured output was refused by the local auto-mode classifier, so the cause wasn't inspected. `git ls-remote` afterwards showed `probe/cloud-agents-1` still at `8413cf7` and no `claude/*` branch, so no push from a cloud session happened. Whether a cloud session was created is unknown; none was steered or messaged afterwards. No second probe was started |
| 8 | Mac → GitHub | `git push origin --delete probe/cloud-agents-1`, `git switch` back to the ticket branch, `git branch -D probe/cloud-agents-1`, then `git ls-remote origin 'refs/heads/probe/*' 'refs/heads/claude/*'` | Removed the throwaway branch locally and on GitHub; the final `ls-remote` printed nothing |
| 9 | Mac (worktree) | Wrote this file; one commit | This file |
| 10 | Mac (follow-up, new worktree) | `git merge --ff-only skills/cloud-agents` (twice, as the effort branch moved on); `curl` of the `.md` form of the cloud, env, quickstart, cli-reference and headless pages; the CHANGELOG through `gh api` (no entry on `--cloud` and terminals or `-p`); `claude --help`; `gh api user/installations` and `gh api repos/yahyabedirhan/skills/installation` to learn whether the Claude GitHub App is installed (GitHub refused both for this token type, so unknown) | Worktree branch fast-forwarded; scratch files outside the repo |
| 11 | Mac → GitHub | `git ls-remote origin 'refs/heads/probe/*' 'refs/heads/claude/*'` (empty), `git switch -c probe/cloud-agents-2` at the effort branch head `d5c9206`, `git push -u origin probe/cloud-agents-2`. The read-only probe prompt (the environment commands, tool versions incl. browsers and Playwright, skill list and first instruction heading, WebFetch of `code.claude.com/docs/llms.txt` and one WebSearch, one sub-agent, `CLAUDE_CODE_REMOTE`, `claude --version`, a read-only `gh api …/issues/45/sub_issues`; results to `probe.md` pushed to the probe branch) went to an ignored `.scratch/` file | Created the throwaway branch locally and on GitHub, with no new commits |
| 12 | Mac | Probe 2: `script -q .scratch/probe2.log claude --cloud "<prompt>"`, first with the prompt substituted from the file, then with it inline | Refused both times by the agent's local permission check. Nothing ran and no cloud session was created; per the effort's rules the probe stopped there instead of working around the check |
| 13 | Mac → GitHub | `git push origin --delete probe/cloud-agents-2`, `git switch` back, `git branch -D probe/cloud-agents-2`, then `git ls-remote origin 'refs/heads/probe/*' 'refs/heads/claude/*'` | Removed the throwaway branch locally and on GitHub; the final `ls-remote` printed nothing |
