---
date: 2026-07-04
title: "Connecting LangGraph Agents to FastMCP Servers"
description: |-
  Building custom tool bindings for AI agents can be incredibly tedious.
  In this guide, I show you how to connect a LangGraph agent to a FastMCP server to create a robust, multi-step filesystem analysis system.
  Learn how to standardize tool access and simplify orchestrator workflows with the Model Context Protocol.
slug: langgraph-agents-with-fastmcp
image: /images/posts/2026/07-04-langgraph-agents-with-fastmcp.jpg
tags:
  - Python
  - MCP
  - LangGraph
  - Agentic Workflows
---

Connecting large language models (LLMs) to local tools and system resources has historically required a lot of custom integration work.
This friction makes agentic systems difficult to scale and maintain.
Fortunately, the Model Context Protocol (MCP) provides a standard way to expose tools, resources, and prompts to your AI assistant.
In my previous post, [Building Agentic System Tools with FastMCP and Python]({{< ref "06-20-mcp-servers-with-fastmcp" >}}), I explored how easy it is to expose system capabilities using FastMCP.
Now, I'll guide you through the process of connecting a custom LangGraph agent directly to a FastMCP server.
You'll see how to leverage these standardized capabilities to execute complex, multi-step filesystem analysis tasks.

## The Power of Standardized Tool Contracts

Before you dive into the implementation, it is worth considering why separating tool hosting from your orchestration framework is a game-changer.
Normally, when you write tools for a LangGraph agent, you bind them directly to the LangChain or LangGraph ecosystem.
This couples your business logic tightly to a single orchestrator framework.
By hosting tools on a FastMCP server instead, you create a standard, reusable endpoint.
Any agent client that implements the open MCP specification can discover and execute these tools instantly.
This separation of concerns makes your tools highly portable and your agent state machine much cleaner.

## The Core System Scenario

To make this integration practical, you'll build a filesystem auditor agent.
Your agent must solve a multi-step problem that requires reading static configuration, gathering local metrics, and performing calculations.
Specifically, the agent needs to:
1. Query a server configuration resource to discover which local folders on your system need auditing.
2. Query a folder-sizing tool to inspect each directory's total size in bytes.
3. Query a summation tool to calculate the collective storage footprint.
4. Compile a human-readable storage summary report.

To achieve this, you'll build a FastMCP server that hosts these resources and tools, and a LangGraph client that orchestrates the execution.

## Part 1: Building the FastMCP Server

First, you'll build the tool server.
Create a new file named `server.py` in your development directory.
You'll import `FastMCP` and register your folders configuration resource, filesystem checker tool, and calculation utility.

```python
import os
import json
from fastmcp import FastMCP

# Initialize a clean FastMCP server instance
mcp = FastMCP("Folder Auditor")

# Register a static resource returning target directories
@mcp.resource("config://folders")
def get_target_folders() -> str:
    """Retrieve the list of target folders to audit."""
    return json.dumps(["./documents", "./downloads", "./desktop"])

# Register a tool to calculate a specific folder's size
@mcp.tool()
def get_folder_size(path: str) -> int:
    """Calculate the total size of a specified folder in bytes.

    Args:
        path: The relative or absolute path of the directory.
    """
    resolved = os.path.abspath(path)
    if not os.path.exists(resolved):
        return 0
        
    total_size = 0
    try:
        for dirpath, _, filenames in os.walk(resolved):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
    except Exception:
        pass
        
    return total_size

# Register a simple calculation tool to sum the values
@mcp.tool()
def sum_values(values: list[int]) -> int:
    """Add together a list of integers to get the total sum.

    Args:
        values: A list of sizes in bytes.
    """
    return sum(values)
```

In this setup, you use the `@mcp.resource` decorator to expose a config endpoint.
You also use the `@mcp.tool` decorator to register functions that inspect the drive and perform mathematical summing.
FastMCP inspects these type hints and docstrings to automatically generate standard JSON-RPC tool schemas.

## Part 2: Connecting the Stdio Bridge

Now that your server is ready, you need to connect your LangGraph client to it.
MCP clients talk to local servers using standard input/output (`stdio`) pipelines.
In your client script, you'll launch the server as a background subprocess.
You can configure this using Python's official `mcp` SDK.

