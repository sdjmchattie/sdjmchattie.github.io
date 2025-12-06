---
date: 2025-12-06
title: "Advent of Code 2025: Day 06"
description: |-
  A look at my Python solution for Day 6 of Advent of Code 2025.
slug: aoc-2025-python-day-06
image: /images/posts/2025-12-06-aoc-2025-python-day-06.jpg
tags:
  - Python
  - Advent of Code
  - Puzzles
---

Day 6 presents a neat parsing twist where the same worksheet must be interpreted in two different ways, and a small amount of transposition and reduction logic solves both parts cleanly.
We will outline what each part asks for, then walk through a compact Python implementation that builds column-wise maths problems and evaluates them.
If you want to follow the whole series, check out the tag page at [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and you can browse the full code for 2025 in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).

---

## Understanding Day 6: Trash Compactor

The full problem is on the [Advent of Code Day 6](https://adventofcode.com/2025/day/6) page.
At a high level, you are given a very wide worksheet where each problem is a vertical stack of numbers with an operator at the bottom, and problems are separated by a blank column.
Part 1 treats each vertical stack as a single problem using ordinary number formatting, while part 2 reinterprets the worksheet so that each column encodes a whole number read from top to bottom.

---

## Parsing and Evaluation Helpers

The solution uses a tiny data model and a shared evaluator that applies either addition or multiplication across the numbers in each problem and then sums over all problems.

```python
from dataclasses import dataclass
from functools import reduce
import operator

OPERATORS = {
    "+": operator.add,
    "*": operator.mul,
}

@dataclass
class MathsProblem:
    values: tuple[int]
    operator: callable

def _solve(maths_problems: list[MathsProblem]):
    results = []
    for problem in maths_problems:
        results.append(
            reduce(
                lambda a, x: problem.operator(a, x),
                problem.values[1:],
                problem.values[0],
            )
        )
    return sum(results)
```

- `MathsProblem` holds the column values and the operator to apply.
- The `operator` package allows us to turn string operators into Python methods ready to apply to the values.
- `_solve` reduces each problem with the appropriate operator and returns the grand total across all problems.
- Using `reduce` with `operator.add` and `operator.mul` avoids branching and keeps evaluation clear and consistent.

Input preparation for this day does not need transformation at read time because the parsing is so different between part 1 and part 2, so the lines are passed through unchanged.

```python
from lib.types import PuzzleInput

def prepare_input(file_content: list[str]) -> PuzzleInput:
    return file_content
```

---

## Part 1: Numbers are arranged in rows

### What part 1 requires

- Each problem appears as a vertical group of numbers aligned in a column, with the operator at the bottom of that column.
- Problems are separated by a full blank column, and horizontal misalignment of digits within a problem does not matter.
- Evaluate each vertical problem by applying its operator across all numbers and sum all results for the final answer.
- See the full description on the [Advent of Code Day 6](https://adventofcode.com/2025/day/6) page.

### Walking through the Python solution to part 1

For part 1, the approach is to treat each input line as a sequence of non-space tokens, transposing rows to columns so that each column yields a full problem.

```python
import re

def part1(input: PuzzleInput) -> None:
    values = [re.findall(r"\S+", line) for line in input]
    transposed = list(zip(*values))
    maths_problems = [
        MathsProblem(
            values=tuple(int(x) for x in prob[:-1]),
            operator=OPERATORS[prob[-1]],
        )
        for prob in transposed
    ]
    print(_solve(maths_problems))
```

- `re.findall(r"\S+", line)` extracts all contiguous non-space tokens from each row into lists, so blank separators between problems are omitted.
- `zip(*values)` transposes the token matrix so each result tuple corresponds to one vertical problem.
- For each transposed column, the last token is the operator and all preceding tokens are the numbers to combine.
- We build `MathsProblem` instances and feed them to `_solve` for reduction and final summation.

This leans on the puzzle guarantee that spacing columns separate problems and that alignment within a problem can be ignored once tokens are extracted.

---

## Part 2: Numbers are arranged in columns

### What part 2 changes

- Each column now encodes an entire number by stacking its digits from top to bottom.
- The operator still lives at the bottom of the problem area, and a fully blank column separates problems.
- Problems are read right-to-left column-wise, but since both `+` and `*` are commutative, column order within a problem does not affect the result.
- The task is to rebuild problems under this new interpretation and compute the new grand total.
- See the full description on the [Advent of Code Day 6](https://adventofcode.com/2025/day/6) page.

### Walking through the Python solution to part 2

For part 2, the code transposes character-by-character to work at true column granularity, then collects digits per column into a number, detects problem boundaries on empty columns, and records the operator when seen at the bottom cell.

```python
def part2(input: PuzzleInput) -> None:
    transpose = list(zip(*input)) + [(" ")]
    maths_problems = []
    operator = None
    values = []
    for line in transpose:
        val_str = "".join(line[:-1]).strip()

        if len(val_str) == 0:
            maths_problems.append(MathsProblem(values=tuple(values), operator=operator))
            values = []
            continue

        if line[-1] != " ":
            operator = OPERATORS[line[-1]]

        values.append(int(val_str))

    print(_solve(maths_problems))
```

- `zip(*input)` transposes raw characters so each `line` variable is actually a column in the input.
- `"".join(line[:-1]).strip()` takes the full column except the last row which could contain the operator, and strips padding to produce the column’s numeric string.
- If that string is empty, we have reached a separator column, so the current problem is finalised.
- If the bottom cell of a column is not a space, it must be the operator for the current problem, so we capture it.
- Otherwise, the assembled `val_str` is a valid integer column and is appended to the list of values for the current problem.
- A trailing blank column was added in line 2 and forces the final problem to be flushed without special-casing the loop end.

The same `_solve` function then evaluates each reconstructed problem and sums the results.

---

## But how does it perform?

- Part 1 relies on token transposition, which is safe because fully blank separator columns never produce tokens and thus naturally segment problems.
  It completes in 2.754 ms on my MacBook Air M1.
- Part 2’s character-level transpose preserves exact column structure so that blank separators and bottom-row operators can be detected.
  It completes in 2.112 ms, so is actually slightly faster than part 1.

---

## Try it yourself

- Fetch your personal input and run the program for both parts to verify your totals match the site for your dataset.
- Read the complete problem statement on the [Advent of Code Day 6](https://adventofcode.com/2025/day/6) page.
- Explore all 2025 solutions in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).
- Browse more posts in this series via the tag page: [Advent of Code]({{< ref "/tags/advent-of-code" >}}).

---

## Wrapping Up

Day 6 is a tidy demonstration of how a small change in interpretation can be handled by pivoting the parsing strategy while reusing the same evaluator.
Part 1 tokenises rows and transposes to columns, while part 2 works at character granularity to build column numbers and detect operators and separators, with both parts sharing the same reduction logic.
If you enjoyed this walkthrough, check out the rest of the series at [Advent of Code]({{< ref "/tags/advent-of-code" >}}) and try the code from [my repository](https://github.com/sdjmchattie/AdventOfCode2025) on your own input.
