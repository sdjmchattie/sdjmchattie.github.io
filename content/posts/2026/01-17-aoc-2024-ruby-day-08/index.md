---
date: 2026-01-17
title: "Advent of Code 2024 Ruby Solutions: Day 8"
description: |-
  Let's look at how to solve both parts of the Advent of Code 2024 puzzle on day 8.
  This solution is in Ruby, but the principles can be applied to any language.
slug: aoc-2024-ruby-day-08
image: /images/posts/2026/01-17-aoc-2024-ruby-day-08.jpg
tags:
  - Ruby
  - Advent of Code
  - Puzzles
---

Day 8 is about mapping antennas on a 2D grid and marking antinodes where signals resonate in straight lines, first at a single step beyond a pair and then across entire lines.
We will walk through a vector-stepping approach in Ruby that keeps the implementation small, readable, and fast.
If you want the full problem statement can be read on the [Advent of Code puzzle page](https://adventofcode.com/2024/day/8).
You can browse all entries in this series under [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and my complete source for 2024's solutions can be found [on GitHub](https://github.com/sdjmchattie/AdventOfCode2024).

## Day 8 Overview

You are given a rectangular grid where each non-dot character represents an antenna keyed by a frequency character.
Part 1 asks you to consider pairs of antennas with the same frequency and mark antinodes one step further along the line past each antenna in the pair.

Part 2 changes the rule so that every position collinear with at least two antennas of the same frequency becomes an antinode, which includes the antennas themselves.
The official puzzle text and examples are on the [day 8 puzzle page](https://adventofcode.com/2024/day/8) on Advent of Code.

## Parsing the Map and Grouping by Frequency

The solution uses a small grid helper to read the input and present convenient operations over coordinates.
The outer loop iterates every distinct character on the map via `map.all_chars`, skips `'.'`, and fetches all coordinates for that frequency with `map.find(freq)`.
This naturally groups antennas by frequency without extra data structures, and it ensures that uppercase and lowercase characters are treated as different frequencies.

```ruby
antinodes = map.empty_dup

map.all_chars.each do |freq|
  next if freq == '.'

  locs = map.find(freq)
  # process pairs in locs...
end
```

A separate `antinodes` grid holds only the detected antinode positions so that we can count unique locations cleanly at the end.
Because we only ever count from the `antinodes` grid, writes that land out of bounds do not affect the result.

## Part 1: What Needs To Be Computed

For every pair of antennas with the same frequency, compute the vector from the first to the second, and place antinodes one vector step beyond each antenna along that line.
Only positions that fall inside the grid are counted, and overlapping antinodes or antinodes that coincide with antennas are allowed.

### Part 1: Walking Through the Ruby Solution

The core of Part 1 is enumerating unordered antenna pairs and then applying a single add or subtract of the pairwise vector.
We use `each_with_index` and slice `locs[i + 1..]` to avoid duplicate pairings and self-pairs.
The vector components `dx` and `dy` come straight from the coordinate difference.

```ruby
locs.each_with_index do |loc1, i|
  locs[i + 1..].each do |loc2|
    dx = loc2.x - loc1.x
    dy = loc2.y - loc1.y

    antinodes[Grid::Point2D.new(loc1.x - dx, loc1.y - dy)] = '#'
    antinodes[Grid::Point2D.new(loc2.x + dx, loc2.y + dy)] = '#'
  end
end

antinodes.count('#')
```

Subtracting the vector from `loc1` yields the antinode one step before `loc1` along the line, and adding the vector to `loc2` yields the antinode one step after `loc2`.
The `antinodes` grid acts like a set, so repeated writes to the same coordinate are harmless.
Finally, the answer is simply `antinodes.count('#')`.

## Part 2: What Changes

In Part 2, every grid position that is collinear with at least two antennas of the same frequency is an antinode.
That means we extend the pairwise line in both directions across the whole grid using the same step vector.
Antennas themselves become antinodes as long as there are at least two antennas for that frequency.

### Part 2: Walking Through the Ruby Solution

We reuse the same pair enumeration and step vector, but now we walk repeatedly along the line in both directions.
Starting at `loc2` and stepping by `-dx, -dy` marches back through `loc1` and beyond until we leave the grid.
Starting at `loc1` and stepping by `+dx, +dy` marches forward through `loc2` and beyond until we leave the grid.
The `in_bounds?` check guards the loop, and each visited position is stamped into the `antinodes` grid.

```ruby
locs.each_with_index do |loc1, i|
  locs[i + 1..].each do |loc2|
    dx = loc2.x - loc1.x
    dy = loc2.y - loc1.y

    point = loc2
    antinodes[point] = '#' while map.in_bounds?(point = Grid::Point2D.new(point.x - dx, point.y - dy))

    point = loc1
    antinodes[point] = '#' while map.in_bounds?(point = Grid::Point2D.new(point.x + dx, point.y + dy))
  end
end

antinodes.count('#')
```

Because the very first backward step from `loc2` and the very first forward step from `loc1` land on the paired antennas, those antennas are correctly included as antinodes.
As in Part 1, uniqueness falls out from writing into a dedicated `antinodes` grid and counting the `'#'` cells at the end.

## Notes on Utilities and Structure

- `Grid::Grid2D` abstracts reading, indexing, bounds checks via `in_bounds?`, and counting cells with `count`.
- `Grid::Point2D` is a simple coordinate value type used for addressing the grid.
- `map.empty_dup` provides a clean writable grid for antinodes so we never risk mutating the original map.
- Processing by `map.all_chars` combined with `map.find(freq)` guarantees only like-for-like characters are paired.
- The pairwise loop uses `each_with_index` and a trailing slice to enumerate each unordered pair exactly once.

## Running The Script

The entrypoint wires up input, runs both parts, and prints timings using `Benchmark.realtime`.
This scaffolding is not needed for the core logic, but it makes it easy to check performance as puzzle sizes grow.

```ruby
contents = File.readlines('input.txt')
map = Grid::Grid2D.new(contents)

p1_result = nil
p2_result = nil

p1_time = Benchmark.realtime { p1_result = part1(map) } * 1000
p2_time = Benchmark.realtime { p2_result = part2(map) } * 1000

puts("Part 1 in #{p1_time.round(3)} ms\n  #{p1_result}\n\n")
puts("Part 2 in #{p2_time.round(3)} ms\n  #{p2_result}\n\n")
```

## Wrapping Up

Day 8 reduces to clean vector stepping over antenna pairs, with Part 1 marking the immediate antinodes and Part 2 sweeping the entire collinear line.
The small `Grid` helper keeps the bookkeeping tidy, and a dedicated `antinodes` grid lets uniqueness and counting fall out naturally.
If this approach resonates, check out the repository for more daily solutions or pick another entry from the [Advent of Code]({{< ref "/tags/advent-of-code" >}}) tag and try it on your own input.
