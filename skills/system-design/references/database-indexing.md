# Database indexing

How a database finds rows without scanning the whole table, and which kind of index fits which query.

## Why indexes, and their cost

Data lives on disk and is read into memory page by page; without an index, a query reads every page. An index is a separate structure that points straight at the pages holding the match. Random reads stay slower than sequential ones even on SSDs, which is why this matters.

Indexes cost disk space and slow every write, because each index is updated too. They don't pay on write-heavy tables that are rarely read, on tiny tables, or for predicates that match most of the table (reading most rows through an index is slower than a scan).

## Index types

| Index | How it works | Use it for |
|---|---|---|
| **B-tree** | A balanced, sorted tree with wide nodes sized to disk pages; a lookup reads a few pages | The default: equality, ranges, sorting. What primary keys and unique constraints create (PostgreSQL, MySQL, MongoDB) |
| **LSM tree** | The table's storage format, not an add-on: writes go to an in-memory table and a write-ahead log, flush to sorted immutable files, and merge in the background. Reads check several files, helped by bloom filters | Write-heavy workloads: metrics, logs, events (Cassandra, RocksDB) |
| **Hash** | A persistent hash map; exact matches only | Rarely; in-memory stores like Redis. B-trees are nearly as fast and also do ranges |
| **Geospatial** | Geohash turns a location into a string whose shared prefix means nearness, so a B-tree can serve it; quadtrees split dense regions finer; R-trees group nearby objects in overlapping rectangles and also hold shapes | "Near me" queries (Yelp, Uber). Latitude and longitude as two B-tree indexes can't do a proximity search. R-trees are the production default (PostGIS); Redis geo uses geohash |
| **Inverted** | Maps each term to the documents containing it, after tokenizing, lowercasing and stemming | Full-text search (Elasticsearch, Lucene); `LIKE '%word%'` can't use a B-tree |

## Optimization patterns

- **Composite indexes** cover several columns in one sorted structure, so a query can filter and sort in one pass: `(user_id, created_at)` serves "a user's posts, newest first". Column order matters: the index serves only queries on a leading prefix of its columns, so it doesn't serve "all posts after a date".
- **Covering indexes** include the columns a query returns, so it never reads the table. A niche optimization with real storage and write costs; name the query that needs it.

## In a design

Name the index each main query needs and tie it to its endpoint ("`GET /users/{id}/posts` needs an index on `posts.user_id`"). B-tree unless the data is spatial or the query is full-text.

---

Source: Hello Interview, [Database Indexing](https://www.hellointerview.com/learn/courses/system-design/lesson/foundations/db-indexing).
