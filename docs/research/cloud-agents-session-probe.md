# Inside a Claude Code cloud session: first-hand probes

Facts for [Research: Claude Code cloud sessions tested from inside one (#78)](https://github.com/yahyabedirhan/skills/issues/78), under [Spec: research cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45). This file answers open questions from inside a real cloud session. [Claude Code in the cloud (#69)](cloud-agents-claude-code.md) left some of these questions. The "#69's cloud sessions" TODO in [cloud-agents-delegation.md](cloud-agents-delegation.md) left the others. The probes ran on 2026-09-29. The maintainer started the session from the Mac with `claude --cloud "say hi"`. The VM ran Claude Code 2.1.285 in an Anthropic-hosted environment, on the default **Trusted** network level.

The probes ran in a sub-agent of that session (spawn depth 1). So the tool findings in probe 5 show what a sub-agent sees. These probes created no session, routine, trigger or webhook. They wrote nothing to GitHub and didn't change `~/.claude`.

Evidence tags:

- **[probe]** a command run for this file. The tag gives the exact command and a shortened output.
- **[harness]** a file the harness itself put in the VM. These are `/root/.ccr/README.md` and `/tmp/claude-append-system-prompt.txt` (text added to the end of Claude's system prompt). The hook scripts under `~/.claude/` and the command line of the `claude` process count too.
- **[doc `<page>`, "`<section>`"]** Claude Code's docs at `https://code.claude.com/docs/en/<page>`, as [cloud-agents-claude-code.md](cloud-agents-claude-code.md) cites them.
- **Unverified** marks an inference.

Each verdict compares a finding with the old doc: **confirmed**, **contradicted**, or **new**.

## Short answer

- **Browser: yes, out of the box, with one catch.** Playwright's Chromium 141 is already installed. It starts headless in under a second. It doesn't trust the CA of the egress proxy. So every HTTPS page fails with `ERR_CERT_AUTHORITY_INVALID` until you trust that one CA key (`--ignore-certificate-errors-spki-list=<proxy CA SPKI>`). After that, allowlisted hosts load and blocked hosts fail with `ERR_TUNNEL_CONNECTION_FAILED`. It needs no setup script and no wider network. This contradicts "a headless browser needs at least a setup script, and likely Custom/Full network".
- **WebFetch obeys the allowlist. WebSearch doesn't need it.** WebFetch runs inside the `claude` process of the VM and returns `EGRESS_BLOCKED` for `example.com`. WebSearch works because it runs on the server.
- **Blocked hosts get a plain `403` with no `x-deny-reason` header.** The body names the host. This contradicts [doc routines, "Environments and network access"].
- **The proxy blocks GitHub GraphQL entirely,** not only outside "a pinned set of PR operations". The proxy answers `403`. It points at REST, plus special `…/ccr/…` REST routes for review threads, auto-merge and draft state. REST works for the attached repo, including sub-issues and `/user`. The proxy refuses REST to any other repo, even a public one. `git` reads of other public repos still work.
- **A push to a non-`claude/` branch works.** The orchestrating session created and pushed `skills/cloud-agents-session-probe` (reflog: "update by push"). The harness prompt only asks the model not to push elsewhere "without explicit permission".
- **Sub-agents don't have the Agent tool** (spawn depth 1 holds), `PushNotification`, `ListAgents` or `CronCreate`. They do get `Monitor`, `SendMessage`, `WebFetch`, `WebSearch`, the GitHub MCP tools and the Claude Code Remote MCP tools. The user's permission prompts still apply to these.
- **The three missing skills** carry `disable-model-invocation: true`. So Claude Code hides them from the model, but the user can still type them.
- **The Stop hook** refuses to end a turn while the checkout has uncommitted changes, untracked files, unpushed commits or unsigned commits.
- **Disk:** `df` shows 252G, but only about 30G is writable. The rest is ext4 reserved blocks. `/tmp` is on the same disk. `/mnt/user-data` exists with empty `uploads`, `working` and `outputs` folders.
- **The session bills to a promotional pool** (`rateLimitType: ccr_promotional`). The rate-limit window of this pool resets (`resetsAt`) at 2026-11-05 00:00 PST. This is a window reset, not a refill. Inferred: that date matches the announced 4 November expiry of the promo credit.

## 1. Headless browser

Commands [probe]:

1. `.scratch/cloud-session/pw-probe.js` starts Chromium through `HTTPS_PROXY`, runs `setContent`, takes a screenshot and runs `goto` on two URLs.
2. `pw-probe2.js` compares the headless shell with full Chromium on three hosts.
3. `pw-probe3.js` does the same, plus the SPKI hash of the proxy CA.

Each ran with `node .scratch/cloud-session/pw-probe.js`. `free -m` measured memory before, during and after.

Results:

- `chromium.launch({headless: true, proxy: {server: HTTPS_PROXY}})` started Chromium 141.0.7390.37 in 765 ms. `setContent` rendered the page and ran its script (title `ok-2`). The screenshot saved.
- `goto https://code.claude.com/docs/llms.txt` → `net::ERR_CERT_AUTHORITY_INVALID`. `https://github.com/` and `https://api.github.com/zen` gave the same error. Both the headless shell and full Chromium failed.
- `goto https://example.com` → `net::ERR_TUNNEL_CONNECTION_FAILED` (the proxy answered 403 to CONNECT).
- Cause: the proxy signs TLS again with its own CA, `CCR Upstream Proxy CA (staging)`. Chromium's NSS store at `~/.pki/nssdb` doesn't hold this CA. This first Chromium run created the store. Nothing filled it in advance. The proxy README says the harness sets up "the browser NSS store". It didn't do this for Playwright's Chromium. `certutil` isn't installed. `apt-get download libnss3-tools` got a 404 because the package index was out of date. So the probe couldn't fill the store without an `apt-get update`.
- A fix that keeps verification on:
  1. Compute the SPKI hash of the proxy CA: `openssl x509 -in /root/.ccr/agent-proxy-ca.crt -noout -pubkey | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | base64`.
  2. Start Chromium with `args: ['--ignore-certificate-errors-spki-list=<hash>']`.

  Chromium then trusts only chains through the proxy's key. Results: `code.claude.com/docs/llms.txt` → 200 (`# Claude Code Docs`). `github.com` → 200, but the proxy blocks its asset host `github.githubassets.com`, so pages show without styles. `example.com` → the proxy refused the tunnel.
- Memory: 537 MB used before and 611 MB during, plus about 400 MB of page cache. Use didn't change after. A headless browser costs little on the 15.7 GiB VM.
- The harness prompt says: "Chromium is pre-installed and Playwright is configured to find it (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`; `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1` …). Do not run `playwright install`" [harness]. It also says to use `executablePath: '/opt/pw-browsers/chromium'` if a project pins another Playwright version. `/opt/pw-browsers` holds `chromium-1194`, `chromium_headless_shell-1194`, `ffmpeg-1011` and a `chromium` symlink.

Verdict: **contradicted** ("no browser named … needs at least a setup script, and likely Custom/Full network"). The browser is there. The Trusted network is enough for allowlisted hosts. **New:** the step to trust the CA.

## 2. WebFetch and WebSearch

Commands [probe]: WebFetch `https://code.claude.com/docs/llms.txt`, WebFetch `https://example.com`, WebFetch `https://en.wikipedia.org/wiki/Firecracker_(software)`, and WebSearch "Claude Code cloud sessions". Then `curl -sS "$HTTPS_PROXY/__agentproxy/status"` checked whether the fetches reached the local relay.

Results:

- `code.claude.com` → fetched and summarized.
- `example.com` and `en.wikipedia.org` → error `{"error_type":"EGRESS_BLOCKED","domain":"example.com","message":"Access to example.com is blocked by the network egress proxy."}`.
- WebSearch → nine results (code.claude.com, theregister.com, anthropic.com and others). WebFetch still can't fetch the hosts it returned.
- Where WebFetch runs: in the VM. The `claude` binary builds that exact error (`EgressBlockedError`) when the proxy refuses a CONNECT from its local HTTP client. The WebFetch attempts didn't show up in the relay's `recentRelayFailures`. The `curl` and Playwright attempts did. The `claude` process itself serves the relay, because it owns the listening port. So the CLI's own requests likely skip the relay's log. Unverified which path they take inside the process.
- `platform.claude.com` answered 200 to `curl`, so Trusted can reach it.

Verdict: **new** for both open items. WebFetch follows the allowlist of the environment, because it runs locally, not on the server. WebSearch works in any case. Research on arbitrary pages still needs **Full** or **Custom** network, as the old doc said.

## 3. Network and the proxy

Commands [probe]:

- `curl -sS -D - https://example.com` and `curl -sv https://example.com`.
- A raw `CONNECT example.com:443` to the relay port, to read the body that curl hides.
- `curl -x "$HTTPS_PROXY" http://example.com`.
- The status endpoint above.
- `cat /root/.ccr/README.md`.

Results:

- Blocked host: `HTTP/1.1 403 Forbidden`, headers `Content-Type: text/plain; charset=utf-8`, `X-Content-Type-Options: nosniff`, `Content-Length: 69`, `Connection: close`. Body: `request blocked: no rule or allowlist entry allows host "example.com"`. **No `x-deny-reason` header.**
- Plain HTTP through the relay: `405 Method Not Allowed`, "this proxy only accepts HTTPS CONNECT tunnels".
- Status endpoint:
  - `enabled`, `gitConfigInjection` and `gitSshRewrite` are true, and `javaTrustStorePath` is set.
  - A `noProxy` list holds the Anthropic API and MCP proxy hosts, npm, jsr, PyPI, crates, the Go proxy and private ranges.
  - A ring holds the last 20 relay failures (host, time, "gateway answered 403 to CONNECT").
- `apt-get` reached `security.ubuntu.com` over plain HTTP. It returned 404 for an out-of-date package. So apt has its own route.
- The README [harness], in short:
  - HTTPS goes to a local relay on `127.0.0.1:<port>` (`HTTPS_PROXY`). The relay tunnels to "a policy-enforcing egress proxy".
  - That proxy terminates TLS again, so tools must trust `/root/.ccr/ca-bundle.crt`.
  - The harness sets up CA env vars, the system store, a JVM truststore, Bazel, "the browser NSS store" and gsutil in advance.
  - It lists these failure classes:
    - TLS errors: point the tool at the bundle.
    - 405: old axios or `HTTP_PROXY`.
    - 403/407: a policy denial. "Do not retry or route around it, report the blocked host".
    - Resets in the middle of a transfer: see `recentRelayFailures`.
    - Tools that ignore the proxy: Node's built-in `fetch` needs `NODE_USE_ENV_PROXY=1`, aiohttp needs `trust_env=True`, and Bundler reads only `HTTP_PROXY`.
    - git: the harness rewrites SSH remotes to HTTPS.
    - Docker: containers can't reach the relay. Use `--network host` and copy the CA.
  - Not supported: gRPC or HTTP/2-only APIs, WebSocket upgrades, client mTLS, pinned certificates, HTTPS ports other than 443, and raw TCP databases.
- The `claude` process owns the relay port. The probe found its PID through `/proc/net/tcp`. Its environment carries `CCR_AGENT_PROXY_ENABLED=1` and `CCR_UPSTREAM_PROXY_ENABLED=1` [probe].

Verdict:

- Security proxy **confirmed** [doc env, "Security proxy"].
- `403` **confirmed**.
- `x-deny-reason: host_not_allowed` **contradicted** for this environment. The reason is in the body.
- The WebSocket, gRPC and raw TCP limits are **new**. They matter for tools that drive a machine remotely (Herdr, SSH-like clients).

## 4. GitHub proxy

Commands [probe]:

- `git ls-remote origin` and `git fetch origin main`.
- `curl -X POST https://api.github.com/graphql` with the placeholder token and four queries: `{ viewer { login } }`, an issue title, `projectsV2(first:1){totalCount}` and `subIssues(first:1){totalCount}`.
- In the review pass, a read-only PR query `repository(owner,name){pullRequest(number:76){title state}}`.
- REST `GET /user`, `GET /repos/yahyabedirhan/skills/issues/45/sub_issues`, and `GET /repos/anthropics/claude-code` with and without the token.
- `git ls-remote https://github.com/anthropics/claude-code HEAD`.
- `raw.githubusercontent.com`.

The probes recorded only status codes and error text.

Results:

| Call | Status |
|---|---|
| `git ls-remote origin` | Works: 19 refs, all branches, PR refs |
| `git fetch origin main` | Works. The shallow single-branch clone gained `origin/main` |
| GraphQL, any query (viewer, issue, Projects v2, sub-issues, a read-only PR query on #76) | `403`: "GitHub GraphQL is not available from Claude Code sessions; use the REST API … For review threads, auto-merge, and draft/ready-for-review use the CCR routes on api.github.com: `GET /repos/{owner}/{repo}/pulls/{n}/ccr/review_threads`, `POST …/pulls/{n}/ccr/comments/{comment_id}/resolve` (or `/unresolve`), `PUT` or `DELETE …/pulls/{n}/ccr/auto_merge`, `POST …/pulls/{n}/ccr/ready_for_review`, `POST …/pulls/{n}/ccr/convert_to_draft`" |
| REST `GET /user` (token) | `200`. So the proxy does add a real credential |
| REST sub-issues of #45 | `200` |
| REST `anthropics/claude-code`, with or without token | `403`: "GitHub access to this repository is not enabled for this session. Use add_repo to request access …" |
| `git ls-remote` of `anthropics/claude-code` | Works (public read over git) |
| `raw.githubusercontent.com` | `200` |

The harness prompt repeats the scope: "GitHub access for this session is currently scoped to `yahyabedirhan/skills`" [harness]. The VM's own `--mcp-config` lists only one MCP server, `github`, reached through `api.anthropic.com` [probe]. The Remote, Gmail and Docs connectors arrive another way. Unverified: they likely come through the session's SDK connection.

Pushing: the remote-tracking reflog shows two pushes [probe, `git reflog show refs/remotes/origin/<branch>`]:

- `claude/<slug>` "update by push" at session start.
- `skills/cloud-agents-session-probe` "update by push" at 20:07 UTC. The orchestrating session pushed this new branch outside `claude/`.

`get_session` lists that branch under the session's `outcomes` [probe]. The harness prompt names one "designated branch" (`claude/<slug>`). It says "NEVER push to a different branch without explicit permission" [harness]. This is an instruction to the model, not a proxy rule.

Verdict:

- GraphQL scope **contradicted**. The doc promised "a pinned set of GraphQL operations for pull-request workflows" [doc env, "GitHub proxy"], but none pass here.
- REST sub-issues **confirmed** working. `/user` 200 now shows the access is authenticated.
- Repository scope **confirmed**, and stricter than expected: it covers public repos too, for REST only.
- The doc says a session pushes only to "the session's current working branch". This is **confirmed** if it means the checked-out branch. A push to a new branch name also works.

## 5. Sub-agent tools

Commands [probe]:

- Read this sub-agent's own tool list.
- Run `ToolSearch` with `select:PushNotification,ListAgents,CronCreate,Agent,SendUserFile,Workflow`, plus keyword searches.
- Call the read-only Remote tools `get_session` and `read_documentation`.

The environment sets `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`.

| Tool | Main session (brief, and `get_session`'s tool list) | This sub-agent |
|---|---|---|
| Agent (Task) | Yes | **No**: spawn depth 1 means sub-agents can't start sub-agents |
| PushNotification | Deferred | **No** ("No matching deferred tools found") |
| ListAgents | Deferred | **No** |
| CronCreate | Deferred | **No** |
| SendUserFile, Workflow | Yes | **No** |
| SendMessage | Deferred | Yes (deferred). A sub-agent's message goes out under the parent's address |
| Monitor | Deferred | Yes (deferred) |
| WebFetch, WebSearch | Deferred | Yes (deferred) |
| `mcp__Claude_Code_Remote__*` | Yes | Yes, all of them, loaded at the start |
| `mcp__github__*` | Yes | Yes (deferred) |
| Gmail, Claude Docs, Artifact | Yes | Yes |

The Remote tools work from a sub-agent, but each call goes through a permission prompt. While the `read_documentation` call waited for approval, `get_session` showed the session blocked on "Waiting on permission: `mcp__Claude_Code_Remote__read_documentation`". The call ran afterwards. The record doesn't show who or what approved it. The session was in auto mode at the time. `get_session` also showed these values [probe]:

- `environment_kind: anthropic_cloud` and `origin: claude_code_cli`.
- A tag `config:auto-create-pr:off`.
- `cross_session_inbound: available`.
- Context use against a 1M-token window.
- `rate_limit_info.rateLimitType: ccr_promotional`.

The command line of the `claude` process shows how the harness chooses tools [probe, `/proc/<pid>/cmdline`, IDs redacted]:

- `--tools preset:default,Task,Bash,…,WebFetch,WebSearch,…,Monitor,SendUserFile,REPL,…,ToolSearch`.
- `--allowed-tools` with the same list plus `mcp__github__*`.
- `--settings ~/.claude/launcher-settings.json`.
- `--mcp-config /tmp/mcp-config-<session>.json`.
- `--append-system-prompt-file /tmp/claude-append-system-prompt.txt`.
- `--input-format stream-json --output-format stream-json`.
- An `--sdk-url` / `--resume` pair on `api.anthropic.com/v1/code/sessions/<id>`.

Verdict: subagents "work the same way" [doc cloud] is **confirmed** for one level only. **New:** sub-agents can't nest. The notification tool and the tool that lists other sessions stay with the main session.

## 6. Worktrees

Command [probe]: `git worktree add -b probe/wt-probe .scratch/cloud-session/wt-probe HEAD`, `git worktree list`, `git -C … status -sb`, `git worktree remove .scratch/cloud-session/wt-probe`, `git branch -D probe/wt-probe`.

Result: git created, checked out, listed and removed the worktree, and deleted the branch, all without error. Nothing was pushed.

Verdict: "plain `git worktree` is available" is **confirmed**. So the worktree step of the orchestrating skills works in a cloud VM without treehouse. Herdr is still absent.

## 7. The `claude` CLI inside the VM

Commands [probe]: `claude --version`, `claude --help | grep -iE -A1 'cloud|teleport|remote'` and `claude auth status`. The probe did not run `claude --cloud "<task>"`.

Results:

- Version 2.1.285. Flags: `--cloud [description|session_id|url]`, `--teleport [session]`, `--remote-control [name]`, `--remote-control-session-name-prefix` and `ultrareview`. One flag the old doc doesn't mention: `--environment <environment_id>`, "Create a new cloud session that runs on the given self-hosted environment".
- `claude auth status`: `loggedIn: true`, `authMethod: oauth_token`, `apiProvider: firstParty`.
- `claude` in the VM is `/opt/claude-code/bin/claude`, on a read-only ext4 volume. A symlink into `/opt/node22/bin` appears at boot. `environment-manager task-run` runs it (`/opt/env-runner`, also read-only). PID 1 `/process_api --firecracker-init` starts `environment-manager` [probe, `ps`].

Verdict: **new.** The CLI in the VM is signed in with a claude.ai OAuth token and has `--cloud`. So it looks possible to start another cloud session from inside. Unverified: the brief's rules didn't allow a run. The arguments of PID 1 now **confirm** Firecracker. The brief only inferred it from the kernel name.

## 8. The three skills that didn't show up

Command [probe]: print the frontmatter of `~/.claude/skills/{init-effort,orchestrate-with-handoff,skill-recap}/SKILL.md` (symlinks into `~/.agents/skills/`). Then list the frontmatter keys of every installed skill.

Result: all three, and only those three, have `disable-model-invocation: true` (with `argument-hint`). The other 16 have neither key.

Verdict: **new, explained.** They are slash commands for the user only. Claude Code hides them from the model's skill list by design. A user who types `/orchestrate-with-handoff <path>` in this session should still run it. Unverified here, because a sub-agent can't type a slash command.

## 9. Hooks and launcher settings

Commands [probe]: `cat ~/.claude/stop-hook-git-check.sh`, the docstrings of `stop-hook-reply-gate.py` and `user-prompt-submit-reply-reminder.py`, and `jq` of `~/.claude/launcher-settings.json` with long strings cut.

`launcher-settings.json` [harness] holds `$schema`, one `hooks.Stop` entry (matcher `""`, command `~/.claude/stop-hook-git-check.sh`) and `permissions.allow: ["Skill"]`. The harness passes it with `--settings`.

The Stop hook first checks three cases, in order. It exits 0 and lets the turn end if the hook is already active, the directory isn't a git repo, or there is no remote. Otherwise it blocks the turn (exit 2, with a message to Claude) in these cases:

1. There are staged or unstaged changes: "Please commit and push".
2. There are untracked files that `.gitignore` doesn't ignore.
3. Commit signing is on, `origin/<branch>` exists, and a commit on no remote ref has a problem. The problem is either no signature or a committer email other than `noreply@anthropic.com`. GitHub would show such a commit as "Unverified". The hook prints the exact `git commit --amend --reset-author` or `git rebase --exec` fix.
4. The branch has unpushed commits against `origin/<branch>`. If the branch has no remote twin, the hook compares against `origin/HEAD`.

So an unattended session can't end its turn cleanly while its work exists only in the VM. The hook sends Claude back to commit and push. This suits a VM that the platform throws away. It has two consequences:

- An agent must git-ignore the files it wants to keep local. This repo's `.scratch/` is git-ignored.
- A session that must not push needs a plain instruction, because the hook keeps asking.

The hook fires only for the Stop of the main loop, not for sub-agents. Unverified: this is an inference from the hook type, which is `Stop`, not `SubagentStop`.

The two Python scripts are for "slackbot v2 sessions" (Claude in Slack). One is a Stop hook that prompts an Opus-class model again until it posts to the Slack thread. The other is a UserPromptSubmit reminder. Their docstrings say that `environment-manager` registers them only when Slack-specific env vars are set. They aren't registered here [harness].

Verdict: **new.** The old doc said user hooks don't carry over [doc env, "What carries over"]. That stays true. These hooks belong to the platform.

## 10. Disk

Commands [probe]: `df -h / /tmp /mnt/user-data`, `mount`, `stat -f /`, `ls -la /mnt/user-data`, `du -sh /tmp`, and `touch` in `/opt/claude-code` and `/mnt/user-data/outputs`.

Results:

- `/`, `/tmp` and `/mnt/user-data` are all on the same ext4 `/dev/vda`. `df` reports 252G size, 7.1G used and 30G available. `stat -f /` shows 245G free but 30G available.
- The mount options are `resv_strict,resuid=65534,resgid=65534`. They reserve all but about 30G for the `nobody` user, so root can write only 30G. The harness prompt says the same: "Writable disk is a fixed per-session allowance, so `df` misleads … deletes still succeed while writes fail" [harness].
- `/tmp` uses 72M and shares that allowance. `/dev/shm` is a 16G tmpfs that lives in RAM.
- Read-only: `/opt/claude-code`, `/opt/env-runner`, `/opt/rclone` (squashfs), `/mnt/skills/public` and `/mnt/skills/examples` (squashfs).
- `/mnt/user-data` exists and is writable, with empty `uploads/`, `working/` and `outputs/` folders. It is `CLAUDE_ADDITIONAL_DIRECTORIES`. `/mnt/attach` is empty.
- `/mnt/skills/public` holds docx, pdf, pptx, xlsx, file-reading, pdf-reading, frontend-design and product-self-knowledge.
- `/mnt/skills/examples` holds about 35 claude.ai example skills: skill-creator, mcp-builder, chrome-browser, computer-use, deep-research and others.
- These two folders are claude.ai's shared skill library, mounted into the VM. The model's skill list doesn't show them. It shows only the nine synced account skills. Unverified what reads these folders.

Verdict: "30 GB of disk" is **confirmed** as a hard allowance for each session. The `df` trap is **new**.

## 11. Time limits

Command [probe]: `env | grep ^BASH_`, and the same on the environment of the `claude` process.

Result: neither `BASH_DEFAULT_TIMEOUT_MS` nor `BASH_MAX_TIMEOUT_MS` is set, so the defaults apply. This sub-agent's Bash tool states "default 120000, max 600000" ms for foreground commands. It allows up to 2 hours for `run_in_background`.

Verdict: the 2 min default and 10 min maximum are **confirmed**. The background limit is **new**.

## 12. How the session is wired

This list combines probes 3, 5, 7, 9 and 10 [probe; harness]:

1. PID 1 is `process_api --firecracker-init`: a Firecracker microVM, with `--block-local-connections` and a vsock log port.
2. A boot shell links `claude` and `environment-manager` from read-only volumes and runs `cd /home/user`. Then it runs `environment-manager task-run --session <cse_…> --session-mode new --upgrade-claude-code=False`.
3. `environment-manager` prepares the session:
   - It clones the repo (shallow, the start branch) and creates the `claude/<slug>` branch.
   - It writes `~/.claude/launcher-settings.json`, the hooks, `/tmp/mcp-config-<session>.json` and `/tmp/claude-append-system-prompt.txt`.
   - It sets up SSH commit signing (`gpg.ssh.program=/tmp/code-sign`).
   - It syncs the account's skills and plugins into `~/.claude/skills/synced/` and `~/.claude/plugins/synced/`. The plugins folder is empty here.
4. It runs `claude` in stream-JSON mode against `api.anthropic.com/v1/code/sessions/<id>`. That process also serves the local HTTPS relay that every tool uses.
5. The appended system prompt has these sections:
   - "Your current remote execution environment", "Environment configuration", "Disk space" and "Pre-installed browser".
   - "GitHub Integration": the attribution footer, PR activity events, how to drive a PR to green, and the repository scope.
   - "Git Development Branch Requirements".
   - "Git Operations":
     - Push with `-u`.
     - Retry network failures 4 times with backoff.
     - Open no PR unless asked.
     - Restart a merged branch from the default branch.

Apart from these files, `~/.claude/` holds `projects/`, `sessions/`, `session-env/`, `shell-snapshots/`, an empty `backups/`, and `environment-manager/` (config for the signing helper).

## Answers to #69's open questions

| Question | Answer | Evidence |
|---|---|---|
| What does the VM actually report (`uname`, `nproc`, `free`, user, `check-tools`)? | Firecracker microVM, Ubuntu 24.04.4, kernel 6.18, 4 vCPU Xeon, 15.7 GiB RAM, no swap, root. 30G writable of a 252G disk. Toolchains as documented, except that `gh` is missing. Playwright and Chromium present | Brief; probes 7 and 10 |
| Does the create form print the session ID or URL, and how? | Yes. It prints them at once, and in effect without interaction: `Created cloud session: <title>`, `View: https://claude.ai/code/session_<id>?from=cli&m=0`, `Resume with: claude --teleport session_<id>`. It showed no live checklist | Brief (maintainer's terminal) |
| Did probe 1 create a session? | No. This sub-agent couldn't test it. The orchestrating session's `list_sessions` covered every 2026-09-29 session, and none came from probe 1 | The orchestrator's own probe, recorded in [cloud-agents-claude-code.md](cloud-agents-claude-code.md#open-questions) |
| Can a cloud session run a headless browser, and on which network level? | Yes, on Trusted, with the pre-installed Chromium. Trust the SPKI of the proxy CA first. Only allowlisted hosts load | Probe 1 |
| Do WebFetch and WebSearch work under Trusted? | WebSearch yes. WebFetch yes for allowlisted hosts, `EGRESS_BLOCKED` for others | Probe 2 |
| Do skills enabled on the claude.ai account load, and does `CLAUDE.md` → `AGENTS.md` load? | Yes to both. Nine account skills synced into `~/.claude/skills/synced/`. `AGENTS.md` reached the model through `CLAUDE.md` | Brief; this sub-agent's own context |
| How long is the idle expiry? | Not testable from inside. The test needs the session to sit idle and then reopen | None |
| Can a plain cloud session push to a branch named in the prompt? | Yes. The session pushed a new `skills/…` branch. The harness prompt asks for "explicit permission" first | Probe 4 |
| Does a plain cloud session send phone push notifications? | Half answered. `PushNotification` is a deferred tool of the main session only. Sub-agents don't have it. The main loop called it at the end of this run ("PR ready for review: …"). It returned "Mobile push requested" [probe], so the session passes the push on. The maintainer must confirm whether it reached the phone | Maintainer: check whether the 2026-09-29 "PR ready for review" push arrived (E19) |
| Can a cloud session start another cloud session? | Likely. The VM's `claude` is signed in with OAuth and has `--cloud`. The Remote MCP `create_session` tool is present. Not run, by the rules | Probes 5 and 7 |
| Promo credit terms and remaining balance | The session draws on a `ccr_promotional` rate-limit pool. Its window resets (`resetsAt`) at 2026-11-05 00:00 PST. This is a reset, not a refill. Inferred: this fits the 4 November expiry. The balance isn't visible from inside | Probe 5 (`get_session`) |
| Does the GitHub proxy allow the REST sub-issue calls? | Yes, `200`. `/user` `200` shows authenticated access. The proxy blocks GraphQL fully | Probe 4 |

These findings also answer the "#69's cloud sessions" TODO in [cloud-agents-delegation.md](cloud-agents-delegation.md):

- The create form prints a session URL and a `--teleport` ID that a skill can record (brief).
- `/orchestrate-with-handoff` doesn't come from the claude.ai account. Only Anthropic's nine skills do. After an install with `npx skills add`, `disable-model-invocation` hides it from the model, but the user should be able to type it (probe 8).
- A push to a non-`claude/` branch works (probe 4).
- Phone push is not testable from inside (probe 5).

## Exploration log

All entries are from 2026-09-29, inside the VM of the cloud session, as a sub-agent. No commits.

| # | Where | Command or action | What it changed |
|---|---|---|---|
| 1 | VM | Read the brief, `cloud-agents-claude-code.md`, the delegation TODO | Nothing |
| 2 | VM | `ToolSearch` for the listed tools. Read this sub-agent's tool list | Nothing |
| 3 | VM | `free -m`, `env` names, `df`, `mount`, `stat -f /`, `ls /mnt/*`, `ls /opt`, `ls ~/.claude`, `ls /tmp`, `du -sh /tmp`, `touch` tests | An empty file in `/mnt/user-data/outputs`, removed at once |
| 4 | VM | Read `/root/.ccr/README.md`, `launcher-settings.json`, the three hook scripts, and the section headings and three sections of the appended system prompt | Nothing |
| 5 | VM | Proxy status endpoint. `curl` of `example.com` (headers, verbose, plain HTTP). Raw `CONNECT` with `nc` | Nothing |
| 6 | VM | Wrote and ran `.scratch/cloud-session/pw-probe.js`, `pw-probe2.js`, `pw-probe3.js`. `openssl s_client` through the relay. `openssl` SPKI hash of the proxy CA | Scripts and `pw-setcontent.png` in `.scratch/cloud-session/` (git-ignored). Chromium created `~/.pki/nssdb` |
| 7 | VM | `apt-get download libnss3-tools` into `/tmp/pwprobe` | 404, nothing installed. An empty `/tmp/pwprobe` stays |
| 8 | VM | WebFetch of three URLs, one WebSearch. `grep -a` in the `claude` binary for `EGRESS_BLOCKED`. `/proc` and `/proc/net/tcp` to find the relay's owner | Nothing |
| 9 | VM → GitHub | `git ls-remote origin`, `git fetch origin main`, `git reflog show refs/remotes/origin/<branch>`, GraphQL and REST reads with `curl` (status codes only), `git ls-remote` of a public repo | `origin/main` fetched locally. `/tmp/gql.out` |
| 10 | VM → Anthropic | Remote MCP `get_session` (no ID) and `read_documentation` (index, `session.resources`, `environment.network`) | Nothing. `read_documentation` waited for approval |
| 11 | VM | `git worktree add -b probe/wt-probe …`, `list`, `remove`, `git branch -D probe/wt-probe` | Created and removed a worktree and local branch. Nothing pushed |
| 12 | VM | `claude --version`, `claude --help`, `claude auth status` | Nothing |
| 13 | VM | Frontmatter of the 20 installed skills | Nothing |
| 14 | VM | Wrote this file | This file |
| 15 | VM (integration) | Reworded the permission-prompt lines: the calls waited for approval, and the record doesn't show who approved. Filled the probe 1 row from the orchestrator's `list_sessions` | This file only |
| 16 | VM → GitHub (review) | GraphQL `curl -X POST https://api.github.com/graphql` with a read-only PR query (`repository(owner,name){pullRequest(number:76){title state}}`), status code only | Nothing. `403` with the same "GitHub GraphQL is not available…" message |
| 17 | VM (main session) → Anthropic | `PushNotification` with the "PR ready for review" line, as the orchestrator's done notice | Returned "Mobile push requested". One notification to the maintainer |
