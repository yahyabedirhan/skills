# Keeping secrets out of agents' reach, beyond rules and hooks

Facts for [Security: Research keeping secrets out of agents' reach beyond rules and hooks (#98)](https://github.com/yahyabedirhan/skills/issues/98), under [Spec: every harness and project is set up and audited from the skills (#49)](https://github.com/yahyabedirhan/skills/issues/49). The rule table and the pre-tool hook refuse the common reads (`cat .env`, `printenv`, `echo $TOKEN`), but nothing pattern-based stops an interpreter (`python3 -c`, `node -e`) or a script that opens `.env`. This page asks what does: keeping the secret out of the environment, an OS sandbox that refuses the read by path, and a way for a project's dev server to get its key without the agent seeing it. It builds on [What each harness can and can't do](harness-capabilities.md) and [Can auto mode block what rules can't?](auto-mode-semantic-guard.md), and leaves the Codex shell snapshot to [#90](https://github.com/yahyabedirhan/skills/issues/90). Researched 2026-10-01; every source below was read that day.

Versions checked: Claude Code 2.1.286, codex-cli 0.159.3, opencode 1.18.34, cursor-agent 2026.09.28-64d2043, macOS 26.5.1. 1Password CLI, direnv, dotenvx and envchain aren't installed here, so they're described from their docs only.

Evidence tags:

- **[doc]** official documentation, linked per section.
- **[src]** official source: `anthropic-experimental/sandbox-runtime` at commit `117eb92`, `openai/codex` at commit `2685e3a`, `anomalyco/opencode` branch `dev` at commit `aa481b8`. All are cloned under `~/Developer/open-source/`.
- **[man]** a man page installed on this Mac (`ps(1)`, `security(1)`), or the Linux man-pages project.
- **[probe]** a command run for this research in a scratch folder, using fake files and a fake variable `ACME_API_TOKEN=probe-not-a-secret`. Each process was started with `env -i`, so no real variable could reach it. Section 5 has the details.
- **To confirm** says what is still open and the exact check that would settle it.

## Short answer

| Question | Answer |
|---|---|
| Keep tokens out of every session's environment | Don't export them from the shell profile. Every harness passes its own environment to the shell it runs: Claude Code, opencode and Cursor pass all of it, and Codex filters by name only when configured, and only with its snapshot off (#90). A secret manager loads a value for one command (`op run`, `envchain`), so it never reaches the agent's environment. |
| Does `op run` protect against the agent? | Only from accidental printing. It masks the secret in its child's stdout and stderr, but `--no-masking` turns that off. CLI authorization is per terminal session and covers sub-shells, so an agent in an authorized session can run `op` itself. The biometric prompt in a new session is the real guard. |
| Can an OS sandbox refuse `.env`, `secrets/`, `~/.ssh` and `~/.aws` by path? | **Claude Code: yes, for Bash only.** `sandbox.filesystem.denyRead` and `sandbox.credentials` are enforced by Seatbelt or bubblewrap for every child process, and Read deny rules are merged into that list. It doesn't cover the file tools, hooks or MCP servers. **Codex: yes,** with a permission-profile `deny` [probe]. **Cursor: partly:** `.cursorignore`d files are refused inside its sandbox, but `~/.ssh` is always readable. **opencode: no sandbox.** |
| Cost | Things that need the home folder, sockets or Apple Events break inside Claude Code's sandbox: git over SSH, `herdr`'s socket, `osascript` notifications, Go-based CLIs such as `gh` (TLS on macOS), `docker` and `watchman`. Each needs `excludedCommands` (not a boundary) or the user. |
| Per-project secrets | The user starts the dev server outside the agent, for example in their own Herdr pane. The app reads the secret at run time from a path the agent's sandbox can't read. On macOS, any same-user process can read another process's **launch** environment, even from inside an approximation of Claude Code's sandbox and inside Codex's own sandbox [probe]. So `op run -- npm run dev` hides the value from the agent's environment but not from `ps -E`. |
| What to configure | Section 6. In short: environment hygiene and an audit line for it now; Claude Code's sandbox with explicit `denyRead` as an opt-in with its costs listed; Codex profiles only if the maintainer leaves `sandbox_mode`; set-up-project audits the new sandbox keys as `weakens`. The maintainer decides. |

---

## 1. The shell environment

### 1.1 What each harness passes to its shell

- **Claude Code** passes its own process environment, and with it whatever the launching terminal exported. "Sandboxed Bash commands inherit the parent process environment by default, including any credentials set there." [doc [sandboxing](https://code.claude.com/docs/en/sandboxing), "Scope"] At session start it also sources `~/.zshrc`, `~/.bashrc` or `~/.profile` and captures "aliases, functions, and shell options"; `CLAUDE_ENV_FILE` runs a script before each command. [doc [tools reference](https://code.claude.com/docs/en/tools-reference), "What persists between commands"; doc [env vars](https://code.claude.com/docs/en/env-vars), `CLAUDE_ENV_FILE`] Hooks inherit the same environment. [doc [hooks](https://code.claude.com/docs/en/hooks)] Three controls remove variables:
  - `sandbox.credentials.envVars` with `"mode": "deny"` unsets a named variable before each **sandboxed** command. `"mask"` swaps in a sentinel, and the sandbox proxy puts the real value back on requests to `injectHosts`. Masking needs `network.tlsTerminate`, and is honoured only from user, managed or `--settings`. "There is no built-in credential deny list, so only the files and variables you list are restricted." [doc sandboxing, "Protect credentials", "Mask credentials"] In the runtime, deny is an `env -u NAME` in front of the command. [src sandbox-runtime `src/sandbox/macos-sandbox-utils.ts`]
  - `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` strips credentials from the Bash tool, hooks and stdio MCP servers. It covers "Anthropic and cloud provider credentials, any other variable that Claude Code recognizes as a credential, and credentials embedded in package registry URLs", not every secret by name. On Linux it also runs Bash in its own PID namespace, "so they cannot read host process environments". [doc env vars, `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`] It turns the sandbox's auto-allow off and locks filesystem isolation on. [doc [settings reference](https://code.claude.com/docs/en/settings-reference), `sandbox.autoAllowBashIfSandboxed`; doc sandboxing, "Which settings can disable it"]
  - Claude Code always removes the `OTEL_*` exporter variables from every subprocess. [doc hooks]
- **Codex:** `shell_environment_policy` filters by name, but in 0.157.1 the shell snapshot restored filtered variables, and only `--disable shell_snapshot` removed them ([auto-mode-semantic-guard 2.4, 5](auto-mode-semantic-guard.md#24-the-deterministic-alternative-filter-the-shell-environment)). Whether the config key `features.shell_snapshot = false` does the same is #90's QA and isn't repeated here. `shell_snapshot` is still `Stable`, on by default, in the current source. [src codex `codex-rs/features/src/lib.rs`]
- **opencode** spreads `process.env` and then a `shell.env` plugin's `output.env` into every shell command. A plugin can set a name to `""` but can't delete it. [src opencode `packages/opencode/src/tool/shell.ts` `shellEnv`]
- **Cursor:** the docs list only the variables the sandbox adds (`CURSOR_SANDBOX`, `CURSOR_ORIG_UID`, `CURSOR_ORIG_GID`, and on Linux `CURSOR_SANDBOX_LANDLOCK_STATUS`). Nothing says any variable is removed. [doc [run modes](https://cursor.com/docs/agent/security/run-modes.md), "Environment variables"]

**So the cause is the profile.** A token exported from `~/.zshrc` reaches every terminal, every Herdr pane, every agent started there, and every shell and hook that agent spawns. Each harness control above is a name filter on top of that. The only complete fix is not exporting the token.

### 1.2 Loading a value for one command

- **1Password `op run`** resolves `op://vault/item/field` secret references, from the environment or from `--env-file`, and runs the command "in a subprocess with the secrets made available as environment variables only for the duration of the process". [doc [load secrets into the environment](https://developer.1password.com/docs/cli/secrets-environment-variables/)] The references are not secrets, so a file of them can be committed. [doc same page, "Map secret references"]
  - **Masking:** "Secrets printed to stdout or stderr are concealed by default. Include the `--no-masking` flag to turn off masking." [doc [`op run` reference](https://developer.1password.com/docs/cli/reference/commands/run/)] It protects a transcript from an accidental `printenv`, but not from an agent that adds `--no-masking`. The docs don't say whether it catches a value that has been transformed, for example base64-encoded.
  - **Authorization:** with the desktop-app integration, each new terminal window or tab asks for Touch ID. The grant lasts 10 minutes, refreshes on each use, and ends after 12 hours or when the app locks. On macOS and Linux "authorization is confined to a terminal session but extends to sub-shell processes in that window", identified by the `tty` and its start time. [doc [app integration security](https://developer.1password.com/docs/cli/app-integration-security/)] So an agent running in a terminal the user has authorized may be able to run `op read` or `op run --no-masking` without a prompt. In a fresh session it triggers a biometric prompt, and the user is the guard. **To confirm** whether a Claude Code Bash call, which may have no `tty`, inherits a Herdr pane's authorization (check 4).
  - **Scope:** 1Password recommends a service account scoped to specific vaults, "so that processes in your authorized terminal session can only access secrets required". It warns: "assume that processes on your computer can access the environment of other processes run by the same user." [doc load secrets into the environment; doc `op run` reference]
- **macOS Keychain (`security`):** "By default, the application which creates an item is trusted to access its data without warning. You can remove this default access by explicitly specifying an empty app pathname: `-T ""`." `-A` lets any application read it. [man `security(1)`, `add-generic-password`] So an item added with `security add-generic-password` and no `-T` trusts `/usr/bin/security`. Any same-user process, an agent included, can then run `security find-generic-password -w -s <service>` and read it with no prompt. With `-T ""`, each read asks. **To confirm** what a sandboxed command can reach: the sandbox runtime's macOS profile allows the `com.apple.SecurityServer` and `com.apple.securityd.xpc` Mach services [src sandbox-runtime `macos-sandbox-utils.ts`] (check 5).
- **envchain** keeps variables in the Keychain (or the D-Bus secret service) per namespace and sets them only for `envchain <ns> <cmd>`. `--require-passphrase` asks for the keychain passphrase every time. [doc [sorah/envchain README](https://github.com/sorah/envchain)] It has the same trust model as `security`, unless the passphrase is required.
- **direnv** does the opposite of what's needed here. It loads `.envrc` exports into the interactive shell whenever you enter the folder [doc [direnv.net](https://direnv.net/)], so an agent started in that folder inherits them.
- **dotenvx** wasn't researched past its docs index. It encrypts `.env` with a key kept beside it in `.env.keys`, which would need the same path deny as `.env`.

---

## 2. OS-level sandboxing

### 2.1 Claude Code

Sources: [sandboxing](https://code.claude.com/docs/en/sandboxing), [settings reference](https://code.claude.com/docs/en/settings-reference) (`sandbox.*`, `permissions.blockReadsOutsideWorkingDirectories`), [permissions](https://code.claude.com/docs/en/permissions), [sandbox environments](https://code.claude.com/docs/en/sandbox-environments).

- **Mechanism:** Seatbelt on macOS, with nothing to install, and bubblewrap plus `socat` on Linux and WSL2. The same primitives ship as `@anthropic-ai/sandbox-runtime`. `sandbox.enabled` defaults to `false`. If the sandbox can't start, commands run unsandboxed with a warning unless `failIfUnavailable` is set. [doc sandboxing]
- **What it covers:** "Bash commands and their child processes" (the permissions page adds PowerShell and Monitor). The file tools use permission rules instead. Hook commands "run unsandboxed". MCP servers aren't in it. Subagents share the parent's sandbox. To put the file tools, hooks and MCP servers inside one boundary, run the whole `claude` process under the sandbox runtime, a dev container or a VM. [doc sandboxing, "Scope"; doc permissions; doc hooks, `DirectoryAdded`; doc sandbox environments]
- **Read is open by default:** "Default read behavior: read access to the entire computer … this default still allows reading credential files such as `~/.aws/credentials` and `~/.ssh/`." Writes are limited to the working directory and the session temp folder. [doc sandboxing, "Filesystem isolation"]
- **Refusing a path:**
  - `sandbox.filesystem.denyRead` takes `/abs`, `~/` and `./` paths. Wildcards work for reads on every platform, and a trailing `/**` is stripped. In **user** settings, `./` resolves to `~/.claude`, not the project. When rules overlap, "the more specific path wins", and a deny holds inside a broader `allowRead`. On Linux a wildcard read entry is expanded to concrete paths when the sandbox starts. [doc settings reference, `sandbox.filesystem`, "Sandbox path prefixes"; doc sandboxing, "Configure sandboxing"]
  - **Read deny rules are merged in:** "Claude Code adds your permission rules to the same lists: `Edit` allow and deny rules to `allowWrite` and `denyWrite`, `Read` deny rules to `denyRead`." [doc settings reference, `sandbox.filesystem`] So with the sandbox on, set-up-machine's `Read(./**/.env)`, `Read(~/.ssh/**)`, `Read(~/.aws/**)` and `Read(./**/secrets/**)` would also bind interpreters. **To confirm** how `./**/.env` from user settings resolves in the merge, since Read rules read `./` as the current directory but sandbox paths read it as `~/.claude`. `/sandbox`'s Config tab shows the resolved list (check 1).
  - `sandbox.credentials.files` with `"mode": "deny"` does the same for named files. Deny entries merge across scopes, and "no scope can remove one that another scope added". [doc sandboxing, "Protect credentials"]
  - `permissions.blockReadsOutsideWorkingDirectories: true` goes further. With the sandbox on, sandboxed commands lose read access to the home folder and `/Users`, `/home` and the other user roots. The working directories, Claude Code's worktrees, the temp folder, the parts of `~/.claude` that commands need, and the git config files are re-opened; `~/.git-credentials` stays blocked. A `true` in any file applies, and a repository "can't lift yours". [doc settings reference, `permissions.blockReadsOutsideWorkingDirectories`, "Sandboxed commands under the block"]
- **What I verified locally:** a hand-written Seatbelt profile denying a fake file and a fake folder by path refused `cat`, `ls`, `python3 open()` and a `sh -c` wrapper with `Operation not permitted`, while the same reads worked outside it [probe, 5.1]. The Seatbelt mechanism holds against interpreters. Claude Code's own generated profile wasn't run (check 1).
- **Escape hatches:**
  - `dangerouslyDisableSandbox`: after a sandbox failure, Claude may retry the command unsandboxed. The retry goes through the normal permission flow: a prompt, or the classifier in auto mode. `allowUnsandboxedCommands: false` ignores the parameter ("Strict sandbox mode"). [doc sandboxing, "The unsandboxed retry escape hatch"]
  - `excludedCommands` run outside the sandbox. "Exclusion is a convenience, not a security boundary." Entries merge from every scope, project included, with no managed-only lock. A call stays sandboxed if it has `cd`, a redirect, a subshell, `$(…)` or `sudo`. [doc settings reference, `sandbox.excludedCommands`]
  - `filesystem.disabled` can't be set from project settings. [doc sandboxing]
  - `allowAppleEvents` "removes code-execution isolation". [doc sandboxing, "Security limitations"]
- **Auto-allow:** `autoAllowBashIfSandboxed` defaults to `true`. Sandboxed commands then run without a prompt, but deny rules and content-scoped ask rules still apply. [doc settings reference]
- **What a project can do:** the array keys (`allowRead`, `allowWrite`, `excludedCommands`) merge from every scope. Because the more specific path wins, a project `allowRead` narrower than a user `denyRead` could re-open it; only managed `allowManagedReadPathsOnly` prevents that. [doc sandboxing, "Keep developers from widening the policy"] `sandbox.enabled` is listed with scope "Any file". **To confirm** whether a project's `false` beats a user's `true` (check 7).
- **Unix sockets:** sockets are blocked unless listed in `network.allowUnixSockets` (macOS paths) or opened with `allowAllUnixSockets`. [doc settings reference, `sandbox.network.allowUnixSockets`] The runtime's comment names "SSH agent, Docker, Gradle". [src sandbox-runtime `macos-sandbox-utils.ts`]
- **Network:** a proxy outside the sandbox enforces a domain allowlist and prompts for each new domain. It doesn't inspect TLS by default, so domain fronting is possible. [doc sandboxing, "Network isolation", "Security limitations"]
- **What breaks** (documented): `watchman` (use `jest --no-watchman`), `docker`, Go-based CLIs (`gh`, `gcloud`, `terraform`, which fail TLS verification on macOS), `open`/`osascript` and browser auth (error `-600`), git commands replacing protected files, and nested bubblewrap in unprivileged containers. "Performance overhead: minimal." [doc sandboxing, "Troubleshooting", "Limitations"] What follows for this setup is inferred, not run:
  - `git push` over SSH needs `~/.ssh` and the agent socket, so it fails with `~/.ssh` denied unless the command is excluded or the user runs it.
  - `herdr` talks over a socket, so it fails without an `allowUnixSockets` entry.
  - The notification command (`osascript`) fails without `allowAppleEvents` or an exclusion.
  - `gh` would need an exclusion.

  Check 3 confirms these.

### 2.2 Codex

Sources: [permissions](https://learn.chatgpt.com/docs/permissions), [sandbox](https://learn.chatgpt.com/docs/sandboxing).

- Seatbelt on macOS; bubblewrap and seccomp on Linux. "If the selected policy cannot be enforced by the platform sandbox, Codex refuses to run the command instead of silently running it unsandboxed." [doc permissions, "How enforcement works"] The base profile is `(deny default)`. [src codex `codex-rs/sandboxing/src/seatbelt_base_policy.sbpl`]
- **Permission profiles (beta)** map paths to `read`, `write` or `deny`. A `deny` covers reads and writes, beats an equally specific grant, and works for `~/path`, absolute paths and `:workspace_roots` globs (`"**/*.env" = "deny"`). On Linux, an unbounded `**` needs `glob_scan_max_depth`. [doc permissions, "Filesystem permissions", "Deny reads with exact paths or globs"]
- **Verified** with `codex sandbox` and a scratch `CODEX_HOME`: under the default policy, a fake file was readable. A profile extending `:workspace` with two absolute `deny` entries refused `cat` and `python3 open()` on both, while writes in the folder still worked. [probe, 5.2]
- **Limits:**
  - Profiles "do not compose with the older sandbox settings": any `sandbox_mode` in a loaded config file, or `--sandbox`, makes Codex use the old settings and ignore `default_permissions`. [doc permissions] set-up-machine's declared Codex defaults (decision 2026-10-01) include `sandbox_mode`, so the two conflict.
  - Profiles govern sandboxed commands only. A command a rule `allow`s runs outside the sandbox [harness-capabilities 2.6], and that includes the `allow-and-report` rows.
  - MCP servers, connectors and web search use their own controls. [doc permissions, "Scope and enforcement"]
  - A trusted project's `.codex/config.toml` can change the sandbox [harness-capabilities 2.5].

### 2.3 Cursor

Sources: [sandbox.json](https://cursor.com/docs/reference/sandbox.md), [run modes](https://cursor.com/docs/agent/security/run-modes.md), [ignore files](https://cursor.com/help/customization/ignore-files.md), [engineering post](https://cursor.com/blog/agent-sandboxing) (2026-02-18).

- Seatbelt on macOS; Landlock and seccomp on Linux. `sandbox.json` (`~/.cursor/` and `<project>/.cursor/`, merged) has `type`, extra read and write paths and `networkPolicy`, but **no read-deny list**. "SSL certificate paths and `~/.ssh` are always readable." A project file can set `"type": "insecure_none"`. [doc sandbox.json]
- **`.cursorignore` feeds the sandbox:** the macOS policy is generated "based on workspace-level and admin-level settings, along with the user's .cursorignore". On Linux, ignored files are overlaid with Landlocked copies "that can't be read or modified". [doc engineering post, "macOS", "Linux"] The help page still says terminal commands "may still be able to read ignored files". [doc ignore files] That's true outside the sandbox. **To confirm** for the CLI, and whether the default ignore list (which includes `.env`) is enforced too (check 6).
- The CLI has `--sandbox enabled|disabled`. [bin `cursor-agent --help`]

### 2.4 opencode

- No OS sandbox: the source has no Seatbelt, bubblewrap or Landlock call. [src opencode `packages/opencode/src`; harness-capabilities 3.6] The only option is wrapping the whole `opencode` process in the sandbox runtime or a container.

---

## 3. Per-project secrets

A project's dev server needs an API key. Who starts the server, and how the key reaches it, decides what the agent can see.

| Route | Value in the agent's environment | Agent can read the file | Agent can read the server's environment |
|---|---|---|---|
| Key exported in the shell profile | yes | — | yes |
| Plain `.env` in the project, gitignored | no | yes, unless the sandbox denies it (the hook catches `cat`, not `python3`) | after dotenv loads, no (see below) |
| Agent runs `op run --env-file=<refs> -- npm run dev` | no, but the agent controls `op` and can add `--no-masking` | references only | yes, on macOS (launch environment) |
| **User** runs `op run --env-file=<refs> -- npm run dev` in their own pane | no | references only | **yes, on macOS** [probe]; on Linux, not from Claude Code's sandbox (PID namespace) |
| User starts the server; the app reads the key at run time from a path the sandbox denies (a 1Password-mounted `.env`, or `secrets/…`) | no | no (sandbox) | no: a value set after launch isn't in the launch environment [probe] |

Why the last two rows differ:

- **macOS exposes a process's launch environment to the same user.** `ps -E` displays "the environment as well. This does not reflect changes in the environment after process launch." [man `ps(1)`] On this Mac, `ps -E` and a direct `sysctl(KERN_PROCARGS2)` read a fake variable from a same-user process. They also read it from inside a `(deny default)` Seatbelt profile modelled on the sandbox runtime's (`process-info*` limited to the same sandbox, its `sysctl` allowlist), and from inside Codex's real sandbox. `/bin/ps` itself couldn't run there (it's setuid), but `python3` could make the call. [probe, 5.3] One exception was observed and isn't explained by any doc: Apple's `/bin/sleep` showed no environment to `ps -E` even outside a sandbox. **To confirm** under Claude Code's own sandbox (check 2).
- **Linux:** `/proc/pid/environ` holds "the initial environment … If, after an execve(2), the process modifies its environment … this file will not reflect those changes". Access is a `PTRACE_MODE_READ_FSCREDS` check. [man [proc_pid_environ(5)](https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html)] Claude Code's bubblewrap sandbox runs with `--unshare-pid` and a fresh `/proc`, so host processes aren't visible. [src sandbox-runtime `src/sandbox/linux-sandbox-utils.ts`] `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` does the same for Bash on Linux. [doc env vars] `enableWeakerNestedSandbox` gives that up. [doc sandboxing, "Troubleshooting"]
- **A value set after launch stays out of both:** a process started without the variable that sets it at run time (as dotenv libraries do) didn't show it to `KERN_PROCARGS2`. [probe, 5.3]
- **1Password-mounted `.env` files** serve the Environment through a named pipe after an authorization prompt, but "There's no distinction made between different processes reading the file. Once the file is unlocked, every process can read it until you lock 1Password". [doc [local .env files](https://developer.1password.com/docs/environments/local-env-file/)] They keep plaintext off the disk. They keep it from the agent only if the path is also in the sandbox's `denyRead`.
- **What none of this covers:** the agent can still call the running server's endpoints, read its logs, or print a key the app echoes. Reading another process's memory isn't covered here.

---

## 4. Comparison

| | Claude Code | Codex | opencode | Cursor |
|---|---|---|---|---|
| Shell gets | the launch environment; sandbox `credentials.envVars` deny/mask; `SUBPROCESS_ENV_SCRUB` for recognised credentials | the environment through `shell_environment_policy`, restored by the snapshot (#90) | `process.env` plus `shell.env` plugin output | the launch environment plus `CURSOR_*` |
| OS sandbox | Seatbelt / bubblewrap, off by default | Seatbelt / bubblewrap, on by default (`workspace-write`) | none | Seatbelt / Landlock |
| Default reads | whole disk | whole disk [probe] | — | workspace plus system; `~/.ssh` always |
| Deny a read by path | `denyRead`, `credentials.files`, Read deny rules merged | profile `deny` (not with `sandbox_mode`) | — | `.cursorignore` (to confirm for the CLI) |
| Covers | Bash, PowerShell, Monitor | sandboxed commands, not rule-allowed ones | — | sandboxed shell commands |
| Not covered | file tools (rules), hooks, MCP | MCP, connectors, rule-allowed commands | everything | MCP, unsandboxed commands |
| Unsandboxed retry | `dangerouslyDisableSandbox`, off with `allowUnsandboxedCommands: false` | approval escalation | — | approval prompt |
| A project can widen it | `allowRead`, `excludedCommands`; `enabled` to confirm | trusted `.codex/config.toml` | — | `.cursor/sandbox.json` (`insecure_none`) |
| Same-user process environments (macOS) | readable [probe, approximation] | readable [probe] | readable | not checked |

---

## 5. Probes

All runs used a scratch folder under the session scratchpad and processes started with `env -i PATH=/usr/bin:/bin ACME_API_TOKEN=probe-not-a-secret`. The pre-tool hook refused writing a fake `.env` and `secrets/key.txt` even in the scratch folder (rules `env-files-write`, `secret-files-write`), so the probes used neutral names, `fake-config.txt` and `fenced/value.txt`. Path denial doesn't depend on the name.

### 5.1 Seatbelt read deny (`sandbox-exec`, throwaway profile)

Profile: `(allow default)` plus `(deny file-read* (literal ".../fake-config.txt") (subpath ".../fenced"))`.

| Command inside | Result |
|---|---|
| `cat fake-config.txt` | `Operation not permitted` |
| `python3 -c 'open("fake-config.txt").read()'` | `PermissionError: [Errno 1] Operation not permitted` |
| `sh -c 'cat fenced/value.txt; ls fenced; python3 …'` | all three refused |
| `cat fake-config.txt` without the sandbox | prints the fake line |

### 5.2 Codex's own sandbox (`codex sandbox`, scratch `CODEX_HOME`, user config untouched)

| Policy | `cat` / `python3` on the fake files | Write in folder | Other process's launch environment |
|---|---|---|---|
| default | readable | — | read |
| `-c default_permissions="probe" -c permissions.probe.extends=":workspace" -c permissions.probe.filesystem={"<abs>/fenced"="deny","<abs>/fake-config.txt"="deny"}` | refused | allowed | read |

### 5.3 Reading a same-user process's environment (macOS)

Target: a `python3` process sleeping, started with `env -i … ACME_API_TOKEN=probe-not-a-secret`. Reader: `ps -E`, and a `python3` script calling `sysctl(CTL_KERN, KERN_PROCARGS2, pid)` that prints only `ACME_*` entries.

| Reader runs | Result |
|---|---|
| unsandboxed, `ps -E` / `ps eww` | the fake variable |
| `(allow default)` with `process-info*` limited to the same sandbox | the fake variable (python) |
| `(deny default)` approximating the sandbox runtime's macOS profile (process, Mach, `sysctl` allowlists copied from `macos-sandbox-utils.ts`; enforcing: a write and a network connect were refused) | the fake variable (python); `/bin/ps` refused to execute |
| Codex's default sandbox | the fake variable |
| target set the variable **after** launch (`os.environ[...] = …`) | nothing |
| target was Apple's `/bin/sleep` | nothing, even unsandboxed (not explained by any doc) |

---

## 6. Recommendation

> **Decided 2026-10-01:** rules and the hook only, with the gap accepted, plus two more file rows. 1Password, the sandbox and the Codex profile were dropped. See [the decision record](../decisions/set-up-machine.md#2026-10-01-secrets-stay-behind-rules-with-the-gap-accepted-98).

The maintainer decides. The maintainer's projects hold no secrets in the environment today (#98), so everything here is preparation. Each option lists its cost.

### 6.1 set-up-machine

1. **Environment hygiene (recommended, no cost):**
   - Keep tokens out of shell profiles, and load them per command with `op run`, `envchain`, or a Keychain item made with `-T ""`. This belongs in the personal workflow or a reference, not the rule table.
   - Optionally, an audit line that lists the **names** (never values) of exported variables matching the hook's secret globs (`*TOKEN*`, `*KEY*`, `*SECRET*`, `*PASSWORD*`, `*PASSWD*`, `*CREDENTIAL*`). The audit reads names from its own process environment, which is what every harness would inherit, and reports a `gap` for each. Cost: it reads the environment's keys, so the maintainer should decide whether that fits the "never read secret environment variables" rule.
2. **Claude Code sandbox as an opt-in (strongest option, real cost).** Write to `~/.claude/settings.json`:

   ```json
   {
     "sandbox": {
       "enabled": true,
       "allowUnsandboxedCommands": false,
       "filesystem": {
         "denyRead": ["~/.ssh", "~/.aws", "~/**/.env", "~/**/.env.*", "~/**/secrets"]
       }
     }
   }
   ```

   - **Why explicit paths:** `./` in user settings means `~/.claude`, so the project-relative Read rules may not carry over (check 1). `~/**/.env` is the docs' own example.
   - **What it adds:** an interpreter or script that opens `.env`, `secrets/`, `~/.ssh` or `~/.aws` is refused by the OS, which closes the gap the decision of 2026-09-30 left open.
   - **Costs:**
     - `.env.example` falls under `~/**/.env.*`. An `allowRead` for it is more specific, so it should re-open it, but that's unconfirmed.
     - Git over SSH, `herdr`, `osascript`, `gh`, `docker` and `watchman` need `excludedCommands`, `allowUnixSockets` entries or the user, as listed in 2.1. Each exclusion is a hole, and a project can add more.
     - On Linux each wildcard is expanded at start-up.
     - With `allowUnsandboxedCommands: false`, a blocked command can't be retried, so the user runs it.
     - Network prompts for each new domain.
   - **Variant:** `permissions.blockReadsOutsideWorkingDirectories: true` instead of the home-folder entries. It fences the whole home folder for both the file tools and sandboxed commands, at the cost of every read outside the project. Whether skills under `~/.agents/skills` stay readable is check 9.
   - **Not recommended alone:** `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`. It strips only recognised credentials, and it turns sandbox auto-allow off.
   - On a VPS, `remote-machine.md` already proposes the sandbox. Linux adds the PID-namespace protection of section 3.
3. **Codex: only after #90, and only if the maintainer moves off `sandbox_mode`.** A profile extending `:workspace` with `"~/.ssh" = "deny"`, `"~/.aws" = "deny"` and `:workspace_roots` `"**/.env" = "deny"`, `"**/.env.*" = "deny"`, `"**/secrets" = "deny"` works [probe]. But it can't coexist with the declared `sandbox_mode`, and the decision of 2026-10-01 says to preserve and report rather than migrate. Rule-allowed commands stay outside it.
4. **opencode:** nothing for files. The optional `shell.env` plugin that blanks secret-named variables stays the opencode adapter's decision ([auto-mode-semantic-guard 6.3](auto-mode-semantic-guard.md#63-opencode-nothing-to-configure)).
5. **Cursor:** keep the sandbox on (the default with Auto-review). `~/.ssh` can't be denied. Reads of project secrets rely on `.cursorignore` (check 6).

**Not to do:**

- export tokens from the profile;
- add Keychain items without `-T ""`;
- treat `op run` masking, `excludedCommands` or Cursor Auto-review as a boundary;
- set `allowAllUnixSockets` or `allowAppleEvents` to make tools work;
- use a 1Password-mounted `.env` as an agent guard without a `denyRead` on its path.

### 6.2 set-up-project

1. **References, not values (recommended where a project needs a key):** commit a file of `op://` references for `op run --env-file`. The hook's rows deny `.env` and `.env.*` other than `.env.example`, `.env.sample` and `.env.template`. A references-only `.env.template` stays readable, which is harmless, and documents the variable names. The real values never sit in the folder. Cost: every developer needs 1Password and the vault.
2. **The user starts the dev server, not the agent:** in their own terminal or Herdr pane, with `op run`, or with the app reading a sandbox-denied path at run time. The agent never holds the key. On macOS, prefer the run-time read: an `op run` launch environment is visible to any same-user process (section 3).
3. **Audit the new keys as `weakens`** in `references/project-files.md`, if 6.1.2 is adopted:
   - **Claude Code:** `sandbox.enabled: false`, `sandbox.filesystem.allowRead`, broad `excludedCommands`, `network.allowUnixSockets` / `allowAllUnixSockets`, and `permissions.blockReadsOutsideWorkingDirectories: false` (the last is harmless: any `true` wins).
   - **Cursor:** `.cursor/sandbox.json` `"type": "insecure_none"`, and a `.cursorignore` that drops `.env` or `secrets/`.
   - **Codex:** trusted `.codex/config.toml` `sandbox_mode = "danger-full-access"` or a `default_permissions` change.
4. **Optionally add project paths:** a project with its own secret locations can add them to `.claude/settings.json` `sandbox.filesystem.denyRead` and to `.cursorignore`. Deny entries only narrow.

**Not to do:**

- let the agent start a dev server through `op run`: it controls `op` and can unmask;
- keep plaintext keys in a gitignored `.env` without the sandbox: `python3` reads it past the hook.

---

## 7. Checks for the maintainer

Each needs a live session or a human at the Mac, and may become a QA issue. Use fake files and `probe-not-a-secret` values only, in a throwaway folder.

1. **Claude Code sandbox merge:**
   - Turn the sandbox on for one session (`claude --settings <file with sandbox.enabled true>`) and open `/sandbox` → Config. Do the existing `Read(./**/.env)`, `Read(~/.ssh/**)` and `Read(./**/secrets/**)` rules appear under denied reads, and resolved where?
   - Then ask for `python3 -c 'print(open("<fake env>").read())'`. Is it refused by the OS?
2. **Process environments under Claude Code's sandbox (macOS):** start `env -i ACME_API_TOKEN=probe-not-a-secret python3 -c 'import time; time.sleep(300)'` in another pane. From a sandboxed Bash call, run the `KERN_PROCARGS2` reader from section 5.3 (the `ACME_` filter only). Is the value printed?
3. **What breaks:** with the sandbox and `denyRead` from 6.1.2, try `git push` (SSH remote), `herdr pane list`, the notification command, `gh api rate_limit` and `treehouse` in a session. Note which need `excludedCommands` or socket entries.
4. **1Password authorization reach:** after authorizing `op` in a Herdr pane, start an agent in that pane and ask it to run `op whoami`. Does it prompt for Touch ID?
5. **Keychain from the sandbox:** create a throwaway item with `security add-generic-password -a probe -s probe-item -w probe-not-a-secret` (and one with `-T ""`). Read each from a sandboxed Bash call with `security find-generic-password -w -s probe-item`, then delete both items.
6. **Cursor CLI:** in a throwaway project with `.cursorignore` listing `fenced/`, run `cursor-agent -p --sandbox enabled` and ask it to `cat` and `python3`-read `fenced/value.txt`. Repeat for a fake `.env`, covered only by the default ignore list.
7. **Project override:** with `sandbox.enabled: true` in user settings, does a project `.claude/settings.json` holding `"sandbox": {"enabled": false}` turn it off (`/sandbox` → Config)? Does a project `allowRead` narrower than a user `denyRead` re-open it?
8. **Codex:** #90 is still open; the shell snapshot question isn't answered here.
9. **Skills under the read block:** with `permissions.blockReadsOutsideWorkingDirectories: true` and the sandbox on, can a skill installed under `~/.agents/skills` (linked from `~/.claude/skills`) still be loaded, and can its scripts run?
