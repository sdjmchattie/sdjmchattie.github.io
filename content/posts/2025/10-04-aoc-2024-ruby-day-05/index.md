---
date: 2025-10-04
title: "Advent of Code 2024 Ruby Solutions: Day 5"
description: |-
  Let's look at how to solve both parts of the Advent of Code 2024 puzzle on day 5.
  This solution is in Ruby, but the principles can be applied to any language.
slug: aoc-2024-ruby-day-05
image: /images/posts/2025-10-04-aoc-2024-ruby-day-05.jpg
tags:
  - Ruby
  - Advent of Code
  - Puzzles
---

Day 5 of Advent of Code 2024 is all about enforcing page ordering rules and pulling the "middle" value out at the right time, and my Ruby solution keeps it tidy with a small helper, a simple validator, and a lightweight reordering trick for the second half.
If you want to browse everything I have done for this event, the series is collected under [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and the full source code for this day and the rest can be found on [GitHub](https://github.com/sdjmchattie/AdventOfCode2024).

---

## Day 5: Print Queue Overview

The [original puzzle](https://adventofcode.com/2024/day/5) provides a set of pairwise ordering constraints between page numbers and a list of "updates," each being a sequence of pages to be printed.
Part 1 asks you to determine which updates already respect all applicable constraints and then sum the middle page number from those valid updates.
Part 2 asks you to take only the invalid updates, reorder each one so that it respects the constraints, and then sum the middle page number of the corrected sequences.

---

## Input Parsing and Data Structures

My solution splits the input into two sections: the rules above a blank line and the updates below it.
Rules are stored in a sparse adjacency list keyed by the "before" page, with each value being the list of pages that must come after it.
Updates are parsed into arrays of strings, one array per update.

```ruby
# Split rules above the blank line and the updates below it.
input = File.readlines('input.txt')
index = input.index("\n")
order = input.shift(index)
input.shift
print_jobs = input.map { |line| line.chomp.split(',') }

# Build adjacency list: before_page => [after_pages...].
rules = SparseArray.new(Array)
order.each do |line|
  before, after = line.chomp.split('|')
  rules[before] << after
end
```

The `SparseArray` helper makes the adjacency structure ergonomic by lazily initialising missing keys to arrays.

```ruby
class SparseArray
  def initialize(value_type, *value_args)
    @store = {}
    @value_type = value_type
    @value_args = value_args
  end

  def [](key)
    @store[key] ||= @value_type.new(*@value_args)
  end

  def []=(key, value)
    @store[key] = value
  end
end
```

---

## Validating an Update Against the Rules

For Part 1 we need a reliable way to tell whether a single update respects all the relevant rules.
The key idea is to walk the update left to right and ensure that no later page is required to appear before an earlier page.

```ruby
def pages_valid(rules, print_job)
  print_job.each_with_index do |page, index|
    print_job[index + 1..].each do |sub_page|
      return false if rules[sub_page].include?(page)
    end
  end
  true
end
```

This checks, for each pair in positional order, that there is no rule of the form "later must come before earlier," which would violate the constraints for the current update.

---

## Part 1: Sum of Middles from Valid Updates

Part 1 requires filtering to only the valid updates and summing their middle values.
Since updates are of odd length, the middle index is simply `(count - 1) / 2`.

```ruby
def part1(rules, print_jobs)
  print_jobs.select { |job|
    pages_valid(rules, job)
  }.sum { |job|
    job[(job.count - 1) / 2].to_i
  }
end
```

This produces the correct total for my input, which the program prints alongside a runtime measured with Ruby’s Benchmark.

---

## Part 2: Fixing the Invalid Updates

For the second half we must correct only the updates that fail the validation and then again extract and sum their middle page numbers.
The reorder in my solution is driven by counting, for each page in the update, how many of its "must come after me" neighbours are also present, and then sorting by that count.

```ruby
def fix_order(rules, print_job)
  print_job.map do |page|
    [page, rules[page].count { |dependents| print_job.include?(dependents) }]
  end.sort_by(&:last).map(&:first)
end
```

Intuitively, this computes a per-page score based on how many pages are constrained to appear after it within this particular update, and then orders pages by that score.
Finally, the Part 2 driver applies that correction to each invalid update and sums the middle values.

```ruby
def part2(rules, print_jobs)
  print_jobs.reject { |job|
    pages_valid(rules, job)
  }.map { |job|
    fix_order(rules, job)
  }.sum { |job|
    job[(job.count - 1) / 2].to_i
  }
end
```

A neat property here is that reversing a sequence does not change its middle element, which means that even if multiple valid orderings exist, the chosen approach still yields the correct middle page for summation.

---

## Notes on Approach

- The validation checks only rules involving pages present in a given update, which matches the problem’s requirement that missing pages imply irrelevant rules.
- The reordering strategy acts like a lightweight topological reordering guided by the number of "after" relations in the current update.
- Because the puzzle asks only for the middle page, this approach is sufficient while remaining straightforward to implement.

---

## Wrapping Up

This day boils down to enforcing precedence constraints per update, first to filter and then to correct, and the Ruby solution uses a compact adjacency structure with a simple validator and reorder pass to keep the implementation clear.
If you want to explore the full code or run it yourself, head to [Advent of Code 2024](https://github.com/sdjmchattie/AdventOfCode2024) and try it on your own input.
If you are following along with the event, you can find the rest of my write-ups under [Advent of Code]({{< ref "/tags/advent-of-code" >}}).
