---
date: 2026-01-31
title: "Structured Output in LangGraph"
description: |-
  Turn free‑form LLM text into reliable, typed data.
  Learn how LangGraph, Pydantic, and OutputFixingParser make structured outputs simple and robust.
slug: structured-output-in-langgraph
image: /images/posts/2026/01-31-structured-output-in-langgraph.jpg
tags:
  - Python
  - LangGraph
  - Agentic AI
---

Large language models are incredibly versatile, but when your code depends on predictable data structures, free‑form text can be a headache. The same information can be expressed in countless ways, making downstream processing error-prone. Structured output bridges this gap: by defining a schema, injecting format instructions into your prompt, and validating (or even repairing) the model’s response, you can turn LLM text into reliable, typed data your code can safely consume. In this post, we’ll explore how to implement this workflow in LangGraph using Pydantic models, parsers, and automatic repair mechanisms.

---

## What We Are Building

We will extract book metadata into a strongly‑typed Pydantic model with a normal LLM call.
We will inject format instructions into the prompt so the model knows exactly what JSON to return.
We will wrap the parser with an `OutputFixingParser` so malformed responses are automatically sent back to an LLM for correction, with optional retries for extra robustness.
Finally, we will show how to ask a prebuilt LangGraph agent to return structured results too.

---

## Define a Pydantic Model for Your Output

A model is our contract with the LLM, and it doubles as a source of schema and validation.

```python
from pydantic import BaseModel, Field

class Book(BaseModel):
    name: str = Field(description="The name of the book")
    author: str = Field(description="The author of the book")
    publisher: str = Field(description="The publisher of the book")
    genre: str = Field(description="The genre of the book")
    publishing_year: int = Field(description="The publishing year of the book")
```

Each field carries a type and a description, which the tooling will turn into formatting instructions for the model.
Descriptions help steer the model while types make validation strict.

---

## Prompt With Format Instructions From the Parser

LangChain’s `PydanticOutputParser` can derive human‑readable instructions and a JSON schema from your model, then validate the response.
We inject those instructions into a normal prompt template.

```python
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

# LLM for generation
llm = ChatOpenAI(model="gpt-4.1-mini")

# Parser bound to our Pydantic model
parser = PydanticOutputParser(pydantic_object=Book)

# Prompt that includes the parser's format instructions
prompt = PromptTemplate(
    template=(
        "Give me the book name, author, publisher, genre, and publishing year for:\n\n"
        "{book_name}\n\n"
        "{format_instructions}"
    ),
    input_variables=["book_name"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Compose a simple chain: prompt -> LLM -> parser
chain = prompt | llm | parser

# Make a call
book = chain.invoke({"book_name": "Wings of Fire"})
```

The secret sauce here is the `parser.get_format_instructions()` which gives all the information needed for the LLM to know the schema of the Pydantic model.
In the examples we're creating here, the following is given to the LLM as part of the prompt.

````text
The output should be formatted as a JSON instance that conforms to the JSON schema below.

