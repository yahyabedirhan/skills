# Decisions: technical writing

How everything under `docs/` is written: research files and their HTML guides in `docs/research/`, the decision records in `docs/decisions/`, and the agent docs in `docs/agents/`. A decision record also follows the shape in [index.md](index.md), and so do the entries below. Skills follow `skill-writing.md` instead.

## 2026-10-03: a light version of ASD-STE100

- **Status:** accepted
- **Context:** Many readers read English as a second language. The cloud-agents research (#76) was hard to read: long sentences, chains of clauses joined with semicolons, and coined terms nobody defined.
- **Options:** Full ASD-STE100 (Simplified Technical English): its controlled dictionary would force awkward wording around product names, citations and comparisons.
- **Choice and why:** Apply only STE100's sentence rules, to every document under `docs/`. They fixed the cloud-agents research. Write every prose sentence to these rules:
  - **One idea per sentence.** Split a sentence that joins two statements with "and", "but", "which", "while" or a dash.
  - **Keep sentences short.** At most 20 words in a step or instruction, at most 25 elsewhere; aim for 15.
  - **Start each step with a verb** in the imperative ("Push the handoff."), with one action per step. Number the steps when their order matters.
  - **End a statement with a full stop.** Use semicolons only between the items of a list.
  - **Write in the active voice,** and name who acts: "The agent opens a workspace." Use the passive only when the actor is unknown.
  - **Use at most three nouns in a row:** "the status file of each remote orchestrator", not "remote orchestrator status file".
  - **Give each word one meaning,** and use the same word for the same thing throughout. Prefer the common word: "use", "start", "check", "about".
  - **Say what a metaphor means:** "run in parallel", not "fan out".
  - **Define each project term once,** in plain words: in the guide's glossary, or at its first use in a Markdown file. Effort, orchestrator, delegate, handover and settle are examples.
  - **Keep paragraphs to six sentences or fewer,** with the main point first.
  - **Turn a sentence into a list** when it names more than three items or conditions.
  - **Keep the small words:** "the", "a", "that". A sentence compressed without them is harder to parse.
- **Consequences:** These parts keep their exact form: code, commands, paths, config keys, URLs, quoted messages and direct quotes; the numbers in tables; citations and their markers; what an exploration log says was run and found; and any heading that another file links to. An example, from the cloud-agents synthesis:

  > Before: "The VPS becomes the off-Mac orchestrator once Herdr is on 0.9.2 on both machines and set-up-machine is applied there, while Claude Code cloud sessions take tasks, not whole efforts, until E1 shows skills can load there."
  >
  > After: "The VPS becomes the orchestrator when the Mac is off. This needed Herdr 0.9.2 on both machines and set-up-machine on the VPS. Claude Code cloud sessions take single tasks for now. They take whole efforts only after E1 shows that skills load there."

## 2026-10-03: a research topic gets its own folder

- **Status:** accepted
- **Context:** The cloud-agents research had fifteen `cloud-agents-*` files side by side in `docs/research/`.
- **Options:** None considered.
- **Choice and why:** A topic with more than one file lives in `docs/research/<topic>/`. Its synthesis is `README.md`, and its HTML guide is `guide.html`. Each other file is named by its subject, without the topic prefix (`docs/research/cloud-agents/vps.md`). The folder groups the files, and GitHub shows the `README.md` when the folder opens.
- **Consequences:** None.

## 2026-10-18: three writing rules for every page

- **Status:** accepted
- **Context:** A cleanup of the repo found the same mistakes in many files: lines joined into long paragraphs, labels that only made sense in the conversation that coined them, and section titles that named a task or a chat phrase instead of a part.
- **Options:** A formatter such as Prettier. Rejected: it breaks a sentence at a column and joins lines that were split on purpose. A rule for each convention found. Rejected: more rules give an agent more to over-apply.
- **Choice and why:** Three rules for every document in the repo.
  - **Write for a reader who was not in the conversation.** A file says what a thing is, not what it was called in chat. Describe what a label names, or define it where it first appears.
  - **Break lines at sentences.** Put one sentence on each line, and keep a paragraph as consecutive lines. Sentences stay easy to scan and to compare in a diff.
  - **Name each section with a noun phrase.** Use one name for one part across pages, such as `Verification`, `Limitations`, `Notes` and `Steps`. Keep every heading that another file points to, and fix the pointers when you change one.
- **Consequences:** Each rule applies to new and changed pages. Dated decision entries stay as written. A pointer to a decision file lives in `AGENTS.md`, since a sentence inside the file cannot make an agent open it. The maintainer's own writing preferences stay in the maintainer's workstation repo.
