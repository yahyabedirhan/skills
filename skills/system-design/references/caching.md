# Caching

Keeping frequently read data in memory so reads skip the store behind it. A Redis read takes about a millisecond where a database query may take tens, and every cache hit is load the database doesn't carry. The price is staleness, invalidation, and new ways to fail.

## When a cache is justified

A named bottleneck, with rough numbers:

- **Read-heavy load**: many reads of the same data.
- **Expensive queries**: a feed built from joins that takes hundreds of milliseconds.
- **Database CPU** spent serving the same queries repeatedly.
- **A latency target** the database can't meet.

An indexed row lookup already takes a few milliseconds; caching it adds infrastructure for nothing ([numbers-to-know.md](numbers-to-know.md)).

## Where to cache

- **External cache** (Redis, Memcached): a separate service every app server shares, with eviction and TTLs. The default.
- **CDN**: edge servers near users cache content; the case to reach for first is static media served worldwide.
- **Client-side**: the browser or app keeps data (HTTP cache, local storage, offline sync). Little control over staleness.
- **In-process**: small, hot, rarely changing values (config, feature flags, hot keys) in the server's own memory. The fastest, but each server has its own copy and invalidations don't reach the others; an extra layer on top of an external cache.

## Read and write patterns

| Pattern | How | Use when |
|---|---|---|
| **Cache-aside** | Read the cache; on a miss, read the database, store the result, return it | The default; caches only what's read, a miss costs extra latency |
| **Write-through** | Write to the cache, which writes the database before acknowledging | Reads must be fresh and slower writes are acceptable; needs a library that supports it, and a failed half still leaves the two inconsistent |
| **Write-behind** | Write to the cache, which flushes to the database later in batches | Very high write throughput where losing recent writes is acceptable (metrics) |
| **Read-through** | The cache fetches from the database on a miss itself | Mostly CDNs; rarely worth it for an application cache |

## Eviction

- **LRU** evicts the least recently used entry; the default.
- **LFU** evicts the least frequently used; for keys that stay popular over time.
- **FIFO** evicts the oldest inserted, ignoring use; rarely right.
- **TTL** expires entries after a set time; combined with LRU or LFU wherever data must refresh.

## What goes wrong

- **Stampede (thundering herd)**: a popular entry expires and every request hits the database at once. Coalesce requests so only one rebuilds while the others wait; or refresh hot keys before they expire.
- **Stale data**: the database changed and the cache didn't. Delete the entry on write, use short TTLs, or accept eventual consistency where the requirements allow it.
- **Hot keys**: one entry (a celebrity profile) overloads one cache node. Replicate it across nodes, keep an in-process copy, or rate-limit.
- **Cache failure**: every read falls to the database. Fall back with a circuit breaker so the database isn't flattened.

## In a design

Name the bottleneck with numbers; what to cache (read often, changes rarely, expensive to produce) and the key shape (`user:123:profile`); the pattern; eviction and TTL; and the one or two failure modes that matter for this system.

---

Source: Hello Interview, [Caching](https://www.hellointerview.com/learn/courses/system-design/lesson/thinking-in-scale/caching).
