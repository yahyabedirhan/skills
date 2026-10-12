# Grok Bot

How to set up and audit Grok Bot, the agent app that works on one persistent Linux box shared by all of the user's agents. The app keeps most settings other harnesses keep in files: memory, Auto-review, connectors, secrets and routines. So the agent applies most areas through the app's own tools, or gives the user a step, and the verifier checks what a file shows.

## Found

Found when `~/agent-data/workflows/` exists: the shared skill library on the box.

## Instructions

Grok Bot loads no instructions file. Neither `~/.config/agents/AGENTS.md` nor a project's `AGENTS.md` reaches the chat agent; a cloud agent it starts reads the project's `AGENTS.md` as that harness does. Memory takes their place:

| Source | Where it goes | Who reads it |
|---|---|---|
| The shared file's personal parts, from the workstation repo's `setup/instructions.md` | **user memory**: one fact per instruction | every agent, each turn |
| Grok Bot's own instructions, the `instructions` file `setup/harnesses.json` names | **agent memory**, at the profile tier: one fact per instruction | this agent, each turn |
| The agent's job, from the same file's notes | the agent's **title and description** (profile) | the app and the user |

Still write the shared file, as every run does: the `setup` line checks it.

- **Apply:** write each instruction as one short fact, in the source's words, in its scope. When the agent can't write memory itself, give the user the list, split by scope, and wait until they confirm. Then write the lock (*Reconcile*).
- **Keep each fact to one instruction.** A fact that names a file to read, such as the shared file, holds one line, not the file.

### Reconcile

Memory can't be read by a script, so the lock records what was applied and from which commit:

```json
{"sha": "<workstation commit>", "date": "<YYYY-MM-DD>",
 "sources": {"setup/instructions.md": ["<fact>"], "<grok-bot instructions path>": ["<fact>"]}}
```

at `~/.local/state/agents/grok-bot-instructions-lock.json`. To bring memory up to date:

1. Run `git -C <path-to-workstation-repo> diff <sha>..HEAD -- setup/instructions.md <grok-bot instructions path>` on the latest default branch.
2. Map each changed line to a fact: an added line is **add**, a changed line is **rewrite** of the fact the lock lists for it, a removed line is **forget** that fact. User scope for `setup/instructions.md`, agent scope for Grok Bot's own file.
3. Apply each one, or give the user the list and wait until they confirm.
4. Rewrite the lock with the new `sha`, the date and every fact now applied.

A fact in memory that the lock doesn't list is the user's: keep it, and name it as `extra` when you see it.

### Memory

Memory stays on: it holds the instructions. Name it once in the report.

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

- **instructions:** `ok` when each source file is the same as at the lock's `sha`; `FAIL`, marked stale, when one changed; `gap` without a lock.
- **guardrails:** `gap`: Auto-review and its rules can't be read.
- **sandbox:** `n/a`.
- **plugins:** `n/a` with no connector declared, else `gap` per connector.
- **skills:** each listed skill has a `SKILL.md` in the library and a lock entry from its source, and its folder's git tree hash equals `skillFolderHash`. `__pycache__` folders are skipped. Freshness against upstream is Inspect's check.
- **config:** each `secrets` name is set in the real home's environment, checked by name only; `routines` is a `gap`; an unknown key is a `gap`; `n/a` without a declared config.

For the live check, ask the agent in a new chat to recall three facts from each scope, and to run `rm -rf x` in a throwaway box folder; Auto-review should block it or ask.
