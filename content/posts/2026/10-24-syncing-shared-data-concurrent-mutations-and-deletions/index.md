---
date: 2026-10-24
title: "Syncing Shared Data: The Hidden Traps of Concurrent Mutations and Deletions"
description: |-
  Discover why overwriting collections breaks distributed synchronisation, foreign keys, and user interfaces.
  Learn how tombstones, delta-based replication, and logical clocks prevent silent data loss in collaborative applications.
slug: syncing-shared-data-concurrent-mutations-and-deletions
image: /images/posts/2026/10-24-syncing-shared-data-concurrent-mutations-and-deletions.png
tags:
  - Software Pitfalls
  - Software Architecture
---

{{< tldr >}}
Synchronising shared collections across multiple clients is deceptively complex.
Overwriting destination data wholesale destroys persistent identifiers, invalidates foreign keys, and silently vaporises concurrent edits made during network transit.

- **Never replace collections wholesale:** Overwriting entire lists breaks relational foreign keys, resets user interface focus, and introduces catastrophic race conditions.
- **Treat removals as explicit facts:** In distributed systems, absence is not proof of deletion; use tombstones (`deleted_at` markers or deletion events) to prevent stale clients from resurrecting zombie records.
- **Synchronise operation deltas, not snapshots:** Transmit discrete mutation events containing entity identifiers, version tokens, and modified attributes.
- **Distrust wall-clock timestamps:** Device clocks drift and skew; rely on monotonic revision numbers, [Lamport timestamps](https://en.wikipedia.org/wiki/Lamport_timestamp), or [Conflict-Free Replicated Data Types (CRDTs)](https://crdt.tech/) to order changes.
{{< /tldr >}}

When you build an application that displays a collection of items, synchronisation feels deceptively straightforward at first.
Your client fetches the current list from an API, your user makes a few edits or removes a row, and you send the updated collection back to the server.
If you only test your application on a fast local connection with a single test account, this approach seems fast, clean, and completely reliable.

In production, this pattern is a ticking time bomb.
The moment two people edit the same shared collection simultaneously, or a mobile user experiences a brief tunnel outage, your synchronisation routine begins silently destroying data.
Data synchronisation is not a file transfer problem; it is a [distributed consensus](https://en.wikipedia.org/wiki/Consensus_(computer_science)) problem.

In this guide, I explore the hidden traps of synchronising shared data across distributed clients.
This article continues my [Software Pitfalls]({{< ref "/tags/software-pitfalls" >}}) series, following [Parsing CSV and Delimited Files]({{< ref "10-17-parsing-csv-and-delimited-files" >}}) and [Never Roll Your Own Date Maths]({{< ref "09-26-never-roll-your-own-date-maths" >}}).
I'll explain why full-collection replacement fails, how early cloud sync engines collapsed under this weight, how to handle deletions safely, and how to structure real-time collaborative updates.

## The Destructive Illusion of the Full Replace

The most common synchronisation anti-pattern is what I call the "full-replace fallacy".
When faced with synchronising a modified list or dataset, developers often choose to wipe the destination table or array and repopulate it with the client's current local state.
On paper, this avoids writing custom merge logic.
In reality, it causes three immediate architectural failures.

First, rebuilding a collection destroys persistent identity.
Real-world entities rarely exist in isolation; they have foreign keys pointing to them from audit logs, analytics events, sub-tasks, or external URLs.
If your sync routine deletes existing records and recreates them, auto-incrementing database identifiers change, [UUIDs](https://en.wikipedia.org/wiki/Universally_unique_identifier) cycle, and relational integrity shatters.

Second, replacing whole collections wrecks client-side user interfaces.
Modern UI frameworks like [React](https://react.dev/), [Vue](https://vuejs.org/), or [SwiftUI](https://developer.apple.com/xcode/swiftui/) rely on stable keys to reconcile the DOM or view hierarchy.
When an entire list is replaced, active text inputs lose focus, scroll positions jump abruptly to the top, and in-flight animations glitch.

Third, and most dangerously, full-state replacement guarantees silent data loss during concurrent edits.
Consider two users, Alice and Bob, collaborating on a shared project list:

1. At time `t=0`, the list contains items `[A, B]`.
2. At `t=1`, Alice goes offline in a train tunnel and adds item `C` locally (`[A, B, C]`).
3. At `t=2`, Bob adds item `D` while connected to office Wi-Fi; the server updates to `[A, B, D]`.
4. At `t=3`, Alice regains connectivity and pushes her complete local array (`[A, B, C]`) to the server.

If the server accepts Alice's snapshot as the new state of truth, Bob's item `D` is permanently erased.
Neither user receives an error, and no exception is thrown; the server simply accepted a blind overwrite.

You might argue that Alice's machine should download the latest server state first before pushing her local changes.
Suppose Alice's client downloads `[A, B, D]` and attempts to merge it with her local `[A, B, C]`.
Immediately, a new architectural dilemma emerges: what order should `C` and `D` be in?

Both Alice and Bob appended their new items directly after `B`.
Neither collaborator had any visibility of the other's concurrent addition.
Should the resulting list become `[A, B, C, D]` or `[A, B, D, C]`?
If Alice's client decides arbitrarily and pushes an updated snapshot, she unilaterally imposes an ordering that contradicts Bob's local view, causing the list order to flap unpredictably on the next sync cycle.

## Lessons from the Early iCloud Sync Collapse

This challenge is not unique to amateur software; even tech giants have stumbled badly here.
In the early days of iOS 5 and iOS 6, Apple introduced iCloud [Core Data](https://developer.apple.com/documentation/coredata) sync ([`NSPersistentStoreUbiquitousContentNameKey`](https://developer.apple.com/documentation/coredata/nspersistentstoreubiquitouscontentnamekey)) to let developers synchronise local [SQLite](https://www.sqlite.org/) databases across Macs, iPhones, and iPads.
The premise sounded magical: developers wrote standard local Core Data code, and Apple's underlying framework promised to keep every device in sync automatically.

Behind the scenes, Apple attempted to sync raw SQLite transaction log files across iCloud storage.
This design contained a fatal conceptual flaw: database transaction logs inherently assume a single, strictly sequential timeline.
They cannot cope with an asynchronous world where multiple physical devices generate competing transaction logs while disconnected.

When devices reconnected and attempted to replay each other's raw database logs out of order, the synchronisation engine buckled.
Developers reported persistent bugs that plagued the Apple ecosystem for years: ghost items that reappeared after being deleted, duplicated records proliferating exponentially, and corrupted local databases that forced users to reinstall apps.
Apple eventually deprecated the original iCloud Core Data sync entirely in iOS 10, later replacing it with [`NSPersistentCloudKitContainer`](https://developer.apple.com/documentation/coredata/nspersistentcloudkitcontainer), which synchronises discrete, record-level field mutations rather than low-level database files.

The lesson from Apple's early struggle is clear: you cannot synchronise distributed state by replaying opaque logs or swapping database snapshots.
You must treat individual mutations as discrete domain operations with explicit semantic meaning.

## Deletions and the Tombstone Imperative

When developers transition from snapshot replacement to delta synchronisation, they quickly discover that deletions are significantly harder to handle than additions.
In a single database, deleting an item simply means executing `DELETE FROM items WHERE id = ?`.
In a distributed system, deleting a row from your local database removes all trace of its existence.

Herein lies the trap: in an asynchronous network, the *absence* of data is completely ambiguous.
If Client A sends a list containing items `[1, 3]`, does that mean Client A deleted item `2`, or does it mean Client A has not yet learned about item `2`?
If you simply broadcast your current local items, any peer that still has item `2` in its local storage will assume you are missing it and helpfully re-upload it to the server.
Your deleted item is resurrected as a zombie record.

To delete data reliably across distributed clients, you must never physically destroy the record immediately.
Instead, you must reify the deletion by transforming it into an explicit, immutable fact known as a [**tombstone**](https://en.wikipedia.org/wiki/Tombstone_(data_structure)).

```json
{
  "entity_id": "item-9481a",
  "version": 4,
  "deleted": true,
  "deleted_at": "2026-10-24T10:15:30Z",
  "deleted_by": "user-402"
}
```

A tombstone is an explicit marker that proves an item once existed and was deliberately removed at a specific point in logical time.
When a peer receives a tombstone with a version higher than its local record, it marks the local entity as deleted and hides it from the user interface.
The deletion propagates reliably because it travels as an active payload, not as a passive omission.

## Architecting Community Sync: Deltas and Clocks

Building a real-time collaborative system, such as a shared document or community list, requires moving away from state replacement entirely.
Instead, you architect the system around **operation deltas**.
Clients communicate what happened, not what their entire database currently looks like.

```json
{
  "client_id": "client-mobile-77",
  "base_revision": 142,
  "mutations": [
    {
      "op": "insert",
      "entity_id": "task-881",
      "data": { "title": "Review pull request", "priority": "high" }
    },
    {
      "op": "update",
      "entity_id": "task-412",
      "patch": { "priority": "low" }
    },
    {
      "op": "tombstone",
      "entity_id": "task-205"
    }
  ]
}
```

When handling concurrent updates to these entities, you cannot rely on wall-clock timestamps (`DateTime.now()`).
Physical device clocks suffer from [Network Time Protocol (NTP)](https://en.wikipedia.org/wiki/Network_Time_Protocol) drift, hardware oscillator variations, and manual user clock adjustments.
If Client A's clock is running two minutes slow, their valid updates will be discarded by any naive [Last-Write-Wins (LWW)](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type#LWW-Element-Set_(Last-Write-Wins-Element-Set)) rule that trusts timestamps.
Instead of relying on physical time, robust distributed engines turn to logical clocks such as [Lamport timestamps](https://en.wikipedia.org/wiki/Lamport_timestamp) or version vectors to establish causal order.

To resolve conflicts without data loss, collaborative systems generally adopt one of two architectural patterns:

### 1. Centralised sequenced logs (operational transformation and server authority)

In a centralised architecture (similar to Google Docs' use of [operational transformation](https://en.wikipedia.org/wiki/Operational_transformation) or standard SaaS collaboration tools), the central server acts as the single source of truth.
The server maintains an append-only, monotonically increasing revision counter.

When a client sends a batch of mutations based on revision 142, the server checks if any other client has committed revision 143 in the meantime.
If a concurrent revision occurred, the server either transforms the incoming operations against the intervening changes or executes field-level three-way merging.
Once validated, the server assigns the next sequence number and broadcasts the accepted delta to all connected clients over [WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API).

### 2. Local-first conflict-free replicated data types (CRDTs)

If you are building an offline-first or peer-to-peer system, you cannot rely on an authoritative server to sequence every event.
Instead, clients store data locally in an embedded engine (such as [SQLite](https://www.sqlite.org/) or [IndexedDB](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)) and utilise [Conflict-Free Replicated Data Types](https://crdt.tech/) (like [Automerge](https://automerge.org/) or [Yjs](https://yjs.dev/)).

CRDTs use mathematical data structures, such as [Observed-Remove Sets (OR-Sets)](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type#OR-Set_(Observed-Remove_Set)) and sequence identifiers, that can be merged concurrently in any arbitrary order.
Regardless of network latency or arrival order, every client that receives the same set of operations is mathematically guaranteed to arrive at the exact same final state without human intervention.

The following pseudocode illustrates how a client-side reconciler processes incoming remote deltas against existing persistent records:

```text
function applyRemoteDeltas(localStore, remoteDeltas):
    for delta in remoteDeltas:
        existing = localStore.findById(delta.entity_id)

        if not existing:
            # If the record is unknown and the delta is not a deletion, insert it
            if delta.op != "tombstone":
                localStore.insert(delta.entity_id, delta.data, delta.version)
            continue

        # If incoming change is older than or equal to local version, ignore it
        if delta.version <= existing.version:
            continue

        # Apply valid, newer operations
        if delta.op == "tombstone":
            localStore.markDeleted(delta.entity_id, delta.version)
        elif delta.op == "update":
            # Apply field-level updates without overwriting untouched properties
            mergedData = mergeFields(existing.data, delta.patch)
            localStore.update(delta.entity_id, mergedData, delta.version)
```

By applying granular field-level patches and checking monotonic version numbers, clients merge concurrent changes without overwriting sibling records or losing updates.

## Food for Thought: Two Distributed Puzzles

While adopting persistent IDs, tombstones, and delta sync solves the primary causes of data loss, distributed systems always present deeper challenges.
I leave the following two classic architectural puzzles as exercises for you to think through for your own system designs.

### Puzzle 1: The tombstone garbage collection dilemma

Tombstones successfully prevent deleted records from turning into zombie additions.
However, if your application runs for five years, your database will eventually accumulate millions of tombstones for items that users deleted years ago.
This causes storage bloat and degrades query performance.

If you decide to prune tombstones older than 30 days, what happens when a user opens an old laptop that has been sitting in a drawer for two months?
That stale client reconnects holding items that were deleted 45 days ago.
Because the server has already purged the corresponding tombstones, the server no longer remembers that those items were deleted.
How can an architecture safely garbage-collect tombstones without risking zombie resurrections from dormant clients?

*Hint for further reading:* Investigate how distributed databases enforce retention grace periods, or read about [version vectors](https://en.wikipedia.org/wiki/Version_vector) on Wikipedia to explore how systems track which nodes have observed a change before compacting records.

### Puzzle 2: Collaborative reordering and positional drift

Synchronising unordered key-value records or sets is well-understood, but maintaining an ordered list (like a collaborative kanban board or ranked task list) is notoriously difficult.
If two users simultaneously drag item `Z` between item `A` (position 1) and item `B` (position 2), assigning simple integer positions (`pos = 2`) triggers immediate collisions and cascades of renumbering queries.

Many engineers turn to [fractional indexing](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/) (such as Jira's [LexoRank](https://confluence.atlassian.com/adminjiraserver/managing-lexorank-938847808.html) algorithm), assigning midpoints such as `pos = 1.5`.
However, what happens when two users concurrently insert items between the exact same boundary?
More critically, what happens after hundreds of edits between adjacent items, when your floating-point numbers exhaust [IEEE 754](https://en.wikipedia.org/wiki/IEEE_754) precision?
How would your sync engine rebalance list positions across concurrent clients without locking the entire table?

*Hint for further reading:* Read about [sequence CRDTs](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type#Sequence_CRDTs) on Wikipedia, or explore how variable-length lexicographical strings and [arbitrary-precision arithmetic](https://en.wikipedia.org/wiki/Arbitrary-precision_arithmetic) avoid floating-point exhaustion by generating infinite-precision fractional midpoints.

## Wrapping Up

Building robust synchronisation is fundamentally about respecting distributed systems realities.
Whenever you are tempted to overwrite a destination dataset with a local array snapshot, remember that you are gambling against network latency and your users' time.

To keep your shared data intact and your application responsive:

1. **Retain persistent identifiers:** Never recreate entities from scratch; preserve IDs so foreign keys, cache layers, and UI hierarchies remain stable.
2. **Reify deletions as tombstones:** Treat removals as first-class operations to ensure offline peers learn about deletions rather than resurrecting stale records.
3. **Transmit deltas instead of snapshots:** Send minimal operation payloads that describe what changed rather than resending what already exists.
4. **Decouple ordering from system clocks:** Use monotonic sequence tokens, logical clocks, or CRDTs instead of fragile wall-clock timestamps.

Synchronisation may never be effortless, but by moving from destructive replacements to immutable deltas, you can build collaborative tools that your users can trust.
