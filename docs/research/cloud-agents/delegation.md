# Delegating to, watching and hearing back from agents off the Mac

Facts for [Research: delegating to, watching and hearing back from agents off the Mac (#73)](https://github.com/yahyabedirhan/skills/issues/73), under [Spec: research cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45). Researched 2026-09-29. They feed the three blocked build tickets:

- [A thinking session on the Mac can hand over to an orchestrator on the VPS (#13)](https://github.com/yahyabedirhan/skills/issues/13)
- [An unfinished effort can be handed to a new orchestrator (#15)](https://github.com/yahyabedirhan/skills/issues/15)
- [Agents on the Mac and the VPS can see each other's state (#16)](https://github.com/yahyabedirhan/skills/issues/16)

The question has four parts:

1. How does a local session (a Mac terminal, a Herdr pane, the desktop app) hand an effort to an agent somewhere else? The **handover** skill does this locally: it commits and pushes a handoff to GitHub and starts the new session with a one-line prompt.
2. How do the maintainer and a local agent watch that agent and answer it?
3. How does "done" or "blocked" reach the maintainer?
4. How does an unfinished effort move between places?

Words used here:

- **Effort**: one piece of work with its own branch and pull request, built from a spec and tickets.
- **Handover**: a session gives an effort to a new session through a committed handoff file.
- **Orchestrator**: the session that runs an effort and gives tickets to sub-agents.
- **Delegate**: an agent that takes one ticket, not a whole effort.

This page builds on these files and doesn't repeat them:

- [herdr-vps.md](../herdr-vps.md): the Herdr machine model, the Mac-to-VPS command reference, the safe-handover checks, VPS-to-Mac options.
- [agent-user-communication.md](../agent-user-communication.md): notification mechanisms in Claude Code and Herdr, and why Herdr loses the built-in notification.
- [effort-branches-and-prs.md](../effort-branches-and-prs.md): how to take over a branch safely, same branch versus stacked branch, and what a merge does to a stacked pull request.
- [harness-capabilities.md](../harness-capabilities.md): what each harness's rules, hooks and instructions can express locally.

The sibling tickets own some facts: Claude Code's cloud (#69), other providers (#70) and the VPS (#71). This page cites those facts straight from the primary docs, and only as far as delegation needs them.

Versions: Claude Code 2.1.284 (Mac) and 2.1.283 (VPS), codex-cli 0.157.1, gh 2.101.0, cursor-agent 2026.09.28, Herdr 0.9.0 on both machines. Herdr 0.9.2 came out today (see [the release](https://github.com/herdrdev/herdr/releases/tag/v0.9.2)).

Evidence tags:

- **[doc]** the provider's official documentation, linked inline.
- **[help]** the installed CLI's own `--help` output on the Mac.
- **[probe]** a command run for this research. Each one is in the exploration log.
- **[probe, #78]** a first-hand check from inside the cloud session of [#78](https://github.com/yahyabedirhan/skills/issues/78). See [session-probe.md](session-probe.md) and [session-workflow.md](session-workflow.md).
- **[prior]** a finding of an earlier research file in `docs/research/`, linked.
- **Unverified** marks a claim with no primary source or probe behind it.

This page cites Herdr docs at the `v0.9.2` tag under `https://raw.githubusercontent.com/herdrdev/herdr/v0.9.2/docs/next/website/src/content/docs/`.

---

## 1. Today's flow, and the steps that depend on where the agent runs

The table shows the local flow as the skills on `main` describe it. It was updated on 2026-09-30, after "Every harness and project is set up and audited from the skills" (#66) merged. The step numbers are today's.

| Step | Skill | What it assumes about place |
|---|---|---|
| Worktree and branch exist | [handover](../../../skills/handover/SKILL.md) step 1 | Made with `<worktree-tool>` (Treehouse on the Mac), else `git worktree add`, on the machine that runs the new session |
| Handoff written, committed, **pushed** | handover steps 3 and 5 | Nothing: the new session reads the repository. Already independent of place |
| One-line starting prompt, `/orchestrate-with-handoff <path>` | handover step 6 | The skill is installed where the new session runs |
| Start it in `<session-host>` | handover step 7, [handover-to-herdr](../../../skills/handover-to-herdr/SKILL.md) steps 1–5 | `herdr` reaches **this** machine's server. The worktree is on this machine. The maintainer can accept a trust prompt in the tab |
| Confirm it started | handover step 8, `herdr agent wait --until working` | Same server |
| Notify done or blocked | [orchestrating](../../../skills/orchestrating/SKILL.md), *Notifications*, `<notification-method>` | `osascript` on macOS (the `notification-method` row of the user's environment defaults) |
| Find agents still working, free the closing session's own worktree from outside it | [close-effort](../../../skills/settle-effort/SKILL.md) steps 7 and 8, [close-effort-commands.md](../../../skills/handover-to-herdr/settle-commands.md) | Same server |

Every step up to "pushed" already works for any destination. The rest changes per option:

- where the worktree comes from
- whether the starting prompt's skill exists there
- how the session starts and how the caller confirms it
- how the caller reads its state
- how it notifies

## 2. The options, side by side

"Local agent" means a Claude Code session on the Mac that acts for the maintainer. "Maintainer" means the person, by hand.

| Option | Hand over | Watch | Answer | Notify | Continue |
|---|---|---|---|---|---|
| **Mac, Herdr tab** (baseline) | handover-to-herdr: `worktree open`, `agent start`, `agent prompt` ([skill](../../../skills/handover-to-herdr/SKILL.md)) | Herdr sidebar. `herdr agent list/read` ([prior](../herdr-vps.md)) | Type in the tab. `herdr agent prompt` | `osascript` from the model ([prior](../agent-user-communication.md)) | Same branch or stacked ([prior](../effort-branches-and-prs.md)) |
| **VPS, Herdr tab** | The same commands run on the VPS server: `ssh <vps> herdr …` on 0.9.0, `herdr --machine <label> …` from 0.9.1 ([cli-reference.mdx](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.2/docs/next/website/src/content/docs/cli-reference.mdx), "Saved SSH machines"). Worktree by `git worktree add` (no Treehouse there) [probe] | The Mac Herdr window shows the VPS's agent states while another machine is selected ([connecting-machines.mdx](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.2/docs/next/website/src/content/docs/connecting-machines.mdx), "Switch between machines"). Agent: `herdr agent list/read` over SSH [probe] | The maintainer selects the VPS in the Herdr window. Agent: `herdr agent prompt` over SSH or `--machine` | `osascript` can't run there (Linux). `herdr notification show` on the VPS server returned `shown` [probe]. Where it appeared is unverified. A Mac-side `herdr agent wait --until done --until blocked` watcher is possible ([cli-reference.mdx](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.2/docs/next/website/src/content/docs/cli-reference.mdx), "Agents") | Git as locally. Check the old side over SSH first ([prior](../herdr-vps.md), "Safe-handover checks") |
| **VPS, Claude Code Remote Control** | Start `claude remote-control` (server mode) or `claude --remote-control` in a VPS pane. Send the prompt from the phone, web or another session ([remote-control](https://code.claude.com/docs/en/remote-control#start-a-remote-control-session)) | claude.ai/code and the Claude app list the session. A local session connected to Remote Control lists it with `ListAgents` ([cross-session-messaging](https://code.claude.com/docs/en/cross-session-messaging#see-which-sessions-claude-can-reach)) | Web or phone. `SendMessage` from a local session, through Anthropic's servers ([cross-session-messaging](https://code.claude.com/docs/en/cross-session-messaging#message-sessions-on-other-machines)) | Mobile push, "Push when Claude decides" / "Push when actions required" ([remote-control](https://code.claude.com/docs/en/remote-control#mobile-push-notifications)) | `claude remote-control --continue` brings the session back within about four hours ([remote-control](https://code.claude.com/docs/en/remote-control#resume-sessions-after-stopping-the-server)) |
| **VPS, Claude desktop SSH session** | Desktop app: environment dropdown, **+ Add SSH connection**. Claude runs on the remote machine ([desktop](https://code.claude.com/docs/en/desktop#ssh-sessions)) | Desktop sidebar. Other desktop sessions can list and read it ([desktop](https://code.claude.com/docs/en/desktop#work-across-sessions)) | In the desktop app | A desktop OS notification when a session finishes and nobody views it ([desktop](https://code.claude.com/docs/en/desktop)) | "Continue in" isn't available for SSH sessions ([desktop](https://code.claude.com/docs/en/desktop#continue-in-another-surface)) |
| **Claude Code cloud session** | The maintainer runs `claude --cloud "<one-line prompt>"` in a terminal in the worktree. It clones the GitHub remote at the current branch, so push first ([claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web#from-terminal-to-cloud)). It prints the session's title, URL and teleport command, and exits [probe, #78]. Untested: whether a local agent's shell, with no terminal, can run it. `-p` rejects `--cloud` with a task ([headless](https://code.claude.com/docs/en/headless), "Basic usage"; [claude-code.md §7](claude-code.md#7-starting-it)). The documented scriptable start is a routine's API trigger. Desktop **Continue in > Claude Code on the Web** pushes and moves a local session ([desktop](https://code.claude.com/docs/en/desktop#continue-in-another-surface)) | claude.ai/code, the app, `/tasks` in the CLI. `ListAgents` from a session connected to Remote Control ([cross-session-messaging](https://code.claude.com/docs/en/cross-session-messaging#see-which-sessions-claude-can-reach)). `list_sessions`/`get_session` from inside a cloud session [probe, #78] | Web or phone. `claude -p "<msg>" --cloud <session-id>` from any logged-in machine ([claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web#send-follow-ups-from-the-cli)) | Desktop and project notifications ([claude-projects](https://code.claude.com/docs/en/claude-projects#see-what-needs-you-in-overview)). Phone push for a plain cloud session is not documented, and untested | `claude --teleport <id>` pulls the branch and conversation into the terminal as a copy ([claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web#from-cloud-to-terminal)) |
| **Codex cloud** | `codex cloud exec --env <env-id> --branch <branch> "<prompt>"` [help] | `codex cloud list --json`, `codex cloud status <task-id>` [help]. The Codex web UI ([cloud](https://learn.chatgpt.com/docs/cloud)) | Follow-ups in the web UI ([cloud](https://learn.chatgpt.com/docs/cloud)). No CLI follow-up command [help] | Unverified: not on the [cloud](https://learn.chatgpt.com/docs/cloud) page | Open a pull request from the task, or `codex cloud apply <task-id>` locally [help] |
| **Cursor Cloud Agent** | `&` before a message in the Cursor CLI ([cli/using](https://cursor.com/docs/cli/using.md)). API `POST /v1/agents` with `repos[].startingRef` and `workOnCurrentBranch` ([api/endpoints](https://cursor.com/docs/cloud-agent/api/endpoints.md)) | cursor.com/agents, the iOS app. API `GET` run and stream endpoints ([api/endpoints](https://cursor.com/docs/cloud-agent/api/endpoints.md)) | Follow-up run, `POST /v1/agents/{id}/runs` (one active run per agent) ([api/endpoints](https://cursor.com/docs/cloud-agent/api/endpoints.md)) | iOS push when an agent finishes a turn ([mobile](https://cursor.com/docs/cloud-agent/mobile.md)). API webhooks only on the legacy v0 API | Pushes to a `cursor/…` branch, or to `startingRef` itself with `workOnCurrentBranch: true` ([api/endpoints](https://cursor.com/docs/cloud-agent/api/endpoints.md)) |
| **GitHub Copilot coding agent** | `gh agent-task create "<prompt>" --base <branch>` [help] | `gh agent-task list`, `gh agent-task view <id> --log --follow`, `--json state,pullRequestUrl` [help] | Follow-up in the agents page, or `@copilot` in a pull request comment ([track sessions](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/track-copilot-sessions), [about](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)) | Unverified: not on the [track sessions](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/track-copilot-sessions) page | One branch and one pull request per task ([about](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)). Stack with `--base` [help] |
| **Google Jules** | `jules remote new --repo <repo> --session "<prompt>"` ([CLI reference](https://jules.google/docs/cli/reference)) | `jules remote list --session`. The `jules` TUI ([CLI reference](https://jules.google/docs/cli/reference)) | Unverified: not in the CLI reference | Unverified: not in the CLI reference | `jules remote pull --session <id>` ([CLI reference](https://jules.google/docs/cli/reference)) |

Only three rows can run **this repo's skills** as they are:

- the Mac
- the VPS (either way)
- a Claude Code cloud session that has the skills (section 4)

The other hosted agents take a task, not an effort. Each one runs one prompt on one branch and returns a pull request or a diff. They fit a **delegate** role (one ticket), not an orchestrator's role.

## 3. The VPS

### 3.1 Handing over through Herdr (#13's path)

What each handover step becomes, from a Mac session to the VPS server:

1. **Worktree.** The VPS has no Treehouse [prior](../herdr-vps.md). So `<worktree-tool>` falls back to `git worktree add` there, in the VPS's own clone, from the pushed branch: `git -C <vps repo> fetch origin <branch>` then `git -C <vps repo> worktree add <path> <branch>`. The VPS's `<worktree-tool>` must come from the VPS's own environment defaults. Those are the table in its shared global instructions, whose roles set-up-machine writes (`skills/set-up-machine/references/global-instructions.md`, *Roles*). The Mac's value doesn't apply. When the row is `none`, the fallback in the roles table is exactly this `git worktree add`.
2. **Workspace and tab.** Run `herdr worktree open --workspace <repo workspace> --path <worktree> --label <topic> --no-focus` on the VPS server, with IDs read from the VPS's own JSON. A probe showed that workspace create, rename and close work over SSH [probe]. `worktree open` needs a workspace on the VPS whose `repo_root` is the clone (handover-to-herdr, step 2).
3. **Agent.** `claude` is on `PATH` inside a new VPS Herdr pane, and so is `herdr` [probe]. That settles the open question in herdr-vps.md: `agent start --kind claude` would find `claude` (the start itself wasn't run). Only `claude` exists there, so `<agent>` must name it [prior](../herdr-vps.md).
4. **Starting prompt.** The VPS has `orchestrate-with-handoff`, `orchestrate-effort`, `orchestrating` and `init-effort` installed. It doesn't have `handover`, `handover-to-herdr`, `herdr`, `close-effort` or `treehouse` [probe]. So the orchestrator starts, but it can't close its own effort or hand over again from there. It can do that only after the VPS gets this branch's skills.
5. **Trust prompt.** A new worktree path shows Claude Code's "trust this folder?" screen (handover-to-herdr, step 4). The maintainer answers it in the VPS tab through the Mac's Herdr window. That window forwards input to the selected machine ([connecting-machines.mdx](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.2/docs/next/website/src/content/docs/connecting-machines.mdx)).
6. **Confirm.** Run `herdr agent wait <name> --until working` on the VPS server, as locally.

Transport on 0.9.0: every command is `ssh <target> "bash -lc '…'"`, and the prompt needs remote-shell quotes [prior](../herdr-vps.md).

From 0.9.1, `herdr --machine <label-or-id> …` forwards `workspace`, `worktree`, `tab`, `pane`, `notification` and `agent` as JSON over non-interactive SSH ([cli-reference.mdx](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.2/docs/next/website/src/content/docs/cli-reference.mdx), "Saved SSH machines"). It:

- needs no open window
- never puts payloads into the shell command
- never falls back to Local
- doesn't let `--current` refer to a local pane

0.9.2 adds `herdr machine status [<label-or-id>] [--json]`. This is a fresh, non-interactive reachability check that a skill can run before a handover. 0.9.2 also opens fewer SSH connections for repeated `--machine` commands ([v0.9.2 release](https://github.com/herdrdev/herdr/releases/tag/v0.9.2)). The VPS target itself comes from `herdr machine list --json`, never from skill text [prior](../herdr-vps.md).

### 3.2 Watching and answering

- **The maintainer** sees the VPS's agent states in the Mac's Herdr window, with no switch to the VPS. The docs say: "Other connected machines keep updating their workspace information, agent states, and notifications without streaming their pane screens" ([connecting-machines.mdx](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.2/docs/next/website/src/content/docs/connecting-machines.mdx)). To answer, the maintainer selects the VPS workspace and types.
- **A local agent** reads with `herdr agent list`, `agent get` and `agent read --source recent-unwrapped` on the VPS server [prior](../herdr-vps.md). It answers with `herdr agent prompt`. When the agent is blocked, `agent prompt` returns `agent_blocked` and sends nothing. So this way can't answer a permission prompt ([cli-reference.mdx](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.2/docs/next/website/src/content/docs/cli-reference.mdx), "Agents"). To message a running remote agent still needs an explicit ask (#13, #16).
- **Claude Code's own channel, no SSH.** Suppose a VPS session runs with Remote Control, and a Mac session is connected to Remote Control too. Then the Mac session lists the VPS session (labelled `Remote Control`) and messages it with `SendMessage`. The message travels "through Anthropic servers, arriving over that machine's Remote Control connection", and the receiver can reply ([cross-session-messaging](https://code.claude.com/docs/en/cross-session-messaging#message-sessions-on-other-machines)).
  - This works in **both directions**, VPS to Mac included. It needs no Remote Login, Tailscale or tunnel, which herdr-vps.md found missing.
  - It carries text only. It doesn't read a transcript or run git.
  - An incoming message "can't approve anything" and can't change configuration ([cross-session-messaging](https://code.claude.com/docs/en/cross-session-messaging#how-a-session-treats-an-incoming-message)). `isolatePeerMachines: true` makes each cross-machine send ask first.
  - The VPS's Claude Code is signed in with a claude.ai account against the first-party API [probe]. Remote Control requires this ([remote-control](https://code.claude.com/docs/en/remote-control#requirements)).
  - Unverified in practice: this research started no Remote Control session.

### 3.3 Notifying

- **`osascript`**, the user's `<notification-method>`, is macOS only. Nothing replaces it on the Linux VPS, which also lacks `notify-send` [prior](../herdr-vps.md).
- **Herdr on the VPS.** `herdr notification show` on the VPS server returned `{"reason":"shown","shown":true}` [probe]. Yet the VPS has no Herdr config file [probe].
  - The documented default is still `off`. The config reference gives `ui.toast.delivery` a default of `"off"` for both 0.9.0 and the current docs (`config-reference.json` under `docs/versions/0.9.0/` and `docs/next/` at `v0.9.2`).
  - The `delivery = "herdr"` on the 0.9.2 configuration page is an example of how to turn it on. It is not the default ([configuration.mdx](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.2/docs/next/website/src/content/docs/configuration.mdx), "Notifications").
  - So nothing explains the `shown` result. [vps.md](vps.md#notifications) records the same.
  - Where it appeared is unverified. The maintainer was away, and the Mac's own config has `delivery = "off"` [probe].
  - Herdr's docs say that sound "plays through the local Herdr client". They also say that terminal and system delivery go through the attached client [prior](../herdr-vps.md). So the Mac client's settings probably decide.
  - Once delivery is on, Herdr also notifies on its own when a background agent finishes or needs input ([configuration.mdx](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.2/docs/next/website/src/content/docs/configuration.mdx)).
- **A Mac-side watcher.** A local agent can wait on the remote agent and raise `osascript` itself ([cli-reference.mdx](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.2/docs/next/website/src/content/docs/cli-reference.mdx)). It waits with `herdr agent wait <name> --until done --until blocked`, which has no time limit without `--timeout`. The watcher lives only as long as that local session and its SSH connection. Not tested.
- **Remote Control push.** A VPS session with Remote Control on can push to the phone ([remote-control](https://code.claude.com/docs/en/remote-control#mobile-push-notifications)):
  - "Push when Claude decides" for finished work
  - "Push when actions required" for permission prompts and questions

  The session must keep running: "To keep a session running on a remote machine after you disconnect from SSH, start it inside `tmux` or `screen`" ([remote-control](https://code.claude.com/docs/en/remote-control#limitations)). A Herdr pane on the VPS server does the same job.

### 3.4 Other ways onto the VPS

- **Desktop SSH sessions** run Claude Code on a Linux or macOS host, with the desktop app as the interface. The app installs Claude Code there on first connect ([desktop](https://code.claude.com/docs/en/desktop#ssh-sessions)). They suit a maintainer at the desk, not a handover that Herdr drives. "Continue in" isn't available for them.
- **Remote Control server mode**, `claude remote-control --spawn worktree`, serves many sessions from one process. Each session gets its own git worktree ([remote-control](https://code.claude.com/docs/en/remote-control#start-a-remote-control-session)). In a directory it hasn't trusted, it asks `Trust <directory>? [y/N]`. When it can't ask, it exits with `Workspace not trusted` ([remote-control](https://code.claude.com/docs/en/remote-control#requirements)).
- **A Claude Code project's "thread on your computer"** runs a project thread through `claude remote-control` on the machine that has the folder ([claude-projects](https://code.claude.com/docs/en/claude-projects#run-a-thread-on-your-own-computer)). Projects are web, desktop and mobile only, not the CLI. They are in a gradual beta on Pro and Max.
- **Cursor's My Machines**: `agent worker start` on a machine makes it a Cloud Agent target. "The agent loop runs in Cursor's cloud, but terminal commands, file edits, browser actions, and other tool calls execute on your machine", over an outbound connection ([my-machines](https://cursor.com/docs/cloud-agent/self-hosted/my-machines.md)). It needs an install on the VPS, so it stays a proposed experiment.

## 4. Claude Code cloud sessions

### 4.1 Handing over

- **Start.** `claude --cloud "<task>"` creates a cloud session. "The cloud VM clones your current directory's GitHub remote at your current branch, not your local checkout, so push first" ([claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web#from-terminal-to-cloud)). The handover's "everything committed and pushed" already covers this.
  - The docs' own pattern is the handover's: "save the plan to the repo, commit, and push so the cloud VM can clone it", then `claude --cloud "Execute the migration plan in docs/migration-plan.md"`.
  - `--remote` is the deprecated spelling. `--environment <id>` picks a self-hosted environment. `/remote-env` sets the default environment [help] ([cloud-environments](https://code.claude.com/docs/en/cloud-environments#select-an-environment-from-the-cli)).
- **Who can run that start.** The docs describe an interactive create form. The CLI "shows a live checklist of setup steps" and "queues messages you type during provisioning" ([claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web#from-terminal-to-cloud)). And `-p` "rejects … `--cloud` with a task description, with an error naming the conflict" ([headless](https://code.claude.com/docs/en/headless), "Basic usage").
  - First-hand, the command starts the session and exits at once. The maintainer's `claude --cloud "say hi"` in a Mac terminal printed three lines and exited, with no checklist [probe, #78; [claude-code.md §7](claude-code.md#7-starting-it)].
  - Untested: whether a local agent's shell, with no terminal, can run it. The research's own try (`< /dev/null`) exited 1 with its output unread, and created no session.
  - So the maintainer can start one. For an agent, the documented scriptable start is a routine's API trigger (below). `claude -p "<msg>" --cloud <session-id>` only sends follow-ups to a session that already exists.
- **Agent-side start and watch, from inside a cloud session.** A cloud session has a "Claude Code Remote" MCP server [probe, #78; [session-workflow.md §3](session-workflow.md#3-the-effort-workflow-in-a-cloud-session)]:
  - `create_session` (repo, branch, `outcome_branch`, prompt) starts another cloud session.
  - `list_sessions` / `get_session` read every session's state, Remote Control sessions on the Mac or VPS included. The state has branch, dirty, unpushed, status bucket and needs action.

  `create_session` is untested (E17 in [README.md](README.md#proposed-experiments)). Nobody knows yet whether a local session on the Mac gets these tools.
- **The starting prompt's skill.** A cloud session reads the repo's `CLAUDE.md` and `.claude/skills/`. It doesn't read `~/.claude/CLAUDE.md` or `~/.claude/skills/`. "Cloud sessions automatically load skills you enable on claude.ai" ([cloud-environments](https://code.claude.com/docs/en/cloud-environments#what-carries-over-from-your-setup)).
  - This repo keeps its skills under `skills/`, not `.claude/skills/`. Other projects don't carry them at all. So `/orchestrate-with-handoff <path>` resolves in the cloud only if the skills get into the VM.
  - #78 found a third way besides claude.ai and `.claude/skills/`. Skills installed into the VM's own `~/.claude/skills` load, even mid-session. So an environment setup script can install them and the global instructions ([session-workflow.md §2](session-workflow.md#2-carrying-the-skills-and-global-instructions-into-cloud-sessions)).
  - One catch: `orchestrate-with-handoff` is `disable-model-invocation: true`, so the model can't pick it on its own. It runs only when someone types it as a slash command. Untested: whether a `--cloud` or `create_session` prompt counts as typed.
- **Sub-agents** work in cloud sessions as locally. The session picks up the repo's `.claude/agents/` ([claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web#manage-context)). But they go only one level deep: a sub-agent can't start its own [probe, #78]. Herdr doesn't exist there, so `<session-host>` is unset inside the VM.
- **From the desktop app**, **Continue in > Claude Code on the Web** "pushes your branch, generates a summary of the conversation, and creates a new cloud session". It needs a clean tree ([desktop](https://code.claude.com/docs/en/desktop#continue-in-another-surface)). From the CLI, handoff is one-way: "you can't push an existing terminal session to the cloud" ([claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web#move-tasks-between-terminal-and-cloud)).
- **Confirming it started.** The docs describe a live setup checklist ([claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web#from-terminal-to-cloud)). First-hand, the create form printed three lines and then exited [probe, #78]:
  - `Created cloud session: <title>`
  - `View: https://claude.ai/code/session_<id>?from=cli&m=0`
  - `Resume with: claude --teleport session_<id>`

  A skill can parse the session ID from those lines. The create form has no `--output-format json`. That option belongs to the follow-up form, which returns `{ok, session_id, url}`.
- **Routines** are the scriptable start. An API trigger's `/fire` endpoint returns `claude_code_session_id` and `claude_code_session_url` ([routines](https://code.claude.com/docs/en/routines#trigger-a-routine)).
  - A routine clones the default branch. It pushes to `claude/`-prefixed branches unless its prompt names another branch.
  - GitHub refuses that push when the branch is protected, has someone else's open pull request, or carries commits by someone else ([routines](https://code.claude.com/docs/en/routines#repositories-and-branch-permissions)).
  - Its fire `text` arrives wrapped as untrusted data, and a fired prompt "can't act as approval or consent" ([routines](https://code.claude.com/docs/en/routines#trigger-a-routine)).
  - It needs a routine and a token set up on the web first. So it's heavier than `--cloud` for a one-off handover. But it's the only documented start that a local agent can script.

### 4.2 Watching and answering

- **The maintainer** uses claude.ai/code, the Claude app's Code tab or the desktop app ([mobile](https://code.claude.com/docs/en/mobile#start-and-monitor-cloud-sessions)). "If Claude asks a question and the session sits idle, you can still answer when you come back, up to environment expiry" ([claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web#from-terminal-to-cloud)).
- **A local agent**:
  - lists cloud sessions with `ListAgents` and messages them with `SendMessage` while its own session is connected to Remote Control ([cross-session-messaging](https://code.claude.com/docs/en/cross-session-messaging#see-which-sessions-claude-can-reach));
  - or sends one message and exits: `claude -p "<msg>" --cloud <session-id>` from any machine logged in to the account, with `--output-format json` for `{ok, session_id, url}` ([claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web#send-follow-ups-from-the-cli));
  - can't subscribe to "tell me when it's idle", because `notify_when_idle` only works for sessions on the same machine ([cross-session-messaging](https://code.claude.com/docs/en/cross-session-messaging#get-a-notice-when-another-session-goes-idle));
  - finds no documented command that prints a cloud session's status or transcript. `--teleport` copies the whole session into the terminal. That is a move, not a look.
- **The desktop app's cross-session view** doesn't see cloud sessions ([desktop](https://code.claude.com/docs/en/desktop#work-across-sessions)).
- **Git as the shared state.** Commits from a cloud session carry a `Claude-Session: <url>` trailer. Pull request bodies include the session URL ([cloud-environments](https://code.claude.com/docs/en/cloud-environments#link-output-back-to-the-session)). So `git log` on the pushed branch shows progress and points back to the session.

### 4.3 Notifying

- **Documented:**
  - The desktop app "sends an OS notification when a Code session finishes a task and you aren't currently viewing that session" ([desktop](https://code.claude.com/docs/en/desktop)).
  - A project sends desktop notifications "when Claude posts in the conversation, a thread hits an error, or a thread needs your input". This is desktop only ([claude-projects](https://code.claude.com/docs/en/claude-projects#see-what-needs-you-in-overview)).
  - Dispatch pushes to the phone ([desktop](https://code.claude.com/docs/en/desktop#sessions-from-dispatch)).
- **Not documented:** a phone push for a plain cloud session. The docs describe mobile push for Remote Control sessions only ([mobile](https://code.claude.com/docs/en/mobile#get-push-notifications)). A cloud session's main loop does have a `PushNotification` tool (sub-agents don't). Whether it reaches the phone is still untested [probe, #78].
- **A permission prompt blocks silently.** In #78's session, the first calls to several tools waited as pending actions until someone approved them. The session sat in the blocked bucket, and nothing notified [probe, #78]. An unattended cloud orchestrator needs allow rules for its tools.
- **The skills' rule** is that the model notifies at done and blocked, through `<notification-method>` (orchestrating's *Notifications*). The VM has no `osascript`.
  - Where the VM has no environment defaults, the fallback in the roles table for `notification-method` is "the harness's notification tool, else a line in the chat". In a cloud session's main loop, that tool is `PushNotification`.
  - Until a phone push is proven (E19 in [README.md](README.md#proposed-experiments)), the delivered pull request is the done signal, with the maintainer's GitHub notifications on it. Blocked means a question left in the session.

### 4.4 Continuing, and keeping two orchestrators off one branch

- **Cloud to terminal:** `claude --teleport <session-id>` (or `/teleport`, or `t` in `/tasks`) checks the repository. It "fetches and checks out the branch from the cloud session, and loads the full conversation history". It needs these ([claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web#from-cloud-to-terminal)):
  - a clean tree
  - the same repository (not a fork)
  - a pushed branch
  - the same account
- **Teleport forks:** "The terminal gets its own copy of the session: new work there stays local and doesn't appear in the cloud session".
  - Unverified: the docs don't say that the cloud session stops. Assume it may still run until experiment E12 in [README.md](README.md#proposed-experiments) settles it.
  - If it does keep running, then after a teleport **two orchestrators can push to one branch**. So the continuation must archive the cloud session before the local copy commits. At least, it must confirm that the cloud session is idle.
- **Terminal to cloud** is a new session, not a move. The maintainer runs `claude --cloud` in a terminal (section 4.1). It starts fresh from the pushed branch and the handoff, like any handover. Stop the local orchestrator first.
- **Lifetime:** a cloud session stops after a time with no activity, and Anthropic reclaims its VM. A reopen restores the conversation. But "background work that was still running … such as subagents and shell commands, isn't restored" ([claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web#environment-expired)).
  - A project thread's sandbox can restart "from a fresh clone, so uncommitted changes can be lost. On long tasks, ask Claude to commit and push work in progress" ([claude-projects](https://code.claude.com/docs/en/claude-projects#limitations)).
  - The orchestrating skills already commit each ticket, which fits.
- **Same branch or stacked:** a `--cloud` session starts on the branch of the local checkout. Then it works on a `claude/<slug>` branch made from it. It may push a **new** non-`claude/` branch that it creates and checks out, and further commits to that branch [probe, #78]. Can it push to an **existing** branch it didn't create (the effort branch, for "same branch")? The docs say so only for routines (above). For sessions it is untested (E20 in [README.md](README.md#proposed-experiments)).

## 5. Other hosted agents, for delegation only

The details belong to #70. These are the facts that delegation needs.

- **Codex cloud**: `codex cloud exec --env <ENV_ID> [--branch <BRANCH>] [--attempts N] "<prompt>"`. The branch "defaults to current branch". Other commands: `codex cloud list [--env] [--json]`, `status <TASK_ID>`, `diff <TASK_ID>`, `apply <TASK_ID>` [help].
  - The CLI has no follow-up command. Follow-ups and "open a pull request" are in the web UI ([cloud](https://learn.chatgpt.com/docs/cloud)).
  - A local agent can poll `list --json`. It can apply a finished diff into a local worktree.
- **Cursor Cloud Agents**: the CLI's `&` prefix pushes the conversation to a Cloud Agent ([cli/using](https://cursor.com/docs/cli/using.md)). The v1 API ("public beta") is the scriptable path ([api/endpoints](https://cursor.com/docs/cloud-agent/api/endpoints.md)):
  - `POST /v1/agents` with `prompt.text`, `repos[0].url`, `repos[0].startingRef`, `workOnCurrentBranch` and `autoCreatePR`. `workOnCurrentBranch` defaults to `false`, which means a new `cursor/…` branch. `true` pushes straight to the starting branch.
  - Follow-ups with `POST /v1/agents/{id}/runs`. It returns `409 agent_busy` while a run is active.
  - `env.type: "machine"` routes to a My Machines worker.

  Cloud agents run the repo's `.cursor/hooks.json` but not `~/.cursor/hooks.json` ([cloud-agent](https://cursor.com/docs/cloud-agent.md)). Billing is at API pricing with a spend limit ([cloud-agent](https://cursor.com/docs/cloud-agent.md)). So it needs a sign-up decision before any trial.
- **GitHub Copilot coding agent**: `gh agent-task create "<prompt>" [--base <branch>] [--custom-agent <name>] [--follow]`. Also `gh agent-task view <session-id|pr> [--log] [--follow] [--json …]`, with fields that include `state`, `pullRequestNumber`, `pullRequestUrl` and `completedAt` [help].
  - A stop "ends the GitHub Actions run and preserves any commits already pushed".
  - For a follow-up typed into the session, "Copilot implements … after it finishes its current tool call" ([track sessions](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/track-copilot-sessions)).
  - It "can only work on one branch at a time and can open exactly one pull request to address each task" ([about](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)).
- **Jules**: `jules remote new --repo <repo> --session "<prompt>"`, `jules remote list --session`, `jules remote pull --session <id>` ([CLI reference](https://jules.google/docs/cli/reference)).

The effort workflow could use these as delegates. The orchestrator stays local (or on the VPS). It hands one ticket to a hosted agent through its CLI or API, and reads its pull request or diff back.

None of them loads this repo's skills as they are, the user's global instructions or the user's deny rules. Only Cursor carries anything personal: the account User Rules and a `~/.cursor/skills` sync ([other-providers.md §2](other-providers.md#2-cursor-cloud-agents-and-the-agent-cli)). So the delegate brief must carry the rules. #74 weighs that.

## 6. What this settles for the three blocked tickets

### A thinking session on the Mac can hand over to an orchestrator on the VPS (#13)

**Settled.**

- The handover's first two steps don't change: the session commits and pushes the handoff, and the prompt is one line.
- The VPS host comes from Herdr's saved machine (`herdr machine list --json`, with `herdr machine status` from 0.9.2), never from skill text.
- The Herdr steps work against the VPS server with explicit remote IDs. Probes showed that workspace create, tab rename and workspace close work over SSH. `claude` is on a new pane's `PATH`.
- `herdr --machine` in place of `ssh … bash -lc` needs Herdr 0.9.1 or later on both ends.
- The shape comes from the Parameters convention. handover-to-herdr gets a target machine (Local or a saved machine's label). The VPS's own environment defaults name its worktree tool (`git worktree add` until Treehouse is installed) and its agent (`claude`).

**Still open:**

- The VPS lacks `handover`, `handover-to-herdr`, `herdr` and `close-effort`. So a VPS orchestrator can't close its effort until set-up-machine sets up the environment there.
- The trust prompt needs the maintainer in the VPS tab.
- Notification: `osascript` is gone. All three candidates need a test with the maintainer present:
  - a Mac-side `agent wait` watcher
  - Herdr's delivery setting (the probe says the VPS server shows notifications, but not where)
  - Remote Control push
- The VPS can't read the thinking session's tab. So the handoff must carry everything (it already must, per the handover skill).

### An unfinished effort can be handed to a new orchestrator (#15)

**Settled.**

- **Detection and the question.** A continuation is a handover whose worktree is the existing effort branch, or a new branch stacked on it. The session refreshes the handoff first. Earlier research already answers the same-branch versus stacked question and its effect on the open pull request [prior](../effort-branches-and-prs.md).
- **Where it runs.** Per option, the move is:
  - Mac or VPS through Herdr: the same steps on the other server;
  - cloud to Mac: `claude --teleport`, which forks the session;
  - Mac to cloud: a new `claude --cloud` session from the pushed branch, or the desktop app's **Continue in**. The maintainer starts it in a terminal, or a routine's API trigger starts it when an agent must;
  - Codex cloud: `codex cloud apply` brings a diff back;
  - Cursor: `workOnCurrentBranch` continues on the same branch.
- **Keeping two orchestrators off one branch** takes a check on the old side before the new side commits:
  - on a Herdr server: the old agent is `idle` or `done` or gone, and its tree is clean and pushed [prior](../herdr-vps.md);
  - on claude.ai: the cloud session is archived or idle;
  - on either: `git ls-remote` matches the old side's `HEAD`.

  Teleport is the risky path. The docs don't say that the cloud session stops. Assume it may still run until E12 settles it ([README.md](README.md#proposed-experiments)).

**Still open:**

- The cloud side has no documented "is it idle?" read from the CLI. There is only `ListAgents` through Remote Control, or a look at claude.ai. From inside a cloud session, `list_sessions` reads it [probe, #78].
- Whether a cloud session may push to an existing effort branch (a new branch works).
- The run notes below.

### Agents on the Mac and the VPS can see each other's state (#16)

**Settled.**

- Mac to VPS: every read works today over SSH. That includes Herdr lists, `agent read`, and `git status`, `git log` and `git ls-remote` in a VPS worktree [prior](../herdr-vps.md).
- From 0.9.1 the same reads run through `herdr --machine`. The host stays in Herdr's machine catalog.
- The new finding is Claude Code's cross-session messaging. Remote Control must be on in both sessions. Then a Mac session and a VPS session (or a cloud session) can list and message each other **in both directions**, through Anthropic's servers.
  - That's the VPS-to-Mac path that herdr-vps.md found missing. It needs no inbound access to the Mac.
  - It carries text, not state. The agent on that machine must still answer "is anything unpushed?". The difference is that a message asks it now, not the maintainer.
  - Incoming messages can't approve anything or change configuration. `isolatePeerMachines` can make each cross-machine send ask first. This matches the permission line that #16 asks for.

**Still open:**

- a live test of Remote Control and `SendMessage` between the Mac and the VPS;
- whether an agent can read the cross-machine agent states in the Herdr sidebar, not only the maintainer see them. `--machine` forwards `api snapshot`, but not event subscriptions ([cli-reference.mdx](https://raw.githubusercontent.com/herdrdev/herdr/v0.9.2/docs/next/website/src/content/docs/cli-reference.mdx)).

## 7. How this effort itself was handed over (material for #15)

This section comes from the effort's handoffs ([.handoff/2026-09-29-cloud-agents.md](../../../.handoff/2026-09-29-cloud-agents.md), [.handoff/2026-09-29-cloud-agents-research.md](../../../.handoff/2026-09-29-cloud-agents-research.md)) and from this ticket's own run.

- **The flow.** The environment effort's orchestrator was busy with its own effort. It handed a **new** effort to a **thinking session** in a **new Herdr workspace**.
  - The new effort's branch, `skills/cloud-agents`, was stacked on the orchestrator's own unmerged branch, `skills/environment`. That branch's pull request (#66) was under review.
  - The handoff named the session that handed over. It told the new session not to message that session or touch its branch.
  - It said: rebase onto #66 if #66 changes. Target `skills/environment` until #66 merges, then `main`.
- **It worked.** The thinking session started from the handoff alone.
- **The maintainer redirected it mid-start.** They stopped a research agent that it had launched. They cut the grilling to one round. They changed the effort from a build to research. The handoff it had received described a build plan, and the grilling then replaced that plan. The thinking session wrote a second handoff that says the first one's plan is superseded, and linked back to it.
- **A delegate's worktree started on the wrong base.** The orchestrator created the worktree for this ticket's delegate from `main`, not from the stacked effort branch. The handoffs that this ticket had to read weren't there. The delegate fast-forwarded its worktree onto `skills/cloud-agents` before it started (exploration log).

What #15 can take from it:

1. **A handover to a new effort stacked on an unmerged branch is a continuation in all but name.** It needs the same base-branch facts as the continuation of an unfinished effort: which branch, which pull request it targets now, and what happens when the lower one merges.
2. **A handoff goes stale.** When the plan changes after a handover, the next session should find a newer handoff that supersedes the old one. It should not find a plan that no longer holds. The second handoff did this by hand. A continuation skill should check for it.
3. **Sub-agent worktrees in a stacked effort must branch from the effort branch.** The default base (the repository's default branch) gives a delegate a tree without the effort's commits. The orchestrator's delegation, or the worktree tool, must pass the base explicitly.
4. **Sometimes the new session can't reach the handing session** (busy, or the maintainer away). Then the new session decides open questions itself and lists them. The handover skill already says this.

## Open questions

Each needs a step outside this ticket's safe zone, so each is a proposed experiment.

- TODO: **Upgrade both machines to Herdr 0.9.2.** It ships `--machine` from 0.9.1, `machine status`, and the `TERM_PROGRAM` fix for [herdr#4104](https://github.com/herdrdev/herdr/issues/4104). Then run section 3.1's steps again through `herdr --machine`. A server update asks before it stops the server's panes, so the maintainer must be present.
- TODO: **Where a VPS notification appears.** With the maintainer at the Mac, run `herdr notification show` on the VPS server three times, and record what shows:
  1. with the Mac window on Local
  2. with the Mac window on the VPS
  3. with the Mac's `delivery` set to `system`

  The probe got `shown` from a VPS with no config.
- TODO: **Remote Control between the Mac and the VPS.** Start `claude --remote-control` in a throwaway VPS Herdr tab. Connect a Mac session to Remote Control. Check that `/list-agents` lists the VPS session and that `SendMessage` works both ways. Then repeat with `isolatePeerMachines: true`. It needs the one-time Remote Control consent on the VPS, which is a config change.
- Answered by #78's cloud session ([session-probe.md](session-probe.md#answers-to-69s-open-questions)), formerly the "#69's cloud sessions" TODO:
  - **Does `claude --cloud` print a session ID a skill can record?** Yes: `Created cloud session: <title>`, `View: <url>`, `Resume with: claude --teleport <id>`, then it exits.
  - **Does `/orchestrate-with-handoff` resolve in a cloud session?** Not from claude.ai: only Anthropic's own skills are enabled there. When installed into the VM's `~/.claude/skills`, it loads. But it is `disable-model-invocation: true`, so the model can't pick it on its own. Someone must type it.
  - **May a cloud session push to a non-`claude/` branch?** A new one it creates, yes. An existing one it didn't create: untested (E20 in [README.md](README.md#proposed-experiments)).
  - **Does a plain cloud session push to the phone?** Still unverified (E19).
- TODO: **Teleport and the cloud original.** After `claude --teleport`, check whether the cloud session still runs, and archive it by hand. This decides whether the continuation must stop the cloud side itself.
- TODO: **Set up the VPS environment with set-up-machine**: the skills from `main` (now that #66 has merged), and environment defaults with `worktree-tool` and `agent`. Then a VPS orchestrator can run close-effort and handovers. It's an install and a config change.
- TODO: **Cursor My Machines on the VPS** (`agent worker start`), if the maintainer adopts Cursor. It would make the VPS a Cloud Agent target, driven from the phone or the API. It needs an install and a paid plan.
- TODO: **Copilot and Codex cloud notifications.** Neither doc page that this research read says how the user hears that a task finished. Check with an account, as #70's ticket allows.
- TODO: **Delegate worktree base in stacked efforts.** Check how the orchestrating skill's sub-agent worktrees pick their base, and make it the effort branch. Still open on 2026-09-30: orchestrate-effort's step 4 says each delegate works "in its own git worktree" and names no base.

## Exploration log

Every command run for this research. "Mac" is the maintainer's Mac. "VPS" commands ran as `ssh <vps> "bash -lc '…'"`. The research read the target from `herdr machine list --json` into a scratch SSH config alias outside the repo, and never printed it. It reduced output to counts and states before it read the output. So it captured no workspace labels, agent names or paths.

| # | Where | Command or action | Changed |
|---|---|---|---|
| 1 | Mac, this worktree | `git merge --ff-only skills/cloud-agents` (the worktree had started on `main`) | This worktree's branch only |
| 2 | Mac | Read the ticket, spec, #13, #15, #16 (`gh issue view`), the two handoffs, the handover, handover-to-herdr, close-effort skills, and the research files above | Nothing |
| 3 | Web | Fetched Claude Code docs: claude-code-on-the-web, remote-control, cloud-environments, settings, claude-projects, mobile, desktop, routines, cross-session-messaging | Nothing |
| 4 | Web | Fetched the Codex cloud page, Cursor cloud-agent, my-machines, api/endpoints, mobile, cli/using (to a scratch folder outside the repo), the Copilot coding agent pages, the Jules CLI reference | Nothing |
| 5 | Web | `gh release list/view -R herdrdev/herdr`; fetched Herdr docs at `v0.9.2` (connecting-machines, cli-reference, configuration, socket-api, persistence-remote, agents) | Nothing |
| 6 | Mac | `herdr --version`, `herdr status --json`, `grep` of `~/.config/herdr/config.toml` for toast and sound | Nothing |
| 7 | Mac | `claude --version`, `claude --help`, `claude auth status` (method fields only) | Nothing |
| 8 | Mac | `codex --version`, `codex cloud --help` and its `exec/status/list/apply/diff --help`; `gh agent-task --help`, `create --help`, `view --help`; `cursor-agent --help`, `--version`; `which jules opencode copilot` | Nothing |
| 9 | Mac | `herdr machine list --json`, reduced to a count; wrote a scratch SSH config alias with the target, outside the repo | A scratch file outside the repo |
| 10 | VPS | `herdr --version`, `claude --version`, test for `~/.config/herdr/config.toml` (absent), `herdr machine list --json` (`[]`) | Nothing |
| 11 | VPS | `herdr agent list`, `herdr workspace list`, reduced to counts and states (1 agent, `claude`, `idle`; 5 workspaces) | Nothing |
| 12 | VPS | `herdr pane run --help`, `pane read --help`, `workspace close --help`, `notification show --help` | Nothing |
| 13 | VPS | `herdr workspace create --cwd /tmp --label probe-73-handover --no-focus` | Created throwaway workspace `probe-73-handover` (its own tab and pane) |
| 14 | VPS | `herdr tab rename <probe tab> "probe-73 · Orchestrator · CC"`; `herdr pane run <probe pane>` with `command -v claude`, `command -v herdr`, `echo $TERM_PROGRAM`; `herdr pane read <probe pane> --source recent --lines 20` | The probe tab's label; output in the probe pane only |
| 15 | VPS | `herdr notification show probe-73-test --body "research probe, ignore"` → `{"reason":"shown","shown":true}` | One notification raised by the VPS server, if any client displayed it |
| 16 | VPS | `herdr workspace close <probe workspace>` → `ok`; `herdr workspace list` again: 5 workspaces, none labelled `probe-73…` | Removed the probe workspace; back to the starting state |
| 17 | VPS | `claude --help` (counted `--cloud`, `--teleport`, `--remote-control`: 3), `claude auth status --help`, `claude auth status` (method fields only: claude.ai, first-party) | Nothing |
| 18 | VPS | `herdr agent list` again: 1 agent, `claude`, `idle`, as before | Nothing |
| 19 | VPS | Test for `orchestrate-with-handoff`, `orchestrate-effort`, `orchestrating`, `handover`, `handover-to-herdr`, `herdr`, `close-effort`, `init-effort`, `treehouse` under `~/.claude/skills` and `~/.agents/skills` | Nothing |
| 20 | Mac | Privacy scan of this file: `grep` for home paths, private repository names and IP addresses, and a check that no part of the saved machine's ID, label or target appears (only the generic word "VPS" does) | Nothing |
| 21 | Mac (synthesis, #74) | Corrected the cloud-session start in section 2 and 4.1 (the create form of `claude --cloud` needs an interactive terminal; a local agent's scriptable start is a routine's API trigger), citing [claude-code.md §7](claude-code.md#7-starting-it) and the headless page. Corrected section 3.3's reading of Herdr's toast default after reading `config-reference.json` at `v0.9.2` (default `off` for 0.9.0 and current) | This file only |
| 22 | Cloud session (#78, integration) | Read the three #78 files and the orchestrator's own session probes. Answered the "#69's cloud sessions" TODO in section 4 and the open questions. Softened "needs an interactive terminal" to the first-hand behaviour (start and exit at once). Added `create_session` and `list_sessions` as agent-side start and watch paths, the silent permission-prompt block, and the new-branch push | This file only |
| 23 | Mac, 2026-09-30 | After #66 merged into `main`: read handover, handover-to-herdr, close-effort, orchestrating, orchestrate-effort and set-up-machine's roles table on `main`. Renumbered section 1's steps. Replaced the removed `notify.md` and `closing-an-effort.md`, the Defaults table and `<agent-to-start>` with their current names | This file only |

This research started no cloud agent session, installed nothing, and changed no configuration on either machine. The only VPS writes were the throwaway workspace in rows 13–16, now closed, and the notification in row 15.
