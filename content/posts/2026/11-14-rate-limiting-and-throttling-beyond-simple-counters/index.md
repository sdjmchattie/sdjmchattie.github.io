---
date: 2026-11-14
title: "Can't I Just Count Requests? The Hidden Pitfalls of Rate Limiting and Throttling"
description: |-
  Discover why simple in-memory request counters fail under boundary burst spikes and multi-instance concurrency.
  Explore Token Buckets, O(1) Sliding Window Counters, atomic Redis Lua scripts, and standard HTTP 429 retry semantics.
slug: rate-limiting-and-throttling-beyond-simple-counters
image: /images/posts/2026/11-14-rate-limiting-and-throttling-beyond-simple-counters.png
tags:
  - Software Pitfalls
  - Python
  - Software Architecture
  - APIs
math: true
---

{{< tldr >}}
Tracking request quotas with a simple counter that resets every minute seems effortless, but naive rate limiters fail under boundary bursts and break across multi-worker deployments.
Building a reliable rate limiter requires continuous-time algorithms, monotonic clocks, and atomic distributed state transitions.

- **Fixed windows invite double-rate bursts:** Resetting a counter on a clock boundary lets callers fire their full quota right before and after the rollover, causing $2\times$ traffic spikes.
- **Avoid $O(N)$ timestamp logs:** Storing every request timestamp in a [sliding window log](https://en.wikipedia.org/wiki/Rate_limiting#Sliding_window_log) solves boundary bursts, but risks memory exhaustion under flood attacks.
- **Favour Token Buckets or Sliding Window Counters:** Use a [Token Bucket](https://en.wikipedia.org/wiki/Token_bucket) to allow short bursts with a steady refill rate, or a [Sliding Window Counter](https://en.wikipedia.org/wiki/Rate_limiting) to approximate rolling windows in $O(1)$ space.
- **Enforce distributed atomicity:** Separate [Redis](https://redis.io/) read and increment calls create [Time-of-Check to Time-of-Use (TOCTOU)](https://en.wikipedia.org/wiki/Time-of-check_to_time-of-use) race conditions; evaluate state atomically inside [Lua](https://www.lua.org/) scripts.
- **Skip the manual mechanics:** Jump straight to [Battle-Tested Libraries: limits and pyrate-limiter](#battle-tested-libraries-limits-and-pyrate-limiter) to use mature Python packages out of the box.
{{< /tldr >}}

"I need to limit users to 100 requests per minute.
I'll just stick a counter in a dictionary and reset it when the minute changes."
If you've ever protected an API endpoint, that thought has probably crossed your mind.

On a whiteboard, rate limiting looks like five lines of arithmetic, and in local testing, it works without a hitch.
I strongly recommend that you resist shipping that counter to production, where real traffic (or a determined scraper) will quickly expose its flaws.

This post is the final instalment in my [Software Pitfalls]({{< ref "/tags/software-pitfalls" >}}) series, following [Implementing a Cache from Scratch]({{< ref "11-07-implementing-a-cache-from-scratch-to-lru-cache" >}}) and [Parsing Structured Identifiers]({{< ref "10-31-parsing-structured-identifiers-email-url" >}}).
In this guide, I explore why simple counters fail at window boundaries, how to implement $O(1)$ rate limiters in Python, why multi-instance concurrency requires atomic execution, and how to reject traffic politely without retry storms.

> **Looking for the ready-made solution?**
> Jump straight to [Battle-Tested Libraries: limits and pyrate-limiter](#battle-tested-libraries-limits-and-pyrate-limiter) to drop a proven package directly into your application.

## Rate Limiting vs. Throttling

Developers often use **rate limiting** and **throttling** interchangeably, though they enforce boundaries differently:

- **[Rate limiting](https://en.wikipedia.org/wiki/Rate_limiting):** Enforces binary admission over a quota period (e.g., 100 requests per minute), immediately rejecting excess requests with HTTP [`429 Too Many Requests`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429).
- **[Throttling (Traffic Shaping)](https://en.wikipedia.org/wiki/Traffic_shaping):** Regulates execution *tempo*, delaying or queueing excess requests so downstream consumers process work at a steady cadence.

API gateways typically apply hard rate limiting at the network edge to shed load cheaply, while internal workers use throttling to protect fragile downstream databases or webhooks.

## The Fixed Window Counter Trap

To see why naive rate limiters fail, consider the classic **Fixed Window Counter** that buckets time into discrete sixty-second intervals (`12:00:00` to `12:00:59`, `12:01:00` to `12:01:59`):

```python
import time

_counters: dict[tuple[str, int], int] = {}

def is_allowed_fixed_window(client_id: str, limit: int = 100) -> bool:
    key = (client_id, int(time.time() // 60))
    count = _counters.get(key, 0)
    if count >= limit:
        return False
    _counters[key] = count + 1
    return True
```

### The boundary burst problem

Aside from leaking memory by never purging old keys (a trap I covered in [Implementing a Cache from Scratch]({{< ref "11-07-implementing-a-cache-from-scratch-to-lru-cache" >}})), fixed windows fail at the seam between intervals:

```text
Window 1 (12:00:00 - 12:00:59)          Window 2 (12:01:00 - 12:01:59)
[......................... 100 reqs] | [100 reqs .........................]
                           12:00:59     12:01:00  --> 200 requests in 2s!
```

A client can fire 100 requests at `12:00:59` and another 100 requests at `12:01:00` as the window resets.
They complied with each isolated calendar minute, yet hammered your backend with **200 requests in two seconds** (double your provisioned rate).

### Clock drift and monotonic time

Notice also the call to [`time.time()`](https://docs.python.org/3/library/time.html#time.time) above.
As I explored in [Never Roll Your Own Date Maths]({{< ref "09-26-never-roll-your-own-date-maths#system-time-jumps-around" >}}), system wall clocks synchronise via the [Network Time Protocol (NTP)](https://en.wikipedia.org/wiki/Network_Time_Protocol) and can step backwards or jump forward at any time.
Always use [`time.monotonic()`](https://docs.python.org/3/library/time.html#time.monotonic) for local duration and refill calculations, as the operating system guarantees it will never jump backwards.

## Algorithmic Upgrades: Smoothing the Spikes

To eliminate boundary bursts, your rate limiter must evaluate traffic across a continuous, rolling horizon rather than resetting on fixed calendar boundaries.

### Sliding window logs vs. O(1) sliding window counters

The most intuitive fix is a **[Sliding Window Log](https://en.wikipedia.org/wiki/Rate_limiting#Sliding_window_log)**: store every request timestamp in a [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque), pop entries older than 60 seconds, and check the queue length.
While exact, its memory scales linearly with the quota ($O(N)$ per user); under a [Distributed Denial-of-Service (DDoS)](https://en.wikipedia.org/wiki/Denial-of-service_attack) flood or high-tier quotas, storing millions of timestamps rapidly exhausts RAM.

A **[Sliding Window Counter](https://en.wikipedia.org/wiki/Rate_limiting)** solves this in $O(1)$ space by keeping only **two integers** per client: the *previous* window's count and the *current* window's count.
When a request arrives 25% into the current minute, the rolling window blends 75% of the previous minute's count with the current count:

$$\text{Estimated Count} = (\text{Previous Count} \times (1 - \text{Progress})) + \text{Current Count}$$

```python
import time
from dataclasses import dataclass

@dataclass
class WindowState:
    window_id: int
    prev: int = 0
    curr: int = 0

class SlidingWindowCounter:
    def __init__(self, limit: int, window_secs: float) -> None:
        self.limit, self.window_secs = limit, window_secs
        self._states: dict[str, WindowState] = {}

    def allow_request(self, client_id: str) -> bool:
        now = time.monotonic()
        win = int(now // self.window_secs)
        progress = (now % self.window_secs) / self.window_secs

        state = self._states.get(client_id)
        if state is None or win > state.window_id + 1:
            self._states[client_id] = WindowState(window_id=win, curr=1)
            return True

        if win == state.window_id + 1:
            state.prev, state.curr, state.window_id = state.curr, 0, win

        if (state.prev * (1.0 - progress)) + state.curr + 1 > self.limit:
            return False

        state.curr += 1
        return True
```

If an attacker fires 100 requests at second 59 of Window 1 and tries again one second into Window 2 (`progress = 1/60`), the estimate evaluates to $(100 \times \frac{59}{60}) + 0 = 98.33$, blocking them after a single request.
Studies at [Cloudflare](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/) show this two-integer formula matches exact sliding logs with over 99.99% accuracy.

### Token bucket vs. leaky bucket

Real-world web traffic is naturally bursty: loading a dashboard page might fire 10 parallel API requests followed by thirty seconds of silence.
To balance burst tolerance with a steady average rate, engineers turn to bucket algorithms:

- **[Token Bucket](https://en.wikipedia.org/wiki/Token_bucket):** Holds up to $B$ tokens (burst cap) and refills continuously at $R$ tokens per second. Each request spends a token (or a custom `cost` for expensive endpoints), permitting an instant burst of $B$ requests before clamping sustained throughput to $R$.
- **[Leaky Bucket](https://en.wikipedia.org/wiki/Leaky_bucket):** Acts as a bounded [FIFO queue](https://en.wikipedia.org/wiki/FIFO_(computing_and_electronics)) that drains at a constant rate, smoothing out bursts completely to protect fragile downstream systems.

You don't need a background timer thread to refill a Token Bucket; calculate replenished tokens **lazily** on each request using `time.monotonic()`:

```python
import time
from dataclasses import dataclass

@dataclass
class Bucket:
    tokens: float
    last_refill: float

class TokenBucketLimiter:
    def __init__(self, capacity: float, refill_rate: float) -> None:
        self.capacity, self.refill_rate = capacity, refill_rate
        self._buckets: dict[str, Bucket] = {}

    def allow_request(self, client_id: str, cost: float = 1.0) -> bool:
        now = time.monotonic()
        b = self._buckets.get(client_id)
        if b is None:
            self._buckets[client_id] = Bucket(self.capacity - cost, now)
            return cost <= self.capacity

        b.tokens = min(self.capacity, b.tokens + (now - b.last_refill) * self.refill_rate)
        b.last_refill = now
        if b.tokens < cost:
            return False
        b.tokens -= cost
        return True
```

## The Multi-Instance Concurrency Trap

Your `TokenBucketLimiter` works cleanly in a single process, but fails the moment you scale horizontally.

### Why local memory and naive Redis calls fail

Production Python web services run multiple worker processes under [Gunicorn](https://gunicorn.org/) or [Uvicorn](https://www.uvicorn.org/) across multiple [Kubernetes](https://kubernetes.io/) pods.
With 5 pods running 4 workers each, you have 20 independent `_buckets` dictionaries in memory, multiplying a user's 100-request quota to 2,000 requests.

Moving state to [Redis](https://redis.io/) solves process isolation, but reading a count with `GET` and incrementing it with `INCR` in Python creates a [Time-of-Check to Time-of-Use (TOCTOU)](https://en.wikipedia.org/wiki/Time-of-check_to_time-of-use) race condition (similar to the concurrency bugs in [Syncing Shared Data]({{< ref "10-24-syncing-shared-data-concurrent-mutations-and-deletions" >}})).
If a user sits at 99/100 requests and fires 10 parallel calls, all 10 workers read `99` simultaneously and allow every request through.

### Atomic execution with Redis Lua scripts

To eliminate TOCTOU races, the read-refill-decrement cycle must run as a single atomic operation on Redis using an embedded [Lua](https://www.lua.org/) script via [`EVAL`](https://redis.io/docs/latest/commands/eval/):

```lua
local key, cap, rate, cost = KEYS[1], tonumber(ARGV[1]), tonumber(ARGV[2]), tonumber(ARGV[3])
local t = redis.call('TIME')
local now = tonumber(t[1]) + (tonumber(t[2]) / 1000000)

local data = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens, last = tonumber(data[1]), tonumber(data[2])
tokens = tokens and math.min(cap, tokens + math.max(0, now - last) * rate) or cap

if tokens < cost then return {0, tostring(tokens)} end
redis.call('HSET', key, 'tokens', tokens - cost, 'last_refill', now)
redis.call('EXPIRE', key, math.ceil(cap / rate) + 10)
return {1, tostring(tokens - cost)}
```

Because Redis executes commands on a single-threaded loop, no other worker can interleave mid-script.
Querying `redis.call('TIME')` ensures every worker uses Redis's internal clock (eliminating cross-server clock drift), while `EXPIRE` automatically purges idle buckets from memory.

## Polite Rejection: HTTP 429 and Client Jitter

How your server communicates rejection determines whether well-behaved clients back off gracefully or accidentally amplify an outage.
Always return HTTP [`429 Too Many Requests`](https://datatracker.ietf.org/doc/html/rfc6585#section-4) ([RFC 6585](https://datatracker.ietf.org/doc/html/rfc6585)) rather than `400` or `500`, paired with standard headers from [RFC 9110](https://datatracker.ietf.org/doc/html/rfc9110#name-retry-after) and the IETF [`RateLimit` specification](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-ratelimit-headers):

- **`Retry-After`:** Seconds the client should wait before retrying a `429` response.
- **`RateLimit-Limit` / `RateLimit-Remaining` / `RateLimit-Reset`:** Lets cooperative SDKs track remaining quota and self-throttle before hitting `429`.

However, if 5,000 throttled clients receive `Retry-After: 60` and sleep for *exactly* 60.0 seconds, they will wake up at the exact same millisecond and slam your server in a synchronised [thundering herd](https://en.wikipedia.org/wiki/Thundering_herd_problem).
Clients must combine **[exponential backoff](https://en.wikipedia.org/wiki/Exponential_backoff)** with **[full jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)** via [`random.uniform`](https://docs.python.org/3/library/random.html#random.uniform):

```python
import random

def backoff_with_jitter(attempt: int, base: float = 1.0, cap: float = 60.0) -> float:
    return random.uniform(0, min(cap, base * (2 ** attempt)))
```

## Battle-Tested Libraries: limits and pyrate-limiter

In production Python, you rarely need to maintain custom Lua scripts yourself.
Two mature libraries handle distributed storage and atomic evaluation out of the box:

- **[`limits`](https://limits.readthedocs.io/):** Powers [`SlowAPI`](https://slowapi.readthedocs.io/) ([FastAPI](https://fastapi.tiangolo.com/)) and [`Flask-Limiter`](https://flask-limiter.readthedocs.io/), supporting fixed window, moving log, and **sliding window counter** strategies across Redis and [Memcached](https://memcached.org/).
- **[`pyrate-limiter`](https://pyratelimiter.readthedocs.io/):** Ideal for bucket smoothing and multi-rate quotas (e.g., max 10 requests/second *and* 500 requests/hour) across in-memory locks, [SQLite](https://www.sqlite.org/), or Redis.

```python
from limits import parse
from limits.storage import RedisStorage
from limits.strategies import SlidingWindowCounterRateLimiter

limiter = SlidingWindowCounterRateLimiter(RedisStorage("redis://localhost:6379"))
policy = parse("100/minute")

def check_api_quota(client_id: str) -> bool:
    return limiter.hit(policy, "api_v1", client_id)
```

| Algorithm | Memory / Client | Stops Boundary Spikes? | Allows Bursts? | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Fixed Window** | $O(1)$ (1 int) | No ($2\times$ spike) | Yes | Coarse daily/monthly billing quotas |
| **Sliding Log** | $O(N)$ ($N$ timestamps) | Yes (exact) | Yes | Low-volume actions (e.g., 3 password resets/hr) |
| **Sliding Counter** | $O(1)$ (2 ints) | Yes (>99.9%) | Yes | General-purpose API rate limiting at scale |
| **Token Bucket** | $O(1)$ (2 floats) | Yes (continuous) | Yes (up to $B$) | Interactive APIs and cost-weighted endpoints |
| **Leaky Bucket** | $O(1)$ + queue | Yes (constant) | No | Throttling calls to fragile downstream services |

## Wrapping Up

Rate limiting and throttling look deceptively simple when sketched as a single-process counter, yet real-world traffic quickly exposes boundary burst spikes, clock drift, $O(N)$ memory traps, distributed TOCTOU race conditions, and retry storms.
Lean on a **Token Bucket** or **Sliding Window Counter** via [`limits`](https://limits.readthedocs.io/) or [`pyrate-limiter`](https://pyratelimiter.readthedocs.io/) to keep memory bounded to $O(1)$ and distributed state transitions atomic.

### Looking back at the Software Pitfalls series

This article brings my [Software Pitfalls]({{< ref "/tags/software-pitfalls" >}}) series to a close.
Over these eight guides, I've explored the hidden depth beneath everyday tasks that look trivial at first glance:

1. **[Date and Time Maths]({{< ref "09-26-never-roll-your-own-date-maths" >}}):** Why days aren't 86,400 seconds and clocks tick backwards.
2. **[Currency Calculations]({{< ref "10-03-handling-currency-calculations" >}}):** Why binary floats corrupt ledgers and penny splitting needs deterministic allocation.
3. **[Parsing and Formatting Numbers]({{< ref "10-10-parsing-and-formatting-numbers" >}}):** Why locales, separators, and non-ASCII digits break naive `float()` casts.
4. **[Parsing CSV and Delimited Files]({{< ref "10-17-parsing-csv-and-delimited-files" >}}):** Why `line.split(",")` fails on embedded newlines and formula injection.
5. **[Syncing Shared Data]({{< ref "10-24-syncing-shared-data-concurrent-mutations-and-deletions" >}}):** Why concurrent edits resurrect deleted records without tombstones and CRDTs.
6. **[Structured Identifiers]({{< ref "10-31-parsing-structured-identifiers-email-url" >}}):** Why regexes fail against RFC email grammars, ReDoS, and obfuscated SSRF IPs.
7. **[In-Memory Caching]({{< ref "11-07-implementing-a-cache-from-scratch-to-lru-cache" >}}):** Why a dictionary is a memory leak without $O(1)$ linked-list eviction and locks.
8. **Rate Limiting and Throttling:** Why simple counters fail under boundary bursts and multi-worker concurrency.

A single thread unites all eight topics: **the problems that sound easiest to describe in plain English are often the hardest to implement correctly from scratch**.
Knowing how these mechanisms work under the hood makes you a wiser architect, and knowing when to reach for a battle-tested library keeps your systems resilient in production.
