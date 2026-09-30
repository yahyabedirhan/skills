---
name: system-design
description: Design, explain or redesign a system at the level of services, data stores, APIs and scale, through the system design delivery framework. Use when designing a new backend or distributed system, explaining or documenting an existing one, redesigning or scaling one, or choosing a database, cache, queue or protocol.
---

# System design

Follow the **delivery framework** in every session, whether the design is new, explained or redesigned. It is the standard order for producing and presenting a system design, and using it every time means the user always finds the same things in the same places. The user decides what the session is for; the framework sets how the answer is laid out.

To design inside one service's codebase, at the level of its modules, classes and folders, use `/low-level-design` instead.

## What the session is for

The user usually says what they want when they invoke the skill. Read the purpose from the request and its context, and restate it in one line before starting, so a misreading costs one reply.

- When the skill is invoked inside a project with no instructions, explain that project's current design through the framework.
- When the purpose isn't clear, ask the user what they want to do with the design, whether it's an existing system or a new one, and whether they want only an explanation.

The purposes below are common cases, not a complete list. A session can mix them, move from one to another (an explanation turning into a redesign), or be something else; adapt the framework to what the user asked for.

### Designing a new system

Starting from the user's requirements, write a complete first draft through every stage. In the deep dives, present each trade-off as options, each with what it gains and what it costs, and recommend one, so the user can pick according to their preferences.

### Explaining an existing system

Walk the system through the stages as it is, without changing it:

- Build each stage from the evidence at hand. If there is an existing design document, start there and check it against the code. In the code, read the routes and handlers, jobs and consumers, schemas and migrations, connection and deploy config, and calls to other services. The user's description is evidence too. Cite the file, section or message behind each claim.
- Mark requirements read from the code **inferred**. Mark what the evidence can't show, such as traffic, data sizes, incidents or why a choice was made, **unknown**, and ask about it rather than filling it in, so a guess never passes for a fact.
- In place of the deep dives, add a section on each concept the design relies on (its cache, its sharding, its consistency choice): what it is, why it matters for this design, and the trade-off the design made. Record weaknesses as observations, not proposals, because the session explains the system without changing it.
- Answer follow-up questions by walking a request or a failure through the design.

### Redesigning an existing system

1. **Explain it as it is now**, as above, and get the user's agreement that it's right.
2. **Redesign it through the same stages**, changing only what the redesign needs. Keep each existing component unless the problem lies in it.
3. **Show the before and after** of every stage that changed.

In the deep dives, present the new design's trade-offs as options, as for a new system.

### Deciding one thing

Answer a single question like "Postgres or DynamoDB here?" as one deep dive: name the parts of the design it touches and the requirement behind it, lay out the options with their trade-offs, and recommend one.

## The delivery framework

```text
Requirements → Core entities → API → [Data flow] → High-level design → Deep dives
```

Work through the stages in this order, because each builds on the one before it: the API serves the requirements, the high-level design serves the API, and the deep dives make the high-level design meet the non-functional requirements. Add caches, queues and other complexity last, in the deep dives: a design that adds them early rarely reaches a complete, working whole.

### 1. Requirements

**Functional requirements** are the core features, as "users should be able to..." statements. A real system has hundreds of features. Cover the few that matter most, about three, and put the rest on an out-of-scope list, each with its reason. Keep the in-scope list short, because every item on it is something the design must then satisfy.

**Non-functional requirements** are the qualities the system must have, as "the system should be..." statements, each stated for this system and quantified where possible: "search results under 500 ms", not "low latency". From this checklist, pick the 3-5 that most constrain this system's design:

- **Consistency or availability** under a network partition, decided per feature ([cap-theorem.md](references/cap-theorem.md)). Settle this first, because it decides which stores fit.
- **Scalability**: bursty traffic, peak events, and the read/write ratio (which side must scale).
- **Latency**, especially for requests that need real computation (search, feeds).
- **Durability**: how bad is losing data (a social post versus a bank transfer)?
- **Security**: data protection, access control.
- **Fault tolerance**: redundancy, failover, recovery.
- **Compliance**: legal and regulatory constraints.
- **Environment**: device, memory or bandwidth limits (mobile, poor networks).

