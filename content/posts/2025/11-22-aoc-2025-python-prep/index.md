---
date: 2025-11-22
title: "Advent of Code 2025: Preparations"
description: |-
  It's almost December 2025 and that means Advent of Code is just around the corner.
  They've slimmed the number of puzzles down to 12, but I'm still fully committed and have prepared a repository to solve these puzzles.
slug: aoc-2025-python-prep
image: /images/posts/2025/11-22-aoc-2025-python-prep.jpg
tags:
  - Python
  - Advent of Code
  - Puzzles
---

Advent of Code 2025 is almost here, and this year I am aiming squarely at speed and optimisation across all 12 puzzles using Python and UV.
I will publish a short post every day covering the approach and performance choices, and you are very welcome to join in using whichever language you want to practice.
You can follow along in my GitHub repository and jump onto a friendly private leaderboard with the join code below.

## Get In The Spirit

Advent of Code is a brilliant way to sharpen problem-solving skills in a fun, collaborative setting.
If you want to browse my intro post and my first few solutions for 2024 in Ruby, check out the [Advent of Code]({{< ref "/tags/advent-of-code" >}}) tag.
This year I will solve all 12 puzzles in Python with my usual tendency towards optimisations and speed, not a focus on production-worthy code.

## Repository, Tooling, And How To Run

### Where the code lives

All solutions and helpers will be tracked in my [GitHub repository.](https://github.com/sdjmchattie/AdventOfCode2025)

### Python and dependencies

The project targets Python 3.12 and uses UV for environment and execution, which I wrote about in a [previous blog post.]({{< ref "07-19-sudoku-solver-move-to-uv" >}})
The `pyproject.toml` keeps runtime dependencies empty and adds `ruff` as a dev tool.

```toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "AdventOfCode2025"
version = "0.1.0"
description = "Solutions to Advent of Code 2025"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = [
  "ruff>=0.12.3",
]

[project.scripts]
solve = "main:solve"
```

### Running a solution

The `solve` script prints timings for each part so you can check the performance.
The aim is to get a solution in just a few milliseconds, but some puzzles need a lot more time.

```bash
uv run solve 1
```

If you forget the day argument, the script prints a usage hint.

```text
Usage: uv run solve [day]
```

## Project Layout And Runner Behaviour

### Files and folders

Here is the core structure.

```text
pyproject.toml
src/
  main.py
  solutions/
    day00.py
    day01.py
    day02.py
    ...
inputs/
  day00.txt
  day01.txt
  day02.txt
  ...
```

The purpose of the `day00` files is to provide a template for the other days.

### What the runner does

The runner dynamically imports `solutions.dayXX`, prepares the input once per part, and times execution using high-resolution timers.
Here is a snippet with the core functionality.

```python
# src/main.py

module_name = f"solutions.{day_str}"
day_module = importlib.import_module(module_name)
prepare_input = getattr(day_module, "prepare_input")
part1 = getattr(day_module, "part1")
part2 = getattr(day_module, "part2")

with input_file.open("r") as f:
    p1_data = prepare_input([line.strip("\n") for line in f.readlines()])
p1_start = time.perf_counter()
part1(p1_data)
p1_time_ms = (time.perf_counter() - p1_start) * 1000
print(f"Part 1 completed in {p1_time_ms:.3f} ms")
```

Functions `part1()` and `part2()` do their own output of the answer content.
This is because sometimes puzzles require more than just a simple string of output.
I also reload the input for part 2 after completing part 1 because sometimes the solution modifies the input and you can avoid part 2 bugs by reloading the input from the original text file.

## Creating A New Day

### Start from the template

Each day’s solution lives in `src/solutions/dayXX.py`, and the template is available as `day00.py`.

```python
# src/solutions/day00.py

from .types import PuzzleInput

def prepare_input(file_content: list[str]) -> PuzzleInput:
    return file_content

def part1(input: PuzzleInput) -> None:
    pass

def part2(input: PuzzleInput) -> None:
    pass
```

`PuzzleInput` is used as a custom type so that we can return any type we want from the `prepare_input()` function.

### Steps to add a new puzzle

1. Copy `day00.py` to `day01.py` and implement `prepare_input`, `part1`, and `part2`.
1. Add your input file as `inputs/day01.txt`.
1. Run the solver with `uv run solve 1`.
1. Use the timings to guide small, targeted optimisations.

## Tips For Following Along

- Use any language you want to practice and compare ideas with the Python versions in the repository.
- Keep `prepare_input` focused on parsing so both parts share the same in-memory representation.
- Treat the printed timings as feedback for optimisations.
  Part 2 usually involves finding optimisations that make clean code much harder, but we're going for speed, not clean code.

## Join The Private Leaderboard

It is more fun together, so come compare daily results in a friendly leaderboard.

- Go to the Advent of Code [private leaderboard page](https://adventofcode.com/2025/leaderboard/private).
- Use code `1097851-faf6948a` to join.

## Daily Posts Plan

I will publish a short blog post each day for the 12 puzzles that will be released, covering my approach and how the code implements it.
If you fancy some warm-up reading, the [Advent of Code]({{< ref "/tags/advent-of-code" >}}) tag will help you find other posts I've made in the past.

## Wrapping Up

I am looking forward to a fast and focused Advent of Code 2025 with Python, UV, and a focus on performance.
Grab the repository, join the leaderboard, and pick the language you want to practice this December.
Look out for my first solution post towards the end of the 1st of December.
