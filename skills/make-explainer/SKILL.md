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
3. **Ask once.** In a single round, ask what the user wants to learn from the video, together with anything else the brief can't settle from the project. Then build the brief and script around that question rather than around everything the project contains, and go on without further check-ins, since the user wants a video, not a discussion.
4. **Build it.** Scaffold the video, write its script, generate the voice, build the scenes, look at stills, and render, as the studio's `AGENTS.md` describes.
5. **Hand it over.** Give the user the path to the rendered MP4, and `npm run dev` in the studio to preview or tweak it.
