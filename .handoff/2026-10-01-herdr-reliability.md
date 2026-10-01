# Handoff: Herdr and Treehouse settlement reliability

## Objective and authority

Implement [issue #123](https://github.com/yahyabedirhan/skills/issues/123), using its updated body as the specification. The user explicitly delegated this to a new Codex session with its own subagents, delivering a pull request. Read the live issue before building. Use subagents for investigation and independent review; coordinate and verify their results. Commit the handoff with the work as the applicable skills direct, push the feature branch and open the PR through to-pr. Stop at a reviewable PR: do not merge or install unmerged skills.

## Scope and decisions

The issue contains the full investigation and grilling decisions; do not duplicate them here. The agreed direction preserves autonomous authorized setup and empty-worktree cleanup. Settlement keeps all Herdr topology and the caller session open, preserves shared/occupied worktrees, reports mismatches, refreshes live caller/target identities, guards release by lease identity, and makes branch deletion conditional on successful release and merge proofs. Do not add blanket approval requirements. Do not implement issues #119 or #67; those remain with the originating session. Issue #25 is closed as not planned.

## Evidence boundaries

Instruction defects and Treehouse process termination are established. Stale-state targeting is plausible but the original workspace movement/deletion and responsible actor are unproven. Do not claim a confirmed Herdr software bug. Use the public references in #123; do not publish private repository identities, transcripts or machine-specific details.

Inspect settle-session, settle-effort, handover-to-herdr including settle-commands.md, treehouse, their callers and decision records. Check installed Herdr guidance against the actual installed CLI and relevant public source. Installed CLI/server were 0.9.0 during handover; installed skill guidance can describe newer behavior, so rediscover supported syntax. The external Herdr skill is upstream-managed: do not patch its installed copy; handle required source changes through a reviewable upstream/fork route or clearly report a remaining gap.

## Verification and operating constraints

Read AGENTS.md and docs/decisions/skill-writing.md before edits. Add dated decisions where appropriate. Verify command semantics with source, CLI help and fixtures. Do not move, close or terminate live user workspaces, tabs, panes, agents or services to reproduce the bug. Use isolated fixtures; any live experiment that needs separate authorization must be reported. Never schedule external delayed cleanup or release this occupied worktree. Leave the Codex session and workspace open when the PR is ready. Use explicit live target IDs and preserve focus during authorized setup.

## Suggested skills

Read and apply maintain-environment, implement, writing-for-agents, diagnosing-bugs where needed, orchestrating for delegated coordination, and to-pr for delivery. Read relevant tool skills only when actually operating those tools. User authorization and the updated issue decisions override conflicting legacy cleanup instructions.

## Delivery

One PR implementing the agreed scope with validation, residual factual uncertainty and external-source limitations reported. Link #123 and provide its final-file/diff review links as to-pr directs. No merge without the user's explicit go.
