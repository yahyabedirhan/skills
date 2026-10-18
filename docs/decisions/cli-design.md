# Decisions: cli-design

The decisions behind the `cli-design` skill. This file is for maintaining it and is never installed. Entries follow the shape in [index.md](index.md).

## Maintaining

`SKILL.md` is the delivery framework, plus how to run it with the user and how each kind of session runs. `references/conventions.md` holds the shared conventions that a stage consults: verbs, flags, exit codes, environment variables, configuration precedence and help layouts. Both end with a Sources line. Keep every example generic: no real tool's commands in the skill's body, because the skill is for any CLI.

## 2026-10-13: the skill is a delivery framework, like its siblings

- **Status:** accepted
- **Context:** A design session on one app's CLI found verbs with several meanings, lists written by hand in three places that disagreed, and a flat help of 78 commands. The maintainer wanted a repeatable way to design CLIs, in the shape of `/low-level-design` and `/system-design`.
- **Options:** A checklist alone: it audits a CLI but doesn't lay out a design.
- **Choice and why:** Seven stages, from requirements to evolution, each with a product to show, and a review checklist at the end. The framework stays in `SKILL.md`, as for the other design skills.
- **Consequences:** The skill joins the Design frameworks family.

## 2026-10-13: generic, with no named tool

- **Status:** accepted
- **Context:** The framework came from comparing one app's CLI with two other tools' CLIs. The maintainer publishes the skill for anyone.
- **Options:** Keep the comparison as worked examples: it overfits the skill to tools a reader may not know.
- **Choice and why:** Placeholders and generic nouns only. The skill tells the agent to study a similar well-known tool's help when one exists.
- **Consequences:** None.

## 2026-10-13: one reference for the conventions

- **Status:** accepted
- **Context:** The verb vocabulary, flag names, exit codes and help layouts are tables that only some stages of some sessions consult.
- **Options:** Inline them: they would double the length of `SKILL.md`. One reference per topic: too many small files.
- **Choice and why:** One reference, `conventions.md`, read when a stage reaches flags, codes, environment, configuration or the help's layout.
- **Consequences:** None.

### References
- [Command Line Interface Guidelines](https://clig.dev/): subcommands, robustness, future-proofing and help
- [POSIX Utility Conventions](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap12.html): argument syntax and `--`
