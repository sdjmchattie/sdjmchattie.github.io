---
title: "Python's Hidden Gems: Packages and Patterns"
date: 2026-08-15
description: |-
  Discover lesser-known but incredibly useful Python packages like Loguru and diskcache.
  Learn modern design patterns including structural matching and memory optimisation techniques.
slug: "python-hidden-gems"
image: "/images/posts/2026/08-15-python-hidden-gems.png"
tags:
  - "Python"
---

{{< tldr >}}
Beyond mainstream packages like [Pandas](https://pandas.pydata.org/) and [Requests](https://requests.readthedocs.io/), Python boasts a rich collection of high-leverage utility libraries and modern patterns.
Adopting these lesser-known tools eliminates boilerplate code and boosts application robustness.

- **Loguru for logging:** Replace verbose standard library logger setups with zero-configuration, coloured logging using [Loguru](https://github.com/Delgan/loguru).
- **DiskCache for persistence:** Cache heavy function results on local disk effortlessly without Redis overhead using [DiskCache](https://grantjenks.com/docs/diskcache/).
- **Structural pattern matching:** Write clean, expressive branching logic using `match` and `case` constructs.
- **Slots for memory savings:** Reduce memory consumption of lightweight dataclasses with `__slots__`.
{{< /tldr >}}

Following up on my previous post about [What's New in Python 3.14 and 3.15]({{< ref "08-08-new-in-python-3-14-and-3-15" >}}), I want to shift focus to the broader Python ecosystem.
While everyone knows about Pandas and Requests, there is a treasure trove of lesser-known packages and modern patterns that can drastically improve your workflow.
If you're tired of writing boilerplate code or struggling with complex configurations, you're in the right place.
In this guide, I explore some of my favourite hidden gems that you can start using today to write cleaner, more efficient Python code.

Specifically, I'll be covering:
*   **Powerful Packages**: [`Loguru`](https://github.com/Delgan/loguru) for logging, [`diskcache`](https://grantjenks.com/docs/diskcache/) for persistence, [`dirty-equals`](https://dirty-equals.helpmanual.io/) for API testing, and [`glom`](https://glom.readthedocs.io/) for nested data manipulation.
*   **Modern Patterns**: Structural pattern matching, memory optimisation with `__slots__`, native memoisation with `functools.cache`, and the walrus operator.

## Powerful Packages

While the Python standard library is incredibly rich, third-party packages often provide solutions that are much more elegant and user-friendly.
Here are four lesser-known utilities that will immediately simplify your logging, caching, testing, and nested data manipulation.

### The Loguru package

If you've ever battled with Python's built-in `logging` module, you know how verbose the configuration can be.
`Loguru` is a massive quality-of-life upgrade that completely eliminates this boilerplate.
It provides a pre-configured logger that supports human-readable formatting, colourised output, and asynchronous logging right out of the box.
To start logging, you simply import the logger instance and use it directly.

```python
from loguru import logger

logger.info("This is an informational message with colour!")
logger.error("Something went wrong, and the stack trace will be beautifully formatted.")
```

With `Loguru`, you'll never have to write another complex `logging.getLogger()` setup again.

### The diskcache package

When you need to cache data but don't want the operational overhead of setting up Redis or Memcached, `diskcache` is a phenomenal alternative.
It is an incredibly fast, SQLite-backed disk and memory cache library.
You can use it to persist expensive API responses or computation results across application restarts.
Because it is process-safe and thread-safe, it is perfect for lightweight web services or local CLI tools that need robust caching capabilities.

### The dirty-equals package

Writing tests for APIs often involves asserting against dynamic data like timestamps, UUIDs, or generated IDs.
Standard assertions usually force you to write complex, multi-line validation logic.
The `dirty-equals` package solves this by allowing you to make "fuzzy" assertions.
Instead of checking for strict equality, you can assert that a value matches a specific type or condition.

```python
from dirty_equals import IsInt, IsDatetime, IsPositive

api_response = {
    "id": 1042,
    "created_at": "2026-08-15T10:00:00Z",
    "status": "active"
}

assert api_response == {
    "id": IsInt & IsPositive,
    "created_at": IsDatetime,
    "status": "active"
}
```

This dramatically reduces the boilerplate in your test suites and makes your assertions much easier to read.

### The glom package

If you regularly work with deeply nested JSON payloads or complex dictionaries, you've likely written messy chains of `.get()` calls to avoid `KeyError` exceptions.
`glom` is a brilliant, declarative data manipulation library that completely replaces this anti-pattern.
It allows you to specify exactly the path you want to extract, providing built-in default fallbacks and data restructuring capabilities.

```python
from glom import glom

data = {"user": {"profile": {"settings": {"theme": "dark"}}}}

# Safely extract a deeply nested value with a fallback default
theme = glom(data, 'user.profile.settings.theme', default='light')
```

By using `glom`, your data extraction logic becomes instantly readable and incredibly robust.

## Modern Patterns

Writing clean, maintainable Python code is as much about leveraging the language's native syntax as it is about using the right packages.
These four modern idioms will help you reduce nesting, optimise memory, cache computation, and write more readable data pipelines.

### Structural pattern matching

Introduced back in Python 3.10, [structural pattern matching](https://docs.python.org/3/whatsnew/3.10.html#pep-634-structural-pattern-matching) (`match` / `case`) is a modern pattern that is still vastly underutilised.
It allows you to move beyond simple, chained `if/elif` statements and route logic based on the actual shape of your data structures.
This is particularly useful when parsing heterogeneous JSON payloads from external APIs.

```python
def process_event(event):
    match event:
        case {"type": "user_signup", "data": {"email": email}}:
            print(f"Sending welcome email to {email}")
        case {"type": "payment_failed", "error_code": code}:
            print(f"Logging payment failure: {code}")
        case _:
            print("Unknown event format received.")
```

By matching on dictionaries or object attributes, you can make your data routing logic highly declarative and much easier to maintain.

### Memory optimisation with slots

If you're building data-heavy applications that instantiate millions of objects, you might notice your RAM usage spiking unexpectedly.
This is because Python creates a dynamic `__dict__` for every class instance to store its attributes.
A lesser-known pattern to solve this is explicitly defining [`__slots__`](https://docs.python.org/3/reference/datamodel.html#slots) within your class.

```python
class Point:
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y
```

By defining `__slots__`, you prevent Python from creating that underlying dictionary, drastically reducing the memory footprint of your objects.

### Native memoisation with functools

Memoisation is a classic pattern for caching the results of expensive function calls based on their inputs.
Historically, developers would write custom dictionary wrappers or rely on third-party caching decorators.
However, Python's built-in [`functools`](https://docs.python.org/3/library/functools.html) module now provides a dead-simple [`@cache`](https://docs.python.org/3/library/functools.html#functools.cache) decorator that does this natively.

```python
from functools import cache

@cache
def expensive_computation(x, y):
    print("Computing...")
    return x ** y

# The first call prints "Computing...", subsequent calls return immediately
result1 = expensive_computation(4, 5)
result2 = expensive_computation(4, 5)
```

It is a completely frictionless way to add performance optimisations to recursive functions or heavy database queries.

### The walrus operator for data pipelines

Introduced a few versions ago, the assignment expression operator (`:=`), affectionately known as the [walrus operator](https://docs.python.org/3/whatsnew/3.8.html#assignment-expressions), is a fantastic pattern for cleaning up data pipelines.
It allows you to assign a variable and evaluate it within the same expression.
This is incredibly useful in `while` loops or list comprehensions where you need to calculate a value, check if it's valid, and then use it.

```python
import re

log_lines = ["INFO: Booting", "ERROR: Disk full", "INFO: Ready"]

# Using the walrus operator to filter and extract matching data simultaneously
errors = [
    match.group(1)
    for line in log_lines
    if (match := re.search(r"ERROR: (.*)", line))
]
```

By preventing double-evaluations, the walrus operator keeps your iterative logic tight and performant.

## Wrapping Up

The Python ecosystem is vast, and diving into these hidden gems can significantly upgrade your development experience.
Whether you're adopting `Loguru` to simplify your logs or leveraging structural matching for cleaner data pipelines, these tools and patterns are incredibly valuable.

Happy coding!
