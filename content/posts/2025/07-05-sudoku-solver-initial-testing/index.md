---
date: 2025-07-05
title: "Unit Testing Our Python Sudoku Solver"
description: |-
  In this third post of the Sudoku series, we look at how to apply unit testing to our initial implementation.
  By testing our code, we are able to find the places it doesn't behave the way we want and we can therefore fix the logic.
slug: sudoku-solver-initial-testing
image: /images/posts/2025/07-05-sudoku-solver-initial-testing.jpg
tags:
  - Python
  - Software Architecture
  - Sudoku Series
  - Unit Testing
---

This week we have a new topic for this blog, which is [Unit Testing]({{< ref "/tags/unit-testing" >}}).
While not as exciting as actually writing the functional code for a project, it is an important skill to have.
By writing tests for your code, you get to check that it behaves the way you intended.
Not only does this let you fix the code where it doesn't work correctly, but you can run the unit tests after any future changes to your code and catch any regressions on the functionality.

If you like this post and you'd like to know more about how to plan and write Python software, check out the [Python]({{< ref "/tags/python" >}}) tag.
You can also find the other posts in this series using the [Sudoku Series]({{< ref "/tags/sudoku-series" >}}) tag.

We will be testing the functionality written for the Sudoku Solver from last time.
Remember that we built a simple set of classes that can load a Sudoku input file and store the starting numbers in memory.
It is then able to print the state of the grid to the screen.
While simple, let's see how we can put our code through its paces and find some ways to make it more robust.

