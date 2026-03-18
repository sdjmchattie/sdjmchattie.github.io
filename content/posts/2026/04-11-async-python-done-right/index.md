---
date: 2026-04-11
title: "Seven Tips for Performant Async Python"
description: |-
  Async Python looks simple on the surface: add async and await and you're done.
  But subtle mistakes can make your code behave synchronously, drop exceptions silently, or stall under load.
  This post walks through seven practical tips to help you avoid those pitfalls and get the performance async promises.
slug: async-python-done-right
image: /images/posts/2026/04-11-async-python-done-right.jpg
tags:
  - Python
  - Software Architecture
---

Adding `async` and `await` to a Python function feels like an easy win.
You've heard it makes code faster, so you sprinkle the keywords in, run your program, and it seems to work.
But async Python has a habit of looking correct while quietly running no better or even worse than the synchronous version.
This post covers seven practical tips to help you avoid the common pitfalls and write async code that delivers the concurrency it promises.

## How Async Python Works

Before the tips, it's worth understanding the model.
Python's `asyncio` is single-threaded.
There is one event loop, running in one thread, executing one task at a time.

The key to concurrency is that tasks cooperate.
When a task hits an `await`, it voluntarily pauses and hands control back to the event loop, which can then run a different task.
When the awaited operation is ready, the event loop resumes the original task.
Nothing runs in parallel. The concurrency comes from overlapping the waiting.

A useful analogy: a chef preparing multiple dishes.
They don't clone themselves to cook several things simultaneously.
Instead they start a sauce, then while it simmers they prep vegetables, then check back on the sauce.
They switch between tasks at natural pause points.
That's exactly what `asyncio` does, except the "simmers" are things like waiting for a network response or a file read to complete.

The critical implication: if a task never reaches an `await`, or hits blocking code before it can yield, the event loop is stuck.
Everything else waits.
That is the root cause of most async performance problems.

## Tip 1: Use Async-Native Libraries

The most common mistake is using synchronous libraries inside async code.

Consider making an HTTP request with `requests`:

```python
import asyncio
import requests

async def fetch(url: str) -> str:
    response = requests.get(url)  # Blocks the entire event loop
    return response.text

async def main():
    results = await asyncio.gather(
        fetch("https://example.com/a"),
        fetch("https://example.com/b"),
    )
```

Even though `gather()` is used here (see Tip 4), the requests are not concurrent.
`requests.get()` is a synchronous blocking call. It holds the event loop hostage until the response arrives, so the second fetch doesn't start until the first finishes.

The fix is to use a library written for async, like `aiohttp`:

```python
import asyncio
import aiohttp

async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()

async def main():
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            fetch(session, "https://example.com/a"),
            fetch(session, "https://example.com/b"),
        )
```

Now both requests are in flight at the same time.
While waiting for one response, the event loop progresses the other.

The same principle applies to `time.sleep()`.
It blocks the thread and freezes the event loop.
Replace it with `await asyncio.sleep()`, which yields control while the timer runs.

```python
# Blocks everything:
import time
time.sleep(5)

# Correct: yields to the event loop:
await asyncio.sleep(5)
```

When choosing libraries for an async project, look for ones with an `aio` prefix or an `async`/`await` API.
Popular async-native options include `aiohttp` for HTTP, `aiofiles` for file I/O, and `asyncpg` or `databases` for database access.

## Tip 2: Offload Blocking Code to a Thread

Sometimes you can't avoid a synchronous library.
Legacy code, third-party SDKs, or C extensions may only offer blocking APIs.
The fix is to run them in a thread pool so the event loop isn't stalled.

Python 3.9+ ships `asyncio.to_thread()` for exactly this:

```python
import asyncio
import json

def load_config() -> dict:
    with open("config.json") as f:
        return json.load(f)

async def main():
    config = await asyncio.to_thread(load_config)
```

`asyncio.to_thread()` runs the function in a thread pool executor and returns an awaitable.
The event loop continues processing other tasks while the thread does its work, and picks up the result when it's ready.

For older Python versions, or when you need more control over the thread pool, use `loop.run_in_executor()` directly:

```python
import asyncio
import functools

async def main():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, functools.partial(blocking_fn, arg1, arg2))
```

Passing `None` as the first argument uses the default thread pool executor.

This approach works for reading files, calling synchronous HTTP clients, interacting with boto3, or any other blocking operation you can't replace.

