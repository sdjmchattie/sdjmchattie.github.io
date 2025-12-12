---
date: 2025-11-15
title: "Sudoku Series: Implementing Wing Rules"
description: |-
  In this post we implement the XY-Wing and the XYZ-Wing rules.
  This will allow solving more complicated Sudoku puzzles.
slug: sudoku-solver-wing-rules
image: /images/posts/2025/11-15-sudoku-solver-wing-rules.jpg
tags:
  - Python
  - Sudoku Series
  - Puzzles
---

The next rules to implement for the Sudoku solver are called wing rules.
There are a few of these rules used in solving Sudoku, but some are hard to identify and are for very advanced solves.
The two needed to solve most Sudoku puzzles are called XY-Wing and XYZ-Wing:

- XY-Wing uses a pivot cell with two candidates `XY` and two wing cells, one with the `XZ` candidates and the other the `YZ` candidates.
- XYZ-Wing is similar, but the pivot cell has all three candidates, `XYZ`, in it.

If you like this post and you'd like to know more about how to plan and write Python software, check out the [Python]({{< ref "/tags/python" >}}) tag.

---

## What are the Wing Rules?

The wing rules all involve a pivot cell.
This cell is surrounded by two wing cells which share a house with the pivot cell.
For a better explanation than I'm going to give, check out the [XY-Wing](https://sudopedia.org/wiki/XY-Wing) page and the [XYZ-Wing](https://sudopedia.org/wiki/XYZ-Wing) page from the Sudopedia site.

Let's look at each individually before we look at the solving code!

### XY-Wing

These come in two varieties, either a box-line version or a row-column version.
They both apply with the same pattern though.

The pivot cell must contain exactly two candidates, `X` and `Y`.
The wing cells must share a house with the pivot cell and one must contain candidates `X` and `Z`, while the other contains candidates `Y` and `Z`.
`Z` is the value which can be removed from all other cells that share houses with both wing cells.

Let's look at this pattern with a type 1 XY-Wing where one wing shares a row or column with the pivot cell and the other shares a box.

```text
.-----------.-----------.-----------.
|  *  P  *  |  .  .  W  |  .  .  .  |
|  .  .  .  |  .  .  .  |  .  .  .  |
|  W  .  .  |  *  *  *  |  .  .  .  |
'-----------'-----------'-----------'
```

`P` is the pivot cell and might contain, for example, candidates 1 and 5 (`X` and `Y`) only.
The `W` in the same row might contain only 1 and 9 (`X` and `Z`) as candidates.
The `W` in the same box would have to contain candidates 5 and 9 (`Y` and `Z`) to complete the XY-Wing pattern.

The cells that are visible to both wings are marked with `*` and candidates `Z` (9) can be removed from all of these.

The other form of this pattern is row-column and looks like the following.

```text
.-----------.-----------.-----------.
|  .  .  .  |  .  .  .  |  .  .  .  |
|  .  P  .  |  .  .  W  |  .  .  .  |
|  .  .  .  |  .  .  .  |  .  .  .  |
 ----------- ----------- -----------
|  .  .  .  |  .  .  .  |  .  .  .  |
|  .  .  .  |  .  .  .  |  .  .  .  |
|  .  W  .  |  .  .  *  |  .  .  .  |
'-----------'-----------'-----------'
```

In this case, there are no wings sharing a box with pivot cell.
They still contain the same candidates as before though:

- `P` has only candidates `X` and `Y`
- one `W` cell has only candidates `X` and `Z`
- the other `W` cell has only candidates `Y` and `Z`

In this case, there is only one cell which can be seen by both wings.
The `Z` candidate can be removed from this cell.

### XYZ-Wing

The only difference in this pattern is that the pivot cell contains all the candidates `X`, `Y` and `Z` and one of the wings must share a box with the pivot cell.
The cells which can remove the `Z` candidate must be able to see both wings and the pivot cell in this pattern.

Let's look at an example.

```text
.-----------.-----------.-----------.
|  *  P  *  |  .  .  W  |  .  .  .  |
|  .  .  .  |  .  .  .  |  .  .  .  |
|  W  .  .  |  .  .  .  |  .  .  .  |
'-----------'-----------'-----------'
```

- The pivot cell, `P`, must contain only candidates `X`, `Y` and `Z`.
- One wing must contain only `X` and `Z` candidates.
- The other wing must contain only `Y` and `Z` candidates.

It looks very similar to the XY-Wing pattern above in a box-line arrangement.
However, the affected cells in the middle box are no longer valid to remove the `Z` candidate from.

---

## Implementing the Rules

