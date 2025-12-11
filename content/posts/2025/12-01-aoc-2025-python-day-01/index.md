---
date: 2025-12-01
title: "Advent of Code 2025: Day 01"
description: |-
  A look at my Python solution for Day 1 of Advent of Code 2025.
slug: aoc-2025-python-day-01
image: /images/posts/2025/12-01-aoc-2025-python-day-01.jpg
tags:
  - Python
  - Advent of Code
  - Puzzles
---

Day 1 of Advent of Code 2025 is a neat exercise in modular arithmetic, where you track a circular dial and count how often it hits zero.
Part 1 counts only the zeros landed on at the end of rotations, and Part 2 upgrades that to count every click that passes through zero mid-rotation too.
In this post I will explain both parts, then walk through a compact Python solution that avoids simulating individual clicks and runs in linear time relative to the number of instructions.
If you want to follow the whole series, check out the tag page at [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and you can browse the full code for 2025 in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).

---

## Understanding Day 1: Secret Entrance

The puzzle describes a safe dial labelled 0 through 99 arranged in a circle and starting at 50.
You are given a list of rotations like L68 or R48, where L means turn towards lower numbers and R means turn towards higher numbers, with wrap-around at the ends.
For Part 1 you must count the number of times the dial is exactly at 0 after finishing each rotation.
For Part 2 you must instead count the number of times any single click during a rotation lands on 0, including clicks that are not at the end of a rotation.
You can read the full puzzle on the [Advent of Code website](https://adventofcode.com/2025/day/1).

---

## Parsing the Input

The input is a list of lines containing the rotations.
These are in the form of L12 or R32 where L rotates the dial counter-clockwise by that many clicks and R rotates the dial clockwise.
The specific instructions are parsed in the logic of each part in my code, so I don't do anything with the values when preparing the input data.

---

## Part 1: Count zeros only at the end of each rotation

### The logic for part 1

- Maintain the dial position as rotations are applied.
- After each rotation, decide whether the dial is at 0 and, if so, increment the answer.
- The dial is circular with values 0 to 99, so this is a mod 100 problem.

### The Python solution for part 1

A simple trick removes the need to keep the dial value wrapped to the range 0..99.
If you track the dial as an unbounded integer, then the physical position on the dial is `dial % 100`.
Therefore the dial is at zero exactly when `dial % 100 == 0`, which makes the check very cheap.

```python
def part1(input: PuzzleInput) -> None:
    zeroes = 0
    dial = 50
    for line in input:
        value = int(line[1:])

        if line[0] == "L":
            dial -= value
        else:
            dial += value

        zeroes += 1 if dial % 100 == 0 else 0

    print(zeroes)
```

- The code starts from 50 and adjusts the dial by subtracting for L and adding for R.
- It then checks `dial % 100 == 0` to see if the dial ended exactly on zero for that rotation.
- `zeroes` is incremented by 1 if the dial ended on zero after a rotation.

---

## Part 2: Count every click that lands on zero during each rotation

### The logic for part 2

- Instead of only checking the end position, count all the clicks that cross index 0 while the dial is moving.
- A long rotation like `R1000` can pass through zero many times, so a per-click simulation would be inefficient.
- We need an arithmetic way to count how many multiples of 100 lie strictly between the start and end of each movement, including the end if it lands on zero.

### The Python solution for part 2

The solution observes that each time the unbounded `dial` crosses a multiple of 100, the physical dial clicks through zero.
So the problem reduces to counting the number of multiples of 100 between the previous dial value and the new dial value for each rotation.
This can be computed with floor division using Python’s `//` operator, which floors towards negative infinity.

```python
def part2(input: PuzzleInput) -> None:
    zeroes = 0
    dial = 50
    for line in input:
        value = int(line[1:])
        prev = dial

        if line[0] == "L":
            dial -= value
            zeroes += ((prev - 1) // 100) - ((dial - 1) // 100)
        else:
            dial += value
            zeroes += (dial // 100) - (prev // 100)

    print(zeroes)
```

- For a right rotation, we move from `prev` up to `dial`, and the number of multiples of 100 hit in that closed movement is `(dial // 100) - (prev // 100)`.
- For a left rotation, we move from `prev` down to `dial`, and the number of multiples of 100 hit is `((prev - 1) // 100) - ((dial - 1) // 100)`, which carefully avoids counting the starting position if it was itself on a multiple of 100.
- These formulas count every click that lands on zero, including when the rotation ends exactly on zero.
- Because each line is processed once with O(1) arithmetic, the solution remains linear in the number of rotations and does not count individual clicks.

---

## Try it yourself

- You can fetch your personalised input from the Advent of Code site and run this code locally.
- The full repository for my 2025 solutions is [on GitHub](https://github.com/sdjmchattie/AdventOfCode2025).
- Explore more write-ups in the series via the tag page: [Advent of Code]({{< ref "/tags/advent-of-code" >}}).

---

## Wrapping Up

Day 1 is a great reminder that modular arithmetic often turns a click-by-click simulation into a couple of integer operations.
Part 1 needs only a modulo check at the end of each move, and Part 2 upgrades this with floor-division counts of how many multiples of 100 are crossed mid-rotation.
If you enjoyed this walkthrough, check out the rest of the series at [Advent of Code]({{< ref "/tags/advent-of-code" >}}) and browse the full code [on GitHub](https://github.com/sdjmchattie/AdventOfCode2025).
Give it a try with your own input and see if your own solution can beat the efficiency here.
