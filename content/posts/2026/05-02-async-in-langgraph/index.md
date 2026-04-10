---
date: 2026-05-02
title: "Using Async Effectively in LangGraph"
description: |-
  Async Python fundamentals still matter when you move into LangGraph.
  This post shows how async nodes, `ainvoke()` and `astream()`, streaming progress, and tool execution fit together in a real workflow.
  It also covers the mistakes that still block performance, plus the extra LangGraph concerns around reducers and replay-safe side effects.
slug: async-in-langgraph
image: /images/posts/2026/05-02-async-in-langgraph.jpg
tags:
  - Python
  - LangGraph
  - Agentic AI
  - Software Architecture
---

In [Seven Tips for Performant Async Python]({{< relref "04-11-async-python-done-right" >}}) I focused on plain `asyncio`.
That is the right place to start, because LangGraph does not replace Python's event loop or make blocking code magically concurrent.
If an async LangGraph node calls a blocking library, the graph still waits.
If you fan out too much work without limits, you can still overload an API.
And if you forget where concurrency is actually happening, your graph can look elegant while quietly behaving synchronously.

This post is the LangGraph version of that earlier article.
We will keep the core async lessons, then layer on the LangGraph-specific parts that matter today: async nodes, `ainvoke()`, async tools, reducers, and one important note about durable execution.
I will mention streaming where it matters, but save the full walkthrough for a near-future post in this series.

This is part of a series of posts on LangGraph.
If you are new to the series, start with [A Primer in LangGraph]({{< relref "10-18-a-primer-in-langgraph" >}}) which covers the basics, before working through the later posts.

## What Still Applies from Plain Async Python

The core model has not changed.
As I explained in [How Async Python Works]({{< relref "04-11-async-python-done-right#how-async-python-works" >}}), the event loop only gets a chance to do something else when your code reaches an `await`.
LangGraph builds orchestration on top of that model, but it does not bypass it.
Your graph can schedule work neatly, yet the actual concurrency still depends on the same underlying Python rules.

That means the old pitfalls still matter.
If you call a synchronous HTTP client inside an async node, you have recreated the exact problem described in [Tip 1: Use Async-Native Libraries]({{< relref "04-11-async-python-done-right#tip-1-use-async-native-libraries" >}}).
The node may be declared with `async def`, but the event loop is still blocked until that library returns.
Likewise, if you need to make dozens of requests inside a node, backpressure still matters, which is why [Tip 6: Control Concurrency with asyncio.Semaphore]({{< relref "04-11-async-python-done-right#tip-6-control-concurrency-with-asynciosemaphore" >}}) carries over cleanly into LangGraph.

The easiest way to think about it is this: LangGraph helps you structure concurrent workflows, but it does not excuse you from writing good async Python.
You still want async-native libraries for I/O-bound work.
You still want `asyncio.to_thread()` when a blocking SDK is unavoidable.
And you still need to decide where concurrency should happen and where it should be capped.

## What LangGraph Adds on Top

LangGraph adds orchestration primitives rather than a new async model.
Nodes can be synchronous functions or asynchronous functions.
If a node needs to await network I/O, stream tokens, or coordinate a batch of concurrent requests, making it `async def` is perfectly natural.
If a node is just formatting data or joining strings, a plain synchronous function is often simpler.

At the graph boundary, the current Python API gives you the async entry points you would expect.
Use `app.ainvoke(...)` when you want the final result asynchronously.
LangGraph also supports `app.astream(...)` when you want updates while the graph is still running, and in LangGraph v1.1 the streaming docs use `version="v2"` for that event format.
That is an important capability to know exists, but I will leave the full streaming walkthrough for a near-future post so we can keep this one focused on the async foundations.

LangGraph also has an opinionated tool story.
If the LLM is deciding which actions to take, `ToolNode` can execute multiple requested tools in parallel automatically.
That is very convenient, but it introduces the same shared-state problem discussed in [Concurrent Nodes in LangGraph]({{< relref "03-21-concurrent-nodes-in-langgraph" >}}).
When parallel branches or parallel tool calls write to the same key, you still need a reducer or you will lose data.

One more piece matters in production: persistence and durable execution.
If you compile a graph with checkpointing, LangGraph can resume or replay work.
That is powerful, but it means your side effects need clearer boundaries.
A node that charges a card, sends an email, or writes a record to an external system must be designed so a replay does not perform the same action twice by accident.
Async does not change that requirement.
It just makes it easier to hide the risky call inside a larger function if you are not careful.

## A Practical Async LangGraph Example

Let's build a small graph that gathers information from several URLs concurrently, then writes a short summary.
This is the kind of pattern where async fits LangGraph very naturally.
The graph is I/O-bound and each fetch is independent, so we can overlap the waiting time efficiently.

