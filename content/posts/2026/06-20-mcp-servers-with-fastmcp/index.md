---
date: 2026-06-20
title: "Building Agentic System Tools with FastMCP and Python"
description: |-
  Model Context Protocol (MCP) is revolutionizing how LLM agents interact with local environments and tools.
  In this guide, I explore FastMCP, a high-level framework that makes building MCP servers in Python incredibly fast.
  Learn how to expose tools, resources, and dynamic prompts to your AI assistant with minimal boilerplate.
slug: mcp-servers-with-fastmcp
image: /images/posts/2026/06-20-mcp-servers-with-fastmcp.jpg
tags:
  - Python
  - MCP
  - Agentic Workflows
---

If you have spent any time building agentic systems recently, you have likely encountered the integration bottleneck.
Connecting large language models (LLMs) to local tools, internal databases, or system utilities has historically meant writing custom APIs for every single integration.
This fragmentation makes agentic workflows fragile and difficult to scale.

Enter the Model Context Protocol (MCP), an open standard developed to serve as the universal "USB-C port" for AI agents.
Instead of building custom pipes for each tool, MCP provides a standard way for clients to discover and execute capabilities.
To make building these servers as fast and Pythonic as possible, the high-level framework FastMCP was created.
I'll show you how you can use FastMCP to turn standard Python functions into powerful tools for your AI assistant.

## The Magic of Python Type Hints and Decorators

Before you write any code, it is worth understanding the design philosophy that makes FastMCP so elegant.
At its core, FastMCP leverages modern Python type hints and function decorators to automate the hardest parts of API design.
If you have used FastAPI or Flask, this pattern will feel instantly familiar.

### Understanding how schemas are auto-generated

Normally, describing a tool to an LLM requires writing complex JSON schemas specifying parameter names, types, and descriptions.
With FastMCP, you simply write a standard Python function and decorate it.
FastMCP inspects your function's type hints (like `a: int`) and parses the docstring to dynamically build the JSON-RPC schemas.
This means your code remains clean, readable, and self-documenting.

## Setting Up Your First Server

To get started, you will need to install the FastMCP library.
I recommend using `uv`, the fast Python package manager, to manage your dependencies.

To install FastMCP:

```bash
uv pip install fastmcp
```

Once installed, creating a server is as simple as importing the library and creating an instance of the `FastMCP` class.
You'll create a file named `server.py` and set up the foundation.

```python
from fastmcp import FastMCP

# Initialize a new server instance
mcp = FastMCP("Developer Helper")
```

With this single instance, you're ready to register tools, resources, and prompts.

## Feature 1: Exposing Tools with Ease

Tools are executable functions that the LLM agent can call to perform actions or run computations.
In FastMCP, registering a tool is as simple as adding the `@mcp.tool()` decorator to a function.

You'll write a simple tool to add two numbers together.

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together.

    Args:
        a: The first number.
        b: The second number.
    """
    return a + b
```

When an LLM client connects to your server, FastMCP exposes this function as an available tool.
The client's model will read the docstring and arguments, understand what the tool does, and generate the correct parameters to call it.
FastMCP handles the underlying JSON-RPC communication and execution automatically.

## Feature 2: Sharing Static Resources

Resources are readable data sources that act similarly to `GET` endpoints in traditional web APIs.
Unlike tools, which perform active operations, resources allow the LLM to read raw files, system configurations, or real-time statuses.

You'll register a simple static resource to expose the server's configuration status.

```python
@mcp.resource("config://status")
def get_status() -> str:
    """Retrieve the current server system status."""
    return "System status: Online | Services: Healthy"
```

The resource path uses a custom URI scheme (`config://status`), allowing the client to request this specific address to retrieve the raw string.

## Feature 3: Designing Reusable Prompts

Prompts are predefined, parameterized templates that help guide how the LLM interacts with the user.
They are excellent for creating standard diagnostic helpers, code reviewers, or specialized agent personas.

You'll define a dynamic greeting template.

```python
@mcp.prompt()
def greet_developer(name: str) -> str:
    """Generate a helpful welcome prompt for a developer.

    Args:
        name: The name of the developer.
    """
    return f"Hello, {name}! I am your system assistant. How can I help you debug your code today?"
```

This registers a template that the client can request, filling in the `name` argument dynamically to seed the conversation.

## Going Deeper with the Context Object

For real-world agentic workflows, your tools will often perform operations that take time or require logging.
FastMCP provides a powerful **`Context`** utility that can be dynamically injected into any of your functions.
By adding a parameter type-annotated with `Context`, you gain access to rich session capabilities.

You'll build a tool that demonstrates logging and progress reporting.

```python
import asyncio
from fastmcp import Context

@mcp.tool()
async def process_task(ctx: Context) -> str:
    """Simulate a multi-step task with progress reporting and logging."""
    await ctx.info("Initializing background task...")
    
    total_steps = 3
    for step in range(1, total_steps + 1):
        await asyncio.sleep(1)  # Simulate active work
        await ctx.report_progress(step, total_steps, f"Step {step} of {total_steps} complete")
        await ctx.info(f"Finished step {step}")
        
    await ctx.info("Task completed successfully!")
    return "All processing steps finished."
```

Notice that because `Context` operations are asynchronous, you'll define the tool as an `async def`.
FastMCP automatically detects this and executes it within the server's async loop, sending real-time progress updates back to the LLM client so it never appears "hung".

## Testing and Debugging Your Server

One of the best parts of the FastMCP developer experience is its built-in tooling.
You do not need to set up a complex LLM client just to test your server.
FastMCP comes with a CLI that launches the interactive **MCP Inspector** web interface.

To start your server in development mode:

```bash
fastmcp dev server.py
```

This will run your server and automatically open a web browser pointing to `http://127.0.0.1:6274`.
From this dashboard, you can view your generated schemas, interactively trigger your tools, inspect resource contents, and test prompt templates in real-time.

Additionally, to quickly audit your server's metadata and schemas from the terminal, you can run:

```bash
fastmcp inspect server.py
```

This will print a clean summary of every tool, resource, and prompt you have registered.

## Wrapping Up

Building custom integrations for AI agents does not have to be painful.
FastMCP abstracts away the low-level complexities of the Model Context Protocol, letting you build robust tools in pure Python.
By letting you focus on your business logic, it turns any standard library or internal utility into an agent-ready service in minutes.

Happy coding!
