---
date: 2025-12-07
title: "Advent of Code 2025: Day 07"
description: |-
  A look at my Python solution for Day 7 of Advent of Code 2025.
slug: aoc-2025-python-day-07
image: /images/posts/2025/12-07-aoc-2025-python-day-07.jpg
tags:
  - Python
  - Advent of Code
  - Puzzles
---

Day 7 models a downward beam traversing a grid of splitters, and a single dynamic programming pass prepares everything we need for both parts.
Part 1 counts where a straight descent is blocked by a splitter and turns into a left–right split, while Part 2 totals the many‑worlds outcomes that land on the bottom row.
On my input the implementation is fast, with Part 1 completing in 3.555 ms and Part 2 completing in 0.049 ms.
If you want to follow the whole series, check out the tag page at [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and you can browse the full code for 2025 in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).

---

## Understanding Day 7: Laboratories

The input is a rectangular map with a single start `S`, empty cells represented by `.` and splitter cells marked with `^`.
A tachyon beam enters at `S` and attempts to move straight down one row at a time.

- If the cell one row below is `.` then the beam continues down into that position.
- If the cell one row below is `^` then the vertical move is blocked and the beam produces two new beams placed in the next row at the immediate left and right columns.

The process proceeds row by row until all beams would move off the grid.

- Part 1 asks for the number of times a would‑be vertical step is replaced by a split.
- Part 2 reframes the process under a many‑worlds interpretation and asks for the total number of distinct timelines that appear on the bottom row after taking both branches at every splitter.

You can read the full problem on the [Advent of Code Day 7](https://adventofcode.com/2025/day/7) page.

### Approach at a glance

We treat the grid as a dynamic program that accumulates how many tachyons reach each coordinate, progressing strictly from top to bottom.
Seed the starting position with a count of 1, then push counts into the next row by either continuing straight down through `.` or splitting left and right when the next row contains `^`.
This single downward tabulation gives us all the information needed for both parts.

---

## Parsing and Precomputation

We load the input into a `Grid2D`, create a same‑sized integer grid to hold tachyon counts, seed `S` with `1`, and sweep from the top to the penultimate row to push counts into the next row.

```python
from lib.types import PuzzleInput
from lib.grid2d import Grid2D


def prepare_input(file_content: list[str]) -> PuzzleInput:
    original = Grid2D.from_data(file_content)
    parsed = Grid2D(original.width, original.height, 0)

    parsed[original.find("S")] = 1

    # Transfer original data into tachyon counts
    for y in range(original.height - 1):
        y_next = y + 1
        for x in range(original.width):
            x_left = x - 1
            x_right = x + 1
            current_count = parsed[x, y]
            if current_count > 0:
                if original[x, y_next] == "^":
                    parsed[x_left, y_next] += current_count
                    parsed[x_right, y_next] += current_count
                else:
                    parsed[x, y_next] += current_count

    return parsed
```

- `parsed` holds the accumulated number of tachyons that arrive at each cell after processing up to that row.
- When the next row at the same column is `^` we do not place any count directly below but instead add the count to `(x-1, y+1)` and `(x+1, y+1)`.
- Otherwise we add the count straight down into `(x, y+1)` through `.`.

By the end of this, we have a grid of integers where the value stored is how many different ways you can reach that point by following paths from the splitters above.

---

## Part 1: Count the splits

Part 1 asks for how many times a potential downward step is blocked and turned into a split.
Having already propagated counts, we can detect each split by checking for positions that had incoming flow from above but ended up with zero count at this position.

```python
def part1(input: PuzzleInput) -> None:
    # Count active splitters
    count = 0
    for y in range(1, input.height):
        y_prev = y - 1
        for x in range(input.width):
            if input[x, y] == 0:
                adjacent = input[x, y_prev]
                if adjacent > 0:
                    count += 1

    print(count)
```

- We scan from the second row, comparing each cell with the one directly above it in the precomputed count grid.
- If there were tachyons present above (`adjacent > 0`) but none arrived in this position (`input[x, y] == 0`), that vertical move was blocked by a `^` and therefore contributed a split.
- The simple scan over the prepared grid yields the total count of split events in 3.555 ms on my input.

---

## Part 2: Count the timelines

Part 2 interprets each split as branching into separate timelines, so we need the total number of outcomes that reach the bottom row.
Because the precomputation already accumulated how many tachyons flow into each coordinate, the answer is just the sum of the counts on the bottom row.

```python
def part2(input: PuzzleInput) -> None:
    # Sum tachyon counts in the bottom row
    print(sum(input[x, input.height - 1] for x in range(input.width)))
```

- Summing the last row returns the number of timelines after all possible branches.
- Python integers are arbitrary‑precision, so large totals are handled safely without extra work.
- This runs in 0.049 ms on my input.

---

## Complexity and Practical Notes

The precomputation performs a single pass over all cells, giving linear time in the size of the grid.
Both parts then perform simple scans of the prepared counts with negligible additional cost.
Conceptually this mirrors standard grid path counting via dynamic programming, adapted so that a downward move conditionally splits into two horizontal placements in the next row when encountering `^`.

---

## Try it yourself

- Read the full description on the [Advent of Code Day 7](https://adventofcode.com/2025/day/7) page.
- Run the solution against your personalised input from the site.
- Explore more write‑ups via the tag page: [Advent of Code]({{< ref "/tags/advent-of-code" >}}).
- Browse the full code for 2025 in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).

---

## Wrapping Up

Day 7 reduces to a clean top‑to‑bottom tabulation that both counts where vertical movement is replaced by splits and aggregates the many‑worlds total at the bottom row.
A single pass prepares the entire state space, after which Part 1 is a split counter and Part 2 is a last‑row sum.
If you enjoyed this walkthrough, check out the rest of the series at [Advent of Code]({{< ref "/tags/advent-of-code" >}}) and browse the full code in [my repository](https://github.com/sdjmchattie/AdventOfCode2025), then try it with your own input to see the algorithm in action.
