---
date: 2025-10-11
title: "Advent of Code 2024 Ruby Solutions: Day 6"
description: |-
  Let's look at how to solve both parts of the Advent of Code 2024 puzzle on day 6.
  This solution is in Ruby, but the principles can be applied to any language.
slug: aoc-2024-ruby-day-06
image: /images/posts/2025-10-11-aoc-2024-ruby-day-06.jpg
tags:
  - Ruby
  - Advent of Code
  - Puzzles
---

Day 6 of Advent of Code 2024 turned out to be trickier than it first looked, but it becomes easier when you can lean on a Grid implementation I built previously.
I'm also able to use a jump-based simulator to keep part two fast and tidy.
You can read the puzzle on [Advent of Code — Day 6](https://adventofcode.com/2024/day/6).
This post explains what each part needs from a solution, then walks through how my Ruby code solves it step by step.

If you want to see the whole series, check out the tag [Advent of Code]({{< ref "/tags/advent-of-code" >}}).
The full source for my solutions is [on GitHub](https://github.com/sdjmchattie/AdventOfCode2024).

---

## Part One: Predict the Patrol

The puzzle provides a rectangular map made of characters, with obstacles marked by `#` and a guard’s starting position indicated with `^` facing up.
The movement rules are simple: if the cell directly ahead is blocked, the guard turns right, otherwise the guard steps forward.
You simulate this until the guard steps off the map, and count how many distinct positions were visited at least once, including the starting cell.

### How my Ruby solution approaches it

I already wrote a small two‑dimensional grid helper to make indexing and searching straightforward, and this solution uses that.
The grid wrapper lets me find the starting position, look up cells safely, and count visited positions at the end.
The core of part one is to walk the guard and mark each visited cell with `X`.

First we implement a tiny direction helper which changes from the direction you're heading, into the direction you'll be facing when you turn right.

```ruby
# ruby
def turn_right(dir)
  { n: :e, e: :s, s: :w, w: :n }[dir]
end
```

The patrol marking function performs the forward/turn logic until the guard exits the grid.
It finds `^`, assumes the guard starts facing north, writes `X` into each visited cell, and stops once the next step would leave the map.
The break condition is driven by reading a `nil` when indexing outside the grid.

```ruby
# ruby
def mark_route(grid)
  loc = grid.find('^').first
  dir = :n

  loop do
    grid[loc] = 'X'

    while grid[loc.move(dir)] == '#'
      dir = turn_right(dir)
    end

    loc = loc.move(dir)

    break unless ['.', 'X'].include?(grid[loc])
  end

  grid
end
```

The part one function simply runs the walker and counts X cells.

```ruby
# ruby
def part1(file_contents)
  marked = mark_route(Grid::Grid2D.new(file_contents))
  marked.count('X')
end
```

As usual, Part One is relatively simple.
It's the trepidation of opening Part Two that can be a thrill or a pain!

---

## Part Two: Force a Loop with One New Obstruction

Now you can add exactly one new `#` anywhere except the starting cell, and you need to count how many placements cause the guard to loop forever inside the map.
The naïve approach is to try a `#` at every open cell, simulate, and detect if a cycle occurs, but that can be slow for larger inputs.
My solution avoids full resimulation for every candidate by turning the patrol into a graph of “turn points” with precomputed jumps, then checking for cycles efficiently.

### Turning movement into jumps between turn points

The key insight in the code is that the guard only changes direction at the cell directly in front of an obstacle, so it is sufficient to model how the guard “jumps” in straight lines from one right‑turn point to the next.
I precompute a mapping from each potential right‑turn cell to the destination cell where the next turn will happen, considering the current obstacles.
This “jump map” replaces step‑by‑step simulation with pointer chasing, which makes cycle detection a set membership problem instead of a full walk.

This function computes jumps created by a single blockage for all four directions.
It starts at the cell you would occupy after turning right around the blockage, then scans forwards until hitting the next obstacle or the edge, recording the destination if that scan stays inside the grid.

```ruby
# ruby
def jumps_from_blockage(blockage, grid)
  jumps = {}

  [:n, :e, :s, :w].each do |dir|
    turn_point = blockage.move(turn_right(dir))
    dest = turn_point

    while ['.', '^'].include?(grid[n_loc = dest.move(dir)])
      dest = n_loc
    end

    next_to_blockage = turn_point == dest
    went_off_grid = grid[n_loc].nil?
    jumps[turn_point] = dest unless next_to_blockage || went_off_grid
  end

  jumps
end
```

### Candidate placements and override jumps

Rather than consider every open cell, I restrict candidates to the cells the guard actually visited in part one, excluding the starting position.
Placing a `#` anywhere else cannot affect the patrol if the guard would never pass it anyway, and the code takes advantage of that fact for speed.
For each candidate, I generate override jumps as if that candidate were a new blockage, then merge them over the baseline jump map built from the original obstacles.
There is also a small pass that seeds extra override edges along straight runs where turning right would lead towards the new blockage, so the merged map accurately reflects how the patrol would flow with the added `#` in place.

### Cycle detection by following jumps

To test a placement, I do not rerun the stepwise simulation.
Instead, I walk the jump map from the starting direction up to the first obstruction, then repeatedly follow jump edges while tracking visited turn points in a `Set`.
If I see a turn point again, a loop exists, and that candidate counts as valid.

Here is the complete structure of part two, excluding the grid helper which was covered briefly in [Day 4]({{< relref "2025-09-20-aoc-2024-ruby-day-04" >}}).

```ruby
# ruby
def part2(file_contents)
  marked = mark_route(Grid::Grid2D.new(file_contents))
  grid = Grid::Grid2D.new(file_contents)

  jumps = {}
  grid.find('#').each { |blockage| jumps.merge!(jumps_from_blockage(blockage, grid)) }

  start_loc = grid.find('^').first

  marked.find('X').reject { |x| x == start_loc }.count do |blockage|
    override_jumps = jumps_from_blockage(blockage, grid)

    [:n, :e, :s, :w].each do |dir|
      dest = blockage.move(dir)
      loc = dest
      next if grid[loc] == '#'

      adj_dir = turn_right(dir)
      loc = loc.move(dir)
      while ['.', '^'].include?(grid[loc])
        adjacent = loc.move(adj_dir)
        override_jumps[loc] = dest if grid[adjacent] == '#'
        loc = loc.move(dir)
      end
    end

    loc = start_loc
    until grid[n_loc = loc.move(:n)] == '#' || n_loc == blockage
      loc = n_loc
    end

    jump_map = jumps.merge(override_jumps)
    seen = Set.new

    until seen.include?(loc) || loc.nil?
      seen << loc
      loc = jump_map[loc]
    end

    seen.include?(loc)
  end
end
```

I found this jump‑based model easier to reason about than stepwise simulation across thousands of candidate placements.

---

## Wrapping Up

Day 6 looks like a simple grid walk, but the search space in part two makes a direct brute force approach less attractive, and a jump map over turn points kept things neat and quick.
If you are following along, [the repository](https://github.com/sdjmchattie/AdventOfCode2024) contains the full code and a tiny benchmarking wrapper so you can run it on your own input and see timings.
You can also explore the rest of the series via the tag [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and of course read the original puzzle at [adventofcode.com](https://adventofcode.com/2024/day/6).
Give this a try on your input and see whether a jump‑based approach helps you keep part two under control too.
