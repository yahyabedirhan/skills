# Common patterns

Recurring problems in system design and their usual shapes. Recognizing a pattern shows what's interesting in a design and where it tends to fail. Most systems combine several: a video platform uploads large blobs, transcodes as a long-running task, pushes progress in real time, and coordinates it all as a multi-step process. Start each with its simplest form and add complexity only for a requirement that needs it.

## Real-time updates

Pushing changes to users as they happen: chat, notifications, live dashboards. Start with HTTP polling; move to SSE (server to client) or WebSockets (both ways) when polling stops meeting the need ([networking-essentials.md](networking-essentials.md)). On the server, pub/sub decouples whoever publishes an update from the servers holding client connections (WhatsApp); stateful servers arranged by consistent hashing suit heavier per-session processing (Google Docs).

## Long-running tasks

Work that takes more than a few seconds: video encoding, reports, bulk operations. The web server validates the request, puts a job on a queue, and returns a job ID immediately; separate workers pull jobs and do the work. Web servers and workers scale independently, and failures stay in the workers. Needs job status tracking, retries, and a dead-letter queue for jobs that keep failing. Short jobs stay synchronous: simpler, with natural back-pressure and a better user experience.

## Dealing with contention

Many users after the same resource at once: the last concert ticket, an auction item. Within one database: transactions, pessimistic locking, or optimistic concurrency control (a version check on write). Across databases: distributed locks, two-phase commit, or serializing through a queue. Databases are built to handle contention; splitting data across stores takes that problem on yourself, so keep contended data in one database as long as possible.

## Scaling reads

Reads usually grow far faster than writes (read-to-write ratios of 10:1 to 100:1 and beyond). The progression: optimize inside the database (indexes, denormalization), then read replicas, then caching layers (Redis, CDNs) ([caching.md](caching.md)). Watch cache invalidation, replica lag, and hot keys.

## Scaling writes

Sharding across servers ([sharding.md](sharding.md)); vertical partitioning (different kinds of data in different stores); queues to absorb bursts; load shedding to drop low-priority writes under overload; batching to cut per-write overhead. The partition key must spread load evenly and keep related data together.

## Handling large blobs

Videos, images, documents. Keep them off the application servers: the server issues a short-lived presigned URL and the client uploads directly to object storage (S3); downloads come from a CDN with signed URLs. This brings resumable uploads and progress tracking. The hard part is keeping database metadata in sync with the blob store through failed uploads and deletions; storage event notifications help.

## Multi-step processes

Business workflows spanning services that must survive failures and retries: order fulfilment, onboarding, payments. From simple to robust: orchestration in a single server; event sourcing, where each step emits the event that triggers the next; workflow engines and durable execution (Temporal, AWS Step Functions) that manage state, retries and history.

## Proximity-based services

Finding entities near a location: rides, restaurants, deliveries. Geospatial indexes (PostgreSQL with PostGIS, Redis geo, Elasticsearch geo queries) divide the map into regions and skip the empty ones ([database-indexing.md](database-indexing.md)). Only needed at hundreds of thousands of items or more; for a thousand, scan them all. Queries are usually local, which also invites regional partitioning.

---

Source: Hello Interview, [Common Patterns](https://www.hellointerview.com/learn/courses/system-design/lesson/scaling-reads/patterns).
