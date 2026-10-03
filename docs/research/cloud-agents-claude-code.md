# Claude Code in the cloud: environment, capabilities and limits

Facts for [Research: Claude Code's cloud agents - environment, capabilities and limits (#69)](https://github.com/yahyabedirhan/skills/issues/69), under [Spec: research cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45). Researched 2026-09-29 against the docs at `code.claude.com` on that date and Claude Code 2.1.284 on the Mac.

This file maps what Anthropic offers to run Claude Code off the Mac:

- cloud sessions (Claude Code on the web)
- how to start them from the CLI
- how to teleport them back
- routines
- projects
- the smaller pieces around them

It builds on two files and doesn't repeat them:

- [What each harness can and can't do](harness-capabilities.md): how Claude Code loads instructions, permissions and hooks locally.
- [Herdr across the Mac and the VPS](herdr-vps.md): the VPS path.

Evidence tags:

- **[doc]** Claude Code's official documentation, cited by page and section. Pages, all under `https://code.claude.com/docs/en/`: [claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web) ("cloud"), [cloud-environments](https://code.claude.com/docs/en/cloud-environments) ("env"), [web-quickstart](https://code.claude.com/docs/en/web-quickstart) ("quickstart"), [routines](https://code.claude.com/docs/en/routines), [claude-projects](https://code.claude.com/docs/en/claude-projects) ("projects"), [remote-control](https://code.claude.com/docs/en/remote-control), [cross-session-messaging](https://code.claude.com/docs/en/cross-session-messaging) ("messaging"), [mobile](https://code.claude.com/docs/en/mobile), [desktop](https://code.claude.com/docs/en/desktop), [skills](https://code.claude.com/docs/en/skills), [settings](https://code.claude.com/docs/en/settings), [tools-reference](https://code.claude.com/docs/en/tools-reference) ("tools"), [ultrareview](https://code.claude.com/docs/en/ultrareview), [costs](https://code.claude.com/docs/en/costs), [feature-availability](https://code.claude.com/docs/en/feature-availability) ("availability"), [self-hosted-environments](https://code.claude.com/docs/en/self-hosted-environments) ("self-hosted").
- **[changelog]** [`anthropics/claude-code` CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md), read at 2.1.284.
- **[bin]** `claude --help` of the installed 2.1.284, read-only.
- **[announce]** Anthropic's own announcement channel (the `@ClaudeDevs` account on X). This research saw it through search-result excerpts only, because the posts returned HTTP 402 to a fetch. Weaker than [doc].
- **[probe]** a hands-on attempt made for this research. See the Exploration log. From issue #78 on, it also covers two more things:
  - the maintainer's own run of `claude --cloud "say hi"` on the Mac (2026-09-29). Nobody recorded the Mac's version for this run. Row 5 had 2.1.284.
  - what the cloud session it created (Claude Code 2.1.285), or that session's sub-agents, saw from inside.
- **Unverified** marks a claim with no primary source.

On 2026-09-29 (issue #78), a cloud session re-read sections 1 to 11 and the Short answer line by line. It compared them with the web-quickstart, claude-code-on-the-web, routines and ultrareview pages. Then it corrected them against that session's first-hand probes.

**See also**, from issue #78:

- [Inside a Claude Code cloud session: first-hand probes](cloud-agents-session-probe.md): the VM, browser, network, GitHub proxy, sub-agent tools and hooks, tested from inside one session. It answers most of the Open questions below.
- [Running the effort workflow in a Claude Code cloud session](cloud-agents-session-workflow.md): how skills and instructions can reach a cloud session, and what the effort workflow needs there.
- [Managed Agents on the Claude Platform vs Claude Code cloud sessions](cloud-agents-managed-agents.md): the API product with a similar name, and why it doesn't replace this one here.

## Short answer

| | Cloud session (web, mobile, Desktop "Cloud", `claude --cloud`) | Routine | Project (threads) | Remote Control (for contrast) |
|---|---|---|---|---|
| **Runs on** | A fresh Anthropic VM per session: Ubuntu 24.04, x86_64, about 4 vCPU / 16 GB / 30 GB [doc env] | A cloud session per run [doc routines] | A cloud session per thread, or a local session on request [doc projects] | Your own machine [doc remote-control] |
| **Lifetime** | Keeps running with the laptop closed. Anthropic reclaims the VM after an idle period that the docs don't state. A reopen restores the conversation but not background work [doc cloud, "Environment expired"] | One session per trigger | Threads resolve on their own after a week idle [doc projects] | As long as the machine and `claude` run |
| **Tools** | Python, Node 20-22, Ruby, PHP, Java, Go, Rust, C/C++, Docker, Postgres, Redis, git, gh, jq, tmux. More through a root setup script, cached as a snapshot [doc env]. `gh` was missing in the probe VM [probe] | Same, from the routine's environment | Same, from the project's environment | Whatever is installed locally |
| **Web** | Allowlist ("Trusted") by default. None / Full / Custom per environment. GitHub, connectors and the Anthropic API are always reachable [doc env] | Same | Same | Your network |
| **Browser** | The docs name none beyond `chromedriver`. First-hand, Playwright's Chromium is pre-installed and runs headless on Trusted, once the proxy's CA is trusted. Only allowlisted hosts load [probe]. Claude in Chrome is local only | Same | Same | Local Chrome |
| **What loads** | Repo `CLAUDE.md`, `.claude/` skills, agents, commands, rules. Repo hooks, permissions and `.mcp.json` only with one repo. claude.ai account skills. **Not** the laptop's `~/.claude/*`, user MCP, or any plugins [doc env, "What carries over"]. The VM's own `~/.claude/skills` does load, even mid-session [probe] | Same, plus the routine's connectors | Same, plus project instructions, memory and plugins from project settings | Everything local |
| **GitHub** | Claude GitHub App or `/web-setup` (sends your `gh` token). A proxy keeps the token out of the VM. Push to the checked-out branch: the session's `claude/<slug>`, or a new branch that the session names itself (an existing branch it didn't create: untested). GraphQL blocked, REST only for the attached repo [probe]. Create PR button (full, draft, or GitHub's compose page) [doc cloud; doc env; doc quickstart] | Clones the default branch unless the prompt says otherwise. Pushes `claude/…` branches, and other branches only after checks [doc routines, "Repositories and branch permissions"] | Own branch per thread, opens PRs, auto-fix on [doc projects] | Your git |
| **Start from** | Web (also a pre-filled `claude.ai/code?prompt=…&repositories=…` link), mobile, Desktop, `claude --cloud "task"`. That command printed the title, URL and a teleport command and exited [probe]. `-p` with a task is rejected [doc quickstart, "Pre-fill sessions"; doc cloud; doc headless] | Schedule (recurring or one-off), API `POST …/fire`, GitHub event (PR or release), `/schedule`, Run now [doc routines] | Web, Desktop, mobile [doc projects] | `claude remote-control` |
| **Permission modes** | Auto, Accept edits, Plan. No Manual or Bypass. You can switch while it runs [doc quickstart, "Choose a permission mode"; doc cloud, "Permission modes in cloud sessions"] | None: no picker. It runs without approval, except some artifact actions [doc routines, "Create a routine"] | Auto mode where the model supports it [doc projects] | Manual, Accept edits or Plan from claude.ai and mobile [doc quickstart, "Compare ways to run Claude Code"] |
| **Long work** | Subagents yes. Agent teams behind an env var [doc cloud] | Autonomous, no permission picker | Built for it: a coordinator plus parallel threads | Local limits |
| **Watch / answer** | claude.ai/code, mobile, Desktop. `/tasks`. `claude -p "msg" --cloud <id>` queues a message. `ListAgents`/`SendMessage` reach it only from a Remote Control session [doc cloud; doc messaging]. Inside a cloud session, the Remote MCP `list_sessions`/`get_session` read every session's state [probe] | Run list on claude.ai. `/schedule` reads run logs [doc routines] | Overview pane. Desktop notifications [doc projects] | claude.ai/code, mobile, push |
| **Move it** | `claude --teleport <id>` pulls it to a local checkout (one-way copy). Desktop "Continue in" sends local to cloud [doc cloud; doc desktop] | Open run as a session | "Run a thread on your computer" [doc projects] | A fork from the Claude app runs on your computer [changelog 2.1.273] |
| **Cost** | Plan usage, no separate VM charge [doc cloud, "Limitations"]. A one-time promo credit of $100 Pro / $250 Max is spent first [announce]. The probe session drew on a promotional rate-limit pool [probe] | Plan usage plus a daily run cap [doc routines] | Plan usage, "uses them faster". 200 new threads a day [doc projects] | Plan usage |
| **Plans** | Pro, Max, Team. Enterprise premium seats [doc cloud] | Pro, Max, Team, Enterprise. Research preview [doc routines] | Pro and Max, public beta, gradual rollout [doc projects] | Pro, Max. Team/Enterprise when an admin enables it [doc availability] |

Cloud sessions need a claude.ai sign-in. They aren't available with a Console API key or through Bedrock, Vertex or Foundry [doc cloud, "Output and errors"; doc availability].

## 1. What there is

- **Cloud session.** "A Claude Code session that runs on cloud infrastructure instead of on your machine". It runs on Anthropic's infrastructure by default, or on an organization's self-hosted environment. "The session keeps running after you close your laptop" [doc cloud, intro]. You can start one from:
  - the browser (claude.ai/code, "Claude Code on the web")
  - the mobile app's Code tab
  - the Desktop app with **Cloud** selected
  - the terminal with `claude --cloud`
  - a routine
- **`claude --cloud`.** Creates a cloud session from the terminal. `--remote` is the older, deprecated spelling [doc cloud, "From terminal to cloud"]. The 2.1.284 help reads `--cloud [description|session_id|url]  Create a cloud session with the given description, or attach to an existing one by session ID or claude.ai/code URL` [bin].
  - The docs narrow "attach". `--cloud <session-id>` without `-p` fails with `Attaching to an existing cloud session is not enabled for your account.` Only `-p "msg" --cloud <id>` works, as a one-message send [doc cloud, "Output and errors"].
  - Bare `claude --cloud` printed `Error: --cloud requires a description.` and a usage line [probe].
- **Pre-filled links.** `https://claude.ai/code?prompt=…&repositories=owner/repo&environment=…` opens the new-session form filled in. `prompt_url` fetches a long prompt from a CORS-enabled URL. The link fills the form, but it doesn't submit it [doc quickstart, "Pre-fill sessions"].
- **Teleport.** `claude --teleport [<id>]`, `/teleport`, or `t` in `/tasks` pulls a cloud session into a local checkout [doc cloud, "From cloud to terminal"].
- **Routines.** "A saved Claude Code configuration: a prompt, one or more repositories, and a set of connectors". A schedule, an API call or a GitHub event runs it on cloud infrastructure. Research preview [doc routines].
- **Projects.** One coordinating conversation that starts parallel cloud "threads" and tracks them. Public beta on Pro and Max, with a gradual rollout. Not on Team or Enterprise yet [doc projects].
- **Auto-fix.** A cloud session that watches a pull request and pushes fixes for CI failures and review comments. `/autofix-pr` starts one from the terminal. It needs the Claude GitHub App [doc cloud, "Auto-fix pull requests"].
- **Ultrareview.** `/code-review ultra` (alias `/ultrareview` where available) runs a fleet of reviewer agents as a cloud session. It reports only findings that were independently verified. `claude ultrareview` is the non-interactive form. Research preview. Pro and Max get three one-time free runs, and Team or Enterprise get none. After that a run typically costs $5-25 in usage credits [doc ultrareview, intro; "Pricing and free runs"]. See section 9.
- **Around them, but not cloud sessions** [doc remote-control, "Remote Control vs cloud sessions"; doc self-hosted, "Availability and limitations"]:
  - Remote Control: drive a session on your own machine from claude.ai or the phone.
  - Dispatch: message the Desktop app from the phone.
  - channels
  - Desktop scheduled tasks and `/loop` (local)
  - Claude in Slack / Claude Tag: a Slack front end on the same cloud infrastructure.
  - GitHub Actions: Claude Code in CI.
  - self-hosted environments: cloud sessions on your own runners. Team and Enterprise only, public beta.

  A self-hosted runner on the VPS would be the cleanest way to give cloud sessions the VPS's tools. But it isn't available on the maintainer's individual plan.

## 2. Environment

- **Machine.** "Each session gets a fresh virtual machine (VM) running Ubuntu 24.04 on x86_64 … with your repository cloned and common toolchains pre-installed" [doc env, "What's available in cloud sessions"].
- **Resources.** "Approximate resource ceilings that may change over time: 4 vCPUs, 16 GB of RAM, 30 GB of disk". The VM "may stop tasks that need significantly more memory" [doc env, "Resource limits"]. The probe VM was a Firecracker microVM. It had 4 vCPU, 15.7 GiB of RAM, no swap, and 30G writable, although `df` shows 252G [probe; [session-probe §10](cloud-agents-session-probe.md#10-disk)].
- **User.** Setup scripts "run as root on Ubuntu 24.04, so `apt install` … work[s]" [doc env, "Setup scripts"]. Claude's own commands run as root too [probe].
- **No shell for you.** "You don't get a shell into the session VM. Claude runs every command for you" [doc env, "Run tests, start services, and add packages"].
- **Lifetime.** Sessions persist across devices and keep running with the laptop closed.
  - "Cloud sessions stop after a period of inactivity and the session's VM is reclaimed". A wait on a connector approval counts as inactive.
  - A reopen will "provision a fresh VM with your conversation history restored. Background work that was still running … such as subagents and shell commands, isn't restored" [doc cloud, "Environment expired"].
  - The docs don't state the idle period. You can answer a question from Claude "up to environment expiry" [doc cloud, "From terminal to cloud"].
  - A closed tab doesn't stop a session. It runs until the current task is done, then idles [doc quickstart, "Session keeps running after closing the tab"].
  - A reopened session resumes in the permission mode it was in [doc cloud, "Permission modes in cloud sessions"].
- **Start failures.** `Session creation failed`, or a stall at provisioning, means that Anthropic could not allocate a VM. Check status.claude.com and retry after a minute [doc cloud, "Session creation failed"]. A setup script that exits non-zero blocks the session. A script that runs past about five minutes can hang new sessions [doc quickstart, "Setup script failed"; "New sessions hang or time out during setup"].
- **Environments.** The same environments apply from every surface (web, terminal, routines, mobile, Desktop, Claude Tag).
  - Pro and Max onboarding creates one named **Default** with Trusted network. Team and Enterprise onboarding shows a form unless Quick web setup is on [doc cloud, "Cloud environments"; doc quickstart, "Set up your Default environment"].
  - On the web you pick the environment per session, or preselect it with `environment=` in a pre-filled link. A routine names one in its form [doc quickstart, "Pre-fill sessions"; doc routines, "Select an environment"].
- **What persists.** The conversation (on claude.ai), and whatever the session pushed to GitHub. Files in the VM don't survive a reclaimed VM (inferred from "fresh VM").
  - Environment cache: when the setup script finishes in about five minutes, "Anthropic snapshots the filesystem and reuses that snapshot" for later sessions.
  - Anthropic rebuilds the snapshot when the script or allowed hosts change, or after about seven days.
  - The cache holds files, not running processes [doc env, "Environment caching"].
- **Time limits** [doc env, "Time limits"]:
  - The Bash tool's defaults apply (2 min, up to 10). You can raise them with `BASH_DEFAULT_TIMEOUT_MS` / `BASH_MAX_TIMEOUT_MS` on the environment.
  - SessionStart hooks: 600 s.
  - Setup script: about 5 min to be cached.
- **Context.** Cloud sessions set `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` themselves. So they compact earlier than a local session, and that value overrides one set on the environment. To move compaction, set `CLAUDE_CODE_AUTO_COMPACT_WINDOW` or run `/autocompact <tokens>`. `/compact` and `/context` work. `/clear` doesn't, so start a new session instead [doc cloud, "Manage context"]. The probe VM had the variable at 80 [probe].
- **Session identity.** `CLAUDE_CODE_REMOTE=true` inside the VM. `CLAUDE_CODE_REMOTE_SESSION_ID` holds the session ID. Commits get a `Claude-Session: <url>` trailer, and PR bodies get a session link, unless `attribution.sessionUrl` is `false` [doc env, "Link output back to the session"; "Install dependencies with a SessionStart hook"].

## 3. Tools and commands

- **Pre-installed** (Anthropic-hosted) [doc env, "Installed tools"]:
  - Python 3 with pip, poetry, uv, black, mypy, pytest, ruff;
  - Node 20/21/22 (22 on `PATH`) with npm, yarn, pnpm, bun, eslint, prettier, chromedriver;
  - Ruby 3.1-3.3; PHP 8.3; OpenJDK 21 with Maven and Gradle; Go; Rust;
  - GCC, Clang, cmake, ninja, conan;
  - docker, dockerd, docker compose;
  - PostgreSQL 16 and Redis 7.0 (not started);
  - git, gh, jq, yq, ripgrep, tmux, vim, nano.

  A `check-tools` command prints versions. In the probe VM, `check-tools` ran, but `gh` was not installed, despite the list [probe].
- **Not there:** anything else, for example .NET, Herdr, treehouse, codex, opencode. Installs are allowed: "Install them with a setup script", or ask Claude mid-session. But mid-session installs "don't carry over to other sessions" [doc env, "Add packages"]. A replacement of the base image "isn't supported yet" [doc env, "Limitations in cloud sessions"].
- **Setup script vs SessionStart hook** [doc env, "Setup scripts vs. SessionStart hooks"]:
  - The script is per environment and set on claude.ai. It runs before Claude starts, and Anthropic caches it.
  - A SessionStart hook is committed in the repo. It runs on every start and resume, local too. So gate it on `CLAUDE_CODE_REMOTE`.
- **Bun** "has known proxy compatibility issues" behind the security proxy [doc env, "Installed tools"].
- **Slash commands** [doc cloud, "Manage context"]:
  - Built-ins with text output work. Terminal-only ones such as `/plugin` and `/resume` don't.
  - `/model`, `/effort`, `/color` and `/rename` take the value as an argument (`/model sonnet`, v2.1.205+ in the session).
  - `/fast` toggles fast mode (v2.1.271+).
  - `/config` on the web opens the settings page and ignores `key=value`. To change a cloud setting, use an environment variable. With one repository, you can also use the committed `.claude/settings.json`.
  - A cloud session refuses `/schedule` [doc routines, "Troubleshooting"].
- **Tools that differ:** `SendUserFile` works in cloud sessions. The LSP tool stays inactive, because plugin language servers don't start. `ListAgents`/`SendMessage` exist [doc tools].

## 4. Web and browser

- **Network levels** per environment [doc env, "Access levels"]:
  - **None**
  - **Trusted** (the default): package registries, GitHub, cloud SDKs and a published allowlist
  - **Full**: any domain
  - **Custom**: your list, optionally plus the defaults

  A blocked request gets `403` with `x-deny-reason: host_not_allowed` [doc routines, "Environments and network access"]. First-hand, the 403 carried no `x-deny-reason` header. The body names the host (`request blocked: no rule or allowlist entry allows host "…"`) [probe; [session-probe §3](cloud-agents-session-probe.md#3-network-and-the-proxy)].
- **Always reachable, whatever the level** [doc env, "Access levels"]:
  - GitHub, through its own proxy
  - MCP connectors (their traffic goes through Anthropic's servers)
  - hosts named on API credentials
  - the Anthropic API
- **Even at None**, Claude Code still talks to the Anthropic API, "which may allow data to exit the VM". On Pro and Max, you can add API keys to an environment as API credentials. They stay outside the sandbox, and the proxy attaches them to matching requests. Team and Enterprise don't have them yet [doc cloud, "Security and isolation"].
- **Security proxy.** All outbound traffic goes through an HTTP/HTTPS proxy. It does rate limits, content filters and a DNS-level audit trail [doc env, "Security proxy"].
- **Trusted list** includes `code.claude.com`, `docs.claude.com`, `github.com`, the npm, PyPI, crates, Go, Maven registries, Docker Hub, `ghcr.io`, `*.googleapis.com`, `*.amazonaws.com`, `developer.apple.com`, `swift.org` and more. It doesn't include general sites [doc env, "Default allowed domains"]. So research against arbitrary web pages needs **Full** or **Custom** on the environment.
- **WebSearch** is a server-side tool on the Claude API [doc tools, WebSearch notes]. First-hand, it works in a cloud session on Trusted. **WebFetch** runs inside the VM's `claude` process, under the environment's allowlist. Allowlisted hosts fetch, and others return `EGRESS_BLOCKED` [probe; [session-probe §2](cloud-agents-session-probe.md#2-webfetch-and-websearch)].
- **Browser.** The docs list `chromedriver` with Node but name no Chrome or Chromium binary. Claude in Chrome drives the local Chrome, and the docs don't list it for cloud sessions. First-hand [probe; [session-probe §1](cloud-agents-session-probe.md#1-headless-browser)]:
  - Playwright's Chromium is pre-installed in `/opt/pw-browsers` (`PLAYWRIGHT_BROWSERS_PATH`). The harness prompt says not to run `playwright install`.
  - It launches headless in under a second on Trusted.
  - But every HTTPS page fails with `ERR_CERT_AUTHORITY_INVALID` until the browser trusts the proxy's CA. One way: `--ignore-certificate-errors-spki-list=<proxy CA SPKI hash>`.
  - Then allowlisted hosts load, and others fail at the tunnel.
  - Allowlisted hosts need no setup script and no wider network.

## 5. What loads

From the "What carries over from your setup" table [doc env] and [doc settings, "Settings in cloud sessions"]:

| Item | Loads? |
|---|---|
| Repo `CLAUDE.md`, `.claude/rules/` | Yes (part of the clone). `AGENTS.md` follows the local rule in [harness-capabilities.md](harness-capabilities.md) 1.1. This repo's `CLAUDE.md` imports it |
| Repo `.claude/skills/`, `.claude/agents/`, `.claude/commands/` | Yes |
| Repo `.claude/settings.json` hooks, permission rules, `env` | Only in a session with **one** repository |
| Repo `.mcp.json` | Only with one repository |
| Plugins in repo or user settings | **No**. Projects can add plugins in project settings |
| `~/.claude/CLAUDE.md`, `~/.claude/skills/`, agents, commands, user hooks, user settings | **No** ("Live on your machine"): this means the laptop's files. The VM has its own `~/.claude/`. Skills placed in its `~/.claude/skills/` load, even mid-session [probe; [session-workflow §1](cloud-agents-session-workflow.md#1-the-layers-in-a-cloud-session)] |
| User or local MCP servers (`claude mcp add`) | **No**. Use `--scope project` and commit `.mcp.json`, or use a claude.ai connector |
| Skills enabled on the claude.ai account | **Yes**: "Cloud sessions automatically load skills you enable on claude.ai" [doc skills, "Use skills in Cowork and cloud sessions"] |
| claude.ai connectors | Routines and projects: yes, chosen per routine or project. A new routine includes **all** connected connectors by default. Claude can use every tool of an included connector, writes too, without a question. Local `claude mcp add` servers never appear there. So add them at claude.ai/customize/connectors, or, with one repository, commit a `.mcp.json` [doc routines, "Review connectors"; "Connectors"]. Plain cloud sessions: the docs don't state how connectors are chosen. They only mention a session that waits to approve "an MCP connector tool call" [doc cloud, "Environment expired"]. The Desktop "+ Connectors" button isn't offered for cloud sessions [doc desktop]. Unverified. The probe session, started with `claude --cloud`, had the account's Gmail and Claude Docs connectors. It also had the GitHub MCP tools and a "Claude Code Remote" server [probe] |
| Server-managed settings | Yes. Device MDM or managed files: no |
| Transport env vars (`NODE_EXTRA_CA_CERTS`, mTLS) | Ignored |

**What this means here.** This repo keeps its skills under `skills/`, not `.claude/skills/`. So a cloud session on it gets none of the maintainer's skills from the clone. It gets only what's enabled on the claude.ai account. The global `~/.claude/CLAUDE.md` rules (privacy line, notification command, Herdr rules) don't reach a cloud session at all.

There are two documented ways to carry them:

- Enable the skills on the claude.ai account.
- Commit a `.claude/skills/` (and project instructions) in the target repo. Routines say the same: a run "uses skills committed to the cloned repository" [doc routines, "Create a routine"].

In the probe session, the account's enabled skills were synced into `~/.claude/skills/synced/`. This repo's skills, installed mid-session with `npx skills add … -g`, loaded at once, but they vanish with the VM [probe]. So a third way works: an environment setup script, or a SessionStart hook, that installs the skills into the VM's home ([session-workflow §2](cloud-agents-session-workflow.md#2-carrying-the-skills-and-global-instructions-into-cloud-sessions)). Untested: whether a `~/.claude/CLAUDE.md` that a setup script writes loads.

## 6. GitHub

- **Granting access.** There are two ways [doc cloud, "GitHub authentication options"; doc quickstart, "Connect from your terminal"]:
  - the **Claude GitHub App**: any public repo, plus private repos where it's installed. Auto-fix, GitHub triggers and project threads need it.
  - **`/web-setup`**: it sends the local `gh auth token` to Anthropic, which stores it encrypted. Sessions then reach any repo that the token can reach.

  More facts:
  - The browser connection alone clones any public repository. It works in a private one only where the App is installed [doc quickstart, "Sign in with GitHub"].
  - `/web-setup` replaces a browser connection. It creates a Trusted environment if there is none. It warns when the token lacks the `workflow` scope, because GitHub can then refuse pushes that touch Actions workflow files. The fix is `gh auth refresh -s workflow` [doc quickstart, "Run /web-setup"; troubleshooting].
  - A disconnect of GitHub at claude.ai/customize/connectors deletes the stored credential, whichever way it came. To revoke the token itself, use GitHub [doc quickstart, "Remove the /web-setup token"].
  - `/web-setup` doesn't install the App. So it enables neither GitHub triggers nor auto-fix [doc routines, "Add a GitHub trigger"].
  - On Team and Enterprise, `/web-setup` stays hidden until an Owner turns on Quick web setup [doc cloud, "GitHub authentication options"].
- **Token handling.** In Anthropic-hosted environments, credentials "never enter a session's VM". A GitHub proxy swaps a scoped credential for the real token. `GH_TOKEN`/`GITHUB_TOKEN` read as the placeholder `proxy-injected` unless you set your own [doc env, "GitHub proxy"; "Work with GitHub issues and pull requests"].
- **Branch.**
  - Web/mobile: pick a repository. Each one shows a branch selector (default branch unless changed). You can add several repositories to one session. "Each task gets its own session and its own branch" [doc quickstart, "Select a repository and branch"].
  - `claude --cloud` clones "your current directory's GitHub remote at your current branch, not your local checkout, so push first" [doc cloud].
  - The docs don't name the session branch for plain sessions. In the probe, the VM made a shallow clone of the Mac's current branch `skills/cloud-agents` (only that branch, and `CLAUDE_CODE_BASE_REF` held its name). Then the harness created and checked out `claude/<slug>` from it [probe].
  - It was a clone, not an upload: a bundle carries the history of all branches [doc cloud, "Send local repositories without GitHub"]. So the Claude GitHub App is very likely installed on this repo (inference).
  - Routines start from the default branch "unless your prompt specifies otherwise". They push `claude/`-prefixed branches, which GitHub always accepts. A push to another branch that the prompt names gets a check first. It is refused if the branch is protected, has someone else's open PR, or carries commits by someone other than you [doc routines, "Repositories and branch permissions"].
  - Project threads work on a new branch from the default branch [doc projects].
- **Pushing.** "`git push` works only against the session's current working branch" [doc env, "GitHub proxy"]. First-hand, that means the checked-out branch, whatever its name.
  - The session pushed its `claude/<slug>` branch. Then it created a new branch named in the prompt (`skills/…`), checked it out, and pushed it and further commits to it. `get_session` then tracked that branch as the session's branch [probe; [session-probe §4](cloud-agents-session-probe.md#4-github-proxy)].
  - The harness prompt tells the model not to push to another branch "without explicit permission". This is an instruction, not a proxy rule [probe].
  - Untested: a push to an existing branch that the session didn't create (for example an effort branch pushed from the Mac).
- **Pull requests.**
  - **Create PR** at the top of the diff view opens a full PR, a draft, or GitHub's compose page, with a generated title and description. The session stays live after that, for CI output or reviewer comments that you paste in [doc quickstart, "Create a pull request"; "Keep iterating after the PR"].
  - In the probe, the session also opened a PR itself with the GitHub MCP tool `create_pull_request` [probe].
  - Built-in GitHub tools and `gh` work through the proxy. But the proxy serves only "a pinned set of GraphQL operations for pull-request workflows". Projects v2 and other GraphQL-only APIs are out of reach [doc env, "GitHub proxy"].
  - First-hand, GraphQL is blocked entirely. Every query, PR-related or not, got `403`. The message pointed to the REST API, and to special REST routes under `/repos/{owner}/{repo}/pulls/{n}/ccr/` for review threads, comment resolution, auto-merge and draft state.
  - REST works for the attached repository. That includes sub-issues (`200`) and `/user` (`200`, so the proxy injects a real credential) [probe; [session-probe §4](cloud-agents-session-probe.md#4-github-proxy)].
  - `gh` itself was missing from the VM. So a `gh` command that uses GraphQL would fail even after an install.
- **Repository scope.** API requests reach only repositories attached to the session. A running session can attach another repository [doc env; changelog 2.1.282, 2.1.283]. First-hand, the proxy refused REST calls to any other repository, even a public one ("GitHub access to this repository is not enabled for this session. Use add_repo …"). Plain `git` reads of other public repositories still work [probe].
- **Non-GitHub.** Clones and PRs need GitHub. `CCR_FORCE_BUNDLE=1` uploads a local bundle (under 100 MB), but the session can't push back to a non-GitHub remote [doc cloud, "Send local repositories without GitHub"; "Limitations"].
- **Auto-fix replies** on PR threads appear under your GitHub account, labelled as Claude Code [doc cloud, "How Claude responds to PR activity"]. Auto-fix is a per-PR toggle [doc cloud, "Auto-fix pull requests"]. Three ways to turn it on:
  - the CI status bar's **Auto-fix** in a cloud session
  - `/autofix-pr` on the PR's branch in the terminal
  - ask Claude in any session, with the PR URL

  More facts:
  - It pushes clear fixes. It asks first about comments that are unclear or about architecture.
  - It can't see merge conflicts from a moving base, because GitHub sends no event. So ask for a rebase.
  - Its replies can fire `issue_comment` automation.
- **Identity.** Routine commits, PRs and connector actions appear as you [doc routines, "Create a routine"]. The probe session's commits had the author `Claude <noreply@anthropic.com>`, and a helper signed them with SSH [probe].
- **Lapsed connection.** Suppose GitHub is disconnected or expired when a routine is due. Then the routine skips runs for up to 72 hours. After that it turns off until you reconnect and turn it on again [doc routines, "Repositories and branch permissions"].

## 7. Starting it

- **Web / mobile / Desktop:** pick repo, branch, environment and a permission mode, then describe the task [doc quickstart, "Choose a permission mode"; doc mobile]. The modes:
  - **Auto:** a classifier reviews Claude's actions, so Claude doesn't ask you. It is offered only when the organization allows auto mode and the model supports it.
  - **Accept edits:** Claude edits and pushes a branch without a stop for approval.
  - **Plan:** Claude proposes an approach and waits for approval before it edits files.
  - No Manual or Bypass. You can change the mode from the dropdown while the session runs. The mode survives an expired VM [doc quickstart, "Choose a permission mode"; doc cloud, "Permission modes in cloud sessions"]. A session started with `claude --cloud` gets no mode choice on the command line (the docs name none. This is an inference).
- **Pre-filled link:** `claude.ai/code?prompt=…&repositories=owner/repo&environment=…` (aliases `q`, `repo`, and `prompt_url` for long prompts) opens the form filled in. One use is a button in an issue tracker. You still submit it [doc quickstart, "Pre-fill sessions"].
- **CLI, one line:** `claude --cloud "Fix the flaky test in auth.spec.ts"`. Each call is its own parallel session. The environment comes from `/remote-env` [doc cloud, "Run tasks in parallel"; doc env, "Select an environment from the CLI"].
- **What `claude --cloud "<task>"` needs** [doc cloud, "From terminal to cloud", "Send local repositories without GitHub", "Unable to get organization UUID"; doc quickstart, troubleshooting; doc env, "Select an environment from the CLI"; doc [headless](https://code.claude.com/docs/en/headless), "Basic usage"]:
  - **A terminal? Probably not a live one.** The page still says: "While the cloud container starts, the CLI shows a live checklist of setup steps … It queues messages you type during provisioning" [doc cloud, "From terminal to cloud"]. First-hand, that is not what happened. The maintainer ran `claude --cloud "say hi"` in a terminal on the Mac. It printed three lines and exited at once, with no checklist [probe]:

    ```
    Created cloud session: Say hi
    View: https://claude.ai/code/session_<id>?from=cli&m=0
    Resume with: claude --teleport session_<id>
    ```

    So the create form starts the session and returns at once. It names the session (the title comes from the task), and gives its URL and the teleport command.
    - The docs' checklist description is out of date for this build, or it applies only in some cases (Unverified which).
    - What still holds from the docs: `-p` doesn't help. "Claude Code rejects … `--cloud` with a task description [under `-p`], with an error naming the conflict" [doc headless, "Basic usage"].
    - Untested: whether the create form runs without a TTY (from an agent's shell). Probe 1 (`< /dev/null`, no terminal) exited 1 with its output unread. That was before anyone saw this run. It created no session (`list_sessions` shows none [probe]).
    - The documented non-interactive way to start cloud work is still a routine's API trigger (below).
  - **A claude.ai sign-in** (not an API key, not Bedrock/Vertex/Foundry), and the organization policy `allow_remote_sessions` on.
  - **A cloud environment.** The CLI creates one if the account has none. "Could not create a cloud environment" or "No cloud environment available" means: run `/web-setup` or add one on claude.ai. The CLI uses the `/remote-env` pick (saved as `remote.defaultEnvironmentId` in user settings). Else it uses the Anthropic-hosted environment, else the first non-bridge one.
  - **A pushed branch on a GitHub remote.** The VM clones "your current directory's GitHub remote at your current branch", so push first.
    - In two cases the CLI bundles and uploads the local repository instead. One: there is no git remote. Two: **the GitHub repo doesn't have the Claude GitHub App installed (even after `/web-setup`)**. The bundle holds the history of all branches plus uncommitted changes to tracked files, under 100 MB.
    - Such a session can push back to GitHub only if the GitHub connection has push access.
    - So a start needs neither the GitHub App nor `/web-setup`. But a push needs one of them.
  - **One repository** per `--cloud` call. The web form allows several [doc cloud, "From terminal to cloud"; doc quickstart, "Select a repository and branch"].
  - **A description.** Bare `claude --cloud` fails with `Error: --cloud requires a description.` [probe].
- **How it reports the session.**
  - Create form: `Created cloud session: <title>`, `View: https://claude.ai/code/session_<id>?from=cli&m=0`, `Resume with: claude --teleport session_<id>`, then exit [probe]. The docs don't show this output. The follow-up form takes the `session_<id>` from those lines.
  - Follow-up form: `Sent to cloud session.`, `Session ID: …`, `View: …`, or `{ok, session_id, url}` with `--output-format json` [doc cloud, "Output and errors"].
  - `--output-format` works only with `-p`, and the create form rejects `-p` [doc headless; bin]. So an agent that reads the create form's output must parse the text lines.
- **[probe], first pass.** This research's agent shell made two tries (see the Exploration log).
  - Probe 1, `claude --cloud "<prompt>" < /dev/null` with no terminal, exited with status 1. Nobody read its output.
  - Probe 2 wrapped the command in `script` to give it a pseudo-terminal. The agent's local permission check refused to run it, twice.
  - Neither created a session: the cloud session's `list_sessions` shows none from probe 1 [probe].
  - The maintainer's own run above, in a real terminal, did create one. That session is the source of issue #78's first-hand answers.
- **Plan locally, execute in the cloud** is the documented pattern: commit a plan, push, then `claude --cloud "Execute the plan in docs/…"` [doc cloud, "Tips for cloud tasks"]. That matches this repo's handoff files.
- **API:** a routine with an API trigger has a per-routine URL and bearer token [doc routines, "Add an API trigger"; "Trigger a routine"].
  - `POST https://api.anthropic.com/v1/claude_code/routines/<id>/fire` with headers `anthropic-beta: experimental-cc-routine-2026-04-01` and `anthropic-version: 2023-06-01` and optional `{"text": "…"}` returns `{"type": "routine_fire", claude_code_session_id, claude_code_session_url}`.
  - You make tokens on the web only.
  - No documented API starts a plain cloud session. But inside a cloud session, a "Claude Code Remote" MCP server offers `create_session` (repo, branch, `outcome_branch`, prompt) [probe]. This research didn't call it. Nobody knows yet whether a local session on the Mac gets the same server.
- **From a local agent's tools:** the `RemoteTrigger` tool (behind `/schedule`) creates, updates, runs and lists routines [doc tools].
- **Requirements** [doc cloud, "Send follow-ups from the CLI"; "GitHub authentication options"]:
  - a claude.ai sign-in, not an API key or third-party provider. An LLM gateway set only through `ANTHROPIC_BASE_URL` is fine if you also run `claude auth login`.
  - the organization policy `allow_remote_sessions` on
  - not a Zero Data Retention organization

### Routines in detail

- **Where you make them.** claude.ai/code/routines, the Desktop app (Routines, **New routine**, **Cloud**), or `/schedule` (alias `/routines`) in the CLI. In the Desktop app, **Local** makes a Desktop scheduled task instead. All of them write to the same account [doc routines, "Create a routine"; "Create from the CLI"]. Routines made from a project appear on its **Routines** tab [doc routines, "Related resources"].
- **What one holds.** Name, prompt (with a model selector: that model on every run), one or more repositories, an environment, connectors, triggers [doc routines, "Create from the web"].
- **The prompt.** It must be self-contained and say what success looks like. From v2.1.213, the fired session takes the saved prompt as its assigned task, not as untrusted content. But it "is not live user input and can't act as approval or consent for actions during the run". The run handles fetched content as usual [doc routines, "Name the routine and write the prompt"].
- **Fire text is untrusted.** `text` from the API, or typed into **Run now**, arrives inside a `<routine-fire-payload>` block labelled untrusted. Claude won't follow instructions in it unless the saved prompt says to (for example "Investigate the alert described in the routine-fire-payload block"). It's a literal string, and the run doesn't parse JSON in it [doc routines, "Trigger a routine"].
- **Schedule trigger** [doc routines, "Add a schedule trigger"; "Schedule a one-off run"]:
  - Presets: hourly, daily, weekdays, weekly, in local time.
  - A custom cron through `/schedule update`. Minimum interval: one hour.
  - A run set exactly on the hour can start several minutes late.
  - One-off runs ("`/schedule tomorrow at 9am, …`") fire once. Then they turn off on their own and show **Ran**.
- **API trigger** [doc routines, "Add an API trigger"; "API reference"]:
  - You add it from the web only, after you save the routine.
  - The token shows once, per routine. **Regenerate** and **Revoke** are in the same modal.
  - The endpoint is for claude.ai users. It is not part of the Claude Platform API.
  - Breaking changes come under new dated beta headers. The two previous headers keep working.
- **GitHub trigger** [doc routines, "Add a GitHub trigger"; "Supported events"; "Filter pull requests"]:
  - It needs the Claude GitHub App on the repository. `/web-setup` isn't enough.
  - Events: pull request (opened, closed, assigned, labeled, synchronized, …) or release.
  - Filters on author, title, body, base branch, head branch, labels, draft, merged. Operators: equals, contains, starts with, is one of, is not one of, or matches regex (whole-field match).
  - Every event starts a new session. No session is reused.
  - Per-routine and per-account hourly caps drop extra events during the preview.
  - From the CLI: v2.1.225+.
- **Branches and connectors.** See sections 5 and 6.
- **Artifacts.** A scheduled or **Run now** run can republish one of your existing artifacts without a question. That works only if the artifact meets all of these [doc routines, "Create a routine"]:
  - it's yours and not public
  - it doesn't show new versions to viewers on its own
  - it carries only the page
  - it holds no connector grant

  Anything else, including a new artifact, waits for approval.
- **Admin switch.** A Team or Enterprise Owner can turn routines off. Then existing ones stop [doc routines, intro].

## 8. Long work

- **Subagents** "work the same way they do locally", and the repo's `.claude/agents/` load [doc cloud, "Manage context"]. First-hand, they go only one level deep: `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`. A sub-agent has no Agent tool, and no `PushNotification`, `ListAgents` or `CronCreate` [probe; [session-probe §5](cloud-agents-session-probe.md#5-sub-agent-tools)].
- **Agent teams** are off by default. Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` on the environment [doc cloud].
- **Idle expiry** kills background subagents and shell commands when Anthropic reclaims the VM [doc cloud, "Environment expired"]. A long orchestration that waits on a human answer risks that.
- **Projects** are Anthropic's answer to "run a whole effort" [doc projects, "How a project is organized"; "What draws on your plan"]:
  - A coordinator conversation (Opus, low effort by default) starts threads (Opus, high effort).
  - Each thread works on its own branch. It opens PRs and auto-fixes them.
  - An Overview pane groups threads as Ready for review, Waiting on you, Working, Landing, Idle, Resolved.
  - Threads run in auto mode where the model supports it.
  - A thread-count limit that you ask for is "a preference rather than a cap". The hard limit is 200 new threads a day.
  - In a project with several repositories, repo permission rules and hooks don't apply [doc projects, "What threads pick up from your repositories"].
- **Routines** run autonomously: "there is no permission-mode picker". Commands and connector writes run "without stopping for approval", apart from some artifact actions [doc routines, "Create a routine"]. The fired prompt can't stand in for your approval of anything during the run [doc routines, "Name the routine and write the prompt"]. So a routine suits a well-defined step that nobody watches. It doesn't suit a step that needs a human go.
- **Parallel sessions from the CLI.** Each `claude --cloud "…"` is its own independent session and branch, and they run at the same time. The docs pitch this for parallel tasks "without managing multiple worktrees" [doc cloud, "Run tasks in parallel"; doc quickstart, intro]. Parallel runs draw rate limits proportionately [doc cloud, "Limitations"].
- **Herdr and worktrees.** Herdr isn't pre-installed. Plain `git worktree` works: the probe created, listed and removed one in the VM [probe; [session-probe §6](cloud-agents-session-probe.md#6-worktrees)]. [session-workflow §3](cloud-agents-session-workflow.md#3-the-effort-workflow-in-a-cloud-session) covers how this repo's effort workflow maps onto one VM. Within one cloud session, the parallel work is subagents. Across sessions, it's projects or several `--cloud` calls.
- **Starting another cloud session from inside one.** The four pages don't say. The VM's `claude` is signed in with a claude.ai OAuth token and has `--cloud`. The session also has the Remote MCP `create_session` tool [probe; [session-probe §7](cloud-agents-session-probe.md#7-the-claude-cli-inside-the-vm)]. Both look possible. This research ran neither.
- **The platform's Stop hook.** Every cloud session runs a Stop hook. It refuses to end a turn while the checkout has uncommitted, untracked, unpushed or unsigned work. So it sends the session back to commit and push. Files meant to stay local must be git-ignored [probe; [session-probe §9](cloud-agents-session-probe.md#9-hooks-and-launcher-settings)].

## 9. Watching and answering

- **Where:** the session list (sidebar) at claude.ai/code, the mobile Code tab, the Desktop app [doc cloud, "Work with sessions"]. From the CLI, `/mobile` shows a QR code for the mobile app [doc quickstart, "Next steps"].
- **Answering:** type in the session. A message sent while Claude works waits in a queue. The ✕ on it takes it back until Claude has read it. You can answer a question until the environment expires [doc cloud, "Take back a queued message"; "From terminal to cloud"].
- **From a local agent, send:** `claude -p "message" --cloud <session-id-or-url>` "posts one message and exits", and doesn't wait for a reply [doc cloud, "Send follow-ups from the CLI"; "Output and errors"].
  - The message can also come on stdin (`echo "…" | claude -p --cloud <id>`).
  - The ID can be bare (`session_…` or `cse_…`) or the claude.ai/code URL, with or without scheme or query.
  - `--output-format json` gives `{ok, session_id, url}`, or `{ok: false, session_id, error}` when the send fails. `stream-json` isn't supported.
  - It needs no local session state and works from any logged-in machine.
- **Send errors worth handling** [doc cloud, "Output and errors"]:
  - `Session not found: <id>`
  - `cloud session <id> is archived and cannot accept new messages` (start a new one)
  - `Attaching to an existing cloud session is not enabled for your account.` (you forgot `-p`)
  - policy and provider errors go to stderr without JSON
- **From a local agent, list and message:** `ListAgents` shows cloud sessions only "while this session is connected to Remote Control". `SendMessage` then goes "through Anthropic servers, straight to the cloud session". Without Remote Control, a message still goes, but it carries no reply address [doc messaging, "See which sessions Claude can reach"; "Message sessions on other machines"].
- **From a local agent, read state:** no documented command prints a cloud session's transcript or status to the terminal.
  - `/tasks` lists background sessions and teleports into one. `--teleport` copies the whole conversation locally [doc cloud].
  - For routines, `/schedule why did my nightly review do nothing` lists runs and reads a run's log (v2.1.227+) [doc routines, "Manage routines from the CLI"].
  - The `notify_when_idle` subscription works only for sessions on the same machine [doc messaging, "Get a notice when another session goes idle"].
  - The practical signal today: watch GitHub (the branch, the PR, the `Claude-Session` trailer).
- **From inside a cloud session, read state** [probe]:
  - The "Claude Code Remote" MCP server's `list_sessions` lists the account's sessions. That includes Remote Control sessions on the maintainer's own machines (shown as `bridge` sessions).
  - Each entry has its repo, branch, head, dirty flag, unpushed commit count, status bucket (working, blocked, review ready, completed, failed), last summary, and whether it needs action.
  - `get_session` gives one session's status, title, pending actions, context use and rate-limit window.
  - The four pages don't document this. Nobody knows yet whether a local session gets these tools.
- **Permission prompts can block a cloud session.** The probe session's first calls to several Remote MCP tools waited as pending actions ("Waiting on permission: `<tool>`"). The session sat in the blocked bucket until someone approved them. The record doesn't say who or what approved them. The session was in auto mode. Anyone who lists sessions sees such a session as one that needs action [probe; [session-probe §5](cloud-agents-session-probe.md#5-sub-agent-tools)].
- **Notifications:**
  - Projects send Desktop notifications when Claude posts, or a thread errors or needs input (Desktop only) [doc projects, "See what needs you in Overview"].
  - The docs describe phone push for Remote Control sessions and Dispatch [doc mobile, "Get push notifications"]. Unverified: whether a plain cloud session pushes to the phone.
  - The probe session's main loop has a `PushNotification` tool (deferred), which its sub-agents lack. This research didn't test whether it reaches the phone [probe].
  - A routine's green status means only no infrastructure error, not success. Blocked requests, missing connector tools and task failures show only in the transcript [doc routines, "View and interact with runs"].
- **Routine runs.** Each run is a new session alongside your others. Open it from the routine's run list to review it, create a PR, or continue. `/schedule list`, `/schedule update` and `/schedule run` manage routines from the CLI. **Run now** and the on/off switch are on the detail page [doc routines, "Manage routines"; "Manage routines from the CLI"].

### Reviewing the work

- **Diff view.** The `+42 -18` indicator opens a file list and diff, against the session's base branch by default. **Compare against** picks another branch. Diffs come from raw git blobs, so repo diff drivers and `textconv` don't apply [doc cloud, "Review changes"; doc quickstart, "Open the diff view"].
- **Inline comments.** Select a line, type, press Enter. Comments wait in a queue and go with your next message. So Claude sees "at `src/auth.ts:47`, …" next to the instruction [doc quickstart, "Leave inline comments"].
- **Create PR.** See section 6. After that, keep work going in the same session, or turn on auto-fix [doc quickstart, "Keep iterating after the PR"].
- **Sharing** [doc cloud, "Share sessions"]:
  - Pro and Max: **Private** or **Public** (any logged-in claude.ai user). Repository access verification is off by default.
  - Team and Enterprise: **Private** or **Team**. Verification is on.
  - Recipients see the state when they open the link, not live updates.
  - Sessions can hold private code and credentials, so check before you share. Settings > Claude Code > Sharing settings can require repo access or hide your name.
- **Archive and delete.** An archive hides a session from the default list (use the filter to see it). An archived session refuses new `-p --cloud` messages. A delete is permanent. You delete from the archived filter or the session menu, with a confirm [doc cloud, "Archive sessions"; "Delete sessions"; "Output and errors"]. You rename, archive or delete routine runs the same way [doc routines, "View and interact with runs"].
- **Ultrareview.** Only you launch it: `/code-review ultra` (Claude never starts one on its own), or `claude ultrareview` [doc ultrareview, "Run ultrareview from the CLI"].
  - **Scope** [doc ultrareview, "Review against a different base"; "Review a pull request"; "Pass a request in plain words"]:
    - No argument reviews the current branch against the default branch, including uncommitted and staged changes.
    - A branch, commit or tag sets another base (fetched from `origin` if needed).
    - A PR number, `#1234`, `PR 1234` or a PR URL for this repo reviews that PR.
    - More than one word is a note that the findings relate to (v2.1.218+).
  - **What it uploads:** a branch review bundles the local repository. Files that look like credentials follow the `--cloud` bundle rules. PR mode uploads nothing. It clones the PR from GitHub with your connected GitHub account, which must see the repo (checked before launch since v2.1.248) [doc ultrareview, "Run ultrareview from the CLI"; "Review a pull request"].
  - **Limits** [doc ultrareview, "Diff limits and fallbacks"; "Run ultrareview non-interactively"]:
    - By default up to 500 changed files and 8,000 changed lines.
    - It refuses an empty diff.
    - A first commit, or a branch with no merge base, gets a review of the whole repository. That needs an interactive confirm, or a `claude ultrareview` that you run yourself.
    - When Claude runs the subcommand through Bash, it refuses the whole-repository review.
    - Too big to bundle: push, open a draft PR, and review that.
  - **Running** [doc ultrareview, "Track a running review"]:
    - A launch dialog shows scope, free runs left and a cost estimate.
    - The review then runs in the background for about 5 to 10 minutes.
    - `/tasks` shows, opens or stops it. A stop archives the session, with no partial findings.
    - Findings arrive as a notification, each with a file location.
  - **Posting** [doc ultrareview, "Post findings to the pull request"]:
    - On a github.com PR, from v2.1.227, it can post the findings as one plain comment from your GitHub account (not a review or approval), through the Anthropic API.
    - It is off by default. `--post` preselects it interactively. In `claude ultrareview`, `--post` posts without a question.
    - In an interactive session, the session must stay open until the findings arrive. Otherwise it posts nothing.
  - **Non-interactive** [doc ultrareview, "Run ultrareview non-interactively"]:
    - `claude ultrareview [PR|base]` blocks until done and prints findings to stdout (`--json` for raw `bugs.json`, `--timeout` default 45 minutes).
    - Progress and the session URL go to stderr.
    - Exit codes: 0 done. 1 failed, stopped or timed out. 130 interrupted (the remote review keeps running).
    - `claude -p '/code-review ultra'` only launches and prints a tracking link. It stops before a paid run.
  - **Where it isn't available** (API key only, Bedrock, Vertex/Agent Platform, Foundry, Zero Data Retention), `/code-review ultra` quietly runs a local review instead [doc ultrareview, intro].

## 10. Moving it

- **Cloud to local:** run `claude --teleport <id>` [doc cloud, "From cloud to terminal"; "Teleport requirements"]. It needs:
  - a clean checkout of the same repository (not a fork)
  - the same claude.ai account
  - a pushed branch

  It fetches the branch and loads the full conversation. The local copy is separate: new work there doesn't appear in the cloud session. Inside a cloud session, `/teleport` prints the exact command (v2.1.223+). The create form of `claude --cloud` prints that command too [probe].
- **Teleport entry points** [doc cloud, "From cloud to terminal"; "Teleport requirements"]:
  - `claude --teleport` (picker) or `--teleport <id>`
  - `/teleport` or `/tp` in a running CLI session
  - `t` in `/tasks`
  - **Open in > Terminal** in the session menu on claude.ai/code, which copies a command

  More facts:
  - Uncommitted changes prompt a stash.
  - A remote that is an SSH host alias is accepted after a confirm, when owner and repo match.
  - `--resume` is different. It reopens local history only and doesn't list cloud sessions.
  - To keep control from the phone after a teleport, start `/remote-control` locally.
- **Teleport errors:** an API-key sign-in gives `Unable to get organization UUID` (or `Error loading Claude Code sessions` in the picker). Fix it with `/login`. Teleport uses the Remote Control infrastructure. So expiry and auth errors read `Remote Control session expired` or `Access denied` [doc cloud, "Unable to get organization UUID"; "Remote Control session expired or access denied"].
- **Local to cloud:** not from the CLI ("you can't push an existing terminal session to the cloud"). The Desktop app's **Continue in > Claude Code on the Web** pushes the branch, summarizes the conversation and starts a new cloud session. It needs a clean tree, and it doesn't work for SSH sessions [doc cloud; doc desktop, "Continue in another surface"]. A cloud session can become a project with **Continue as a project** or **Move to project** [doc projects].
- **Anywhere else:** a routine run is an ordinary session that you can open and continue [doc routines]. A project thread can run locally through Remote Control on request [doc projects, "Run a thread on your own computer"].

## 11. Cost and limits

- **Plans** [doc cloud; doc routines; doc projects; doc availability]:
  - cloud sessions: Pro, Max, Team, and Enterprise premium or Chat + Claude Code seats
  - routines: all four
  - projects: Pro and Max only (beta)
- **Usage:** cloud sessions "share rate limits with all other Claude and Claude Code usage within your account … There is no separate compute charge for the cloud VM" [doc cloud, "Limitations"]. Limits are the plan's five-hour and weekly windows [doc costs; doc projects, "A thread hit the usage limit"]. Project threads that hit a limit wait, and continue on their own in the next window. Threads that a routine started stop instead [doc projects].
- **Parallelism:** several cloud sessions at once "consumes more rate limits proportionately" [doc cloud, "Limitations"].
- **Routines** [doc routines, "Usage and limits"; "Add a schedule trigger"; "Create a routine"]:
  - They draw subscription usage like any session.
  - A per-account daily cap on runs applies. The docs don't give the number. claude.ai/code/routines and claude.ai/settings/usage show it. One-off runs are exempt.
  - Minimum schedule interval: one hour.
  - GitHub-event hourly caps apply during the preview, and extra events are dropped.
  - Past the cap or the usage limit, runs continue only with usage credits on. Else they're rejected until the window resets.
  - Routines belong to one account and aren't shared.
  - A paused subscription puts routines on hold. Turn them back on afterwards.
- **IP allowlists:** an organization with IP allowlists on sees every Anthropic-hosted cloud session fail with an authentication error. The same goes for routines on Anthropic-hosted environments. They fail until support exempts them [doc cloud, "Limitations"]. Not relevant to an individual plan.
- **Usage credits** let work continue past the plan limit at API rates. Turn them on at claude.ai/settings/usage. `/usage-credits` opens that page [doc costs, "Add usage credits to your subscription"].
- **The promo credit.** Anthropic announced that cloud sessions left research preview with "a one-time credit to try them: $100 on Pro, $250 on Max". The credit is what "your cloud sessions spend first, before falling back onto your normal plan usage" [announce: [post 1](https://x.com/ClaudeDevs/status/2102871550974427462), [post 2](https://x.com/ClaudeDevs/status/2102940480736821610)].
  - Search excerpts also report three terms: a claim with `/claim-credit` or the banner at claude.ai/code, a claim deadline of 7 October (11:59 PM PT), and expiry on 4 November.
  - Unverified: this research found no docs or help-center page for these terms. `claim-credit` doesn't appear in the CHANGELOG through 2.1.284.
  - First-hand, the credit is live and in use. `get_session` reports the probe session's rate-limit type as promotional (`ccr_promotional`). Its rate-limit window resets (`resetsAt`) on 2026-11-05 at 08:00 UTC, which is midnight PST. That is a window reset, not a refill.
  - Inferred: it lines up with the reported 4 November expiry.
  - The remaining balance isn't visible from inside [probe].
- **Ultrareview** is billed as usage credits, not plan usage [doc ultrareview, "Pricing and free runs"].
  - Pro and Max get three free runs, once per account, never refreshed. Team and Enterprise get none.
  - After that, it's typically $5 to $25 a review, as the launch dialog estimates.
  - A run counts once its cloud session starts. A stopped or failed review still uses a free run. A paid one bills only the part that ran.
  - Usage credits must be on before a paid launch. The billing confirm comes once per conversation.

## Open questions

The first pass left twelve questions. Issue #78's cloud session answered most of them from inside. The rows still open say what to try next. "SP" links a section of [cloud-agents-session-probe.md](cloud-agents-session-probe.md). A bare [probe] is a check that the orchestrating session ran itself, described in the cell.

| Question | Answer | Evidence or next step |
|---|---|---|
| What does the VM actually report (`uname`, `nproc`, `free`, user, `check-tools`)? | A Firecracker microVM: Ubuntu 24.04.4, kernel 6.18, 4 vCPU Xeon, 15.7 GiB RAM, no swap, root. 30G writable of a 252G disk. Toolchains as documented, except that `gh` is missing. Playwright and Chromium present | [probe]: `uname`, `nproc`, `free`, `check-tools` in the session; [SP §7](cloud-agents-session-probe.md#7-the-claude-cli-inside-the-vm), [SP §10](cloud-agents-session-probe.md#10-disk) |
| Does the create form print the session ID or URL, and how? | Yes, then it exits: `Created cloud session: <title>`, `View: https://claude.ai/code/session_<id>?from=cli&m=0`, `Resume with: claude --teleport session_<id>`. No live checklist | [probe]: the maintainer's `claude --cloud "say hi"` on the Mac (section 7) |
| Did probe 1 create a session? | No. **Settled (E2).** | [probe]: the Remote MCP `list_sessions`, run inside the cloud session, returned a first page that reached back to 2026-09-14. So it held every 2026-09-29 session, and none came from probe 1 |
| Can a cloud session run a headless browser, and on which network level? | Yes, on Trusted, with the pre-installed Chromium, once the browser trusts the proxy's CA (`--ignore-certificate-errors-spki-list`). Only allowlisted hosts load | [SP §1](cloud-agents-session-probe.md#1-headless-browser) |
| Do WebFetch and WebSearch work under **Trusted**? | WebSearch yes. WebFetch runs in the VM under the allowlist: allowlisted hosts yes, others `EGRESS_BLOCKED` | [SP §2](cloud-agents-session-probe.md#2-webfetch-and-websearch) |
| Do skills enabled on the claude.ai account load, and does this repo's `CLAUDE.md` → `AGENTS.md` import load? | Yes to both. The account's nine skills are synced into the VM's `~/.claude/skills/synced/`, and `AGENTS.md` loaded through `CLAUDE.md`. Skills installed into the VM's `~/.claude/skills/` mid-session loaded too | [probe]: file listing and the session's own context; [session-workflow §1](cloud-agents-session-workflow.md#1-the-layers-in-a-cloud-session) |
| Does a `~/.claude/CLAUDE.md` written by the environment's setup script load? | Open (new) | Add a personal environment with the setup script in [session-workflow §2](cloud-agents-session-workflow.md#b-the-setup-script). Start one session, and ask it to quote a rule line |
| How long is the idle expiry? | Open | Not testable from inside. Leave a probe session idle, and note when a reopen provisions a fresh VM |
| Can a plain cloud session push to a branch named in the prompt (an effort branch), not only its own? | A **new** branch, yes. The session created `skills/…` from its start branch and pushed it and further commits. `get_session` then tracked it. An **existing** branch it didn't create: untested | [probe]: `git push -u origin <new branch>`, then `get_session`; [SP §4](cloud-agents-session-probe.md#4-github-proxy). Next: a session on a throwaway `probe/…` branch pushed from the Mac, asked to push there |
| Does a plain cloud session send phone push notifications? | Half answered. The main session's deferred `PushNotification` tool, called at the end of the #78 run, returned "Mobile push requested" [probe]. Sub-agents don't have it. Arrival on the phone is unconfirmed | [SP §5](cloud-agents-session-probe.md#5-sub-agent-tools). Next: the maintainer confirms whether that push arrived (E19) |
| Can a cloud session start another cloud session? | Likely. The VM's `claude` is signed in with OAuth and has `--cloud`, and the Remote MCP `create_session` is present. Not run | [SP §7](cloud-agents-session-probe.md#7-the-claude-cli-inside-the-vm). Next: one `create_session` child on a throwaway branch, then archive it ([session-workflow §4](cloud-agents-session-workflow.md#4-suggestions), suggestion 6) |
| Promo credit terms and remaining balance | The credit is live and spent first. The session's rate-limit type is promotional, and it resets 2026-11-05 at midnight PST. Balance not visible from inside | [probe]: `get_session` on the session itself (section 11). Next: the maintainer reads the balance at claude.ai/settings/usage |
| Does the GitHub proxy allow the REST sub-issue calls this repo's skills make? | Yes (`200`, with a real credential injected). GraphQL is blocked entirely, not only outside PR workflows | [SP §4](cloud-agents-session-probe.md#4-github-proxy) |
| After `claude --teleport`, does the cloud original keep running? | Open | Not run. Teleport a throwaway session, then check it with `list_sessions` or on claude.ai, and archive it (E12 in [cloud-agents.md](cloud-agents.md#proposed-experiments)) |

### Settled since the first pass

- **Can `claude --cloud "<task>"` start a session from a non-interactive agent shell?** [doc cloud; doc headless; probe]
  - The docs describe an interactive create form (live setup checklist, queued typed messages). But first-hand, the create form printed three lines and exited at once, with no checklist (section 7).
  - Still untested: whether it runs without a TTY. Probe 1 (`< /dev/null`) exited 1 with its output unread, and it created no session.
  - `-p` with a task description is rejected. `-p "msg" --cloud <session-id>` sends a follow-up.
  - The documented non-interactive start is a routine's API trigger. Inside a cloud session, the Remote MCP `create_session` is a second one, untested.
- **What does it need?** [doc cloud; doc quickstart] See section 7.
  - a claude.ai sign-in
  - `allow_remote_sessions`
  - a cloud environment (created on its own, else `/web-setup`)
  - a pushed branch on a GitHub remote
  - to push back: the GitHub App, or a `/web-setup` connection with push access. Without the App, the CLI bundles the local repository and doesn't clone it.

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
| 7 | Mac → Anthropic | Probe 1: `claude --cloud "<read-only probe prompt>" < /dev/null`, run in the background. The prompt asked for the environment commands, tool list, network checks, skill list and one subagent listed under Open questions. It asked for the results to be committed as `probe/report-1.md` and pushed to `probe/cloud-agents-1`, with no code changes, installs or PR | Exited with status 1. The local auto-mode classifier refused a read of its captured output, so nobody inspected the cause. `git ls-remote` afterwards showed `probe/cloud-agents-1` still at `8413cf7` and no `claude/*` branch. So no push from a cloud session happened. Whether it created a cloud session is unknown. Nobody steered or messaged one afterwards. No second probe was started |
| 8 | Mac → GitHub | `git push origin --delete probe/cloud-agents-1`, `git switch` back to the ticket branch, `git branch -D probe/cloud-agents-1`, then `git ls-remote origin 'refs/heads/probe/*' 'refs/heads/claude/*'` | Removed the throwaway branch locally and on GitHub; the final `ls-remote` printed nothing |
| 9 | Mac (worktree) | Wrote this file; one commit | This file |
| 10 | Mac (follow-up, new worktree) | `git merge --ff-only skills/cloud-agents` (twice, as the effort branch moved on); `curl` of the `.md` form of the cloud, env, quickstart, cli-reference and headless pages; the CHANGELOG through `gh api` (no entry on `--cloud` and terminals or `-p`); `claude --help`; `gh api user/installations` and `gh api repos/yahyabedirhan/skills/installation` to learn whether the Claude GitHub App is installed (GitHub refused both for this token type, so unknown) | Worktree branch fast-forwarded; scratch files outside the repo |
| 11 | Mac → GitHub | `git ls-remote origin 'refs/heads/probe/*' 'refs/heads/claude/*'` (empty), `git switch -c probe/cloud-agents-2` at the effort branch head `d5c9206`, `git push -u origin probe/cloud-agents-2`. The read-only probe prompt (the environment commands, tool versions incl. browsers and Playwright, skill list and first instruction heading, WebFetch of `code.claude.com/docs/llms.txt` and one WebSearch, one sub-agent, `CLAUDE_CODE_REMOTE`, `claude --version`, a read-only `gh api …/issues/45/sub_issues`; results to `probe.md` pushed to the probe branch) went to an ignored `.scratch/` file | Created the throwaway branch locally and on GitHub, with no new commits |
| 12 | Mac | Probe 2: `script -q .scratch/probe2.log claude --cloud "<prompt>"`, first with the prompt substituted from the file, then with it inline | The agent's local permission check refused it both times. Nothing ran, and no cloud session was created. Per the effort's rules, the probe stopped there and didn't work around the check |
| 13 | Mac → GitHub | `git push origin --delete probe/cloud-agents-2`, `git switch` back, `git branch -D probe/cloud-agents-2`, then `git ls-remote origin 'refs/heads/probe/*' 'refs/heads/claude/*'` | Removed the throwaway branch locally and on GitHub; the final `ls-remote` printed nothing |
| 14 | Mac (synthesis, #74) | Added `claude_code_session_id` to the routine `/fire` response in §7 | This file only |
| 15 | Cloud session (#78) | `curl -sS https://code.claude.com/docs/en/<page>.md` for web-quickstart, claude-code-on-the-web, routines, ultrareview and headless (all 200); read in full and compared with sections 1 to 11; reconciled with the maintainer's `claude --cloud "say hi"` run on the Mac | Copies in `.scratch/cloud-session/docs/` (ignored); this file's Short answer and sections 1 to 11 |
| 16 | Cloud session (#78, integration) | Read the three new #78 files and the orchestrator's own session probes; corrected the Short answer (browser, what loads, GitHub, watching, cost) and sections 2, 4, 5, 6, 7, 8, 9 and 11 against them; replaced the Open questions table with the answered one; added the See also list | This file only |
