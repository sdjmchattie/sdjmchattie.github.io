---
date: 2026-05-16
title: "Streaming State and Tokens in LangGraph"
description: |-
  Waiting for a complete graph execution can ruin the user experience in agentic applications.
  This post shows how to use LangGraph's streaming functions to yield state updates and LLM tokens as they happen, covering the updates, messages, and custom streaming modes with practical examples.
slug: streaming-in-langgraph
image: /images/posts/2026/05-16-streaming-in-langgraph.jpg
tags:
  - Python
  - LangGraph
  - Agentic AI
  - Software Architecture
---

If you have been following the earlier posts in this series, you will have built graphs that gather data, call tools, and produce structured output.
Every one of those examples used `.invoke()`, which means the caller waits in silence until the entire graph finishes and then receives the final state.
That is fine for batch jobs or background pipelines, but it is a terrible experience for anything interactive.
A user watching a chatbot stare blankly for fifteen seconds while it researches, reasons, and writes is a user wondering whether the application has crashed.

LangGraph solves this with streaming.
Instead of waiting for the final result, you can watch the graph work as it happens: node by node, or even word by word.
This post walks through the streaming modes that matter most and shows how to use each one with practical code.

This is part of a series of posts on LangGraph.
If you are new to the series, start with [A Primer in LangGraph]({{< relref "10-18-a-primer-in-langgraph" >}}) which covers the basics, before working through the later posts.
All streaming examples use the synchronous `.stream()` method to keep things focused.
If you need asynchronous execution, the same principles apply using `.astream()` instead, as covered in [Using Async Effectively in LangGraph]({{< relref "05-02-async-in-langgraph" >}}).

## The Example Graph

To keep things concrete, every example in this post uses the same small graph.
It has two nodes: one that researches a topic by calling an LLM, and one that writes a summary based on the research.

```python
from typing import Annotated, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph


class ResearchState(TypedDict):
    topic: str
    research: str
    summary: str


llm = ChatOpenAI(model="gpt-4o", streaming=True)


def research_topic(state: ResearchState) -> dict:
    prompt = f"Research the following topic in detail: {state['topic']}"
    response = llm.invoke(prompt)
    return {"research": response.content}


def write_summary(state: ResearchState) -> dict:
    prompt = (
        f"Write a concise summary of this research:\n\n{state['research']}"
    )
    response = llm.invoke(prompt)
    return {"summary": response.content}


builder = StateGraph(ResearchState)
builder.add_node("research_topic", research_topic)
builder.add_node("write_summary", write_summary)
builder.add_edge(START, "research_topic")
builder.add_edge("research_topic", "write_summary")
builder.add_edge("write_summary", END)

app = builder.compile()
```

Notice that the LLM is initialised with `streaming=True`.
That flag tells the model provider to send tokens incrementally rather than waiting for the full response.
It does not change how `invoke()` behaves at the graph level, but it is essential for the `messages` streaming mode we will use later.

If you call `app.invoke({"topic": "LangGraph streaming"})`, you get back the completed state with both `research` and `summary` filled in.
Nothing appears until the entire graph finishes.
The rest of this post replaces that single call with `.stream()` and explores what each streaming mode gives you.

## The Streaming Modes

LangGraph supports several streaming modes that you select by passing `stream_mode` to `.stream()`.
The three you will use most often are `updates`, `messages`, and `custom`.
There are also modes called `values`, `debug`, and others, but these three cover the vast majority of real applications.

Here is a quick summary before we dive into each one.

- **`updates`**: yields the state changes produced by each node as it finishes.
- **`messages`**: yields LLM tokens one at a time as the model generates them.
- **`custom`**: yields arbitrary data that you emit explicitly from inside your nodes.

## Streaming State Updates

The `updates` mode is the default.
When you call `.stream()` without specifying a mode, this is what you get.
Each time a node finishes executing, the stream yields a dictionary where the key is the node name and the value is the state update that node returned.

```python
for chunk in app.stream(
    {"topic": "LangGraph streaming"},
    stream_mode="updates",
):
    for node_name, state_update in chunk.items():
        print(f"--- Node '{node_name}' finished ---")
        for key, value in state_update.items():
            preview = value[:120] + "..." if len(value) > 120 else value
            print(f"  {key}: {preview}")
        print()
```

Running this, you would see something like:

```
--- Node 'research_topic' finished ---
  research: LangGraph is a framework built on top of LangChain that enables developers to create stateful, multi-actor ...

--- Node 'write_summary' finished ---
  summary: LangGraph provides a graph-based orchestration layer for building agentic AI applications. It extends ...
```

This mode is ideal for building progress indicators.
If your graph has five nodes, you can show the user which step is currently running and update a progress bar each time one completes.
In a web application, you could push each update over a WebSocket or server-sent event stream so the frontend stays in sync with the backend.

The `values` mode is similar but heavier.
Instead of yielding just the changes from each node, it yields the entire state snapshot after every step.
That can be useful for debugging because you can see exactly what state looks like at each point, but it generates a lot more data and is usually unnecessary in production.

## Streaming LLM Tokens

The `messages` mode goes a layer deeper than node-level updates.
Instead of waiting for a node to finish, it yields individual tokens as the LLM generates them.
This is what you need for that familiar ChatGPT typing effect where words appear one at a time.