## Tip 3: Always Await Your Coroutines

An `async def` function doesn't run when you call it.
It returns a coroutine object.
The coroutine only executes when you `await` it (or schedule it as a task).

Here's the easy mistake to make:

```python
async def send_notification(user_id: int) -> None:
    await some_http_call(user_id)

async def process_order(order_id: int) -> None:
    await save_order(order_id)
    send_notification(order_id)  # Coroutine created but never run
```

`send_notification` is called but not awaited.
Python will emit a `RuntimeWarning: coroutine 'send_notification' was never awaited`, but the code won't crash and the notification will silently never be sent.

The fix is to either await it immediately:

```python
await send_notification(order_id)
```

Or, if you want it to run concurrently without blocking the current function, schedule it as a task:

```python
asyncio.create_task(send_notification(order_id))
```

Be aware of the exception-handling implications of `create_task()`, which are covered in Tip 7.

## Tip 4: Run Tasks Concurrently with `asyncio.gather()`

Awaiting coroutines one after another is still sequential:

```python
async def main():
    result_a = await fetch("https://example.com/a")  # Waits here
    result_b = await fetch("https://example.com/b")  # Then waits here
```

If each fetch takes one second, `main()` takes two seconds total.
Async adds no benefit. This is behaviorally identical to synchronous code.

`asyncio.gather()` runs multiple coroutines concurrently:

```python
async def main():
    result_a, result_b = await asyncio.gather(
        fetch("https://example.com/a"),
        fetch("https://example.com/b"),
    )
```

Now both fetches are in flight simultaneously.
If each takes one second, `main()` completes in roughly one second.

By default, if any coroutine raises an exception, `gather()` immediately raises that exception to the caller.
The other coroutines continue running, but their results and any exceptions they raise are lost.
To handle errors gracefully, pass `return_exceptions=True`:

```python
results = await asyncio.gather(
    fetch("https://example.com/a"),
    fetch("https://example.com/b"),
    return_exceptions=True,
)

for result in results:
    if isinstance(result, Exception):
        print(f"Request failed: {result}")
    else:
        print(f"Got {len(result)} bytes")
```

With this approach every result or exception is captured, and you can decide how to handle each one.

## Tip 5: Use `TaskGroup` for Safer Concurrency (Python 3.11+)

`asyncio.TaskGroup` is the modern alternative to `gather()`, introduced in Python 3.11.
It uses a context manager to group tasks and provides cleaner error semantics.

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        task_a = tg.create_task(fetch("https://example.com/a"))
        task_b = tg.create_task(fetch("https://example.com/b"))

    # Results available after the block
    print(task_a.result())
    print(task_b.result())
```

The block waits until all tasks complete.
If any task raises an exception, the task group cancels the remaining tasks and re-raises the exception as an `ExceptionGroup`.
This makes error handling predictable: a failure in one task won't leave other tasks running in the background.

`TaskGroup` also makes it easy to add tasks dynamically inside the block, which can be awkward to manage with `gather()`.
If you're on Python 3.11 or later, prefer `TaskGroup` for most concurrent workloads.

## Tip 6: Control Concurrency with `asyncio.Semaphore`

`gather()` and `TaskGroup` will launch all tasks immediately.
If you have hundreds of URLs to fetch or files to process, that means hundreds of simultaneous connections, which can overwhelm an API, exhaust a connection pool, or get your IP rate-limited.

`asyncio.Semaphore` solves this by capping how many tasks run at once:

```python
import asyncio
import aiohttp

async def fetch(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, url: str) -> str:
    async with semaphore:
        async with session.get(url) as response:
            return await response.text()

async def main():
    urls = [f"https://example.com/item/{i}" for i in range(200)]
    semaphore = asyncio.Semaphore(10)  # At most 10 concurrent requests

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, semaphore, url) for url in urls]
        results = await asyncio.gather(*tasks)
```

The semaphore acts like a gate: each task acquires it before doing work and releases it when done.
Once 10 tasks hold the semaphore, any additional tasks pause at the `async with semaphore:` line until one of the running tasks finishes.

This lets you tune throughput to what the target system can handle, without changing the structure of the rest of the code.

## Tip 7: Never Lose Task Exceptions

`asyncio.create_task()` schedules a coroutine to run concurrently without blocking the current function.
It's useful, but there's a trap.

If you don't keep a reference to the task and await it, any exception it raises is silently swallowed:

```python
async def risky_operation() -> None:
    raise ValueError("Something went wrong")

