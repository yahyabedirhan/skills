# Consistent hashing

How to place keys on a changing set of nodes so that adding or losing a node moves only a small share of the data.

## The problem

Modulo hashing (`hash(key) % number_of_nodes`) spreads keys evenly, but changing the number of nodes changes almost every key's node: adding a fourth database, or losing one, forces most data to move, with load spikes and slow or failed reads while it does.

## How it works

Nodes and keys are hashed onto the same ring of values (in practice 0 to 2^32 - 1). A key belongs to the first node clockwise from its position. Adding a node takes over only the keys between it and the node before it; removing one hands its keys to the next node. Everything else stays put.

**Virtual nodes**: each physical node is placed at many points on the ring (hashing `DB1-vn1`, `DB1-vn2`, and so on). When a node leaves, its keys spread across all the others instead of doubling one neighbour's load; a new node takes a small share from many nodes. More virtual nodes, more even distribution.

## Limits

- **Hot spots**: consistent hashing spreads keys evenly, not traffic. A key that is far busier than the rest (a hugely popular event) needs replication across nodes with reads balanced among them, key salting (`key-0` to `key-9`, read and merged), or moving hot ranges. Virtual nodes fix uneven key placement; replication and salting fix uneven traffic.
- **Data movement on failure**: in practice stores replicate each key range to several nodes (DynamoDB across three zones, Cassandra to the next N nodes on the ring) and promote a replica when a node fails, so no data moves. Data moves on planned changes, and then only a bounded share.
- **An alternative**: fixed hash slots. Redis Cluster maps keys to 16,384 slots and assigns slot ranges to nodes: simpler to reason about, more coordination when rebalancing.

## Where it applies

Anything spread across a cluster: databases (Cassandra, DynamoDB), caches, message brokers, CDNs, stateful servers. When a design uses one of these stores, it's enough to note that it distributes data this way. Explain the ring, virtual nodes, failures and hot spots in depth when designing the distributed database, cache or broker itself.

---

Source: Hello Interview, [Consistent Hashing](https://www.hellointerview.com/learn/courses/system-design/lesson/thinking-in-scale/consistent-hashing).
