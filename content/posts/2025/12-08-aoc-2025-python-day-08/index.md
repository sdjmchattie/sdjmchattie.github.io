---
date: 2025-12-08
title: "Advent of Code 2025: Day 08"
description: |-
  A look at my Python solution for Day 8 of Advent of Code 2025.
slug: aoc-2025-python-day-08
image: /images/posts/2025/12-08-aoc-2025-python-day-08.jpg
tags:
  - Python
  - Advent of Code
  - Puzzles
---

Day 8 is all about finding edges between 1,000 nodes in a graph, each with a 3D set of integer coordinates.
Graphs can be computationally expensive if the wrong types are used, but my solutions run in under a second for each part of the puzzle.
Let's take a look at the puzzle specifics and how it can be solved in Python.

If you want to follow the whole series, check out the tag page at [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and you can browse the full code for 2025 in [my 2025 solutions repository](https://github.com/sdjmchattie/AdventOfCode2025).

---

## Understanding Day 8: Playground

The input is a list of junction box positions in 3D space, one per line, as comma-separated integers.
You can read the full puzzle on the [Advent of Code Day 8](https://adventofcode.com/2025/day/8) page.
The task is to consider all pairs of boxes, sort those pairs by straight-line distance, and iteratively connect them in ascending order to form circuits where electricity can flow.

Each connection merges the two circuits containing the endpoints.
For Part 1 you process only the first 1,000 connections and then multiply the sizes of the three largest circuits.
For Part 2 you continue connecting in the same distance order until everything becomes a single circuit, and then report the product of the X coordinates of the two boxes responsible for that final join.

### Why this framing works

- Sorting all pairs by Euclidean distance ensures each step chooses the globally nearest unconnected pair across the entire set.
- Merging the two circuits for each chosen pair mirrors the way connectivity expands as cables are added.
- Part 1 stops after a fixed number of joins and inspects circuit sizes, while Part 2 runs until all junction boxes are in the same circuit and inspects the final connecting edge.

---

## Parsing the input

Each line is converted into a `Point3D[int]` which exposes a `distance_to` method for Euclidean distance.
No trimming beyond splitting by commas is needed because every line is defined as three integers.

```python
from dataclasses import dataclass
from functools import reduce
from itertools import combinations
from lib.point3d import Point3D
from lib.types import PuzzleInput


def prepare_input(file_content: list[str]) -> PuzzleInput:
    return [
        Point3D(x, y, z)
        for x, y, z in (map(int, line.split(",")) for line in file_content)
    ]
```

- Each junction becomes a `Point3D`, and the whole input is a list of those points.
- The `Point3D.distance_to` method is used later to compute straight-line distances for sorting.

---

## Precomputing the nearest pairs

We generate all unique pairs of junctions, compute their Euclidean distance, and sort the list by that distance.
We also initialise circuits as a list of singleton sets, one per junction.

```python
@dataclass
class JunctionPair:
    a: Point3D[int]
    b: Point3D[int]
    distance: float


type Circuits = list[set[Point3D[int]]]
type Pairs = list[JunctionPair]


def _parse_circuits_and_pairs(
    input: PuzzleInput,
) -> tuple[Circuits, Pairs]:
    circuits = [{junc} for junc in input]
    pairs = [
        JunctionPair(c[0], c[1], c[0].distance_to(c[1])) for c in combinations(input, 2)
    ]
    pairs.sort(key=lambda jp: jp.distance)

    return circuits, pairs
```

- Defining `Circuits` and `Pairs` allows us to specify the often used types more simply.
- `combinations(input, 2)` enumerates each pair exactly once.
- Sorting by `distance` globally orders the edges from shortest to longest, which is what both parts require.
- `circuits` starts as disjoint singletons and will be merged as we process the sorted pairs.

---

## Joining circuits as we add cables

A connection merges the two circuits that contain the pair endpoints, or does nothing if they are already in the same circuit.
The implementation scans the list of circuits for those containing either endpoint and unions them.

```python
def _join_junctions(pair: JunctionPair, circuits: Circuits) -> Circuits:
    to_merge = list(c for c in circuits if pair.a in c or pair.b in c)
    merged_circuit = set().union(*to_merge)

    circuits = [c for c in circuits if c not in to_merge]
    circuits.append(merged_circuit)

    return circuits
```

- `to_merge` yields one set when both endpoints are already connected, in which case the overall structure is unchanged.
- Otherwise it yields two sets, which are unioned into a new merged circuit and spliced back into the list.
- This is a straightforward union-by-scan approach, which is more than fast enough for the puzzle input.

---

## Part 1: Multiply the three largest circuits after 1,000 joins

Part 1 needs to find the circuit landscape after the first 1,000 shortest connections have been applied.
We then sort circuit sizes and multiply the largest three.

```python
def part1(input: PuzzleInput) -> None:
    circuits, pairs = _parse_circuits_and_pairs(input)

    for pair in pairs[:1000]:
        circuits = _join_junctions(pair, circuits)

    circuit_sizes = sorted([len(c) for c in circuits], reverse=True)

    print(reduce(lambda a, x: a * x, circuit_sizes[:3], 1))
```

- The pairs are already globally ordered by distance, so `pairs[:1000]` exactly matches the required join count.
- We collect sizes, sort descending, and reduce the top three by multiplication.
- On my input on a MacBook Air M1 this completes in 711.249 ms.

---

## Part 2: Find the last join that makes everything connected

Part 2 keeps processing the same sorted list of pairs until only one circuit remains.
At the moment of full connectivity, we output the product of the X coordinates of the endpoints that caused that final merge.

```python
def part2(input: PuzzleInput) -> None:
    circuits, pairs = _parse_circuits_and_pairs(input)

    for pair in pairs:
        circuits = _join_junctions(pair, circuits)

        if len(circuits) == 1:
            print(pair.a.x * pair.b.x)
            return
```

- `len(circuits) == 1` indicates that all junctions are connected, so the current `pair` is the decisive final edge.
- The required output is the product of the `x` fields from the two `Point3D`s on that edge.
- On my input on a MacBook Air M1 this completes in 837.246 ms.

---

## Try it yourself

- Read the full puzzle on the [Advent of Code Day 8](https://adventofcode.com/2025/day/8) page.
- Pull the code and run it with your personalised input from [my 2025 solutions repository](https://github.com/sdjmchattie/AdventOfCode2025).
- Explore more write-ups in the series via the tag page: [Advent of Code]({{< ref "/tags/advent-of-code" >}}).

---

## Wrapping Up

Day 8 reduces to sorting all point pairs by Euclidean distance and merging components in that order, with Part 1 stopping after a fixed number of joins and Part 2 reporting the final edge that achieves full connectivity.
A small set-union implementation keeps the code readable and fast within the problem bounds, and the same machinery powers both answers.
If you enjoyed this walkthrough, check out the rest of the series at [Advent of Code]({{< ref "/tags/advent-of-code" >}}) and browse the full code in [my 2025 solutions repository](https://github.com/sdjmchattie/AdventOfCode2025), then try it with your own input to see the merges unfold.
