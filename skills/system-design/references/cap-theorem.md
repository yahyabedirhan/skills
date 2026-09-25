# CAP theorem

What a distributed system does when its nodes can't reach each other: refuse to answer, or answer with possibly stale data. It is the first non-functional requirement to settle, because it shapes every store and replication choice after it.

## The theorem

A distributed system can guarantee at most two of:

- **Consistency**: every read sees the most recent write, on any node.
- **Availability**: every request to a live node gets a response, possibly not the latest data.
- **Partition tolerance**: the system keeps working when messages between nodes are lost.

Network partitions happen, so partition tolerance is required, and the real choice is between consistency and availability during a partition. CAP's consistency is not ACID's consistency, which is about a transaction leaving the data valid.

An example: users in the USA and Europe, with a server in each and replication between them. When the link breaks and a European user views an American user's profile, the system either returns an error (consistency) or shows the last name it has, possibly stale (availability). For a profile, stale is better than an error.

## Choosing

The question: would it be a disaster if users briefly saw inconsistent data? Does every read need the latest write?

- **Consistency**: ticket and seat booking (no double booking), inventory (no overselling the last item), financial systems (order books, balances).
- **Availability**: social media, content platforms, review sites. Most systems are here, with eventual consistency: replicas converge within seconds or minutes.

Real systems choose **per feature**: Ticketmaster is consistent for booking a seat and available for browsing events; a dating app is consistent for matches and available for viewing profiles.

## What each choice puts in the design

- **Consistency**: distributed transactions across stores that must agree, or a single database as the one source of truth; higher latency while nodes agree. PostgreSQL, MySQL, Spanner, DynamoDB in strong consistency mode.
- **Availability**: read replicas with asynchronous replication; change data capture propagating changes to replicas, caches and other systems. Cassandra, multi-zone DynamoDB, Redis clusters.

Most distributed databases are configurable either way; the design names the setting.

## Levels of consistency

- **Strong**: every read sees the latest write. The most expensive.
- **Causal**: related events appear in the same order to everyone (a comment never before its post).
- **Read-your-own-writes**: a user sees their own changes immediately; others may see older versions.
- **Eventual**: replicas converge over time (DNS). The default of most distributed databases, and what choosing availability means.

Naming the weakest level that meets the requirement is more precise than "strongly consistent".

---

Source: Hello Interview, [CAP Theorem](https://www.hellointerview.com/learn/courses/system-design/lesson/thinking-in-scale/cap-theorem).
