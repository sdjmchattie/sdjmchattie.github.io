---
date: 2025-09-27
title: "Sudoku Series: Implementing the Fish Rules"
description: |-
  In this post we implement the fish rules.
  This will allow solving more complicated Sudoku puzzles.
slug: sudoku-solver-fish-rules
image: /images/posts/2025-09-27-sudoku-solver-fish-rules.jpg
tags:
  - Python
  - Sudoku Series
  - Puzzles
---

The next rules to implement for the Sudoku solver are called the fish rules.
There are three versions of these rules but they all share the same principles:

- X-Wing works with a 2x2 fish pattern.
- Swordfish works with a 3x3 fish pattern.
- Jellyfish works with a 4x4 fish pattern.

If you like this post and you'd like to know more about how to plan and write Python software, check out the [Python]({{< ref "/tags/python" >}}) tag.

---

## What are the Fish Rules?

The fish rules are complicated to explain, and you might want to refer to Sudopedia's [X-Wing](https://www.sudopedia.org/wiki/X-Wing), [Swordfish](https://www.sudopedia.org/wiki/Swordfish), and [Jellyfish](https://www.sudopedia.org/wiki/Jellyfish) explanations.
I will attempt to explain concisely.

In the row version of a fish, we are looking for a number of rows, *n*, which have exactly *n* columns for a candidate.
All the rows must contain those candidates in the same columns for it to be valid.
There are exceptions where you can have missing candidates, but those are even harder to explain so I won't try to do it here.
This can also all be applied to columns instead of rows.

Once a fish is found, we can identify that all other cells in the secondary axis will not contain the candidate.
For clarification, that's all other cells in the columns in the first example above, and all other cells in the rows in the second example.

Let's look at specific examples!

### 2x2 X-Wing

Let's assume that `X` in the diagram below represents a cell with a candidate value in it and that `-` represents that a cell does not contain that candidate.
What we're seeing here is that the second and seventh row of the grid both only have that candidate in the `X` position.
This is an X-Wing!

```text
.-----------.-----------.-----------.
|     *     |        *  |           |
|  -  X  -  |  -  -  X  |  -  -  -  |
|     *     |        *  |           |
 ----------- ----------- -----------
|     *     |        *  |           |
|     *     |        *  |           |
|     *     |        *  |           |
 ----------- ----------- -----------
|  -  X  -  |  -  -  X  |  -  -  -  |
|     *     |        *  |           |
|     *     |        *  |           |
'-----------'-----------'-----------'
```

There are only two ways those candidates can fit into the rows.
Either they're top-left and bottom-right, or they're top-right and bottom-left.
Either way, the columns involved cannot contain that candidate anywhere else in them.
So everywhere we see a `*`, the candidate definitely doesn't exist and it can be removed.

As already mentioned, this could be treated the other way around.
If the `*` cells do not contain the candidate, you then have an X-Wing fish in columns 2 and 6.
Then the cells marked with `-` should have the candidate removed from them by following the same logic.

### 3x3 Swordfish

The Swordfish is really no different from the X-Wing other than is involves three rows with the candidate only present in the same three columns.
Here's an example.

```text
.-----------.-----------.-----------.
|     *     |        *  |     *     |
|  -  X  -  |  -  -  X  |  -  X  -  |
|     *     |        *  |     *     |
 ----------- ----------- -----------
|  -  X  -  |  -  -  X  |  -  X  -  |
|     *     |        *  |     *     |
|     *     |        *  |     *     |
 ----------- ----------- -----------
|  -  X  -  |  -  -  X  |  -  X  -  |
|     *     |        *  |     *     |
|     *     |        *  |     *     |
'-----------'-----------'-----------'
```

Like before, the `X` cells are the only ones in those rows that contain the candidate.
Once those are filled in with the candidate, the columns are no longer able to contain the candidate elsewhere, and we can remove the candidate from the cells marked with a `*`.

From the Swordfish and beyond, it's possible to have the candidate missing in some positions and still apply the rule.
Let's look at an example.

```text
.-----------.-----------.-----------.
|     *     |        *  |     *     |
|  -  X  -  |  -  -  -  |  -  X  -  |
|     *     |        *  |     *     |
 ----------- ----------- -----------
|  -  -  -  |  -  -  X  |  -  X  -  |
|     *     |        *  |     *     |
|     *     |        *  |     *     |
 ----------- ----------- -----------
|  -  X  -  |  -  -  X  |  -  -  -  |
|     *     |        *  |     *     |
|     *     |        *  |     *     |
'-----------'-----------'-----------'
```

Note how some of the `X` cells now do not contain the candidate.
However, the remaining candidates still occupy three columns and the Swordfish is still valid.
The cells marked with a `*` still cannot contain the candidate any more.

### 4x4 Jellyfish

The principles are the same so I won't try to explain, I'll just show an example.

