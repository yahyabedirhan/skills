# Numbers to know

What modern hardware can do, so a design scales where the numbers say and nowhere else. Designs built on outdated limits come out over-engineered: sharding, caching and queueing that a single modern machine didn't need. The figures are 2026 values for well-tuned cloud systems; hardware keeps improving, so treat them as orders of magnitude.

## Hardware

- **Memory**: 512 GiB on a general-purpose server; up to 4 TB on memory-optimized instances, and beyond on specialized ones.
- **Storage**: tens of terabytes of local SSD per machine; object storage (S3) is effectively unlimited.
- **Network**: 25 Gbps standard, 50-100 Gbps on high-performance instances. Latency under 1 ms within an availability zone, 1-2 ms across zones in a region, 50-150 ms across regions.

## Per component

| Component | Capacity | Consider scaling when |
|---|---|---|
| **Cache** (Redis) | ~1 ms reads; 100k+ operations/s per instance; up to ~1 TB memory | Data nears 1 TB, sustained 100k+ ops/s, reads must be under 0.5 ms, hit rate under ~80% |
| **Database** (PostgreSQL, MySQL) | 1-5 ms cached reads, 5-30 ms from disk; 5-15 ms commits; up to ~50k read and 10-20k write TPS; 64 TiB per instance (Aurora 256 TiB); 5-20k connections | Tens of terabytes; sustained writes above ~10k TPS; uncached reads needed under 5 ms; multi-region needs; backups taking hours |
| **App server** | 100k+ concurrent connections; 8-64 cores; 64-512 GB RAM; containers start in 30-60 s | CPU or memory above 70-80%; latency over target; bandwidth near the limit |
| **Message queue** (Kafka) | Up to ~1M messages/s per broker; 1-5 ms end to end; up to 50 TB and weeks of retention | Near 800k messages/s per broker; consumer lag keeps growing |

What these imply:

- A single database handles terabytes; sharding is for the largest systems or for regional needs.
- A cache can hold a whole dataset in memory, which is often simpler than selective caching.
- A server's first limit is usually CPU, not memory, so local caches and in-memory work are cheap.
- Queues are fast enough to sit inside a synchronous request when there's no backlog.

## Common mistakes

- **Premature sharding**: 10M businesses at 1 KB each is 10 GB; ten times that for reviews is 100 GB, which one database holds easily. 100k contests times 100k users at 40 bytes is 400 GB: one large cache.
- **Overestimating latency**: an indexed row lookup takes under a millisecond to a few milliseconds. Cache expensive queries, not simple lookups.
- **A queue for modest writes**: a well-tuned PostgreSQL takes 20k+ simple writes per second (the ~10k TPS trigger above is for typical transactional writes). At 5k writes per second, batch writes, trim indexes and pool connections first. A queue earns its place for guaranteed delivery past a failing consumer, decoupling, event sourcing, or spikes beyond what the database takes.

Cost: orders of magnitude matter (a hundred machines where one will do); exact prices don't.

---

Source: Hello Interview, [Numbers to Know](https://www.hellointerview.com/learn/courses/system-design/lesson/thinking-in-scale/numbers-to-know).