async def main():
    asyncio.create_task(risky_operation())  # Exception is lost
    await asyncio.sleep(1)
```

When `risky_operation()` raises, Python has nowhere to deliver the exception because nothing is watching the task.
Python will eventually log a `Task exception was never retrieved` message, but that's easy to miss and comes too late to handle the failure meaningfully.

To reliably handle the exception, save the task and await it:

```python
async def main():
    task = asyncio.create_task(risky_operation())
    try:
        await task
    except ValueError as e:
        print(f"Caught: {e}")
```

If you're firing off background tasks and don't want to await them inline, add a done callback:

```python
def handle_result(task: asyncio.Task) -> None:
    if task.exception():
        print(f"Background task failed: {task.exception()}")

task = asyncio.create_task(risky_operation())
task.add_done_callback(handle_result)
```

The callback runs when the task completes or raises, giving you a place to log or recover.
With Python 3.11+, `TaskGroup` is often cleaner than managing this manually, as it raises exceptions automatically when the group exits.

## When Async Isn't the Answer

Async excels at I/O-bound work: anything where your code spends time _waiting_.
Waiting for an HTTP response, a database query, or a file read are all idle periods where the event loop can do something else.

For CPU-bound work such as heavy computation, image processing, data transformations, or encryption, async adds no benefit.
The event loop is a single thread, and CPU work keeps it completely occupied.
While your code crunches numbers, no other task can run.

This is where the difference between concurrency and parallelism matters.
Async gives you concurrency: multiple tasks progressing by taking turns on one thread.
For CPU work you need parallelism: multiple cores running simultaneously.

Python threads can help in some cases, since the GIL is released during I/O and C extensions, and Python 3.13 introduced a free-threaded mode that reduces GIL contention further.
But for pure Python CPU work, threads compete on the GIL and don't truly run in parallel.

The right tool for CPU-bound parallelism is `concurrent.futures.ProcessPoolExecutor`, which distributes work across multiple processes:

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

def heavy_computation(n: int) -> int:
    return sum(i * i for i in range(n))

async def main():
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, heavy_computation, 10_000_000)
    print(result)
```

This offloads the CPU work to a separate process, and the event loop remains free to handle other tasks in the meantime.
If your async application has both I/O and CPU-heavy operations, combining `asyncio` with `ProcessPoolExecutor` gives you the best of both worlds.

## Debugging Async Code

When async code misbehaves, the default error messages can be cryptic.
Debug mode makes the event loop much more talkative:

```python
asyncio.run(main(), debug=True)
```

Or set the environment variable before running your script:

```bash
PYTHONASYNCIODEBUG=1 python main.py
```

With debug mode on, the event loop will:

- Log a warning for any callback or coroutine that takes longer than 100ms, which is a strong signal that something is blocking.
- Detect non-threadsafe API calls from outside the event loop thread.
- Provide longer, more detailed tracebacks for async errors.

For finer-grained inspection, configure the asyncio logger:

```python
import logging
logging.getLogger("asyncio").setLevel(logging.DEBUG)
```

To see all tasks currently running or pending:

```python
tasks = asyncio.all_tasks()
for task in tasks:
    task.print_stack()
```

This is particularly useful when the program hangs and you want to know which tasks are stuck and where.

## Wrapping Up

Async Python delivers real performance gains, but only when you use it correctly.
Here's a summary of the seven tips:

1. **Use async-native libraries**: `aiohttp` instead of `requests`, `asyncio.sleep()` instead of `time.sleep()`.
2. **Offload blocking code**: wrap sync libraries with `asyncio.to_thread()` or `run_in_executor()`.
3. **Always await coroutines**: calling without `await` silently does nothing.
4. **Use `asyncio.gather()`** with `return_exceptions=True` to run tasks concurrently without losing errors.
5. **Prefer `TaskGroup`** on Python 3.11+ for safer structured concurrency.
6. **Throttle with `Semaphore`** when running many tasks against rate-limited or resource-constrained targets.
7. **Track your tasks**: always await or add callbacks to tasks created with `create_task()`.

And remember: async is the right tool for I/O-bound work, not CPU-bound work.
When you need to crunch numbers in parallel, reach for `ProcessPoolExecutor` instead.

For more Python content, browse the [Python]({{< ref "/tags/python" >}}) tag.
Happy coding!
