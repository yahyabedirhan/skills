# Delivery framework

What each stage of the delivery framework covers, and how to show it. The stages come in this order because each builds on the one before it: the API serves the requirements, the high-level design serves the API, and the deep dives make the high-level design meet the non-functional requirements.

## Requirements

**Functional requirements** are the core features, as "users should be able to..." statements. A real system has hundreds of features; keep the in-scope list to about three, because every item on it is something the design must then satisfy.

**Non-functional requirements** are the qualities the system must have, as "the system should be..." statements, each stated for this system and quantified where possible: "search results under 500 ms", not "low latency". Pick the 3-5 that most constrain this design from this checklist:

- **Consistency or availability** under a network partition, decided per feature ([cap-theorem.md](references/cap-theorem.md)). Settle this first, because it decides which stores fit.
- **Scalability**: bursty traffic, peak events, and the read/write ratio, which says which side must scale.
- **Latency**, especially for requests that need real computation, such as search and feeds.
- **Durability**: how bad losing data is, a social post against a bank transfer.
- **Security**: data protection and access control.
- **Fault tolerance**: redundancy, failover and recovery.
- **Compliance**: legal and regulatory constraints.
- **Environment**: device, memory or bandwidth limits, such as mobile clients on poor networks.

**Estimates:** work out users, QPS or storage only where the number changes a decision, such as whether a top-K counter fits in one in-memory heap or must be sharded. Do the arithmetic at the point in the design where a choice depends on it ([numbers-to-know.md](references/numbers-to-know.md)).

Show requirements as short lists: functional, non-functional, and out of scope with reasons.

## Core entities

The things the API exchanges and the stores persist, as a short first draft with clear names (for Twitter: User, Tweet, Follow). Ask who the actors are and whether they overlap, and which resources each functional requirement needs. Leave fields for the high-level design, where a request shows which ones matter.

## API

Use the core entities as resources. Use REST by default, GraphQL for diverse clients with different data needs, and RPC for internal, performance-critical calls. Design real-time features, such as WebSockets or SSE, after the core API. Take the current user from the auth token, never from the request body ([api-design.md](references/api-design.md)).

Show entities and endpoints as short lists or tables.

## Data flow

For a data-processing system, a numbered list of steps from input to output (a web crawler: fetch seed URLs, parse HTML, extract URLs, store data, repeat).

## High-level design

Lay out the components (clients, load balancers, services, databases, caches, queues) and how they interact.

- Say how data flows through the system for each request, from the API call to the response, and what state changes where.
- When a request reaches a store, write the fields that matter beside it: the ones the design depends on, not the obvious ones ([data-modeling.md](references/data-modeling.md), [database-indexing.md](references/database-indexing.md)).
- When a part looks like it needs a cache or a queue, note it for the deep dives and move on.

Show the design as a component flow (`client -> LB -> API -> Postgres`), a request or a failure as a numbered walk through the components with the state it changes, and stores as a table of what each holds, who writes it, and its key or shard key.

## Deep dives

Beyond the non-functional requirements, handle edge cases. Name each problem, with numbers when it's about scale, then its options and their trade-offs. Twitter's scale leads to horizontal scaling, caching and sharding; its fast feeds lead to fanout-on-read against fanout-on-write. Choose the deep dives yourself, and let the user redirect them toward what they care about.

Each default in `SKILL.md` has a reference that says when to move off it: the store in [data-modeling.md](references/data-modeling.md), the API in [api-design.md](references/api-design.md), transport and real-time in [networking-essentials.md](references/networking-essentials.md), the cache in [caching.md](references/caching.md), scale in [sharding.md](references/sharding.md) and [numbers-to-know.md](references/numbers-to-know.md), and async work in [common-patterns.md](references/common-patterns.md).

Show the options side by side, each with its gain and cost, and a redesign or revision as a before/after `diff` of the flow or the list that changed.

---

Source: Hello Interview, [Delivery Framework](https://www.hellointerview.com/learn/courses/system-design/lesson/orientation/delivery).
