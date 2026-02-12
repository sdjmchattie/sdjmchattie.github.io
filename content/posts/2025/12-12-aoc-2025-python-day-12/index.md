---
date: 2025-12-12
title: "Advent of Code 2025: Day 12"
description: |-
  A look at my Python solution for Day 12 of Advent of Code 2025.
slug: aoc-2025-python-day-12
image: /images/posts/2025/12-12-aoc-2025-python-day-12.jpg
tags:
  - Python
  - Advent of Code
  - Puzzles
---

Day 12 is the last day of Advent of Code 2025, and the last day is historically quite easy.
The puzzle today looks like a polyomino packing puzzle at first glance, but for this input it reduces neatly to a capacity check on occupied cells per region.
This was an assumption on my part because of the historical ease of the final day of puzzles.

Part 1 completes in 0.643 ms on my MacBook Air M1.
Part 2 is a meta star that unlocks when you have finished all the other days, so there is nothing new to code today.

If you want to follow the whole series, visit the tag page at [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and you can browse every 2025 solution in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).

## Understanding Day 12: Christmas Tree Farm

The input is in two sections, first a catalogue of present shapes drawn on a unit grid and second a list of rectangular regions with a required quantity of each shape.
Presents may be rotated or flipped and must sit on grid cells without overlap, though unused cells in the region are allowed.
Your goal for Part 1 is to count how many regions can accommodate all the requested presents, and you can read the full puzzle on the [Advent of Code Day 12](https://adventofcode.com/2025/day/12) page.

### Why a capacity check is sufficient here

The general problem of packing polyominoes can be expressed as an exact cover, and tools like Algorithm X with Dancing Links are commonly applied to such tiling problems.
In this input, the only constraint we need to evaluate is whether the sum of occupied cells across all requested presents fits within the region area.

If the total requested area exceeds the region area then the region cannot possibly fit the presents.
If it does not exceed the region area then this solution treats the region as a fit.
This is based on an assumption because the 6 shapes in this input almost entirely fill the square area that contains them when you have them in pair.

That means we can solve Part 1 by counting the number of filled cells per shape once, and then checking each region’s requested quantities against its area.

## Parsing the Input

The parser reads shapes as blocks of `.` and `#` lines and regions as `<width>x<height>: <counts...>`.
It accumulates the shapes as lists of strings and each region as a tuple of dimensions and counts.

```python
from lib.types import PuzzleInput


def prepare_input(file_content: list[str]) -> PuzzleInput:
    shapes = []
    grids = []
    next_shape = []
    for line in file_content:
        if line == "" or line.endswith(":"):
            if next_shape:
                shapes.append(next_shape)
            next_shape = []
            continue

        if "x" in line:
            parts = [p.strip() for p in line.split(":")]
            dims = [int(x) for x in parts[0].split("x")]
            shape_counts = [int(x) for x in parts[1].split(" ")]
            grids.append((dims, shape_counts))
        else:
            next_shape.append(line)

    return shapes, grids
```

- Shapes are recorded verbatim so we can count their occupied cells.
- Regions are stored as `((width, height), [count_per_shape...])` for straightforward arithmetic later.

## Part 1: Count regions that can fit the requested presents

### The logic for part 1

- Compute the occupied cell count for each shape by counting `#` in its definition.
- For each region, compute its area as `width * height`.
- Multiply each shape’s cell count by the requested quantity and sum across shapes for that region.
- If the requested total is strictly less than the region area, count the region as a fit.

### The Python solution for part 1

```python
def part1(input: PuzzleInput) -> None:
    hash_sizes = []
    for grid in input[0]:
        size = 0
        for line in grid:
            size += line.count("#")
        hash_sizes.append(size)

    fits = 0
    for dims, shape_counts in input[1]:
        grid_size = dims[0] * dims[1]
        full_size_shapes = sum([c * hash_sizes[i] for i, c in enumerate(shape_counts)])

        fits += 1 if full_size_shapes < grid_size else 0

    print(fits)
```

- `hash_sizes` collects the area of each shape once by summing `#` cells per definition.
- For each region we compute `grid_size` and then the total requested area as a dot product of counts and `hash_sizes`.
- A strict less than test treats any region with spare cells as a success and adds it to the answer.
- On my MacBook Air M1 this completes in 0.643 ms for my input.

## Part 2: There is no new code today

Part 2 for Day 12 does not add a new constraint or twist and is not a coding challenge today.
You simply need to have completed all of the other days to earn the second star, which I have.

## Notes on tiling and exact cover

Packing polyominoes into regions is a classic exact cover problem in the general case.
[Algorithm X](https://en.wikipedia.org/wiki/Knuth%27s_Algorithm_X) is a backtracking method for exact cover, and [Dancing Links](https://en.wikipedia.org/wiki/Dancing_links) is a technique that makes covering and uncovering constraints efficient.
Many polyomino tiling solvers represent placements as rows in an incidence matrix and then use Algorithm X or a DLX implementation to search for valid coverings.
Those approaches are valuable when arrangement constraints matter, but they are unnecessary for this Day 12 input where an area capacity check suffices.

## Try it yourself

- Fetch your personalised input and read the full description on the [Advent of Code Day 12](https://adventofcode.com/2025/day/12) page.
- Run the solution from [my repository](https://github.com/sdjmchattie/AdventOfCode2025) and compare your timings.
- Explore more write-ups in this series via the tag page: [Advent of Code]({{< ref "/tags/advent-of-code" >}}).

## Wrapping Up

Day 12 boils down to counting occupied cells per shape and checking whether each region has enough capacity to hold the requested presents, which makes for a fast and simple Part 1.
Part 2 is a meta completion check, so there is no additional code to write today.
If you found this helpful, browse the rest of the series at [Advent of Code]({{< ref "/tags/advent-of-code" >}}) and try the code from [my repository](https://github.com/sdjmchattie/AdventOfCode2025) with your own input.
