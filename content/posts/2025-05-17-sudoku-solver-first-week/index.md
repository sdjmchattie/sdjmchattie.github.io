---
date: 2025-05-17
title: "First week implementing the Python Sudoku solver"
description: |-
  This is the second post in the Sudoku series, building an efficient Sudoku solver using Python.
  In this post, we'll review the steps I've taken in the first week in implementing our Sudoku solver.
slug: sudoku-solver-first-week
image: /images/posts/2025-05-17-sudoku-solver-first-week.jpg
tags:
  - Python
  - Software Architecture
  - Sudoku Series
---

This is the update post, a week after planning to build a Sudoku puzzle solver in Python.
In this post, we'll review the direction the project is going and discuss the setup steps involved in this new project.

If you like this post and you'd like to know more about how to plan and write Python software, check out the [Python]({{< ref "/tags/python" >}}) tag.
You can also find the other posts in this series using the [Sudoku Series]({{< ref "/tags/sudoku-series" >}}) tag.

This week, I've focussed on getting the basics in place without addressing solving any puzzles.
In other words, I've created a first version of the `Grid` and `Cell` class with the intention of loading a puzzle from a text file using a simple notation.
I've also implemented a form of output for the puzzle.
This sets up some of the groundwork required to actually start applying some solving logic.

I also want to address a criticism I expect some people might have over my approach here.
The most usual way to solve Sudoku puzzles with code is to take a somewhat brute force approach called [backtracking](https://en.wikipedia.org/wiki/Sudoku_solving_algorithms#Backtracking).
Clearly this is a valid way of solving the puzzle and likely requires the least code to find a solution.
However, the purpose of my project here is to practice applying complex logic to the puzzle grid.
At this time, I still don't know how practical this will be, but that's why we're trying it out.

The current code at the time of writing can be found [on GitHub](https://github.com/sdjmchattie/sudoku-solver/tree/blog/2025-05-17).

## Setting up a new project

For this project, I used Poetry as it creates an environment for Python, separating the packages from the rest of your system.
I wrote an article about [Python package management]({{< ref "2025-04-26-package-managers-for-python" >}}) last month which shows how to choose which package management you wish to use.

After installing Poetry, I created a new project using

```shell
poetry new sudoku-solver
```

This gives you a folder structure for the project and generates a template for the `pyproject.toml` file.
I edited the file to include a decription for the app and to ensure the desired version of Python was selected.

## Maintaining code quality

It's important to maintain a consistent style in your project and to avoid dead code and inconsistencies.
However, it's hard to meet all those ambitions, which is why you should employ linters and static analysers.
I chose to use `mypy` for checking type hinting and `ruff` for linting and format.
Installing these is simple, you just use the following commands, noting the use of a dependencies group for `dev`:

```shell
poetry add mypy --group dev
poetry add ruff --group dev
```

Now we can install all the dependencies and create the lock file for the project by using

```shell
poetry install
```

At this point, you can check the [`pyproject.toml`](https://github.com/sdjmchattie/sudoku-solver/blob/blog/2025-05-17/pyproject.toml) file to see these changes in action.
You can also see the [`poetry.lock`](https://github.com/sdjmchattie/sudoku-solver/blob/blog/2025-05-17/poetry.lock) file, but it's important to realise that this file should not be edited by hand.

With the linters installed, we can now use commands to apply the different types of checks we're interested in.

```shell
poetry run mypy .
poetry run ruff check
poetry run ruff format
```

Rather than having to remember these commands, I've created [a shell script](https://github.com/sdjmchattie/sudoku-solver/blob/blog/2025-05-17/lint.sh) to apply all the linting at once.
With this, I can lint the project using:

```shell
./lint.sh
```

## Implementing the in-memory model

There are three Python files now implemented for the solver, a `__main__.py` as an entry point, a `Grid.py` to manage the Sudoku grid and a `Cell.py` to manage the value in a cell and the candidates the cell could contain.
The `__main__.py` file is set up to be executed using a Poetry script, so we can run the application using

```shell
poetry run sudoku-solver ./puzzles/very_easy.txt
```

This file is responsible for reading the contents of the specified file and passing it as a row notation to the `Grid` class.
In its current state, it also asks the `Grid` object to display the puzzle.
That's all this version of the application does.

Let's take a look at how the other files are implemented.

### `Cell` class

Starting with [`cell.py`](https://github.com/sdjmchattie/sudoku-solver/blob/blog/2025-05-17/src/model/cell.py), we can see that the initialiser takes an optional value as an argument which is used to populate the `value` property.
Meanwhile, the `candidates` property is used to indicate which values are still possible in the cell.
The initial value for `candidates` is a set containing 1 through 9, but if a `value` is set on the cell, the `candidates` set is emptied.

Because `candidates` is a mutable type, the getter and setter have been carefully designed to output a copy of the set when the property is accessed and to make a copy of any value set on the property.
This is good practice to avoid external actors from modifying the state of the class without the class knowing about it.

### `Grid` class

In [`grid.py`](https://github.com/sdjmchattie/sudoku-solver/blob/blog/2025-05-17/src/model/grid.py), the initializer needs a 2D list of optional integer values arranged in the traditional 9x9 grid of a Sudoku puzzle.
It basically creates an internal representation of those values by generating 81 Cell class instances, assigning the values to them as they're created.
Any `None` value creates a blank cell.

Because we expect most grids to be created from the notation found in the [very easy text file](https://github.com/sdjmchattie/sudoku-solver/blob/blog/2025-05-17/puzzles/very_easy.txt) mentioned earlier, there is a class method on the `Grid` class that can turn that notation into the 2D list needed by the class initialiser.
This splits each line of the file's contents into single characters and checks whether they are numeric using a regular expression searching for digits.
For digits, they're converted to integers, otherwise `None` values are used to represent blanks in the grid.

The final method is `display()` which outputs an ASCII representation for the grid.
For example, the output for the puzzle loaded from the text file is displayed as shown.

```text
+-------+-------+-------+
| . 7 . | 2 . 8 | . 3 1 |
| 4 8 . | 3 . 7 | . . . |
| 9 . 3 | . . 4 | 7 5 8 |
+-------+-------+-------+
| . 4 6 | 8 7 . | . . 3 |
| 8 9 . | . 3 . | 5 6 . |
| . . 7 | 9 2 . | 8 1 . |
+-------+-------+-------+
| 7 5 4 | . 1 2 | . . . |
| . . . | 7 . 3 | 1 4 5 |
| 3 . 8 | . 4 . | 2 . 6 |
+-------+-------+-------+
```

A lot of assumptions are made here about the layout of the grid being a standard 9x9 Sudoku grid.
However, when the grid is valid, the code outputs a standard horizontal line with vertices represented with `+`.
This is followed by rows of the grid displaying the digits with spaces in between, in chunks of three, `|` displayed after each chunk.
Repeating this pattern, and including a new horizontal line after each 3 rows, the grid is rendered.

## Wrapping up

This is all we have for now, but it sets a solid base for having an in-memory model we can use to apply solvers and to be able to display the state of the grid whenever we want.

If you're already pretty familiar with Python and the problem space, I expect you've already identified some missing checks and some invalid logic in the code.
I'm aware of these and when we visit testing in the near future, we'll be able to highlight these discrepencies and fix them.

I hope you've been enjoying this series and will keep up with the articles as I release them.
