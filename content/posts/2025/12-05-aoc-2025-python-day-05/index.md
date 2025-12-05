---
date: 2025-12-05
title: "Advent of Code 2025: Day 05"
description: |-
  A look at my Python solution for Day 5 of Advent of Code 2025.
slug: aoc-2025-python-day-05
image: /images/posts/2025-12-05-aoc-2025-python-day-05.jpg
tags:
  - Python
  - Advent of Code
  - Puzzles
---

Day 5 serves up two courses: a quick taste test to check whether each ingredient is fresh according to ranges of fresh items.
Then a hearty main where we reduce overlapping ranges of the fresh items and identify how many unique ingredients are included.
We manipulate the input into integers for analysis, then work out way through the two tasks at hand until we've got a dish to be proud of.
If you fancy seconds, browse more posts via the tag page at [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and you can inspect all of the 2025 recipes in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).

---

## Understanding Day 5: Cafeteria

The input contains inclusive ranges marking fresh ingredients by ID, followed by a blank line, and then a list of available IDs to check.
Part 1 asks how many of the available IDs land inside any of the fresh ranges.
Part 2 ignores the available IDs and instead asks how many integers are covered by the union of all fresh ranges, ensuring overlaps are not double counted.
You can read the full puzzle on the [Advent of Code Day 5](https://adventofcode.com/2025/day/5) page.

---

## Parsing the Input

We split on the first blank line to separate the range definitions from the available IDs, parse range lines of the form `a-b` into `(a, b)`, and convert the remaining lines into integers.

```python
from dataclasses import dataclass


@dataclass
class InputData:
    fresh_stock: list[tuple[int, int]]
    stock: list[int]


def prepare_input(file_content: list[str]) -> InputData:
    split = file_content.index("")
    fresh, all = file_content[:split], file_content[split + 1 :]

    fresh_stock = [
        tuple(int(val_str) for val_str in range_str.split("-")) for range_str in fresh
    ]
    stock = [int(line) for line in all]

    return InputData(fresh_stock=fresh_stock, stock=stock)
```

- `fresh_stock` holds inclusive ranges as `(start, end)`.
- `stock` holds the available IDs that part 1 will check.

---

## Part 1: Count fresh available IDs

### What part 1 needs

- Determine whether each available ID falls inside at least one inclusive range.
- Count how many IDs are fresh.
- Overlapping ranges need no special handling because we can check the ID against ranges until we find one it's inside.

### How the Python code solves part 1

A helper returns early when an ID is found within any range, and a generator expression sums the fresh IDs.

```python
def part1(input: InputData) -> None:
    def item_is_fresh(item: int, fresh_stock: list[tuple[int, int]]) -> bool:
        return any(fresh[0] <= item <= fresh[1] for fresh in fresh_stock)

    print(sum(1 for item in input.stock if item_is_fresh(item, input.fresh_stock)))
```

- `item_is_fresh` takes advantage of the `any` method Python provides, returning True if any fresh range contains the ingredient item.
- The final `sum` adds one for each available ID that tested fresh.

---

## Part 2: Count all IDs covered by the fresh ranges

### A naive approach that works on the example but not on real inputs

- One tempting idea is to enumerate every integer from each range, add them all to a set, and then return the set size.
- This is fine for tiny examples, but it becomes impractical when ranges are large because you would materialise vast numbers of integers in memory and spend time inserting every single one.
- Similar ideas like building an array up to the maximum ID suffer the same fate because they allocate space proportional to the value range rather than the number of ranges.

```python
def naive_total_coverage(ranges: list[tuple[int, int]]) -> int:
    covered = set()
    for a, b in ranges:
        for x in range(a, b + 1):
            covered.add(x)

    return len(covered)
```

- The inner loop enumerates every covered ID, which is precisely what we need to avoid when ranges span huge spaces.
- The right approach is to compute the union of intervals and then sum their inclusive lengths without enumerating members.

### How the Python code solves part 2

We merge overlaps on the fly by absorbing any existing ranges that the new range touches or contains, and then we sum the inclusive lengths of all our non-connected ranges.

```python
def part2(input: InputData) -> None:
    merged_ranges = []
    for fresh in input.fresh_stock:
        start, end = fresh

        # Find any lower end range that this new range extends.
        # Also find any upper end range that this new range extends.
        # There could be one at both ends!
        # We also need to find any ranges that are within the new one because
        # the new one will replace it entirely.
        # All discovered ranges can be removed from merged_ranges.
        lower = next((r for r in merged_ranges if r[0] <= start <= r[1]), None)
        upper = next((r for r in merged_ranges if r[0] <= end <= r[1]), None)
        within = list(r for r in merged_ranges if start <= r[0] <= end and start <= r[1] <= end)
        merged_ranges = [r for r in merged_ranges if r not in [lower, upper] + within]

        # Adjust our new range to include lower and upper ranges, then append to merged_ranges
        start = lower[0] if lower else start
        end = upper[1] if upper else end
        merged_ranges.append((start, end))

    print(sum(r[1] - r[0] + 1 for r in merged_ranges))
```

- `merged_ranges` collects disjoint intervals as we go.
- For each new `(start, end)`, we look for an existing interval that already spans `start` (`lower`), one that already spans `end` (`upper`), and any intervals that lie fully within `[start, end]` (`within`).
- We remove the discovered intervals, widen `start` and `end` to extend through the `upper` and `lower` ranges when present, and append the merged range.
- Finally we compute coverage with `end - start + 1` on each inclusive interval, which avoids enumerating any IDs.

---

## Complexity and practical notes

- Part 1 runs a membership check for each available ID against each range, which scales with the product of their counts.
- Part 2 avoids materialising covered IDs by merging intervals and then summing their lengths directly, which is what keeps the run time and memory in check for large inputs.
- Python integers comfortably handle very large totals, so summing inclusive lengths will not overflow.

---

## Try it yourself

- Fetch your personalised input and run the solution to get your own results.
- You can read the full puzzle on the [Advent of Code Day 5](https://adventofcode.com/2025/day/5) page.
- The full repository for my 2025 solutions is available in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).
- Explore more write ups in the series via the tag page: [Advent of Code]({{< ref "/tags/advent-of-code" >}}).

---

## Wrapping Up

Day 5 is the first puzzle this year where the naive approach will not work at all for part 2.
These are my favourite puzzles because you have to think outside the box to get anywhere.
Even more satisfying for me is that my implementation runs faster for part 2 today and it does for part 1!

If you enjoyed this walkthrough, check out the rest of the series at [Advent of Code]({{< ref "/tags/advent-of-code" >}}) and browse the full code in [my repository](https://github.com/sdjmchattie/AdventOfCode2025), then grab your own input and give the solution a stir.
