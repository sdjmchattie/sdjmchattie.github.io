---
date: 2026-02-21
title: "Sudoku Series: Nishio Rule"
description: |-
  In this post we implement the Nishio rule.
  This will allow solving all remaining puzzles.
slug: sudoku-solver-nishio-rule
image: /images/posts/2026/02-21-sudoku-solver-nishio-rule.jpg
tags:
  - Python
  - Sudoku Series
  - Puzzles
---

The next rule to implement for the Sudoku solver is Nishio.
This will make all outstanding puzzles solvable because it effectively brute forces the removal of an invalid candidate until other rules can take over.

If you like this post and you'd like to know more about how to plan and write Python software, check out the [Python]({{< ref "/tags/python" >}}) tag.

---

## What Is The Nishio Rule?

Nishio is described as a last-resort approach [on Sudopedia](https://www.sudopedia.org/wiki/Nishio), and we will treat it as such.
Effectively you employ this technique when you've exhausted all your other rules and you need to find another way to make progress.

The rule considers candidates for cells that haven't been solved yet, with a particular focus on those with fewer candidates remaining.
After selecting one, you start solving the puzzle again with that candidate removed.
If the puzzle reaches an invalid state, you know that candidate was not correct and can go back to the puzzle before this analysis and remove the candidate.

Clearly this is easier for a computer to do than when doing a puzzle by hand.
But for most puzzles, you shouldn't have many unsolved cells by the time you reach this state.

---

## Implementing The Rule

The current code at the time of writing can be found [on GitHub](https://github.com/sdjmchattie/sudoku-solver/tree/blog/2026-02-21) where you can also see the [pull request](https://github.com/sdjmchattie/sudoku-solver/pull/7/files) for the changes in this post.

I used Claude Code on this project to see what it is capable of.
I plan to write a future article about the use of AI tools during software engineering.

### Finding removable candidates

```python
def apply_nishio_rule(grid: Grid) -> bool:
    unsolved = sorted(
        (cell for cell in grid if cell.value is None),
        key=lambda c: len(c.candidates),
    )

    for cell in unsolved:
        for candidate in cell.candidates:
            trial_grid = grid.duplicate()
            trial_cell = trial_grid[cell.coord]
            if trial_cell is None:
                continue

            set_cell_value(trial_grid, trial_cell, candidate)

            solver = Solver(trial_grid, use_nishio=False)
            solver.solve()

            if not solver.is_valid():
                cell.candidates -= {candidate}
                return True

    return False
```

Let's go over how this works:

- Lines 2–5 sort unsolved cells by the number of candidates they have left.
- Line 7 loops through the unsolved cells, focussing on the lower candidate count cells.
- Line 8 loops through the candidates for the cell.
- Lines 9–12 duplicate the grid and extract the cell being tested.
- Line 14 applies the candidate as a final value on the cell.
- Lines 16–17 continue the solving process with Nishio turned off.
  This will result in either a solved grid or a new blocked state.
- Lines 19–21 validate that we didn't end up with an invalid grid, and returns `True` after the candidate is removed from the original grid.
- If we reach line 23, we can't use Nishio for this solve.
  This shouldn't happen, but we don't want an infinite loop.

### Adding the rule to the solver

I moved the application of the rules in sequence into the `rules` module.
This feels less like a Solver concern and it can focus on applying the loop over these rules instead.

```python
def apply(grid: Grid, include_nishio: bool = True) -> bool:
    applied = (
        apply_single_candidate_rule(grid)
        or apply_naked_pairs_rule(grid)
        or apply_naked_triples_rule(grid)
        or apply_hidden_single_rule(grid)
        or apply_hidden_pairs_rule(grid)
        or apply_hidden_triples_rule(grid)
        or apply_locked_candidates_rule(grid)
        or apply_fish_rule(grid, size=2)
        or apply_fish_rule(grid, size=3)
        or apply_fish_rule(grid, size=4)
        or apply_xy_wing_rule(grid)
        or apply_xyz_wing_rule(grid)
    )

    if not applied:
        if include_nishio:
            from rules.nishio_rule import apply_nishio_rule

            applied = apply_nishio_rule(grid)

    return applied
```

The key lines are 15 through 21.
Note that we don't just apply the rule at the end of the existing rules as it involves extra checks.
First, we don't want to use the rule if others were applied.
Second, we don't want to apply the rule if `include_nishio` was `False`.
This allows us to turn off Nishio when applying the Nishio rule.

We also only import `apply_nishio_rule` if these conditions are satisfied.
If we don't, we can't import this rule applying method from inside the `Solver` or we'd get a circular import.
`Solver` imports this method, which would import `apply_nishio_rule` which imports the `Solver` to apply the rule.

---

## Testing Our Code

The tests are fairly similar to the ones created for previous rules.
The only big changes here are about separating the `Solver` from the `apply` method which also simplifies those rules.
Claude did most of these test refactors for me.

---

## Solving Puzzles

Running the new code against our puzzles shows that we can now solve all of them.
The ones that wouldn't solve before do take a short time longer than other solves, but this is the nature of brute-forcing a solution.
This is why I wanted the solver to use human-like approaches instead of brute-forcing the whole puzzle.

---

## Wrapping Up

We've implemented and applied the Nishio rule for our Sudoku solver.
Given that it now solves all the puzzles we throw at it, this concludes our solver and I won't be coming back to this series for solving functionality.
I might come back to this to build a UI for the application.