Create a file named `agent.py` and set up the stdio bridge.

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Define parameters to launch the FastMCP server
server_params = StdioServerParameters(
    command="uv",
    args=["run", "server.py"],
    env=None
)
```

This configuration tells the client to execute your server code inside a virtual environment using `uv`.
You are now ready to establish the connection and discover the server capabilities dynamically.

## Part 3: Dynamically Mapping MCP Tools to LangChain

Before your LangGraph agent can use the MCP tools, you need to map them to LangChain's tool structure.
While there are community wrappers available, writing a lightweight, custom translation function is highly educational.
It keeps your code self-contained and avoids brittle dependency version mismatches.

You'll add this mapping helper to `agent.py`.

```python
from langchain_core.tools import StructuredTool

def make_langchain_tool(mcp_tool, session: ClientSession) -> StructuredTool:
    """Wrap an MCP tool into a LangChain StructuredTool dynamically."""
    name = mcp_tool.name
    description = mcp_tool.description
    
    # Define an async coroutine wrapper to execute the RPC call
    async def _coroutine(**kwargs):
        response = await session.call_tool(name, arguments=kwargs)
        if response.isError:
            raise ValueError(f"Tool execution failed: {response.content}")
        return response.content[0].text
        
    return StructuredTool.from_function(
        name=name,
        description=description,
        coroutine=_coroutine
    )
```

This helper reads the registered MCP tool details.
It then creates a standard `StructuredTool` that forwards arguments back to your background server session whenever the agent triggers it.

## Part 4: Designing the Custom LangGraph State Machine

With your tools mapped, you can now structure the agent orchestration flow.
You'll construct a custom `StateGraph` consisting of an agent node, a tool execution node, and a router.

Add the following LangGraph orchestration code to `agent.py`.

```python
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END

# Define our agent state structure
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# Define the node that calls the model
def make_agent_node(model, tools):
    bound_model = model.bind_tools(tools)
    
    async def agent_node(state: AgentState):
        response = await bound_model.ainvoke(state["messages"])
        return {"messages": [response]}
        
    return agent_node

# Define the node that executes our MCP tools
def make_tools_node(tool_map):
    async def tools_node(state: AgentState):
        last_message = state["messages"][-1]
        tool_outputs = []
        
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Execute the custom wrapped MCP tool
            target_tool = tool_map[tool_name]
            output = await target_tool.ainvoke(tool_args)
            
            tool_outputs.append(
                ToolMessage(
                    content=str(output),
                    tool_call_id=tool_call["id"],
                    name=tool_name
                )
            )
        return {"messages": tool_outputs}
        
    return tools_node

# Router logic to determine next step
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END
```

This architecture gives you complete control over the execution flow.
Your agent node evaluates the message history, decides which capabilities to call, and delegates the work to your custom tools node.

## Part 5: Running the End-to-End Workflow

You are now ready to assemble the components into a single executable application.
You'll set up a system prompt that guides the LLM to use both resources and tools.
You'll also configure the runtime loop inside `agent.py`.

```python
async def run_agent():
    # Start the background subprocess connection
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize our MCP session
            await session.initialize()
            
            # Read our target static folders config resource
            folders_resource = await session.read_resource("config://folders")
            folders_list = folders_resource.contents[0].text
            
            # Dynamically fetch tools from the FastMCP server
            mcp_tools = await session.list_tools()
            tool_map = {}
            for t in mcp_tools.tools:
                tool_map[t.name] = make_langchain_tool(t, session)
                
            # Initialize the model and build the state graph
            model = ChatOpenAI(model="gpt-4o", temperature=0)
            
            workflow = StateGraph(AgentState)
            workflow.add_node("agent", make_agent_node(model, list(tool_map.values())))
            workflow.add_node("tools", make_tools_node(tool_map))
            
            workflow.add_edge(START, "agent")
            workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
            workflow.add_edge("tools", "agent")
            
            app = workflow.compile()
            
            # Seed our agent with instructions and folders configuration
            sys_message = (
                "You are a filesystem storage auditor.\n"
                "Your objective is to scan the target folders listed in the context, "
                "query their individual sizes, and sum them to compile a report.\n"
                f"Target configuration: {folders_list}"
            )
            
            inputs = {
                "messages": [
                    HumanMessage(content=sys_message),
                    HumanMessage(content="Calculate the total size of the folders.")
                ]
            }
            
            # Stream the execution steps
            async for step in app.astream(inputs):
                for node_name, state in step.items():
                    print(f"\n--- Node: {node_name} ---")
                    last_msg = state["messages"][-1]
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        print(f"Tool Calls: {last_msg.tool_calls}")
                    else:
                        print(f"Content: {last_msg.content}")

if __name__ == "__main__":
    asyncio.run(run_agent())
