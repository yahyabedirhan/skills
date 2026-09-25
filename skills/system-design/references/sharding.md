# Sharding

Splitting data across machines once a single database can't keep up with its storage, writes or reads.

## Partitioning and sharding

- **Partitioning** splits a large table inside one database: by rows (one partition per year of orders) or by columns (frequently read columns apart from large, rarely read ones). Queries touch less data; no new machines.
- **Sharding** splits rows across machines. Each shard is a full database with its own CPU, memory, disk and connections, so storage and throughput grow with the number of shards.

Replicas for availability are a separate concern: a primary with replicas is not a single point of failure, and it isn't sharded.

## When to shard

Only after showing one database won't do ([numbers-to-know.md](numbers-to-know.md)): storage approaching tens of terabytes, sustained writes above about 10k per second, or read load that replicas and caching can't absorb. State the bottleneck, why a single database can't handle it, then propose sharding. Sharding before the math is the most common mistake.

## The shard key

What the data is split by. A good key has:

- **High cardinality**: many distinct values (user ID, not a boolean).
- **Even distribution**: no value holds most of the data (not country when most users live in one).
- **Alignment with queries**: the most common queries hit a single shard.

`user_id` suits user-centric apps; `order_id` suits an orders table. `created_at` on a growing table is a bad key: every new write lands on the newest shard.

## Distribution strategies

| Strategy | How | Strengths | Weaknesses |
|---|---|---|---|
| **Hash** | `hash(key)` chooses the shard | The default: even distribution | Plain modulo remaps nearly every key when shards are added; use consistent hashing ([consistent-hashing.md](consistent-hashing.md)) |
| **Range** | Contiguous key ranges per shard | Simple; efficient range scans; fits multi-tenant systems where each tenant queries its own range | Access clusters on some ranges (recent data), creating hot shards |
| **Directory** | A lookup table maps each key to its shard | Keys can move individually (a huge tenant to its own shard) | A lookup on every request, and the directory becomes a critical single point of failure; rarely the answer |

## Challenges

- **Hot spots**: some keys are simply busier (the celebrity problem), and hashing doesn't help. Give hot keys a dedicated shard, use a compound key (`hash(user_id + date)`), or rely on stores that split hot shards.
- **Cross-shard queries**: a query that isn't scoped by the shard key goes to every shard and merges the results. Cache the result, precompute it in the background, or denormalize the data onto the shard that reads it; accept fan-out only for rare queries (an admin dashboard). A common query that fans out suggests the shard key is wrong.
- **Consistency across shards**: a transaction touching two shards can't use one database transaction. Two-phase commit guarantees consistency but is slow and fragile. Better: keep all of a transaction's data on one shard; when that's impossible, use a saga (a sequence of steps, each with a compensating action) or accept eventual consistency.

## In practice

Most distributed databases shard automatically: Cassandra, DynamoDB and MongoDB take a partition key and route and rebalance themselves (each with its own mechanism); Vitess and Citus shard MySQL and PostgreSQL. In a design it's enough to name the store and the key ("DynamoDB with `user_id` as the partition key").

## In a design

The shard key and why it matches the main access pattern; the distribution strategy; the trade-off (which queries now fan out, and how they're served); how it grows (start with more shards than needed; consistent hashing to add more).

---

Source: Hello Interview, [Sharding](https://www.hellointerview.com/learn/courses/system-design/lesson/thinking-in-scale/sharding).
