---
name: system-design
description: Design, explain or redesign a system at the level of services, data stores, APIs and scale, through the system design delivery framework. Use when designing a new backend or distributed system, explaining or documenting an existing one, redesigning or scaling one, or choosing a database, cache, queue or protocol.
---

# System design

This skill is the **delivery framework**: the standard order for producing and presenting a system design. Every session follows it, whether the design is new, explained, or redesigned, so the user always finds the same things in the same places. The user decides what the session is for; the framework decides how the answer is laid out. The references hold the concepts each stage draws on.

Inside one service's codebase (modules, classes, folders), the design is a low-level design: use the **low-level-design** skill.

## What the session is for

The user usually says what they want when they invoke the skill. Read the purpose from the request and its context, and restate it in one line before starting, so a misreading costs one reply.

- Invoked with no instructions inside a project: write down that project's current design through the framework.
- When the purpose isn't clear, ask the user what they want to do with the design, whether it's an existing system or a new one, and whether they want only an explanation.

The purposes below are common shapes, not a menu. A session can mix them, move from one to another (an explanation turning into a redesign), or be something else; fit the framework to what the user asked for.

### Designing a new system

Design it end to end: a complete first draft through every stage, from the user's requirements. Deep dives present the design's trade-offs as options, each with what it gains and costs and a recommendation, so the user picks according to their preferences. When feedback changes one part, carry the change through every part it affects, and show what moved.

### Explaining an existing system

Walk the system through the stages as it is, without changing it:

- Build each stage from the evidence at hand: an existing design document (start there and check it against the code), the code itself (routes and handlers, jobs and consumers, schemas and migrations, connection and deploy config, calls to other services), or the user's description. Cite the file, section or message behind each claim.
- Requirements read from the code are marked **inferred**. What the evidence can't show (traffic, data sizes, incidents, why a choice was made) is marked **unknown** and asked about, never filled in.
- The deep dives become a bonus section: for each concept the design relies on (its cache, its sharding, its consistency choice), what it is, why it matters for this design, and the trade-off the design made. Weaknesses are observations, not proposals.
- Answer follow-up questions by walking a request or a failure through the design.

### Redesigning an existing system

1. **Explain it as it is now**, as above, and get the user's agreement that it's right.
2. **Redesign it through the same stages**, changing only what the redesign needs. Existing components stand unless the problem is about them.
3. **Show the before and after** of every stage that changed.

Deep dives present the new design's trade-offs as options, as for a new system.

### Deciding one thing

A question like "Postgres or DynamoDB here?" is one deep dive: the parts of the design it touches, the requirement behind it, the options with their trade-offs, and a recommendation.

## The delivery framework

```text
Requirements → Core entities → API → [Data flow] → High-level design → Deep dives
```

Each stage rests on the one before it: the API serves the requirements, the high-level design serves the API, the deep dives harden the high-level design against the non-functional requirements. Complexity arrives last, on purpose; a design that layers on caches and queues early rarely reaches a complete, working whole.

### 1. Requirements

**Functional requirements** are the core features, as "users should be able to..." statements. A real system has hundreds of features; the design covers the few that matter most (about three), and the rest go to an out-of-scope list, each with its reason. A long list hurts: every item is something the design must then satisfy.

**Non-functional requirements** are the qualities the system must have, as "the system should be..." statements, each placed in the system's context and quantified where possible: "search results under 500 ms", not "low latency". Pick the 3-5 that shape this system from this checklist:

- **Consistency or availability** under a network partition, decided per feature ([cap-theorem.md](references/cap-theorem.md)). Settle this first; it shapes the stores.
- **Scalability**: bursty traffic, peak events, and the read/write ratio (which side must scale).
- **Latency**, especially for requests that need real computation (search, feeds).
- **Durability**: how bad is losing data (a social post versus a bank transfer)?
- **Security**: data protection, access control.
- **Fault tolerance**: redundancy, failover, recovery.
- **Compliance**: legal and regulatory constraints.
- **Environment**: device, memory or bandwidth limits (mobile, poor networks).

**Estimates** (users, QPS, storage) only where the number changes a decision, such as whether a top-K counter fits in one in-memory heap or must be sharded. Do the arithmetic during the design, when a choice depends on it ([numbers-to-know.md](references/numbers-to-know.md)).

### 2. Core entities

The nouns and actors the functional requirements need: the things the API exchanges and the stores persist. A short first-draft list with good names (for Twitter: User, Tweet, Follow). Fields come later, in the high-level design, when a request shows which ones matter.

