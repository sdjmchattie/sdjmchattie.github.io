---
date: 2025-09-20
title: "Advent of Code 2024 Ruby Solutions: Day 4"
description: |-
  Let's look at how to solve both parts of the Advent of Code 2024 puzzle on day 4.
  This solution is in Ruby, but the principles can be applied to any language.
slug: aoc-2024-ruby-day-04
image: /images/posts/2025/09-20-aoc-2024-ruby-day-04.jpg
tags:
  - Ruby
  - Advent of Code
  - Puzzles
---

Day 4 of Advent of Code 2024 turns a simple word search into a neat grid‑traversal exercise, and my Ruby solution keeps it readable, fast, and precise.
This post explains the requirements for both parts, then walks through how the code solves them, including how diagonals and boundaries are handled.
If you want to browse the rest of my Advent of Code write‑ups, head over to the tag page at [Advent of Code]({{< ref "/tags/advent-of-code" >}}).
You can also dive straight into the full source for every day at https://github.com/sdjmchattie/AdventOfCode2024.

---

## Part 1 — Counting every “XMAS” in the grid

The first half asks you to count every straight‑line occurrence of the string XMAS in a rectangular grid, covering all eight directions and both orientations, and you can read the full brief here for flavour and examples: https://adventofcode.com/2024/day/4.
My approach is to scan every coordinate, begin directional checks only when the current character is `X`, and then look ahead along each direction for the next three characters to see if they form `MAS`.
Because we search all eight directions, reversed words are covered by looking “the other way” without any extra branching.

```ruby
def part1(input)
  input.width.times.sum do |x|
    input.height.times.sum do |y|
      point = Grid::Point2D.new(x, y)
      next 0 unless input[point] == 'X'

      Grid::DIRECTIONS.keys.count do |direction|
        input.adjacent_values_in_direction(point, direction).join.start_with?('MAS')
      end
    end
  end
end
```

- `input` is an instance of `Grid::Grid2D`, which is a small helper class I created for handling 2D grids of information such as this character matrix.
- The nested loops iterate the full grid and construct a `Grid::Point2D` for index access via `input[point]`.
- We short‑circuit unless the current cell is `X`, which avoids unnecessary work.
- For each direction in `Grid::DIRECTIONS`, we call `input.adjacent_values_in_direction(point, direction)` to pull the straight‑line run of characters after the starting point.
- Joining the run and testing `start_with?('MAS')` is equivalent to asking whether `X` plus those three characters spells `XMAS`.
- Edge cells are naturally safe because truncated runs cannot start with `MAS`, so they simply do not count.

---

## Part 2 — Detecting “X‑MAS” crosses

The second half pivots to finding an X shape made from two diagonal instances of `MAS` that cross at their shared centre, with each diagonal allowing either orientation (`MAS` or `SAM`), and only the diagonals matter this time, and the full description is here: https://adventofcode.com/2024/day/4.
A valid X looks like this, where the diagonals are each a `MAS` in either direction and the centre is the shared `A`.

```text
M.S
.A.
M.S
```

Rather than scan every direction from every cell, the solution treats each `(x, y)` as the potential upper‑left of the 3×3 window that could contain an X and then checks the two diagonals that would form that X.

```ruby
def part2(input)
  input.width.times.sum do |x|
    input.height.times.count do |y|
      ne_word = input.adjacent_values_in_direction(Grid::Point2D.new(x, y), :ne, including_self: true).join
      next false unless ne_word.start_with?('MAS') || ne_word.start_with?('SAM')

      se_word = input.adjacent_values_in_direction(Grid::Point2D.new(x, y - 2), :se, including_self: true).join
      se_word.start_with?('MAS') || se_word.start_with?('SAM')
    end
  end
end
```

- `input` is the same `Grid::Grid2D` instance, so all traversal helpers apply here too.
- We first gather the north‑east diagonal from `(x, y)` including the starting cell by setting `including_self: true`, and we accept it if it starts with `MAS` or `SAM`.
- We then gather the south‑east diagonal from `(x, y - 2)` including the starting cell, again accepting `MAS` or `SAM`.
- The offset `(x, y - 2)` deliberately aligns the two diagonals so they intersect at the same centre cell, forming the 3×3 X with the centre at `(x + 1, y - 1)`.
- Boundaries remain safe because diagonals that do not have three characters cannot start with `MAS` or `SAM`, so they simply evaluate to false.
- Because both diagonals are coupled around the same centre, we do not need any extra bookkeeping for overlaps.

---

## Grid helpers and structure

The code relies on a small utility module for clarity and reuse, and `input` is an instance of `Grid::Grid2D`, which is a class created specifically for handling 2D grids of information.
`Grid::Grid2D` exposes `width`, `height`, index access via `input[Grid::Point2D.new(x, y)]`, a direction map in `Grid::DIRECTIONS`, and a traversal utility `adjacent_values_in_direction(point, direction, including_self: false)`.
In Part 1 we exclude the starting cell because we have already verified it is `X`, and in Part 2 we include it so the three collected characters are exactly the diagonal `MAS` or `SAM`.

```ruby
# Example of collecting a diagonal run including the starting cell.
chars = input.adjacent_values_in_direction(Grid::Point2D.new(x, y), :ne, including_self: true)
word  = chars.join
```

This small abstraction keeps the puzzle logic tidy while centralising boundary handling and directional movement.

---

## Wrapping Up

Part 1 reduces neatly to scanning from each `X` in eight directions and checking for `MAS` ahead, while Part 2 locks two diagonals together to recognise X‑shaped `MAS` pairs with either orientation.
The `Grid::Grid2D` helper makes traversal intent clear, keeps the loops compact, and lets boundary cases fall out naturally from the prefix checks.
If you enjoyed this, browse the rest of the write‑ups at [Advent of Code]({{< ref "/tags/advent-of-code" >}}), or explore the full source for every day in my repo at https://github.com/sdjmchattie/AdventOfCode2024.
