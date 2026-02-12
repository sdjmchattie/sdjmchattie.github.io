---
date: 2026-02-28
title: "Improving Python Code Quality and Consistency Using Ruff"
description: |-
  Ruff is an extremely fast Python linter and formatter written in Rust.
  Learn how to install and configure Ruff for your Python projects and integrate it into CI/CD pipelines for consistent code quality.
slug: ruff-for-python-code-quality
image: /images/posts/2026/02-28-ruff-for-python-code-quality.jpg
tags:
  - Python
  - Code Quality
  - Tooling
---

Consistency and quality are the foundations of maintainable Python code.
As projects grow and teams expand, maintaining these standards becomes increasingly challenging without the right tools.
Ruff is an extremely fast linter and code formatter written in Rust that helps teams improve their code quality while ensuring consistency across the entire codebase.
It replaces multiple tools like Flake8, isort, and Black with a single unified solution.
In this post, we'll explore how to install Ruff, configure it for your projects, and integrate it into CI/CD pipelines to automatically enforce quality standards.

If you're interested in Python tooling, you may also enjoy reading about [Python package managers]({{< ref "04-26-package-managers-for-python" >}}).

## What is Ruff and Why Should You Use It?

Ruff is a modern Python linter and formatter that stands out for its exceptional speed and comprehensive feature set.
Written in Rust, it can check and format code 10-100x faster than traditional Python-based tools.

### Key Benefits of Ruff

**Speed**: Ruff is incredibly fast, often completing in milliseconds what would take seconds with other tools.
This makes it practical to run on every file save or as a pre-commit hook without frustrating delays.

**All-in-one solution**: Ruff combines the functionality of multiple tools including Flake8, isort, Black, pyupgrade, and more.
This simplifies your toolchain and reduces the number of dependencies your project needs.

**Comprehensive rule set**: Ruff supports over 700 lint rules, including those from popular plugins like flake8-bugbear, flake8-comprehensions, and many others.
You can enable exactly the checks that matter for your project.

**Automatic fixes**: Many issues Ruff identifies can be automatically fixed with the `--fix` flag, saving you time on manual corrections.

**Active development**: Ruff is actively maintained with frequent updates, bug fixes, and new features being added regularly.

### When to Use Ruff

Ruff is valuable for any Python project where code quality matters.
This includes web applications, data science projects, CLI tools, libraries, and microservices.
If you're working on a team or building software that others will use or maintain, Ruff helps ensure consistency and catch common mistakes before they become problems.

## Installing Ruff

Ruff can be installed using virtually any Python package manager or system package manager.
Choose the method that best fits your project's setup.

### Installing with pip

The simplest way to install Ruff is using pip:

```bash
pip install ruff
```

To verify the installation:

```bash
ruff --version
```

### Installing with pipx

If you want to install Ruff as a standalone tool available system-wide, use pipx:

```bash
pipx install ruff
```

This isolates Ruff in its own environment while making it available globally on your system.

### Installing with uv

If you're using UV for package management, you can add Ruff as a development dependency:

```bash
uv add --dev ruff
```

You can also run Ruff without installing it into your project using uvx:

```bash
uvx ruff check
uvx ruff format
```

### Installing with Poetry

For Poetry-managed projects, add Ruff as a development dependency:

```bash
poetry add --group dev ruff
```

### Installing with Conda

If you're using Conda for environment management:

```bash
conda install -c conda-forge ruff
```

### Installing with Homebrew

On macOS or Linux with Homebrew:

```bash
brew install ruff
```

### Installing with Cargo

If you have Rust's Cargo package manager installed:

```bash
cargo install ruff
```

## Basic Usage

Ruff provides two main commands: `check` for linting and `format` for code formatting.

### Linting with Ruff

To check your code for issues:

```bash
ruff check .
```

This scans all Python files in the current directory and subdirectories, reporting any issues it finds.

To automatically fix issues where possible:

```bash
ruff check --fix .
```

To check a specific file:

```bash
ruff check src/main.py
```

### Formatting with Ruff

Ruff includes a fast code formatter compatible with Black's style:

```bash
ruff format .
```

This formats all Python files in your project to match Ruff's style guidelines.

To check what would be formatted without making changes:

```bash
ruff format --check .
```

To format a specific file:

```bash
ruff format src/main.py
```

## Configuring Ruff

Ruff can be configured using a `pyproject.toml` file or a dedicated `ruff.toml` file.
Most Python projects already use `pyproject.toml`, so that's typically the best choice.

### Basic Configuration

Here's a minimal configuration to get started:

```toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I"]
```

This configuration:

