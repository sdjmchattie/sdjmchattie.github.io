---
date: 2026-03-14
title: "Using Tools in LangGraph"
description: |-
  LLMs know a lot, but on their own they cannot look up live data or run code.
  Learn how to give your LangGraph agents real capabilities by wiring in tools using ToolNode and MessagesState.
slug: using-tools-in-langgraph
image: /images/posts/2026/03-14-using-tools-in-langgraph.jpg
tags:
  - Python
  - LangGraph
  - Agentic AI
---

LLMs are impressive, but they are limited to the knowledge baked in at training time and can't take actions in the world on their own. Tools are what change that. By giving an LLM access to tools, you turn it from a static knowledge store into an agent that can look up live data, run calculations, call APIs, and more. In this post we will build a LangGraph agent that uses tools, and explore every piece of the pattern you will need.

This is part of a series of posts on LangGraph. If you are new to the series, start with [A Primer in LangGraph]({{< relref "10-18-a-primer-in-langgraph" >}}) which covers the basics, before working through the later posts.

## What Is a Tool?

In LangGraph, a tool is a Python function that the LLM can choose to call. You define the function, and LangGraph passes its name, description, and input schema to the LLM so it knows when and how to use it.

The simplest way to create a tool is with the `@tool` decorator from LangChain:

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # In a real app you would call a weather API here.
    return f"It is 18°C and cloudy in {city}."

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers and return the result."""
    return a * b
```

The docstring becomes the tool's description, which the LLM reads to understand what the tool does and when to use it. The type hints become the input schema. Both matter: a vague docstring leads to poor tool selection, and missing type hints break schema inference.

## MessagesState

Previous posts in this series used a custom `TypedDict` to hold graph state. Tool use requires a different approach because the LLM and tools need to exchange a sequence of messages: the user's question, the LLM's tool call request, the tool's result, and the LLM's final answer. LangGraph provides `MessagesState` for exactly this purpose.

```python
from langgraph.graph import MessagesState

# MessagesState is a TypedDict with a single key: messages.
# It uses a built-in reducer that appends new messages to the list
# rather than replacing the whole list on each state update.
```

You don't need to define this yourself. Import it and use it as the state type for any tool-calling graph. The append behaviour is essential: without it, each node would overwrite the conversation history instead of building on it.

## Binding Tools to the LLM

Before the LLM can use your tools, you need to tell it about them. Calling `bind_tools` on the LLM attaches the tool schemas so the model knows it can request them.

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0)
tools = [get_weather, multiply]
llm_with_tools = llm.bind_tools(tools)
```

When you invoke `llm_with_tools`, the response may include a `tool_calls` attribute listing the tools the LLM wants to call, along with the arguments it has chosen. If the LLM decides it doesn't need a tool, `tool_calls` will be empty and the response is already the final answer.

## The Agent Node

The agent node is a regular Python function that calls the LLM and returns the response. LangGraph appends the new message to the state's message list via the reducer mentioned above.

```python
def agent(state: MessagesState) -> dict:
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}
```

Note that the LLM receives the full message history every time this node runs. That history includes any tool results from previous iterations of the loop, which is how the LLM learns from what the tools returned before deciding its next move.

## ToolNode

`ToolNode` is a prebuilt node that handles everything on the tool execution side. You pass it your list of tools, and it reads the LLM's tool call requests from the last message, runs the matching tools, and returns a `ToolMessage` for each result.

```python
from langgraph.prebuilt import ToolNode

tool_node = ToolNode(tools)
```

If the LLM requests multiple tools in one response, `ToolNode` runs them in parallel automatically. You can also tell it to handle errors gracefully instead of crashing the graph:

```python
tool_node = ToolNode(tools, handle_tool_errors=True)
```

With error handling enabled, if a tool raises an exception, the error is returned to the LLM as a message so it can decide what to do next, rather than the whole run failing.

## Routing with tools_condition

After the agent node runs we need to decide whether to execute tools or end the graph. LangGraph ships a prebuilt routing function called `tools_condition` that does exactly this. It checks whether the last message contains tool calls and routes accordingly.

```python
from langgraph.prebuilt import tools_condition
```

`tools_condition` returns `"tools"` when the last message has tool calls, and `END` when it does not. This is the same conditional edge pattern from the [flow control post]({{< relref "10-25-flow-control-in-langgraph" >}}), just without needing to write the routing function yourself.

## Wiring the Loop

Here is the full graph. The key difference from earlier posts in this series is the loop: after tools execute, the graph routes back to the agent so the LLM can see the results and decide what to do next.

```python
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"It is 18°C and cloudy in {city}."

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers and return the result."""
    return a * b

llm = ChatOpenAI(model="gpt-4o", temperature=0)
tools = [get_weather, multiply]
llm_with_tools = llm.bind_tools(tools)

def agent(state: MessagesState) -> dict:
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

graph = StateGraph(MessagesState)

graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools, handle_tool_errors=True))

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")

app = graph.compile()
```

The flow looks like this:

```text
START
  ↓
agent ──── no tool calls ──→ END
  ↑               ↓
  └──── tools ←── tool calls
```

The loop continues until the LLM is satisfied it has enough information to respond without calling any more tools.

## Running It

Invoke the graph with a `HumanMessage` to kick things off. The LLM will decide which tools to call, the results will feed back into the conversation, and the final message will be the LLM's composed answer once it no longer needs tools.

```python
from langchain_core.messages import HumanMessage

result = app.invoke({
    "messages": [
        HumanMessage(content="What is 6 times 7, and what is the weather in Edinburgh?")
    ]
})

print(result["messages"][-1].content)
```

The LLM will call `multiply` and `get_weather`, receive the results, and compose a natural language answer using both. You can inspect the full `result["messages"]` list to see every step: the initial question, the tool call requests, the tool results, and the final answer.

## Wrapping Up

You now have a working tool-calling agent in LangGraph. The core pattern is:

- Define tools with `@tool`, keeping docstrings accurate and type hints present.
- Use `MessagesState` so the full conversation history is available to the LLM and tools.
- Bind tools to the LLM with `bind_tools` before building the agent node.
- Use `ToolNode` to handle execution, parallel calls, and optionally errors gracefully.
- Use `tools_condition` and a loop edge to let the LLM call tools as many times as it needs.

If you want a quick start without wiring the graph manually, LangGraph's `create_react_agent` helper builds the same structure in a single line. But understanding each piece means you can extend it, add human-in-the-loop steps like those covered in the [human feedback post]({{< relref "11-29-human-feedback-in-langgraph" >}}), or swap in custom routing logic as your needs grow.

Browse the [LangGraph]({{< ref "/tags/langgraph" >}}) tag for more posts in this series. Happy coding!
