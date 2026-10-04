---
name: make-explainer
description: Make a narrated explainer video about a project, feature or setup in the local explainer studio. Use when the user asks for an explainer or walkthrough video.
---

# Make an explainer

Make a narrated explainer video about the project the user is working in. The video is made and kept in the explainer studio, [yahyabedirhan/explainer-studio](https://github.com/yahyabedirhan/explainer-studio). The project is only the source: read it and leave it unchanged, so no video setup ever lands in it.

## Parameters

- `<studio>`: the studio's clone, e.g. `~/Developer/<owner>/explainer-studio`.

## Flow

1. **Open the studio.** Work in `<studio>` and read its `AGENTS.md` before anything else. It holds the studio's commands and rules, and wins where it differs from this skill.
   - **When there's no clone:** clone it to `<studio>`, set it up as its README's Setup section says, and render the README's smoke-test video once to confirm it works.
2. **Learn the subject.** Read the project's code, docs and pull requests until you can explain what the user asked about, end to end.
3. **Plan with the user.** Find out what the user wants to learn from the video, and build the brief and script around that question rather than around everything the project contains. Scaffold the video, fill its brief, and draft the script and scene plan as the studio's `AGENTS.md` describes. Show them to the user and wait for their approval before writing animation code, since the script is the part they most want to shape.
4. **Build it.** Generate the voice, build the scenes, look at stills, and render, as the studio's `AGENTS.md` describes.
5. **Hand it over.** Give the user the path to the rendered MP4, and `npm run dev` in the studio to preview or tweak it.
