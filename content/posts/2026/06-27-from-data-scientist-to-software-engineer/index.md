---
date: 2026-06-27
title: "From Insight to Production: Software Engineering Habits for Data Scientists"
description: |-
  Transitioning from exploratory data analysis to building robust software requires adopting key engineering practices.
  In this guide, I share five fundamental software engineering habits that data scientists can adopt to make their code more modular, testable, and reproducible.
  Learn how to build systems that others can run, extend, and deploy with confidence.
slug: from-data-scientist-to-software-engineer
image: /images/posts/2026/06-27-from-data-scientist-to-software-engineer.png
tags:
  - Python
  - Developer Tools
---

If you come from a data science background, your core strength lies in translating complex, messy datasets into actionable business insights.
You are likely a master of statistical modelling, feature engineering, and extracting patterns from noise.
However, a common bottleneck arises when you need to transition your exploratory models into software that other developers, operational pipelines, or clients can reliably run.
Sharing a Jupyter notebook is a fantastic way to communicate results, but it is rarely a robust strategy for delivering production software.

To expand your impact, you can adopt key software engineering practices that turn your local analyses into production-ready software systems.
In my experience, this transition is not about changing your identity as a scientist.
Instead, it is about adding engineering tools to your arsenal to magnify the reach of your analytical work.
Here are five fundamental habits you can start implementing to build software that others can run with ease.

## 1. Structuring Code: From Notebooks to Modular Packages

Jupyter notebooks are unparalleled for exploratory data analysis, visualising plots, and rapid experimentation.
However, they naturally encourage linear execution and global state, which makes code reuse difficult.
When your logic is locked inside notebook cells, other systems cannot import or run it.

I recommend starting your projects by moving core helper functions and data pipelines into modular Python files.
Instead of copying and pasting code blocks across cells, you can organise your functions into a standard Python package structure.

For example, you'll want to structure your project with a clean separation of concerns:

```
my_project/
├── pyproject.toml
├── src/
│   └── data_pipeline/
│       ├── __init__.py
│       ├── clean.py
│       └── model.py
└── main.py
```

Inside `src/data_pipeline/clean.py`, you'll define a clean, modularised function with clear type annotations:

```python
# clean.py

def clean_dataset(data_path: str) -> list[str]:
    """Clean the raw text dataset by removing whitespace and special characters.

    Args:
        data_path: The path to the raw dataset file.

    Returns:
        A list of cleaned text records.
    """
    with open(data_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    # Clean and filter empty lines
    cleaned_records = [line.strip().lower() for line in lines if line.strip()]
    return cleaned_records
```

By structuring your logic inside normal Python modules, you make it easy for your team members to import your clean functions elsewhere.
You also unlock the ability to write automated tests for individual components.

## 2. Durable Debugging: From print() to Structured Logging

When exploring data, a quick `print(df.shape)` or `print(mean_value)` is often the fastest way to verify your progress.
But when your code runs as a background job, inside a container, or on a remote runner, print statements quickly lose their utility.
They pollute standard output and lack context, making it extremely difficult for others to debug failures.

Replacing print statements with the standard Python `logging` module is a vital step in system reliability.
Logging allows you to assign levels of importance to your outputs and filter them depending on the environment.

To set up basic logging for your pipeline:

```python
# main.py
import logging

# Configure logging behaviour
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def execute_pipeline():
    logger.info("Starting data ingestion process.")
    try:
        # Imagine data ingestion happens here
        logger.debug("Connecting to database source.")
        # Perform work
        logger.info("Successfully ingested 5000 rows.")
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
```

With structured logging, you'll capture timestamps, log levels, and stack traces automatically.
This makes your code dramatically more operational, enabling team members to diagnose issues without needing to run the script interactively.

## 3. Writing Robust Tests: From Visual Checks to Automated Tests

