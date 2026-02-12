---
date: 2025-12-10
title: "Advent of Code 2025: Day 10"
description: |-
  A look at my Python solution for Day 10 of Advent of Code 2025.
slug: aoc-2025-python-day-10
image: /images/posts/2025/12-10-aoc-2025-python-day-10.jpg
tags:
  - Python
  - Advent of Code
  - Puzzles
---

Day 10 is by far the hardest puzzle so far in 2025.
First a classic bit-flipping puzzle that reduces to XOR over bitmasks, then a minimal-presses counter puzzle modelled as an integer optimisation.
If you want to follow the whole series, check out the tag page at [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and you can browse the full code for 2025 in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).

## Understanding Day 10: Factory

Each input line describes a machine with three parts.
There is a target indicator pattern in square brackets, a list of buttons in parentheses where each button toggles or increments a subset of positions, and a list of target counter values in curly braces.
Part 1 asks for the minimum number of button presses to match the indicator pattern while ignoring the counters, and Part 2 switches mode so that buttons increment counters to match a target with the fewest total presses.
You can read the full puzzle on the [Advent of Code Day 10](https://adventofcode.com/2025/day/10) page.

## Parsing and Representation

The input is parsed into a small `Machine` type that normalises lights and buttons into bit-aligned structures that both parts can reuse.
The lights pattern becomes a binary string by mapping `.` to `0` and `#` to `1`, each button becomes a bit vector over the same width, and there is also an integer mask per button for fast XOR.

```python
class Machine:
    def __init__(
        self, lights: str, buttons: list[list[int]], joltages: list[int]
    ) -> None:
        self._lights_binary = lights.replace(".", "0").replace("#", "1")
        self.button_bin_digits = [
            self._button_binary(button, len(lights)) for button in buttons
        ]
        self.button_ints = [
            int("".join(map(str, bits)), 2) for bits in self.button_bin_digits
        ]
        self.joltages = joltages

    @property
    def lights_int(self) -> str:
        return int(self._lights_binary, 2)

    def _button_binary(self, effect: list[int], lights_count: int) -> list[int]:
        return [1 if i in effect else 0 for i in range(lights_count)]
```

Parsing splits each line into the bracketed lights, the parenthesised lists of indices for each button, and the target counters in braces.

```python
def prepare_input(file_content: list[str]) -> PuzzleInput:
    machines = []
    for line in file_content:
        parts = line.split(" ")
        lights = parts[0][1:-1]
        buttons = [list(map(int, part[1:-1].split(","))) for part in parts[1:-1]]
        joltages = tuple(map(int, parts[-1][1:-1].split(",")))

        machines.append(Machine(lights, buttons, joltages))

    return machines
```

## Part 1: Minimum presses to match the indicator pattern

Part 1 ignores counters and treats each press as toggling a set of lights, so the combined effect of pressing a subset of buttons is the XOR of their bitmasks.
The goal is to find a subset whose XOR equals the target mask with the smallest number of presses, which you can frame as a minimum Hamming weight subset XOR search.
The solution enumerates all subsets of buttons as a bitmask, XORs the corresponding button masks, and records the popcount of the subset when the XOR matches the target.
It's worth noting that pressing a button twice has no net effect, so we never try a combination that presses a button twice.

```python
from functools import reduce

def part1(input: PuzzleInput) -> None:
    best_per_machine = []

    for machine in input:
        machine_combos = []
        button_count = len(machine.button_ints)
        for combo in range(2**button_count):
            buttons = [
                machine.button_ints[i] for i in range(button_count) if (combo >> i) & 1
            ]
            combined_effect = reduce(lambda acc, b: acc ^ b, buttons, 0)
            if combined_effect == machine.lights_int:
                machine_combos.append(bin(combo).count("1"))

        best_per_machine.append(min(machine_combos))

    print(sum(best_per_machine))
```

Using integer masks keeps combination and XOR very fast, and `bin(combo).count("1")` gives the press count per subset without extra bookkeeping.
Part 1 completed in 205.823 ms on my MacBook Air M1.

## Part 2: Minimum presses to reach the target counters

Part 2 switches semantics so that each press adds 1 to the listed counters starting from zero, and the task is to reach the exact target vector with the fewest total presses.
This can be modelled with linear algebra and, thankfully, the `z3` package makes setting the algebra up very simple.

```python
from z3 import Int, Optimize, Sum

def _solve_machine(buttons: list[list[int]], joltages: list[int]) -> int:
    presses = [Int(f"p_{i}") for i in range(len(buttons))]
    eqs = [
        Sum([presses[j] * buttons[j][i] for j in range(len(buttons))]) == joltages[i]
        for i in range(len(joltages))
    ]

    opt = Optimize()
    for p in presses:
        opt.add(p >= 0)

    opt.add(*eqs)

    total = Sum(presses)
    opt.minimize(total)
    opt.check()
    model = opt.model()
    return model.evaluate(total).as_long()

def part2(input: PuzzleInput) -> None:
    results = [
        _solve_machine(machine.button_bin_digits, machine.joltages)
        for machine in input
    ]

    print(sum(results))
```

The same bit vectors that power XOR in Part 1 become the 0–1 coefficients in the Part 2 equalities, so the representation carries across cleanly.
Z3 computes an optimal integer solution for each machine, and we sum the minimum press totals across machines for the final answer.
Part 2 completed in 574.508 ms.

### What I tried before Z3

I first tried greedy strategies that fulfil one counter at a time by selecting buttons that contribute towards a single target while keeping others feasible, but the search exploded and was too slow.
I then tried a Dijkstra style search with `heapq` over counter vectors using total presses as the distance metric, but the state space was still too large for my input and it did not finish quickly.
Z3 gave me a concise and reliable way to state the constraints and objective directly, and it found the optimal totals fast enough without hand-rolled pruning or heuristics.

## Try it yourself

- Fetch your personalised input from the Advent of Code site and run both parts locally.
- Read the full puzzle on the [Advent of Code Day 10](https://adventofcode.com/2025/day/10) page.
- Explore more write-ups via the tag page: [Advent of Code]({{< ref "/tags/advent-of-code" >}}).
- Browse the full 2025 solutions in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).

## Wrapping Up

Day 10 splits neatly between bitmask XOR for lights and an integer optimisation for counters, and a shared representation makes both parts straightforward to implement.
The final code leans on Python bitwise operations for Part 1 and Z3 for Part 2, after experiments with custom search strategies proved too slow for the second part.
If you enjoyed this walkthrough, check out the rest of the series at [Advent of Code]({{< ref "/tags/advent-of-code" >}}) and try the code in [my repository](https://github.com/sdjmchattie/AdventOfCode2025) with your own input to compare results and timings.