Useful questions: who are the actors, and do they overlap? Which resources does each functional requirement need?

### 3. API

The contract between the system and its users, usually one endpoint per functional requirement, with the core entities as resources. REST by default; GraphQL for diverse clients with different data needs; RPC for internal, performance-critical calls. Real-time features (WebSockets, SSE) come after the core API. The current user comes from the auth token, never from the request body ([api-design.md](references/api-design.md)).

### 4. Data flow (optional)

For data-processing systems, the sequence of steps from input to output as a numbered list (a web crawler: fetch seed URLs, parse HTML, extract URLs, store data, repeat). Skip it when the system isn't a pipeline.

### 5. High-level design

The components (clients, load balancers, services, databases, caches, queues) and how they interact, built to satisfy the API, endpoint by endpoint.

- Say how data flows through the system for each request, from the API call to the response, and what state changes where.
- When a request reaches a store, write the fields that matter beside it: the ones the design depends on, not the obvious ones ([data-modeling.md](references/data-modeling.md), [database-indexing.md](references/database-indexing.md)).
- Keep it simple enough to meet the functional requirements. When a spot calls for a cache or a queue, note it for the deep dives and move on.

### 6. Deep dives

Harden the high-level design: meet each non-functional requirement, handle edge cases, remove bottlenecks and single points of failure, and answer the user's probes. For each, name the problem (with numbers when it's about scale), the options, and their trade-offs. Twitter's scale leads to horizontal scaling, caching and sharding; its fast feeds lead to fanout-on-read against fanout-on-write. Lead the deep dives, and leave room for the user to steer toward what they care about.

### Defaults first, prove the need

The recurring failure in system design is complexity added before it is needed. Start from the default and move off it for a named requirement, with numbers when the case is about scale:

| Choice | Default | Move off it when |
|---|---|---|
| Store | PostgreSQL | [data-modeling.md](references/data-modeling.md) |
| API | REST | [api-design.md](references/api-design.md) |
| Transport, real-time | TCP; HTTP polling | [networking-essentials.md](references/networking-essentials.md) |
| Cache | None; then Redis, cache-aside | [caching.md](references/caching.md) |
| Scale | One bigger database plus replicas; then hash sharding | [sharding.md](references/sharding.md), [numbers-to-know.md](references/numbers-to-know.md) |
| Async work | Synchronous | [common-patterns.md](references/common-patterns.md) |

Typical over-design: a queue at 5k writes per second, sharding at 100 GB, a WebSocket where polling would do, a cache in front of an indexed lookup.

## Working with the user

A session is a loop: present, the user gives feedback, revise, present again, until the user is satisfied.

- **Keep one current version** of the design and revise it; don't start over.
- **Open each revision with what changed and why**, as a before/after of the parts that moved, including parts changed only because a change elsewhere reached them.
- **A point the user settled stays settled** unless they reopen it.

Ask only what the code, the existing design documents and the user's earlier answers can't settle, one question at a time; decide the rest and say what you decided.

## Showing it

Load the **show-me** skill and present every stage visually, with prose only for the reasons behind choices:

- requirements, entities and endpoints as short lists or tables;
- the high-level design as a component flow (`client -> LB -> API -> Postgres`);
- a request or a failure as a numbered walk through the components, with the state it changes;
- stores as a table: what each holds, who writes it, its key or shard key;
- a redesign or a revision as a before/after `diff` of the flow or the list that changed;
- deep-dive options side by side, each with its gain and cost.

## Concepts and technologies

The references hold the concepts: each concept, why it matters, its trade-offs, and when to choose which kind of technology. Read the one a stage needs when it needs it:

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

When the design adopts a specific technology (Kafka, DynamoDB, Elasticsearch), research how it works, from its documentation, before relying on its details: limits, guarantees, and how it fails.

## What the session produces

The user decides. The design lives in the conversation unless the user asks for it to be written somewhere. A written design follows the stages as sections:

1. **Requirements**: functional, non-functional, out of scope.
2. **Core entities**.
3. **API**.
4. **Data flow**, when the system is a pipeline.
5. **High-level design**: the component flow, each request's path and the state it changes, the fields beside each store.
6. **Deep dives**: each problem, its options and trade-offs, and the choice.

---

Source: Hello Interview, [Delivery Framework](https://www.hellointerview.com/learn/courses/system-design/lesson/orientation/delivery).
