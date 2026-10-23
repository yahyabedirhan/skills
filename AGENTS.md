# Agent instructions

This file holds the rules every agent follows when it works in this repo.

## Agent skills

### Issue tracker

Issues live in this repo's GitHub issues, in `yahyabedirhan/skills`, through the `gh` CLI.
There are no triage labels: label a new issue `enhancement` or `bug`, whichever fits.

### Domain docs

This repo is single-context, with one `GLOSSARY.md` at the root and the decision records in `docs/decisions/`.
See `docs/agents/domain.md`.

### Glossary

Before maintaining the repo, read `GLOSSARY.md`, which defines the words this repo uses for its skills, forks and their origins.

### Writing skills

Before writing or changing a skill, read `docs/decisions/skill-writing.md`: the shape, the language and what a skill leaves out and keeps.

### Writing docs

Before writing or changing anything under `docs/`, such as research, guides, decision records and agent docs, read `docs/decisions/technical-writing.md`: a light version of ASD-STE100 for every sentence, and one folder per research topic.

Before changing a skill, read its decision file in `docs/decisions/`: why the skill is shaped as it is.

A decision entry has five fields, as `docs/decisions/index.md` shows.
Before changing `maintain-environment`, `set-up-machine` or `set-up-project`, read its design in `docs/design/`.
