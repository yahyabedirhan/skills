# Running the effort workflow in a Claude Code cloud session

Part of [Research: Claude Code cloud sessions tested from inside one (#78)](https://github.com/yahyabedirhan/skills/issues/78), under [Spec: research cloud agents (#45)](https://github.com/yahyabedirhan/skills/issues/45). It answers two questions:

- How do instructions and skills reach a cloud session (account, global, project)?
- How could this repo's effort workflow run there?

The author wrote this file on 2026-09-29, from inside a cloud session. `claude --cloud` on the Mac started that session, on Claude Code 2.1.285.

It builds on [README.md](README.md) and [claude-code.md](claude-code.md). The first is the synthesis, with decisions D1-D13 and experiments E1-E20. The second is the docs-only first pass. This file repeats neither.

**Updated 2026-09-30** after "Every harness and project is set up and audited from the skills" (#66) merged into `main`. The changes:

- `main` now holds the whole effort family, so a pin to `main` is enough.
- The Defaults table is now the **environment defaults** table of the shared global instructions. Its `agent-to-start` role is now `agent`.
- An agent applies set-up-machine from its references. There is no plan script.
- close-effort's steps have new numbers.

The probes below are unchanged.

Evidence tags:

- **[doc `<page>`, "`<section>`"]** Claude Code's docs, pages under `https://code.claude.com/docs/en/`: [cloud-environments](https://code.claude.com/docs/en/cloud-environments) ("env"), [claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web) ("cloud"), [skills](https://code.claude.com/docs/en/skills), [hooks](https://code.claude.com/docs/en/hooks), [settings](https://code.claude.com/docs/en/settings), [memory](https://code.claude.com/docs/en/memory). The author fetched them as `.md` with `curl` from the cloud VM.
- **[probe]** seen first-hand in this cloud session. Either this file's author saw it, or the orchestrator that ran before it recorded it in the session's brief.
- **[cli]** the `skills` CLI 1.7.0 (`npx skills`), its `--help`, its source, and installs into a throwaway home folder.
- **Inferred** reasoned from the above, not seen.
- **Unverified** no source either way.

## Short answer

- **The VM's own `~/.claude/` does load.** The docs say "No" for `~/.claude/skills` and `~/.claude/CLAUDE.md`. That "No" means *your laptop's* files. Skills placed in the VM's `~/.claude/skills/` load, even mid-session [probe]. So a setup script or a SessionStart hook can install this repo's skills into every cloud session. This corrects the wording of [D6](README.md#d6-how-do-skills-and-instructions-reach-a-claude-code-cloud-session) and [cc §5](claude-code.md#5-what-loads). It also makes D6 (c) the likely answer.
- **Best carrier: the environment's setup script.** It installs the skills from a pinned ref with `npx skills add … -g -a claude-code -y`. It also installs `gh`. Then it writes a cloud copy of the global instructions, which `~/.claude/CLAUDE.md` imports. It reaches every repo that uses the environment and costs about 3 seconds. The environment caches its result as a snapshot. Whether a `~/.claude/CLAUDE.md` that the script writes will load is **unverified**.
- **Most of the workflow still works, through fallbacks.** Suppose every role in the environment defaults is `none`. Then the skills already fall back to "this session", `git worktree add` and the harness's notification tool. These things break:
  - `gh` is missing.
  - Herdr and Treehouse are absent.
  - The skills don't know four cloud facts. Sub-agent depth is 1. Background work dies on idle reclaim. The clone is shallow. The GitHub proxy blocks GraphQL entirely ([session-probe §4](session-probe.md#4-github-proxy)).
- **An unattended run needs its permissions settled first.** This session stopped at tool permission prompts. The prompts waited for approval before the calls ran. The record doesn't say who or what approved them. The session was in auto mode at the time [probe]. An orchestrator left alone needs allow rules for its tools. Auto mode alone didn't prevent these prompts.
- **Sessions can see each other.** The Remote MCP tools `list_sessions` and `get_session` list every session on the account. That includes Remote Control sessions on the maintainer's own machines (`environment_kind: "bridge"`). For each session they show its branch, dirty state, unpushed commit count, status bucket and whether it needs action [probe]. A cloud orchestrator can watch a local or VPS session. A local or VPS session can also watch a cloud one.
- **A new session host is possible.** The session has a "Claude Code Remote" MCP server. Its `create_session` takes a repo, a branch, an `outcome_branch` and a prompt [probe]. A `handover-to-<host>` skill could wrap it. That gives a way to hand over from a cloud session without `claude --cloud` or a routine (compare [E11 and E17](README.md#proposed-experiments)). This research created no session to test it.

Cost: this session spends the promo credit first. `get_session` reports the rate-limit type as promotional, with a reset on 2026-11-05 [probe]. This bears on [D12](README.md#d12-the-promo-credit-and-the-one-unused-cloud-session).

## 1. The layers in a cloud session

This section shows what reaches the model, where each piece comes from, and how long it lasts. "Reclaimed VM" means a session reopened after idle expiry. The docs call it "a fresh VM with your conversation history restored", and the session loses its background work [doc cloud, "Environment expired"].

| Layer | Who writes it | When it loads | Survives a reclaimed VM | Reaches | Evidence |
|---|---|---|---|---|---|
| **claude.ai account skills** | The maintainer, in claude.ai settings (upload or enable) | The platform downloads them into `~/.claude/skills/synced/<org>_<account>/` at session start | Yes: they download again | Every cloud session, every Cowork session, and every terminal session signed in to the account | [probe]: 9 Anthropic skills and a `manifest.json` there. [doc skills, "Skills synced from claude.ai"] |
| **Harness files** in `~/.claude/` | The platform | Before launch. Claude Code runs with `--settings ~/.claude/launcher-settings.json` (one Stop hook, `permissions.allow: ["Skill"]`). The built-in `session-start-hook` skill | Yes | Every session | [probe] (process arguments, file listing) |
| **VM home `~/.claude/`**: `CLAUDE.md`, `skills/`, `settings.json` | Nobody by default. It is empty apart from the two rows above. A setup script, a hook or the agent can write it | Skills: at start, and mid-session after an install. `CLAUDE.md`: at launch, like any user file | Only when a setup script wrote it (snapshot, Inferred) or a hook writes it again. The VM loses a mid-session install | Every repo in that environment | Skills [probe]: `npx skills add` installed 19 mid-session, and they appeared at once. The model's list showed 16, because `init-effort`, `orchestrate-with-handoff` and `skill-recap` carry `disable-model-invocation: true`. `CLAUDE.md` and `settings.json` in the VM: Unverified |
| **Repo `CLAUDE.md` / `AGENTS.md`** | The project, committed | At launch, from the clone | Yes (the clone) | That repo | [probe]: this repo's `CLAUDE.md` (`@AGENTS.md`) loaded. [doc env, "What carries over"] |
| **Repo `.claude/skills/`, `agents/`, `commands/`, `rules/`** | The project, committed | At launch | Yes | That repo | [doc env, "What carries over"]. This repo has no `.claude/` |
| **Repo `.claude/settings.json`** (hooks, permissions, `env`) | The project, committed | At launch, **only in a one-repo session** | Yes | That repo | [doc settings, "Settings in cloud sessions"] |
| **Environment setup script** | The maintainer, in the environment dialog on claude.ai/code | Before Claude Code launches, as root. It doesn't run when a cached snapshot exists | Yes, if the snapshot restores it (Inferred: a reopened session gets a fresh VM, which should start from the snapshot) | Every session using that environment, any repo | [doc env, "Setup scripts", "Environment caching"]. This session uses the Default environment, which has none [probe: `CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default`] |
| **SessionStart hook** in repo settings | The project, committed | After launch, on every start and resume. It can ask for a skill re-scan with `reloadSkills` | Yes: it runs again | That repo, one-repo sessions only | [doc hooks, "SessionStart decision control"; doc env, "Limitations in cloud sessions"] |
| **Environment variables** | The maintainer, in the environment dialog | The platform copies them once at session start | Yes | Every session using that environment | [doc env, "Set environment variables"]. Anyone who uses the environment can read them |
| **Profile preferences** | The maintainer, in claude.ai settings | Through the session, not a file | Yes | Every session on the account | [probe]: the "avoid em dash" preference reached the model. No file holds it |
| **Server-managed settings** | An organization owner | At session start | Yes | Every session in the organization | [doc env, "What carries over"]. None here [probe] |

Two things from the table matter most:

- **The docs' "No" rows are about the laptop.** "Your user `~/.claude/skills/` … No: live on your machine" [doc env, "What carries over"]. The VM has its own `~/.claude/`. Claude Code reads it like any home. The hooks doc says the same thing from the other side. A hook that writes "into `~/.claude/skills/`" can call `reloadSkills` "so skills the hook installed are available in the same session" [doc hooks, "SessionStart decision control"].
- **`CLAUDE.md` loads only at launch** [doc memory, "Import additional files"]. A setup script runs before launch, so a `~/.claude/CLAUDE.md` that it writes should load (Inferred). A hook runs after launch. So a hook passes instructions through `additionalContext` instead. That field has a cap of 10,000 characters [doc hooks, "Add context for Claude"].

## 2. Carrying the skills and global instructions into cloud sessions

The goal is to carry two things into cloud sessions:

- this repo's skills, with the four from `mattpocock/skills` that the effort family needs: `grilling`, `prototype`, `tdd`, `code-review`
- the shared global instructions `~/.config/agents/AGENTS.md`, which set-up-machine writes on the Mac

### The options

| Option | Reaches | Cost | Risk | Verified |
|---|---|---|---|---|
| **(a) Enable the skills on the claude.ai account** (upload each skill) | Every cloud, Cowork and signed-in terminal session | 22 uploads by hand, again on every change | The copies drift from the repo. On the Mac they sync next to the `npx` installs. When another skill already has a synced skill's short name, the synced one runs only as `anthropic-skills:<name>`. So the Mac lists near-duplicates. `syncClaudeAiSkills: false` on the Mac stops that. But it also drops every synced skill there. This option carries no global instructions | Loading: [probe] for the Anthropic skills. Upload of multi-file skills (set-up-machine's scripts): Unverified |
| **(b) Environment setup script** installs the skills and writes the global instructions | Every repo on that environment | One script. About 3 s per install [cli] | The snapshot can be up to about 7 days old. An unpinned install drifts without warning. Anyone who uses the environment can read the script (in a personal environment, only the maintainer) | Install command: [cli]. Skills in `~/.claude/skills` load: [probe]. The script itself and `CLAUDE.md` loading: Unverified |
| **(c) SessionStart hook** in a project's `.claude/settings.json`, gated on `CLAUDE_CODE_REMOTE` | That repo, one-repo sessions | A script and a settings block per project | It runs on every start and resume, which adds latency. It runs locally too unless gated. A project hook can't carry personal instructions in a public repo | `reloadSkills`: [doc hooks]. The hook itself: Unverified |
| **(d) Commit `.claude/skills/`** in each project | That repo | 22 skill copies per project | Copies drift. Every skill update is a commit in every project. [D6](README.md#d6-how-do-skills-and-instructions-reach-a-claude-code-cloud-session) already advised against it for this repo | [doc env, "What carries over"] |
| **(e) Cloud-only environment defaults**, written by (b) | Every repo on that environment | One file | A second copy of the global instructions to keep in step with the Mac's | Unverified |
| **(f) Profile preferences** on claude.ai | Every session on the account, everywhere | A few lines | A third copy. It also reaches the Mac's claude.ai sessions. Its length limit is unknown | [probe] for one line |

Recommendation: use **(b) with (e)** for every repo. Use **(c)** only in this repo, and install from the checkout, so a session that edits the skills runs its own versions. Keep (a) for skills that must also reach Cowork. Skip (d).

### (b) The setup script

Paste this into the environment's **Setup script** field on claude.ai/code. It runs as root before Claude Code starts, and it must exit 0. It should finish in about five minutes, so that the environment can cache it [doc env, "Script requirements"].

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

# Global instructions: the cloud variant of ~/.config/agents/AGENTS.md (section 3 has its environment defaults).
mkdir -p "$H/.config/agents" "$H/.claude"
cat > "$H/.config/agents/AGENTS.md" <<'EOF'
<the cloud variant of the shared global instructions>
EOF
grep -qxF '@~/.config/agents/AGENTS.md' "$H/.claude/CLAUDE.md" 2>/dev/null \
  || echo '@~/.config/agents/AGENTS.md' >> "$H/.claude/CLAUDE.md"
exit 0
```

Notes:

- **Pin the ref.** `npx skills add yahyabedirhan/skills` takes the default branch, `main`, not the checkout [probe]. The CLI has no `--ref` flag. But the source takes `#<ref>`: a branch, a tag or a full commit SHA. `…#<sha> -l` cloned at that SHA and listed 19 skills. `…#skills/cloud-agents` listed 22. A missing ref fails with "Could not find remote branch" [cli]. A GitHub `…/tree/<ref>` URL works too, for a ref without a `/` [cli, `parseSource`].
- **`main` lacked** `set-up-machine`, `set-up-project`, `maintain-environment` and `treehouse` on 2026-09-29. It still had `maintain-skills` [cli]. #66 merged on 2026-09-30. Since then, `main` has all four and no `maintain-skills`: 22 skills, the whole effort family. Pin to a commit of `main`.
- **`-a claude-code`** copies each skill straight into `~/.claude/skills/<name>`, with no `~/.agents/skills` symlink [cli, into a throwaway home]. Inside this session the CLI printed "Agent detected, installing non-interactively". A setup script runs before Claude Code, so that detection shouldn't fire (Inferred). That is why the script passes explicit flags.
- **The global instructions are personal**, so they can't come from this public repo. The heredoc keeps them in the environment, which only the maintainer uses. Here their size has no cap, unlike a hook's `additionalContext`.
- **set-up-machine's rules** (deny entries, the pre-tool hook) don't take effect. An agent runs set-up-machine: it reads its harness references and asks for one approval. A setup script runs before any agent starts, so nothing applies the rules there. The rule *lines* still arrive, because they sit in the shared file's generated block. So the gap is enforcement, not instructions. The script could write the hook's wiring from `references/claude-code.md` by hand (untested).

### (c) The SessionStart hook

For this repo: install the skills from the checkout, so the session runs the branch's own skills. Put this in `.claude/settings.json`:

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

For another project, replace the source with `"yahyabedirhan/skills#${SKILLS_REF:-<sha>}"`. Then set `SKILLS_REF` as an environment variable, so a new pin needs no commit.

Notes:

- **It runs on every start and resume**, unlike the cached setup script [doc env, "Setup scripts vs. SessionStart hooks"]. The install took 3 s with the `npx` package already in the cache [cli]. On a fresh VM, add the time of the package download.
- **Keep stdout to the JSON line.** Plain stdout from a SessionStart hook goes into Claude's context [doc hooks, "SessionStart decision control"].
- **Both matchers.** Claude Code in this session ran with `--resume=<session URL>` [probe, process arguments]. So it is Unverified whether a new cloud session reports `startup` or `resume`. `startup|resume` covers both.
- **An install from the checkout** (`npx skills add <local path>`) copied all 22 skills [cli, throwaway home]. On this repo it overrides the pinned copy from (b) by name. A session that edits the skills wants exactly that.
- **It doesn't run in a multi-repo session**, because no repo's hooks run there [doc env, "Limitations in cloud sessions"].

## 3. The effort workflow in a cloud session

### Step by step

| Step | In a cloud session | Works as is | Breaks or changes |
|---|---|---|---|
| **init-effort** | The maintainer starts a session on the repo (web, phone, or `claude --cloud` on the Mac) | Naming, the handoff file | When `<worktree-tool>` is unset, the skill uses `git worktree add ../<repo>-<effort>`. That makes a sibling folder that the session didn't start in. In the cloud, the session's own checkout should be the worktree: `git switch -c <branch>` there (Inferred). A new project needs `gh repo create`. But there is no `gh`, and the GitHub MCP tools reach only attached repos [probe: scoped to this repo]. `create_repository` and `add_repo` exist, but nobody tried them |
| **Thinking**: grilling, prototype | The same session, with the maintainer in the browser or on the phone | Question rounds. Idle expiry loses only background work, and the platform restores the conversation [doc cloud, "Environment expired"] | A prototype that the maintainer should click needs a way to reach it. The docs mention no preview URL (Unverified) |
| **to-spec, to-tickets** | GitHub tracker | Writing the spec and tickets | Both follow `issue-tracker-github.md`, which says `gh issue create`. `gh` is missing [probe]. Once installed, `gh issue` uses GraphQL, and the proxy blocks GraphQL entirely. Every query got `403` [probe; [session-probe §4](session-probe.md#4-github-proxy)]. Yet the docs say the proxy serves "a pinned set of GraphQL operations for pull-request workflows" [doc env, "GitHub proxy"]. REST passes: `gh api repos/…/issues`, or `curl` with the placeholder token. `GET …/sub_issues` returned 200 [probe]. The GitHub MCP tools cover issues too [probe] |
| **handoff, handover** | Commit, push, starting prompt | Commit and push. A push of the session branch worked. A push of a new branch that the session named itself also worked (`skills/…`, created from the start branch) [probe]. The docs say the proxy "works only against the session's current working branch" [doc env, "GitHub proxy"]. That means the checked-out branch, whatever its name. `get_session` then tracks that branch as the session's [probe]. So the effort branch naming convention can hold in the cloud. A push to an *existing* branch that the session didn't create (an effort branch made on the Mac) is untested | Mechanism: see `<session-host>` below. The starting prompt `/orchestrate-with-handoff <path>` names a skill with `disable-model-invocation: true`. That skill runs only when the prompt arrives as a typed slash command. It is Unverified whether a prompt passed to `claude --cloud "<prompt>"` or `create_session` expands as one |
| **orchestrate-with-handoff, orchestrate-effort** | The orchestrator must be the top-level session | Reading, planning, show-me, committing | Sub-agent depth is 1 (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`) [probe]. Delegates can't start their own sub-agents. This file's author, a delegate, has no Agent tool [probe]. The orchestrating skill already tells delegates to review synchronously. An orchestrator that starts as someone's sub-agent gets no delegates at all |
| **Delegates** (implement, one worktree each) | Sub-agents with worktree isolation, on the VM's 4 vCPU / 15.7 GiB | Sub-agents work [probe: this run]. Local commits and `git worktree` need no push | [D8](README.md#d8-what-does-an-orchestrator-delegate-to-and-from-which-base)'s base-branch fix applies here too. Parallel delegates share 4 vCPU (Inferred: two or three at a time) |
| **Integrate and push** | Cherry-pick, commit, push per batch | Yes | The shallow clone [probe] is fine for cherry-picks |
| **Waiting on the maintainer** | The one blocked question | The conversation survives reclaim | Background sub-agents and shell commands die on reclaim [doc cloud, "Environment expired"]. The discipline already fits: ask only when nothing can continue. The one addition: push and stop background work before you ask. A tool permission prompt also blocks the session. The first calls to several MCP tools sat as pending actions, "Waiting on permission", until someone approved them. Meanwhile the session sat in the blocked bucket [probe]. The session was in auto mode at the time. An unattended orchestrator needs allow rules for every tool it uses. Otherwise it stalls silently until someone opens it |
| **Final review, to-pr** | A sub-agent reviews, and the PR opens | `create_pull_request` worked [probe]. The session UI also has **Create PR** | to-pr calls `gh pr view`/`gh pr edit`. Those use GraphQL, which the proxy blocks entirely [probe; [session-probe §4](session-probe.md#4-github-proxy)]. So even with `gh` installed, the model has to map them to the MCP tools or REST. The proxy points to `/pulls/{n}/ccr/` routes for draft state, auto-merge and review threads. The PR head is the session branch (`claude/<slug>`), unless the orchestrator checks out and pushes the effort branch. This research did that with its own branch [probe] |
| **Notify** | `<notification-method>` | When it is unset, the skills fall back to the harness tool: `PushNotification` exists as a deferred tool [probe]. Whether it reaches the phone is Unverified. The PR is the done signal ([D9](README.md#d9-how-does-done-or-blocked-reach-the-maintainer-from-off-the-mac) (d)) | `subscribe_pr_activity` can wake the session on review comments [probe: tool present] |
| **close-effort** | The maintainer says "go" in the same session. If the platform reclaimed it, the maintainer reopens it first | The read of the pull request's description and the handoff (step 3), carry-over tickets (MCP or REST), and the merge (`merge_pull_request` exists [probe], but nobody tried it) | For `gh pr checks` and `gh run list`, use `get_check_run`/`actions_list`. The merge proofs of step 7 need history, so run `git fetch --unshallow` first. Deletion of a remote branch under push protection: Unverified. Step 8 frees the session's own worktree through `<session-host>`. In the cloud there is no host, and the VM is the checkout. So the report ends the close. `archive_session` could close the effort's other cloud sessions (Unverified). But close-effort leaves sessions open for the maintainer |

### The Parameters in the cloud

These are proposed values for the cloud environment defaults. The setup script writes them (option (e)). Each is Inferred unless marked.

| Role | Cloud value | Why |
|---|---|---|
| `session-host` | `none` now. Later a new host, for example `claude-code-cloud`. Its `handover-to-claude-code-cloud` skill calls the Claude Code Remote MCP `create_session`, then confirms with `get_session`. The call sets `source_url`, `source_revision` and `outcome_branch` to the effort branch, and the starting prompt as `prompt` | `none` falls back to "this session". That is right for thinking and building in one session. The MCP tools are present [probe]. Per its tool description, `outcome_branch` "pushes directly to this branch" [probe]. This research created no session to test it. A child session inherits the environment, so it runs the same setup script (per the tool description) |
| `worktree-tool` | A value that means "this checkout". Either a tiny how-to skill (for example `session-checkout`: `git switch -c <branch>` in place, never a sibling folder), or a line in the cloud instructions that says so | `none` means `git worktree add` into a sibling folder. The session can't move into that folder. Handover step 1 and init-effort step 4 would then work outside the session's checkout |
| `notification-method` | Unset | The fallback is already the harness tool, `PushNotification` [probe: present] |
| `agent` | On the Mac, for the paste path: `claude --cloud`. Inside the cloud: unset | `claude --cloud "<prompt>"` from the maintainer's terminal created this session and returned at once with a URL [probe]. It clones the current branch from GitHub, so the handover's "pushed" check matters |
| `skills-repo` | `yahyabedirhan/skills` | Same as the Mac |
| `path-to-skills-repo` | The clone's path when the session is on this repo, else `none` | The VM has no other clone |

A verbatim copy of the Mac's global instructions would name Herdr and Treehouse. Every skill would then look for `handover-to-herdr` or `treehouse`, find the tool unreachable, and fall back. That works, but it costs a detour each time. So the cloud copy should say `none` for them.

## 4. Suggestions

The suggestions are in order. Each names what it unblocks in [README.md](README.md).

| # | Suggestion | Cost | Risk | Unblocks |
|---|---|---|---|---|
| 1 | **Add a personal cloud environment with the setup script in section 2 (b).** Pin it to a commit that has the whole effort family, plus the four `mattpocock/skills`. Start one session on it. Check `/skills` and a quote of a rule line | Minutes on claude.ai. No repo change | Low. A bad script fails the session start (it exits 0 on every path above) | D6 (c) settled. The "skills and `AGENTS.md` loading" half of E1 |
| 2 | **Write the cloud variant of the global instructions**, and embed it in the script. Give it the environment defaults in section 3: `session-host none`, the checkout rule for `worktree-tool`, and notifications unset | An hour: one file, derived from the Mac's | A second copy drifts. Later, set-up-machine could print it (a `cloud` target) | D1 (c) for single-session efforts. D9 for cloud (harness push plus the PR) |
| 3 | **Make the orchestrator's starting prompt work without a typed slash command.** Either drop `disable-model-invocation` from `orchestrate-with-handoff`. Or have handover write, for a cloud target, "Read the handoff at `<path>` and run the orchestrate-effort skill" | A line or two in two skills | Low. A model-invocable `orchestrate-with-handoff` could start on a stray mention (its description is narrow) | Handing over through `claude --cloud` or `create_session`. E11 becomes optional |
| 4 | **Three small edits for cloud facts, one per file.** (1) orchestrating says that the orchestrator is a top-level session, and that it pushes and stops background work before it asks. (2) close-effort runs `git fetch --unshallow` before its proofs. (3) `issue-tracker-github.md` prefers REST (`gh api`) over `gh issue` for writes | Small edits | Low. Each holds on the Mac too | D8 (a) (alongside its base-branch fix). close-effort in the cloud |
| 5 | **A SessionStart hook in this repo** (section 2 (c)), installing from the checkout | Two small files | It runs locally only if the gate is wrong. It adds a few seconds per start | Cloud sessions that edit these skills test their own versions |
| 6 | **Experiment, then a how-to skill for `create_session`.** Start one child session on a throwaway branch of this repo, with `source_revision` and `outcome_branch` set. Does it get the environment's skills? Does it push to that branch and appear in `list_sessions`? Then archive it. If it works, write `handover-to-claude-code-cloud` | One session of plan usage | Low on a public repo and throwaway branch | D1 (c) with separate thinking and building sessions. [#15](https://github.com/yahyabedirhan/skills/issues/15) continuations in the cloud |
| 7 | **Settle permissions before an unattended run.** Commit allow rules to the project's `.claude/settings.json`, for the GitHub and Remote MCP tools it uses. Auto mode alone didn't stop this session's prompts. The orchestrating skill's "notify when blocked" can't fire when the block is a permission prompt | A few allow rules | Allow rules in a public repo are visible. They also widen what any session there may do | Unattended D1 (c) runs |
| 8 | **Use `list_sessions` / `get_session` as the cross-session status read.** A cloud orchestrator reads a Mac or VPS session on Remote Control. A Remote Control session reads a cloud one (branch, dirty, unpushed, blocked, needs action) | None to try. A line in the skills that watch | It reads other sessions' private titles and repos. Those must stay out of public files | [#16](https://github.com/yahyabedirhan/skills/issues/16) (see each other's state), D9 and D10 |
| 9 | **Don't** upload all skills to claude.ai or commit `.claude/skills/` copies into projects | None | None | Keeps D6's advice against restructuring |

## Open questions

- Does a `~/.claude/CLAUDE.md` that the setup script writes load? Does a `~/.claude/settings.json` there apply alongside the launcher's `--settings` file?
- Does a reopened (reclaimed) session start from the environment's snapshot, so that setup-script files survive? Does a SessionStart hook see `startup` or `resume` in a new cloud session?
- Does Claude Code expand `/orchestrate-with-handoff <path>` as a command when it arrives as the prompt of `claude --cloud` or `create_session`?
- A session pushes to whatever branch it has checked out, including a new one it named [probe]. Can it push to an existing branch it didn't create (an effort branch pushed from the Mac)? Can it delete a remote branch, or push to a branch that holds someone else's commits?
- This session was in auto mode. Its first Remote MCP calls still waited for approval. Does an allow rule in the project's settings stop that? What mode does `claude --cloud` start in? It takes no mode on the command line.
- Settled since: `gh issue create` would get a 403, because the proxy blocks GraphQL entirely ([session-probe §4](session-probe.md#4-github-proxy)).
- Can an environment variable raise `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`? Or does the session override it, as it does `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` [doc cloud, "Manage context"]?
- Does `PushNotification` reach the phone from a cloud session?
- Is the Claude Code Remote MCP server (`create_session`) available to a local session on the Mac too? If so, a Mac agent could start cloud work without a routine.
- `mattpocock/skills`' `code-review` shares its name with a built-in `code-review` listed in this session. Which one does `/code-review` run?

## Exploration log

All on 2026-09-29, in this cloud session's VM, unless a row says otherwise. The throwaway homes sat in the session's scratch folder, outside the repo.

| # | Where | Command or action | What it changed |
|---|---|---|---|
| 1 | VM | Read the brief, `README.md`, the orchestrating, handover, handover-to-herdr, orchestrate-with-handoff, orchestrate-effort, init-effort, close-effort, set-up-machine (and its Claude Code and global-instructions references), set-up-project, treehouse skills, `where-things-go.md`, `README.md`, `claude-code.md` | Nothing |
| 2 | VM | `curl` of the `.md` form of `cloud-environments`, `skills`, `hooks`, `settings`, `memory`, `claude-code-on-the-web` (all 200) | Copies in the scratch folder |
| 3 | VM | `npx -y skills add --help`. Read `parseSource` in the CLI's `dist/cli.mjs` for ref syntax | Nothing (the `npx` cache already held the package) |
| 4 | VM → GitHub | `curl` of `api.github.com/repos/yahyabedirhan/skills/commits/main`. Then `npx skills add` with `-l` for `#<main sha>`, `#skills/cloud-agents`, `#nonexistent-ref-xyz`, and `mattpocock/skills` | Nothing (list only) |
| 5 | VM (scratch) | `HOME=<scratch>/fakehome npx skills add 'yahyabedirhan/skills#<main sha>' -g -a claude-code -s '*' -y`, the same for `#skills/cloud-agents` (timed: 3 s), and for the local checkout path | Three throwaway homes in the scratch folder. The real `~` stayed untouched |
| 6 | VM | `ls -la ~/.claude`, `launcher-settings.json` (hook commands left out), Claude Code's process arguments, `apt-cache policy gh`, `grep disable-model-invocation`, `grep` for `gh` calls in the skills | Nothing |
| 7 | VM | Read the orchestrator's notes on its own probes (push of a new named branch, `get_session`, `list_sessions`, permission prompts, rate-limit type). Used only their generic shape | Nothing |
| 8 | VM | `git branch -r`, `git reflog` of the remote-tracking branches, `git rev-parse --is-shallow-repository` | Nothing |
| 9 | VM (worktree) | Wrote this file. Did not commit it | This file |
| 10 | VM (integration) | Aligned the file with the first-hand probes in three places. The proxy blocks GraphQL entirely (Short answer, to-spec and to-pr rows, open questions). Permission prompts wait for approval in auto mode, and allow rules are the fix. The experiment range is E1-E20 | This file only |
| 11 | Mac, 2026-09-30 | After #66 merged: listed `skills/` on `main` (22 skills). Read set-up-machine, its roles table, close-effort, orchestrate-with-handoff and `issue-tracker-github.md` on `main`. Updated the names of the environment defaults and the `agent` role, the pin note, set-up-machine's gap and the close-effort row. Suggestions 3 and 4 are still open: `orchestrate-with-handoff` keeps `disable-model-invocation`, and nothing on `main` mentions `--unshallow` | This file only |
