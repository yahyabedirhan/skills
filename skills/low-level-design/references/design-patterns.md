# Design patterns

Names for structures good design produces on its own. A pattern follows from a decision; it doesn't drive one. Most good designs use none or one or two, and reaching for three usually means forcing them.

## Creational: how objects get made

**Factory.** One place decides which concrete class to create from a value the caller has: `NotificationFactory.create("email")` instead of `new EmailNotification()` scattered around, so adding SMS changes one place. Some engineers see it as over-engineering; use it when that choice is made in several places, not when there is one implementation or the caller already knows what it wants.

**Builder.** Assemble an object step by step and validate once at the end, instead of a constructor with ten parameters half of them null. It fits request and configuration objects with many optional parts. Most domain objects have a few required fields and a normal constructor; where the language has object literals or named arguments, those usually beat a builder.

**Singleton.** Exactly one instance for the whole process. Rarely the answer: it hides a dependency and makes tests share state. Pass the shared object through constructors, or export one instance from a module.

## Structural: how objects connect

**Decorator.** Wrap an object in another with the same interface to add behaviour, stacking as needed (compression on encryption on a file source) instead of a subclass per combination. Use it when optional behaviours combine at runtime; a fixed, design-time variation is a subclass or a function.

**Facade.** A coordinator that hides several parts behind a simple entry point. The orchestrator of most designs already is one (a `Game` coordinating board, players and state); name it when that helps, especially when wrapping a messy existing subsystem.

**Adapter.** Wrap a dependency whose interface doesn't match yours, so its vocabulary stops at one file. Useful at a third-party boundary; pointless when the interfaces already match.

## Behavioural: how objects interact

**Strategy.** Replace an `if/else` on type with interchangeable implementations held by composition (a cart holding a `PaymentStrategy`). The most common pattern, and just polymorphism with a name. Factory decides which object to create; strategy decides which behaviour an existing object uses. If the choice is made once at startup and never changes, a plain function will do.

**Observer.** Subscribers register with a subject and are notified when it changes, without the subject knowing what they do (a stock price feeding displays and alerts; an order feeding inventory, notifications and analytics). Use it when one event has several independent consequences; with one listener, call it directly.

**State machine.** An object whose valid operations depend on its current state, with each state's behaviour and transitions made explicit (a vending machine moving from no coin, to coin inserted, to dispensing). Signals: a lifecycle in the requirements, or the same `if (state == …)` guard in many methods. When one is present it is usually the centre of the design, best shown as a state diagram; two states and one transition are just a boolean.

**Command.** An operation as a value (its validated input and a function that applies it), so operations can be listed, queued, logged or undone uniformly. Worth it once there are several operations handled the same way.

**Registry.** A list of definitions the core iterates over, so adding a variant is one new file plus one entry.

## Cheat sheet

| Pattern | Use when |
|---|---|
| Factory | Callers shouldn't care which concrete class is created |
| Builder | Many optional fields or messy construction |
| Singleton | One global instance is truly required (rare) |
| Decorator | Optional behaviours layer at runtime |
| Facade | Internal complexity hides behind one entry point |
| Adapter | A dependency's interface doesn't fit yours |
| Strategy | Interchangeable behaviours replace an if/else |
| Observer | Several components react to one event |
| State machine | Behaviour depends on state and transitions get messy |
| Command | Operations are handled uniformly |
| Registry | New variants plug in with one entry |

---

Source: Hello Interview, [Design Patterns](https://www.hellointerview.com/learn/low-level-design/in-a-hurry/patterns). Adapter, command and registry come from practice.
