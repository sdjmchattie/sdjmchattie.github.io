---
date: 2025-08-09
title: "Advent of Code 2024 Ruby Solutions: Day 1"
description: |-
  Let's look at how to solve both parts of the Advent of Code 2024 puzzle on day 1.
  This solution is in Ruby, but the principles can be applied to any language.
slug: aoc-2024-ruby-day-01
image: /images/posts/2025/08-09-aoc-2024-ruby-day-01.jpg
tags:
  - Ruby
  - Advent of Code
  - Puzzles
---

Advent of Code is an annual programming event that offers daily puzzles throughout December, delighting enthusiasts with clever challenges and a festive spirit.
If you’d like to know more about what Advent of Code entails, take a look at my previous blog post: [Advent of Code Introduction]({{< ref "01-26-advent-of-code" >}}).

I’m excited to share a new series detailing my solutions for Advent of Code 2024, written in Ruby.
I chose Ruby because of its clear and logical approach to managing complex data, along with its functional syntax that makes parsing and analysing puzzle inputs straightforward.
Ruby’s expressive enumerable methods allow for concise and readable code, ideal for the kinds of data transformations these puzzles require.

All of my code for Advent of Code 2024 is available on GitHub at:
[https://github.com/sdjmchattie/AdventOfCode2024](https://github.com/sdjmchattie/AdventOfCode2024).

---

## Day 1 Puzzle

The first day’s puzzle, [Historian Hysteria](https://adventofcode.com/2024/day/1), introduces two lists of location IDs from senior historians.
Your job is to analyse these lists in two parts, each revealing new insights about their differences and similarities.

### Part 1: Total Distance

In this part, the goal is to measure how far apart the two lists are by pairing their numbers after sorting both lists.
Sorting ensures that the smallest numbers align with each other, the second smallest pair together, and so on, rather than pairing numbers in their original order.
By doing this, you get a meaningful comparison that accounts for relative position rather than just sequence.

The solution works by:

- Separating the input into two arrays representing the two lists.
- Sorting each array ensures that numbers are paired logically by size.
- Pairing the sorted elements allows direct comparison between aligned values.
- Calculating the absolute difference for each pair quantifies how far apart the values are.
- Summing these differences produces the total distance score.

This approach helps uncover the overall disparity between the two lists in a simple yet effective manner.

Here’s how this looks in Ruby:

```ruby
def part1(input)
  left, right = input.transpose
  left.sort!
  right.sort!

  left.zip(right).map { |l, r| (l - r).abs }.sum
end
```

The code elegantly leverages Ruby's enumerable capabilities: `transpose` splits the input into left and right lists; `sort!` orders them; `zip` pairs elements; and `map` with `sum` computes the cumulative difference.

### Part 2: Similarity Score

The second part shifts focus to identifying how often numbers from the left list appear in the right list.
Rather than sorting or pairing, this part looks at frequency and weighted contributions to a similarity score.

The solution involves:

- Counting the occurrences of each number in the right list using Ruby's `group_by` and `transform_values`, which efficiently aggregates counts into a hash.
- Iterating over the left list to multiply each number by how many times it appears in the right list.
- Summing these products to reflect how closely the two lists align based on repeated values.

This method quantifies similarity in terms of frequency overlap rather than positional differences, providing a complementary perspective to Part 1.

The Ruby code demonstrating this logic is:

```ruby
def part2(input)
  left, right = input.transpose

  right_counts = right.group_by(&:itself).transform_values(&:count)
  left.map { |l| l * right_counts.fetch(l, 0) }.sum
end
```

By grouping the right list elements by their own value and counting occurrences, this technique quickly produces a lookup table.
The `map` iterates over the left list and performs a weighted sum using that frequency information, resulting in the final similarity score.

---

## Wrapping Up

In this post, we introduced an Advent of Code 2024 series with an exploration of the first day’s puzzle and its two distinct parts.
Ruby’s powerful enumeration and data manipulation methods make it particularly well-suited for efficiently solving puzzles that involve comparing and transforming lists.

I invite you to try the puzzle yourself at [adventofcode.com/2024/day/1](https://adventofcode.com/2024/day/1) and explore the full set of my solutions on GitHub:
[https://github.com/sdjmchattie/AdventOfCode2024](https://github.com/sdjmchattie/AdventOfCode2024).

In future posts, we'll explore some of the more complex puzzles from Advent of Code 2024 and how they might be solved efficiently in Ruby.
