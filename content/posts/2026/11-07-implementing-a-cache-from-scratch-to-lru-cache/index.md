---
date: 2026-11-07
title: "A Cache Is Just a Dictionary, Right? Implementing LRU Caching from Scratch"
description: |-
  Discover why building a reliable in-memory cache is far more complex than wrapping a dictionary.
  Explore memory exhaustion, O(1) doubly-linked list eviction, hash collisions, concurrency locks, and how Python's functools.lru_cache solves them all.
slug: implementing-a-cache-from-scratch-to-lru-cache
image: /images/posts/2026/11-07-implementing-a-cache-from-scratch-to-lru-cache.png
tags:
  - Software Pitfalls
  - Python
  - Software Architecture
math: true
---

{{< tldr >}}
Wrapping a hash map in a helper function seems like a trivial weekend project, but custom in-memory caches rapidly cause severe memory leaks, subtle data corruption, and catastrophic performance degradation.
Writing a production-ready cache demands constant-time eviction algorithms, defensive key serialisation, and rigorous thread synchronisation.

- **Unbounded caches exhaust memory:** Naive dictionaries grow indefinitely until the operating system's [Out-of-memory (OOM) killer](https://en.wikipedia.org/wiki/Out_of_memory) terminates your application process.
- **Eviction requires linked structures:** Slicing a [Python list](https://docs.python.org/3/tutorial/datastructures.html) to track recency creates $O(N)$ overhead; true [Least Recently Used (LRU)](https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU)) eviction demands a combined [hash map](https://en.wikipedia.org/wiki/Hash_table) and [doubly-linked list](https://en.wikipedia.org/wiki/Doubly_linked_list) operating in [amortised constant time](https://en.wikipedia.org/wiki/Amortized_analysis) $O(1)$.
- **Beware type and mutability traps:** Python treats `1`, `1.0`, and `True` as identical dictionary keys, while returning mutable objects allows callers to corrupt cached state across the entire application.
- **Threading demands locks:** Unsynchronised pointer updates under concurrent access trigger race conditions, corrupted linked chains, and infinite loops.
- **Skip the manual mechanics:** If you need an efficient, battle-tested solution, jump straight to [The Standard Library Rescue: functools.lru_cache](#the-standard-library-rescue-functoolslru_cache) to see how Python's standard library solves these headaches with a single decorator.
{{< /tldr >}}

"Why would you need a dedicated caching library?
A cache is just a dictionary."
It is very easy to think that way about what, on the surface, looks like a subclass of a dictionary.

When you notice a slow database query or a CPU-intensive calculation, reaching for an in-memory dictionary feels like common sense.
You write three lines of code: check whether the arguments exist in a global dictionary, return the cached value if found, or compute and store it otherwise.
In local development, your response times drop from hundreds of milliseconds to microseconds, and everything looks triumphant.

I strongly recommend that you pause before shipping that pattern to production.
A naive dictionary is not a cache; it is a slow-motion memory leak waiting for sufficient traffic to crash your server.

This post forms part of my [Software Pitfalls]({{< ref "/tags/software-pitfalls" >}}) series, continuing from [Parsing Structured Identifiers]({{< ref "10-31-parsing-structured-identifiers-email-url" >}}) and [Handling Currency Calculations]({{< ref "10-03-handling-currency-calculations" >}}).
In this guide, I explore the layers of complexity behind building an in-memory cache manually, from bounded eviction data structures to thread safety and subtle hash collisions.

> **Looking for the ready-made solution?**
> If you want to skip the algorithmic mechanics and see how to configure Python's standard library decorator, jump straight to [The Standard Library Rescue: functools.lru_cache](#the-standard-library-rescue-functoolslru_cache).

## The Seductive Simplicity of Unbounded Dictionaries

To see why rolling your own cache is hazardous, consider the classic implementation that many developers write early in their careers.

```python
_cache: dict[tuple, object] = {}

def fetch_user_profile(user_id: int) -> dict:
    if user_id not in _cache:
        # Simulate an expensive database fetch
        _cache[user_id] = query_database_for_profile(user_id)
    return _cache[user_id]
```

At first glance, this pattern seems completely functional.
It avoids duplicate network calls and leverages Python's built-in [`dict`](https://docs.python.org/3/tutorial/datastructures.html#dictionaries), which provides average $O(1)$ key lookups.

The fatal defect lies in the lifetime of the process.
Every unique user identifier stored in `_cache` remains in memory forever.
In a long-running web service built with [FastAPI](https://fastapi.tiangolo.com/) or [Gunicorn](https://gunicorn.org/), incoming traffic will continuously add new entries without ever discarding old ones.

Over hours or days, resident memory steadily climbs.
Eventually, the host system runs out of physical memory and swap space, prompting the operating system's [Out-of-memory (OOM) killer](https://en.wikipedia.org/wiki/Out_of_memory) to terminate the process without warning.
To build a sustainable cache, you must enforce an absolute upper bound on memory consumption.

## Choosing an Eviction Strategy

Once you accept that a cache must have a fixed capacity, you face a fundamental question: when the cache is full and a new item arrives, which existing entry should you discard?

Several standard [cache replacement policies](https://en.wikipedia.org/wiki/Cache_replacement_policies) exist:

- **[FIFO (First-In, First-Out)](https://en.wikipedia.org/wiki/FIFO_(computing_and_electronics)):** Discards the oldest item inserted into the cache. While trivial to implement with a queue, it frequently purges critical, high-frequency data that happened to load during server startup.
- **[LFU (Least Frequently Used)](https://en.wikipedia.org/wiki/Least_frequently_used):** Counts how many times each key is requested and evicts the lowest count. While intuitive, it suffers from severe historical bias: an item requested a thousand times during a morning traffic spike remains cached indefinitely, preventing newly trending items from entering.
- **[LRU (Least Recently Used)](https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU)):** Discards the entry that has gone the longest without being accessed. LRU exploits [temporal locality](https://en.wikipedia.org/wiki/Locality_of_reference): data accessed recently is statistically much more likely to be requested again in the near future.

For general-purpose application caching, LRU represents the standard benchmark.
However, implementing an LRU policy introduces strict algorithmic constraints: lookups, updates, and evictions must all execute in [amortised constant time](https://en.wikipedia.org/wiki/Amortized_analysis) $O(1)$.

## Building an LRU Cache from Scratch

When developers first attempt to implement an LRU cache, they often reach for a familiar data structure: a standard list.

### The linear scan trap

A common initial attempt combines a dictionary for values with a list to track recency.
Whenever a key is requested, you find its position in the list, remove it, and append it to the end.

```python
class NaiveLRUCache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.cache: dict[str, object] = {}
        self.order: list[str] = []

    def get(self, key: str) -> object | None:
        if key not in self.cache:
            return None
        # O(N) search and removal!
        self.order.remove(key)
        self.order.append(key)
        return self.cache[key]
```

This approach works logically, but it ruins performance.
Calling `list.remove(key)` performs an $O(N)$ linear search through the list, followed by an $O(N)$ memory shift to close the resulting gap.
Under heavy throughput with a capacity of thousands of items, your cache spends vastly more CPU cycles shifting memory in arrays than executing your business logic.

### Hash map meets doubly-linked list

To achieve true $O(1)$ operations, you need two properties simultaneously: instant key lookup and instant element reordering without shifting neighbours.
A [hash map](https://en.wikipedia.org/wiki/Hash_table) provides instant lookups, while a [doubly-linked list](https://en.wikipedia.org/wiki/Doubly_linked_list) allows removing and splicing nodes in $O(1)$ time, provided you already hold a direct pointer to the target node.

You combine them by storing list nodes directly inside the dictionary values.
Each node tracks its key, its stored value, and pointers to its preceding and succeeding neighbours.

To eliminate fiddly `None` pointer checks when updating the list boundaries, you establish two sentinel nodes: a dummy `head` and a dummy `tail`.

```
  [Head Sentinel] <---> [Most Recent Node] <---> [Least Recent Node] <---> [Tail Sentinel]
```

Every time a key is accessed or updated, you detach its node from its current position and splice it immediately behind `head`.
When the cache reaches capacity, the node directly preceding `tail` is evicted.

### Implementing constant-time eviction

Here is how you assemble this data structure in Python:

```python
class Node:
    __slots__ = ("key", "val", "prev", "next")

    def __init__(self, key: str = "", val: object = None) -> None:
        self.key = key
        self.val = val
        self.prev: Node | None = None
        self.next: Node | None = None


class ManualLRUCache:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("Capacity must be greater than zero.")
        self.capacity = capacity
        self.lookup: dict[str, Node] = {}

        # Sentinel nodes simplify pointer manipulation
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove_node(self, node: Node) -> None:
        """Unlink an existing node from the doubly-linked list."""
        prev_node = node.prev
        next_node = node.next
        if prev_node and next_node:
            prev_node.next = next_node
            next_node.prev = prev_node

    def _add_to_front(self, node: Node) -> None:
        """Insert a node directly after the dummy head (most recently used)."""
        node.next = self.head.next
        node.prev = self.head
        if self.head.next:
            self.head.next.prev = node
        self.head.next = node

    def get(self, key: str) -> object | None:
        node = self.lookup.get(key)
        if node is None:
            return None

        # Move accessed node to the front
        self._remove_node(node)
        self._add_to_front(node)
        return node.val

    def put(self, key: str, val: object) -> None:
        if key in self.lookup:
            node = self.lookup[key]
            node.val = val
            self._remove_node(node)
            self._add_to_front(node)
            return

        if len(self.lookup) >= self.capacity:
            # Evict least recently used node (immediately before tail sentinel)
            lru_node = self.tail.prev
            if lru_node and lru_node != self.head:
                self._remove_node(lru_node)
                del self.lookup[lru_node.key]

        new_node = Node(key, val)
        self._add_to_front(new_node)
        self.lookup[key] = new_node
```

Python actually bundles this linked structure inside the standard library under [`collections.OrderedDict`](https://docs.python.org/3/library/collections.html#collections.OrderedDict).
By combining `OrderedDict.move_to_end()` and `OrderedDict.popitem(last=False)`, you can achieve the same algorithmic behaviour with fewer manual pointers.

However, writing the pointers by hand illuminates the mechanical reality: maintaining an eviction policy requires deliberate state management and constant pointer coordination.
And unfortunately, getting the pointers right is only your first hurdle.

## The Hidden Engineering Traps

Once your data structure handles $O(1)$ lookups and evictions, real-world application quirks begin to emerge.
Building a generic cache exposes subtle corner cases in language semantics and systems architecture.

### Hash collisions and type confusion

In Python, dictionary keys rely on the [`hash()`](https://docs.python.org/3/library/functions.html#hash) built-in and equality comparison (`==`).
Because of Python's numerical model, booleans inherit from integers, and float equality bridges type boundaries.

Specifically, Python evaluates:
```python
hash(1) == hash(1.0) == hash(True)  # Evaluates to True
1 == 1.0 == True                    # Evaluates to True
```

If your cache key is derived naively from function arguments, calling `fetch_report(1)` will produce an entry that is immediately overwritten by `fetch_report(1.0)` or `fetch_report(True)`.
Unless your cache key includes explicit type metadata alongside values, one data type will silently corrupt the cached result for another.

### Argument ordering and unhashable parameters

When you turn a function call into a cache key, function arguments introduce further pitfalls:

- **Keyword permutations:** Calling `calculate(limit=10, offset=0)` and `calculate(offset=0, limit=10)` represent the identical invocation, yet a naive tuple serialisation treats them as different keys.
- **Default arguments:** Calling `render(title="Home")` versus `render(title="Home", theme="dark")` where `theme="dark"` is the function default produces redundant cache entries unless arguments are bound to the function signature using [`inspect.signature`](https://docs.python.org/3/library/inspect.html#inspect.signature).
- **Unhashable arguments:** If a function accepts a `list`, `dict`, or custom class without a `__hash__` method, Python raises a `TypeError: unhashable type` the moment you attempt to use it as a dictionary key.

Generating a reliable cache key requires sorting keyword arguments, canonicalising defaults, and converting nested mutable structures into immutable equivalents like tuples or frozen sets.

### Concurrency and thread safety

Modern web frameworks handle requests across multiple threads or asynchronous worker pools.
Our `ManualLRUCache` class is completely unsafe in a multithreaded environment.

Consider what happens when Thread A and Thread B call `put()` at the exact same millisecond:

1. Thread A detaches `lru_node` from the tail.
2. The operating system context-switches to Thread B before Thread A updates `node.prev.next`.
3. Thread B attempts to inspect `self.tail.prev` and reads stale pointer references.
4. Pointers become detached, orphan nodes remain in memory, and the linked list enters an infinite cycle, locking your CPU core at 100%.

To make the cache thread-safe, you must wrap all reads, writes, and pointer updates in a mutual exclusion lock using [`threading.Lock`](https://docs.python.org/3/library/threading.html#threading.Lock) or [`threading.RLock`](https://docs.python.org/3/library/threading.html#threading.RLock).

```python
import threading

class ThreadSafeLRUCache(ManualLRUCache):
    def __init__(self, capacity: int) -> None:
        super().__init__(capacity)
        self._lock = threading.Lock()

    def get(self, key: str) -> object | None:
        with self._lock:
            return super().get(key)

    def put(self, key: str, val: object) -> None:
        with self._lock:
            super().put(key, val)
```

Adding a lock introduces [lock contention](https://en.wikipedia.org/wiki/Lock_contention).
Every single read request must acquire the exact same lock because `get()` modifies the linked list pointers to track recency.
Under heavy concurrent load, threads queue up waiting for the lock, turning your high-speed cache into a throughput bottleneck.

### Time-to-live and passive expiration

Capacity eviction protects memory bounds, but it does not protect data freshness.
If an external API returns currency conversion rates or auth tokens, caching those values indefinitely based on LRU access order means your application serves stale data long after the source has changed.

Adding [Time-to-live (TTL)](https://en.wikipedia.org/wiki/Time_to_live) brings its own design dilemma:

- **Passive expiration:** Check the timestamp on `get()`. If the entry has expired, discard it and return a cache miss. The downside: keys that are never requested again sit in memory forever, bypassing eviction until the cache fills up.
- **Active expiration:** Run a background worker thread that sweeps through keys periodically to purge expired entries. The downside: periodic sweeps consume CPU cycles and introduce additional locking contention against active readers.

### Mutation and reference aliasing

When an in-memory cache stores a Python object, it does not store a clone; it stores a pointer to the existing object on the heap.
If your cached function returns a mutable structure like a list or a dictionary, any caller that modifies the returned value unwittingly mutates the cached object for every future caller.

```python
@my_custom_cache
def get_allowed_roles(team_id: int) -> list[str]:
    return ["viewer", "editor"]

# In request handler 1:
roles = get_allowed_roles(42)
roles.append("admin")  # Mutates the cached list in-place!

# In request handler 2:
print(get_allowed_roles(42))
# Output: ['viewer', 'editor', 'admin'] -> Critical security bug!
```

To prevent reference aliasing, a custom cache must either enforce deep copies on retrieval using [`copy.deepcopy`](https://docs.python.org/3/library/copy.html#copy.deepcopy), which degrades performance, or require cached functions to return strictly immutable data structures like `tuple` or frozen dataclasses.

## The Standard Library Rescue: functools.lru_cache

At this point, you might wonder whether building and maintaining your own cache wrapper is worth the engineering cost.
Unless you have unique requirements, the answer is almost certainly no.

Python includes a production-grade, highly optimised LRU cache directly in the standard library: [`functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache).
Implemented in C with an underlying circular doubly-linked list and thread-safe locking, it handles recency updates, hashing, and capacity eviction with exceptional speed.

```python
import functools
import time

@functools.lru_cache(maxsize=128)
def fetch_exchange_rate(base: str, target: str) -> float:
    # Simulate an expensive network or database operation
    time.sleep(0.5)
    return 1.25
```

With a single decorator, you get bounded memory, constant-time eviction, and thread-safe execution without managing pointer references or lock primitives.

### Core configuration parameters

As detailed in the official [`functools.lru_cache` documentation](https://docs.python.org/3/library/functools.html#functools.lru_cache), the decorator accepts two configuration arguments:

- **`maxsize`:** Sets the maximum number of items the cache holds before evicting the least recently used entry.
Setting `maxsize=128` (the default) bounds memory predictably.
In Python 3.9+, if you genuinely want unbounded caching without eviction overhead, you can use [`functools.cache`](https://docs.python.org/3/library/functools.html#functools.cache), which is equivalent to `lru_cache(maxsize=None)`.
- **`typed=False`:** By default, arguments of different types with equal values are treated as the same key (e.g., `3` and `3.0`).
Setting `typed=True` forces the cache to categorise arguments of different types separately, neatly solving the type confusion bug we explored earlier.

```python
@functools.lru_cache(maxsize=256, typed=True)
def parse_payload(payload_id: int | float) -> str:
    return f"Processed: {payload_id}"

# With typed=True, these trigger separate cache entries:
parse_payload(1)
parse_payload(1.0)
```

### Cache inspection and invalidation

Production code requires observability and administrative control.
Functions decorated with `lru_cache` expose helper methods directly on the wrapper object.

```python
# Inspect operational telemetry
info = fetch_exchange_rate.cache_info()
print(info)
# Output: CacheInfo(hits=142, misses=12, maxsize=128, currsize=12)

# Inspect configured cache parameters
params = fetch_exchange_rate.cache_parameters()
print(params)
# Output: {'maxsize': 128, 'typed': False}

# Calculate your cache hit ratio
hit_ratio = info.hits / (info.hits + info.misses) if (info.hits + info.misses) else 0.0
print(f"Hit ratio: {hit_ratio:.1%}")

# Manually flush the cache when upstream data changes
fetch_exchange_rate.cache_clear()

# Bypass caching during unit tests or profiling
raw_result = fetch_exchange_rate.__wrapped__("USD", "EUR")
```

The `.cache_info()` method gives you real-time metrics on cache efficacy.
If you observe that `misses` remain consistently high while `currsize` matches `maxsize`, your cache capacity is likely too small for your application's working set, causing thrashing.

### Method caching and time-based expiration

While `functools.lru_cache` solves most caching problems cleanly, you should remain mindful of two specific constraints:

1. **Instance method memory leaks:** If you place `@lru_cache` on an instance method of a class, the cache stores `self` as part of the positional argument key. Because the cache retains strong references to `self` in a global dictionary, instances of your class cannot be garbage-collected, creating a subtle memory leak. For property caching on instances, use [`functools.cached_property`](https://docs.python.org/3/library/functools.html#functools.cached_property) instead.
2. **Lack of time-to-live:** The standard `lru_cache` does not support TTL expiration. If your data becomes invalid after a specific duration, rely on dedicated third-party packages like [`cachetools`](https://github.com/tkem/cachetools) (which offers `TTLCache`) or an external shared cache like [Redis](https://redis.io/).

## Wrapping Up

Writing an in-memory cache is a classic computer science exercise that exposes just how quickly practical software development diverges from simple theory.
What begins as a convenient dictionary lookup rapidly expands into circular doubly-linked lists, pointer management, mutex locking, hash differentiation, and memory isolation.

Understanding these mechanics makes you a much sharper software engineer.
You recognise that memory exhaustion is the default fate of unbounded state, that $O(1)$ operations require specialised composite structures, and that language-level type equality can silently subvert key lookups.

When you need an in-memory cache in production Python, lean on [`functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache).
Configure its `maxsize` to keep memory bounded, enable `typed=True` whenever argument types matter, and monitor your hit ratios via `.cache_info()`.

For more deep dives into deceptive software pitfalls and systems engineering, explore the rest of my articles under the [Software Pitfalls]({{< ref "/tags/software-pitfalls" >}}) tag.
