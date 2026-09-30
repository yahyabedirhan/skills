---
name: low-level-design
description: Design, explain or redesign code at the level of modules, classes, files and folders, through the low-level design delivery framework. Use when designing a new project or feature from a spec, explaining how an existing codebase is structured, restructuring one, or deciding where code should live.
---

# Low-level design

A low-level design decides which modules exist, what state and rules each one owns, how they call each other, and where each file sits. A good one lets a newcomer find what they came for (where the program starts, how to add an endpoint, where the shared logic lives, what a change touches) without reading everything. Produce and present it through the **delivery framework** in every session, whether you are designing, explaining or redesigning, so the user always finds the same things in the same places. The user chooses what the session is for; the framework sets how you lay out the answer. Stop once the user agrees to the design, since building it is done later, from tickets.

The recurring failure is structure added before it is needed: factories with one product, interfaces with one implementation, a file per function. Start from the simplest design that meets the requirements, and add a class, an interface or a pattern only for a named reason, such as a second implementation today or the same edit repeated across several files. Before designing a module, check whether a dependency the project already has provides it, and build only the difference.

## The flow

1. **Restate the session's purpose in one line**, read from the request and its context, so a misreading costs one reply: designing something new, explaining existing code, redesigning it, deciding one thing, or a mix. Invoked with no instructions inside a project, write down that project's current design. When the purpose isn't clear, ask what the user wants to do with the design, whether the code exists, and whether they want only an explanation. For any purpose but a new design, read `session-purposes.md`.
2. **Requirements**: numbered, checkable requirements, and an out-of-scope list with a reason for each exclusion.
3. **Entities and relationships**: the entities, the orchestrator that drives the main workflow, and how they relate, as arrows.
4. **Class design**: each module's state and operations, derived from the requirements, and the folder tree.
5. **Implementation**: the methods that carry the logic, and one traced scenario plus one traced rejection.
6. **Extensibility**: a "change → what you touch" table, and the changes refused for now with their reasons.
7. **Present, take feedback and revise** until the user agrees.
8. **Keep the design where the user wants it.**

Steps 2 to 6 are the framework's stages, and each rests on the one before it. Go back to an earlier stage when a later one exposes a gap. Avoid two opposite failures: writing code before the structure is clear, and polishing details so long that the design never comes together. Read `delivery-stages.md` for how to work each one, and a principles, concepts or patterns reference when a decision calls for it.

### Presenting and revising

Load `/show-me` and present every stage visually, with prose only for the reasons behind choices.

- Keep one current version of the design and revise it rather than starting over.
- Open each revision with what changed and why, as a before/after of the parts that moved, and carry a change through every part it affects.
- Leave a point the user settled as it is unless they reopen it.
- When the design has more than one reasonable option, number the options side by side, each with its cost, and lead with your recommendation.
- Ask only what the code, the spec and the project's docs can't settle, one question at a time. Decide the rest and say what you decided.

### Keeping the design

The user decides what is kept and where. While the design is being refined, keep it in a draft in the project's temp or scratch folder, following the repository's conventions; when it has none, ask where. An explanation can stay in the conversation. Once the user agrees and wants the design kept, write it into the project's documentation, and update an existing design document rather than adding a second, so the project has one. Open it with what a newcomer needs first, then give each stage its own section.

## References

- [delivery-stages.md](references/delivery-stages.md): how to work each stage, and how to show what it produces.
- [session-purposes.md](references/session-purposes.md): how explaining existing code, redesigning it and deciding one thing run.

### Principles, concepts and patterns

| Reference | Covers |
|---|---|
| [design-principles.md](references/design-principles.md) | KISS, DRY, YAGNI, separation of concerns, Law of Demeter, SOLID |
| [oop-concepts.md](references/oop-concepts.md) | Encapsulation, abstraction, polymorphism, inheritance and composition |
| [design-patterns.md](references/design-patterns.md) | Creational, structural and behavioural patterns, and when each is over-engineering |
| [layout.md](references/layout.md) | Folders, generic and business code, naming, when to split a file |

---

Source: Hello Interview, [Introduction](https://www.hellointerview.com/learn/low-level-design/in-a-hurry/introduction) and [Delivery Framework](https://www.hellointerview.com/learn/low-level-design/in-a-hurry/delivery).
