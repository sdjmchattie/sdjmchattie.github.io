---
date: 2026-06-13
title: "Building Modern APIs with FastAPI and Python"
description: |-
  FastAPI has become the standard for building backend APIs in Python.
  This post covers the essential concepts, setting up endpoints, and handling authentication.
  We will build a simple Books API to see how it all fits together.
slug: building-apis-with-fastapi
image: /images/posts/2026/06-13-building-apis-with-fastapi.jpg
tags:
  - Python
  - Backend Services
---

If you're starting a new Python backend project today, you're almost certainly going to use FastAPI.
It has rapidly displaced older frameworks to become the industry standard for API development.
The reasons are simple: it's fast, it embraces modern Python type hints, and it does a lot of the heavy lifting for you.

When you use FastAPI, you get automatic validation, interactive documentation, and excellent performance right out of the box.
But how do you actually structure a real application?
Let's build a simple Books API to see how it all fits together, from basic endpoints to authentication.

## Core Concepts to Think About

Before writing any code, it's worth understanding the design philosophy behind FastAPI.
It relies heavily on Pydantic, which means your data models are the source of truth.
You define your data structures using standard Python types, and FastAPI handles the validation and parsing automatically.

You also need to think about asynchronous execution.
FastAPI is built on ASGI (Asynchronous Server Gateway Interface), which means it can handle high concurrency gracefully.
If your API makes database calls or talks to other services, you should be using `async def` for your endpoints.
If you're doing heavy CPU-bound work, a standard `def` is better because FastAPI will automatically run it in a separate thread pool.

## Setting Up Your First Endpoints

Let's start by building a basic API to manage a collection of books.
First, you'll need to install FastAPI and an ASGI server like Uvicorn.
Instead of using `pip` directly, we'll use `uv`, an extremely fast Python package and project manager.

```bash
uv pip install "fastapi[standard]" uvicorn
```

Now, we can create our main application file, typically called `main.py`.
We'll define a Pydantic model for our book and create some basic routes.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Books API")

class Book(BaseModel):
    id: int
    title: str
    author: str
    year: int

# In-memory database for our example
db = [
    Book(id=1, title="1984", author="George Orwell", year=1949),
    Book(id=2, title="Dune", author="Frank Herbert", year=1965)
]

@app.get("/books", response_model=list[Book])
async def get_books():
    """Retrieve all books from the database."""
    return db

@app.post("/books", response_model=Book, status_code=201)
async def create_book(book: Book):
    """Add a new book to the collection."""
    db.append(book)
    return book
```

In this code, we've defined our `Book` schema and created a `GET` endpoint to list books and a `POST` endpoint to add one.
Notice how we use `response_model` to tell FastAPI exactly what data shape to return.
This powers the automatic documentation and ensures we don't leak sensitive fields.

## Adding Authentication

Security is a critical part of any backend service.
FastAPI has extensive support for complex authentication schemes like OAuth2 with JWT (JSON Web Tokens).
Because OAuth2 is so popular, the official documentation covers it in great detail, showing how to handle password hashing and token generation.
However, for some services, a full OAuth2 flow can be overkill.

### Implementing API key headers

Let's implement a simpler approach using API keys passed via headers.
We can use FastAPI's dependency injection system to enforce this security check on specific endpoints.

```python
from fastapi import Security, Depends
from fastapi.security import APIKeyHeader

API_KEY = "super-secret-key-123"
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Dependency to verify the API key."""
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

@app.delete("/books/{book_id}")
async def delete_book(book_id: int, key: str = Depends(verify_api_key)):
    """Delete a book, requiring a valid API key."""
    for i, book in enumerate(db):
        if book.id == book_id:
            del db[i]
            return {"message": "Book deleted successfully"}

    raise HTTPException(status_code=404, detail="Book not found")
```

By adding `Depends(verify_api_key)` to our `delete_book` endpoint, we've secured it.
FastAPI will automatically extract the `X-API-Key` header from the request and pass it to our verification function.
If the key is missing or incorrect, it returns a 403 Forbidden error before our endpoint code even runs.

## Running the API Locally

To test this out, you need to start the development server.
FastAPI recently introduced a handy CLI tool, or you can use Uvicorn directly.

```bash
fastapi dev main.py
```

This will spin up a local server with auto-reload enabled, usually at `http://127.0.0.1:8000`.
The best part of FastAPI is what happens when you visit `http://127.0.0.1:8000/docs`.
You'll see a fully interactive Swagger UI where you can test your endpoints, view your Pydantic schemas, and even input your API key to test the secured delete route.

## Wrapping Up

FastAPI strikes a brilliant balance between developer ergonomics and raw performance.
By leaning on Python's type hints and Pydantic, it eliminates entire classes of bugs related to data validation and parsing.
Whether you're building a simple microservice or a complex backend, the pattern of defining clear schemas and injecting dependencies keeps your code clean and maintainable.

Happy coding!
