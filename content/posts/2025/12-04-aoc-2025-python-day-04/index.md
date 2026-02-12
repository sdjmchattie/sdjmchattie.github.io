---
date: 2025-12-04
title: "Advent of Code 2025: Day 04"
description: |-
  A look at my Python solution for Day 4 of Advent of Code 2025.
slug: aoc-2025-python-day-04
image: /images/posts/2025/12-04-aoc-2025-python-day-04.jpg
tags:
  - Python
  - Advent of Code
  - Puzzles
---

Day 4 boils down to counting and then repeatedly removing rolls of paper that have fewer than four neighbouring rolls.
A small `Grid2D` helper plus a couple of concise functions are all you need.
We will go over the rule for a roll being accessed, show how to parse the grid and inspect eight-way neighbours.
Then we'll walk through the direct count for part 1 and the repeat-until-stable removal for part 2.
If you want to follow the whole series, check out the tag page at [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and you can browse the full code for 2025 in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).

## Understanding Day 4: Printing Department

The input is a rectangular grid of characters where `@` marks a roll of paper and `.` marks empty space.
A roll is considered accessible if strictly fewer than four of its eight surrounding cells are also rolls, where neighbours include both orthogonal and diagonal cells.
Part 1 asks you to count all rolls that are accessible under that rule.
Part 2 asks you to repeatedly remove all accessible rolls and then re-evaluate, counting the total number of rolls removed until no more removals are possible.
You can read the full puzzle on the [Advent of Code Day 4](https://adventofcode.com/2025/day/4) page.

## Parsing the Input

Each line of the input is read into a list of characters, and a small grid helper wraps the 2D data to provide safe indexing and neighbour queries.

```python
from lib.grid2d import Grid2D
from lib.types import PuzzleInput

def prepare_input(file_content: list[str]) -> PuzzleInput:
    chars = [list(line.strip()) for line in file_content]
    return Grid2D.from_data(chars)
```

The `Grid2D` class exposes `width`, `height`, `__getitem__`, and `__setitem__` using `grid[x, y]` indexing for clarity.
A dedicated neighbour method returns the eight adjacent values and gracefully skips out-of-bounds locations.

```python
class Grid2D(Generic[T]):
    # ... constructor and indexing omitted for brevity ...

    def adjacent_values(self, x: int, y: int) -> list[T]:
        deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        values = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            try:
                values.append(self[nx, ny])
            except IndexError:
                continue
        return values
```

This keeps the main solution code focused on the puzzle logic rather than on bounds checks.

## Part 1: Count accessible rolls

### What part 1 needs

- Inspect every grid cell.
- When the cell is a roll `@`, count how many of the eight neighbours are also `@`.
- If that count is less than four, the roll is accessible and should contribute to the total.

### How the code solves part 1

A tiny predicate checks the cell value and counts adjacent rolls, and a simple double loop sums accessible rolls across the grid.

```python
def _is_movable_roll(grid: Grid2D[str], x: int, y: int) -> bool:
    current = grid[x, y]
    adjacent = grid.adjacent_values(x, y)
    return current == "@" and sum(1 for v in adjacent if v == "@") < 4

def part1(input: PuzzleInput) -> None:
    print(
        sum(
            1
            for x in range(input.width)
            for y in range(input.height)
            if _is_movable_roll(input, x, y)
        )
    )
```

- `_is_movable_roll` enforces the core rule directly by filtering neighbours to those that are rolls and comparing the count against four.
- The generator expression visits every `(x, y)` and increments the count whenever the predicate is satisfied.
- The result is the total number of accessible rolls for the initial configuration.

## Part 2: Remove rolls until stable

### What part 2 needs

- Find all currently accessible rolls using the same rule as part 1.
- Remove them in that round by turning them into empty cells.
- Repeat the process on the updated grid until a full pass removes nothing.
- Return the total number of rolls removed across all rounds.

### How the code solves part 2

A recursive helper performs full passes over the grid, mutates accessible rolls to `.` in place, and recurses until a pass makes no progress.

```python
def _removable_rolls(grid: Grid2D[str], removed: int = 0) -> int:
    before = removed
    for x in range(grid.width):
        for y in range(grid.height):
            if _is_movable_roll(grid, x, y):
                grid[x, y] = "."
                removed += 1

    return removed if removed == before else _removable_rolls(grid, removed)

def part2(input: PuzzleInput) -> None:
    print(_removable_rolls(input))
```

- Each pass uses `_is_movable_roll` to identify currently accessible rolls and removes them by writing `.` to the grid.
- The function tracks how many removals have occurred so far and compares the total before and after a pass.
- If a pass removes at least one roll, it recurses to evaluate the now-changed neighbourhoods in a fresh pass.
- When a pass removes none, the process has stabilised and the accumulated count is returned.

## Implementation notes and complexity

- Neighbour inspection is constant time per cell thanks to the eight fixed offsets.
- Part 1 scans the grid once, so the work is proportional to `width * height`.
- Part 2 runs multiple full passes, each pass scanning the whole grid and potentially shrinking the set of rolls, and it stops once no more cells meet the accessibility rule.
- The part 2 helper mutates the grid in place which is not always best practice, but the input for part 1 and part 2 are fresh instances in our solving application.

## Try it yourself

- Fetch your personalised input from the [Advent of Code Day 4](https://adventofcode.com/2025/day/4) page and run the code against it.
- Explore more write-ups in the series via the tag page: [Advent of Code]({{< ref "/tags/advent-of-code" >}}).
- See the complete implementation and supporting utilities in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).

## Wrapping Up

Day 4 is a neat neighbour-counting problem that first asks for a direct count and then extends naturally to an iterative removal process until stability.
A compact grid abstraction plus two short functions handle both parts with clear logic and minimal overhead.
If you enjoyed this walkthrough, check out the rest of the series at [Advent of Code]({{< ref "/tags/advent-of-code" >}}) and browse the full code in [my repository](https://github.com/sdjmchattie/AdventOfCode2025), then try it with your own input to see the progression of removals.
