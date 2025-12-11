---
date: 2025-12-11
title: "Advent of Code 2025: Day 11"
description: |-
  A look at my Python solution for Day 11 of Advent of Code 2025.
slug: aoc-2025-python-day-11
image: /images/posts/2025-12-11-aoc-2025-python-day-11.jpg
tags:
  - Python
  - Advent of Code
  - Puzzles
---

Day 11 is about counting all possible paths through a graph between two specific nodes.
This sort of problem is best solved with a depth-first search using memoisation.
A tiny bit of state is added in to enforce constraints in Part 2.

The whole thing runs in well under a millisecond per part on my MacBook Air M1, with Part 1 in 0.068 ms and Part 2 in 0.956 ms.
If you want to follow the whole series, check out the tag page at [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and you can browse the full code for 2025 in [my 2025 solutions repository](https://github.com/sdjmchattie/AdventOfCode2025).

---

## Understanding Day 11: Reactor

Each line of input describes a directed connection from one device to multiple downstream devices, forming a graph where data flows forward through outputs.
Part 1 asks you to count every distinct path from the start device `you` to the sink device `out`, with data always moving along the listed outputs.
Part 2 changes the start to `svr` and asks for the number of paths to `out` that visit both `dac` and `fft` in any order, effectively counting only the constrained subset of all possible paths.
You can read the full puzzle on the [Advent of Code Day 11](https://adventofcode.com/2025/day/11) page.

### Parsing the input

The input is parsed into a dictionary mapping each device to the list of its output targets.
Each line looks like `src: a b c`, and we normalise it by removing the colon and splitting on spaces so the first token is the source and the rest are destinations.

```python
from lib.types import PuzzleInput

def prepare_input(file_content: list[str]) -> PuzzleInput:
    map = {
        src: dests
        for line in file_content
        for src, *dests in [line.replace(":", "").split(" ")]
    }

    return PathFinder(map)
```

- The result is a simple adjacency list like `{"you": ["bbb", "ccc"], "bbb": ["ddd", "eee"], ...}`.
- This keeps traversal straightforward and works for both parts.

### The core: DFS with memoisation and a small state

The heart of the solution is a recursive path counter that sums the number of ways to reach `out` from any node.
To avoid recomputing the same subproblems, the function is cached by its full argument list, which requires all arguments to be hashable, so the state is carried as tuples.

```python
from functools import cache

class PathFinder:
    def __init__(self, map: PuzzleInput) -> None:
        self._map = map

    @cache
    def find_path_count(
        self, src: str, specials: tuple[str] = (), seen_specials: tuple[str] = ()
    ) -> int:
        if src == "out":
            return 1 if all(s in seen_specials for s in specials) else 0
        else:
            paths = 0

            for dest in self._map[src]:
                new_seen = (
                    seen_specials + (dest,) if dest in specials else seen_specials
                )
                paths += self.find_path_count(dest, specials, new_seen)

            return paths
```

- At each node, we recursively sum the counts from each outgoing edge.
- The base case returns `1` if we reach `out` and have visited all required special nodes, otherwise `0`.
- The `specials` tuple lists nodes that must appear on the path, and `seen_specials` tracks which of those have been visited so far.
- Because we decorate with `@cache`, overlapping subtrees are computed once per distinct `(src, specials, seen_specials)` triple, which keeps the traversal fast.

---

## Part 1: Count all paths from `you` to `out`

Part 1 requires counting every distinct path starting at `you` and ending at `out` with no extra constraints.
That means we do not care about special nodes, so the default empty `specials` tuple is perfect.

```python
def part1(input: PuzzleInput) -> None:
    print(input.find_path_count("you"))
```

- The base case hits as soon as a route arrives at `out`, and each such route contributes exactly 1 to the total.
- Memoisation means any node reachable from multiple parents is solved once per relevant state, which is all we need for this unconstrained count.

---

## Part 2: Constrained paths that include dac and fft

Part 2 asks for the number of paths from `svr` to `out` that include both `dac` and `fft`, in any order.
A common way to think about this is to split by order and multiply segments, but this can get fiddly to implement and easy to get wrong when graphs rejoin.
Instead, the same DFS as Part 1 is extended to carry a tiny bit of state describing which required nodes have been seen, and the base case filters on that.

```python
def part2(input: PuzzleInput) -> None:
    print(input.find_path_count("svr", specials=("dac", "fft")))
```

- When we traverse an edge to `dest`, we append `dest` to `seen_specials` if it is required, which means the order is irrelevant because membership is what matters.
- On reaching `out`, we only count paths where every required node appears in `seen_specials`, which guarantees that both `dac` and `fft` were visited somewhere along the way.
- This approach naturally handles both possible orders in one pass.

### Why this stateful DFS helps

- It avoids separate counting passes for each order of required nodes.
- It works even if multiple parts of the graph merge and diverge because the cache key includes both the current node and the set-like tuple of visited specials.
- It keeps the code small and composable, letting you add more constraints by extending the `specials` tuple.

---

## Complexity and performance

- The traversal does a single depth-first walk of the reachable graph with memoisation, so each state `(node, seen_specials)` is computed once.
- Because arguments to cached functions must be hashable, the code represents the required and visited sets as tuples, which the `@cache` decorator can key on efficiently.
- On my MacBook Air M1, Part 1 completes in 0.068 ms and Part 2 completes in 0.956 ms, which reflects the small constant overhead added by the extra state in Part 2.

---

## Try it yourself

- Fetch your personalised input and read the problem statement on the [Advent of Code Day 11](https://adventofcode.com/2025/day/11) page.
- Run the code for your input and compare the timings on your machine.
- Browse the complete solution and the shared puzzle harness in [my 2025 solutions repository](https://github.com/sdjmchattie/AdventOfCode2025).
- Explore more write-ups in the series via the tag page: [Advent of Code]({{< ref "/tags/advent-of-code" >}}).

---

## Wrapping Up

Day 11 is a neat example of turning path counting into a cached DFS, with Part 2 adding just enough state to filter for paths that visit required nodes in any order.
The same `find_path_count` routine solves both parts by changing only the start node and the `specials` list, keeping the implementation compact and fast.
If you enjoyed this walkthrough, check out the rest of the series at [Advent of Code]({{< ref "/tags/advent-of-code" >}}) and browse the full code in [my 2025 solutions repository](https://github.com/sdjmchattie/AdventOfCode2025), then try it with your own input to see the algorithm in action.
