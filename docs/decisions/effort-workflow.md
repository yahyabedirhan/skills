# Decisions: effort workflow

The decisions behind the effort skills: `init-effort`, `orchestrating`, `orchestrate-effort`, `orchestrate-with-handoff`, `handover`, `handover-to-herdr`, `settle-effort`, `settle-session`, and the `implement`, `handoff`, `to-spec` and `to-tickets` forks they rely on. This file is for maintaining those skills and is never installed. Entries follow the shape in [index.md](index.md). Older entries keep the skill names of their time, such as `close-effort` and `init-effort-with-herdr`.

## 2026-09-24: the family mirrors grilling

- **Status:** accepted
- **Context:** The effort skills need a structure.
- **Options:** None considered.
- **Choice and why:** `orchestrating` is the discipline, like `grilling`. The other skills are entry points that each add one thing: a start, a handoff to read, or Herdr automation.
- **Consequences:** None.

## 2026-09-24: a skill another skill calls is model-invoked

- **Status:** accepted
- **Context:** A skill can't load a user-invoked one. A prompt that one agent sends another through Herdr counts as typed input.
- **Options:** None considered.
- **Choice and why:** A skill that another skill calls is model-invoked; a skill only the user starts is user-invoked. `orchestrating`, `orchestrate-effort`, `orchestrate-with-herdr` and the `implement` fork are model-invoked with narrow triggers. `init-effort`, `init-effort-with-herdr` and `orchestrate-with-handoff` are user-invoked.
- **Consequences:** Each user-invoked skill ships `agents/openai.yaml` with `allow_implicit_invocation: false`, because Codex ignores `disable-model-invocation`.

## 2026-09-24: an effort gets its own branch, worktree and pull request

- **Status:** accepted
- **Context:** Some work needs isolation and some doesn't.
- **Options:** None considered.
- **Choice and why:** An effort is a feature, a new app, a refactor or a re-architecture, and it gets its own branch, worktree and pull request. Routine data upkeep runs in the current checkout.
- **Consequences:** Each project lists its own routine work in its instructions.

## 2026-09-24: the worktree is decided at the start, not at the build

- **Status:** accepted
- **Context:** Creating the worktree only at build time leaves thinking artifacts on the default branch, some merged and some not.
- **Options:** Create the worktree at the build.
- **Choice and why:** Spec, tickets and handoff are born on the effort's branch.
- **Consequences:** The orchestrator works wherever it finds itself.

## 2026-09-24: two paths, plain and Herdr

