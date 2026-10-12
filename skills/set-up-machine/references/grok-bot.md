# Grok Bot

How to set up and audit Grok Bot, the agent app that works on one persistent Linux box shared by all of the user's agents. The app keeps most settings other harnesses keep in files: memory, Auto-review, connectors, secrets and routines. So the agent applies most areas through the app's own tools, or gives the user a step, and the verifier checks what a file shows.

## Found

Found when `~/agent-data/workflows/` exists: the shared skill library on the box.

## Instructions

> **Grok Bot differs here.** Other harnesses read instructions from files the setup writes. Grok Bot reads none: the agent applies instructions into its own memory with its memory tool. The verifier can't read memory, so it compares a lock (the source commit and the exact facts written) with the current sources. Follow the steps below instead of the shared file's link or copy.

| Source | Scope | Who reads it |
|---|---|---|
| `setup/instructions.md` in the workstation repo | user memory | every agent, each turn |
| the `instructions` file `setup/harnesses.json` names for `grok-bot` | agent memory, profile tier | this agent, each turn |
| that file's notes on the agent's job | the profile's title and description | the app and the user |

The lock is `~/.local/state/agents/grok-bot-instructions-lock.json`:

```json
{"sha": "<workstation commit>", "date": "<YYYY-MM-DD>",
 "sources": {"setup/instructions.md": ["<fact as written>"], "<grok-bot instructions path>": ["<fact as written>"]}}
```

The **applied log** is the workstation repo's `harnesses/grok-bot/applied.md`, when it exists: one dated entry per apply or reconcile, never edited later.

You may merge or reword lines into facts. The lock and the log always hold the exact text written, since a later forget or rewrite finds the fact by it.

### First-time apply

1. Write the shared file as every run does; the `setup` line checks it.
2. Read `setup/instructions.md` and Grok Bot's instructions file at the workstation repo's latest default branch. Note its commit, `git rev-parse HEAD`.
3. Turn each instruction line of `setup/instructions.md` into one short fact, and write each with the memory tool in user scope.
4. Turn each line under `## Instructions` of Grok Bot's file into a fact, and write each in agent scope.
5. Set the profile's title and description from that file's notes.
6. When you can't write memory or the profile, give the user the facts by scope and wait until they confirm the exact texts written.
7. Write the lock with the commit, the date and each exact fact.
8. Append a log entry: the date, the commit, each fact added per scope, and the Auto-review rules handed over.
9. Give the user the Auto-review rules text (*Guardrails*) and each user-only step: rules to paste, connectors, secrets, rulesets.

### Reconcile

Run it when the verifier's instructions cell says stale.

1. Run `git -C <path-to-workstation-repo> diff <lock sha>..HEAD -- setup/instructions.md <grok-bot instructions path>`.
2. Map each changed line: added is **add**; changed is **rewrite** of the lock's fact for it; removed is **forget** that fact. User scope for `setup/instructions.md`, agent scope for Grok Bot's file.
3. Apply each with the memory tool, finding an old fact by its exact lock text. Or give the user the list and wait until they confirm.
4. Rewrite the lock with the new commit, the date and every fact now applied.
5. Append a log entry with each fact added, rewritten (old and new text) or forgotten, per scope.

### Audit

1. Run `verify.py`. Instructions is `ok` when each source equals its version at the lock's commit, stale (`FAIL`) when one changed, `gap` without a lock.
2. Recall memory in each scope and compare it with the lock's facts. A lock fact missing from memory is drift: write it again. A fact the lock doesn't list is the user's: keep it, and name it `extra`.
3. Live check: in a new chat, ask the agent to recall three facts from each scope.

Memory stays on: it holds the instructions.

## Guardrails

Grok Bot has no permission lists and no hook. The app decides each call:

