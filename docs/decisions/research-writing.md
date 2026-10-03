# Decisions: research writing

How research documentation in this repo is written: the files in `docs/research/` and the HTML guides beside them. Read it before writing or changing any of them, and add a dated entry for each new decision.

## 2026-10-03: a light version of ASD-STE100

The maintainer reads English as a second language, and the cloud-agents research (#76) was hard to read: long sentences, chains of clauses joined with semicolons, and coined terms nobody defined. A light version of ASD-STE100 (Simplified Technical English) fixed it. Full STE100 doesn't fit research: its controlled dictionary would force awkward wording around product names, citations and comparisons. So only its sentence rules apply.

Write every prose sentence to these rules:

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

These parts keep their exact form: code, commands, paths, config keys, URLs, quoted messages and direct quotes; the numbers in tables; citations and their markers; what an exploration log says was run and found; and any heading that another file links to.

An example, from the cloud-agents synthesis:

> Before: "The VPS becomes the off-Mac orchestrator once Herdr is on 0.9.2 on both machines and set-up-machine is applied there, while Claude Code cloud sessions take tasks, not whole efforts, until E1 shows skills can load there."
>
> After: "The VPS becomes the orchestrator when the Mac is off. This needed Herdr 0.9.2 on both machines and set-up-machine on the VPS. Claude Code cloud sessions take single tasks for now. They take whole efforts only after E1 shows that skills load there."

## 2026-10-03: a research topic gets its own folder

A topic with more than one file lives in `docs/research/<topic>/`: its synthesis is `README.md`, its HTML guide `guide.html`, and each other file is named by its subject without the topic prefix (`docs/research/cloud-agents/vps.md`). The cloud-agents research had fifteen `cloud-agents-*` files side by side in `docs/research/`, and the folder groups them, while GitHub shows the `README.md` when the folder opens.
