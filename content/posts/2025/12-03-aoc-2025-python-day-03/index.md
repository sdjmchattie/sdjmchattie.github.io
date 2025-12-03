---
date: 2025-12-03
title: "Advent of Code 2025: Day 03"
description: |-
  A look at my Python solution for Day 3 of Advent of Code 2025.
slug: aoc-2025-python-day-03
image: /images/posts/2025-12-03-aoc-2025-python-day-03.jpg
tags:
  - Python
  - Advent of Code
  - Puzzles
---

Day 3 builds a number from digits by picking a subsequence with the largest possible value, and the same greedy approach powers both parts.
We will unpack the problem requirements at a high level, then walk through a compact Python solution that selects the maximum value subsequence per digit sequence and sums the results across the input.
If you want to follow the whole series, check out the tag page at [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and you can browse the full code for 2025 in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).

---

## Understanding Day 3: Lobby

Each input line is a bank of single-digit battery ratings, referred to as joltges, from 1 to 9.
The task is to choose a fixed number of digits per bank, without changing the order, to form the largest possible number for that bank.
Part 1 requires picking exactly two digits per bank and summing the resulting two-digit numbers across all banks.
Part 2 increases the requirement to exactly twelve digits per bank, again summing across all banks.
You can read the full puzzle on the [Advent of Code Day 3](https://adventofcode.com/2025/day/3) page.

### How to approach the problem

Before we write any code, let's consider the correct way to find the highest number you can extract from a sequence of digits.
Let's say, for example, that you need to find the highest three digit number in the sequence `123475689` without changing the order.
The number we need to extract is `789`.

As we're not changing the order, the first digit has to come from somewhere in the sequence that doesn't include the last two digits, otherwise we can't create a three digit number.
So the first digit is the highest one you can find in all but the last two of the sequence, which is the `7` in the middle.

To find the second digit, we apply similar logic, but this time look at everything to the right of the `7` only and exclude one digit on the right hand end.  The largest satisfying digit is the `8` because the `9` is not being considered for this digit.

And finally of course, the `9` becomes the final digit.
For the final digit, we can consider all of the rest of the sequence we are left with.

Now let's take a look at how to capture this in Python.

---

## Parsing the Input

The input is read as a list of lines where each character is a digit, and we convert each line into a list of integers for easy numeric comparisons.

```python
from .types import PuzzleInput

def prepare_input(file_content: list[str]) -> PuzzleInput:
    return [[int(char) for char in line] for line in file_content]
```

- Every bank becomes a list like `[9, 8, 7, 6, ...]` which we will treat as a sequence to pick a subsequence from.
- No trimming or validation is required because all characters are digits `1` through `9` by puzzle definition.

---

## Part 1: Pick two digits per bank for the maximum value

### The logic for part 1

- For each bank, select exactly two digits in their original order to maximise the resulting two-digit number.
- This is equivalent to finding the lexicographically largest subsequence of length 2.
- A greedy strategy works by choosing the leftmost possible next digit that is as large as possible while still leaving enough digits to fill the remaining slots.

### The Python solution for part 1

The helper `_max_joltage` implements the greedy subsequence selection and builds the resulting number as an integer.
In essence we follow the logic presented above, by find the highest first digit that we can.
The `size` parameter allows us to know what value to assign to this digit when building an integer.

For each digit in an integer, it is worth a different amount according to its position in the number.
For example:

`789 = (7 * 100) + (8 * 10) + (9 * 1)`

Or in other words, the right-most digit is multiplied by 10 to the power of 0 (`10**0` in Python code) which is 1.
The second right-most digit is multiplied by 10 to the power of 1.
And the third right-most digit is multiplied by 10 to the power of 2.

```python
def _max_joltage(starting_bank: list[int], size: int) -> int:
    bank = starting_bank.copy()
    joltage = 0

    while size > 0:
        size -= 1
        digit = max(bank[: len(bank) - size])
        joltage += digit * (10**size)
        loc = bank.index(digit)
        bank = bank[loc + 1 :]

    return joltage

def part1(input: PuzzleInput) -> None:
    print(sum(_max_joltage(bank, 2) for bank in input))
```

- On each iteration we must pick one digit while ensuring that enough digits remain to finish the subsequence, so the search window is `bank[: len(bank) - size]` having already reduced `size` by 1.
- We pick the maximum digit within that window, append it to the answer by multiplying with its positional weight, and then drop everything after the first instance of the digit in the bank.
- Because the weight decreases each step, picking the largest available digit as early as possible guarantees the maximum two-digit number for that bank.
- Finally we sum across all the digits multiplied by their weights to get the integer they represent.

For part 1, we call our helper for each bank of joltages, passing the size as 2 because we're finding 2-digit joltages.
These joltages are summed to give us the solution to the puzzle.

---

## Part 2: Pick twelve digits per bank for the maximum value

### The solution for part 2

- The rule is the same but now you must select exactly twelve digits from each bank.
- We again need the largest subsequence, only with a larger target length.
- The same greedy approach applies as part 1, just with a `size` parameter of `12`.

```python
def part2(input: PuzzleInput) -> None:
    print(sum(_max_joltage(bank, 12) for bank in input))
```

---

## Complexity and practical notes

`_max_joltage` performs `size` selections per bank, and each selection scans a prefix to find a maximum and locate its index.
That gives an overall cost proportional to the product of bank length and `size`, which is perfectly fine for the size of the input on this problem.
The approach keeps the code short and clear, and the same helper solves both parts with only the target length changed.

---

## Try it yourself

- Fetch your personalised input from the Advent of Code site and run my code against it.
- You can read the full puzzle on the [Advent of Code Day 3](https://adventofcode.com/2025/day/3) page.
- The full repository for my 2025 solutions is available in [my repository](https://github.com/sdjmchattie/AdventOfCode2025).
- Explore more write-ups in the series via the tag page: [Advent of Code]({{< ref "/tags/advent-of-code" >}}).

---

## Wrapping Up

Day 3 reduces neatly to finding the largest subsequence of a fixed length, and a small greedy helper does all the heavy lifting for both parts.
Part 1 picks two digits, Part 2 picks twelve, and the same selection rule maximises each bank before summing the totals.
If you enjoyed this walkthrough, check out the rest of the series at [Advent of Code]({{< ref "/tags/advent-of-code" >}}) and browse the full code in [my repository](https://github.com/sdjmchattie/AdventOfCode2025), then try it with your own input to see the algorithm in action.