**Estimates**: work out users, QPS or storage only where the number changes a decision, such as whether a top-K counter fits in one in-memory heap or must be sharded. Do the arithmetic during the design, at the point where a choice depends on it ([numbers-to-know.md](references/numbers-to-know.md)).

### 2. Core entities

List the nouns and actors the functional requirements need: the things the API exchanges and the stores persist. Keep it a short first draft with clear names (for Twitter: User, Tweet, Follow). Leave fields for the high-level design, where a request shows which ones matter.

Useful questions: who are the actors, and do they overlap? Which resources does each functional requirement need?

### 3. API

Define the contract between the system and its users: usually one endpoint per functional requirement, with the core entities as resources. Use REST by default, GraphQL for diverse clients with different data needs, and RPC for internal, performance-critical calls. Design real-time features (WebSockets, SSE) after the core API. Take the current user from the auth token, never from the request body ([api-design.md](references/api-design.md)).

### 4. Data flow (optional)

For a data-processing system, list the steps from input to output as a numbered list (a web crawler: fetch seed URLs, parse HTML, extract URLs, store data, repeat). Skip this stage when the system isn't a pipeline.

### 5. High-level design

Lay out the components (clients, load balancers, services, databases, caches, queues) and how they interact, going endpoint by endpoint until the design satisfies the whole API.

- Say how data flows through the system for each request, from the API call to the response, and what state changes where.
- When a request reaches a store, write the fields that matter beside it: the ones the design depends on, not the obvious ones ([data-modeling.md](references/data-modeling.md), [database-indexing.md](references/database-indexing.md)).
- Include only what the functional requirements need. When a part looks like it needs a cache or a queue, note it for the deep dives and move on.

### 6. Deep dives

Strengthen the high-level design: meet each non-functional requirement, handle edge cases, remove bottlenecks and single points of failure, and answer the user's probes. For each, name the problem (with numbers when it's about scale), the options, and their trade-offs. Twitter's scale leads to horizontal scaling, caching and sharding; its fast feeds lead to fanout-on-read against fanout-on-write. Choose the deep dives yourself, and let the user redirect them toward what they care about.

### Defaults first, prove the need

Start each choice from its default below, because the most common failure in system design is complexity added before it is needed. Move off a default only for a named requirement, with numbers when the case is about scale:

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

Run the session as a loop: present the design, take the user's feedback, revise, and present again, until the user is satisfied.

- **Keep one current version** of the design and revise it; don't start over.
- **When feedback changes one part, carry the change through every part it affects.**
- **Open each revision with what changed and why**, as a before/after of the parts that moved, including parts that changed only because of a change elsewhere.
- **Leave a point the user settled as it is** unless they reopen it.

Ask only what the code, the existing design documents and the user's earlier answers can't settle, one question at a time; decide the rest and say what you decided.

## Showing it

Load `/show-me` and present every stage visually, with prose only for the reasons behind choices:

- requirements, entities and endpoints as short lists or tables;
- the high-level design as a component flow (`client -> LB -> API -> Postgres`);
- a request or a failure as a numbered walk through the components, with the state it changes;
- stores as a table: what each holds, who writes it, its key or shard key;
- a redesign or a revision as a before/after `diff` of the flow or the list that changed;
- deep-dive options side by side, each with its gain and cost.

## Concepts and technologies

Each reference covers one concept: what it is, why it matters, its trade-offs, and when to choose which kind of technology. Read a reference when a stage reaches its concept, not before:

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

When the design adopts a specific technology (Kafka, DynamoDB, Elasticsearch), research it in its documentation before relying on its details: its limits, its guarantees, and how it fails.

## What the session produces

Keep the design in the conversation unless the user asks for it to be written somewhere; where it goes is the user's decision. When you write it, use the stages as sections:

1. **Requirements**: functional, non-functional, out of scope.
2. **Core entities**.
3. **API**.
4. **Data flow**, when the system is a pipeline.
5. **High-level design**: the component flow, each request's path and the state it changes, the fields beside each store.
6. **Deep dives**: each problem, its options and trade-offs, and the choice.

---

Source: Hello Interview, [Delivery Framework](https://www.hellointerview.com/learn/courses/system-design/lesson/orientation/delivery).
