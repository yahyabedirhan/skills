# Data modeling

How the data is structured, stored and related: which kind of database, the schema inside it, and how it holds up as it grows. Core entities are named in their stage of the delivery framework; the schema is sketched beside each store in the high-level design.

## Database models

| Model | How it stores data | Choose it when | Modeling impact |
|---|---|---|---|
| **Relational** (PostgreSQL, MySQL) | Tables with fixed schemas; foreign keys; joins; ACID transactions | The default. Most domains are entities with clear relationships; strong consistency (payments, inventory) needs ACID | Normalized tables, keys, constraints |
| **Document** (MongoDB, Firestore) | JSON-like documents with flexible schemas | Records vary widely in shape, or deep nesting would need many joins | Embed related data; updating nested data touches the whole document |
| **Key-value** (Redis, DynamoDB) | Values fetched by exact key | Lookups only by one key: cache, sessions, feature flags, very high write rates | Flat; data duplicated per access pattern; no joins. Usually beside SQL as a cache, not instead of it |
| **Wide-column** (Cassandra) | Rows grouped by partition key, sorted within it | Massive append-heavy writes: time series, events, telemetry | Designed per query; data duplicated across tables; time is first-class |
| **Graph** (Neo4j) | Nodes and edges | Almost never; even large social graphs run on relational stores | |

Relational scales further than its reputation, through indexes, read replicas, caching and sharding.

## Three drivers of a schema

- **Access patterns**, the most important: which queries does each endpoint run? Design keys and indexes for them.
- **Data volume**: where the data can physically live, and whether it must be split across machines or stores.
- **Consistency**: data that must change together (a charge and its order) stays in one ACID store; data that can lag (like counts) can live in separate systems ([cap-theorem.md](cap-theorem.md)).

Tie each schema choice back to one of them.

## Schema

- **Primary keys**: system-generated IDs, not business data like email, so they stay stable when rules change.
- **Relationships**: one-to-many through a foreign key on the many side; many-to-many through a join table; one-to-one is often a sign two tables should merge.
- **Foreign keys and constraints** (`NOT NULL`, `UNIQUE`, `CHECK`) keep data correct at a write cost; very large systems sometimes enforce them in the application instead.
- **Indexes** for the main queries, tied to the endpoints that need them ([database-indexing.md](database-indexing.md)).
- **Normalize first**: each fact stored once, so updates can't leave copies inconsistent. Denormalize only for analytics, point-in-time snapshots (audit logs, order lines), or read-optimized systems like search. Often better: keep the source of truth normalized and put the denormalized view in a cache.
- **Sharding** when one machine can't hold the data: shard by the main access pattern and avoid cross-shard queries ([sharding.md](sharding.md)). Beware time-range shard keys: every current write hits the newest shard.

## In a design

When a store enters the high-level design: its type, the fields each entity needs for the functional requirements, primary and foreign keys, indexes, any denormalization, and whether sharding is needed and on which key.

---

Source: Hello Interview, [Data Modeling](https://www.hellointerview.com/learn/courses/system-design/lesson/foundations/data-modeling).
