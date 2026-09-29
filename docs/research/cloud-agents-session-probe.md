# Inside a Claude Code cloud session: first-hand probes

Facts for [Research: Claude Code cloud sessions tested from inside one (#78)](https://github.com/yahyabedirhan/skills/issues/78), under [Spec: research cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45). It answers, from inside a real cloud session, the open questions left by [Claude Code in the cloud (#69)](cloud-agents-claude-code.md) and the "#69's cloud sessions" TODO in [cloud-agents-delegation.md](cloud-agents-delegation.md). Run on 2026-09-29 in a session the maintainer started with `claude --cloud "say hi"` from the Mac; Claude Code 2.1.285 in the VM; Anthropic-hosted environment on the default **Trusted** network level.

The probes ran in a sub-agent of that session (spawn depth 1), so the tool findings in probe 5 are a sub-agent's view. Nothing here created a session, routine, trigger or webhook, wrote to GitHub, or changed `~/.claude`.

Evidence tags:

- **[probe]** a command run for this file; exact command given, output shortened.
- **[harness]** a file the harness itself put in the VM: `/root/.ccr/README.md`, `/tmp/claude-append-system-prompt.txt` (text appended to Claude's system prompt), the hook scripts under `~/.claude/`, or the `claude` process's command line.
- **[doc `<page>`, "`<section>`"]** Claude Code's docs at `https://code.claude.com/docs/en/<page>`, as cited in [cloud-agents-claude-code.md](cloud-agents-claude-code.md).
- **Unverified** marks an inference.

Verdicts against the old doc: **confirmed**, **contradicted**, or **new**.

## Short answer

- **Browser: yes, out of the box, with one catch.** Chromium 141 is pre-installed for Playwright and launches headless in under a second. It doesn't trust the egress proxy's CA, so every HTTPS page fails with `ERR_CERT_AUTHORITY_INVALID` until you trust that one CA key (`--ignore-certificate-errors-spki-list=<proxy CA SPKI>`). Then allowlisted hosts load and blocked hosts fail with `ERR_TUNNEL_CONNECTION_FAILED`. No setup script or wider network needed. Contradicts "a headless browser needs at least a setup script, and likely Custom/Full network".
- **WebFetch obeys the allowlist; WebSearch doesn't need it.** WebFetch runs inside the VM's `claude` process and returns `EGRESS_BLOCKED` for `example.com`. WebSearch works (server-side).
- **Blocked hosts get a plain `403` with no `x-deny-reason` header.** The body names the host. Contradicts [doc routines, "Environments and network access"].
- **GitHub GraphQL is blocked entirely,** not "a pinned set of PR operations". The proxy answers `403` and points at REST plus special `…/ccr/…` REST routes for review threads, auto-merge and draft state. REST works for the attached repo, including sub-issues and `/user`. REST to any other repo is refused, even a public one; `git` reads of other public repos still work.
- **Push to a non-`claude/` branch works.** The orchestrating session created and pushed `skills/cloud-agents-session-probe` (reflog: "update by push"). The harness prompt only asks the model not to push elsewhere "without explicit permission".
- **Sub-agents lack the Agent tool** (spawn depth 1 holds), `PushNotification`, `ListAgents` and `CronCreate`. They do get `Monitor`, `SendMessage`, `WebFetch`, `WebSearch`, the GitHub MCP tools and the Claude Code Remote MCP tools (subject to the user's permission prompts).
- **The three missing skills** carry `disable-model-invocation: true`, so they're hidden from the model but meant for the user to type.
- **The Stop hook** refuses to end a turn while the checkout has uncommitted, untracked, unpushed or unsigned commits.
- **Disk:** `df` shows 252G, but only about 30G is writable; the rest is ext4 reserved blocks. `/tmp` is on the same disk. `/mnt/user-data` exists with empty `uploads`, `working` and `outputs`.
- **The session bills to a promotional pool** (`rateLimitType: ccr_promotional`) whose rate-limit window resets (`resetsAt`) 2026-11-05 00:00 PST: a window reset, not a refill. Inferred: that matches the announced 4 November promo credit expiry.

## 1. Headless browser

Commands [probe]: `.scratch/cloud-session/pw-probe.js` (launch Chromium through `HTTPS_PROXY`, `setContent`, screenshot, `goto` two URLs), then `pw-probe2.js` (headless shell vs full Chromium, three hosts), then `pw-probe3.js` (same, plus the proxy CA's SPKI hash). Run with `node .scratch/cloud-session/pw-probe.js`; memory with `free -m` before, during and after.

Results:

- `chromium.launch({headless: true, proxy: {server: HTTPS_PROXY}})` launched Chromium 141.0.7390.37 in 765 ms. `setContent` rendered and ran its script (title `ok-2`), and the screenshot saved.
- `goto https://code.claude.com/docs/llms.txt` → `net::ERR_CERT_AUTHORITY_INVALID`. Same for `https://github.com/` and `https://api.github.com/zen`, with both the headless shell and full Chromium.
- `goto https://example.com` → `net::ERR_TUNNEL_CONNECTION_FAILED` (the proxy's 403 to CONNECT).
- Cause: the proxy re-signs TLS with its own CA, `CCR Upstream Proxy CA (staging)`, and Chromium's NSS store at `~/.pki/nssdb` holds no such CA; the store was created by this first Chromium run, not pre-seeded. The proxy README says "the browser NSS store" is set up; it wasn't for Playwright's Chromium. `certutil` isn't installed and `apt-get download libnss3-tools` got a 404 (stale package index), so the store couldn't be filled without an `apt-get update`.
- Fix that keeps verification on: compute the proxy CA's SPKI hash (`openssl x509 -in /root/.ccr/agent-proxy-ca.crt -noout -pubkey | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | base64`) and launch with `args: ['--ignore-certificate-errors-spki-list=<hash>']`. That trusts only chains through the proxy's key. Then `code.claude.com/docs/llms.txt` → 200 (`# Claude Code Docs`), `github.com` → 200 (its asset host `github.githubassets.com` is blocked, so pages render unstyled), `example.com` → tunnel refused.
- Memory: used 537 MB before, 611 MB during (plus about 400 MB page cache), unchanged after. A headless browser is cheap on the 15.7 GiB VM.
- The harness prompt says: "Chromium is pre-installed and Playwright is configured to find it (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`; `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1` …). Do not run `playwright install`", and to use `executablePath: '/opt/pw-browsers/chromium'` if a project pins another Playwright version [harness]. `/opt/pw-browsers` holds `chromium-1194`, `chromium_headless_shell-1194`, `ffmpeg-1011` and a `chromium` symlink.

Verdict: **contradicted** ("no browser named … needs at least a setup script, and likely Custom/Full network"). The browser is there and the Trusted network is enough for allowlisted hosts. **New:** the CA trust step.

## 2. WebFetch and WebSearch

Commands [probe]: WebFetch `https://code.claude.com/docs/llms.txt`; WebFetch `https://example.com`; WebFetch `https://en.wikipedia.org/wiki/Firecracker_(software)`; WebSearch "Claude Code cloud sessions". Then `curl -sS "$HTTPS_PROXY/__agentproxy/status"` to see whether the fetches reached the local relay.

Results:

- `code.claude.com` → fetched and summarized.
- `example.com` and `en.wikipedia.org` → error `{"error_type":"EGRESS_BLOCKED","domain":"example.com","message":"Access to example.com is blocked by the network egress proxy."}`.
- WebSearch → nine results (code.claude.com, theregister.com, anthropic.com and others). Hosts it returned are still unfetchable here.
- Where WebFetch runs: in the VM. The `claude` binary builds that exact error (`EgressBlockedError`) when its local HTTP client gets a proxy CONNECT refusal. The WebFetch attempts didn't show up in the relay's `recentRelayFailures`, while `curl` and Playwright attempts did; the relay is served by the `claude` process itself (it owns the listening port), so the CLI's own requests likely skip the relay's log. Unverified which path they take inside the process.
- `platform.claude.com` answered 200 to `curl` (it's reachable under Trusted).

Verdict: **new** for both open items: WebFetch follows the environment's allowlist (it runs locally, not server-side), WebSearch works regardless. Research against arbitrary pages still needs **Full** or **Custom** network, as the old doc said.

## 3. Network and the proxy

Commands [probe]: `curl -sS -D - https://example.com`; `curl -sv https://example.com`; a raw `CONNECT example.com:443` to the relay port to read the body curl hides; `curl -x "$HTTPS_PROXY" http://example.com`; the status endpoint above; `cat /root/.ccr/README.md`.

Results:

- Blocked host: `HTTP/1.1 403 Forbidden`, headers `Content-Type: text/plain; charset=utf-8`, `X-Content-Type-Options: nosniff`, `Content-Length: 69`, `Connection: close`. Body: `request blocked: no rule or allowlist entry allows host "example.com"`. **No `x-deny-reason` header.**
- Plain HTTP through the relay: `405 Method Not Allowed`, "this proxy only accepts HTTPS CONNECT tunnels".
- Status endpoint: `enabled`, `gitConfigInjection` and `gitSshRewrite` true, `javaTrustStorePath` set, a `noProxy` list (Anthropic API and MCP proxy hosts, npm, jsr, PyPI, crates, Go proxy, private ranges), and a ring of the last 20 relay failures (host, time, "gateway answered 403 to CONNECT").
- `apt-get` reached `security.ubuntu.com` over plain HTTP (it returned 404 for a stale package), so apt has its own route.
- The README [harness], in short: HTTPS goes to a local relay on `127.0.0.1:<port>` (`HTTPS_PROXY`), which tunnels to "a policy-enforcing egress proxy"; TLS is re-terminated there, so tools must trust `/root/.ccr/ca-bundle.crt`; CA env vars, the system store, a JVM truststore, Bazel, "the browser NSS store" and gsutil are pre-set. It lists failure classes: TLS errors (point the tool at the bundle), 405 (old axios or `HTTP_PROXY`), 403/407 (policy denial: "Do not retry or route around it, report the blocked host"), mid-transfer resets (see `recentRelayFailures`), tools that ignore the proxy (Node's built-in `fetch` needs `NODE_USE_ENV_PROXY=1`, aiohttp `trust_env=True`, Bundler reads only `HTTP_PROXY`), git (SSH remotes rewritten to HTTPS), Docker (containers can't reach the relay; use `--network host` and copy the CA). Not supported: gRPC or HTTP/2-only APIs, WebSocket upgrades, client mTLS, pinned certificates, non-443 HTTPS ports, raw TCP databases.
- The relay port is owned by the `claude` process (PID found through `/proc/net/tcp`), whose environment carries `CCR_AGENT_PROXY_ENABLED=1` and `CCR_UPSTREAM_PROXY_ENABLED=1` [probe].

Verdict: security proxy **confirmed** [doc env, "Security proxy"]; `403` **confirmed**; `x-deny-reason: host_not_allowed` **contradicted** for this environment (the reason is in the body); the WebSocket, gRPC and raw TCP limits are **new** and matter for remote-driving tools (Herdr, SSH-like clients).

## 4. GitHub proxy

Commands [probe]: `git ls-remote origin`; `git fetch origin main`; `curl -X POST https://api.github.com/graphql` with the placeholder token and four queries (`{ viewer { login } }`, an issue title, `projectsV2(first:1){totalCount}`, `subIssues(first:1){totalCount}`), and, in the review pass, a read-only PR query `repository(owner,name){pullRequest(number:76){title state}}`; REST `GET /user`, `GET /repos/yahyabedirhan/skills/issues/45/sub_issues`, `GET /repos/anthropics/claude-code` with and without the token; `git ls-remote https://github.com/anthropics/claude-code HEAD`; `raw.githubusercontent.com`. Only status codes and error text recorded.

Results:

| Call | Status |
|---|---|
| `git ls-remote origin` | Works: 19 refs, all branches, PR refs |
| `git fetch origin main` | Works; the shallow single-branch clone gained `origin/main` |
| GraphQL, any query (viewer, issue, Projects v2, sub-issues, a read-only PR query on #76) | `403`: "GitHub GraphQL is not available from Claude Code sessions; use the REST API … For review threads, auto-merge, and draft/ready-for-review use the CCR routes on api.github.com: `GET /repos/{owner}/{repo}/pulls/{n}/ccr/review_threads`, `POST …/pulls/{n}/ccr/comments/{comment_id}/resolve` (or `/unresolve`), `PUT` or `DELETE …/pulls/{n}/ccr/auto_merge`, `POST …/pulls/{n}/ccr/ready_for_review`, `POST …/pulls/{n}/ccr/convert_to_draft`" |
| REST `GET /user` (token) | `200` (so the proxy does inject a real credential) |
| REST sub-issues of #45 | `200` |
| REST `anthropics/claude-code`, with or without token | `403`: "GitHub access to this repository is not enabled for this session. Use add_repo to request access …" |
| `git ls-remote` of `anthropics/claude-code` | Works (public read over git) |
| `raw.githubusercontent.com` | `200` |

The harness prompt repeats the scope: "GitHub access for this session is currently scoped to `yahyabedirhan/skills`" [harness]. The only MCP server in the VM's own `--mcp-config` is `github`, reached through `api.anthropic.com` [probe]; the Remote, Gmail and Docs connectors arrive another way (Unverified: through the session's SDK connection).

Pushing: the remote-tracking reflog shows `claude/<slug>` "update by push" at session start and `skills/cloud-agents-session-probe` "update by push" at 20:07 UTC, a new branch outside `claude/` pushed by the orchestrating session [probe, `git reflog show refs/remotes/origin/<branch>`]. `get_session` lists that branch under the session's `outcomes` [probe]. The harness prompt names one "designated branch" (`claude/<slug>`) and says "NEVER push to a different branch without explicit permission" [harness], which is an instruction, not a proxy rule.

Verdict: GraphQL scope **contradicted** ("a pinned set of GraphQL operations for pull-request workflows" [doc env, "GitHub proxy"]: none pass here). REST sub-issues **confirmed** working, now with evidence of authenticated access (`/user` 200). Repository scope **confirmed** and stricter than expected (public repos too, REST only). Push to "the session's current working branch" only **confirmed**, read as the checked-out branch; a new branch name works.

## 5. Sub-agent tools

Commands [probe]: read this sub-agent's own tool list; `ToolSearch` with `select:PushNotification,ListAgents,CronCreate,Agent,SendUserFile,Workflow` and keyword searches; call the read-only Remote tools `get_session` and `read_documentation`. `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` in the environment.

| Tool | Main session (brief, and `get_session`'s tool list) | This sub-agent |
|---|---|---|
| Agent (Task) | Yes | **No**: spawn depth 1 means sub-agents can't spawn |
| PushNotification | Deferred | **No** ("No matching deferred tools found") |
| ListAgents | Deferred | **No** |
| CronCreate | Deferred | **No** |
| SendUserFile, Workflow | Yes | **No** |
| SendMessage | Deferred | Yes (deferred; a sub-agent's send goes out under the parent's address) |
| Monitor | Deferred | Yes (deferred) |
| WebFetch, WebSearch | Deferred | Yes (deferred) |
| `mcp__Claude_Code_Remote__*` | Yes | Yes, all of them, loaded up front |
| `mcp__github__*` | Yes | Yes (deferred) |
| Gmail, Claude Docs, Artifact | Yes | Yes |

The Remote tools work from a sub-agent but go through a permission prompt: `get_session` showed the session blocked on "Waiting on permission: `mcp__Claude_Code_Remote__read_documentation`" while that call waited for approval, and it ran afterwards. Who or what approved isn't recorded; the session was in auto mode at the time. `get_session` also showed `environment_kind: anthropic_cloud`, `origin: claude_code_cli`, a tag `config:auto-create-pr:off`, `cross_session_inbound: available`, context use against a 1M-token window, and `rate_limit_info.rateLimitType: ccr_promotional` [probe].

The `claude` process's command line shows how tools are chosen: `--tools preset:default,Task,Bash,…,WebFetch,WebSearch,…,Monitor,SendUserFile,REPL,…,ToolSearch`, `--allowed-tools` the same plus `mcp__github__*`, `--settings ~/.claude/launcher-settings.json`, `--mcp-config /tmp/mcp-config-<session>.json`, `--append-system-prompt-file /tmp/claude-append-system-prompt.txt`, `--input-format stream-json --output-format stream-json`, and an `--sdk-url` / `--resume` pair on `api.anthropic.com/v1/code/sessions/<id>` [probe, `/proc/<pid>/cmdline`, IDs redacted].

Verdict: subagents "work the same way" [doc cloud] **confirmed** for one level only; **new:** no nesting, and the notification and cross-session listing tools stay with the main session.

## 6. Worktrees

Command [probe]: `git worktree add -b probe/wt-probe .scratch/cloud-session/wt-probe HEAD`, `git worktree list`, `git -C … status -sb`, `git worktree remove .scratch/cloud-session/wt-probe`, `git branch -D probe/wt-probe`.

Result: created, checked out, listed, removed, branch deleted, all without error. Nothing pushed.

Verdict: "plain `git worktree` is available" **confirmed**. So the orchestrating skills' worktree step works in a cloud VM without treehouse; Herdr is still absent.

## 7. The `claude` CLI inside the VM

Commands [probe]: `claude --version`; `claude --help | grep -iE -A1 'cloud|teleport|remote'`; `claude auth status`. `claude --cloud "<task>"` was not run.

Results:

- 2.1.285. `--cloud [description|session_id|url]`, `--teleport [session]`, `--remote-control [name]`, `--remote-control-session-name-prefix`, `ultrareview`, and a flag the old doc doesn't mention: `--environment <environment_id>`, "Create a new cloud session that runs on the given self-hosted environment".
- `claude auth status`: `loggedIn: true`, `authMethod: oauth_token`, `apiProvider: firstParty`.
- `claude` in the VM is `/opt/claude-code/bin/claude`, a read-only ext4 volume, symlinked into `/opt/node22/bin` at boot; it's run by `environment-manager task-run` (`/opt/env-runner`, also read-only), itself started by PID 1 `/process_api --firecracker-init` [probe, `ps`].

Verdict: **new.** The VM's CLI is signed in with a claude.ai OAuth token and has `--cloud`, so starting another cloud session from inside looks possible. Unverified: not run, by the brief's rules. Firecracker is now **confirmed** from PID 1's arguments (the brief had it as an inference from the kernel name).

## 8. The three skills that didn't show up

Command [probe]: print the frontmatter of `~/.claude/skills/{init-effort,orchestrate-with-handoff,skill-recap}/SKILL.md` (symlinks into `~/.agents/skills/`), and list the frontmatter keys of every installed skill.

Result: all three, and only those three, have `disable-model-invocation: true` (with `argument-hint`). The other 16 have none.

Verdict: **new, explained.** They are user-only slash commands; Claude Code hides them from the model's skill list by design. A user typing `/orchestrate-with-handoff <path>` in this session should still run it. Unverified here: a sub-agent can't type a slash command.

## 9. Hooks and launcher settings

Commands [probe]: `cat ~/.claude/stop-hook-git-check.sh`; the docstrings of `stop-hook-reply-gate.py` and `user-prompt-submit-reply-reminder.py`; `jq` of `~/.claude/launcher-settings.json` with long strings cut.

`launcher-settings.json` [harness]: `$schema`, one `hooks.Stop` entry (matcher `""`, command `~/.claude/stop-hook-git-check.sh`) and `permissions.allow: ["Skill"]`. It's passed with `--settings`.

The Stop hook, in order, exits 0 (lets the turn end) if the hook is already active, if the directory isn't a git repo, or if there is no remote. Otherwise it blocks (exit 2, message to Claude) when:

1. there are staged or unstaged changes: "Please commit and push";
2. there are untracked files not ignored by `.gitignore`;
3. commit signing is on, `origin/<branch>` exists, and a commit on no remote ref is unsigned or has a committer email other than `noreply@anthropic.com` (GitHub would show it "Unverified"); it prints the exact `git commit --amend --reset-author` or `git rebase --exec` fix;
4. the branch has unpushed commits against `origin/<branch>`, or against `origin/HEAD` when the branch has no remote twin.

So an unattended session can't end its turn cleanly with work only in the VM: the hook sends Claude back to commit and push, which suits "the VM is thrown away". Two consequences: files an agent wants to keep local must be git-ignored (this repo's `.scratch/` is), and a session that must not push has to be told so plainly, because the hook keeps asking. The hook only fires for the main loop's Stop, not for sub-agents (Unverified: inferred from it being a `Stop`, not `SubagentStop`, hook).

The two Python scripts are for "slackbot v2 sessions" (Claude in Slack): a Stop hook that re-prompts an Opus-class model until it posts to the Slack thread, and a UserPromptSubmit reminder. Their docstrings say `environment-manager` registers them only when Slack-specific env vars are set; they aren't registered here [harness].

Verdict: **new.** The old doc said user hooks don't carry over [doc env, "What carries over"], which stays true; these are the platform's own.

## 10. Disk

Commands [probe]: `df -h / /tmp /mnt/user-data`; `mount`; `stat -f /`; `ls -la /mnt/user-data`; `du -sh /tmp`; `touch` in `/opt/claude-code` and `/mnt/user-data/outputs`.

Results:

- `/`, `/tmp` and `/mnt/user-data` are the same ext4 `/dev/vda`: `df` says 252G size, 7.1G used, 30G available. `stat -f /` shows 245G free but 30G available. The mount options are `resv_strict,resuid=65534,resgid=65534`: all but about 30G is reserved for the `nobody` user, so root can write only 30G. The harness prompt says the same: "Writable disk is a fixed per-session allowance, so `df` misleads … deletes still succeed while writes fail" [harness].
- `/tmp` is 72M used and shares that allowance. `/dev/shm` is a 16G tmpfs (RAM-backed).
- Read-only: `/opt/claude-code`, `/opt/env-runner`, `/opt/rclone` (squashfs), `/mnt/skills/public` and `/mnt/skills/examples` (squashfs).
- `/mnt/user-data` exists, writable, with empty `uploads/`, `working/`, `outputs/`; it's `CLAUDE_ADDITIONAL_DIRECTORIES`. `/mnt/attach` is empty.
- `/mnt/skills/public` holds docx, pdf, pptx, xlsx, file-reading, pdf-reading, frontend-design, product-self-knowledge; `/mnt/skills/examples` holds about 35 claude.ai example skills (skill-creator, mcp-builder, chrome-browser, computer-use, deep-research and others). These are claude.ai's shared skill library mounted into the VM; the model's skill list doesn't show them, only the nine synced account skills (Unverified what reads them).

Verdict: "30 GB of disk" **confirmed** as a hard per-session allowance; the `df` trap is **new**.

## 11. Time limits

Command [probe]: `env | grep ^BASH_`, and the same on the `claude` process's environment.

Result: neither `BASH_DEFAULT_TIMEOUT_MS` nor `BASH_MAX_TIMEOUT_MS` is set, so the defaults stand. This sub-agent's Bash tool states "default 120000, max 600000" ms for foreground commands, and up to 2 hours for `run_in_background`.

Verdict: 2 min default, 10 min max **confirmed**; the background limit is **new**.

## 12. How the session is wired

Put together from probes 3, 5, 7, 9 and 10 [probe; harness]:

1. PID 1 is `process_api --firecracker-init` (a Firecracker microVM, `--block-local-connections`, a vsock log port).
2. A boot shell links `claude` and `environment-manager` from read-only volumes, `cd /home/user`, and runs `environment-manager task-run --session <cse_…> --session-mode new --upgrade-claude-code=False`.
3. `environment-manager` clones the repo (shallow, the start branch), creates the `claude/<slug>` branch, writes `~/.claude/launcher-settings.json`, the hooks, `/tmp/mcp-config-<session>.json` and `/tmp/claude-append-system-prompt.txt`, sets up SSH commit signing (`gpg.ssh.program=/tmp/code-sign`), and syncs the account's skills and plugins into `~/.claude/skills/synced/` and `~/.claude/plugins/synced/` (the plugins folder is empty here).
4. It runs `claude` in stream-JSON mode against `api.anthropic.com/v1/code/sessions/<id>`; that process also serves the local HTTPS relay that every tool uses.
5. The appended system prompt has sections "Your current remote execution environment", "Environment configuration", "Disk space", "Pre-installed browser", "GitHub Integration" (attribution footer, PR activity events, driving a PR to green, repository scope), "Git Development Branch Requirements" and "Git Operations" (push with `-u`, retry network failures 4 times with backoff, no PR unless asked, restart a merged branch from the default branch).

`~/.claude/` otherwise holds `projects/`, `sessions/`, `session-env/`, `shell-snapshots/`, an empty `backups/`, and `environment-manager/` (signing helper config).

## Answers to #69's open questions

| Question | Answer | Evidence |
|---|---|---|
| What does the VM actually report (`uname`, `nproc`, `free`, user, `check-tools`)? | Firecracker microVM, Ubuntu 24.04.4, kernel 6.18, 4 vCPU Xeon, 15.7 GiB RAM, no swap, root; 30G writable of a 252G disk; toolchains as documented except `gh` is missing; Playwright and Chromium present | Brief; probes 7 and 10 |
| Does the create form print the session ID or URL, and how? | Yes, at once and non-interactively in effect: `Created cloud session: <title>`, `View: https://claude.ai/code/session_<id>?from=cli&m=0`, `Resume with: claude --teleport session_<id>`; no live checklist was shown | Brief (maintainer's terminal) |
| Did probe 1 create a session? | No. Not testable from this sub-agent; the orchestrating session's `list_sessions` covered every 2026-09-29 session and none came from probe 1 | The orchestrator's own probe, recorded in [cloud-agents-claude-code.md](cloud-agents-claude-code.md#open-questions) |
| Can a cloud session run a headless browser, and on which network level? | Yes, on Trusted, with the pre-installed Chromium; trust the proxy CA's SPKI first; only allowlisted hosts load | Probe 1 |
| Do WebFetch and WebSearch work under Trusted? | WebSearch yes. WebFetch yes for allowlisted hosts, `EGRESS_BLOCKED` for others | Probe 2 |
| Do skills enabled on the claude.ai account load, and does `CLAUDE.md` → `AGENTS.md` load? | Yes to both: nine account skills synced into `~/.claude/skills/synced/`; `AGENTS.md` reached the model through `CLAUDE.md` | Brief; this sub-agent's own context |
| How long is the idle expiry? | Not testable from inside: it needs the session to sit idle and be reopened | None |
| Can a plain cloud session push to a branch named in the prompt? | Yes: a new `skills/…` branch was pushed; the harness prompt asks for "explicit permission" first | Probe 4 |
| Does a plain cloud session send phone push notifications? | Half answered. `PushNotification` is a deferred tool of the main session only (sub-agents lack it). Called from the main loop at the end of this run ("PR ready for review: …"), it returned "Mobile push requested" [probe], so the session hands the push on. Whether it reached the phone needs the maintainer to confirm | Maintainer: check whether the 2026-09-29 "PR ready for review" push arrived (E19) |
| Can a cloud session start another cloud session? | Likely: the VM's `claude` is OAuth-signed-in and has `--cloud`, and the Remote MCP `create_session` tool is present. Not run, by the rules | Probes 5 and 7 |
| Promo credit terms and remaining balance | The session draws on a `ccr_promotional` rate-limit pool whose window resets (`resetsAt`) 2026-11-05 00:00 PST, a reset rather than a refill; Inferred: consistent with the 4 November expiry. Balance not visible from inside | Probe 5 (`get_session`) |
| Does the GitHub proxy allow the REST sub-issue calls? | Yes, `200`, with authenticated access shown by `/user` `200`; GraphQL is fully blocked | Probe 4 |

And the "#69's cloud sessions" TODO in [cloud-agents-delegation.md](cloud-agents-delegation.md): the create form prints a session URL and `--teleport` ID a skill can record (brief); `/orchestrate-with-handoff` doesn't come from the claude.ai account (only Anthropic's nine skills do), and once installed with `npx skills add` it is hidden from the model by `disable-model-invocation` but should be typeable (probe 8); a non-`claude/` branch push works (probe 4); phone push is not testable from inside (probe 5).

## Exploration log

All on 2026-09-29, inside the cloud session's VM, as a sub-agent. No commits.

| # | Where | Command or action | What it changed |
|---|---|---|---|
| 1 | VM | Read the brief, `cloud-agents-claude-code.md`, the delegation TODO | Nothing |
| 2 | VM | `ToolSearch` for the listed tools; read this sub-agent's tool list | Nothing |
| 3 | VM | `free -m`, `env` names, `df`, `mount`, `stat -f /`, `ls /mnt/*`, `ls /opt`, `ls ~/.claude`, `ls /tmp`, `du -sh /tmp`, `touch` tests | An empty file in `/mnt/user-data/outputs`, removed at once |
| 4 | VM | Read `/root/.ccr/README.md`, `launcher-settings.json`, the three hook scripts, section headings and three sections of the appended system prompt | Nothing |
| 5 | VM | Proxy status endpoint; `curl` of `example.com` (headers, verbose, plain HTTP); raw `CONNECT` with `nc` | Nothing |
| 6 | VM | Wrote and ran `.scratch/cloud-session/pw-probe.js`, `pw-probe2.js`, `pw-probe3.js`; `openssl s_client` through the relay; `openssl` SPKI hash of the proxy CA | Scripts and `pw-setcontent.png` in `.scratch/cloud-session/` (git-ignored); Chromium created `~/.pki/nssdb` |
| 7 | VM | `apt-get download libnss3-tools` into `/tmp/pwprobe` | 404, nothing installed; empty `/tmp/pwprobe` left |
| 8 | VM | WebFetch of three URLs, one WebSearch; `grep -a` in the `claude` binary for `EGRESS_BLOCKED`; `/proc` and `/proc/net/tcp` to find the relay's owner | Nothing |
| 9 | VM → GitHub | `git ls-remote origin`, `git fetch origin main`, `git reflog show refs/remotes/origin/<branch>`, GraphQL and REST reads with `curl` (status codes only), `git ls-remote` of a public repo | `origin/main` fetched locally; `/tmp/gql.out` |
| 10 | VM → Anthropic | Remote MCP `get_session` (no ID) and `read_documentation` (index, `session.resources`, `environment.network`) | Nothing; `read_documentation` waited for approval |
| 11 | VM | `git worktree add -b probe/wt-probe …`, `list`, `remove`, `git branch -D probe/wt-probe` | Created and removed a worktree and local branch; nothing pushed |
| 12 | VM | `claude --version`, `claude --help`, `claude auth status` | Nothing |
| 13 | VM | Frontmatter of the 20 installed skills | Nothing |
| 14 | VM | Wrote this file | This file |
| 15 | VM (integration) | Reworded the permission-prompt lines (they waited for approval; who approved isn't recorded); filled the probe 1 row from the orchestrator's `list_sessions` | This file only |
| 16 | VM → GitHub (review) | GraphQL `curl -X POST https://api.github.com/graphql` with a read-only PR query (`repository(owner,name){pullRequest(number:76){title state}}`), status code only | Nothing; `403` with the same "GitHub GraphQL is not available…" message |
| 17 | VM (main session) → Anthropic | `PushNotification` with the "PR ready for review" line, as the orchestrator's done notice | Returned "Mobile push requested"; one notification to the maintainer |
