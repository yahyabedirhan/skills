# Designs

This folder explains how a skill is built: its requirements, its parts and how they call each other, a traced run, and what a likely change touches.
It has one file per skill whose parts are not obvious from its `SKILL.md`.
These files are for maintainers and are never installed.
Each follows the low-level design stages: Requirements, Entities and relationships, Class design, Implementation, Extensibility.

- [maintain-environment.md](maintain-environment.md): the starting point for any change to what agents run with.
- [set-up-machine.md](set-up-machine.md): applying the workstation repo's `setup/` to a machine, the pre-tool hook, and the verifier.
- [set-up-project.md](set-up-project.md): one project's agent files and its audit.