In data science, testing often consists of visual checks: reading the head of a dataframe, plotting a histogram, or evaluating a confusion matrix.
While this confirms your model's behaviour for your current session, it does not guarantee that your pipeline will remain correct in the future.
As soon as another developer modifies a preprocessing helper, your model might silently fail or ingest corrupted inputs.

Automated unit tests serve as a contract and a safety net for your codebase.
Using a testing framework like `pytest` allows you to write assertions that check your code's logic automatically.

To write a test for your text cleaning function:

```python
# test_clean.py
import pytest
from data_pipeline.clean import clean_dataset

def test_clean_dataset_removes_whitespace(tmp_path):
    # Set up a temporary test file
    test_file = tmp_path / "test_data.txt"
    test_file.write_text("  Clean record \n\n  Another record  \n")
    
    # Run the cleaning function
    result = clean_dataset(str(test_file))
    
    # Verify the results match expectations
    assert result == ["clean record", "another record"]
```

To run your tests and verify your pipeline is working:

```bash
pytest
```

Writing tests forces you to design smaller, more modular functions.
It also ensures that any developer can confidently modify the codebase without worrying about breaking existing functionality.

## 4. Configuration & Context: From Hardcoded Constants to Clean Environments

A common trap when shifting from exploration to production is hardcoding constants, file paths, and credentials.
Lines like `data_path = "/Users/username/Downloads/data.csv"` or `api_key = "my-secret-key"` guarantee that your code will fail the moment someone else runs it.

To build portable software, you must separate your application configuration from its core logic.
This allows you to change file locations, API endpoints, or security credentials depending on where the code is executing.

I recommend using a configuration library like `pydantic-settings` to declare and validate your configurations.
This package parses environment variables and validates their types, failing fast if a required setting is missing.
I wrote about configuring python applications in a [previous guide on Pydantic Settings]({{< ref "03-07-pydantic-settings-safer-config" >}}).

To define your configuration schema:

```python
# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class PipelineConfig(BaseSettings):
    # Automatically loads from environment variables
    data_input_path: str
    model_output_path: str
    database_timeout: int = 30
    
    model_config = SettingsConfigDict(env_file=".env")

# Initialise configuration
config = PipelineConfig()
```

By defining a config object, you'll make it straightforward for operations teams to point your script to a cloud storage bucket or staging database simply by setting environment variables, without editing a single line of your code.

## 5. Reproducible Environments: From Global pip to Dependency Pinning

When you run `pip install pandas` globally on your workstation, you are modifying your system's global Python environment.
While this is convenient, it is a recipe for environment drift.
If you share your code, the next user might have a different version of pandas, numpy, or scikit-learn installed, leading to runtime crashes or subtle differences in model predictions.

To solve this "works on my machine" problem, you'll want to use a package manager that pins the exact versions of every library your project uses.
I recommend using `uv`, an incredibly fast Python package manager and project manager.
You can read about my experiences with package managers in [Package Managers for Python]({{< ref "../2025/04-26-package-managers-for-python" >}}) or check out my guide on [Migrating from Poetry to UV]({{< ref "../2025/07-19-sudoku-solver-move-to-uv" >}}).

To initialise a new project with `uv` and add dependencies:

```bash
# Create a new uv python project
uv init my-project

# Add pandas and scikit-learn
uv add pandas scikit-learn
```

This creates a `pyproject.toml` file containing your dependencies, along with a `uv.lock` file that locks the exact versions and sub-dependencies.
When your colleague runs `uv sync`, they will get the exact same environment state, ensuring identical execution behaviour.

## Wrapping Up

Embracing software engineering habits is not about abandoning your data science roots.
Rather, it is about giving your mathematical and statistical models the professional housing they need to survive in production environments.
By modularising your code, utilising structured logging, writing automated tests, separating configuration, and locking your environments, you will elevate your code from a local analysis to a durable software product.

If you want to start adopting these habits, I recommend picking one project and starting with structured logging or basic test cases.
You will quickly see the benefits in your own development workflow, and your engineering colleagues will thank you.
Happy coding!
