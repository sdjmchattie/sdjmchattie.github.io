---
date: 2026-05-16
title: "Streaming State and Tokens in LangGraph"
description: |-
  Waiting for a complete graph execution can ruin the user experience in agentic applications.
  This post shows how to use LangGraph's streaming functions to yield state updates and LLM tokens as they happen.
slug: streaming-in-langgraph
image: /images/posts/2026/05-16-streaming-in-langgraph.jpg
tags:
  - Python
  - LangGraph
  - Agentic AI
  - Software Architecture
---

Waiting for an agent to finish a complex task can feel like staring at a frozen progress bar.
If your LangGraph application just uses `.invoke()`, your user sees nothing until the entire graph completes.
That is fine for background jobs, but it is a terrible experience for interactive applications.
LangGraph solves this problem by letting you stream the execution as it happens.
Instead of waiting for the final state, you can watch the graph work node by node or even word by word.

## Using stream Over invoke

The easiest way to make a graph feel dynamic is to replace `.invoke()` with `.stream()`.
When you invoke a graph, you pass in the initial state and get back the final state.
When you stream a graph, it yields updates as an iterator.
If you need asynchronous execution, the same principles apply using `.astream()` instead, as we discussed in [Using Async Effectively in LangGraph]({{< relref "05-02-async-in-langgraph" >}}).
For this post, we will stick to the synchronous `.stream()` method to keep the focus on the streaming concepts themselves.

## Understanding Streaming Modes

LangGraph supports four distinct streaming modes: `values`, `updates`, `messages`, and `events`.
You can pass any of these as the `stream_mode` argument to control what the graph yields.
While you should know they all exist, you will mostly rely on `updates` and `messages` to make your applications responsive.

The `updates` mode is the default and yields the exact state changes returned by each node.
This is perfect for showing the user which step the agent is currently working on.
The `messages` mode goes a layer deeper and yields partial message chunks as the LLM generates them.
If you want that classic ChatGPT typing effect, `messages` is the mode you need.

The `values` mode yields the entire state of the graph after every node completes, which can be useful for debugging but is often too heavy for production.
The `events` mode provides deep, LangChain-level callback events, which is powerful but usually overkill unless you are building a complex observability tool.

## An Example of State Updates

Let us look at a simple graph that researches a topic and writes a summary.
If we use `.invoke()`, the user waits in silence while the agent searches the web and writes the draft.
If we use `.stream()` with the default `updates` mode, we can tell the user exactly what is happening.

```python
for update in app.stream({"query": "LangGraph streaming modes"}):
    for node_name, state_change in update.items():
        print(f"Update from node '{node_name}':")
        print(state_change)
```

In this example, the loop yields a dictionary every time a node finishes.
The key is the name of the node, and the value is the state update it returned.
You can use this to update a user interface, showing a spinner that states "Searching the web" when the research node runs, and "Drafting summary" when the writer node takes over.
This simple change transforms a slow, silent process into an engaging, transparent workflow.

## A Note on the V2 API

If you dive deeper into streaming, you will likely encounter `astream_events()` for fine-grained token streaming.
When you use that method, you should always pass `version="v2"` as an argument.
The v2 streaming API is the current standard and provides a much more consistent event structure than the older v1 API.

If you find yourself maintaining a legacy codebase that still uses the v1 API, migrating is straightforward.
First, update the argument to `version="v2"` in your streaming call.
Then, update your event handlers because the v2 API yields `(event, data)` tuples rather than flat dictionaries.
Finally, check that your token accumulation logic handles the new chunk format correctly.
Once you make those changes, your application will be on the modern standard.

## Wrapping Up

Streaming is not just a nice addition to LangGraph applications.
It is an essential pattern for building agents that feel responsive and alive.
By switching from `.invoke()` to `.stream()`, and choosing the right streaming mode for your needs, you can keep your users informed and engaged even during the longest operations.

If you want more from this series, browse the [LangGraph]({{< ref "/tags/langgraph" >}}) tag.
Happy coding!
