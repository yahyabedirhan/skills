# Design principles

Tools for deciding whether something should be its own class, whether to use inheritance, whether an abstraction is worth it, and for explaining the decision. Apply them; name one only when it explains a trade-off.

## General principles

**KISS: keep it simple.** The simplest design that works is usually right: a conditional before a strategy pattern, one class before three. It is the principle most often broken, by designs that reach for factories and decorators to look thorough. Add complexity when simplicity stops working: a class grown to many responsibilities, or a new variant that means editing five places.

**DRY: don't repeat yourself.** Logic that is conceptually the same lives in one place, so a rule change or a bug fix is one edit. Code that only looks similar but serves different purposes may stay duplicated; forcing it to share couples two things that change for different reasons. DRY and KISS pull against each other: keep the logic where it is first, and extract it once it repeats (by the third copy, what varies is visible).

**YAGNI: you aren't gonna need it.** Build what the requirements need now. Design with extension in mind, but don't build ahead: guessed-at futures are usually guessed wrong and leave dead code.

**Separation of concerns.** Presentation, business logic and storage live apart and don't know each other's internals. Then switching the UI touches only the UI, changing a rule touches only the rule, and each part can be tested on its own.

**Law of Demeter.** A method talks to its immediate collaborators, not through them: `order.getCustomer().getAddress().getZipCode()` couples the caller to three structures; `order.getCustomerZipCode()` hides them. Fluent chains that return the same type are fine.

## SOLID

Born in class-heavy languages; elsewhere, composition and plain functions often do the job with less ceremony. Apply them where the problem calls for them.

- **Single responsibility.** One reason to change. A class that generates a report, formats it as PDF and saves it to disk changes for three reasons; split it into content, printer and storage.
- **Open/closed.** Add behaviour by adding code, not by editing what works: a payment processor with an `if` per method type becomes a `PaymentMethod` interface with one class per method.
- **Liskov substitution.** A subtype works anywhere its parent does. Red flags: a subclass that throws on an inherited method (a penguin that can't `fly()`), or callers checking `instanceof`. Fix by splitting the capability into its own interface.
- **Interface segregation.** Small, focused interfaces over one broad one. When implementations leave methods empty or throw "not supported", the interface is several interfaces.
- **Dependency inversion.** Business logic defines the interface it needs, and the detail implements it: a notification service takes a `MessageSender` rather than building an `EmailSender`, so it can be tested with a fake and switched to SMS. Dependency injection (passing it through the constructor) is the technique that achieves it.

## Cheat sheet

| Principle | What it buys |
|---|---|
| KISS | Complexity only when needed |
| DRY | One place to change |
| YAGNI | No code for hypothetical futures |
| Separation of concerns | Independent changes and tests |
| Law of Demeter | Hidden internal structure, less coupling |
| SRP | Focused classes |
| OCP | New behaviour without editing old code |
| LSP | Hierarchies that don't break at runtime |
| ISP | Clean, focused interfaces |
| DIP | Business logic free of implementation details |

---

Source: Hello Interview, [Design Principles](https://www.hellointerview.com/learn/low-level-design/in-a-hurry/design-principles).