```python
import asyncio
from typing import TypedDict

import httpx
from langgraph.graph import START, END, StateGraph


class ResearchState(TypedDict):
    query: str
    urls: list[str]
    documents: list[str]
    summary: str


async def fetch_one(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    url: str,
) -> str:
    async with semaphore:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        text = response.text[:800]
        return f"Source: {url}\n{text}"


async def collect_documents(state: ResearchState) -> dict:
    semaphore = asyncio.Semaphore(3)

    async with httpx.AsyncClient() as client:
        documents = await asyncio.gather(
            *(fetch_one(client, semaphore, url) for url in state["urls"])
        )

    return {"documents": documents}


def write_summary(state: ResearchState) -> dict:
    combined = "\n\n".join(state["documents"])
    summary = (
        f"Research brief for {state['query']}:\n\n"
        f"{combined[:1200]}"
    )
    return {"summary": summary}


builder = StateGraph(ResearchState)
builder.add_node("collect_documents", collect_documents)
builder.add_node("write_summary", write_summary)
builder.add_edge(START, "collect_documents")
builder.add_edge("collect_documents", "write_summary")
builder.add_edge("write_summary", END)

app = builder.compile()
```

There are a few important details hiding in this short example.
The `collect_documents` node is async because it spends most of its time waiting on network I/O.
Inside that node we still use `asyncio.gather()` because LangGraph does not remove the need to structure concurrency within a node.
And we wrap the work in a semaphore because unbounded fan-out is still a fast route to timeouts and rate limits.

To run the graph asynchronously, call `ainvoke()` instead of `invoke()`:

```python
result = await app.ainvoke(
    {
        "query": "Latest LangGraph async guidance",
        "urls": [
            "https://docs.langchain.com/oss/python/langgraph/graph-api",
            "https://docs.langchain.com/oss/python/langgraph/durable-execution",
            "https://docs.langchain.com/oss/python/langchain/tools",
        ],
        "documents": [],
        "summary": "",
    }
)

print(result["summary"])
```

LangGraph also supports async streaming with `astream()`, which is especially useful when you want progress updates or token-level output.
That deserves its own treatment though, so I will cover it properly in the near future rather than squeezing it into this post.

Notice what we did not do here.
We did not use `ToolNode`, because the LLM is not choosing actions in this example.
The graph itself already knows it should fetch every URL in `state["urls"]`.
If the LLM needs to decide which lookups to perform, then the better fit is the tool-calling pattern from [Using Tools in LangGraph]({{< relref "03-14-using-tools-in-langgraph" >}}), ideally with async tools where the underlying work is also I/O-bound.

## Where Async Tools Fit

Async tools are useful when the model is making the choice, but the tool implementation is still network-heavy.
For example, an LLM might decide whether to call `search_docs`, `check_status_page`, or `lookup_pricing`.
If those tools talk to external services, defining them as async functions lets the runtime await them without blocking the event loop.

The important thing to remember is that `ToolNode` handling parallel tool execution does not remove state design concerns.
If two tools can update the same state field, define a reducer for that field.
Otherwise you risk the same silent overwrites that happen with any other parallel branch in LangGraph.

## Practical Mistakes to Avoid

- **Declaring a node async while still using blocking I/O:** `async def` is not magic.
  If the node calls `requests`, `time.sleep()`, or another blocking SDK, the graph still stalls.
- **Calling `invoke()` when you really want async behaviour:** `invoke()` is fine for synchronous runs, but if you want non-blocking graph execution, reach for `ainvoke()`.
- **Forgetting reducers on parallel updates:** this applies to fan-out branches and to parallel tool calls.
  If several concurrent paths write to one key, define how those values should be merged.
- **Launching too much work at once:** `asyncio.gather()` is easy to overuse.
  Add a semaphore or another limiter before you discover the API's rate limit the hard way.
- **Hiding side effects inside replayable nodes:** with persistence enabled, retries and resumes are features, not bugs.
  Keep external side effects idempotent or isolate them so replay does not create duplicates.

One short footnote is worth calling out.
If you are stuck on Python earlier than 3.11, LangGraph's async streaming docs currently require a bit more manual work around context propagation.
That is another good reason to prefer Python 3.11+ for new LangGraph projects.

## Wrapping Up

Async is a great fit for LangGraph when the workload is I/O-bound and the graph is structured clearly.
The fundamentals are still plain Python fundamentals: yield control, use async-native libraries, and limit concurrency intentionally.
LangGraph then adds the orchestration layer on top with async graph entry points, streamed progress, tool execution, reducers, and durable execution.

If you keep those layers separate in your head, the design becomes much easier.
Write sound async Python first.
Then use LangGraph to decide how that work should be coordinated, observed, and resumed.

If you want more from this series, browse the [LangGraph]({{< ref "/tags/langgraph" >}}) tag.
Happy coding!
