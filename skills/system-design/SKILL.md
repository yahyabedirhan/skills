---
name: system-design
description: Design, explain or redesign a system at the level of services, data stores, APIs and scale, through the system design delivery framework. Use when designing a new backend or distributed system, explaining or documenting an existing one, redesigning or scaling one, or choosing a database, cache, queue or protocol.
---

# System design

Follow the **delivery framework** in every session, whether the design is new, explained or redesigned, so the user always finds the same things in the same places. The user decides what the session is for; the framework sets how the answer is laid out. Keep the design in the conversation unless the user asks for it to be written somewhere, and then use the stages as its sections.

To design inside one service's codebase, at the level of its modules, classes and folders, use `/low-level-design` instead.

## Flow

```text
Requirements → Core entities → API → [Data flow] → High-level design → Deep dives
```

1. **Read what the session is for** from the request and its context, and restate it in one line before starting, so a misreading costs one reply. Read `delivery-framework.md` for what each stage covers, `existing-systems.md` when the system already exists, and a concept reference when a stage reaches its concept.
   - **Invoked inside a project with no instructions:** explain that project's current design.
   - **When the purpose is unclear:** ask what the user wants to do with the design, whether the system exists, and whether they want only an explanation.
2. **Requirements:** the few core features, about three, with the rest out of scope and a reason for each; and the 3-5 non-functional requirements that most constrain this system, quantified.
3. **Core entities:** the nouns and actors the functional requirements need.
4. **API:** the contract with the system's users, usually one endpoint per functional requirement.
5. **Data flow**, only when the system is a pipeline: the steps from input to output.
6. **High-level design:** the components and each request's path through them, endpoint by endpoint, until the design satisfies the whole API. Include only what the functional requirements need.
7. **Deep dives:** meet each non-functional requirement, remove bottlenecks and single points of failure, and answer the user's probes. Add caches, queues and other complexity here and not earlier, because a design that adds them early rarely reaches a complete, working whole. For each problem, lay out the options with what each gains and costs, and recommend one.

The purpose decides how the stages are walked. The cases below are common, not a complete list; a session can mix them or move from one to another.

- **Designing a new system:** write a complete first draft through every stage.
- **Explaining an existing system:** walk it through the stages as it is, without changing it, and in place of the deep dives explain each concept the design relies on.
- **Redesigning an existing system:** explain it as it is and get the user's agreement, redesign it through the same stages changing only what the redesign needs, and show the before and after of every stage that changed.
- **Deciding one thing,** such as "Postgres or DynamoDB here?": answer it as one deep dive, naming the parts of the design it touches and the requirement behind it.

## Defaults first

Start each choice from its default, because the most common failure in system design is complexity added before it is needed: PostgreSQL as the store, REST for the API, TCP and HTTP polling for transport and real-time, no cache and then Redis cache-aside, one bigger database with replicas and then hash sharding, and synchronous work. Move off a default only for a named requirement, with numbers when the case is about scale. Typical over-design: a queue at 5k writes per second, sharding at 100 GB, a WebSocket where polling would do, a cache in front of an indexed lookup.

When the design adopts a specific technology (Kafka, DynamoDB, Elasticsearch), research it in its documentation before relying on its details: its limits, its guarantees, and how it fails.

## Working with the user

Load `/show-me` and present every stage visually, with prose only for the reasons behind choices. Then loop: take the user's feedback, revise, and present again until the user is satisfied.

- Keep one current version of the design and revise it.
- When feedback changes one part, carry the change through every part it affects.
- Open each revision with what changed and why, as a before/after of the parts that moved, including parts that changed only because of a change elsewhere.
- Leave a point the user settled as it is unless they reopen it.

Ask only what the code, the existing design documents and the user's earlier answers can't settle, one question at a time; decide the rest and say what you decided.

## References

- [delivery-framework.md](delivery-framework.md): what each stage covers, and how to show it.
- [existing-systems.md](existing-systems.md): building an explanation of an existing system from evidence, and running a redesign.

### Concepts and technologies

Each covers one concept: what it is, why it matters, its trade-offs, and when to choose which kind of technology.

| Reference | Covers |
|---|---|
| [networking-essentials.md](references/networking-essentials.md) | TCP and UDP, HTTP, REST, gRPC, SSE, WebSockets, WebRTC, load balancing, regions, failure handling |
| [api-design.md](references/api-design.md) | REST, GraphQL, RPC, resources, pagination, idempotency, versioning, auth |
| [data-modeling.md](references/data-modeling.md) | Database models, schema design, normalization |
| [database-indexing.md](references/database-indexing.md) | B-tree, LSM, hash, geospatial and inverted indexes, composite indexes |
| [caching.md](references/caching.md) | Where to cache, cache patterns, eviction, what goes wrong |
| [sharding.md](references/sharding.md) | Shard keys, distribution strategies, hot spots, cross-shard work |
| [consistent-hashing.md](references/consistent-hashing.md) | The hash ring, virtual nodes, hot keys |
| [cap-theorem.md](references/cap-theorem.md) | Consistency against availability, consistency levels |
| [numbers-to-know.md](references/numbers-to-know.md) | Hardware and component capacities, over-design they prevent |
| [common-patterns.md](references/common-patterns.md) | Real-time updates, long-running tasks, contention, scaling reads and writes, large blobs, multi-step processes, proximity |

---

Source: Hello Interview, [Delivery Framework](https://www.hellointerview.com/learn/courses/system-design/lesson/orientation/delivery).