- Sets the maximum line length to 88 characters (matching Black's default)
- Targets Python 3.12
- Enables pycodestyle errors (E), Pyflakes (F), and isort (I) rules

### Selecting Rules

Ruff organizes its rules into categories. You can enable entire categories or individual rules:

```toml
[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "F",      # Pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "SIM",    # flake8-simplify
]
```

You can also ignore specific rules:

```toml
[tool.ruff.lint]
ignore = ["E501"]  # Ignore line-too-long errors
```

### Excluding Files

To exclude certain files or directories from checking:

```toml
[tool.ruff]
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "migrations",
]
```

### Per-File Ignores

Sometimes you need to ignore specific rules in certain files:

```toml
[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Ignore unused imports in __init__.py files
"tests/*" = ["S101"]      # Allow assert statements in tests
```

### Import Sorting Configuration

Ruff includes isort functionality for organizing imports:

```toml
[tool.ruff.lint.isort]
known-first-party = ["myapp"]
```

### A Comprehensive Example

Here's a more complete configuration suitable for most projects:

```toml
[tool.ruff]
line-length = 88
target-version = "py312"
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
]

ignore = [
    "E501",   # line-too-long (formatter handles this)
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/*" = ["S101"]

[tool.ruff.lint.isort]
known-first-party = ["myapp"]
```

## Integrating Ruff into CI/CD Pipelines

Running Ruff as part of your CI/CD pipeline ensures that code quality checks happen automatically before code is merged or deployed.
This catches issues early and maintains consistency across your team.

### GitHub Actions

Here's a GitHub Actions workflow that runs Ruff on every push and pull request:

```yaml
name: Lint

on: [push, pull_request]

jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install Ruff
        run: pip install ruff
      - name: Run Ruff linter
        run: ruff check .
      - name: Run Ruff formatter check
        run: ruff format --check .
```

You can also use the official Ruff action:

```yaml
name: Lint

on: [push, pull_request]

jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/ruff-action@v1
        with:
          args: check
      - uses: astral-sh/ruff-action@v1
        with:
          args: format --check
```

### GitLab CI

For GitLab CI, add this to your `.gitlab-ci.yml`:

```yaml
ruff:
  image: python:3.12
  stage: test
  script:
    - pip install ruff
    - ruff check .
    - ruff format --check .
```

### Pre-commit Hooks

Running Ruff before every commit catches issues even earlier.
Create a `.pre-commit-config.yaml` file:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

Install the hooks:

```bash
pip install pre-commit
pre-commit install
```

Now Ruff will run automatically before each commit, fixing issues where possible and blocking commits if unfixable issues remain.

### Docker Integration

If you're using Docker, add Ruff to your development image:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Install development dependencies
RUN pip install ruff

COPY . .

# Run checks as part of the build
RUN ruff check .
RUN ruff format --check .
```

## Common Workflows

### Local Development

Create a shell script `lint.sh` to run all checks:

```bash
#!/bin/bash
set -e

echo "Running Ruff linter..."
ruff check .

echo "Running Ruff formatter check..."
ruff format --check .

echo "All checks passed!"
```

Make it executable:

```bash
chmod +x lint.sh
```

Run before committing:

```bash
./lint.sh
```

### Automatic Fixing

For quick fixes during development:

```bash
ruff check --fix . && ruff format .
```

This fixes all auto-fixable issues and formats your code in one command.

### Editor Integration

Most editors support Ruff through extensions:

- **VS Code**: Install the "Ruff" extension
- **PyCharm**: Configure Ruff as an external tool
- **Vim/Neovim**: Use ALE, null-ls, or nvim-lint
- **Sublime Text**: Install the Ruff plugin

With editor integration, you get real-time feedback as you type and can format on save.

## Migration from Other Tools

If you're currently using Flake8, Black, and isort, migrating to Ruff is straightforward:

1. Install Ruff as shown above
2. Create a `pyproject.toml` with equivalent rules
3. Remove old tools from your dependencies
4. Update your CI/CD scripts to use Ruff commands
5. Update pre-commit hooks to use Ruff

For most projects, Ruff's default configuration works well out of the box.
You can start with minimal config and add rules as needed.

## Wrapping Up

Ruff brings exceptional speed and comprehensive checking to Python projects without the complexity of managing multiple tools.
Whether you're starting a new project or maintaining an existing codebase, Ruff can help you maintain high code quality with minimal friction.

The combination of fast execution, automatic fixes, and extensive rule coverage makes Ruff an excellent choice for teams that value both code quality and developer productivity.
By integrating Ruff into your CI/CD pipeline, you ensure that quality checks happen automatically, catching issues before they reach production.

Give Ruff a try on your next Python project and experience the difference that fast, comprehensive tooling can make.
If you found this helpful, check out more Python content under the [Python]({{< ref "/tags/python" >}}) tag.

Happy coding!
