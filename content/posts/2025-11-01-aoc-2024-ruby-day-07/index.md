---
date: 2025-11-01
title: "Advent of Code 2024 Ruby Solutions: Day 7"
description: |-
  Let's look at how to solve both parts of the Advent of Code 2024 puzzle on day 7.
  This solution is in Ruby, but the principles can be applied to any language.
slug: aoc-2024-ruby-day-07
image: /images/posts/2025-11-01-aoc-2024-ruby-day-07.jpg
tags:
  - Ruby
  - Advent of Code
  - Puzzles
---

Day 7 of Advent of Code 2024 boils down to testing all `left-to-right` operator choices between fixed numbers and summing the targets that are achievable, and a compact `base-k` iterator in Ruby keeps both parts small, clear, and fast.
You can browse the rest of this series under [Advent of Code]({{< ref "/tags/advent-of-code" >}}).
The full source for all of my 2024 solutions lives in [my GitHub repository](https://github.com/sdjmchattie/AdventOfCode2024).

---

## Understanding the Challenge

The task is to determine which calibration equations become true by inserting operators between a fixed sequence of numbers and then sum the targets for all solvable equations.
You can read the full problem description for Day 7 [on the Advent of Code website](https://adventofcode.com/2024/day/7).
Part 1 allows `+` and `*` only and mandates strict `left-to-right` evaluation with no precedence.
Part 2 adds `||` (digit concatenation) while keeping everything else the same.

---

## Parsing the Input

Each line is in the shape `target: n1 n2 n3 ...`, and the script parses this into `[target, [n1, n2, n3, ...]]` pairs.
Also, importantly, the numbers are converted to integers, as this allows mathematical operations to be applied to them.

```ruby
equations = File.readlines('input.txt').map { |line| line.chomp.split(':') }
equations.each do |eq|
  eq[0] = eq[0].to_i
  eq[1] = eq[1].chomp.split(' ').map(&:to_i)
end
```

This structure keeps the `target` and component list together in a convenient format for evaluation.

---

## Core Evaluator: `base-k` Operator Enumeration

The heart of the solution is a predicate that tries every operator assignment for a given equation and returns `true` if any `left-to-right` evaluation hits the target.

```ruby
def valid_equation?(eq, op_count)
  result = eq[0]
  components = eq[1]
  ops_count = components.count - 1
  perms = op_count**(components.count - 1)

  perms.times do |perm|
    evaluated = perm.to_s(op_count).rjust(ops_count, '0').split('').each_with_index.reduce(components[0]) do |acc, e|
      next_val = components[e[1] + 1]
      case e[0]
      when '0'
        acc + next_val
      when '1'
        acc * next_val
      when '2'
        (acc.to_s + next_val.to_s).to_i
      end
    end

    return true if evaluated == result
  end

  return false
end
```

The key idea is to treat an operator plan as a number written in `base-k`, where `k` is the number of operators we are allowed to use.
For `m` numbers there are `m-1` operator slots, so there are `k**(m-1)` possible assignments to enumerate.
The loop converts each integer `perm` to `perm.to_s(op_count)`, `rjust`s it to `ops_count` digits, and then uses `each_with_index` and `reduce` to evaluate the expression strictly `left-to-right`.
The digit to operator mapping is explicit and fixed, with `'0'` meaning `+`, `'1'` meaning `*`, and `'2'` meaning `||`.
The function returns early as soon as a matching evaluation is found, which prunes the search work in many cases.

---

## Part 1: Addition and Multiplication Only

Part 1 asks which equations are solvable when only `+` and `*` are available.
That means `op_count` is `2`, so we explore all `2**(m-1)` assignments and include the `target` in the total if any assignment matches.

```ruby
def part1(equations)
  equations.reduce(0) { |acc, eq| acc + (valid_equation?(eq, 2) ? eq[0] : 0) }
end
```

The script reports execution time using Ruby’s `Benchmark` module and `Benchmark.realtime`.

```ruby
require 'benchmark'

p1_result = nil
p1_time = Benchmark.realtime { p1_result = part1(equations) } * 1000
puts("Part 1 in #{p1_time.round(3)} ms\n  #{p1_result}\n\n")
```

Because evaluation is strictly `left-to-right` and the number order is fixed, a single `reduce` neatly mirrors the problem’s semantics.

---

## Part 2: Adding Concatenation

Part 2 adds the concatenation operator `||`, bringing the operator set to `+`, `*`, and `||`, and thus `op_count` to `3`.
The evaluator already handles this via the `'2'` branch, which glues the digits of the accumulator and the next value using string concatenation and parses the result back to an integer.

```ruby
when '2'
  (acc.to_s + next_val.to_s).to_i
```

With that in place, Part 2 is the same fold over equations but with `op_count` set to `3`.

```ruby
def part2(equations)
  equations.reduce(0) { |acc, eq| acc + (valid_equation?(eq, 3) ? eq[0] : 0) }
end

p2_result = nil
p2_time = Benchmark.realtime { p2_result = part2(equations) } * 1000
puts("Part 2 in #{p2_time.round(3)} ms\n  #{p2_result}\n\n")
```

The enumeration now spans `3**(m-1)` operator assignments per equation, and `left-to-right` evaluation still applies uniformly, so no precedence handling is required.

---

## Implementation Notes

- The `base-k` enumeration compresses the entire search into a simple counter loop without recursion.
- `rjust` on the `to_s(op_count)` representation ensures operator digits align reliably with all positions.
- Concatenation is modelled directly via `acc.to_s + next_val.to_s` and `to_i`, which keeps the intent clear.
- Early return on the first success can cut down work significantly on larger lines.
- Measuring runtime with `Benchmark.realtime` provides quick feedback on overall performance.

---

## Wrapping Up

Both parts reduce cleanly to exhaustive `left-to-right` operator enumeration, and pairing a `base-k` iterator with a single `reduce` keeps the implementation compact and robust.
If you are following along with the series, you can find every entry under [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and you can explore or run the code yourself in [my GitHub repository](https://github.com/sdjmchattie/AdventOfCode2024).
Read the full Day 7 description [on the Advent of Code website](https://adventofcode.com/2024/day/7), then try your own input to see the enumerator adapt as the operator set changes.