The current code at the time of writing can be found [on GitHub](https://github.com/sdjmchattie/sudoku-solver/tree/blog/2025-07-05) where you can also see the [differences](https://github.com/sdjmchattie/sudoku-solver/compare/blog/2025-05-17...blog/2025-07-05) since the last blog post.

---

## A Quick Primer

The aim of this post is not to teach you every last detail about unit testing, but if you're new to this area, you'll probably need some information about how unit testing is used.
Let's cover some basics of pytest that will help to explain the rest of this post.

### Test Function Naming

Test functions should be named starting with `test_` to be automatically discovered by pytest.
Naming them by what they test makes the output from testing much more meaningful and easier to scope out the failures if they happen.

### Asserting Truthiness

Use a plain `assert` statement to check if a condition is true.

```python
def test_value_is_positive():
    value = 5
    assert value > 0
```

### Asserting Falseness

Similar to truth checks, you can assert that something is not true.

```python
def test_value_is_not_zero():
    value = 5
    assert value != 0
```

### Checking Expected Return Values

Verify that your functions return the expected output.

```python
def add(x, y):
    return x + y

def test_add_sums_its_arguments():
    assert add(2, 3) == 5
```

### Asserting Exceptions for Bad Input

Use `pytest.raises()` as a context manager to assert that a particular exception is raised when invalid input is given.
This gives you the opportunity to check your error handling is correct

```python
import pytest

def divide(x, y):
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y

def test_divide_raises():
    with pytest.raises(ValueError):
        divide(10, 0)
```

### Combining Multiple Asserts

You can have multiple assertions in one test function as long as they check the same logical behaviour.

```python
def test_values():
    x, y = 3, 4
    assert x < y
    assert x - y < 0
```

While you can have multiple asserts in one test, make sure the test covers a single piece of functionality.
Avoid combining unrelated checks that test different behaviours in the same test function.

---

## Setup Pytest

Before we can run any tests, we need to set `pytest` up.
Thankfully this is really simple with our Poetry environment.
The following command prepares the installation of `pytest` in our project as a dev dependency.
It should be run from the root of the repository.

```shell
poetry add --dev pytest
```

Now all we need to do to run our tests is execute the following command.

```shell
poetry run pytest
```

`pytest` will search for any test files in our repository and will execute them.

---

## Writing Tests

So in order to write some tests, we need to review our functionality and test accordingly.
We'll start with the classes that have the least dependencies and work our way up.

### The Cell Class

The `Cell` class has an initialiser as well as a getter and setter for the value in the cell and the candidates for the cell.
So let's focus on writing tests around that.
The following are test names and a description of what the test does.
Refer to the repository linked at the start of this post to see the final file.

These tests are written to `tests/model/test_cell.py` and get picked up by `pytest` automatically.

- `test_new_cell_has_no_value` — Call the constructor without arguments and assert the new cell to have no `value` set.
- `test_new_cell_has_candidates_set` — Also assert that the new cell has the standard 1–9 `candidates` set.
- `test_new_cell_value_can_be_set_through_init` — Assert that we can set the `value` via the constructor argument.
- `test_new_cell_value_can_be_set_through_property` — Assert that we can set the `value` on an existing cell.
- `test_cell_with_value_has_no_candidates` — Assert that if the cell is constructed with a `value`, the `candidates` are removed.
- `test_setting_cell_value_removes_candidates` — Assert that if the `value` is set on a cell after construction, the `candidates` are removed.
- `test_cell_value_cannot_be_set_twice` — Assert that setting a `value` on a cell that already has one raises the correct `ValueError`.
- `test_cell_value_cannot_be_set_to_zero` — Assert that setting `0` as the `value` on a cell raises the correct `ValueError`.
- `test_cell_value_cannot_be_set_to_ten` — Assert that setting `10` as the `value` on a cell raises the correct `ValueError`.
- `test_cell_candidates_can_be_set` — Assert that the `candidates` set can be updated.
- `test_cell_candidates_returns_a_copy` — Assert that the `candidates` retrieved from the getter are a copy, not the original set.
- `test_cell_candidates_cannot_be_set_if_value_is_set` — Assert that `candidates` cannot be set when the cell has a `value` and that the correct `ValueError` is raised.
- `test_cell_candidates_cannot_be_set_with_invalid_value_zero` — Assert that the correct `ValueError` is raised when the `candidates` are set with a `0` in the set.
- `test_cell_candidates_cannot_be_set_with_invalid_value_ten` — Assert that the correct `ValueError` is raised when the `candidates` are set with a `10` in the set.

These tests form the core set of tests I would want to apply to this class.
While writing them, I was able to identify a couple of errors in my logic from last time.
This is where the value of tests come in, because those did not show up when I was running the code without tests before.

The main bug I'm talking about is where the setter for `value` gets called with `None` and the `candidates` were being cleared when they shouldn't be.

### The Grid Class

We'll test the `Grid` class similarly to how we tested the `Cell` class, but it's worth noting that we don't test the private methods.
We want to test the public behaviour of the class, not every inner working.

The following is a list of functionality we're writing tests for.

- When constructing a new one with empty values, the grid has empty cells.
- When constructing a new one with numbers throughout, the grid stores those numbers.
- When using the class method for creating a grid from notation, the grid is generated with the correct values.
- When the notation contains unexpected characters, they are treated as empty cells.
- A well defined grid is able to be displayed like a proper Sudoku puzzle.
- A grid that isn't 9x9 should not be accepted.

One bug that was identified here was that a `0` in the input for the `Grid` class tries to create a cell with a zero value, which raises a `ValueError` from the `Cell` class.

A second bug is that the grid allowed any size of numbers, when the `display()` method expects exactly 9x9.

Both these bugs have been fixed now.

### The Main Method

Ideally we'd also write tests for the `main` method, but it mostly just calls the things we've already tested.
The only extra thing it does is reads the contents from a file, and it's not usually a good idea to test file I/O unless you really need to.
In the interests of keeping things simple, we'll assume this bit of the application gets enough of a workout when we're using it.

---

## Test Results

When we run the tests now, we get something that looks similar to the following:

```shell
configfile: pyproject.toml
collected 21 items

tests/model/test_cell.py ..............                   [ 66%]
tests/model/test_grid.py .......                          [100%]

====================== 21 passed in 0.01s ======================
```

As long as we continue to get this result in the future, we know we haven't broken our existing functionality.

---

## Wrapping up

Now that we have completed testing of our existing functionality, we can continue developing our solution in the knowledge that what we've already created will not drift into a broken state.
By running our tests after future changes and adding new tests for new functionality, we can protect ourselves from subtle bugs.

Have you added tests to your own projects?
Does this post help you to know how to do more of it?
If so, remember to share it with others using the buttons at the top of the post so more people can benefit!
