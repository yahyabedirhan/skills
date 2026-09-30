# Efficiency analysis

Measure what one run of a skill costs in tokens and minutes, and find how to make the next run cheaper.

## 1. Find the run

- The session transcript: a JSONL file under `~/.claude/projects/<project>/<session-id>.jsonl` (Codex: `~/.codex/sessions/`).
- The **phases**: split the run at the user's messages, so each phase is one request and the time spent waiting for the user shows up as its own phase.
- Every sub-agent the run dispatched. Its tokens live in its own transcript, not the parent's; the completion notice reports its total tokens, tool uses and duration.

## 2. Measure

```bash
python3 <skill-dir>/scripts/session-usage.py <transcript.jsonl> --split <HH:MM:SS> ...
```

It prints the user-message timestamps (to choose `--split` points) and, per phase: model calls, output tokens, cache reads, cache writes and uncached input. Add wall time per phase and the duration of each slow command (renders, installs, crawls, long waits) from the tool results.

Plan cost: on a subscription, report the host's usage reading (percent of the 5-hour and weekly windows, from the app's usage tool or `/usage`). On API billing, price the tokens with the current rates from `/claude-api`, never from memory, because rates change.

## 3. Split one-time from per-run

Mark each cost **one-time** (learning a tool, reading its docs, exploring assets, first installs, designing the templates) or **per-run** (what the next run repeats). The skill exists to carry the one-time learning, so a later run pays only the per-run share.

## 4. Find the levers

Rank them by the saving they buy:

- **Context re-reads** usually dominate: every model call re-reads the whole context, so cost grows as calls × context size. Run a heavy phase in a fresh sub-agent that starts from a short brief and returns a short report; batch commands into fewer calls; keep large outputs in files and read excerpts.
- **Authored output**: move code or prose written fresh each run into scripts and templates the skill ships, so a run writes only its data.
- **Waiting**: run slow commands in the background, each with a time budget, while other work continues.
- **Images**: every screenshot read costs tokens; review one contact sheet rather than each frame.
- **Model**: judge cost per task, not per token. A stronger model that finishes in fewer calls is usually cheaper overall, so keep the session's model unless a measured run says otherwise.

## 5. Report

A table of phases and sub-agents (time, calls, output, cache reads, sub-agent tokens), the plan usage or price, the one-time and per-run split, and the ranked levers. End with the estimated per-run cost once the levers are applied, labelled as an estimate.