```text
.-----------.-----------.-----------.
|     *     |  *     *  |     *     |
|  -  X  -  |  X  -  X  |  -  X  -  |
|     *     |  *     *  |     *     |
 ----------- ----------- -----------
|  -  X  -  |  X  -  X  |  -  X  -  |
|     *     |  *     *  |     *     |
|     *     |  *     *  |     *     |
 ----------- ----------- -----------
|  -  X  -  |  X  -  X  |  -  X  -  |
|     *     |  *     *  |     *     |
|  -  X  -  |  X  -  X  |  -  X  -  |
'-----------'-----------'-----------'
```

There are now 4 rows with candidates in the same 4 columns, or vice versa.
The cells in the secondary direction can have the candidate removed.

---

## Implementing the Rules

The current code at the time of writing can be found [on GitHub](https://github.com/sdjmchattie/sudoku-solver/tree/blog/2025-09-27) where you can also see the [pull request](https://github.com/sdjmchattie/sudoku-solver/pull/5/files) for the changes in this post.
It is worth noting that the `test` folder was renamed `tests` in this pull request so those file changes can be ignored.

### Fish in Rows

The implementation is in two parts, almost identical.
First we check for fish in rows, as shown here.
`size` is a parameter passed into the function indicating which type of fish we're looking for.

```python
applied = False

# Check rows for fish patterns
for candidate in range(1, 10):
    rows_with_candidate = [
        r
        for r in range(9)
        if sum(1 for c in range(9) if candidate in grid[Point(c, r)].candidates) > 0
    ]
    if len(rows_with_candidate) < size:
        continue

    for row_comb in combinations(rows_with_candidate, size):
        cols = {
            c
            for r in row_comb
            for c in range(9)
            if candidate in grid[Point(c, r)].candidates
        }

        if len(cols) == size:
            # Found a fish pattern
            for c in cols:
                for r in range(9):
                    if (
                        r not in row_comb
                        and candidate in grid[Point(c, r)].candidates
                    ):
                        grid[Point(c, r)].candidates -= {candidate}
                        applied = True
```

Let's go over an explanation of this implementation:

- The `applied` variable will allow us to return the correct value at the end of applying the rule.
  Returning `True` means we've been able to make a change to the grid using the rule.
- Line 4 lets us investigate each of the possible candidates, 1 through 9.
- Lines 5–9 finds the indexes of rows that have any cells with the given candidate.
- On lines 10 and 11, if we have fewer rows with a candidate than the size of fish we're looking for, we move on to the next candidate value.
- Line 13 takes all possible combinations of the rows discovered earlier, in groups the size of the fish we're looking for.
- Lines 14–19 follow similar logic to lines 5–9 to find the indexes of columns containing the candidate.
- Line 21 checks that we have the same number of columns as the size of fish we're looking for.
  If this check passes, we have definitely found a fish!
- The remaining lines go over the discovered columns, stripping the candidate where it exists in rows other than the ones containing the fish.
  `applied` is changed to `True` when a removal occurs.

### Fish in Columns

The rest of the function applying the rule uses almost identical logic, swapping rows and columns.

```python
# Check columns for fish patterns
for candidate in range(1, 10):
    cols_with_candidate = [
        c
        for c in range(9)
        if sum(1 for r in range(9) if candidate in grid[Point(c, r)].candidates) > 0
    ]
    if len(cols_with_candidate) < size:
        continue

    for col_comb in combinations(cols_with_candidate, size):
        rows = {
            r
            for c in col_comb
            for r in range(9)
            if candidate in grid[Point(c, r)].candidates
        }

        if len(rows) == size:
            # Found a fish pattern
            for r in rows:
                for c in range(9):
                    if (
                        c not in col_comb
                        and candidate in grid[Point(c, r)].candidates
                    ):
                        grid[Point(c, r)].candidates -= {candidate}
                        applied = True
```

The logic is the same as above, so I won't break it down line by line.

---

## Testing Our Code

The tests are very similar to other rules we've created.
I chose to break them down into the three types of fish, despite being the same function for all three.
In each case, I check that we can find a fish in rows, that we can find a fish in columns, that we get a `True` result when the fish was found, that we get a `False` result when there is no fish, and that we get a `False` result when the grid is complete.

---

## Solving Puzzles

I've added some extra puzzle files, taken from those on Sudopedia, where the puzzle can only be solved if you have an implementation for the type of fish.
In all these cases, our solver now works!
In fact, disabling the fish of the needed size demonstrates that we couldn't solve these before.

We still cannot solve the expert puzzles generated weeks ago.

---

## Wrapping Up

Although we've handled the simplest types of fish in this post, there are more complicated type of fish we should look at implementing next.
These include the [Finned Fish](https://www.sudopedia.org/wiki/Finned_Fish) and the [Sashimi Fish](https://www.sudopedia.org/wiki/Sashimi_Fish).

Again, it is unclear whether these are what we need to be able to solve our remaining puzzles.
We will find out when we implement the rules.