As an example, for the schema {"properties": {"foo": {"title": "Foo", "description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}
the object {"foo": ["bar", "baz"]} is a well-formatted instance of the schema. The object {"properties": {"foo": ["bar", "baz"]}} is not well-formatted.

Here is the output schema:
```
{"properties": {"name": {"description": "The name of the book", "title": "Name", "type": "string"}, "author": {"description": "The author of the book", "title": "Author", "type": "string"}, "publisher": {"description": "The publisher of the book", "title": "Publisher", "type": "string"}, "genre": {"description": "The genre of the book", "title": "Genre", "type": "string"}, "publishing_year": {"description": "The publishing year of the book", "title": "Publishing Year", "type": "integer"}}, "required": ["name", "author", "publisher", "genre", "publishing_year"]}
```
````

The parser at the end of the chain does the conversion of the LLM's response into the `Book` type we're trying to get.
Parsing errors are normal when models wander off the required structure, which is where the `OutputFixingParser` comes in.

---

## Add OutputFixingParser For Automatic Repairs

The `OutputFixingParser` wraps your base parser and uses an LLM to correct malformed outputs when parsing fails.
Under the hood it takes the base parser’s formatting instructions and the bad text, asks an LLM to fix the text to satisfy the schema, and tries to parse again.
You can use a different model and temperature for fixing than for generation, which is a handy way to mix a creative generator with a deterministic fixer.

Note that while the `OutputFixingParser` used to exist as part of the `langchain-core` package, it has recently been moved to the `langchain-classic` package which you will need to add as a dependency of your project.
I've seen this parser move around quite a lot over the last year or two.
The code below works at the time of writing, but you may have to find out where it's been moved to again if it isn't part of the `langchain-classic` package when you try to access it.

```python
from langchain_classic.output_parsers import OutputFixingParser

# A separate LLM to act as the "fixer"
# Perhaps a weaker model which will run fast and doesn't need to be as creative
fixer_llm = ChatOpenAI(model="gpt-4o-mini")

# Wrap the base parser so malformed JSON/text can be corrected automatically
fixing_parser = OutputFixingParser.from_llm(llm=fixer_llm, parser=parser)

chain = prompt | llm | fixing_parser

# Make a call with automatic fixing
book = chain.invoke({"book_name": "Wings of Fire"})
```

If the first parse attempt fails, the fixing parser prompts the fixer LLM with the schema‑driven instructions to return a corrected object.
Note that this isn't a new attempt to find the book data, only to convert the original response for the book into a valid format for an instance of the Pydantic object.
This keeps your downstream code simple by centralising recovery logic in the parser.

---

## Optional: Add Retries Around Fixing

In production you almost certainly want to try multiple fix attempts before giving up.
The `OutputFixingParser` has the machinery to do this for you, but by default, as above, it will only try one fixing attempt.
By adding the `max_retries` argument when creating the `OutputFixingParser`, failed fixing attempts will be retried a number of times.

```python
fixing_parser = OutputFixingParser.from_llm(
    llm=fixer_llm,
    parser=parser,
    max_retries=3,
)
chain = prompt | llm | fixing_parser

# Make a call with automatic fixing
# This will now try up to 3 times to fix the output if it will not parse
book = chain.invoke({"book_name": "Wings of Fire"})
```

Obviously each attempt to fix the output requires another round trip to an LLM, so be wary of the time cost this might have on your application.
Additionally, if the original response never contained the required data, no amount of fixing will create a valid Pydantic model instance.

---

## How OutputFixingParser Works Under The Hood

- It wraps another output parser such as `PydanticOutputParser`.
- When `parse` fails, it constructs a targeted prompt that includes the base parser’s format instructions and the failing text.
- It calls a designated LLM to transform the text so that it conforms to the schema.
- It re‑runs the underlying parser on the fixed text, returning structured data if validation now passes.

You can use a different LLM and temperature for fixing than for generation, depending on what gives you the best results.
Often, fixing is easier than the original generation, so you might find using a weaker model is faster and just as effective as a more powerful model.

---

## Alternatives And Notes

- If you prefer `TypedDict` schemas, you can ask an LLM to produce that structure directly with `with_structured_output`, for example a `PlayerDict` that returns `{'name': ..., 'age': ..., 'position': ...}` using `ChatOpenAI`.
- You can also build response schemas using `ResponseSchema` and `StructuredOutputParser`, which generate format instructions for arbitrary field lists rather than full Pydantic models.
- Structured outputs remain valuable even when providers offer native JSON modes, because parsers add validation, shape conversions, and repair logic that native modes may not guarantee across providers.
- For a broader tour of structured outputs in LangGraph’s ecosystem and prebuilt nodes, the LangGraph Advanced code examples in the LangGraph Advanced GitHub repository are a helpful reference.

---

## Wrapping Up

You have seen how to define a Pydantic model, inject precise format instructions into prompts, and validate the result with a parser that can automatically fix malformed outputs.
This approach gives your LangGraph applications a predictable contract between prompts and downstream code.
