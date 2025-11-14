---
date: 2025-07-19
title: "Migrating from Poetry to UV in a Python Project"
description: |-
  Moving between package managers can be a risky endeavour.
  Sometimes the risk is worth the reward.
  In this article we'll move from Poetry to UV in our Python Sudoku Solver.
slug: sudoku-solver-move-to-uv
image: /images/posts/2025-07-19-sudoku-solver-move-to-uv.jpg
tags:
  - Python
  - Package Management
  - Sudoku Series
---

This is a very short post about our move from Poetry to UV in the Sudoku Solver we're building in Python.
I don’t have a definitive reason for switching, but I’ve been experimenting with UV recently and I’m starting to prefer it over Poetry.
In this post, we’ll outline the goals of the migration, the steps we took, and the outcome.
If you find this informative, you may also benefit from my previous post about [Python package managers in 2025]({{< ref "04-26-package-managers-for-python" >}}).

The current code at the time of writing can be found [on GitHub](https://github.com/sdjmchattie/sudoku-solver/tree/blog/2025-07-19) where you can also see the [differences](https://github.com/sdjmchattie/sudoku-solver/compare/blog/2025-07-05...blog/2025-07-19) since the last blog post.

If you like this post and you'd like to know more about how to plan and write Python software, check out the [Python]({{< ref "/tags/python" >}}) tag.
You can also find other posts in the [Sudoku Series]({{< ref "/tags/sudoku-series" >}}).

---

## Aims of the Migration

Before embarking on a complex process such as switching package managers, it's a good idea to set out your aims.
These are mostly around not losing functionality and identifying where enhancements could be made to the process.

- Keep the installation of dependencies simple.
- Ensure the system can still be run after the transition.
- Ensure our tests still pass.
- See if there are any `uv` specific techniques that we can apply.

---

## Steps to Migrate

I wanted to keep things simple.
Poetry was using a `pyproject.toml` file and so does UV.
So here's what I did to get everything moved over to UV.

- Rename `pyproject.toml` to `oldpyproject.toml` to keep it as a reference.
- Delete any Poetry specific lock files and virtual environment directories.
- Run `uv init` in the repository to generate some initial files, including:
  - A new `pyproject.toml`.
  - A `.python-version` file.
- Update the project description in the `pyproject.toml` file.
- Add dependencies back to the project.
- Set up a build environment and move to a package code layout.
- Add a project script to run the solver.
- Update our linting script with UV specific calls.

Let’s go into more detail on the last few steps.

---

## Adding Dependencies

Although we have no core project dependencies yet, if we did we could add them to the `uv` managed environment using the following:

```shell
uv add package-name
```

We do have some dev dependencies though, which we can install as follows:

```shell
uv add --dev mypy pytest ruff
```

This in turn updates the `pyproject.toml` file with these dependencies, creates the `uv.lock` file and generates a new `.venv` directory with the packages included.

---

## Define a Build Environment with setuptools

It would be nice if we could continue to run the solver with a custom script name instead of having to call python on `main.py` or something similar.
This is possible in `uv` and we need to define a build environment.
By adding the following section to the `pyproject.toml`, we tell `uv` to use that for building our code and in turn it treats our project as a package with modules.

```toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"
```

To get the most from this arrangement, we need to move our source code and tests into a standard package structure.
So we ensure our application files are under a `src` sub-directory, which they already are, and we move our tests from last time into a `test` directory.

---

## Creating a Script Command

Now we can create a custom script to run our solver by adding the following to our `pyproject.toml` file.

```toml
[project.scripts]
sudoku-solver = "solver:run"
```

At the same time, I've renamed the awkwardly named `__main__.py` file to `runner.py` and renamed the `main()` method to `run()` to match this script definition.

This allows us to build and run the application using the simple command:

```shell
uv run sudoku-solver
```

This automatically ensures the environment is up-to-date, then it runs our Python code.

---

## Update Linting to Use UV and UVX

The `lint.sh` file has references to Poetry in it and that's no longer the right way to call the linters.
So let's make some updates:

```shell
uv run mypy .
```

This ensures the project environment is active, which is necessary for `mypy` to resolve imports correctly.

```shell
uvx ruff check
uvx ruff format
```

These run `ruff` in an isolated tool environment, which avoids unexpected side effects from project-level configuration.

You cannot use the `uvx` command for `mypy` because, without the project environment, you cannot parse the imports and other Python specific features.
A separate environment for `mypy` causes the analysis to fail.

---

## Verify Everything Works with Tests

As discussed last time, the litmus test is to ensure your tests still work.
We do this by executing the command:

```shell
uv run pytest
```

We are greeted with a full suite of passing tests, which means we can rest easy that we haven't broken any logic while updating the package manager:

```shell
configfile: pyproject.toml
collected 21 items

tests/model/test_cell.py ..............                   [ 66%]
tests/model/test_grid.py .......                          [100%]

====================== 21 passed in 0.01s ======================
```

---

## Wrapping up

This was a relatively simple change overall, and while not strictly necessary, it’s helping align the project with tooling I’m more comfortable with going forward.
UV not only achieves all the same functionality we had with Poetry on this project;
it also provides us useful features for the future, such as the ability to load environment variables from a file without the need for `python-dotenv`.

I hope this gives you the confidence and helps you to migrate your projects as well.
If this has been useful to you, please share it with others in your tech groups.
