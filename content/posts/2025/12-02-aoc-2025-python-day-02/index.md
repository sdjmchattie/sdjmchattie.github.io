---
date: 2025-12-02
title: "Advent of Code 2025: Day 02"
description: |-
  A look at my Python solution for Day 2 of Advent of Code 2025.
slug: aoc-2025-python-day-02
image: /images/posts/2025-12-02-aoc-2025-python-day-02.jpg
tags:
  - Python
  - Advent of Code
  - Puzzles
---

Day 2 of Advent of Code 2025 is a satisfying dive into pattern detection over numeric ranges, starting with pairs of repeated digit sequences and then generalising to any number of repeats.
The Python solution below uses straightforward string slicing and chunking to get the job done with clear, readable logic.
If you want to follow the whole series, check out the tag page at [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and you can browse the full code for 2025 in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).

---

## Understanding Day 2: Gift Shop

The puzzle provides one long line of comma-separated numeric ranges, each written as start-end, and asks you to find certain IDs inside those ranges that follow specific repetition rules.
Part 1 considers an ID invalid if its digits are exactly two copies of the same sequence, while Part 2 expands that rule so any whole-number repetition of a smaller sequence counts as invalid.
You can read the full puzzle on the [Advent of Code website](https://adventofcode.com/2025/day/2).

---

## Parsing the Input

The input for the day is a single line containing ranges separated by commas, with each range formatted as a pair of integers joined by a dash.
The parser reads the first line, splits on commas, then splits each range on the dash and converts both ends to integers.

```python
from .types import PuzzleInput


def prepare_input(file_content: list[str]) -> PuzzleInput:
    ranges = file_content[0].split(",")
    numbers = [[int(x) for x in r.split("-")] for r in ranges]
    return numbers
```

This produces a list of [start, end] pairs that downstream logic can iterate over inclusively.

---

## Part 1: Find IDs that are exactly two copies of the same digit sequence

### The logic for part 1

- Consider each integer `x` in each inclusive range `[start, end]` and convert it to a string.
- Split the string into two halves and compare them.
- If the halves are equal, the ID is invalid and should be included in the running sum.

### The Python solution for part 1

The implementation converts each number to a string, computes `half_length` as integer division by two, slices the first and second halves, and compares them.
Odd-length strings cannot be composed of two equal halves, so they naturally fail the test.

```python
def part1(input: PuzzleInput) -> None:
    bad = []
    for start, end in input:
        for x in range(start, end + 1):
            str_x = str(x)
            half_length = len(str_x) // 2

            first_half = str_x[:half_length]
            second_half = str_x[half_length:]

            if first_half == second_half:
                bad.append(x)

    print(sum(bad))
```

- Each candidate is checked in O(d) where d is the number of digits because slicing and comparison traverse the string once.
- The code accumulates invalid IDs in a list and prints the sum of all such IDs at the end.

---

## Part 2: Generalise to any number of repeated chunks

### The logic for part 2

- Now an ID is invalid if its digits are a whole-number repetition of some shorter chunk repeated at least twice.
- For each number, try all possible chunk sizes from 1 up to half the length, and only consider chunk sizes that evenly divide the total length.
- Split the string into fixed-size chunks and verify that every chunk matches the first one.

### The Python solution for part 2

The code extends the Part 1 approach by iterating over candidate chunk sizes and using a list comprehension to build all chunks, then `all(...)` to verify they match.
On the first success, the number is added to the invalid list and the inner loop breaks to avoid duplicate counting.

```python
def part2(input: PuzzleInput) -> None:
    bad = []
    for start, end in input:
        for x in range(start, end + 1):
            str_x = str(x)
            half_length = len(str_x) // 2
            for chunk_size in range(1, half_length + 1):
                if len(str_x) % chunk_size != 0:
                    continue

                chunks = [
                    str_x[i : i + chunk_size]
                    for i in range(0, len(str_x), chunk_size)
                ]
                if all(chunk == chunks[0] for chunk in chunks):
                    bad.append(x)
                    break

    print(sum(bad))
```

- The `len(str_x) % chunk_size != 0` guard ensures we only test chunk sizes that tile the string exactly.
- The `break` ensures each number contributes at most once even if multiple chunk sizes could explain it.

---

## Try it yourself

- Fetch your personalised input from the [Advent of Code website](https://adventofcode.com/2025/day/2) and run the code locally with your ranges.
- The full repository for my 2025 solutions is [on GitHub](https://github.com/sdjmchattie/AdventOfCode2025).
- Explore more write-ups in the series via the tag page: [Advent of Code]({{< ref "/tags/advent-of-code" >}}).

---

## Wrapping Up

Day 2 boils the problem down to string operations: halves comparison for Part 1 and evenly sized chunk equality for Part 2, both implemented cleanly with Python slicing and a simple loop over candidate chunk sizes.
If you enjoyed this walkthrough, check out the rest of the series at [Advent of Code]({{< ref "/tags/advent-of-code" >}}) and browse the full code [on GitHub](https://github.com/sdjmchattie/AdventOfCode2025).
Give it a try with your own input and see how your ranges affect the sum.
