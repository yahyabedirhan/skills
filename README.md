# skills

Agent skills I use across projects: my own, and forks of other people's that I've changed.

## Install

```bash
npx skills add yahyabedirhan/skills
```

Add `-s <name>` for one skill, or `-g` to install it for your user rather than the current project.

## Skills

The Origin column names the upstream commit each fork was copied from, so a later upstream change can be diffed against it.

| Skill | What it does | Origin |
|---|---|---|
| [to-pr](skills/to-pr/SKILL.md) | Opens a pull request or rewrites its description: a one-sentence why, reviewer notes, and a visual change outline. | Fork of `visual-pr` from [humanlayer/skills](https://github.com/humanlayer/skills) at [`4e39d8f`](https://github.com/humanlayer/skills/tree/4e39d8fe020f/plugins/visual-pr/skills/visual-pr) (MIT, see `skills/to-pr/LICENSE.humanlayer`). Changes: renamed, a real trigger description, and no Mermaid views. |
| [show-me](skills/show-me/SKILL.md) | Explains the current topic visually with pseudocode, call trees, file trees, `diff` blocks, or one focused HTML file. | Fork of `show-me` from [humanlayer/skills](https://github.com/humanlayer/skills) at [`6ab9013`](https://github.com/humanlayer/skills/tree/6ab9013a10c2/plugins/show-me/skills/show-me) (MIT, see `skills/show-me/LICENSE.humanlayer`). Changes: no Mermaid views, so every view renders as plain text. |
| [maintain-skills](skills/maintain-skills/SKILL.md) | Installs, moves, updates, forks, publishes, removes, and audits skills across global scope, project scope, and your own skills repo with `npx skills`. | Original. |
