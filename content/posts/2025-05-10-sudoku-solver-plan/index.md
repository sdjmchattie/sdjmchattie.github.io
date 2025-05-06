---
date: 2025-05-10
title: "Planning to build a Sudoku Solver in Python"
description: |-
  This is the first post in a new series, building an efficient Sudoku solver using Python.
  In this post, we'll explore the problem space and plan the first parts of the software.
  That includes deciding on object-oriented design, a user interface, and formats for input and output.
sslug: planning-a-sudoku-solver
image: /images/posts/2025-05-10-sudoku-solver-plan.jpg
tags:
  - Python
  - Software Architecture
  - Sudoku Series
---

Sudoku is one of those puzzles that captivates anyone who attempts to solve one.
They can range from very easy to fiendishly difficult, despite the rules being relatively simple and never changing.

To be valid, a Sudoku puzzle must have only a single solution — and this constraint actually becomes part of the logic required to solve some of the harder puzzles.
In other words, if you reach a point where the digits can be completed in more than one way without breaking the rules, a previously applied solving step was invalid.
The techniques used to solve them are well-documented and definitive, which means we can write code that follows those same techniques to find that unique solution.

But how do we go about that?
That's what this post is about!

If you like this post and you'd like to know more about how to plan and write Python software, check out the [Python]({{< ref "/tags/python" >}}) tag.
You can also find the other posts in this series using the [Sudoku Series]({{< ref "/tags/sudoku-series" >}}) tag.

This post doesn't aim to explain how Sudoku works in detail, but we will cover some aspects of solving as we progress through the series.
To make the content accessible to everyone, here’s a quick overview of the basic rules:

- Every row in the grid must contain each of the digits 1 to 9 exactly once.
- Every column in the grid must also contain the digits exactly once.
- Every 3×3 block on the grid must also contain the digits exactly once.

The game starts with some values already placed, and your task is to fill in the remaining digits correctly.

With that out of the way, let’s get started!