- **Status:** replaced by [2026-09-28: init-effort is the one start](#2026-09-28-init-effort-is-the-one-start) and [2026-09-28: Herdr from anywhere](#2026-09-28-herdr-from-anywhere)
- **Context:** Desktop apps can't drive Herdr or Treehouse.
- **Options:** None considered.
- **Choice and why:** `init-effort` uses the environment's own worktree feature, else `git worktree`, and its handover is a prompt the user pastes. `init-effort-with-herdr` and `orchestrate-with-herdr` automate the same steps with Treehouse and Herdr.
- **Consequences:** Two start skills to keep in step.

## 2026-09-24: Treehouse owns worktrees, Herdr owns the view, git owns the branch

- **Status:** replaced by [2026-09-29: the effort skills name roles, not tools](#2026-09-29-the-effort-skills-name-roles-not-tools)
- **Context:** Several tools can create worktrees. `git worktree add` and `herdr worktree create` bypass Treehouse's pool.
- **Options:** `git worktree add` or `herdr worktree create`: they bypass the pool.
- **Choice and why:** Treehouse owns worktrees, because its pool keeps dependencies installed and refuses to destroy unfinished work. Herdr owns the view and sessions, and git owns the branch. `treehouse.md` and `herdr.md` in `init-effort-with-herdr` hold the daily operations, so agents don't rediscover them from `--help`.
- **Consequences:** Those files are the place to grow the workflow's commands, such as running builds on a remote machine later. This stays true of the maintainer's own setup.

## 2026-09-24: new branches don't track the default branch

- **Status:** accepted
- **Context:** A new branch that tracks the default branch makes "matches its remote" compare against the default branch, and a bare push targets it.
- **Options:** None considered.
- **Choice and why:** Create new branches with `--no-track`. The first push sets the real upstream.
- **Consequences:** The lesson later moved to the tools; see [2026-09-30: the no-track lesson lives with the tool](#2026-09-30-the-no-track-lesson-lives-with-the-tool).

## 2026-09-24: the thinking session owns the clean ending

- **Status:** replaced by [2026-09-28: handover is its own skill, and the mechanism is another](#2026-09-28-handover-is-its-own-skill-and-the-mechanism-is-another)
- **Context:** Someone must save the thinking work before the build starts.
- **Options:** None considered.
- **Choice and why:** The thinking session writes the handoff, commits and pushes everything, then hands over. On the Herdr path, that is step 1 of `orchestrate-with-herdr`, which the thinking session runs.
- **Consequences:** None.

## 2026-09-24: the family writes handoffs itself

- **Status:** replaced by [2026-09-28: handoff is forked from Matt Pocock's skill](#2026-09-28-handoff-is-forked-from-matt-pococks-skill)
- **Context:** Matt Pocock's `handoff` skill saves to a temp folder and is user-invoked. The handoff is part of the effort's record, and a fresh worktree must see it.
- **Options:** Call the upstream `handoff` skill: it saves outside the repository and can't be loaded by a skill.
- **Choice and why:** The family states the few requirements inline. A handoff lives in the repository, by convention at `.handoff/<date>-<effort>.md`, committed with the spec and tickets.
- **Consequences:** None.

## 2026-09-24: the handoff names the thinking session

- **Status:** accepted
- **Context:** The orchestrator and later sessions may need the thinking session's messages.
- **Options:** None considered.
- **Choice and why:** The handoff names the thinking session, so they can refer back to it.
- **Consequences:** None.

## 2026-09-24: the handover prompt carries the worktree, branch and thinking session

- **Status:** replaced by [2026-09-28: the starting prompt is always one line](#2026-09-28-the-starting-prompt-is-always-one-line)
- **Context:** A thinking session ends in `init-effort` or `orchestrate-with-herdr`.
- **Options:** None considered.
- **Choice and why:** The handover prompt has one shape on both paths: `/orchestrate-with-handoff <handoff>`, the worktree and branch, and the thinking session. It is written out in both skills.
- **Consequences:** None.

## 2026-09-24: the thinking session stops after the handover and stays open

- **Status:** accepted
- **Context:** The user may want to return to the thinking session.
- **Options:** None considered.
- **Choice and why:** The thinking session stops after the handover and stays open. On the Herdr path, its tab is labelled as the thinking tab, and the new one as the orchestrator.
- **Consequences:** See the tab-label entries below.

## 2026-09-24: the agent to start is read from the user's instructions

- **Status:** replaced by [2026-09-29: the effort skills name roles, not tools](#2026-09-29-the-effort-skills-name-roles-not-tools)
- **Context:** Users run different harnesses.
- **Options:** None considered.
- **Choice and why:** The agent to start is the user's preference, read from their instructions. The default is `claude`. Other options are `codex`, `opencode` and `cursor`.
- **Consequences:** Where that preference should live long-term stayed open.

## 2026-09-24: the orchestrator trusts its delegates

- **Status:** accepted
- **Context:** Redoing a delegate's checks repeats its work.
- **Options:** None considered.
- **Choice and why:** A delegate builds, tests and reviews its own ticket. The orchestrator reads the report against the acceptance criteria and doesn't redo the checks.
- **Consequences:** None.

## 2026-09-24: orchestrating doesn't prescribe how to delegate

- **Status:** accepted
- **Context:** The user is still experimenting with delegating tickets to Herdr tabs.
- **Options:** None considered.
- **Choice and why:** Delegates are sub-agents by default. An entry-point skill that wants another mechanism, such as Herdr tabs, says so itself.
- **Consequences:** Delegating tickets to Herdr tabs is not built yet.

## 2026-09-24: implement is forked to be model-invoked

- **Status:** accepted
- **Context:** Upstream `implement` is user-invoked and always commits.
- **Options:** Use upstream: an orchestrator's sub-agents can't load it.
- **Choice and why:** The fork is model-invoked, so sub-agents can load it. It commits only when the delegating agent doesn't.
- **Consequences:** None.

## 2026-09-24: the orchestrator commits each ticket

- **Status:** replaced by [2026-09-28: tickets run in parallel, each delegate in its own worktree](#2026-09-28-tickets-run-in-parallel-each-delegate-in-its-own-worktree)
- **Context:** Delegates share one checkout.
- **Options:** None considered.
- **Choice and why:** The orchestrator commits each ticket, so each ticket's changes stay apart.
- **Consequences:** None.

## 2026-09-24: tool references hold the tool, skills hold the workflow

- **Status:** accepted
- **Context:** Commands and the order of steps change for different reasons.
- **Options:** None considered.
- **Choice and why:** `treehouse.md` and `herdr.md` carry each tool's everyday commands and gotchas. The order of steps, such as closing an effort after its merge, lives in the skill that runs it.
- **Consequences:** None.

## 2026-09-24: tabs are labelled effort, role, harness

- **Status:** replaced by [2026-09-30: tabs are labelled harness, role, topic](#2026-09-30-tabs-are-labelled-harness-role-topic)
- **Context:** The user must tell sessions and harnesses apart at a glance.
- **Options:** None considered.
- **Choice and why:** Label tabs `<effort> · <role> · <harness>`, appended to an existing label rather than replacing it. The harness is short: `CC` for Claude Code, `Codex`, `OpenCode`, `Cursor`.
- **Consequences:** None.

## 2026-09-24: the orchestrator reads lifecycle.md every time

- **Status:** accepted
- **Context:** Without `lifecycle.md`, the orchestrator lacks the context of where its part sits.
- **Options:** Read it only when asked.
- **Choice and why:** The orchestrator reads `lifecycle.md` every time it orchestrates.
- **Consequences:** None.

## 2026-09-24: the final branch review is delegated too

- **Status:** accepted
- **Context:** The orchestrator's context should stay on coordination.
- **Options:** None considered.
- **Choice and why:** Delegate the final branch review and its fixes, like the tickets.
- **Consequences:** None.

## 2026-09-24: prompts use each harness's skill syntax

- **Status:** accepted
- **Context:** Claude Code starts a skill with `/name`, Codex with `$name`.
- **Options:** Two copies of each prompt.
- **Choice and why:** The skills that write prompts for another agent say so in one line.
- **Consequences:** None.

## 2026-09-24: decisions are recorded here, not as ADRs

- **Status:** accepted
- **Context:** Most workflow decisions are easy to reverse, which fails the ADR bar. The history still matters to whoever changes the workflow next.
- **Options:** ADRs.
- **Choice and why:** Record the decisions in this file.
- **Consequences:** None.

## 2026-09-24: a tab that has handed over is marked settled at the end

- **Status:** replaced by [2026-09-30: a settled tab gets settled at the start of its label](#2026-09-30-a-settled-tab-gets-settled-at-the-start-of-its-label)
- **Context:** The user asked for a marker that says the session is finished and the tab is only a record. A role name doesn't say that.
- **Options:** Relabel the tab `thinking` at handover.
- **Choice and why:** Append ` [settled]` to the label.
- **Consequences:** The `thinking` role label from `init-effort-with-herdr` still names the tab while the session is live.

## 2026-09-28: to-spec and to-tickets are forked to be model-invoked

- **Status:** accepted
- **Context:** Upstream they are user-invoked. A thinking session started with a pasted or sent prompt couldn't load them, and wrote the spec by hand or asked the user to type the commands.
- **Options:** None considered.
- **Choice and why:** Fork them, as `implement` was. The forks drop `disable-model-invocation`, set `allow_implicit_invocation: true` for Codex, and gain a "Use when" clause. Everything else stays as upstream, so a diff against upstream shows only these changes.
- **Consequences:** The upstream installs are removed once the forks are installed.

## 2026-09-28: a local tracker keeps an effort's spec and tickets in .efforts/

- **Status:** accepted
- **Context:** Upstream `to-tickets` wrote tickets to `.scratch/<feature-slug>/issues/`, which the folder standard makes ignored.
- **Options:** None considered.
- **Choice and why:** On a local-files tracker, the spec and tickets live in `.efforts/<effort>/` (`spec.md`, `issues/<NN>-<slug>.md`), tracked. `.scratch/` is ignored and holds only temporary agent files.
- **Consequences:** Without an effort, `<effort>` is a short slug for the feature.

## 2026-09-28: to-tickets names a ticket by its title

- **Status:** accepted
- **Context:** A bare number means nothing to a reader without the tracker open.
- **Options:** None considered.
- **Choice and why:** Name a ticket by its title, never by its number alone (`#12 Add login`, not `#12`): in the breakdown, in "Blocked by", and when talking to the user.
- **Consequences:** None.

## 2026-09-28: handover is its own skill, and the mechanism is another

- **Status:** accepted
- **Context:** This replaces the 2026-09-24 entries that put the handover in `orchestrate-with-herdr`, such as [the thinking session owns the clean ending](#2026-09-24-the-thinking-session-owns-the-clean-ending). That skill's name described the receiving side while the sending side ran it.
- **Options:** None considered.
- **Choice and why:** `handover` owns the flow of starting a session outside this one: the readiness checklist, the starting prompt, picking a mechanism, and confirming the new session started. `handover-to-herdr` is the Herdr mechanism.
- **Consequences:** Together they replace `orchestrate-with-herdr`.

## 2026-09-28: a handover can happen at any point, from any session

- **Status:** accepted
- **Context:** A desktop-app session may hand an effort to Herdr, and a thinking session may hand over to a fresh thinking session.
- **Options:** Only from a thinking session to an orchestrator.
- **Choice and why:** Any session can hand over at any point. Only the orchestrator has a receiving skill. Any other session starts from a one-line "continue from the handoff" prompt.
- **Consequences:** None.

## 2026-09-28: orchestrate-with-handoff stays the receiver, tool-agnostic

- **Status:** accepted
- **Context:** The handoff is the input on every path. A desktop-app session isn't a Herdr tab, so the handing session may not be reachable.
- **Options:** A Herdr-specific receiver.
- **Choice and why:** Keep one receiver. It no longer assumes the handing session is reachable. When the handoff says it can't be reached, the orchestrator decides open questions itself and records them for the pull request.
- **Consequences:** None.

## 2026-09-28: handoff is forked from Matt Pocock's skill

- **Status:** accepted
- **Context:** This replaces [2026-09-24: the family writes handoffs itself](#2026-09-24-the-family-writes-handoffs-itself). Upstream saves to a temp folder and is user-invoked.
- **Options:** None considered.
- **Choice and why:** Fork it as model-invocable. The fork writes `.handoff/<date>-<topic>.md` in the repository, and leaves it uncommitted for the session that hands over.
- **Consequences:** *Handoff* is the document; *handover* is starting the other session.

## 2026-09-28: handover and handover-to-herdr are model-invoked

- **Status:** accepted
- **Context:** The handing session runs them itself, and `init-effort` points at them. `orchestrate-with-handoff`'s one-line starting prompt arrives as a real slash command.
- **Options:** None considered.
- **Choice and why:** `handover` and `handover-to-herdr` are model-invoked. `orchestrate-with-handoff` stays user-invoked.
- **Consequences:** None.

## 2026-09-28: the starting prompt is always one line

- **Status:** accepted
- **Context:** This replaces [2026-09-24: the handover prompt carries the worktree, branch and thinking session](#2026-09-24-the-handover-prompt-carries-the-worktree-branch-and-thinking-session). `herdr agent prompt` delivers text as a paste. Claude Code collapses a paste of more than three lines or 800 characters into pasted content, which never runs as a command. A four-line handover prompt left the orchestrator asking for a go-ahead, while a one-line prompt sent the same way started the skill (see `docs/research/agent-skill-invocation.md`).
- **Options:** None considered.
- **Choice and why:** The prompt is one line: `/orchestrate-with-handoff <handoff>`, or "Continue from the handoff at <path>." Everything else goes in the handoff.
- **Consequences:** None.

## 2026-09-28: receiving the handover is the maintainer's go-ahead

- **Status:** accepted
- **Context:** A receiving session asked for a go-ahead before it started.
- **Options:** None considered.
- **Choice and why:** The receiving session starts work without asking. It asks only for inputs only the maintainer has. The handing session collects those before it hands over.
- **Consequences:** None.

## 2026-09-28: init-effort hands over through handover

- **Status:** accepted
- **Context:** `init-effort` printed its own prompt.
- **Options:** None considered.
- **Choice and why:** `init-effort` hands over through `handover`, so the prompt's shape lives in one place.
- **Consequences:** None.

## 2026-09-28: Herdr from anywhere

- **Status:** accepted
- **Context:** This replaces the claim in [2026-09-24: two paths, plain and Herdr](#2026-09-24-two-paths-plain-and-herdr) that desktop apps can't drive Herdr.
- **Options:** Check `HERDR_ENV`: it exists only inside a Herdr pane.
- **Choice and why:** `handover-to-herdr` checks the server with `herdr status`, so a desktop-app session can hand over to a Herdr tab. Its safety comes from targeting instead: explicit IDs from Herdr's JSON, `--no-focus`, never `--current`.
- **Consequences:** The upstream `herdr` skill isn't forked. `handover-to-herdr` states the rule and carries the commands it needs.

## 2026-09-28: from outside a pane, worktree open always gets --workspace

- **Status:** accepted
- **Context:** Without `--workspace`, the source workspace depends on state, and the call can fail with `linked_worktree_source`.
- **Options:** None considered.
- **Choice and why:** Pass the repository's own workspace. A plain workspace on the main checkout works.
- **Consequences:** None.

## 2026-09-28: a "trust this folder?" prompt goes to the maintainer

- **Status:** accepted
- **Context:** A new worktree path shows the prompt at agent start, which Herdr reports as `agent_not_ready`. It is a security decision.
- **Options:** None considered.
- **Choice and why:** The skill reads the screen and asks the maintainer to accept it in the tab.
- **Consequences:** None.

## 2026-09-28: the handover is fire-and-forget

- **Status:** accepted
- **Context:** `agent prompt --wait` waits for the agent to settle, and times out on a long run.
- **Options:** `agent prompt --wait`.
- **Choice and why:** `agent wait --until working` confirms the handover. The handing session doesn't check on the new one afterwards.
- **Consequences:** None.

## 2026-09-28: the handing session stays on its own checkout

- **Status:** accepted
- **Context:** A desktop session should keep its thread on the default branch.
- **Options:** None considered.
- **Choice and why:** The handing session writes into the worktree by absolute path and commits with `git -C`. The worktree branches from the local default branch when the work builds on unpushed commits there.
- **Consequences:** Pre-handover commits run one per call, because a rejected chain can stop halfway.

## 2026-09-28: the orchestrator starts from a clean worktree

- **Status:** accepted
- **Context:** A worktree can still reach the orchestrator dirty after the thinking session's clean ending. Protecting files "another session owns" cost a whole run: paths named one by one, no full format, every status view cluttered. It bought nothing.
- **Options:** Protect the uncommitted files.
- **Choice and why:** Before the first delegate, the orchestrator commits any uncommitted changes in their own commit.
- **Consequences:** None.

## 2026-09-28: "done" is every acceptance criterion ticked on evidence

- **Status:** accepted
- **Context:** An orchestrator had changed only a `Status:` line and read that as the skill's rule, because the skill never said what "done" meant.
- **Options:** None considered.
- **Choice and why:** The delegate's report gives evidence per criterion, and the orchestrator ticks only what it shows. A criterion shown only outside the checkout stays unticked with a note. On a local tracker, the ticks and status land in the ticket's own commit. On a hosted one, the issue's checklist is ticked and the issue closed.
- **Consequences:** "Done" never has to choose between ticking an unproven box and leaving a proven one blank.

## 2026-09-28: delegates stop what they start, and the orchestrator sweeps for leftovers

- **Status:** accepted
- **Context:** A verification server ran for hours after its delegate finished. A backgrounded formatter with an empty file list waited on stdin for an hour.
- **Options:** None considered.
- **Choice and why:** `implement` stops its servers, tabs, background commands and watchers before reporting, and names anything left running on purpose. The orchestrator checks each report for leftovers and sweeps its own before saying a run is finished.
- **Consequences:** `implement` also carries the one-line zsh gotcha behind the formatter case.

## 2026-09-28: tickets run in parallel, each delegate in its own worktree

- **Status:** accepted
- **Context:** This replaces the shared checkout of [2026-09-24: the orchestrator commits each ticket](#2026-09-24-the-orchestrator-commits-each-ticket). A seven-ticket run took 74 minutes one after another, because "only disjoint files" serialised tickets whose real constraint was one installed app.
- **Options:** Serialise tickets that touch the same files: conflicts are cheap at integration.
- **Choice and why:** Run tickets in parallel by default, each delegate in its own git worktree. Only the step that uses a shared resource, such as an installed app, one real UI, a port or a database, is serialised. A delegate commits once in its worktree. The orchestrator cherry-picks it with `--no-commit`, ticks its criteria, and commits it as the ticket's own commit. It then tests, installs and checks the real app once per batch.
- **Consequences:** Machine-specific limits, such as a small VPS that builds serially, belong to the cloud-agents effort.

## 2026-09-28: the orchestrator sets each ticket's review depth

- **Status:** accepted
- **Context:** Per-ticket two-reviewer passes took about a quarter of each ticket's time, and duplicated the branch review at delivery.
- **Options:** A full review per ticket.
- **Choice and why:** `implement` reviews at the depth its brief sets: none, one light pass, or `code-review`. It runs `code-review` only when nobody delegated it.
- **Consequences:** A large or risky ticket still gets its own review.

## 2026-09-28: a delegate brief points and names what comes back

- **Status:** accepted
- **Context:** Briefs carried paraphrases, documented recipes and commit rules.
- **Options:** None considered.
- **Choice and why:** A brief carries paths, the review depth, the shared resources left to the orchestrator, and the report's shape: evidence per criterion, proof that no temporary verification code is left, and anything left running.
- **Consequences:** None.

## 2026-09-28: verification prefers the real app over off-screen renders

- **Status:** accepted
- **Context:** Off-screen renders cost time, and missed a bug that the first real-screen check found.
- **Options:** Off-screen renders.
- **Choice and why:** Verify in the real app.
- **Consequences:** This named no tool. [2026-10-02: real-app checks run in a headless browser](#2026-10-02-real-app-checks-run-in-a-headless-browser) narrows it.

## 2026-09-28: one folder standard for agent records

- **Status:** accepted
- **Context:** Records were scattered across `.scratch/`, `.handoff/` and `.humanlayer/`.
- **Options:** None considered.
- **Choice and why:** Define the standard once, in `orchestrating/folders.md`:
  - `.handoff/<date>-<topic>.md`, tracked.
  - `.efforts/<effort>/` for a local tracker's spec and tickets, tracked.
  - `docs/agents/issue-tracker.md` for which tracker the repo uses.
  - `docs/assets/<topic>/` for screenshots worth keeping.
  - One ignored `.scratch/` for agent notes, logs, temp files and the pull request description source, with `.claude/worktrees/` also ignored.

  It lives beside `lifecycle.md`, because the orchestrator reads that every run. A reference file lets `to-pr` and `init-effort` point at it without loading the whole lifecycle.
- **Consequences:** Each writer points at the one file instead of restating paths.

## 2026-09-28: to-pr saves its description source to .scratch/

- **Status:** accepted
- **Context:** The `.humanlayer/` prefix came with the fork of HumanLayer's `visual-pr`. Upstream saved to HumanLayer's product task folder, synced to its cloud, not to git. Without that cloud nothing syncs, and GitHub already holds the description.
- **Options:** A `.prs/` folder or `tmp/`: one ignored folder is enough.
- **Choice and why:** `to-pr` drops the `.humanlayer/` prefix and saves to `.scratch/pr-<number>/description.md`. The source is temporary.
- **Consequences:** The licence file stays as the fork's credit.

## 2026-09-28: the PR debrief is not a separate file

- **Status:** accepted
- **Context:** The spec replaced the debrief with `to-pr`'s last section, things to be aware of.
- **Options:** A separate debrief file.
- **Choice and why:** The debrief lives in the description: in the pull request, and in its `.scratch/` source.
- **Consequences:** None.

## 2026-09-28: the folder standard is tracker-agnostic

- **Status:** accepted
- **Context:** Projects use hosted or local trackers.
- **Options:** None considered.
- **Choice and why:** With a hosted tracker, the spec and tickets live there and a project has no `.efforts/`. With a local one, `.efforts/` holds them.
- **Consequences:** This repo tracks on GitHub, so it gets `docs/agents/issue-tracker.md` and no `.efforts/`.

## 2026-09-28: this repo migrates itself, other projects through tickets

- **Status:** accepted
- **Context:** Existing projects follow the old layout.
- **Options:** None considered.
- **Choice and why:** This repo's `.gitignore` gains `.scratch/` and `.claude/worktrees/`; `.handoff/` stays. Other projects migrate through tickets in their own trackers, following the migration table in `folders.md`.
- **Consequences:** `to-spec` and `to-tickets` already write `.efforts/` and don't point at `folders.md`, to keep their diff against upstream to the intended change.

## 2026-09-28: the orchestrator rarely asks

- **Status:** accepted
- **Context:** A request dropped into a progress update ("send the client ID any time") left the maintainer to decode what it was, why it was needed and where to answer.
- **Options:** Batch questions at stop points: a question the orchestrator can answer itself costs the maintainer more than a decision they review in the pull request.
- **Choice and why:** The thinking session gathers every input only the maintainer has, such as credentials, IDs, accounts and external setup, before the handover, while the maintainer is present. The handoff records them. A secret stays out of chat and committed files, and the handoff says where it lives. The orchestrator decides every other open question itself, keeps a list of those decisions with their reasons, and puts them in the pull request's last section.
- **Consequences:** None.

## 2026-09-28: the orchestrator interrupts only for a critical blocker

- **Status:** accepted
- **Context:** The maintainer asked for a prose question to be redrawn, and called the result "a lot better".
- **Options:** Use show-me for every question.
- **Choice and why:** Interrupt only when nothing can continue: a notification plus one question in a fixed shape. The question comes first, then the facts it rests on, a table of options with the pick marked, and a one-line close. **show-me** adds a picture only where it helps weigh the options.
- **Consequences:** This folds in "an orchestrator asks its questions with show-me".

## 2026-09-28: notifications at two moments only, from one reference

- **Status:** accepted
- **Context:** The built-in notification tool reported success under one terminal multiplexer while nothing arrived. The working fix, a macOS command, is one machine's answer and will change.
- **Options:** Hard-code the notification command in the skills.
- **Choice and why:** `orchestrating/notify.md` holds when (the pull request is delivered; nothing can continue without the maintainer) and what (one line under 200 characters, leading with what the maintainer acts on). Every skill that notifies points at it. How is left to the maintainer's own agent instructions, else the harness's built-in tool.
- **Consequences:** None.

## 2026-09-28: three working-style points live in the skills that own them

- **Status:** accepted
- **Context:** Three working-style points kept being rediscovered each session and copied into handoffs, where the next session might not read them. How the maintainer likes to work otherwise depends on the project.
- **Options:** A shared working-style file.
- **Choice and why:** Each point goes where it is used:
  - Decisions come with their facts, options and a pick (`orchestrating`; `grilling` is upstream and not forked, so it is left as is).
  - Visual reports follow `show-me`, which the others point at.
  - Issues and pull requests are named by title, never by a number alone (`orchestrating`, `to-pr`, and `to-tickets` already).
- **Consequences:** None.

## 2026-09-28: init-effort is the one start

- **Status:** accepted
- **Context:** This replaces the start part of [2026-09-24: two paths, plain and Herdr](#2026-09-24-two-paths-plain-and-herdr). `init-effort` and `init-effort-with-herdr` differed only in the mechanism: the worktree tool and how the thinking session starts.
- **Options:** None considered.
- **Choice and why:** Retire `init-effort-with-herdr`. `init-effort` creates the worktree with the project's own tool: Treehouse by default when installed, else the environment's feature or `git worktree`. It suggests starting the thinking session in a Herdr tab through `handover-to-herdr`, with this session or a pasted prompt as fallbacks.
- **Consequences:** None.

## 2026-09-28: init-effort also starts a brand-new project

- **Status:** accepted
- **Context:** A session once improvised a new project with no commit, no remote and no worktree, and had to skip Treehouse.
- **Options:** None considered.
- **Choice and why:** A new project differs from an effort only before the worktree exists. It gets a folder under the maintainer's projects folder (named in their instructions, never hard-coded), `git init`, a README, a licence, the folder standard's setup (`.gitignore`, `docs/agents/issue-tracker.md`), a first commit and `gh repo create`. The first commit and `origin` let Treehouse lease worktrees of it, so the project's first effort then runs the normal path.
- **Consequences:** Public or private is asked every time, because publishing a repo can't be undone quietly.

## 2026-09-28: the thinking session starts from a handoff and a one-line prompt

- **Status:** accepted
- **Context:** A pasted multi-line prompt, or one that named user-only skills, left an earlier thinking session writing the spec by hand.
- **Options:** None considered.
- **Choice and why:** `init-effort` writes the idea into `.handoff/<date>-<effort>.md` in the worktree. The starting prompt names `grilling`, `prototype`, `to-spec`, `to-tickets` and `handover` in words rather than as slash commands, so it works the same in every harness. It never names a user-only skill such as `grill-with-docs`.
- **Consequences:** None.

## 2026-09-28: treehouse.md moves beside init-effort, and herdr.md goes

- **Status:** replaced by [2026-09-29: a tool's commands live in its how-to skill](#2026-09-29-a-tools-commands-live-in-its-how-to-skill)
- **Context:** `init-effort` is where a worktree is created. `handover-to-herdr` already carries every Herdr command the start needs.
- **Options:** Keep a second Herdr reference: it would duplicate `handover-to-herdr`.
- **Choice and why:** Move `treehouse.md` beside `init-effort`, and remove `herdr.md`.
- **Consequences:** The closing steps after a merge stay in `init-effort` until a closing skill takes them over.

## 2026-09-29: the pull request's last section is the one report-back channel

- **Status:** accepted
- **Context:** A delegated orchestrator had learned things during a build, such as a skipped end-to-end rerun, changes with wider reach than the ticket, and review findings left unfixed. They reached neither the pull request nor a ticket, and surfaced only when the maintainer asked for a debrief.
- **Options:** A separate debrief file: one pull request is the whole delivery.
- **Choice and why:** `to-pr`'s template ends with *Things to be aware of*: four short lines for decisions made alone, surprises, what's not in the PR, and follow-ups. Each follow-up is marked as a ticket, a todo for the maintainer, or nothing needed. An empty line says "None.", so the reader knows it was considered. Any agent that opens a pull request fills it. `orchestrate-effort` fills it from the orchestrator's running list of decisions and what delegates reported.
- **Consequences:** A session closing the effort reads the section first. It stays apart from *Special things to note*, which is about the change itself.

## 2026-09-29: orchestrate-with-handoff runs on the spec and tickets the handoff names

- **Status:** accepted
- **Context:** A GitHub-tracked effort has no effort folder.
- **Options:** Read an effort folder.
- **Choice and why:** Run on the spec and tickets that the handoff names.
- **Consequences:** None.

## 2026-09-29: the worktree is clean after delivery, and the orchestrator reports it

- **Status:** accepted
- **Context:** An orchestrator had left `to-pr`'s saved description untracked in the worktree, because nothing said whether to commit it.
- **Options:** None considered.
- **Choice and why:** `orchestrate-effort` owns the rule, since its step ends a build. It checks `git status`, and reports a clean tree or names each file left out with its reason. Delivery writes nothing that needs committing: `to-pr` saves the description's source in the ignored `.scratch/`, and a rerun rewrites it there.
- **Consequences:** None.

## 2026-09-29: after delivery the maintainer only reviews

- **Status:** accepted
- **Context:** A delivery report had ended with a "next steps for you" list, of which only the first line was the maintainer's.
- **Options:** None considered.
- **Choice and why:** The maintainer reviews and says "go"; the rest is the agent's. The final report lists what the agent will do once told, as its own steps: merge, run the post-merge follow-ups, try what can only be tried after the merge, and close the effort with `close-effort`.
- **Consequences:** The literal "go" was later dropped; see [2026-09-30: no go keyword](#2026-09-30-no-go-keyword).

## 2026-09-29: QA by the maintainer is opt-in per project and non-blocking by default

- **Status:** accepted
- **Context:** "Closes" in a pull request had auto-closed tickets at merge, before anyone tried them.
- **Options:** Close the built ticket and open a separate QA ticket: keeping the one ticket open and assigned puts it in the maintainer's issues list with its history.
- **Choice and why:**
  - A project opts in through its own instructions, which also say how a build reaches the maintainer: an install, a dev server or a preview link. A CLI or a skill usually needs none.
  - A ticket the maintainer can use stays open after it is built, assigned to them, with a "Ready for you to try" comment: how to reach the build, how to use it, numbered try-this steps, and what to do when done.
  - The pull request says "Refs", not "Closes".
  - The merge waits only when the spec says "QA: blocking". The thinking session decides that for UX-heavy work the maintainer will iterate on.
  - It lives in `orchestrate-effort`'s build step, with the "Refs" rule in `to-pr` and a line in `lifecycle.md`'s Build phase. It is one step of the build, so it is not a new skill.
- **Consequences:** `to-spec`, a fork, stays unchanged, since the spec only needs to say "QA: blocking" in its own words.

## 2026-09-29: close-effort is its own skill

- **Status:** accepted
- **Context:** This completes [2026-09-28: treehouse.md moves beside init-effort, and herdr.md goes](#2026-09-28-treehousemd-moves-beside-init-effort-and-herdrmd-goes), which kept the closing steps in `init-effort` until a closing skill took them over. Every close so far needed the maintainer to ask for each part by hand: checking the merge, auditing what was left, carrying it over, closing tickets, removing worktrees and branches, closing the Herdr workspace.
- **Options:** None considered.
- **Choice and why:** `close-effort` runs when the maintainer tells the orchestrator the pull request is good ("go"), or when any session is told the pull request merged or to merge it. A skill the agent must reach from those words needs a description, so it is model-invoked with `allow_implicit_invocation: true` for Codex.
- **Consequences:** The closing steps that `init-effort` carried from the retired `init-effort-with-herdr` move into it. `init-effort` and `lifecycle.md`'s Close phase point at it.

## 2026-09-29: the agent merges and runs every cleanup command itself

- **Status:** accepted
- **Context:** A close once ended by handing the maintainer the commands to paste.
- **Options:** None considered.
- **Choice and why:** The maintainer's only step after delivery is the review. The agent merges and runs every cleanup command.
- **Consequences:** None.

## 2026-09-29: the close reads Things to be aware of first

- **Status:** accepted
- **Context:** The section replaced the separate debrief. A close that read a debrief first caught a skipped end-to-end rerun nobody else knew about.
- **Options:** None considered.
- **Choice and why:** The close reads the section before anything else, and routes each item to a check run now, a next-effort ticket, a todo for the maintainer, or nothing needed. Without the section (an older effort), it asks the delivering orchestrator once through Herdr when that session is still alive, else reads the handoff and tickets.
- **Consequences:** The fallback changed in [2026-09-30: without the report-back section, the close reads the handoff and tickets](#2026-09-30-without-the-report-back-section-the-close-reads-the-handoff-and-tickets).

## 2026-09-29: unfinished work always ends as linked next-effort tickets

- **Status:** accepted
- **Context:** Work left at a close can be lost.
- **Options:** None considered.
- **Choice and why:** Unfinished work ends as linked tickets, labelled for the next effort, never dropped.
- **Consequences:** QA tickets left open for the maintainer (non-blocking QA, "Refs" in the pull request) aren't unfinished work. They stay open and assigned, with a comment that the work is merged.

## 2026-09-29: destructive steps need proof of merged work

- **Status:** accepted
- **Context:** Sub-agent work is often cherry-picked with fixes or squashed, so reachability alone misses it.
- **Options:** None considered.
- **Choice and why:** A branch or worktree goes only when its work is proven merged: reachable from the default branch, or matched by patch with `git cherry`. Anything unproven is kept and reported.
- **Consequences:** The claim that `git cherry` catches squashed or fixed-up work is wrong; see [2026-09-29: three proofs of merged work](#2026-09-29-three-proofs-of-merged-work).

## 2026-09-29: a refused deletion goes into a script for the maintainer

- **Status:** replaced by [2026-09-30: no cleanup script](#2026-09-30-no-cleanup-script)
- **Context:** An earlier close had `git worktree remove --force` and `git branch -D` refused as irreversible local destruction.
- **Options:** Try a variant of the command.
- **Choice and why:** A denial is final. The command goes into a script in the main checkout's `.scratch/`, each line under its proof, for the maintainer to run. The agent tries no variant.
- **Consequences:** None.

## 2026-09-29: ignored and untracked files are copied out first

- **Status:** accepted
- **Context:** `treehouse return` and `git worktree remove` delete these files without warning. An untracked `.vscode/` would have been lost.
- **Options:** None considered.
- **Choice and why:** The skill lists them per worktree, and copies what is worth keeping per the folder standard.
- **Consequences:** None.

## 2026-09-29: the close frees its own worktree last, from a tab outside it

- **Status:** replaced by [2026-10-01: settlement saves work and leaves the caller available](#2026-10-01-settlement-saves-work-and-leaves-the-caller-available)
- **Context:** Returning a worktree stops every process in it, the closing session included.
- **Options:** None considered.
- **Choice and why:** After its report, the skill opens a tab in the repository's main-checkout workspace. It runs the return, after a short pause, and the workspace close there. The tab's output is its report. Without Herdr, that one step is the maintainer's. Worktrees return to the Treehouse pool rather than being destroyed, so the pool keeps its warm slots.
- **Consequences:** The workspace close was reversed by [2026-09-30: workspaces and sessions stay open](#2026-09-30-workspaces-and-sessions-stay-open).

## 2026-09-29: three proofs of merged work

- **Status:** accepted
- **Context:** This corrects [2026-09-29: destructive steps need proof of merged work](#2026-09-29-destructive-steps-need-proof-of-merged-work). `git cherry` matches commits by patch. A throwaway repo showed that it prints `+` both for an effort branch that was squash-merged and for a delegate commit integrated with `cherry-pick --no-commit` plus ticked criteria.
- **Options:** None considered.
- **Choice and why:** `close-effort` adds a third proof: the pull request is `MERGED`, and the branch's tip is its `headRefOid` or an ancestor of it. A leftover delegate branch counts when its ticket's commit is in that head and it holds nothing else.
- **Consequences:** `orchestrate-effort` now removes each delegate's worktree and branch right after its ticket commit is integrated and pushed. The integrated commit is the proof, so few delegate branches reach the close.

## 2026-09-29: the close leaves the maintainer's main checkout where it is

- **Status:** accepted
- **Context:** Switching branches under the maintainer could strand their work in progress.
- **Options:** None considered.
- **Choice and why:** The close runs git there with `git -C`. It pulls only when the checkout is clean and already on the default branch. Otherwise it fetches and works from `origin/<default>`.
- **Consequences:** None.

## 2026-09-29: the close commits nothing straight to the default branch

- **Status:** accepted
- **Context:** The close may change tracked files, such as a local tracker's done marks or files kept from worktrees.
- **Options:** None considered.
- **Choice and why:** These changes follow the project's instructions. By default they go on a small follow-up branch with a pull request through `to-pr`, or are listed in the report when too small for one. It matches how every other change reaches the default branch.
- **Consequences:** None.

## 2026-09-29: the install names the upstream skills one by one

- **Status:** accepted
- **Context:** Installing all of `mattpocock/skills` beside the family would put the upstream `handoff`, `to-spec` and `to-tickets` over the forks.
- **Options:** Install the whole upstream repo.
- **Choice and why:** The README and `lifecycle.md` list only the upstream skills the family cites (`grilling`, `prototype`, `tdd`, `code-review`, `setup-matt-pocock-skills`), and say the forks replace the other three.
- **Consequences:** None.

## 2026-09-29: the handover settles QA before it hands over

- **Status:** replaced by [2026-09-30: handover drops its QA check](#2026-09-30-handover-drops-its-qa-check)
- **Context:** Nothing prompted the QA choice, so every effort fell to the non-blocking default unasked.
- **Options:** None considered.
- **Choice and why:** In a project that opts in to QA, `handover`'s readiness check asks that the spec say whether QA is blocking. When it doesn't, it asks the maintainer while they are present.
- **Consequences:** None.

## 2026-09-29: agents never run rm -rf

- **Status:** accepted
- **Context:** An orchestrator once sent commit, push and an `rm -rf` of a delegate's temporary folder as one command. The permission check refused it because of the `rm -rf`. The orchestrator read that as a refused commit, and asked the maintainer for permission to commit three times while it held back tickets.
- **Options:** None considered.
- **Choice and why:** Agents move what is no longer needed into `.scratch/`. Moving into the gitignored folder keeps the tree clean, can be undone, and never meets a deny rule.
- **Consequences:** The rule lives in `folders.md`, with a pointer in `orchestrating`'s discipline and one line in the `implement` fork, so orchestrators and delegates both see it.

## 2026-09-29: the effort skills name roles, not tools

- **Status:** accepted
- **Context:** This replaces [2026-09-24: Treehouse owns worktrees, Herdr owns the view, git owns the branch](#2026-09-24-treehouse-owns-worktrees-herdr-owns-the-view-git-owns-the-branch) as a default, and [2026-09-24: the agent to start is read from the user's instructions](#2026-09-24-the-agent-to-start-is-read-from-the-users-instructions). `init-effort`, `handover`, `close-effort` and `lifecycle.md` said "Treehouse by default" and "a Herdr tab by default", so a teammate on tmux, or a change of tool, meant editing each skill.
- **Options:** None considered.
- **Choice and why:** The skills name `<session-host>`, `<worktree-tool>` and `<agent>` as parameters, resolved from the Defaults table in the environment's instructions, a project's table overriding the global one. This follows the parameter convention in **maintain-environment**'s `where-things-go.md`. Each says what happens when unset: `git worktree add`, the same session or a pasted prompt, and the host steps of a close skipped or left to the maintainer.
- **Consequences:** Treehouse and Herdr stay true of the maintainer's own setup.

## 2026-09-29: a tool's commands live in its how-to skill

- **Status:** accepted
- **Context:** This replaces [2026-09-28: treehouse.md moves beside init-effort, and herdr.md goes](#2026-09-28-treehousemd-moves-beside-init-effort-and-herdrmd-goes).
- **Options:** None considered.
- **Choice and why:** `treehouse.md` leaves `init-effort` and becomes the `treehouse` skill. `close-effort`'s Herdr commands move into `handover-to-herdr`'s `closing-an-effort.md`, which makes `handover-to-herdr` the how-to skill for Herdr as a session host.
- **Consequences:** None.

## 2026-09-29: a session host's how-to skill is named after the host

- **Status:** replaced by [2026-09-30: the effort skills name the tools' skills directly](#2026-09-30-the-effort-skills-name-the-tools-skills-directly)
- **Context:** The skills must find a host's how-to skill from the Defaults row alone.
- **Options:** None considered.
- **Choice and why:** A session host's how-to skill is named `handover-to-<session-host>`.
- **Consequences:** Switching to tmux is one row and one `handover-to-tmux` skill.

## 2026-09-29: with no session host, a handover offers the same session

- **Status:** accepted
- **Context:** A handover used to probe `herdr status` itself.
- **Options:** None considered.
- **Choice and why:** A handover follows the Defaults row. With no session host, it runs the starting prompt here, once this session works in the worktree, or prints it to paste, whichever the maintainer picks. The host's how-to skill checks that it can reach the host, and hands back when it can't.
- **Consequences:** None.

## 2026-09-30: tabs are labelled harness, role, topic

- **Status:** accepted
- **Context:** This replaces [2026-09-24: tabs are labelled effort, role, harness](#2026-09-24-tabs-are-labelled-effort-role-harness). The maintainer asked for it while reviewing #66 ([#44](https://github.com/yahyabedirhan/skills/issues/44#issuecomment-5906231131)).
- **Options:** None considered.
- **Choice and why:** Tabs are labelled `<harness> · <role> · <topic>`, such as `CC · Orchestrator · environment`. close-effort's shell is `shell · Close · <effort>`.
- **Consequences:** The harness short names and the pane's agent name (`<topic>-<role>`) are unchanged.

## 2026-09-30: a settled tab gets settled at the start of its label

- **Status:** accepted
- **Context:** This replaces [2026-09-24: a tab that has handed over is marked settled at the end](#2026-09-24-a-tab-that-has-handed-over-is-marked-settled-at-the-end), at the maintainer's request.
- **Options:** None considered.
- **Choice and why:** Put `[settled] ` at the start of the label, such as `[settled] CC · Thinking · environment`.
- **Consequences:** None.

## 2026-09-30: the effort skills name the tools' skills directly

- **Status:** replaced by [2026-09-30: the effort skills no longer name handover-to-herdr](#2026-09-30-the-effort-skills-no-longer-name-handover-to-herdr)
- **Context:** This replaces [2026-09-29: a session host's how-to skill is named after the host](#2026-09-29-a-session-hosts-how-to-skill-is-named-after-the-host) (#83). There is one host and one worktree tool with a skill. A reader shouldn't resolve a variable to find a skill that can be named.
- **Options:** None considered.
- **Choice and why:** The effort skills name `handover-to-herdr` and `treehouse` in a line that routes to each ("when `<session-host>` is Herdr, use the **handover-to-herdr** skill; otherwise …").
- **Consequences:** A new tool gets its own line once its skill exists. With no session host or worktree tool set, the skills still work in the same session with `git worktree add`.

## 2026-09-30: lifecycle.md uses plain words

- **Status:** accepted
- **Context:** `orchestrating/lifecycle.md` used placeholders it never declared (#83).
- **Options:** None considered.
- **Choice and why:** Use plain words, such as "the session host".
- **Consequences:** None.

## 2026-09-30: close-effort's commands move to commands.md

- **Status:** replaced by [2026-09-30: close-effort's SKILL.md holds the flow, and one reference holds how](#2026-09-30-close-efforts-skillmd-holds-the-flow-and-one-reference-holds-how)
- **Context:** About 25 inline commands interrupted the explanation, and none said why it was used. The maintainer asked for it while reviewing #66 ([#83](https://github.com/yahyabedirhan/skills/issues/83)).
- **Options:** None considered.
- **Choice and why:** The body keeps the outcomes, the maintainer's preferences, the workflow and the lessons. The git and gh commands move to `commands.md`, each with what it is for, its alternatives and when to use it, as `closing-an-effort.md` already did for Herdr.
- **Consequences:** The three proofs of merged work stay in the body as ideas.

## 2026-09-30: close-effort has only three ordering rules

- **Status:** accepted
- **Context:** Real closes needed only some of the orderings (#83).
- **Options:** None considered.
- **Choice and why:** Keep three: read *Things to be aware of* before any cleanup; copy out a worktree's files before removing it; free this session's own worktree last, from outside it. The rest runs in the order that fits.
- **Consequences:** None.

## 2026-09-30: no go keyword

- **Status:** accepted
- **Context:** This replaces the "go" of the 2026-09-29 entries (#83).
- **Options:** None considered.
- **Choice and why:** The maintainer approves the pull request. The skills don't wait for a literal word.
- **Consequences:** None.

## 2026-09-30: workspaces and sessions stay open

- **Status:** accepted
- **Context:** This reverses the workspace close in [2026-09-29: the close frees its own worktree last, from a tab outside it](#2026-09-29-the-close-frees-its-own-worktree-last-from-a-tab-outside-it) (#83).
- **Options:** None considered.
- **Choice and why:** The close no longer closes the effort's workspaces. Instead, nothing is left only inside the session: it is committed and pushed, in a ticket, or in a handoff, so another session can continue.
- **Consequences:** The close still frees every proven-merged worktree to save disk, its own last.

## 2026-09-30: no cleanup script

- **Status:** accepted
- **Context:** This replaces [2026-09-29: a refused deletion goes into a script for the maintainer](#2026-09-29-a-refused-deletion-goes-into-a-script-for-the-maintainer) (#83).
- **Options:** None considered.
- **Choice and why:** Permission rules belong to the environment, not the skill. What can't be proven or removed is kept and reported.
- **Consequences:** None.

## 2026-09-30: without the report-back section, the close reads the handoff and tickets

- **Status:** accepted
- **Context:** This replaces the fallback in [2026-09-29: the close reads Things to be aware of first](#2026-09-29-the-close-reads-things-to-be-aware-of-first) (#83).
- **Options:** Ask the delivering orchestrator through the session host.
- **Choice and why:** Without *Things to be aware of*, the close reads the handoff and tickets.
- **Consequences:** None.

## 2026-09-30: the close frees its own follow-up worktree once the branch is pushed

- **Status:** replaced by [2026-10-01: release precedes branch deletion](#2026-10-01-release-precedes-branch-deletion)
- **Context:** #21 asked for this after a close handed the maintainer this cleanup to paste.
- **Options:** None considered.
- **Choice and why:** The follow-up branch's pushed pull request is its proof. Its worktree goes to save disk, and its local branch goes when the remote holds it.
- **Consequences:** It was the one exception to "proven merged, or kept".

## 2026-09-30: each skill file reads on its own

- **Status:** accepted
- **Context:** Bare "(step 8)" labels in `closing-an-effort.md` meant nothing to a reader arriving from another skill. The maintainer asked for it while reviewing #66.
- **Options:** None considered.
- **Choice and why:** A file names another skill's step only when it has to, and then says which skill and what the step does. A sibling reference file carries no step numbers from `SKILL.md`.
- **Consequences:** None.

## 2026-09-30: init-effort keeps no commands file

- **Status:** accepted
- **Context:** After pruning what the model already knows, only two lessons were left: the first commit's message, and a new branch with no upstream until its first push.
- **Options:** None considered.
- **Choice and why:** Both sit in the body as sentences. `handover` states the upstream lesson itself instead of pointing at `init-effort`.
- **Consequences:** None.

## 2026-09-30: a parameter's meaning lives only in Parameters

- **Status:** replaced by [2026-09-30: a role is defined once, in the roles table](#2026-09-30-a-role-is-defined-once-in-the-roles-table)
- **Context:** handover, init-effort and close-effort repeated the Treehouse and Herdr routing and the unset fallback in their steps. That left the Parameters section with no purpose. The maintainer asked for it while reviewing #66.
- **Options:** None considered.
- **Choice and why:** Each Parameters entry says what the parameter is, which skill a known value uses, and what happens when it is unset. The steps use the placeholder as a noun ("start the session through `<session-host>`").
- **Consequences:** The convention in `where-things-go.md` says so too.

## 2026-09-30: a Parameters section holds only its entries

- **Status:** accepted
- **Context:** The Defaults table, loaded with the instructions, already says that a project's row overrides the global one and that `none` means the skill's fallback. The maintainer asked for it while reviewing #66.
- **Options:** None considered.
- **Choice and why:** Remove the line that says where parameters come from and when one is unset, from every skill.
- **Consequences:** None.

## 2026-09-30: a parameter's fallback is its Default line

- **Status:** replaced by [2026-09-30: a role is defined once, in the roles table](#2026-09-30-a-role-is-defined-once-in-the-roles-table)
- **Context:** This supersedes the "what happens when it's unset" wording above.
- **Options:** None considered.
- **Choice and why:** Each Parameters entry ends with what the skill does when the value isn't set, written "Default: …", never "Unset, …".
- **Consequences:** `where-things-go.md` says the same.

## 2026-09-30: plain words over defined variables

- **Status:** accepted
- **Context:** Every variable is one more thing to resolve.
- **Options:** None considered.
- **Choice and why:** A skill writes "the default branch" and "the pull request's number", not `<default>` and `<n>` defined once and used below.
- **Consequences:** Placeholders stay for parameters, and for format templates such as a tab label.

## 2026-09-30: the effort skills went through a per-skill audit

- **Status:** accepted
- **Context:** The skills repeated other skills and the model's own knowledge.
- **Options:** None considered.
- **Choice and why:** A fresh sub-agent per skill audited it with writing-for-agents and the prompt-audit guide, and edited its own skill. Repeats were cut, and the lessons from real sessions kept.
- **Consequences:** The maintainer reviews the result in #66.

## 2026-09-30: skills name other skills by their slash command

- **Status:** accepted
- **Context:** Bold marked a skill and a key term the same way, so a reader couldn't tell `handover` the skill from a handover. The maintainer asked for it while reviewing #66.
- **Options:** None considered.
- **Choice and why:** Write `/to-tickets` rather than **to-tickets**, across the maintainer's own skills. The forks keep their wording.
- **Consequences:** A starting prompt still names skills in words, as the 2026-09-28 entry requires, so it works in every harness.

## 2026-09-30: skills don't mention the Defaults table

- **Status:** accepted
- **Context:** When the table is in context the agent already sees it. When it isn't, the mention points at nothing. The maintainer asked for it while reviewing #66.
- **Options:** None considered.
- **Choice and why:** Remove every mention. `/maintain-environment` no longer offers to add an answered parameter to the table. `default_tools.py` flags the mention anywhere in a skill, Parameters sections included.
- **Consequences:** The skills that own the instruction files stay exempt.

## 2026-09-30: skills don't point at the user's instructions

- **Status:** replaced by [2026-09-30: the rule against pointing at the user's instructions is dropped](#2026-09-30-the-rule-against-pointing-at-the-users-instructions-is-dropped)
- **Context:** The reasoning of the Defaults-table rule seemed to cover "named in their instructions" and "that rule lives in their agent instructions".
- **Options:** None considered.
- **Choice and why:** `/init-effort` asks for the projects folder when it doesn't know it. `/skill-recap` drops its pointer to the public-repository rule. `/email` says what to do with a message is the user's call.
- **Consequences:** Only the skills that own the instruction files mention them.

## 2026-09-30: reference documents are named for their topic

- **Status:** accepted
- **Context:** Names like "where things go" and "carrying a change" read like headings in a narrative. Technical writing names a reference document by its topic, as `efficiency-analysis.md` and `skill-operations.md` already were (#83). The maintainer asked for it while reviewing #66.
- **Options:** None considered.
- **Choice and why:** Rename as noun phrases:
  - `maintain-environment`'s `where-things-go.md` became `environment-layers.md`, and `carrying-a-change.md` became `change-propagation.md`.
  - `handover-to-herdr`'s `closing-an-effort.md` became `close-effort-commands.md`.
  - `orchestrating`'s `notify.md` became `notifications.md`, and `folders.md` became `folder-standard.md`.
- **Consequences:** Each document's title, opening and section headings match its new name, and its rules are unchanged. Older entries keep the old names, since they record what was true then.

## 2026-09-30: close-effort's SKILL.md holds the flow, and one reference holds how

- **Status:** replaced by [2026-09-30: a must-read lives in SKILL.md](#2026-09-30-a-must-read-lives-in-skillmd)
- **Context:** This replaces [2026-09-30: close-effort's commands move to commands.md](#2026-09-30-close-efforts-commands-move-to-commandsmd). The maintainer found the skill enforced too much in its main body, and asked for the core flow at the centre (#83).
- **Options:** Five topic references: they felt like too many.
- **Choice and why:** Eight numbered steps, from finding the effort to the report, carry what each step must achieve. `command-reference.md` holds the git and gh commands, their pitfalls and the three proofs of merged work. What to do stays in the skill; how to do it goes to a reference.
- **Consequences:** None.

## 2026-09-30: no skill names another skill's section

- **Status:** accepted
- **Context:** A section name used across skills was a hidden dependency. Renaming it in `to-pr` would have left the others stale (#83).
- **Options:** None considered.
- **Choice and why:** `close-effort` reads the pull request's description and the handoff instead of the *Things to be aware of* section. `orchestrate-effort` puts its report in the description. `to-pr` no longer says who reads its last section.
- **Consequences:** None.

## 2026-09-30: every skill's SKILL.md says what to do, a reference says how

- **Status:** replaced by [2026-09-30: a must-read lives in SKILL.md](#2026-09-30-a-must-read-lives-in-skillmd)
- **Context:** The close-effort test applied to every skill (#83).
- **Options:** None considered.
- **Choice and why:** Each of the maintainer's own skills opens with its preferences and a short numbered flow. Commands, pitfalls, detailed procedures and edge cases move into a few references named by topic. A rule about what to do stays in the flow even when it is a restriction; only the how moves out.
- **Consequences:** A fresh sub-agent restructured each skill, and the result was checked for dead links and the standards above.

## 2026-09-30: small references folded back

- **Status:** accepted
- **Context:** Some references were too small to stand alone (#83).
- **Options:** None considered.
- **Choice and why:** `/orchestrating`'s `notifications.md` became a section of its `SKILL.md`. `/maintain-environment`'s `change-propagation.md` became its flow's last steps. `/orchestrate-effort`'s three references became one, `ticket-handling.md`.
- **Consequences:** None.

## 2026-09-30: a role is defined once, in the roles table

- **Status:** accepted
- **Context:** This replaces [a parameter's meaning lives only in Parameters](#2026-09-30-a-parameters-meaning-lives-only-in-parameters) and [a parameter's fallback is its Default line](#2026-09-30-a-parameters-fallback-is-its-default-line). The same routing and fallback had been written into four skills. The maintainer asked for it while reviewing #66.
- **Options:** None considered.
- **Choice and why:** What each role is, and what to do when it has no tool, live only in `/set-up-machine`'s roles table. `/set-up-machine` copies both into the global Defaults as columns beside the user's tool, so every session has them in context. A skill's Parameters section shrinks to one line per role, such as "`<session-host>`: where agent sessions run, e.g. Herdr, Claude Code Desktop, Codex Desktop." A tool's own skill says when to use it and what is specific to it, such as `/treehouse` returning worktrees to the pool.
- **Consequences:** The team test now assumes a machine set up with `/set-up-machine`, since that is how the roles reach a teammate.

## 2026-09-30: supporting files are listed in closing sections and read from the body

- **Status:** accepted
- **Context:** Some skills pointed at their files from their intro, some from a step and some from their own section. The sections mixed descriptions with read-when rules. The maintainer asked for it while reviewing #66.
- **Options:** None considered.
- **Choice and why:** A skill with references ends with `## References`, and one with scripts with `## Scripts`: one line per file saying what it covers, never when to read it. The instruction to read a file sits in the step that needs it ("Read `command-reference.md` before running the steps' git and gh commands").
- **Consequences:** None.

## 2026-09-30: a step's special cases sit under it as bullets

- **Status:** accepted
- **Context:** Special cases inside a step hide the usual path. The maintainer asked for it while reviewing #66.
- **Options:** None considered.
- **Choice and why:** A numbered step says only what always happens. Each case that applies to some runs, such as "When the spec says "QA: blocking"", is an indented bullet that opens with its condition in bold.
- **Consequences:** A reader of the flow sees the usual path at a glance, and reads a case only when it applies.

## 2026-09-30: default_tools.py is gone

- **Status:** accepted
- **Context:** The script and its tests were 270 lines to keep up. After the roles change, it mostly reported parameter examples. The maintainer doesn't want scripts whose upkeep outweighs what they catch.
- **Options:** Keep the script.
- **Choice and why:** The team-test audit is now a grep described in `/maintain-environment`'s `environment-layers.md`.
- **Consequences:** None.

## 2026-09-30: the rule against pointing at the user's instructions is dropped

- **Status:** accepted
- **Context:** This replaces [2026-09-30: skills don't point at the user's instructions](#2026-09-30-skills-dont-point-at-the-users-instructions). That rule came from the Defaults-table rule by analogy, not from the maintainer, who doesn't hold it.
- **Options:** None considered.
- **Choice and why:** Drop the rule.
- **Consequences:** The Defaults-table rule stays.

## 2026-09-30: herdr and treehouse are written as commands

- **Status:** accepted
- **Context:** A reader should see a CLI.
- **Options:** None considered.
- **Choice and why:** Write `herdr` and `treehouse` as code in running text.
- **Consequences:** Skill titles and display names keep the product's name.

## 2026-09-30: the no-track lesson lives with the tool

- **Status:** accepted
- **Context:** Several skills repeated the `--no-track` lesson from [2026-09-24: new branches don't track the default branch](#2026-09-24-new-branches-dont-track-the-default-branch).
- **Options:** None considered.
- **Choice and why:** The lesson lives in the roles table's fallback for plain git worktrees, and in `/treehouse` for its own path.
- **Consequences:** The skills that make a worktree say only which branch to start from: the remote default branch, or the local one when the work builds on its unpushed commits.

## 2026-09-30: a must-read lives in SKILL.md

- **Status:** accepted
- **Context:** This refines [2026-09-30: every skill's SKILL.md says what to do, a reference says how](#2026-09-30-every-skills-skillmd-says-what-to-do-a-reference-says-how). A reference is only for what some runs need. The maintainer asked for it while reviewing #66.
- **Options:** None considered.
- **Choice and why:** Every file that each run had to read came back into its skill: handover's readiness checklist, close-effort's command reference, most of orchestrate-effort's ticket handling (its QA part stays as `user-qa.md`), handover-to-herdr's session-start commands, and orchestrating's lifecycle. How-to detail stays in `SKILL.md` when every run needs it.
- **Consequences:** The same pass folded `/maintain-environment`'s `environment-layers.md`, `/set-up-machine`'s machine diff and most of its rule table and hook, and the command references of `/email`, `/skill-recap` and `/wispr-flow-dictionary`.

## 2026-09-30: the effort skills no longer name handover-to-herdr

- **Status:** accepted
- **Context:** This replaces [2026-09-30: the effort skills name the tools' skills directly](#2026-09-30-the-effort-skills-name-the-tools-skills-directly), now that the roles table carries each role's meaning and fallback.
- **Options:** None considered.
- **Choice and why:** The skills start a session "through `<session-host>`". `/handover-to-herdr`'s description says it is used when that host is `herdr`.
- **Consequences:** None.

## 2026-09-30: apply the last prompt audit's behaviour fixes

- **Status:** accepted
- **Context:** The last prompt audit found fixes that change behaviour.
- **Options:** None considered.
- **Choice and why:** Apply them:
  - `/handover-to-herdr` escapes apostrophes in the single-quoted starting prompt.
  - `/orchestrate-effort` records a local QA ticket as waiting for the user's QA, not done.
  - `/orchestrating`'s lifecycle puts `/tdd` and `/code-review` in the build, not the thinking.
  - `/email` never adds `TRASH` or `SPAM` with a label tool, since that would trash or spam around the deny rules.
- **Consequences:** None.

## 2026-09-30: a handover uses the context it holds

- **Status:** accepted
- **Context:** Handing over raw thinking makes the next session rebuild it. The maintainer set these rules while reviewing #66.
- **Options:** None considered.
- **Choice and why:** A thinking session writes its spec and tickets before handing over. Handing an active session's work to a fresh one needs a reason from the maintainer, such as a context grown too long. Work that isn't an effort has no spec or tickets, so its handoff and its one-line starting prompt say what to do next.
- **Consequences:** None.

## 2026-09-30: treehouse v2.3.0 behaviour, from a test

- **Status:** accepted
- **Context:** `/treehouse` said `return` deleted ignored and untracked files without asking. A test on a throwaway pool checked it.
- **Options:** None considered.
- **Choice and why:** `/treehouse` now states what the test showed:
  - `return` asks before deleting untracked files. With no terminal, it aborts and still exits 0. `--force` deletes them.
  - Ignored files survive a return, even with `--force`, and reach the next effort that leases the worktree.
  - `destroy` removes everything, and needs `--include-in-use` for a worktree with a running process.
- **Consequences:** None.

## 2026-09-30: the agent parameter is named agent

- **Status:** accepted
- **Context:** The maintainer edited the skills during the #66 review.
- **Options:** None considered.
- **Choice and why:** `<agent-to-start>` became `<agent>`.
- **Consequences:** None.

## 2026-09-30: tab roles are lowercase

- **Status:** accepted
- **Context:** The maintainer edited the skills during the #66 review.
- **Options:** None considered.
- **Choice and why:** Tab roles are lowercase: `thinking`, `orchestrator`.
- **Consequences:** None.

## 2026-09-30: handover drops its QA check

- **Status:** accepted
- **Context:** This replaces [2026-09-29: the handover settles QA before it hands over](#2026-09-29-the-handover-settles-qa-before-it-hands-over). The maintainer made this edit during the #66 review.
- **Options:** None considered.
- **Choice and why:** Handover drops its QA check, and keeps a fresh start for when the maintainer asks.
- **Consequences:** None.

## 2026-09-30: close-effort's description names when it runs

- **Status:** accepted
- **Context:** The maintainer edited the skills during the #66 review.
- **Options:** None considered.
- **Choice and why:** close-effort's description says it runs once the pull request is good to merge or merged.
- **Consequences:** None.

## 2026-09-30: handover-to-herdr names the worktree tool

- **Status:** accepted
- **Context:** The maintainer edited the skills during the #66 review.
- **Options:** None considered.
- **Choice and why:** handover-to-herdr names `<worktree-tool>`.
- **Consequences:** None.

## 2026-09-30: the first commit of a new project is init: start name

- **Status:** accepted
- **Context:** The maintainer edited the skills during the #66 review.
- **Options:** None considered.
- **Choice and why:** The first commit of a new project is `init: start <name>`.
- **Consequences:** None.

## 2026-09-30: treehouse v3.1.0 behaviour, from a retest

- **Status:** accepted
- **Context:** Treehouse was updated from v2.3.0 (#89), and retested on a throwaway pool.
- **Options:** None considered.
- **Choice and why:** `/treehouse` follows the new behaviour:
  - `get --lease -b <branch>` now creates the effort's branch, with no upstream, so `/treehouse` drops the separate `git switch --no-track -c`.
  - `return` with untracked files and no terminal still keeps the lease, but now exits 3 instead of 0.
  - `--force` still deletes untracked files and keeps ignored ones.
  - `destroy` on a named worktree it skips exits 1 and names the flag. `--include-in-use` ends the process and removes the worktree.
- **Consequences:** None.

## 2026-09-30: close the editor before a treehouse return

- **Status:** accepted
- **Context:** In a live run on v2.3.0, `return` on a worktree with a VS Code window open ended the editor's helpers, which came back. It failed with "worktree still has live processes after termination" while exiting 0.
- **Options:** None considered.
- **Choice and why:** `/treehouse` says to close the editor first.
- **Consequences:** None.

## 2026-10-01: images move to a root assets/ folder

- **Status:** accepted
- **Context:** Images aren't documentation, so the maintainer wants them out of `docs/` (#108).
- **Options:** None considered.
- **Choice and why:** `docs/assets/<topic>/` becomes `assets/images/<topic>/` and `assets/screenshots/<topic>/`. Splitting images from screenshots keeps a project's own art apart from captures of the app.
- **Consequences:** The folder standard's migration table says how to move an existing `docs/assets/`, and `set-up-project` proposes the move when it finds one. Links already posted in issues and pull requests point at a commit, so they keep working.

## 2026-10-01: settle-session is the wrap-up for any session

- **Status:** accepted
- **Context:** Many sessions aren't efforts: a review-feedback round, a one-off fix, a config change, a research question. Each improvised its wrap-up, since `close-effort` assumed a spec, tickets and a pull request. The maintainer settled this while grilling #109.
- **Options:** None considered.
- **Choice and why:** A settled session leaves the environment clean: nothing uncommitted or unpushed, and everything it knows saved in the tracker or the project's files. Another agent can then pick the work up without reading it. `settle-session` is a discipline skill, like `orchestrating`: what settling means, in four "nothing" steps (running, unsaid, undecided, unsaved), then freeing what merged, and the report.
- **Consequences:** It knows nothing about efforts, and reads its tools from `<worktree-tool>` and `<session-host>`.

## 2026-10-01: close-effort is renamed settle-effort

- **Status:** accepted
- **Context:** The effort's wrap-up and the shared cleanup must not drift (#109).
- **Options:** Keep an alias for the old name.
- **Choice and why:** Rename everywhere at once, with no alias. `settle-effort` keeps only the effort's own steps (find, merge, post-merge follow-ups, carry tickets into the next effort, close the spec and tickets), and calls `settle-session` for the shared cleanup. The shared steps moved from `close-effort` unchanged in substance: one call per commit, push and deletion; saving ignored and untracked files before a worktree goes; the follow-up branch for tracked changes after the merge; the three proofs of merged work; freeing its own worktree last, from outside.
- **Consequences:** The orchestrating lifecycle's Close phase is now Settle. Older entries keep the old names.

## 2026-10-01: narrow triggers, both settle skills model-invoked

- **Status:** accepted
- **Context:** The maintainer says "settle" explicitly (#109).
- **Options:** Collect wrap-up phrases such as "good to merge" or "merged".
- **Choice and why:** `settle-session` answers to "settle" and "end the session" about this session, and sends "settle the effort" to `settle-effort`. `settle-effort` answers to "settle the effort" or another skill. An approval reaches it through `/orchestrating`'s Settle phase. Both are model-invoked with `allow_implicit_invocation: true`, since another skill calls each.
- **Consequences:** Neither sends a notification: `/orchestrating`'s notifications cover an orchestrator's done and blocked moments only.

## 2026-10-01: the settle triggers override the no-trigger-keyword rule

- **Status:** accepted
- **Context:** `skill-writing.md` says a skill uses no trigger keyword (#109).
- **Options:** None considered.
- **Choice and why:** The maintainer chose the narrow triggers, so `settle-session`'s description keeps "settle" and "end the session" on purpose.
- **Consequences:** None.

## 2026-10-01: a remote branch proven merged is deleted with its local branch

- **Status:** accepted
- **Context:** The repository may have deleted the remote branch on merge (#109).
- **Options:** None considered.
- **Choice and why:** Delete the remote branch with its local branch, as `close-effort` did. First check that it still exists, and that its tip is the local branch's tip or passes a proof.
- **Consequences:** None.

## 2026-10-01: settle-commands.md and the release shell

- **Status:** replaced by [2026-10-01: settlement saves work and leaves the caller available](#2026-10-01-settlement-saves-work-and-leaves-the-caller-available)
- **Context:** `settle-session` needs `handover-to-herdr`'s closing commands (#109).
- **Options:** None considered.
- **Choice and why:** `close-effort-commands.md` becomes `settle-commands.md`, used by `settle-session`. It gains the `[settled]` tab marker, since settling is what the marker means. The release shell is labelled `shell · Settle · <topic>`, created with `--label` in one call. The release command now deletes the session's own branch after freeing its worktree, which `close-effort` left behind.
- **Consequences:** None.

## 2026-10-01: apply the first settle prompt audit

- **Status:** accepted
- **Context:** A fresh sub-agent ran `/claude-api`'s `prompt-audit` on both settle skills and `settle-commands.md` (#109).
- **Options:** None considered.
- **Choice and why:** Apply its findings:
  - (high) The ignored-files check covered only the checkouts the session worked in, so a delegate's worktree named by `settle-effort` lost its ignored files when freed. It now covers every worktree the settle frees.
  - (high) Step 6 would have freed the session's own worktree mid-flow, before the report, and could have reached the main checkout or the default branch. It now leaves all three out.
  - (medium) The handoff and decisions written after the commit step were left uncommitted. "Nothing unsaved" now runs after "nothing unsaid" and "nothing undecided".
  - (medium) Committing in the main checkout could push to the default branch. That case now goes on a new branch with a pull request.
  - (medium) `settle-session` spoke of delegates, tickets and done marks. The proof is generalised, and the delegate case moved to `settle-effort`.
  - (medium) The bare "settle" trigger overlapped `settle-effort`. The description now routes effort settles there.
  - (medium) `settle-effort` had no case for a pull request already merged, which `/orchestrating` still sends it. It now skips the merge and keeps the checks.
  - (low) The kept-worktree case still marks the session settled; the session's own branch is deleted after its worktree; a "Done when" line that restated the intro went; "maintainer" became "user" to match `settle-session`; a descriptive intro line became an instruction; the release tab is created with its label; the Codex short description dropped a metaphor.
- **Consequences:** Three findings were left unchanged:
  - The claim that `herdr workspace list` lacks `checkout_path`, `repo_root` and `is_linked_worktree`: a live run shows them under each workspace's `worktree`.
  - The pointer to `/orchestrating`'s `folder-standard.md`: the folder standard is the family's single source for where files go.
  - The suggestion that `settle-session` name `/handover-to-herdr`: it reaches the host's skill through `<session-host>`, per [2026-09-30: the effort skills no longer name handover-to-herdr](#2026-09-30-the-effort-skills-no-longer-name-handover-to-herdr).

## 2026-10-01: both settle skills went through writing-for-agents

- **Status:** accepted
- **Context:** The settle skills needed the same writing review as the others (6af1d9c for `settle-effort`, a44e09e for `settle-session`).
- **Options:** None considered.
- **Choice and why:** Apply the `/writing-for-agents` review: each description is built from the step names; the intros were trimmed; deleting a freed branch's remote copy became an explicit case; `settle-commands.md` gained the case where the repository has no `herdr` workspace; and `settle-effort` creates an `effort:` label only when it is missing, and puts the follow-ups' results in the report.
- **Consequences:** None.

## 2026-10-01: apply the second settle prompt audit

- **Status:** accepted
- **Context:** A fresh, report-only auditor found 13 issues.
- **Options:** None considered.
- **Choice and why:** Apply 12 of them:
  - A freed branch's remote copy is deleted only when `git ls-remote --heads origin <branch>` shows it and its tip is the local tip or passes a proof. Otherwise it is kept and reported.
  - `git branch -d` checks against the upstream or `HEAD`, not the remote default branch, so `-D` is used when `-d` refuses a branch a proof passed.
  - The pull-request-head proof accepts a commit that carries the same change, since a commit changed while integrated has a new SHA. When unsure, the branch is kept.
  - The unattended release in `settle-commands.md` deletes the branch with `-D`, since `-d` from the main checkout could fail unseen.
  - Finding active agents leaves out only this session's pane, `$HERDR_PANE_ID`, not its whole workspace, which hid other agents in the same worktree.
  - `settle-effort` stops before carrying work over when the default branch's CI fails after the merge. The user decides whether to file or fix it.
  - Under "QA: blocking", the settle stops after naming the open QA tickets, and resumes once they are closed.
  - Step 7 deletes the session's own branch's remote copy, as step 6 does, before the release.
  - The ignored-files check names its worktrees as those from step 1 other than the main checkout, instead of pointing forward at proofs not yet run.
  - Step 2 waits for or stops the agents this session started that are still working, and leaves idle sessions and their workspaces open. This settles a clash with the intro.
  - The `[settled]` rename is skipped when the label already has it, and `/handover-to-herdr`'s step 6 points at `settle-commands.md` instead of restating the rule.
  - Copied editor settings keep any file already in the main checkout.
- **Consequences:** Open, for the maintainer to decide: whether the spec should stay open while QA tickets are open.

## 2026-10-01: no merge guard in settle-effort

- **Status:** accepted
- **Context:** The second audit proposed a "merge only when the user approved" guard.
- **Options:** Add the guard: it would restate the decided routing.
- **Choice and why:** Leave it out. The global "ask before merging" rule and `/orchestrating`'s Settle phase already route approval.
- **Consequences:** None.

## 2026-10-01: settlement saves work and leaves the caller available

- **Status:** accepted
- **Context:** This reverses the earlier self-release instructions and external release shell: [2026-09-29: the close frees its own worktree last, from a tab outside it](#2026-09-29-the-close-frees-its-own-worktree-last-from-a-tab-outside-it) and [2026-10-01: settle-commands.md and the release shell](#2026-10-01-settle-commandsmd-and-the-release-shell). Returning an occupied worktree can terminate the session without a terminal close command. The specification is [Workflow: Make Herdr and Treehouse settlement reliable without closing topology](https://github.com/yahyabedirhan/skills/issues/123).
- **Options:** None considered.
- **Choice and why:** Keep the occupied worktree leased and retain its branches, even after merge. Keep all Herdr workspaces, tabs and panes open.
- **Consequences:** An explicit request may authorize closing named topology separately. Linked or grouped closure is never inferred.

## 2026-10-01: authorized setup remains autonomous

- **Status:** accepted
- **Context:** Inherited IDs, titles and another client's focus cannot establish the caller's identity (#123).
- **Options:** None considered.
- **Choice and why:** Create the layout the task needs with explicit live targets, and preserve focus. Resolve the caller through caller-aware inspection before reading its current hierarchy. Read creation and move results for later IDs. Refresh immediately before mutations, and inspect live state before retrying an uncertain result.
- **Consequences:** None.

## 2026-10-01: protect every occupant, including idle ones

- **Status:** accepted
- **Context:** Workspace checkout metadata cannot establish where processes run (#123).
- **Options:** None considered.
- **Choice and why:** Check actual pane and process locations, and report mismatches. Preserve a shared, occupied or uncertain target. Finish or interrupt task work without terminating its terminal session, and preserve unrelated agents, shells and services.
- **Consequences:** None.

## 2026-10-01: release precedes branch deletion

- **Status:** accepted
- **Context:** This replaces [2026-09-30: the close frees its own follow-up worktree once the branch is pushed](#2026-09-30-the-close-frees-its-own-follow-up-worktree-once-the-branch-is-pushed) (#123).
- **Options:** None considered.
- **Choice and why:** Return only clean, proven-merged, unoccupied worktrees, after live verification and lease identity checks. Retain both branches when release fails or its outcome is uncertain, and inspect before retrying. Never schedule delayed destructive cleanup.
- **Consequences:** Follow-up worktrees no longer qualify merely because their branch was pushed.

## 2026-10-01: keep factual uncertainty explicit, and external guidance upstream

- **Status:** accepted
- **Context:** The evidence establishes instruction defects, a context mismatch and Treehouse process termination. It does not establish workspace deletion or movement, a responsible actor or a Herdr software bug. The installed Herdr skill describes newer syntax, allows closure of agent-created topology, and assumes caller context for `--current` (#123).
- **Options:** Patch the installed copy of the Herdr skill.
- **Choice and why:** State only what the evidence shows. Keep external tool guidance at its source, and report remaining compatibility gaps. Change this repository's handover and settlement guidance, check installed help, and report the remaining external mismatch. Do not edit installed copies or install unmerged changes.
- **Consequences:** Reconcile the source role fallback, and install merged skills only after approval and merge.

### References

- Checked Herdr 0.9.0 help and [herdrdev/herdr at b99002ac99b09e00b4ca692436cb15a6b0d676f1](https://github.com/herdrdev/herdr/tree/b99002ac99b09e00b4ca692436cb15a6b0d676f1). `pane current --current` can fall back to another client's focus without caller context, so check context first. Moved panes can receive new public IDs; use the resolved terminal and live hierarchy. `foreground_cwd` and process information supply location evidence that workspace metadata does not.
- Checked Treehouse 3.1.0 help and [kunchenguid/treehouse at c099281010efda0bf82bbaf8d882528fcbed6acc](https://github.com/kunchenguid/treehouse/tree/c099281010efda0bf82bbaf8d882528fcbed6acc). Its process listing filters the caller's process tree and skips unreadable locations; the guidance now requires independent checks. Lease guards execute under the pool lock before detach, termination and reset, but cannot make the separate occupancy check atomic. Preserve targets when ownership through execution is uncertain.
- Ran the pinned Treehouse source's nine selected lease/process seam tests and four isolated CLI tests: `ReturnConditionalLeaseIdentityLifecycle`, `ReturnConditionalDirtyPromptDoesNotHoldPoolLock`, `ReturnExplicitPathFromOutsideRepoReleasesLease`, and `ReturnDirtyNonTTYKeepsLeaseAndExitsNotReturned`. They cover mismatched ID/holder, same-holder lease reuse, lease change during a dirty prompt, clean return, and noninteractive refusal. All passed using temporary repositories and pools, with no live topology changes.
- Independent review exercised moved callers, absent caller context, idle/shared occupants, detached services, false-empty process lists and failed returns. It found a changed-tip gap; proofs now bind to the inspected tip and must be checked again before release and deletion.
- Three installed-Herdr CLI checks passed against an isolated mock Unix socket: inherited caller identity is sent and the returned live identity and foreground location are preserved; an unresolved caller reports `pane_not_found`; absent caller context sends no caller ID. These check CLI transport and selection, not runtime pane movement. Server movement and focus semantics were checked in the pinned source; Rust tooling was unavailable for its runtime tests. The repository's 112 machine-setup tests and independent Treehouse path-containment fixtures also passed. No live topology was used for verification.

## 2026-10-02: real-app checks run in a headless browser

- **Status:** accepted
- **Context:** This narrows [2026-09-28: verification prefers the real app over off-screen renders](#2026-09-28-verification-prefers-the-real-app-over-off-screen-renders), which named no tool (#147). In one effort run, both orchestrators filled the gap with the Claude in Chrome extension the harness advertises. Six ticket delegates, the final review and a walk-through made about 130 calls in the user's own Chrome, and took over the browser the user was working in.
- **Options:** The Claude in Chrome extension: it takes over the user's browser.
- **Choice and why:** The agent drives a headless browser itself, such as the project's Playwright or `npx playwright` against the real dev server, with screenshots saved to files. A headless run with real clicks still counts as the real app, so the lesson about off-screen renders holds.
- **Consequences:** The extension is used only when the user asks for it in the current task.

## 2026-10-02: verification keeps off the user's screen and clipboard

- **Status:** accepted
- **Context:** A walk-through brief asked for "Reveal in Finder" to be clicked and the Finder window closed. Closing it through System Events raised an Accessibility prompt the user won't grant (#147).
- **Options:** None considered.
- **Choice and why:** No Finder windows or `open` on files, no System Events scripting, no `pbcopy` or `pbpaste`.
- **Consequences:** None.

## 2026-10-02: the verification rule lives in orchestrate-effort and travels in the briefs

- **Status:** accepted
- **Context:** The orchestrator writes each delegate's instructions, and the gap reached delegates through them (#147).
- **Options:** Change `implement` or `orchestrating`: neither says how to verify a UI, so neither pushed the extension.
- **Choice and why:** The rule lives in `orchestrate-effort` step 4, and travels in every brief that checks a UI, not only the ticket briefs.
- **Consequences:** The user's global "control my Mac only when requested" rule covers `implement` used on its own. `run` is a harness skill outside this repo.

## 2026-10-04: settling ends with a resume prompt

- **Status:** accepted
- **Context:** The maintainer settled two sessions before a break. Coming back meant asking an agent what to paste.
- **Options:** None considered.
- **Choice and why:** `/settle-session` ends its report with a one-line prompt to resume the work. It names the worktree's path, its branch, where what remains is written (the handoff, or the issue or pull request that holds it) and the first thing to do. It keeps the 2026-09-29 rule that the maintainer pastes nothing after approving: a settle hands the work back for later, and the maintainer chooses when to start it again.
- **Consequences:** `/settle-effort` gets the prompt through `/settle-session` and doesn't change. `/handover` keeps its own starting prompt, which the session it starts receives at once.

## 2026-10-04: the resume prompt stays one line

- **Status:** accepted
- **Context:** [2026-09-28: the starting prompt is always one line](#2026-09-28-the-starting-prompt-is-always-one-line) took the worktree and branch out of the starting prompt because the prompt had grown to four lines and arrived as pasted text, not because the next session didn't need them. In the session that asked for the resume prompt, the first draft was four lines.
- **Options:** A multi-line prompt: it arrives as pasted text.
- **Choice and why:** Keep it one line. On one line, the worktree and branch come back without that failure.
- **Consequences:** None.

## 2026-10-06: the settle skills read open decisions only through the session-status tool

- **Status:** accepted
- **Context:** The session-status mod owns its store file's format and can change it ([yahyabedirhan/claude-mods#15](https://github.com/yahyabedirhan/claude-mods/issues/15)).
- **Options:** Read the store file: the skill breaks after a format change.
- **Choice and why:** Call the tool's `list` action, and never read its store file.
- **Consequences:** None.

## 2026-10-06: before-settling decisions are raised before the work is saved or merged

- **Status:** accepted
- **Context:** The user's answer can still change the settle.
- **Options:** None considered.
- **Choice and why:** `/settle-session` raises the open `before_settling` and `blocked` decisions in its "Nothing undecided" step. `/settle-effort` raises them before its merge, since it runs `/settle-session` only after the merge.
- **Consequences:** None.

## 2026-10-06: after-settling decisions go in the report

- **Status:** accepted
- **Context:** Some decisions can wait until after the settle.
- **Options:** None considered.
- **Choice and why:** The report lists each decision that is still open as one numbered list, with its id, question, default and options. Then the agent calls `post_decide_list`.
- **Consequences:** None.

## 2026-10-10: settlement retargets stacked pull requests before it deletes a remote branch

- **Status:** accepted
- **Context:** A stacked pull request has another pull request's branch as its base. Pull request A merged, and its head branch was deleted. Pull request B was stacked on A, and the deletion closed B automatically. B could not be reopened against the default branch, and the same commits had to go into a new pull request.
- **Options:** None considered.
- **Choice and why:** `/settle-session` lists the open pull requests whose base is the freed branch. It retargets each one to the default branch, then deletes the remote branch.
- **Consequences:** When a retarget fails, it keeps the remote branch and names it in the report.

## 2026-10-10: settle-effort merges a stacked pull request after its base

- **Status:** accepted
- **Context:** The same failure as the entry above.
- **Options:** None considered.
- **Choice and why:** `/settle-effort` merges a stacked pull request after its base pull request. It retargets the stacked pull request to the default branch before the base branch is deleted.
- **Consequences:** None.

## 2026-10-23: settle-effort follows the project's release page after a version bump

- **Status:** accepted
- **Context:** A version bump merged inside a feature pull request, and the release stopped there: the version reached its registry with no tag and no GitHub release.
- **Options:** None considered.
- **Choice and why:** When the merge carried a version bump, `/settle-effort` follows the project's `docs/agents/releasing.md` from the step after the merge through its check. It hands the user each step the page gives them, and offers `/set-up-project` when the project has no page.
- **Consequences:** The settle report names each part's version.