```python
for message_chunk, metadata in app.stream(
    {"topic": "LangGraph streaming"},
    stream_mode="messages",
):
    if metadata["langgraph_node"] == "write_summary" and message_chunk.content:
        print(message_chunk.content, end="", flush=True)
```

There are a few important details in this short example.

First, the stream yields a tuple of `(message_chunk, metadata)` rather than a plain dictionary.
The `message_chunk` is an `AIMessageChunk` object whose `.content` attribute holds the text fragment.
The `metadata` dictionary tells you which node produced the token via the `langgraph_node` key, plus other context like the LLM invocation ID.

Second, we filter on `metadata["langgraph_node"]` to only print tokens from the `write_summary` node.
Without this filter, you would see tokens from both the research node and the summary node interleaved in the output.
In a real application, you might want to show research tokens in a collapsible panel and summary tokens in the main chat area.

Third, we check `message_chunk.content` because the stream occasionally emits metadata chunks with empty content.
Skipping those avoids printing blank lines.

This mode only works when the underlying LLM is configured for streaming.
If you forget to pass `streaming=True` when initialising the model, the LLM will generate the entire response internally and then emit it as a single chunk, which defeats the purpose entirely.

## Emitting Custom Data

The `custom` mode is the most flexible.
It lets you emit whatever data you want from inside a node using `get_stream_writer()`.
This is useful when you need progress updates that do not map neatly to state changes or LLM tokens: status messages, percentage progress, intermediate calculations, or any other signal that your frontend needs.

Here is a modified version of the research node that emits status updates as it works:

```python
from langgraph.config import get_stream_writer


def research_topic(state: ResearchState) -> dict:
    writer = get_stream_writer()

    writer({"status": "Starting research", "node": "research_topic"})

    prompt = f"Research the following topic in detail: {state['topic']}"
    response = llm.invoke(prompt)

    writer({"status": "Research complete", "node": "research_topic"})

    return {"research": response.content}
```

To receive these events, pass `stream_mode="custom"`:

```python
for chunk in app.stream(
    {"topic": "LangGraph streaming"},
    stream_mode="custom",
):
    print(f"[{chunk['node']}] {chunk['status']}")
```

The writer accepts any JSON-serialisable data, so you can structure the events however your application needs.
You could emit progress percentages, lists of URLs being fetched, or partial results that the frontend renders incrementally.

One thing to be aware of is that `get_stream_writer()` depends on the LangGraph execution context.
If you call the node function directly in a test without running it through the graph, the writer call will raise an error.
A simple `try`/`except` around the writer calls lets you support both standalone testing and graph-based execution.

## Combining Multiple Modes

You are not limited to a single streaming mode.
If you pass a list to `stream_mode`, LangGraph interleaves all of the requested event types in a single stream.
This is powerful because a real application often needs both state updates and custom progress events, or both token streaming and node-level progress.

```python
for event in app.stream(
    {"topic": "LangGraph streaming"},
    stream_mode=["updates", "custom"],
):
    if event["type"] == "updates":
        node_name = list(event["data"].keys())[0]
        print(f"Node '{node_name}' completed")
    elif event["type"] == "custom":
        print(f"Status: {event['data']['status']}")
```

When using multiple modes, each event arrives as a dictionary with a `type` field that tells you which mode produced it and a `data` field containing the payload.
This makes it straightforward to dispatch events to different handlers in your application.

## A Note on the V2 Streaming API

If you explore the LangGraph documentation, you will encounter references to `astream_events()`, which is a lower-level API that emits fine-grained callback events for the entire execution lifecycle.
When using that method, always pass `version="v2"`.
The v2 event format is the current standard and provides a much more consistent structure than the older v1 format.

For most applications, the `stream_mode` approach covered in this post is cleaner and easier to work with.
The `astream_events()` API is worth reaching for when you need deep observability, such as building a custom tracing dashboard or monitoring tool that needs to see every internal event.

If you inherit a codebase using the v1 event format, migrating is straightforward.
Update the `version` argument to `"v2"`, adjust your event handlers to expect the new tuple structure rather than flat dictionaries, and verify that any token accumulation logic handles the updated chunk format.

## Choosing the Right Mode

The right streaming mode depends on what your application is doing with the output.

If you are building a dashboard or progress tracker that shows which step the agent is working on, `updates` gives you exactly what you need with minimal complexity.
Each node completion becomes a progress tick.

If you are building a chat interface where users watch the response appear word by word, `messages` is the right choice.
Filter by node name to control which part of the graph streams to the user.

If you need to send custom signals, such as status messages, progress percentages, or intermediate results that do not belong in the graph state, `custom` with `get_stream_writer()` gives you full control.

And if you need more than one of these at the same time, pass them as a list.
A chat interface might combine `messages` for token streaming with `custom` for status indicators, giving the frontend everything it needs from a single event loop.

## Wrapping Up

Streaming transforms a LangGraph application from something that disappears for seconds at a time into something that feels responsive and alive.
The `updates` mode shows the user which step is running.
The `messages` mode delivers the classic typing effect.
The `custom` mode lets you emit whatever your frontend needs.
And combining them gives you a single stream of everything.

If you are building anything interactive with LangGraph, streaming is not optional.
It is the difference between an application that feels broken while it thinks and one that feels like it is working with you.

If you want more from this series, browse the [LangGraph]({{< ref "/tags/langgraph" >}}) tag.
Happy coding!
