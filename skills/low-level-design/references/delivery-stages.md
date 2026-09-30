# Delivery stages

How to work each stage of the delivery framework, and how to show what it produces. Move to the next stage once the current one has everything its product lists.

## Requirements

Turn the request or spec into something to design against, working down four themes:

- **Capabilities**: the operations the system must support.
- **Rules and completion**: what defines success and failure, and when the system stops or changes state.
- **Error handling**: how it responds to invalid input and illegal actions.
- **Scope**: what is in (core logic, business rules), and what is explicitly out (UI, storage, concurrency, whatever the user excludes). The exclusions keep the design from growing features nobody asked for.

Show them as a short numbered list. A mapping from requirement to module fits as a small table once the modules exist.

## Entities and relationships

Take the nouns from the requirements. A noun that holds changing state or enforces rules is an entity; one that is only information attached to another is a field on it. This keeps the design from splitting into many tiny objects.

Then settle how they relate: which entity is the orchestrator, which own durable state, which has, uses or contains which, and where each rule lives.

Show the entities as a short list and the relationships as arrows (`Game -> Board`). Boxes and arrows are enough; skip formal UML.

## Class design

Turn each entity into a class or module, top-down from the orchestrator, and derive its state and behaviour from the requirements rather than from intuition:

- **State**: what it must remember to enforce the requirements it owns.
- **Behaviour**: what callers must be able to ask or tell it, each operation with what it returns and rejects, in a small API where each method matches a real action or question.

Keep each rule with the module that owns its state (**tell, don't ask**): lifecycle rules ("can this run now?") belong to the orchestrator, data rules ("is this cell taken?") to the module holding the data, so when something breaks you know which module to open. Place the modules in folders following [layout.md](layout.md).

Show the folder tree with one comment per line saying what each file or folder owns.

## Implementation

Sketch the methods that carry the logic, not every method: the happy path first (the steps, the calls into other modules, the state changed), then the edge cases (invalid input, illegal operations, calls in the wrong state). Write pseudocode unless the project needs real code.

Then verify: trace one concrete scenario step by step, with the state after each step, plus one rejection, and fix what the trace reveals, such as a state never set or a rule checked too late.

Show a traced flow as a call tree, with the owning file beside each call.

## Extensibility

List the changes likely to come next, and for each one name the part of the design that absorbs it and what changes. A design that routes every state change through one place takes a feature like undo without restructuring. A change that lands in one new file plus a registration is already absorbed; one that repeats the same edit across several files needs a seam. Refuse the changes the current requirements don't need, rather than designing for them.

Show the changes as a small "change → what you touch" table.

## Revisions

Show a redesign or a revision as a before/after `diff` of the tree or list that changed.

---

Source: Hello Interview, [Delivery Framework](https://www.hellointerview.com/learn/low-level-design/in-a-hurry/delivery).