The current code at the time of writing can be found [on GitHub](https://github.com/sdjmchattie/sudoku-solver/tree/blog/2025-11-15) where you can also see the [pull request](https://github.com/sdjmchattie/sudoku-solver/pull/6/files) for the changes in this post.
I also tidied up the tests for the `solver.py` file in this pull request as they were getting unmanageable.

### Finding XY-Wings

```python
applied = False

# Find an XY-Wing pattern.
for pivot in [cell for cell in grid if len(cell.candidates) == 2]:
    xy = pivot.candidates

    # Wings must have 2 candidates and share only one with the pivot.
    wings = [
        wing
        for wing in grid.get_neighbours(pivot)
        if len(wing.candidates) == 2 and len(xy.difference(wing.candidates)) == 1
    ]

    for wing1, wing2 in combinations(wings, 2):
        # Reject the wings if they don't share a symmetric difference with the pivot.
        if wing1.candidates.symmetric_difference(wing2.candidates) != xy:
            continue

        # Find a z-value common to both wings.
        z_set = wing1.candidates.intersection(wing2.candidates)
        if len(z_set) != 1:
            continue
        z = z_set.pop()

        # Eliminate z from cells that see both wings of the XY-Wing.
        wing1_neighbours = grid.get_neighbours(wing1)
        wing2_neighbours = grid.get_neighbours(wing2)
        common_neighbours = wing1_neighbours.intersection(wing2_neighbours)

        for cell in [
            cell
            for cell in common_neighbours
            if z in cell.candidates and cell != pivot
        ]:
            cell.candidates -= {z}
            applied = True

return applied
```

Let's go over how this works:

- Line 1 sets us up with a variable to return if we make any changes to the grid.
- Line 4 iterates over potential pivots from all cells in the grid that have exactly 2 candidates.
- Line 5 defines a set containing the `XY` candidates.
- Lines 8 to 12 establishes a list of possible wings, where they must be neighbours of the pivot cell, must have exactly 2 candidates, and only contain one of the `XY` candidates.
- Line 14 iterates over pairs of potential wings.
- In lines 16 and 17, if the two wings do not contain `X` and `Y` candidates between them, they are skipped as they don't fit the pattern.
- Lines 20 to 23 reject a pair of wings if they don't also contain the same `Z` candidate.
- Lines 26 to 28 are only reached if the pattern matches, and they work out which cells could have the `Z` candidate removed from them.
- Lines 30 to 36 remove the `Z` candidate from the identified cells, if they contain it.
  If this is possible, the `applied` variable is changed to `True` as the grid was changed.

### Finding XYZ-Wings

```python
applied = False

# Find an XYZ-Wing pattern.
for pivot in [cell for cell in grid if len(cell.candidates) == 3]:
    xyz = pivot.candidates

    # Wings must have 2 candidates that are a subset of the pivot's candidates.
    wings = [
        wing
        for wing in grid.get_neighbours(pivot)
        if len(wing.candidates) == 2 and wing.candidates.issubset(xyz)
    ]

    for wing1, wing2 in combinations(wings, 2):
        # Find the z-value common to both wings.
        z_set = wing1.candidates.intersection(wing2.candidates)
        if len(z_set) != 1:
            continue
        z = z_set.pop()

        # Eliminate z from cells that see all three of the XYZ-Wing cells.
        pivot_neighbours = grid.get_neighbours(pivot)
        wing1_neighbours = grid.get_neighbours(wing1)
        wing2_neighbours = grid.get_neighbours(wing2)
        common_neighbours = pivot_neighbours.intersection(
            wing1_neighbours
        ).intersection(wing2_neighbours)

        for cell in [cell for cell in common_neighbours if z in cell.candidates]:
            cell.candidates -= {z}
            applied = True

return applied
```

This logic is almost identical to the logic for an XY-Wing with the following differences:

- Line 4 finds pivot cells as those with exactly 3 candidates.
- Line 11 identifies wing cells as those who have 2 candidates, both of which have to be shared with the pivot.
- Line 22 to 27 find the cells that can have the `Z` candidate removed by finding those which share a house with the pivot and both wing cells.

---

## Testing Our Code

The tests are very similar to other rules we've created.
In each case, I check that we can find the wings we expect to find, that we get a `True` result when a wing was found, that we get a `False` result when there is no wing, and that we get a `False` result when the grid is complete.

---

## Solving Puzzles

Running the new code against our existing "expert" puzzles shows that we can now solve the one labelled `expert_02` so we've made progress!
The other two expert puzzles still do not fully solve, but they are more solved than they were before these rules.
We still need to implement more rules.

---

## Wrapping Up

We've implemented and applied the XY-Wing and the XYZ-Wing rules for our Sudoku solver.
I've checked what's blocking us from solving the other expert puzzles and it seems like the next step to solve these requires the [Nishio](https://www.sudopedia.org/wiki/Nishio) approach.
We'll have a go at implementing this next time we work on the solver.
I'm a little disappointed that this technique is needed because it's less about logic, and more about trial and error.

We'll take a look at an approach to that next time.
