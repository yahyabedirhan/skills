# Handoff: Codex configuration setup and audit

## Objective and authority

Implement [issue #119](https://github.com/yahyabedirhan/skills/issues/119). Its updated body holds the agreed specification and investigation findings; read it live before work. The user requests the same delegation as #123: a dedicated Codex orchestrator, its own subagents, and a reviewable pull request. Coordinate investigation, implementation and independent review through subagents and verify the combined result. Work on set-up-machine/codex-configuration. Commit this handoff with the work as applicable skills direct, push the feature branch, and open the PR with to-pr. Do not merge or install unmerged skills.

## Agreed decisions

Manage only explicitly declared preferences from private agents/codex.toml found through the existing personal-source pointer. Initial keys are sandbox_mode, approval_policy and approvals_reviewer; retain existing hook/memory ownership. Preserve unrelated settings, profiles and stricter constraints. Validate installed-version support; resolve custom Codex config homes consistently. Preserve conflicting default_permissions configurations and report the gap. Distinguish persisted defaults from effective overrides and existing sessions. Keep personal choices and private repository details out of public artifacts.

The issue contains the full facts and criteria. During grilling the inspected CLI was 0.159.3; recheck current support and official docs rather than assume these facts hold forever. Official docs reported separate profile files, unsupported legacy inline profiles and a conflict between default_permissions and legacy sandbox keys. Existing verify.py has fixture-home tests, misses these preference checks and hardcodes default Codex paths in relevant places.

## Scope boundaries

Implement the reusable source schema, setup guidance and verification/tests in this public repository. Do not apply live personal preferences or rewrite installed harness configuration as part of the build; make that a concrete reviewed post-merge follow-up if needed. Never read credentials, environment values, .env files, auth stores or runtime state. Use synthetic configuration and fixture homes without authenticated sessions. Apply only authorized source keys; reject unsupported input and report constraints.

Issue #123 is concurrently delegated in another worktree, addressing Herdr/Treehouse reliability. Issue #67 remains with the originating session, including per-tool human draft approvals. Do not implement those issues here. If source files overlap, keep edits narrowly scoped and report integration considerations in the PR rather than editing the other branch.

## Operating constraints

Read AGENTS.md and docs/decisions/skill-writing.md before edits. Add dated decision entries where needed. Leave this session, Herdr topology and occupied worktree open after delivery. Do not terminate agents, return an occupied worktree, or use delayed external cleanup. Do not restart live sessions to activate defaults.

## Suggested skills

Apply maintain-environment, implement, writing-for-agents, openai-docs, orchestrating for delegated work, and to-pr for delivery. Use primary official references for current Codex behavior, checking installed code/help first per openai-docs. Follow the personal/public source separation required by maintain-environment.

## Delivery

One PR linked to #119, with meaningful fixture tests for fresh setup, preservation, repeat audit, custom config home, invalid input, overrides and conflicts. Report support gaps and activation limits. Provide final-file/diff review links as to-pr directs. Stop for review; no merge without an explicit user go.
