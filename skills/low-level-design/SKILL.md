---
name: low-level-design
description: Design, explain or redesign code at the level of modules, classes, files and folders, through the low-level design delivery framework. Use when designing a new project or feature from a spec, explaining how an existing codebase is structured, restructuring one, or deciding where code should live.
---

# Low-level design

This skill is the **delivery framework**: the standard order for producing and presenting a low-level design. Every session follows it, whether the design is new, explained, or redesigned, so the user always finds the same things in the same places. The user decides what the session is for; the framework decides how the answer is laid out. The references hold the principles, concepts and patterns each stage draws on.

A low-level design decides which modules exist, what state and rules each one owns, how they call each other, and where each file sits. A good one lets a newcomer find what they came for (where the program starts, how to add an endpoint, where the shared logic lives, what a change touches) without reading everything. The session ends at an agreed design; building it goes to tickets.

## What the session is for

The user usually says what they want when they invoke the skill. Read the purpose from the request and its context, and restate it in one line before starting, so a misreading costs one reply.

- Invoked with no instructions inside a project: write down that project's current design through the framework.
- When the purpose isn't clear, ask the user what they want to do with the design, whether the code exists or is new, and whether they want only an explanation.

The purposes below are common shapes, not a menu. A session can mix them, move from one to another (an explanation turning into a redesign), or be something else; fit the framework to what the user asked for.

### Designing something new

Design it end to end from the user's spec: a complete first draft through every stage. Where the design forks, present the options with what each gains and costs and a recommendation, so the user picks. When feedback changes one part, carry the change through every part it affects, and show what moved.

### Explaining existing code

Walk the code through the stages as it is, without changing it:

- Build each stage from the evidence: an existing design document (start there and check it against the code), the code itself (entry points, types, folders, tests), or the user's description. Cite the file behind each claim.
- Requirements read from behaviour and tests are marked **inferred**. What the code can't show (why a choice was made, what is planned) is marked **unknown** and asked about, never filled in.
- Show what each file owns and, where a file mixes several things, what it mixes. Weaknesses are observations, not proposals.
- Answer follow-up questions by tracing a call through the design.

### Redesigning existing code

1. **Explain it as it is now**, as above, and get the user's agreement that it's right.
2. **Redesign it through the same stages**, changing only what the redesign needs. A small change runs only the stages it touches; a restructure runs them all.
3. **Show the before and after** of every stage that changed, including the folder tree.

### Deciding one thing

A question like "should this be an interface?" or "where does this module go?" is one decision: the part of the design it touches, the requirement behind it, the options with their trade-offs, and a recommendation.

## The delivery framework

```text
Requirements → Entities and relationships → Class design → Implementation → Extensibility
```

Each stage rests on the one before it: the entities come from the requirements, the classes give the entities state and behaviour, the implementation proves the classes work, and extensibility tests them against what comes next. Move on once a stage has its product, and come back when a later stage exposes a gap. The two ways to fail are opposite: jumping to code before the structure is clear, and polishing details until there is no design.

### 1. Requirements

Turn the request or spec into something to design against, working down four themes:

- **Capabilities**: the operations the system must support.
- **Rules and completion**: what defines success and failure, and when the system stops or changes state.
- **Error handling**: how it responds to invalid input and illegal actions.
- **Scope**: what is in (core logic, business rules), and what is explicitly out (UI, storage, concurrency, whatever the user excludes).

Product: numbered, checkable requirements, and an out-of-scope list with a reason for each exclusion. The exclusions keep the design from growing features nobody asked for.

### 2. Entities and relationships

Take the nouns from the requirements. A noun that holds changing state or enforces rules is an entity; one that is only information attached to another is a field on it. This keeps the design from breaking into micro-objects.

Then settle how they relate: which entity is the **orchestrator** driving the main workflow, which own durable state, which has, uses or contains which, and where each rule lives.

Product: the entities as a list and the relationships as arrows (`Game -> Board`). Boxes and arrows are enough; skip formal UML.

### 3. Class design

Turn each entity into a class or module, top-down from the orchestrator, and derive both halves from the requirements rather than from intuition:

- **State**: what it must remember to enforce the requirements it owns.
- **Behaviour**: what callers must be able to ask or tell it, each operation with what it returns and rejects, in a small API where each method matches a real action or question.

Keep each rule with the module that owns its state (**tell, don't ask**): lifecycle rules ("can this run now?") belong to the orchestrator, data rules ("is this cell taken?") to the module holding the data, so when something breaks you know which module to open. Place the modules in folders by [layout.md](references/layout.md).

Product: each module's state and operations, and the folder tree.

### 4. Implementation

Sketch the methods that carry the logic, not every method: the happy path first (the steps, the calls into other modules, the state changed), then the edge cases (invalid input, illegal operations, calls in the wrong state). Pseudocode unless the project needs real code.

Then verify: trace one concrete scenario step by step, with the state after each step, plus one rejection, and fix what the trace reveals (a state never set, a rule checked too late).

Product: the key methods and the two traces.

### 5. Extensibility

Test the design against the changes likely to come next: for each, the part that absorbs it and what changes. A design that routes every state change through one place takes a feature like undo without restructuring. A change that lands in one new file plus a registration is already absorbed; one that repeats the same edit across several files needs a seam. Refuse the rest, keeping to what the requirements need now.

Product: a "change → what you touch" table, and the changes refused for now with their reasons.

### Simple first, prove the need

The recurring failure in low-level design is structure added before it is needed: factories with one product, interfaces with one implementation, a file per function. Start from the simplest design that meets the requirements and add a class, an interface or a pattern for a named reason, such as a second implementation today or the same edit repeated across several files. Before designing a module, check whether a dependency the project already has provides it, and build only the difference.

## Working with the user

A session is a loop: present, the user gives feedback, revise, present again, until the user is satisfied.

- **Keep one current version** of the design and revise it; don't start over.
- **Open each revision with what changed and why**, as a before/after of the parts that moved.
- **A point the user settled stays settled** unless they reopen it.

## Showing and asking

Load the **show-me** skill and present every stage visually, with prose only for the reasons behind choices:

- requirements and entities as short lists, relationships as arrows;
- the folder tree with one comment per line saying what each file or folder owns;
- a redesign or a revision as a before/after `diff` of the tree or list that changed;
- a traced flow as a call tree, with the owning file beside each call;
- mappings as small tables: requirement → module, change → what you touch.

At a real fork, number the options side by side, each with its cost, and lead with your recommendation. Ask only what the code, the spec and the project's docs can't settle, one question at a time; decide the rest and say what you decided.

## Principles, concepts and patterns

The references hold what each stage draws on. Read the one a decision needs when it needs it:

| Reference | Covers |
|---|---|
| [design-principles.md](references/design-principles.md) | KISS, DRY, YAGNI, separation of concerns, Law of Demeter, SOLID |
| [oop-concepts.md](references/oop-concepts.md) | Encapsulation, abstraction, polymorphism, inheritance and composition |
| [design-patterns.md](references/design-patterns.md) | Creational, structural and behavioural patterns, and when each is over-engineering |
| [layout.md](references/layout.md) | Folders, generic and business code, naming, when to split a file |

## What the session produces

The user decides. While the design is being refined, it lives in a draft in the project's temp or scratch folder (by the repository's conventions; ask where when it has none), and an explanation can stay in the conversation. Once the user agrees and wants it kept, the design goes into the project's documentation by the repository's conventions, updating an existing design document rather than adding a second. A written design opens with what a newcomer needs first, then follows the stages as sections:

1. **Requirements**: numbered, and out of scope.
2. **Entities and relationships**.
3. **Class design**: each module's state and operations, and the folder tree.
4. **Implementation**: the key methods and the traced flows.
5. **Extensibility**: change → what you touch, and what is refused for now.

---

Source: Hello Interview, [Introduction](https://www.hellointerview.com/learn/low-level-design/in-a-hurry/introduction) and [Delivery Framework](https://www.hellointerview.com/learn/low-level-design/in-a-hurry/delivery).
