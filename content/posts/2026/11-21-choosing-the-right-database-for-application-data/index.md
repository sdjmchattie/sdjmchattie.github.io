---
date: 2026-11-21
title: "Beyond SQL: Choosing the Right Database for Your Application Data"
description: |-
  Relational SQL databases are a brilliant default, but they aren't the best match for every kind of application data.
  See through everyday examples when document, key-value, wide-column, and time-series databases make life easier, and weigh the pros and cons of the leading options.
slug: choosing-the-right-database-for-application-data
image: /images/posts/2026/11-21-choosing-the-right-database-for-application-data.png
tags:
  - Databases
  - Software Architecture
  - Cloud Computing
---

{{< tldr >}}
If you're comfortable with [SQL](https://en.wikipedia.org/wiki/SQL), relational databases should still be your starting point for most applications.
When your data stops fitting neatly into rows and tables, however, [document](https://en.wikipedia.org/wiki/Document-oriented_database), [key-value](https://en.wikipedia.org/wiki/Key%E2%80%93value_database), [wide-column](https://en.wikipedia.org/wiki/Wide-column_store), and [time-series](https://en.wikipedia.org/wiki/Time_series_database) databases each solve a distinct practical problem.

- **Stay with relational SQL as your default:** [PostgreSQL](https://www.postgresql.org/), [MySQL](https://www.mysql.com/), and [Microsoft SQL Server](https://www.microsoft.com/en-us/sql-server) give you flexible joins, [ACID](https://en.wikipedia.org/wiki/ACID) reliability, and `jsonb` columns for occasional unstructured fields.
- **Try a document store for nested objects:** [MongoDB](https://www.mongodb.com/), [Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/introduction), and [Amazon DocumentDB](https://aws.amazon.com/documentdb/) let you store and fetch a whole product or profile in one JSON document.
- **Use a key-value store for instant temporary state:** [Valkey](https://valkey.io/), [Redis](https://redis.io/), and [Memcached](https://memcached.org/) keep caches, sessions, and counters in memory for sub-millisecond lookups.
- **Pick a wide-column store for massive predictable feeds:** [Amazon DynamoDB](https://aws.amazon.com/dynamodb/), [Apache Cassandra](https://cassandra.apache.org/), and [ScyllaDB](https://www.scylladb.com/) handle huge write traffic when you always look up data by the same key.
- **Reach for a time-series database for streams of readings:** [TimescaleDB](https://www.timescale.com/), [InfluxDB](https://www.influxdata.com/), and [QuestDB](https://questdb.io/) compress timestamped metrics and clear out old history cleanly.
{{< /tldr >}}

In an earlier post, I compared [MySQL, PostgreSQL, and SQL Server]({{< ref "05-30-mysql-postgresql-sql-server" >}}) to help you choose a relational database.
For many developers, [SQL](https://en.wikipedia.org/wiki/SQL) is home turf, so the natural follow-up question is: when does it actually make sense to leave relational tables behind?

Most applications don't only store neat customer and order tables.
Sooner or later, you run into product catalogues with wildly different attributes, short-lived login sessions, activity feeds with millions of rows, or sensor readings arriving every second.

In this guide, I look at the four main database types used for everyday application data alongside SQL (leaving aside specialist graph stores and the AI embedding stores I covered in [Vector Databases: What They Are and How To Use Them]({{< ref "04-18-vector-databases" >}})), using plain examples to show where each one shines and where it hurts.

## Starting from SQL: Why Look Anywhere Else?

Relational databases like [PostgreSQL](https://www.postgresql.org/), [MySQL](https://www.mysql.com/), and [Microsoft SQL Server](https://www.microsoft.com/en-us/sql-server) remain the best default choice for most projects.
You get reliable [ACID](https://en.wikipedia.org/wiki/ACID) transactions, clear relationships across tables, and the freedom to invent new `JOIN` and `WHERE` queries months after launch.

PostgreSQL even includes a native [`jsonb`](https://www.postgresql.org/docs/current/datatype-json.html) column type, so having a few unpredictable fields doesn't automatically mean you need a new database.
Still, four everyday situations often push teams to look beyond plain SQL tables:

- Your records look like nested JSON objects whose fields change from item to item.
- You're hitting a disk-backed table thousands of times a second just to read temporary session or cache data.
- Write traffic is growing rapidly, yet your application always fetches records using one predictable lookup key.
- You're appending millions of timestamped readings a day and deleting old data is slowing the database down.

Each of the four database categories below tackles one of those problems head-on.

## Document Databases: When Your Data Looks Like Nested Objects

Imagine building an online shop that sells both computer monitors and winter coats.
In SQL, a single `products` table quickly fills up with empty `NULL` columns (`screen_size`, `refresh_rate`, `collar_style`, `fabric`), or forces you to join four or five attribute tables just to render one product page.

A [document database](https://en.wikipedia.org/wiki/Document-oriented_database) stores each product as one self-contained JSON-like record instead.
Here's how that monitor looks inside a document store:

```json
{
  "_id": "prod_84920",
  "category": "monitors",
  "name": "27-Inch IPS Studio Monitor",
  "price_pence": 42900,
  "specifications": {
    "resolution": "3840x2160",
    "refresh_rate_hz": 60
  },
  "variants": [
    { "colour": "silver", "stock": 14 },
    { "colour": "matte-black", "stock": 3 }
  ]
}
```

One read grabs the entire product, including its nested specifications and stock variants, without any joins.
When you add a winter coat next week with `size` and `material` inside `specifications`, the database stores it straight away with no `ALTER TABLE` migration.

### Comparing the options: MongoDB, Azure Cosmos DB, and Amazon DocumentDB

**[MongoDB](https://www.mongodb.com/)** is the best-known document database and offers the richest query features, flexible secondary indexes, and managed cloud hosting via [MongoDB Atlas](https://www.mongodb.com/atlas).
Its downside shows up when you model data relationally anyway: joining across collections is slower and clunkier than SQL, and documents can't grow indefinitely (MongoDB caps each one at 16 MB).

**[Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/introduction)** is Microsoft's globally distributed cloud database, widely used through its JSON document API.
It shines when you want effortless multi-region replication and predictable speed, though its capacity-unit pricing can punish careless queries and ties your system closely to Azure.

**[Amazon DocumentDB](https://aws.amazon.com/documentdb/)** is AWS's managed document engine that speaks the same client protocol as MongoDB.
It integrates smoothly with AWS networking and automated backups, but because it reimplements MongoDB under the hood, some newer MongoDB features and query behaviours lag behind or act slightly differently.

### When a document database fits best

Choose a document database for product catalogues, content management systems, user profiles, or complex forms that your code loads and saves as a single object.
If most of your app is still standard relational tables, however, keeping PostgreSQL and using a `jsonb` column for the occasional flexible field saves you from running a second database.

## Key-Value Stores: When You Need Instant Lookups by ID

Suppose every API call checks a `user_sessions` table in SQL to verify who's logged in, or recalculates a live daily leaderboard across thousands of players.
Running disk-backed SQL queries for temporary data that only lives for 30 minutes wastes database capacity and adds avoidable latency.

A [key-value store](https://en.wikipedia.org/wiki/Key%E2%80%93value_database) skips tables and query planners altogether, keeping data in memory so you can read or update a record by its key in under a millisecond.
Here's how you store an expiring session and maintain a live leaderboard in a couple of commands:

```bash
# Save a session and expire it automatically after 30 minutes
HSET session:9f82a user_id "usr_412" role "editor"
EXPIRE session:9f82a 1800

# Add 25 points to a player's score and fetch the top three
ZINCRBY leaderboard:daily 25 "usr_412"
ZREVRANGE leaderboard:daily 0 2 WITHSCORES
```

Automatic expiry removes the need for a scheduled SQL `DELETE` job to clean up stale sessions.
Keeping the leaderboard in an in-memory sorted set means fetching the top players stays instant without sorting a whole database table.

### Comparing the options: Redis, Valkey, and Memcached

**[Redis](https://redis.io/)** made in-memory key-value stores famous by supporting helpful data structures (hashes, lists, sets, and sorted sets) alongside optional disk persistence.
Its main caveat today is licensing: Redis moved away from its traditional permissive open-source licence in 2024, prompting many teams to check alternatives.

**[Valkey](https://valkey.io/)** is the community-backed open-source fork of Redis created under the Linux Foundation with support from AWS, Google Cloud, and others.
It works with existing Redis libraries out of the box whilst keeping an open-source BSD licence, making it a straightforward choice on managed platforms and self-hosted servers alike.

**[Memcached](https://memcached.org/)** is a simpler, battle-tested cache that stores plain strings and bytes across multiple CPU cores.
It has no persistence and no lists or sorted sets, which makes it less versatile than Valkey or Redis, though it remains fast and dependable for straightforward query caching.

### When a key-value store fits best

Pair a key-value store with your primary database for query caching, user sessions, feature flags, leaderboards, and the request counters I explored in [Rate Limiting and Throttling]({{< ref "11-14-rate-limiting-and-throttling-beyond-simple-counters" >}}) and [Implementing a Cache from Scratch]({{< ref "11-07-implementing-a-cache-from-scratch-to-lru-cache" >}}).
Because memory is far pricier than disk and you can't run ad-hoc searches across arbitrary fields, treat it as a speed layer rather than your sole source of truth.

## Wide-Column Stores: When Massive Scale Meets Predictable Queries

Imagine an application where millions of customers generate activity events all day long.
Your main SQL database starts buckling under constant writes, yet your application only ever runs one query: "give me the 20 latest events for customer X".

A [wide-column store](https://en.wikipedia.org/wiki/Wide-column_store) is built for exactly that trade-off.
Instead of letting you query any column freely like SQL, it organises data physically around the exact lookup key and sort order you specify up front, as shown in this Cassandra table:

```sql
CREATE TABLE activity_feed (
    customer_id uuid,
    created_at timestamp,
    action text,
    details text,
    PRIMARY KEY (customer_id, created_at)
) WITH CLUSTERING ORDER BY (created_at DESC);

-- Fetch the 20 most recent events for one customer
SELECT created_at, action, details
FROM activity_feed
WHERE customer_id = 550e8400-e29b-41d4-a716-446655440000
LIMIT 20;
```

Because every event for a customer sits together on disk sorted newest-first, this lookup stays consistently fast whether you have ten thousand rows or ten billion.
The catch is rigidity: if someone later asks for "all customers who clicked `checkout` yesterday", you can't easily run that query without adding another table shaped for that access pattern.

### Comparing the options: Amazon DynamoDB, Apache Cassandra, and ScyllaDB

**[Amazon DynamoDB](https://aws.amazon.com/dynamodb/)** offers this predictable-key scaling as a serverless AWS service with zero server management.
As I covered in [Why DynamoDB Feels Magical Until You Learn the Trade-Offs]({{< ref "05-09-choosing-dynamodb-in-aws" >}}), it delivers single-digit millisecond speed at virtually any scale, provided you commit to your query patterns early and accept tight AWS coupling.

**[Apache Cassandra](https://cassandra.apache.org/)** is an open-source distributed database built so no single server is a bottleneck or single point of failure.
It absorbs huge write volumes across multiple datacentres reliably, though operating a cluster yourself takes real effort around tuning and routine maintenance.

**[ScyllaDB](https://www.scylladb.com/)** is a C++ reimplementation of Cassandra designed to squeeze much higher throughput and steadier tail latencies out of fewer machines.
It speaks the same query language as Cassandra without Java garbage-collection pauses, though its third-party ecosystem is smaller and some enterprise features are commercial.

### When a wide-column store fits best

Reach for a wide-column database for chat histories, activity feeds, order-tracking timelines, and high-traffic shopping carts where read and write patterns are well understood.
Avoid it during early product prototyping when your data model changes every week, or whenever your team needs flexible joins and ad-hoc reporting.

## Time-Series Databases: When Data Is a Constant Stream of Timestamps

Picture collecting temperature and humidity readings from 50,000 sensors every ten seconds.
A regular SQL table handles the first few million rows fine, until inserts slow down and your nightly `DELETE` query to purge data older than 30 days locks rows and leaves bloated storage behind.

A [time-series database](https://en.wikipedia.org/wiki/Time_series_database) treats time as its main organising axis, automatically grouping incoming readings into daily or weekly chunks.
Grouping by time lets the engine compress repetitive sensor values heavily, calculate time-window averages quickly, and expire old data by dropping an entire past chunk instantaneously instead of deleting rows one by one.

Here's how [TimescaleDB](https://www.timescale.com/) keeps standard SQL syntax while grouping readings into five-minute averages with [`time_bucket`](https://docs.timescale.com/api/latest/hyperfunctions/time_bucket/):

```sql
-- Turn a normal SQL table into a time-partitioned hypertable
SELECT create_hypertable('sensor_readings', by_range('recorded_at'));

-- Calculate five-minute averages across the past hour
SELECT
    time_bucket('5 minutes', recorded_at) AS bucket,
    device_id,
    AVG(temperature_c) AS avg_temp
FROM sensor_readings
WHERE recorded_at >= NOW() - INTERVAL '1 hour'
GROUP BY bucket, device_id
ORDER BY bucket DESC;
```

You write familiar SQL queries, yet behind the scenes the database stores, compresses, and expires those time chunks automatically.

### Comparing the options: TimescaleDB, InfluxDB, and QuestDB

**TimescaleDB** runs as an extension inside PostgreSQL, letting you keep standard SQL joins, ORMs, and backup tooling whilst gaining time-chunk partitioning and compression.
It's the easiest transition for SQL-first teams, though a PostgreSQL-based engine generally won't match the absolute peak single-node ingestion rates of a specialist engine written from scratch.

**[InfluxDB](https://www.influxdata.com/)** is a widely adopted purpose-built time-series database with strong compression and telemetry agent integrations.
Its biggest drawback has been version churn (moving from InfluxQL to a custom Flux language in v2, then pivoting back towards SQL in v3), which left many teams rewriting queries across upgrades.

**[QuestDB](https://questdb.io/)** is an open-source time-series database built for blistering ingestion speed and rapid time-window analytics, adding handy SQL helpers like `SAMPLE BY` and `ASOF JOIN`.
It's a compelling fit for financial tick data and high-frequency telemetry, though you'll still pair it with a normal relational database for user accounts and billing records.

### When a time-series database fits best

Use a time-series database for IoT telemetry, usage metering, server metrics, and financial price histories where records are appended once and queried by time window.
If you regularly update past rows or only log a few thousand events a day, a plain SQL table is simpler and more than enough.

## Wrapping Up

Start with SQL whenever you're unsure, and only adopt a specialist database when your data's shape or traffic genuinely justifies it.
Here's a quick rule of thumb when weighing your options:

- **Stick with relational SQL** (`PostgreSQL`, `MySQL`, `SQL Server`) for core business records, multi-table joins, transactions, and evolving reporting needs.
- **Choose a document store** (`MongoDB`, `Cosmos DB`, `DocumentDB`) when records are self-contained nested objects read and saved as one unit.
- **Add a key-value store** (`Valkey`, `Redis`, `Memcached`) when you need sub-millisecond in-memory speed for caches, sessions, locks, or counters.
- **Choose a wide-column store** (`DynamoDB`, `Cassandra`, `ScyllaDB`) when massive write scale matters more than flexible queries and you already know your lookup keys.
- **Choose a time-series database** (`TimescaleDB`, `InfluxDB`, `QuestDB`) when endless streams of timestamped readings need heavy compression, time-window rollups, and fast expiry.

Most teams get surprisingly far with one solid SQL database and an in-memory cache, adding specialist engines only once a concrete bottleneck appears.
If you'd like to explore more database and architecture trade-offs, browse my posts tagged with [Databases]({{< ref "/tags/databases" >}}), [Software Architecture]({{< ref "/tags/software-architecture" >}}), and [Cloud Computing]({{< ref "/tags/cloud-computing" >}}).

Happy architecting.
