---
date: 2025-08-16
title: "Sudoku Series: Implementing Naked Set Rules"
description: |-
  In this post we implement the naked pair and naked triple rules.
  These will allow solving more complicated Sudoku puzzles.
slug: sudoku-solver-naked-set-rules
image: /images/posts/2025-08-16-sudoku-solver-naked-set-rules.jpg
tags:
  - Python
  - Sudoku Series
  - Puzzles
---

In the last [Sudoku Series blog post]({{< relref "2025-08-02-sudoku-solver-single-candidate-rule" >}}) we implemented the single candidate rule.
In this post, we will look at implementing both the naked pair rule and the naked triple rule.
These are documented alongside more advanced rules on a [Mastering Sudoku website](https://masteringsudoku.com/sudoku-solving-techniques/).

The current code at the time of writing can be found [on GitHub](https://github.com/sdjmchattie/sudoku-solver/tree/blog/2025-08-16) where you can also see the [pull request](https://github.com/sdjmchattie/sudoku-solver/pull/2) for the changes in this post.

If you like this post and you'd like to know more about how to plan and write Python software, check out the [Python]({{< ref "/tags/python" >}}) tag.
You can also find other posts in the [Sudoku Series]({{< ref "/tags/sudoku-series" >}}).

---

## What are the Naked Set Rules?

These rules use logical deduction to identify that two or more cells are in the same block, row, or column; that they each contain the same candidates; and the number of candidates equals the number of cells identified, they form a naked set.
All other cells in the set same scope can no longer contain those candidates.
This is easier to explain with images and specific examples of what we're looking for.

### Naked Pairs

A naked pair is the simplest of these sets.
This occurs when exactly two cells in the same block, row, or column meet the following two criteria:

- They both contain only two candidates.
- The candidates are the same in both cells.

Because these cells must, between them, contain those two values; any others that are neighbours of both cells cannot contain those candidates.

Consider the state of the board when we had only partly solved the Easy puzzle in the previous post.

![Naked Pair Examples](naked_pair_examples.png "A Sudoku grid for a partly solved easy puzzle shows examples of naked pairs in rows.")

In the top row, there are two orange cells which contain the candidates 1 and 2 only.
Therefore those two cells must contain the 1 and the 2 for this row and the blue cell cannot.
Removing the 2 from the blue cell leaves it with just 8 as a candidate.

Similarly, in row 3 there are two green cells with 2 and 4 as the only candidates.
Therefore none of the yellow cells can contain a 2 or a 4.
Removing those candidates reduces one of the yellow cells to a single candidate of 7.

### Naked Triples

A naked triple is really just an extension of the naked pair.
In this case you're looking for three cells in a block, row, or column that share the same three candidates.
Let's once again consider the same partly solved grid.

![Naked Triple Example](naked_triple_example.png "A Sudoku grid for a partly solved easy puzzle shows an example of a naked triple in a column.")

In this case, the three orange cells in the second column all contain combinations of the candidates 2, 3, and 6.
Note that they don't all have to contain all of the candidates, as long as none of them contain any additional candidates.
Because 2, 3, and 6 must exist among these three cells, that means the blue cell cannot contain any of those candidates and it is reduced to the single candidate of 5.

### Naked Singles?

Let's recall what we were doing the other week.
In the single candidate rule, we were finding a cell with a single candidate, setting its value to the candidate and removing the candidate from all neighbouring cells.
That last part is effectively what we're doing with the naked pair and naked triple rules above, just with one cell instead of a set of two or three.
The only difference is that we still don't know which of the two or three candidates go in which specific cell yet.

---

## Applying These Rules



---

## Wrapping up

This is a huge milestone for the project, despite only being able to solve very easy puzzles right now.
We have a solving loop which is capable of applying rules we develop in future weeks.
We also have a way of seeing the state of the grid any time we want.

With these, it would be possible to output a report on how the puzzle was solved, step-by-step, and we could grade the difficulty of the puzzle depending on how many times each type of rule was needed.

Next post for the Sudoku solver will look at other simple rules we can apply such as the hidden single rule.
Have you attempted to implement a solver for your favourite puzzle?
Let me know if this series or any of the other material from the blog were useful to you.