- **Auto-review** checks a shell command, an MCP call, a browser action or a cloud agent before it runs. A block raises an approval card for the user.
- **Auto-review rules** add the user's own rules to it. Only the user edits them, in Settings > General. Print the paste-ready text with `verify.py --grok-bot-rules`, which turns every row of the rule table and the personal permissions into a Block, Ask the user first or Allow line. Give it to the user to paste whenever a row changes.
- **Sending a message or email, posting, buying, and deleting or sharing outside the box** need the user's approval through a draft or an approval card.
- **Hard limits outside the agent:** a token's scope and a repository's rulesets, such as blocking force pushes to `main`, hold even when an instruction is missed. Name each one the workstation repo lists as a step for the user.

## Sandbox

`none`: the box is the sandbox, and the app sets it. Commands on a **registered computer** run through the app, each approved by the user when local execution asks, and only while that computer is online. Document which computers are registered in the workstation repo; there is nothing to write.

## Plugins

Connectors (MCP servers) are installed in the app, per account, each with optional custom instructions. List the expected ones in the declared config's `connectors`, or as `setup/installs.json` plugins that name `grok-bot`. For each one, give the user the step to add it and sign in, and put any instruction for that connector in its custom instructions, not in memory. List the connectors the agent can see, for the report.

## Skills

The library, `~/agent-data/workflows/<skill>/SKILL.md`, is shared by every agent. `npx skills` doesn't know it, so copy each skill folder from its source:

1. Clone or update each `setup/installs.json` skills source at its latest default branch, in a scratch folder.
2. For each skill that applies (every skill folder in a whole-source entry, the named ones otherwise): back up the library first, then replace `~/agent-data/workflows/<skill>/` with the files git tracks in that folder (`git archive HEAD <path> | tar -x --strip-components=<depth>`). Mark it `added`, `updated` or `present`.
3. Record it in `~/.local/state/agents/grok-bot-skill-lock.json`, in the shape of `~/.agents/.skill-lock.json`: `{"skills": {"<skill>": {"source": "<owner>/<repo>", "skillPath": "<path>/SKILL.md", "skillFolderHash": "<git rev-parse HEAD:<path>>"}}}`.

A library folder no entry provides is `extra`, or `ignored` when `ignore` names it: keep it. It may be a skill the user made in the app.

## Config

There is no model to set: the app picks it. When `setup/harnesses.json` names a Grok Bot `config`, it is a JSON object with these keys, each optional:

- `secrets`: the names of the environment variables the app's secret store must set, such as a GitHub token. The user adds each in the app. Check a name with `test -n "$NAME"`; never print a value.
- `connectors`: the connectors the user should have (*Plugins*).
- `routines`: each scheduled or event-triggered prompt the agent should run, as `{"name", "trigger", "prompt"}`. Create or check each with the app's routine tools; an empty list means none.

## Hook wiring

`none`: no hook runs. An agent can check a command by hand before running it: `echo '{"command": "<command>"}' | python3 <script> --harness grok-bot` prints `{}`, or a deny with the refusal. Every ask row is refused, since the hook can't see whether the user will be asked.

## Gaps

Memory and Auto-review rules can't be read from the box; connectors and routines are seen only through the app; no session host starts a Grok Bot session for the live check.

## Checking it

The verifier's Grok Bot row, from `scripts/setupmachine/harnesses/grok_bot.py`:

- **instructions:** as *Audit*, step 1.
- **guardrails:** `gap`: Auto-review and its rules can't be read.
- **sandbox:** `n/a`.
- **plugins:** `n/a` with no connector declared, else `gap` per connector.
- **skills:** each listed skill has a `SKILL.md` in the library and a lock entry from its source, and its folder's git tree hash equals `skillFolderHash`. `__pycache__` folders are skipped. Freshness against upstream is Inspect's check.
- **config:** each `secrets` name is set in the real home's environment, checked by name only; `routines` is a `gap`; an unknown key is a `gap`; `n/a` without a declared config.

For the live check, ask the agent in a new chat to recall three facts from each scope, and to run `rm -rf x` in a throwaway box folder; Auto-review should block it or ask.
