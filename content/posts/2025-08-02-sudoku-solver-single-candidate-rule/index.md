---
date: 2025-08-02
title: "Sudoku Series: Implementing the Single Candidate Rule"
description: |-
  NEEDS A DESCRIPTION
slug: sudoku-solver-single-candidate-rule
image: /images/posts/2025-08-02-sudoku-solver-single-candidate-rule.jpg
tags:
  - Python
  - Software Architecture
  - Sudoku Series
---

When solving Sudoku puzzles, a lot of the logic is about spotting patterns among groups of cells.
In this context, a group of cells are those which must not contain a number among them more than once.
Let's build some logic to pick out groups of cells we might want to work with in our solving components.

The current code at the time of writing can be found [on GitHub](https://github.com/sdjmchattie/sudoku-solver/tree/blog/2025-08-02) where you can also see the [pull request](https://github.com/sdjmchattie/sudoku-solver/pull/1) for the changes in this post.

If you like this post and you'd like to know more about how to plan and write Python software, check out the [Python]({{< ref "/tags/python" >}}) tag.
You can also find other posts in the [Sudoku Series]({{< ref "/tags/sudoku-series" >}}).

---

## What is the Single Candidate Rule?

Text

---

## Wrapping up

We've made some good progress here.
The very next thing we're going to be able to do now that we have groupings of cells, particularly for neighbours, is to get the initial candidates right for each cell.
For our very easy puzzle, this should make the puzzle practically solvable.

Our first solver method, coming shortly after the candidate population, will look for cells with only a single candidate.
It will change the definite value of the cell to the single candidate, then it will remove the value from all the candidate lists of neighbours of the cell.

I hope you're as interested as I've been so far in this project.
I honestly hope we can build a fast solver that is capable of some complicated approaches to Sudoku puzzles.
