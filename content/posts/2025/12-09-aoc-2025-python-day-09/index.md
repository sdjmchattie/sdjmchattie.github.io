---
date: 2025-12-09
title: "Advent of Code 2025: Day 09"
description: |-
  A look at my Python solution for Day 9 of Advent of Code 2025.
slug: aoc-2025-python-day-09
image: /images/posts/2025/12-09-aoc-2025-python-day-09.jpg
tags:
  - Python
  - Advent of Code
  - Puzzles
---

Day 9 asks for the largest axis-aligned rectangle defined by any two corner coordinates in the input.
It then graduates to validating that a candidate rectangle must lie wholly inside the rectilinear loop traced by those corners.
Part 1 is a straightforward exhaustive search over corner pairs with an inclusive area calculation, while Part 2 adds a check for edges inside the area.

On my MacBook Air M1, Part 1 completed in 20.908 ms and Part 2 in 249.882 ms.
If you want to follow the whole series, check out the tag page at [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and you can browse the full code for 2025 in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).

## Understanding Day 9: Movie Theater

The input is a list of integer grid coordinates representing special tiles on a large floor.
Part 1 asks for the total number of tiles (area) of the largest axis-aligned rectangle you can make by choosing any two of the coordinates as opposite corners.
Part 2 keeps the same corner rule but restricts candidates to rectangles that are wholly inside the rectilinear polygon formed by joining the input points with axis-aligned edges in sequence and taking the loop interior.
You can read the full puzzle on the [Advent of Code Day 9](https://adventofcode.com/2025/day/9) page.

## Parsing the Input

Each line is a comma-separated `x,y` pair, which we parse to tuples ready for geometry operations.

```python
from lib.types import PuzzleInput

type Point = tuple[int, int]

def prepare_input(file_content: list[str]) -> PuzzleInput:
    return tuple(tuple(map(int, line.split(","))) for line in file_content)
```

- The resulting immutable tuple of `(x, y)` points is used by both parts.

## Part 1: Largest rectangle from any two corners

Part 1 is a direct enumeration of all unordered pairs of points and an area computation for the rectangle each pair determines.

### Area calculation

```python
def _calculate_area(a: Point, b: Point) -> int:
    return (abs(a[0] - b[0]) + 1) * (abs(a[1] - b[1]) + 1)
```

The area is inclusive of both corners, so we add `1` to both width and height:

```text
  1 2 3
1 # # #
2 # # #
3 # # #
```

If these were the tiles we wanted to know the count / area of, the coordinates of the corners could be `(1, 3)` and `(3, 1)`.
Subtracting the `x` values and the `y` values gives us `2` and `2`.
But the area is `3 * 3 = 9`, hence why `1` must be added to each axis.

### Enumerating pairs and selecting the maximum

We iterate all unique pairs with `itertools.combinations` and take the maximum area.

```python
from itertools import combinations

def part1(input: PuzzleInput) -> None:
    areas = (_calculate_area(a, b) for a, b in combinations(input, 2))
    print(max(areas))
```

This covers every candidate rectangle induced by two corners and finishes quickly for the problem size here.

## Part 2: Rectangles wholly inside the loop

For Part 2 we keep only rectangles that lie entirely within the rectilinear loop created by the input corners.
Each corner aligns to exactly two other corners, one with a shared `x` value to form a vertical edge, and another with a shared `y` value to form a vertical edge.
The implementation follows a simple plan.

- Identify the coordinates of all the edges of the loop.
- Iterate over all possible pairs of corners as we did in Part 1.
- Reject any rectangle that would include any edge tiles.

Due to the complexity of the analysis, I extracted these steps out to a separate class for Part 2 so that I wouldn't have to keep passing variables around between methods.

### Representing the boundary as edges

An edge is captured by the coordinate on which it is aligned and the span on the perpendicular axis.

```python
from dataclasses import dataclass
from enum import Enum
from itertools import combinations

class Axis(Enum):
    VERTICAL = 0
    HORIZONTAL = 1

@dataclass(frozen=True)
class Edge:
    aligned: int
    perp_min: int
    perp_max: int
```

We gather vertical and horizontal edges by considering all pairs that lie on the same column or row.

```python
class Part2:
    def __init__(self, points: PuzzleInput) -> None:
        self.points = points
        self.vert_edges = self._find_edges(Axis.VERTICAL)
        self.horz_edges = self._find_edges(Axis.HORIZONTAL)

    def _find_edges(self, axis: Axis) -> set[Edge]:
        aligned = axis.value
        perp = 1 - aligned
        return set(
            Edge(
                a[aligned],
                min(a[perp], b[perp]),
                max(a[perp], b[perp]),
            )
            for a, b in combinations(self.points, 2)
            if a[aligned] == b[aligned]
        )
```

- For a vertical edge the `aligned` field holds the shared `x`, and the `y` interval is `perp_min..perp_max`.
- For a horizontal edge the `aligned` field is the shared `y`, with its `x` interval in the perpendicular fields.

### Reject rectangles that are crossed by edges

A valid rectangle cannot strictly contain any edge tiles in its interior,.

```python
def _area_contains_no_edges(self, a: Point, b: Point) -> bool:
    x_min, x_max = min(a[0], b[0]), max(a[0], b[0])
    y_min, y_max = min(a[1], b[1]), max(a[1], b[1])

    for edge in self.vert_edges:
        if (
            x_min < edge.aligned < x_max
            and edge.perp_max > y_min
            and edge.perp_min < y_max
        ):
            return False

    for edge in self.horz_edges:
        if (
            y_min < edge.aligned < y_max
            and edge.perp_max > x_min
            and edge.perp_min < x_max
        ):
            return False

    return True
```

- Vertical edges are not allowed to sit strictly between the rectangle’s left and right sides while overlapping on `y`.
- Horizontal edges are not allowed to sit strictly between the top and bottom while overlapping on `x`.

### Bringing it together

We filter pairwise corners with the check for intersecting edges and print the size of the largest valid rectangle.

```python
def solve(self) -> None:
    areas = [
        _calculate_area(a, b)
        for a, b in combinations(self.points, 2)
        if self._area_contains_no_edges(a, b)
    ]
    print(max(areas))

def part2(input: PuzzleInput) -> None:
    Part2(input).solve()
```

## Performance

The pairwise enumeration is the dominant loop in both parts and is fast enough for typical inputs.
On my machine, Part 1 took 20.908 ms and Part 2 took 249.882 ms.

## Try it yourself

- Fetch your personalised input from the Advent of Code site and run the code against it.
- You can read the full puzzle on the [Advent of Code Day 9](https://adventofcode.com/2025/day/9) page.
- The full repository for my 2025 solutions is available in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).
- Explore more write-ups in the series via the tag page: [Advent of Code]({{< ref "/tags/advent-of-code" >}}).

## Wrapping Up

Part 1 computes inclusive rectangle areas for every pair of corners and picks the best, while Part 2 filters those candidates to rectangles that sit wholly inside the rectilinear loop defined by the corners in the input.
A minimal edge model together with a simple boundary-crossing exclusion keeps the implementation compact and clear.
If you enjoyed this walkthrough, check out the rest of the series at [Advent of Code]({{< ref "/tags/advent-of-code" >}}) and browse the full code in [my repository](https://github.com/sdjmchattie/AdventOfCode2025), then try it with your own input to see the algorithm in action.