```

When you execute this script, you'll observe a beautiful orchestrator execution sequence:
1. The client establishes the stdio channel with your background `server.py`.
2. The client fetches the static resource `config://folders` to read the configuration.
3. The client lists and maps the available server tools (`get_folder_size` and `sum_values`).
4. The LangGraph agent receives the instructions and schedules tool calls for `./documents`, `./downloads`, and `./desktop` in parallel.
5. Once the size inputs are returned from the tools node, the agent triggers `sum_values` to aggregate the measurements.
6. The agent writes a clean final report for you summarizing the storage distribution.

## The Complete agent.py Script

To make it as easy as possible to follow how all of these components connect, here is the complete, unified `agent.py` script.
This consolidates all the import statements and modules into a single, runnable file.

```python
import asyncio
import operator
from typing import TypedDict, Annotated, Sequence

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langgraph.graph import StateGraph, START, END

# Define parameters to launch the FastMCP server
server_params = StdioServerParameters(
    command="uv",
    args=["run", "server.py"],
    env=None
)

def make_langchain_tool(mcp_tool, session: ClientSession) -> StructuredTool:
    """Wrap an MCP tool into a LangChain StructuredTool dynamically."""
    name = mcp_tool.name
    description = mcp_tool.description
    
    # Define an async coroutine wrapper to execute the RPC call
    async def _coroutine(**kwargs):
        response = await session.call_tool(name, arguments=kwargs)
        if response.isError:
            raise ValueError(f"Tool execution failed: {response.content}")
        return response.content[0].text
        
    return StructuredTool.from_function(
        name=name,
        description=description,
        coroutine=_coroutine
    )

# Define our agent state structure
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# Define the node that calls the model
def make_agent_node(model, tools):
    bound_model = model.bind_tools(tools)
    
    async def agent_node(state: AgentState):
        response = await bound_model.ainvoke(state["messages"])
        return {"messages": [response]}
        
    return agent_node

# Define the node that executes our MCP tools
def make_tools_node(tool_map):
    async def tools_node(state: AgentState):
        last_message = state["messages"][-1]
        tool_outputs = []
        
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Execute the custom wrapped MCP tool
            target_tool = tool_map[tool_name]
            output = await target_tool.ainvoke(tool_args)
            
            tool_outputs.append(
                ToolMessage(
                    content=str(output),
                    tool_call_id=tool_call["id"],
                    name=tool_name
                )
            )
        return {"messages": tool_outputs}
        
    return tools_node

# Router logic to determine next step
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

async def run_agent():
    # Start the background subprocess connection
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize our MCP session
            await session.initialize()
            
            # Read our target static folders config resource
            folders_resource = await session.read_resource("config://folders")
            folders_list = folders_resource.contents[0].text
            
            # Dynamically fetch tools from the FastMCP server
            mcp_tools = await session.list_tools()
            tool_map = {}
            for t in mcp_tools.tools:
                tool_map[t.name] = make_langchain_tool(t, session)
                
            # Initialize the model and build the state graph
            model = ChatOpenAI(model="gpt-4o", temperature=0)
            
            workflow = StateGraph(AgentState)
            workflow.add_node("agent", make_agent_node(model, list(tool_map.values())))
            workflow.add_node("tools", make_tools_node(tool_map))
            
            workflow.add_edge(START, "agent")
            workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
            workflow.add_edge("tools", "agent")
            
            app = workflow.compile()
            
            # Seed our agent with instructions and folders configuration
            sys_message = (
                "You are a filesystem storage auditor.\n"
                "Your objective is to scan the target folders listed in the context, "
                "query their individual sizes, and sum them to compile a report.\n"
                f"Target configuration: {folders_list}"
            )
            
            inputs = {
                "messages": [
                    HumanMessage(content=sys_message),
                    HumanMessage(content="Calculate the total size of the folders.")
                ]
            }
            
            # Stream the execution steps
            async for step in app.astream(inputs):
                for node_name, state in step.items():
                    print(f"\n--- Node: {node_name} ---")
                    last_msg = state["messages"][-1]
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        print(f"Tool Calls: {last_msg.tool_calls}")
                    else:
                        print(f"Content: {last_msg.content}")

if __name__ == "__main__":
    asyncio.run(run_agent())
```

To run your complete integration:

```bash
uv run agent.py
```

## Wrapping Up

Decoupling your tools from your core agent code using FastMCP makes your architecture remarkably modular.
By standardizing tool exposure via standard input/output protocols, you ensure that your capabilities remain generic and easily reusable.
This allows you to focus on building complex orchestration graphs in LangGraph, while keeping your business systems clean and maintainable.

Happy coding!
