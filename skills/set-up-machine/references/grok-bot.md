# Grok Bot

How to set up and audit Grok Bot, the agent app that works on one persistent Linux box shared by all of the user's bots. The app owns approvals, the model, connectors and memory, so most setup areas have no file to write. Skills are the one area the machine setup writes in full.

## Found

Found when `~/agent-data/workflows/` exists: the shared skill library on the box, which every bot reads.

## Instructions

### Global instructions

Grok Bot loads no global instructions file: neither `~/.config/agents/AGENTS.md` nor a project's `AGENTS.md` reaches the chat agent. A cloud agent it starts reads the project's `AGENTS.md` as that harness does.

- Still write the shared file, as every run does, since the `setup` line checks it and it is the source for the next step.
- **Memory:** each bot has its own memory, and all bots share one user memory. Give the user the lines to add, one per instruction, taken from the shared file's Working agreement and Personal workflow sections and from the harness instructions below. The user writes them, or approves the bot writing them, in the app. Mark each line `added` or `present` as the user confirms. The check can't see memory, so this is a `gap`.
- **Harness instructions:** when `setup/harnesses.json` names Grok Bot's `instructions` (workstation.md), its `## Instructions` lines go into the same memory, by the same steps.

### Memory

Memory stays on: it is the only place Grok Bot keeps instructions. Name it once in the report as `gap`, with this reason.

## Guardrails

Grok Bot has no permission lists and no hook. The app decides each call:

- Auto-review checks a shell command, an MCP call, a browser action or a cloud agent before it runs. A block raises an approval card for the user.
- Sending a message or email, posting, buying, and deleting or sharing outside the box need the user's approval, through a draft or approval card.

Mark each rule-table row and personal permission `gap` with the reason "the app's Auto-review decides". Give the user any row Auto-review doesn't hold that matters to them, to add to the bot's memory as an instruction.

## Sandbox

`none`: the box is the sandbox, and the app sets it. Commands on a registered user computer run through the app, each one approved.

## Plugins

Connectors (MCP servers) are added and signed in to in the app, not by a file. For each `setup/installs.json` plugin that names `grok-bot`, a `gap` line asks the user to add or check it in the app's connectors. List the connectors the bot can see, for the report.

## Skills

The library, `~/agent-data/workflows/<skill>/SKILL.md`, is shared by every bot. `npx skills` doesn't know it, so copy each skill folder from its source:

1. Clone or update each `setup/installs.json` skills source at its latest default branch, in a scratch folder.
2. For each skill that applies (every skill folder in a whole-source entry, the named ones otherwise): back up the library first, then replace `~/agent-data/workflows/<skill>/` with the files git tracks in that folder (`git archive HEAD <path> | tar -x --strip-components=<depth>`). Mark it `added`, `updated` or `present`.
3. Record it in `~/.local/state/agents/grok-bot-skill-lock.json`, in the shape of `~/.agents/.skill-lock.json`: `{"skills": {"<skill>": {"source": "<owner>/<repo>", "skillPath": "<path>/SKILL.md", "skillFolderHash": "<git rev-parse HEAD:<path>>"}}}`.

A library folder no entry provides is `extra`, or `ignored` when `ignore` names it: keep it. It may be a skill the user made in the app.

## Config

`none`: the user picks the model in the app. A declared Grok Bot config is a `gap`.

## Hook wiring

`none`: no hook runs. An agent can check a command by hand before running it: `echo '{"command": "<command>"}' | python3 <script> --harness grok-bot` prints `{}`, or a deny with the refusal. Every ask row is refused, since the hook can't see whether the user will be asked.

## Gaps

Instructions, guardrails, memory, plugins and config, as above, and the live check: no session host can start a Grok Bot session.

## Checking it

The verifier's Grok Bot row, from `scripts/setupmachine/harnesses/grok_bot.py`:

- **instructions:** `gap`: the check can't see memory.
- **guardrails:** `gap`: Auto-review and approval cards, no hook.
- **sandbox:** `n/a`.
- **plugins:** `n/a` with no entry for `grok-bot`, else `gap` per entry.
- **skills:** each listed skill has a `SKILL.md` in the library and a lock entry from its source, and its folder's git tree hash equals `skillFolderHash`, so a copy edited after its sync fails. `__pycache__` folders are skipped. Freshness against upstream is Inspect's check, not the verifier's.
- **config:** `n/a` without a declared config, else `gap`.

To see the guardrails act, ask the bot to run `rm -rf x` in a throwaway box folder and check that Auto-review blocks it or asks.
