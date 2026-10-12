---
name: show-me-diagram
description: Explain the current topic, a status or a concept as one designed diagram, made with the diagram-design skill in the user's Cursor Dark profile. Use when the user asks to see it as a diagram or with diagram-design. For a quick view in plain text, use show-me; for a report or decision page to read later, use show-me-artifact.
---

Show the topic as one diagram the user opens in a browser. The diagram is for the user's own understanding, so stay with plain text when you only need to explain something to another agent.

1. **Load the `diagram-design` skill** and follow it for the build. Don't restate or replace its rules, since it changes upstream.
2. **Use the user's profile** at `$HOME/.diagram-design/profiles/cursor-dark.md`.
   - **When the file is missing,** tell the user and build with the shipped default, since the profile copy is a manual step on a new machine.
3. **Pick the diagram type that fits the point,** from the types `diagram-design` lists: a flowchart or sequence for a process, a state machine for status, a tree or layer stack for structure, a timeline for progress. Make one diagram per point. Above about nine nodes, split it.
4. **Open the file for the user,** with one or two lines on what it shows. Keep the rest of the reply short, since the diagram carries the point.
