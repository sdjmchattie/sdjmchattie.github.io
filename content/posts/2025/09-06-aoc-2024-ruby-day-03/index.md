---
date: 2025-09-06
title: "Advent of Code 2024 Ruby Solutions: Day 3"
description: |-
  Let's look at how to solve both parts of the Advent of Code 2024 puzzle on day 3.
  This solution is in Ruby, but the principles can be applied to any language.
slug: aoc-2024-ruby-day-03
image: /images/posts/2025/09-06-aoc-2024-ruby-day-03.jpg
tags:
  - Ruby
  - Advent of Code
  - Puzzles
---

Advent of Code is an annual event that invites programmers to solve a series of themed puzzles each December, and this post is the third in my ongoing series for 2024.
Day 3, ["Mull It Over"](https://adventofcode.com/2024/day/3), seemed simple at first glance: find and evaluate multiplications in a corrupted memory dump.
But as is tradition, complexity soon crept in, especially with part two's toggling of logic state.
In this walkthrough, I’ll describe the core requirements of both parts, show what corrupted input looks like, and explain step-by-step how my Ruby solution cracks the puzzle.
For further reading, browse [the rest of the Advent of Code series]({{< ref "/tags/advent-of-code" >}}), or see all my 2024 solutions on [GitHub](https://github.com/sdjmchattie/AdventOfCode2024).

---

## Day 3: “Mull It Over” In Brief

This puzzle delivers a memory dump riddled with a mixture of valid and nonsensical code.
The input is a long single line of text featuring snippets like this (assembled here for illustration):

```text
bla!mul(2,4)%mul[3,7]?not_real_mul(10,2)mul(8,3)xyzmul(1,5)
```

Most of it is junk or malformed instructions, but hidden throughout are perfect matches like `mul(8,3)` or `mul(1,5)` which follow the strict format of `mul(X,Y)`.
Your job is to find exactly those valid pieces and work out the result as described below.

---

## Part One: Extracting and Summing Real Multiplications

The task in part one is this:

- Scan the entire corrupted memory, pick out every valid instruction that looks exactly like `mul(X,Y)` (where X and Y are both integer numbers).
- Ignore anything with typos, spacing or other syntax problems; the match must be perfect.
- For each valid instruction, multiply X by Y.
- Sum all such products to find your answer.

The real challenge lies in separating the clean from the corrupted, as illustrated in this snippet:

```text
gibberishmul(12,7)!mul(8,88)xmul[5,4]mul(13,2)randomtext
```

Only `mul(12,7)`, `mul(8,88)`, and `mul(13,2)` are valid, so the products are 84, 704 and 26, which would be summed.

### Ruby Solution: Regular Expression Extraction

To handle this reliably, my Ruby solution employs regular expressions for robust pattern matching:

```ruby
def get_mul(input)
  input.scan(/mul\((\d+),(\d+)\)/).reduce(0) { |acc, mul| acc + mul.map(&:to_i).reduce(&:*) }
end

def part1(input)
  get_mul(input)
end
```

### How does this work?

- The `scan` method uses the expression `mul\((\d+),(\d+)\)` to find every genuine match: only instances precisely following `mul(`, an integer number, comma, another integer number, and `)`.
- `scan` creates an array of paired digits for each match and those are passed to an outer `reduce` function.
- `reduce` accumulates a single value, starting with `0` and adding a new value for each pair of numbers `scan` found.
- The outer `reduce` takes each pair of numbers, `map`s the strings into integers using `to_i`, then passes them to an inner `reduce` function which uses the multiplication operator (`&;*`) to multiply the numbers together.
- The outer `reduce` finishes its job by adding this new product to the running total.

This matches the puzzle’s requirement to only process the legitimate instructions and skip over the noise.

---

## Part Two: Decoding `do` and `don’t` Toggles

Part two ratchets up the difficulty by introducing two new types of instructions:

- `do()`: enables subsequent multiplication instructions.
- `don't()`: disables subsequent multiplication instructions.

At the start, multiplications are enabled.
Whenever a `don't()` appears, all following multiplications stop getting counted until a `do()` re-enables them (and vice versa).
Only the current toggle state decides whether to include `mul()` instructions.

In a sample corrupted input, it might look something like:

```text
mul(2,10)garbledstuffdon't()mul(6,7)random()do()mul(8,2)
```

In this example:

- `mul(2,10)` is enabled and counted.
- The `don't()` disables `mul(6,7)`, so we skip this one.
- The following `do()` re-enables, so `mul(8,2)` is counted.

### Ruby Solution: Slicing Out the Disabled Chunks

It would be possible to walk the entire input, tracking enable/disable state, but my solution found a regular-expression based shortcut:

```ruby
def part2(input)
  disabled = input.scan(/don't\(\).*?do\(\)/).reduce("", &:+)
  get_mul(input) - get_mul(disabled)
end
```

Here’s what this does:

- The pattern `don't\(\).*?do\(\)` matches every section starting with `don't()` and ending at the immediately following `do()`.
  Everything in those sections—including any `mul` instructions—should be ignored for scoring.
- All disabled chunks are gathered, merged together as one block (`disabled`).
- First, compute the total sum for all `mul` instructions in the full input.
- Next, compute the sum for all `mul` instructions found inside those disabled blocks.
- The correct answer for part two is then the total sum minus the disabled sum.

This technique is both succinct and effective, sidestepping the need for manual input processing by letting regular expressions exclude everything that shouldn’t count.

---

## Wrapping Up

Day 3 is an example of how Advent of Code puzzles turn an ordinary parsing task into a test of precision and cleverness.
Identifying exactly-formatted instructions in a soup of corrupt data, and then adjusting logic with toggles, shows the combined power of pattern matching and careful state management.
If you enjoyed this explanation, you might like to check out [the rest of my Advent of Code series]({{< ref "/tags/advent-of-code" >}}), or grab [the full repo on GitHub](https://github.com/sdjmchattie/AdventOfCode2024) to explore and run the solutions yourself.

See you for how to solve day 4 in the near future.
