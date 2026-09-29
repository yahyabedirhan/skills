# Running the effort workflow in a Claude Code cloud session

Part of [Research: Claude Code cloud sessions tested from inside one (#78)](https://github.com/yahyabedirhan/skills/issues/78), under [Spec: research cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45). It answers two questions: how instructions and skills reach a cloud session (account, global, project), and how this repo's effort workflow could run there. Written 2026-09-29 from inside a cloud session started with `claude --cloud` on the Mac, Claude Code 2.1.285.

It builds on [cloud-agents.md](cloud-agents.md) (the synthesis: decisions D1-D13, experiments E1-E15) and [cloud-agents-claude-code.md](cloud-agents-claude-code.md) (the docs-only first pass). Neither is repeated here.

Evidence tags:

- **[doc <page>, "<section>"]** Claude Code's docs, pages under `https://code.claude.com/docs/en/`: [cloud-environments](https://code.claude.com/docs/en/cloud-environments) ("env"), [claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web) ("cloud"), [skills](https://code.claude.com/docs/en/skills), [hooks](https://code.claude.com/docs/en/hooks), [settings](https://code.claude.com/docs/en/settings), [memory](https://code.claude.com/docs/en/memory). Fetched as `.md` with `curl` from the cloud VM.
- **[probe]** seen first-hand in this cloud session: by this file's author, or recorded in the session's brief by the orchestrator that ran before it.
- **[cli]** the `skills` CLI 1.7.0 (`npx skills`), its `--help`, its source, and installs into a throwaway home folder.
- **Inferred** reasoned from the above, not seen.
- **Unverified** no source either way.

## Short answer

- **The VM's own `~/.claude/` does load.** The docs' "No" for `~/.claude/skills` and `~/.claude/CLAUDE.md` means *your laptop's* files. Skills placed in the VM's `~/.claude/skills/` load, even mid-session [probe]. So a setup script or a SessionStart hook can install this repo's skills into every cloud session. This corrects the wording of [D6](cloud-agents.md#d6-how-do-skills-and-instructions-reach-a-claude-code-cloud-session) and [cc §5](cloud-agents-claude-code.md#5-what-loads), and makes D6 (c) the likely answer.
- **Best carrier: the environment's setup script.** It installs the skills from a pinned ref with `npx skills add … -g -a claude-code -y`, installs `gh`, and writes a cloud copy of the global instructions that `~/.claude/CLAUDE.md` imports. It reaches every repo that uses the environment, costs about 3 seconds, and is cached as a snapshot. Whether a `~/.claude/CLAUDE.md` written by the script loads is **unverified**.
- **The workflow mostly degrades gracefully.** With every Defaults role unset, the skills already fall back to "this session", `git worktree add` and the harness's notification tool. What breaks: `gh` is missing, Herdr and Treehouse are absent, and there are four cloud facts the skills don't know about: sub-agent depth is 1, background work dies on idle reclaim, the clone is shallow, and the GitHub proxy allows only pull-request GraphQL.
- **Unattended runs need permissions settled up front.** This session blocked on tool approval prompts until the maintainer answered [probe]. An orchestrator left alone needs auto mode, or allow rules for its tools.
- **Sessions can see each other.** The Remote MCP `list_sessions` and `get_session` list every session on the account, including Remote Control sessions on the maintainer's own machines (`environment_kind: "bridge"`), each with its branch, dirty state, unpushed commit count, status bucket and whether it needs action [probe]. A cloud orchestrator can watch a local or VPS session, and the reverse.
- **A new session host is within reach.** The session has a "Claude Code Remote" MCP server whose `create_session` takes a repo, a branch, an `outcome_branch` and a prompt [probe]. A `handover-to-<host>` skill could wrap it. That is a way to hand over from a cloud session without `claude --cloud` or a routine (compare [E11](cloud-agents.md#proposed-experiments)). Nothing was created to test it.

Cost: this session is spending the promo credit first (`get_session` reports the rate-limit type as promotional, resetting 2026-11-05) [probe], which bears on [D12](cloud-agents.md#d12-the-promo-credit-and-the-one-unused-cloud-session).

## 1. The layers in a cloud session

What reaches the model, where each piece comes from, and how long it lasts. "Reclaimed VM" means a session reopened after idle expiry: "a fresh VM with your conversation history restored", and background work lost [doc cloud, "Environment expired"].

| Layer | Who writes it | When it loads | Survives a reclaimed VM | Reaches | Evidence |
|---|---|---|---|---|---|
| **claude.ai account skills** | The maintainer, in claude.ai settings (upload or enable) | Downloaded into `~/.claude/skills/synced/<org>_<account>/` at session start, then checked about every 10 minutes | Yes: downloaded again | Every cloud session, every Cowork session, and every terminal session signed in to the account | [probe]: 9 Anthropic skills and a `manifest.json` there. [doc skills, "Skills synced from claude.ai"] |
| **Harness files** in `~/.claude/` | The platform | Before launch. Claude Code runs with `--settings ~/.claude/launcher-settings.json` (one Stop hook, `permissions.allow: ["Skill"]`). The built-in `session-start-hook` skill | Yes | Every session | [probe] (process arguments, file listing) |
| **VM home `~/.claude/`**: `CLAUDE.md`, `skills/`, `settings.json` | Nobody by default; empty apart from the two rows above. A setup script, a hook or the agent can write it | Skills: at start, and mid-session when installed. `CLAUDE.md`: at launch, like any user file | Only when a setup script wrote it (snapshot, Inferred) or a hook writes it again. A mid-session install is lost | Every repo in that environment | Skills [probe]: 19 installed by `npx skills add` mid-session appeared at once (16 in the model's list; `init-effort`, `orchestrate-with-handoff` and `skill-recap` carry `disable-model-invocation: true`). `CLAUDE.md` and `settings.json` in the VM: Unverified |
| **Repo `CLAUDE.md` / `AGENTS.md`** | The project, committed | At launch, from the clone | Yes (the clone) | That repo | [probe]: this repo's `CLAUDE.md` (`@AGENTS.md`) loaded. [doc env, "What carries over"] |
| **Repo `.claude/skills/`, `agents/`, `commands/`, `rules/`** | The project, committed | At launch | Yes | That repo | [doc env, "What carries over"]. This repo has no `.claude/` |
| **Repo `.claude/settings.json`** (hooks, permissions, `env`) | The project, committed | At launch, **only in a one-repo session** | Yes | That repo | [doc settings, "Settings in cloud sessions"] |
| **Environment setup script** | The maintainer, in the environment dialog on claude.ai/code | Before Claude Code launches, as root; skipped when a cached snapshot exists | Yes, if the snapshot restores it (Inferred: a reopened session gets a fresh VM, which should start from the snapshot) | Every session using that environment, any repo | [doc env, "Setup scripts", "Environment caching"]. This session uses the Default environment, which has none [probe: `CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default`] |
| **SessionStart hook** in repo settings | The project, committed | After launch, on every start and resume; can ask for a skill re-scan with `reloadSkills` | Yes: it runs again | That repo, one-repo sessions only | [doc hooks, "SessionStart decision control"; doc env, "Limitations in cloud sessions"] |
| **Environment variables** | The maintainer, in the environment dialog | Copied once at session start | Yes | Every session using that environment | [doc env, "Set environment variables"]. Readable by anyone who uses the environment |
| **Profile preferences** | The maintainer, in claude.ai settings | Through the session, not a file | Yes | Every session on the account | [probe]: the "avoid em dash" preference reached the model; no file holds it |
| **Server-managed settings** | An organization owner | At session start | Yes | Every session in the organization | [doc env, "What carries over"]. None here [probe] |

Two things from the table matter most:

- **The docs' "No" rows are about the laptop.** "Your user `~/.claude/skills/` … No: live on your machine" [doc env, "What carries over"]. The VM has its own `~/.claude/`, and Claude Code reads it like any home. The skills doc says the same thing from the other side: a hook that writes "into `~/.claude/skills/`" can call `reloadSkills` "so skills the hook installed are available in the same session" [doc hooks, "SessionStart decision control"].
- **`CLAUDE.md` loads only at launch** [doc memory, "Import additional files"]. A setup script runs before launch, so a `~/.claude/CLAUDE.md` it writes should load (Inferred). A hook runs after launch, so a hook passes instructions through `additionalContext` instead, which is capped at 10,000 characters [doc hooks, "Add context for Claude"].

## 2. Carrying the skills and global instructions into cloud sessions

The goal: this repo's skills (with the four from `mattpocock/skills` the effort family needs: `grilling`, `prototype`, `tdd`, `code-review`), and the shared global instructions `~/.config/agents/AGENTS.md` that set-up-machine writes on the Mac.

### The options

| Option | Reaches | Cost | Risk | Verified |
|---|---|---|---|---|
| **(a) Enable the skills on the claude.ai account** (upload each skill) | Every cloud, Cowork and signed-in terminal session | 22 uploads by hand, again on every change | Drift from the repo. On the Mac they sync next to the `npx` installs; a synced skill whose short name is taken runs only as `anthropic-skills:<name>`, so the Mac lists near-duplicates. `syncClaudeAiSkills: false` on the Mac stops that but also drops every synced skill there. Carries no global instructions | Loading: [probe] for the Anthropic skills. Upload of multi-file skills (set-up-machine's scripts): Unverified |
| **(b) Environment setup script** installs the skills and writes the global instructions | Every repo on that environment | One script; about 3 s per install [cli] | Snapshot is up to about 7 days old; an unpinned install drifts silently. The script is readable by anyone who uses the environment (personal environments: only the maintainer) | Install command [cli]; skills in `~/.claude/skills` load [probe]; the script itself and `CLAUDE.md` loading: Unverified |
| **(c) SessionStart hook** in a project's `.claude/settings.json`, gated on `CLAUDE_CODE_REMOTE` | That repo, one-repo sessions | A script and a settings block per project | Runs on every start and resume (latency); runs locally too unless gated; a project hook can't carry personal instructions in a public repo | `reloadSkills` [doc hooks]; the hook itself: Unverified |
| **(d) Commit `.claude/skills/`** in each project | That repo | 22 skill copies per project | Copies drift; every skill update is a commit in every project. [D6](cloud-agents.md#d6-how-do-skills-and-instructions-reach-a-claude-code-cloud-session) already advised against it for this repo | [doc env, "What carries over"] |
| **(e) A cloud-only Defaults table**, written by (b) | Every repo on that environment | One file | A second copy of the global instructions to keep in step with the Mac's | Unverified |
| **(f) Profile preferences** on claude.ai | Every session on the account, everywhere | A few lines | A third copy; also reaches the Mac's claude.ai sessions; length limit unknown | [probe] for one line |

Recommendation: **(b) with (e)** for every repo, and **(c)** only in this repo, installing from the checkout so a session that edits the skills runs its own versions. Keep (a) for skills that must also reach Cowork. Skip (d).

### (b) The setup script

Paste into the environment's **Setup script** field on claude.ai/code. It runs as root before Claude Code starts, must exit 0, and should finish in about five minutes to be cached [doc env, "Script requirements"].

```bash
#!/bin/bash
# Cloud setup: the maintainer's skills and global instructions for every repo on this environment.
# Cached as a snapshot; runs again only when this script or the network setting changes, or after about 7 days.
H="${HOME:-/root}"
SKILLS_REF="<commit sha or tag of yahyabedirhan/skills>"   # pin; change on purpose, which also rebuilds the cache
MATT_REF="<commit sha of mattpocock/skills>"

# gh: listed in the docs, missing in this VM. apt's archive is on the Trusted allowlist.
(apt-get update -qq && apt-get install -y -qq gh) >/dev/null 2>&1 || true

# Skills, for Claude Code only (-a): before launch the CLI can't detect the agent, and without -a it installs for every agent it knows.
npx -y skills add "yahyabedirhan/skills#${SKILLS_REF}" -g -a claude-code -s '*' -y < /dev/null || true
npx -y skills add "mattpocock/skills#${MATT_REF}" -g -a claude-code -s grilling prototype tdd code-review -y < /dev/null || true

# Global instructions: the cloud variant of ~/.config/agents/AGENTS.md (section 3 has its Defaults).
mkdir -p "$H/.config/agents" "$H/.claude"
cat > "$H/.config/agents/AGENTS.md" <<'EOF'
<the cloud variant of the shared global instructions>
EOF
grep -qxF '@~/.config/agents/AGENTS.md' "$H/.claude/CLAUDE.md" 2>/dev/null \
  || echo '@~/.config/agents/AGENTS.md' >> "$H/.claude/CLAUDE.md"
exit 0
```

Notes:

- **Pin the ref.** `npx skills add yahyabedirhan/skills` takes the default branch, `main`, not the checkout [probe]. The CLI has no `--ref` flag, but the source takes `#<ref>`: a branch, a tag or a full commit SHA. `…#<sha> -l` cloned at that SHA and listed 19 skills; `…#skills/cloud-agents` listed 22; a missing ref fails with "Could not find remote branch" [cli]. A GitHub `…/tree/<ref>` URL works too, for a ref without a `/` [cli, `parseSource`].
- **`main` today lacks** `set-up-machine`, `set-up-project`, `maintain-environment` and `treehouse`, and still has `maintain-skills` [cli]. Pin to a commit that has what the workflow needs.
- **`-a claude-code`** copies each skill straight into `~/.claude/skills/<name>` (no `~/.agents/skills` symlink) [cli, into a throwaway home]. Inside this session the CLI printed "Agent detected, installing non-interactively"; a setup script runs before Claude Code, so that detection shouldn't fire (Inferred), hence the explicit flags.
- **The global instructions are personal**, so they can't come from this public repo. The heredoc keeps them in the environment, which only the maintainer uses. Size isn't capped here, unlike a hook's `additionalContext`.
- **set-up-machine's rules** (deny entries, the pre-tool hook) are not applied. Its plan starts `claude -p` to list MCP tools, which has no sign-in before launch. The rule *lines* still arrive, since they sit in the shared file's generated block. The gap is enforcement, not instructions.

### (c) The SessionStart hook

For this repo: install the skills from the checkout, so the session runs the branch's own skills. In `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/cloud-skills.sh",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

And `.claude/hooks/cloud-skills.sh`:

```bash
#!/bin/bash
# Cloud sessions only: install this checkout's skills, then ask Claude Code to re-scan.
[ "$CLAUDE_CODE_REMOTE" = "true" ] || exit 0
npx -y skills add "$CLAUDE_PROJECT_DIR" -g -a claude-code -s '*' -y < /dev/null >/dev/null 2>&1 || true
echo '{"hookSpecificOutput": {"hookEventName": "SessionStart", "reloadSkills": true}}'
exit 0
```

For another project, replace the source with `"yahyabedirhan/skills#${SKILLS_REF:-<sha>}"` and set `SKILLS_REF` as an environment variable, so a new pin needs no commit.

Notes:

- **It runs on every start and resume**, unlike the cached setup script [doc env, "Setup scripts vs. SessionStart hooks"]. The install took 3 s with the `npx` package cached [cli]; on a fresh VM add the package download.
- **Keep stdout to the JSON line.** Plain stdout from a SessionStart hook goes into Claude's context [doc hooks, "SessionStart decision control"].
- **Both matchers.** This session's Claude Code was started with `--resume=<session URL>` [probe, process arguments], so whether a new cloud session reports `startup` or `resume` is Unverified. `startup|resume` covers both.
- **Installing from the checkout** (`npx skills add <local path>`) copied all 22 skills [cli, throwaway home]. On this repo it overrides the pinned copy from (b) by name, which is what a session editing the skills wants.
- **Not in a multi-repo session**, where no repo's hooks run [doc env, "Limitations in cloud sessions"].

## 3. The effort workflow in a cloud session

### Step by step

| Step | In a cloud session | Works as is | Breaks or changes |
|---|---|---|---|
| **init-effort** | The maintainer starts a session on the repo (web, phone, or `claude --cloud` on the Mac) | Naming, the handoff file | `<worktree-tool>` unset means `git worktree add ../<repo>-<effort>`: a sibling folder the session wasn't started in. In the cloud the session's own checkout should be the worktree: `git switch -c <branch>` there (Inferred). A new project needs `gh repo create`: no `gh`, and the GitHub MCP tools reach only attached repos [probe: scoped to this repo]. `create_repository` and `add_repo` exist but weren't tried |
| **Thinking**: grilling, prototype | The same session, with the maintainer in the browser or on the phone | Question rounds; idle expiry only loses background work, and the conversation is restored [doc cloud, "Environment expired"] | A prototype the maintainer should click needs a way to reach it; there's no preview URL in the docs (Unverified) |
| **to-spec, to-tickets** | GitHub tracker | Writing the spec and tickets | Both follow `issue-tracker-github.md`, which says `gh issue create`. `gh` is missing [probe]. Installed, `gh issue` uses GraphQL, and the proxy serves "only a pinned set of GraphQL operations for pull-request workflows" [doc env, "GitHub proxy"], so it may get a 403 (Inferred). REST (`gh api repos/…/issues`, or `curl` with the placeholder token) passes: `GET …/sub_issues` returned 200 [probe]. The GitHub MCP tools cover issues too [probe] |
| **handoff, handover** | Commit, push, starting prompt | Commit and push. Pushing the session branch worked, and so did pushing a new branch the session named itself (`skills/…`, created from the start branch) [probe]. The docs' "works only against the session's current working branch" [doc env, "GitHub proxy"] means the checked-out branch, whatever its name, and `get_session` then tracks that branch as the session's [probe]. So the effort branch naming convention can hold in the cloud. Pushing to an *existing* branch the session didn't create (an effort branch made on the Mac) is untested | Mechanism: see `<session-host>` below. The starting prompt `/orchestrate-with-handoff <path>` names a skill with `disable-model-invocation: true`: it runs only when the prompt arrives as a typed slash command. Whether a prompt passed to `claude --cloud "<prompt>"` or `create_session` is expanded as one is Unverified |
| **orchestrate-with-handoff, orchestrate-effort** | The orchestrator must be the top-level session | Reading, planning, show-me, committing | Sub-agent depth is 1 (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`) [probe]. Delegates can't start their own sub-agents; this file's author, a delegate, has no Agent tool [probe]. The orchestrating skill already tells delegates to review synchronously. An orchestrator started as someone's sub-agent gets no delegates at all |
| **Delegates** (implement, one worktree each) | Sub-agents with worktree isolation, on the VM's 4 vCPU / 16 GB | Sub-agents work [probe: this run]. Local commits and `git worktree` need no push | [D8](cloud-agents.md#d8-what-does-an-orchestrator-delegate-to-and-from-which-base)'s base-branch fix applies here too. Parallel delegates share 4 vCPU (Inferred: two or three at a time) |
| **Integrate and push** | Cherry-pick, commit, push per batch | Yes | The shallow clone [probe] is fine for cherry-picks |
| **Waiting on the maintainer** | The one blocked question | The conversation survives reclaim | Background sub-agents and shell commands die on reclaim [doc cloud, "Environment expired"]. The discipline already fits: ask only when nothing can continue. The one addition is to push and stop background work before asking. A tool permission prompt also blocks the session: the first calls to several MCP tools sat as pending actions, "Waiting on permission", with the session in the blocked bucket, until approved [probe]. An unattended orchestrator needs auto mode or allow rules for every tool it uses, or it stalls silently until someone opens it |
| **Final review, to-pr** | A sub-agent reviews; the PR opens | `create_pull_request` worked [probe]. The session UI also has **Create PR** | to-pr calls `gh pr view`/`gh pr edit`. With `gh` installed they go through the pinned PR GraphQL set, probably allowed (Inferred); without it the model maps them to the MCP tools. The PR head is the session branch (`claude/<slug>`) unless the orchestrator checks out and pushes the effort branch, as this research did with its own branch [probe] |
| **Notify** | `<notification-method>` | Unset falls back to the harness tool: `PushNotification` exists as a deferred tool [probe]; whether it reaches the phone is Unverified. The PR is the done signal ([D9](cloud-agents.md#d9-how-does-done-or-blocked-reach-the-maintainer-from-off-the-mac) (d)) | `subscribe_pr_activity` can wake the session on review comments [probe: tool present] |
| **close-effort** | The maintainer says "go" in the same session, reopened if it was reclaimed | Reading *Things to be aware of*, carry-over tickets (MCP or REST), merging (`merge_pull_request` exists [probe], not tried) | `gh pr checks`, `gh run list`: use `get_check_run`/`actions_list`. The merge proofs need history: `git fetch --unshallow` first. Deleting a remote branch under push protection: Unverified. Herdr steps (8, 9) are skipped; the VM is the worktree, so step 9 returns nothing. `archive_session` could close the effort's other cloud sessions (Unverified) |

### The Parameters in the cloud

Proposed values for a cloud Defaults table, written by the setup script (option (e)). Each is Inferred unless marked.

| Role | Cloud value | Why |
|---|---|---|
| `session-host` | `none` now. Later a new host, for example `claude-code-cloud`, whose `handover-to-claude-code-cloud` skill calls the Claude Code Remote MCP `create_session` (`source_url`, `source_revision` and `outcome_branch` set to the effort branch, the starting prompt as `prompt`) and confirms with `get_session` | `none` falls back to "this session", which is right for thinking and building in one session. The MCP tools are present [probe]; `outcome_branch` "pushes directly to this branch" per its tool description [probe]. No session was created to test it. A child session inherits the environment, so it runs the same setup script (per the tool description) |
| `worktree-tool` | A value meaning "this checkout": either a tiny how-to skill (for example `session-checkout`: `git switch -c <branch>` in place, never a sibling folder), or a line in the cloud instructions saying so | `none` means `git worktree add` into a sibling folder the session can't be moved into; handover step 1 and init-effort step 4 would then work outside the session's checkout |
| `notification-method` | Unset | The fallback is already the harness tool, `PushNotification` [probe: present] |
| `agent-to-start` | On the Mac, for the paste path: `claude --cloud`. Inside the cloud: unset | `claude --cloud "<prompt>"` from the maintainer's terminal created this session and returned at once with a URL [probe]. It clones the current branch from GitHub, so the handover's "pushed" check matters |
| `skills-repo` | `yahyabedirhan/skills` | Same as the Mac |
| `path-to-skills-repo` | The clone's path when the session is on this repo, else `none` | The VM has no other clone |

The global instructions copied verbatim from the Mac would name Herdr and Treehouse. Every skill then looks for `handover-to-herdr` or `treehouse`, finds the tool unreachable, and falls back. That works but costs a detour each time, so the cloud copy should say `none` for them.

## 4. Suggestions

In order. Each names what it unblocks in [cloud-agents.md](cloud-agents.md).

| # | Suggestion | Cost | Risk | Unblocks |
|---|---|---|---|---|
| 1 | **Add a personal cloud environment with the setup script in section 2 (b)**, pinned to a commit that has the whole effort family, plus the four `mattpocock/skills`. Start one session on it and check `/skills` and a quote of a rule line | Minutes on claude.ai; no repo change | Low. A bad script fails the session start (it exits 0 on every path above) | D6 (c) settled; the "skills and `AGENTS.md` loading" half of E1 |
| 2 | **Write the cloud variant of the global instructions**, with the Defaults in section 3 (`session-host none`, the checkout rule for `worktree-tool`, notifications unset), and embed it in the script | An hour: one file, derived from the Mac's | A second copy drifts. Later, set-up-machine could print it (a `cloud` target) | D1 (c) for single-session efforts; D9 for cloud (harness push plus the PR) |
| 3 | **Make the orchestrator's starting prompt work without a typed slash command.** Either drop `disable-model-invocation` from `orchestrate-with-handoff`, or have handover write, for a cloud target, "Read the handoff at `<path>` and run the orchestrate-effort skill" | A line or two in two skills | Low. A model-invocable `orchestrate-with-handoff` could start on a stray mention (its description is narrow) | Handing over through `claude --cloud` or `create_session`; E11 becomes optional |
| 4 | **Four small edits for cloud facts**: orchestrating says the orchestrator is a top-level session and pushes and stops background work before it asks; close-effort runs `git fetch --unshallow` before its proofs; `issue-tracker-github.md` prefers REST (`gh api`) over `gh issue` for writes | Small edits | Low; each holds on the Mac too | D8 (a) (alongside its base-branch fix); close-effort in the cloud |
| 5 | **A SessionStart hook in this repo** (section 2 (c)), installing from the checkout | Two small files | Runs locally only if the gate is wrong; adds a few seconds per start | Cloud sessions that edit these skills test their own versions |
| 6 | **Experiment, then a how-to skill for `create_session`.** One child session on a throwaway branch of this repo with `source_revision` and `outcome_branch` set: does it get the environment's skills, push to that branch, and appear in `list_sessions`? Then archive it. If it works, write `handover-to-claude-code-cloud` | One session of plan usage | Low on a public repo and throwaway branch | D1 (c) with separate thinking and building sessions; [#15](https://github.com/yahyabedirhan/skills/issues/15) continuations in the cloud |
| 7 | **Settle permissions before an unattended run**: start orchestrator sessions in auto mode, or commit allow rules (for the GitHub and Remote MCP tools it uses) to the project's `.claude/settings.json`. The orchestrating skill's "notify when blocked" can't fire when the block is a permission prompt | A few allow rules | Allow rules in a public repo are visible, and they widen what any session there may do | Unattended D1 (c) runs |
| 8 | **Use `list_sessions` / `get_session` as the cross-session status read**: a cloud orchestrator reads a Mac or VPS session on Remote Control, and a Remote Control session reads a cloud one (branch, dirty, unpushed, blocked, needs action) | None to try; a line in the skills that watch | Reads other sessions' private titles and repos, which must stay out of public files | [#16](https://github.com/yahyabedirhan/skills/issues/16) (see each other's state), D9 and D10 |
| 9 | **Don't** upload all skills to claude.ai or commit `.claude/skills/` copies into projects | None | None | Keeps D6's advice against restructuring |

## Open questions

- Does a `~/.claude/CLAUDE.md` written by the setup script load, and does a `~/.claude/settings.json` there apply alongside the launcher's `--settings` file?
- Does a reopened (reclaimed) session start from the environment's snapshot, so setup-script files survive, and does a SessionStart hook see `startup` or `resume` in a new cloud session?
- Is `/orchestrate-with-handoff <path>` expanded as a command when it arrives as the prompt of `claude --cloud` or `create_session`?
- A session pushes to whatever branch it has checked out, including a new one it named [probe]. Can it push to an existing branch it didn't create (an effort branch pushed from the Mac), delete a remote branch, or push to a branch that holds someone else's commits?
- Does the permission mode chosen at creation (`claude --cloud` takes none on the command line) cover MCP tools, or do Remote MCP tools prompt even in auto mode?
- Does `gh issue create` get a 403 from the proxy's GraphQL filter?
- Can an environment variable raise `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, or does the session override it, as it does `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` [doc cloud, "Manage context"]?
- Does `PushNotification` reach the phone from a cloud session?
- Is the Claude Code Remote MCP server (`create_session`) available to a local session on the Mac too? If so, a Mac agent could start cloud work without a routine.
- `mattpocock/skills`' `code-review` shares its name with a built-in `code-review` listed in this session. Which one does `/code-review` run?

## Exploration log

All on 2026-09-29, in this cloud session's VM. The throwaway homes were under the session's scratch folder, outside the repo.

| # | Where | Command or action | What it changed |
|---|---|---|---|
| 1 | VM | Read the brief, `README.md`, the orchestrating, handover, handover-to-herdr, orchestrate-with-handoff, orchestrate-effort, init-effort, close-effort, set-up-machine (and its Claude Code and global-instructions references), set-up-project, treehouse skills, `where-things-go.md`, `cloud-agents.md`, `cloud-agents-claude-code.md` | Nothing |
| 2 | VM | `curl` of the `.md` form of `cloud-environments`, `skills`, `hooks`, `settings`, `memory`, `claude-code-on-the-web` (all 200) | Copies in the scratch folder |
| 3 | VM | `npx -y skills add --help`; read `parseSource` in the CLI's `dist/cli.mjs` for ref syntax | Nothing (the `npx` cache already held the package) |
| 4 | VM → GitHub | `curl` of `api.github.com/repos/yahyabedirhan/skills/commits/main`; `npx skills add` with `-l` for `#<main sha>`, `#skills/cloud-agents`, `#nonexistent-ref-xyz`, and `mattpocock/skills` | Nothing (list only) |
| 5 | VM (scratch) | `HOME=<scratch>/fakehome npx skills add 'yahyabedirhan/skills#<main sha>' -g -a claude-code -s '*' -y`, the same for `#skills/cloud-agents` (timed: 3 s), and for the local checkout path | Three throwaway homes in the scratch folder; the real `~` untouched |
| 6 | VM | `ls -la ~/.claude`, `launcher-settings.json` (hook commands left out), Claude Code's process arguments, `apt-cache policy gh`, `grep disable-model-invocation`, `grep` for `gh` calls in the skills | Nothing |
| 7 | VM | Read the orchestrator's notes on its own probes (push of a new named branch, `get_session`, `list_sessions`, permission prompts, rate-limit type); used their generic shape only | Nothing |
| 8 | VM | `git branch -r`, `git reflog` of the remote-tracking branches, `git rev-parse --is-shallow-repository` | Nothing |
| 9 | VM (worktree) | Wrote this file; not committed | This file |
