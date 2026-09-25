# OOP concepts

The mechanisms a language gives you to carry out the design principles.

## Encapsulation

An object keeps its data private and controls how it changes, through methods that enforce its rules. An `Account` that owns `balance` and exposes only `deposit()` and `withdraw()` can refuse a negative balance and log every change; a public `balance` guarantees nothing. Check two things: fields are not exposed directly, and internal collections are returned as copies or read-only views, never as the live reference.

## Abstraction

Expose what something does and hide how. An `OrderService` that depends on a `PaymentMethod` interface doesn't care whether payment goes through one provider's API or another. Introduce an abstraction where logic is complex or varies: several ways to do one thing, messy details, rules that tangle. Pitch it at the caller's needs: too abstract (`doWork()`) says nothing; too specific hides nothing.

## Polymorphism

Instead of branching on type (`if (type == "car") … else if (type == "truck")`), call one method and let each type answer for itself (`vehicle.getRequiredSpotSize()`). Adding a type then means adding a class, not editing every branch. The cost is that flows get harder to trace as implementations multiply, and teams differ in how much they tolerate it; a type check or `switch` repeated across the code is the signal it's worth it.

## Inheritance, and composition instead

Inheritance shares implementation by making one class a more specific version of another. It couples tightly: a change to the parent can break every child (the fragile base class).

- **It fits** when the shared implementation is stable and every subclass truly is the parent: savings and checking accounts sharing balance, deposit and withdraw logic.
- **It breaks** when subclasses override methods to do something different: an `ElectricCar` overriding `Car.startEngine()` has no engine, and a hybrid fits under neither.
- **Compose instead** when behaviour varies: give `Car` a `Drivetrain` (gas engine, electric motor, both for a hybrid) and let new kinds be new implementations.

Default to interfaces and composition; most designs need no inheritance at all.

---

Source: Hello Interview, [OOP Concepts](https://www.hellointerview.com/learn/low-level-design/in-a-hurry/oop-concepts).
