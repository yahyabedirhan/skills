# Decisions: skill-recap

The decisions behind the `skill-recap` skill, and the repo's tracker setup that serves it. This file is for maintaining it and is never installed. Entries follow the shape in [index.md](index.md).

## 2026-09-28: its own skill, separate from maintain-skills

- **Status:** accepted
- **Context:** `maintain-skills` changes skills. The recap looks back over a session to find what should change.
- **Options:** Fold the recap into `maintain-skills`: every install or update would load a session audit.
- **Choice and why:** A separate skill.
- **Consequences:** None.

## 2026-09-28: user-invoked only

- **Status:** accepted
- **Context:** An audit of a whole session costs real tokens, and should run when the user wants it.
- **Options:** None considered.
- **Choice and why:** A recap starts only when the user types `/skill-recap` (Codex: `$skill-recap`). It is never offered or run automatically. Set `disable-model-invocation: true` for Claude Code, and ship `agents/openai.yaml` with `allow_implicit_invocation: false` for Codex, which ignores the frontmatter flag.
- **Consequences:** See [2026-09-28: invocation stays a hard gate](#2026-09-28-invocation-stays-a-hard-gate).

## 2026-09-28: a purpose, not a checklist

- **Status:** accepted
- **Context:** The first manual recap, on 2026-09-27, found five improvements of different kinds.
- **Options:** A fixed checklist: it would find only what it lists.
- **Choice and why:** The skill says what a recap is for, and gives examples of what fits it: inefficiency, rabbit holes, wrong or stale skill content, surprises, missed triggers, rules stated only in chat, invented workarounds.
- **Consequences:** None.

## 2026-09-28: the scope is this session and its sub-agents, or what the user names

- **Status:** accepted
- **Context:** A recap needs a scope.
- **Options:** A standard time window: none fits every case.
- **Choice and why:** By default, the scope is the current session and its sub-agents. Otherwise it is exactly the scope the user names. The session is already in context. Sub-agents are read from their transcripts on disk, and the skill states their Claude Code layout so the recap doesn't rediscover it.
- **Consequences:** The audit is the same whatever the scope.

## 2026-09-28: findings with evidence, ending with a verdict

- **Status:** accepted
- **Context:** A recap must not manufacture findings.
- **Options:** None considered.
- **Choice and why:** "No skill changes needed" is a valid outcome. Each finding names the skill, the evidence, the cost and the opportunity, so it reads as a ticket's draft.
- **Consequences:** None.

## 2026-09-28: the recap files nothing; to-tickets does

- **Status:** accepted
- **Context:** `to-tickets` (mattpocock/skills) is user-invoked, so the recap can't call it. A filing step was planned in issue #30.
- **Options:** A filing step in the recap: closed as superseded (#30).
- **Choice and why:** The recap names `/to-tickets` as the user's next step, into the skills repo resolved the way `maintain-skills` resolves `<skills-repo>`.
- **Consequences:** None.

## 2026-09-28: findings about other people's skills are reported like any other

- **Status:** accepted
- **Context:** A finding may concern a skill the user didn't write.
- **Options:** None considered.
- **Choice and why:** Report it. Whether to fork, file upstream or drop the skill is the user's call, case by case.
- **Consequences:** None.

## 2026-09-28: the public-repository rule is pointed at, not restated

- **Status:** accepted
- **Context:** The public-repository rule lives in the user's own agent instructions.
- **Options:** Restate it in the skill: two copies to keep in step.
- **Choice and why:** Point at the rule.
- **Consequences:** On 2026-09-30 the skill dropped this pointer, as part of a rule against pointing at the user's instructions. That rule was later dropped too. Both are recorded in `effort-workflow.md`.

## 2026-09-28: the repo names GitHub issues as its tracker in AGENTS.md

- **Status:** accepted
- **Context:** `to-tickets` expects the tracker to be in the agent's context, by convention under an `## Agent skills` heading that `setup-matt-pocock-skills` writes.
- **Options:** A separate `docs/agents/issue-tracker.md`: one line says it.
- **Choice and why:** Inline the block in `AGENTS.md`, with `CLAUDE.md` importing it. It names `enhancement` or `bug` as the labels, because this repo has no triage labels and `to-tickets` otherwise applies `ready-for-agent`.
- **Consequences:** None.

## 2026-09-28: two prompt audits before publishing

- **Status:** accepted
- **Context:** `maintain-skills` asks for a fresh sub-agent audit. The building agent also ran the `claude-api` prompt audit on the skill folder as a separate pass first.
- **Options:** None considered.
- **Choice and why:** Apply both audits' accepted fixes.
  - The builder's pass, applied:
    - The transcript layout is marked as the one Claude Code uses today, with a fallback search by session id, since it is undocumented and may move.
    - "Each session has been read" became "searched", to agree with the advice to search long transcripts rather than read them whole.
    - "Long runs of tool calls on one problem" joined the search targets, so rabbit holes are found as well as errors.
    - The verdict is a fixed phrase ("No skill changes needed." or "<n> opportunities"), followed by the `/to-tickets` step.
    - The purpose paragraph no longer repeats the closing line that filing is the user's.
  - The builder's pass, left: the numbered steps, since their order is real (select, audit, report); and the line calling "No skill changes needed." a good outcome, since it guards against manufactured findings.
  - The fresh sub-agent, applied: (medium) the invocation config couldn't honour "or asking for one", resolved by [2026-09-28: invocation stays a hard gate](#2026-09-28-invocation-stays-a-hard-gate); (medium) the Codex pointer didn't say how a skill load shows in its sessions, so the skill now says a read of `skills/<name>/SKILL.md` is the load.
  - The fresh sub-agent, flagged and left: nested sub-agents stored flat, with their depth in `.meta.json` as `spawnDepth` (later verified correct by the branch review against a live session); the facts stated about the third-party `to-tickets` (kept); the public-repository rule pointing at the user's own instructions (a settled decision; no fallback clause added).
- **Consequences:** Re-check the facts about `to-tickets` if upstream changes.

## 2026-09-28: invocation stays a hard gate

- **Status:** accepted
- **Context:** The docs said the user could also start a recap by asking for one, which the invocation config couldn't honour.
- **Options:** Plain-language triggering: "never offered or run automatically" is the stronger requirement.
- **Choice and why:** Keep `disable-model-invocation: true` and `allow_implicit_invocation: false`, so only `/skill-recap` (Codex: `$skill-recap`) starts it. The docs now name the command.
- **Consequences:** Asking in plain words doesn't start a recap.
