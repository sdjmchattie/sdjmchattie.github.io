---
date: 2025-08-23
title: "Advent of Code 2024 Ruby Solutions: Day 2"
description: |-
  Let's look at how to solve both parts of the Advent of Code 2024 puzzle on day 2.
  This solution is in Ruby, but the principles can be applied to any language.
slug: aoc-2024-ruby-day-02
image: /images/posts/2025/08-23-aoc-2024-ruby-day-02.jpg
tags:
  - Ruby
  - Advent of Code
  - Puzzles
---

A couple of weeks ago, I published the first post in my Ruby solutions to Advent of Code 2024.
In this second post of the series, we'll tackle Day 2's challenge: "Red-Nosed Reports."
Join me as we explore the problem, understand the requirements, and walk through my Ruby solution step-by-step for both parts of the puzzle.

If you'd like to see the rest of my Advent of Code journey, check out related posts by following the [Advent of Code]({{< ref "/tags/advent-of-code" >}}) tag.
You can also browse the full repository of my solutions [on GitHub](https://github.com/sdjmchattie/AdventOfCode2024).

## Understanding the Puzzle: Red-Nosed Reports

The problem presents us with a list of reports from a nuclear fusion/fission plant referred to as the Red-Nosed reactor.
Each report is a list of integer "levels", such as:

```text
7 6 4 2 1
1 2 7 8 9
9 7 6 2 1
1 3 2 4 5
8 6 4 4 1
1 3 6 7 9
```

Each line is a report, containing a sequence of level readings from the plant.
The engineers want us to determine which of these reports are "safe" based on specific criteria.

For the first part of the puzzle, a report is only safe if **both** of the following are true:

1. Its levels are either strictly increasing or strictly decreasing throughout (all adjacent pairs go in the same direction).
2. The difference between any two adjacent levels is at least 1 but no more than 3 in absolute value.

In other words, if the levels increase, every step must be +1, +2, or +3.
If they decrease, every step must be -1, -2, or -3.
Any report violating those constraints is considered unsafe.

For example, the first report `7 6 4 2 1` is safe because it decreases at every digit with differences of either 1 or 2.
However, `1 2 7 8 9` is unsafe because it jumps from 2 to 7, a difference of 5.

Your challenge is to analyse all the reports and count how many satisfy this safety condition.

## Solving Part 1 with Ruby

My Ruby solution reads input reports into arrays of integers.
For each report, it checks whether the sequence is consistently increasing or decreasing, and whether adjacent level differences fit the allowed range.

Here’s the core logic broken down:

```ruby
def part1(input)
  input.count do |report|
    sign_method = report[1] - report[0] < 0 ? :negative? : :positive?
    report.each_with_index.all? do |level, i|
      next true if i == 0

      diff = level - report[i - 1]
      diff.send(sign_method) && diff.abs <= 3
    end
  end
end
```

- We calculate the difference between the first and second level to establish if the `positive?` or `negative?` sign function should be used for the rest of the values.
- We then iterate over all the values, skipping the first, and ensure that the difference with the previous value returns `true` for the identified method above, and that the difference has an absolute value of 3 or less.
- If all pairs pass the check, the report is considered safe.
- All safe reports pass the check, and the `count` method tallies how many do.

This approach efficiently processes the input and counts the safe reports using Ruby's enumerable methods and concise symbol-based checks.

## Extending to Part 2: The Problem Dampener

Part 2 introduces the "Problem Dampener": a device that allows the safety system to overlook **a single bad level** in an otherwise safe report.
If removing exactly one level from an unsafe report produces a safe report by part 1's criteria, that report can now be considered safe.
One example of this is `1 3 2 4 5`, which would normally be an unsafe report, but removing the 3 gives `1 2 4 5` which is a safe report.

To solve this, my code generates all possible variations of the report with one element removed.
It then checks each variation, and the original report, against the safety criteria from part 1.
If any of the variations are safe, the original report is considered safe too.

The relevant part of the Ruby solution looks like this:

```ruby
def part2(input)
  input.count do |report|
    variations = report.each_index.map { |i| report.dup.tap { |rep_dup| rep_dup.delete_at(i) } }
    ([report] + variations).any? do |r|
      sign_method = r[1] - r[0] < 0 ? :negative? : :positive?
      r.each_with_index.all? do |level, i|
        next true if i == 0

        diff = level - r[i - 1]
        diff.send(sign_method) && diff.abs <= 3
      end
    end
  end
end
```

- The code duplicates the report multiple times, each time removing a different level to simulate the Problem Dampener's effect.
- Using the same logic from Part 1, it checks if at least one version, with one item removed, meets the safety criteria.
- If yes, the report is safe under the new rules.
- The safe reports are counted in the same way as they were for part 1.

This effectively tolerates a single "bad" level, greatly increasing the number of safe reports.

## Wrapping Up

Day 2’s “Red-Nosed Reports” puzzle offers a nice warm-up challenge focusing on sequence validation and tolerating exceptions in data analysis.
By carefully checking directional consistency and differences in values, we can quickly filter safe reports from unsafe ones.
Extending this with the Problem Dampener mechanic adds a compelling twist, allowing for flexible error handling.

While I enjoyed using Ruby for these puzzles, these approaches can be implemented in any language.
If I had to choose another, I'd probably use Python, but I've also used C# and JavaScript in previous years.
Feel free to explore the code yourself in my [GitHub repository](https://github.com/sdjmchattie/AdventOfCode2024) and try it on your input data!

If you want to dive deeper into puzzles like these, don’t forget to follow the [Advent of Code]({{< ref "/tags/advent-of-code" >}}) tag.
