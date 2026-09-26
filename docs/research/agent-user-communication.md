# How a long-running agent reaches the user

> Moved from the job-search vault's `.scratch/skill-improvements/research/` on 2026-09-26. Paths under `tmp/`, `~/.claude/` and the vault point at the user's machine and are not in this repo. The VPS host, user and machine ID are redacted.

Purpose: the facts behind issues [#5](https://github.com/yahyabedirhan/skills/issues/5), [#9](https://github.com/yahyabedirhan/skills/issues/9) and [#18](https://github.com/yahyabedirhan/skills/issues/18): how an orchestrator (Claude Code, Codex where relevant) notifies the user, asks for decisions, and receives values only the user has. Researched on 2026-09-25 against Claude Code 2.1.282, Herdr 0.9.0 and Ghostty 1.3.1 on the user's Mac. Claims marked **unverified** were read in a source but not tested here.

## Notifications

### Mechanisms in Claude Code

| Mechanism | Who triggers it | What it does | Source |
| :-- | :-- | :-- | :-- |
| Built-in notification (`preferredNotifChannel`) | Claude Code, when a task finishes or a permission prompt waits and you "appear to be away" | Writes a terminal escape sequence or a bell | [terminal-config](https://code.claude.com/docs/en/terminal-config#get-a-terminal-bell-or-notification), [settings](https://code.claude.com/docs/en/settings-reference#preferrednotifchannel) |
| `PushNotification` tool | The model, when it decides to | Desktop notification, plus a phone push when Remote Control is connected | [tools-reference](https://code.claude.com/docs/en/tools-reference) |
| Remote Control mobile push | The model (`agentPushNotifEnabled`, "Push when Claude decides") or Claude Code on permission prompts and questions (`inputNeededNotifEnabled`, "Push when actions required") | Push to the Claude phone app, only while Remote Control is connected | [remote-control](https://code.claude.com/docs/en/remote-control#mobile-push-notifications), [settings](https://code.claude.com/docs/en/settings-reference#agentpushnotifenabled) |
| `Notification` hook | The harness, on events such as `permission_prompt`, `idle_prompt`, `elicitation_dialog` | Runs any shell command; runs even with `notifications_disabled` | [hooks](https://code.claude.com/docs/en/hooks#notification) |
| `Stop` hook | The harness, each time the main agent finishes responding | Runs any shell command; input includes `last_assistant_message` and `background_tasks` | [hooks](https://code.claude.com/docs/en/hooks#stop) |

`preferredNotifChannel` values: `auto` (desktop notification in iTerm2, Ghostty and Kitty; bell in Terminal.app only when its audible bell is off; nothing elsewhere), `terminal_bell`, `iterm2`, `iterm2_with_bell`, `kitty`, `ghostty`, `notifications_disabled` ([settings](https://code.claude.com/docs/en/settings-reference#preferrednotifchannel)). The user's `~/.claude/settings.json` sets none, so it is `auto`, and it has `agentPushNotifEnabled: true`.

Presence gating: `PushNotification` skips both the desktop notification and the mobile push when it detects recent keyboard activity or terminal focus; `CLAUDE_CODE_DISABLE_NOTIFICATION_PRESENCE_CHECK=1` turns the local check off ([env-vars](https://code.claude.com/docs/en/env-vars)). `CLAUDE_CLIENT_PRESENCE_FILE` suppresses mobile pushes while a marker file exists ([remote-control](https://code.claude.com/docs/en/remote-control#mobile-push-notifications)). The built-in `permission_prompt` and `idle_prompt` notifications fire only after about 6 s and 60 s without typing ([hooks](https://code.claude.com/docs/en/hooks#notification)).

Terminal escape sequences: Ghostty implements OSC 9 as "show a desktop notification" ([Ghostty OSC 9](https://ghostty.org/docs/vt/osc/9)), and its `desktop-notifications` option (default `true`) lets programs notify "using certain escape sequences such as OSC 9 or OSC 777" (`ghostty +show-config --default --docs`, local 1.3.1). The user's Ghostty config does not change it. iTerm2 needs "Send escape sequence-generated alerts" enabled; tmux needs `set -g allow-passthrough on`, or notifications "never reach the outer terminal" ([terminal-config](https://code.claude.com/docs/en/terminal-config#configure-tmux)).

### Why the built-in tool's message did not arrive under Herdr

Two causes stack (the cause chain is inferred from the sources; not reproduced here, and no notification was sent during this research):

1. **Wrong terminal detected.** A Herdr server keeps the environment it was started with and passes it to every pane, including `TERM_PROGRAM=iTerm.app` and a dead `ITERM_SESSION_ID` when the server was first started from iTerm2. Open bug, Herdr 0.9.0 ([herdr#4104](https://github.com/herdrdev/herdr/issues/4104)). With `auto`, Claude Code then emits the iTerm2 form, not the Ghostty form.
2. **Herdr does not forward notification escapes.** Herdr "swallows bare OSC 9 / OSC 99", has no DCS passthrough envelope like tmux, and its bell relay never flags a backgrounded tab (third-party report in [oh-my-pi#11054](https://github.com/can1357/oh-my-pi/pull/11054); **unverified** against Herdr's own docs, which say nothing on passthrough). So even a correct Ghostty sequence stops at Herdr.

The tool therefore reports "Terminal notification sent" truthfully: it wrote the bytes, and Herdr dropped them. Setting `preferredNotifChannel: "ghostty"` would fix cause 1 but not cause 2 (**unverified**).

### What Herdr offers instead

- `herdr notification show <TITLE> [--body TEXT] [--sound none|done|request]` shows a notification through the user's `[ui.toast]` setting (`herdr notification show --help`, local).
- `[ui.toast] delivery` is `off`, `herdr` (in-app toast), `terminal` (outer terminal, works over SSH) or `system` (the OS notification service); toasts are suppressed for the active tab ([Herdr configuration](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.1/docs/next/website/src/content/docs/configuration.mdx)). The user's `~/.config/herdr/config.toml` has `delivery = "off"` and `[ui.sound] enabled = false`, so today Herdr shows nothing.
- Herdr already tracks agent state: `blocked` means "Herdr recognized an approval or question UI"; `done` means finished and unseen (`herdr --skill`, local). With delivery on, Herdr notifies on these state changes in background workspaces without the model doing anything ([Herdr configuration](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.1/docs/next/website/src/content/docs/configuration.mdx); exact triggers **unverified**).

### Direct macOS routes

- `osascript -e 'display notification "<msg>" with title "Claude Code" sound name "Glass"'` is the command the Claude Code hooks guide itself uses on macOS ([hooks-guide](https://code.claude.com/docs/en/hooks-guide#get-notified-when-claude-needs-input)). It posts as Script Editor; if Script Editor lacks notification permission it fails silently. Tested working by the user on 2026-09-24 (issue [#9](https://github.com/yahyabedirhan/skills/issues/9)). Needs no escape passthrough, so Herdr cannot block it. Mac only: it does nothing on the VPS (`docs/vps.md`).
- `terminal-notifier` is not installed here, and no primary Apple source covers it. Not needed while `osascript` works.

### Recommendation

1. **The model notifies at the two moments; a command does the delivery.** "Done" and "blocked" are judgments about the effort (PR delivered, every remaining ticket waits on the user), which no hook can see: `Stop` fires after every turn and `idle_prompt` after any 60 s idle. So the skill tells the orchestrator when to notify, as issue [#9](https://github.com/yahyabedirhan/skills/issues/9) says.
2. **Delivery order:** on macOS with `HERDR_ENV=1`, run `osascript` (proven). Otherwise call `PushNotification`. Where neither exists (VPS without Remote Control), skip silently. Once the user turns on Herdr toasts, `herdr notification show` becomes the Herdr-wide route that also works for the VPS via `--remote` (`terminal` delivery over SSH, **unverified**).
3. **Config-level safety net, optional:** a `Notification` hook with matcher `permission_prompt|elicitation_dialog` running the same `osascript` covers the moments a question or permission dialog sits unanswered, independent of the model. Or set Herdr `[ui.toast] delivery = "system"`, which covers `blocked` and `done` for every agent in Herdr. Either is a settings change for the user to make, not a skill rule. Avoid a `Stop` hook for "done": it fires on every turn.

## Asking questions

### Tools

**Claude Code `AskUserQuestion`.**
- Shape: 1 to 4 questions per call, 2 to 4 options each; each question has `question`, a `header` of at most 12 characters, `options` with `label` and `description`, and `multiSelect` ([Agent SDK user input](https://code.claude.com/docs/en/agent-sdk/user-input#question-format), [hooks](https://code.claude.com/docs/en/hooks#askuserquestion)). The user can always type free text through `Other` or the notes field ([tools-reference](https://code.claude.com/docs/en/tools-reference#askuserquestion-tool-behavior)).
- Previews: options can carry a `preview` (Markdown ASCII art or an HTML fragment). The SDK documents this as a TypeScript option, `toolConfig.askUserQuestion.previewFormat` ([SDK](https://code.claude.com/docs/en/agent-sdk/user-input#option-previews-typescript)); the CLI changelog shows a preview mode in the terminal dialog ([changelog](https://code.claude.com/docs/en/changelog)). Whether an orchestrator in the CLI can rely on previews is **unverified**.
- Waiting: questions stay open until answered; `askUserQuestionTimeout` (`60s`, `5m`, `10m`, default `never`) auto-continues and tells Claude you may be away ([settings](https://code.claude.com/docs/en/settings-reference#askuserquestiontimeout)).
- Sub-agents: removed from every sub-agent's tools, even when listed ([sub-agents](https://code.claude.com/docs/en/sub-agents#available-tools); [SDK limitations](https://code.claude.com/docs/en/agent-sdk/user-input#limitations)). Only the orchestrator can ask, which matches the "one contact" rule.
- `-p` mode: offered only when the run has a permission host (for example a `canUseTool` callback or `--permission-prompt-tool`); a `PreToolUse` hook can answer it by returning `updatedInput` with `answers`. `--permission-prompts none` removes it ([hooks](https://code.claude.com/docs/en/hooks#pretooluse-decision-control), [headless](https://code.claude.com/docs/en/headless)). Also disabled when `--channels` is active ([changelog](https://code.claude.com/docs/en/changelog)).
- Under Herdr: the dialog renders in the pane like any TUI. Herdr classifies it as `blocked`, and `herdr agent prompt` refuses to type into a blocked agent (`agent_blocked`), so a driving agent must read the dialog and ask the user (`herdr --skill`, local). The user answers in the pane.
- Limit for this use: a picker holds a short label and one description line per option. It cannot hold the comparison table and diff the user preferred in issue [#18](https://github.com/yahyabedirhan/skills/issues/18), and it is a poor slot for a free value such as an ID.

**Codex.** Codex has `request_user_input`: 1 to 3 structured questions with labelled options, rendered as a TUI overlay. It is available in Plan mode and not in Default mode; open requests ask to expose it more widely ([openai/codex#29104](https://github.com/openai/codex/issues/29104), [#30150](https://github.com/openai/codex/issues/30150), Plan-mode template [plan.md](https://github.com/openai/codex/blob/main/codex-rs/collaboration-mode-templates/templates/plan.md)). Not in the official config reference; **unverified**. Codex notifications: `notify` (a command receiving a JSON payload), `tui.notifications`, `tui.notification_method` (`auto`, `osc9`, `bel`), `tui.notification_condition` (`unfocused`, `always`) ([Codex config reference](https://learn.chatgpt.com/docs/config-file/config-reference)). Under Herdr, `osc9` would hit the same wall as Claude Code; `notify` with `osascript` would not (**unverified**).

**MCP elicitation.** A server can open a form or a URL in Claude Code mid-task ([mcp](https://code.claude.com/docs/en/mcp#respond-to-mcp-elicitation-requests)). It is server-initiated, so not a tool an orchestrator calls. The spec says servers MUST NOT use form mode for passwords, API keys or tokens and MUST use URL mode for them ([MCP elicitation, 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation)): the same principle as the secrets section below.

### Recommended question shape

Anthropic's guidance frames asking as a checkpoint, not a chat habit: agents "pause for human feedback at checkpoints or when encountering blockers" ([Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)). Claude Code's docs add: ask about the hard parts, not obvious ones, and treat a question the docs already answer as a sign the docs are ambiguous ([best practices](https://code.claude.com/docs/en/best-practices)). Long-running work carries state in files so a later session can pick it up ([Effective harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).

Combined with the shape the user validated (issue [#18](https://github.com/yahyabedirhan/skills/issues/18), second scenario), a decision request is:

1. **Questions first.** One line: "N questions; the plan is below them."
2. **Per question**, in this order: what it is in plain words; which ticket needs it and why; whether the agent can get or decide it itself, and why not; the options as a table with one column per option, the recommended column headed "(my pick)", one row per difference; how to answer; what happens if the user doesn't answer yet.
3. **The outcome as a diff** of the ticket tree, commit tree or file tree under the recommended options (the **show-me** `diff` form).
4. **A one-line close:** "Reply `go` to accept the picks, or name the options you'd rather have."

Collection: put the full view in the chat (or a show-me page), then, for picks, optionally follow with one `AskUserQuestion` call whose options repeat the table's columns, the pick first and labelled "(Recommended)". The table carries the context, the picker makes the answer one keystroke. For a value (an ID), give a named slot instead of a picker (see below).

### Timing and batching

- **Kickoff:** scan every ticket for user-only inputs (IDs, accounts, external setup, secrets) and ask for them in one batch before the first wave.
- **During the build:** hold new questions; ask them together at a stop point (a wave ends, or nothing unblocked remains), and notify "blocked" only when every remaining ticket waits. Never end a progress update with a question.
- **At the end:** leftover questions ride with the "done" notification and the final show-me view.

These are design choices drawn from the sources above and the two ticket scenarios; no primary source prescribes the exact cadence.

### Recording answers

Write each answer where the ticket that needs it will read it: a `Decisions` section in the ticket, or a `decisions.md` in the effort's folder that tickets link to. Each entry gives the question, the answer, the date, and which ticket consumes it. A later delegate or a successor orchestrator (issue [#15](https://github.com/yahyabedirhan/skills/issues/15)) then reads it instead of asking again, in line with the progress-file pattern in [Effective harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents). Secrets are recorded only as where they live (the env var name, the keychain item), never the value.

## Secrets and user-only inputs

| Kind | Example | How the user hands it over | Where it lives |
| :-- | :-- | :-- | :-- |
| Non-secret identifier | GitHub OAuth App client ID | Paste in chat, or fill the slot in the decisions file | Committed config or the ticket. GitHub's device flow sends only `client_id` ([authorizing OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps)), and public clients "cannot secure" a client secret ([best practices](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/best-practices-for-creating-an-oauth-app)), so the ID is meant to ship in the app |
| Secret for local runs | API key, client secret, token | The user runs the command themselves, never pastes it to the agent | macOS keychain: `security add-generic-password -a <acct> -s <service> -w` with `-w` last, which prompts for the value (`man security`); code reads it with `security find-generic-password -w`. Or a gitignored `.env` the user edits |
| Secret for CI | Same | `gh secret set NAME`, which prompts for the value interactively or reads stdin (`gh secret set --help`) | GitHub Actions secrets |

Claude Code specifics:
- `env` in settings is for non-secret variables; for secrets use credential helpers such as `apiKeyHelper` ([settings](https://code.claude.com/docs/en/settings-reference)).
- `permissions.deny` rules like `Read(./.env)` and `Read(./secrets/**)` hide files from discovery, search and reads, including `cat`/`head` in Bash; they don't stop an arbitrary subprocess, for which the sandbox is the OS-level fence ([settings](https://code.claude.com/docs/en/settings-reference#exclude-sensitive-files), [permissions](https://code.claude.com/docs/en/permissions)).
- Claude Code stores its own credentials in the macOS Keychain ([security](https://code.claude.com/docs/en/security)).

Rule for the orchestrator: ask for a secret by naming the command for the user to run (with the exact service or secret name) and the check it will run afterwards (the variable exists, the keychain item resolves), never by asking for the value. Where a step is long, the **wizard** skill can generate a script the user runs.

## What this means for the tickets

- **#5 (ask with show-me):** holds, and should be folded into #18. Show-me is the view; `AskUserQuestion` is at most the answer widget after it, since sub-agents cannot ask and the picker can't carry the table. The "answers already on the page are not asked" rule matches Claude Code's best-practice note.
- **#9 (notify when done or blocked):** keep the two moments and the model-triggered rule; no hook can judge them. Correct the explanation: the built-in tool fails under Herdr because Herdr drops OSC notifications and passes a stale `TERM_PROGRAM=iTerm.app` (herdr#4104), not because of `preferredNotifChannel`. Keep `osascript` as the macOS route under Herdr; add "skip silently" for the VPS. Mention `herdr notification show` and Herdr toasts as the route once the user enables them.
- **#18 (question agreement):** the doc supplies the design it asks to settle: kickoff scan, batching at stop points, the per-question fields, the ticket-17 view shape followed by an optional `AskUserQuestion`, answers recorded in a decisions section or file, and the secrets table. Replayed: the OAuth App client ID is a non-secret identifier, asked at kickoff with that explanation and stored in the ticket or config.

## Open questions

- TODO: Does Herdr forward OSC 9/777 in any mode? Only a third-party PR says it doesn't; ask Herdr or test with the user's consent.
- TODO: Would `preferredNotifChannel: "ghostty"` plus a Herdr fix deliver the built-in notification? Test once herdr#4104 ships.
- TODO: Does the user want Herdr `[ui.toast] delivery = "system"` (and sound on)? It would cover done and blocked for every agent without skill rules. User's call; it changes their config.
- TODO: Does `AskUserQuestion` in the CLI accept option previews an orchestrator can fill with a table or diff? Try it in a scratch session.
- TODO: On the VPS, is Remote Control connected during runs, so `PushNotification` reaches the phone? Otherwise the VPS orchestrator has no notification route.
- TODO: Pick one home for recorded answers (ticket section versus effort `decisions.md`) when implementing issue [#18](https://github.com/yahyabedirhan/skills/issues/18).
