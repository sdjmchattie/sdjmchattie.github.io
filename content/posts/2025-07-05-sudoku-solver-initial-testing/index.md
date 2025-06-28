---
date: 2025-07-05
title: "Unit Testing Our Python Sudoku Solver"
description: |-
  In this third post of the Sudoku series, we look at how to apply unit testing to our initial implementation.
  By testing our code, we are able to find the places it doesn't behave the way we want and we can therefore fix the logic.
slug: sudoku-solver-initial-testing
image: /images/posts/2025-07-05-sudoku-solver-initial-testing.jpg
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

The current code at the time of writing can be found [on GitHub](https://github.com/sdjmchattie/sudoku-solver/tree/blog/2025-07-05) where you can also see the [differences](https://github.com/sdjmchattie/sudoku-solver/tree/blog/2025-05-17) since the last blog post.

---

## A quick primer

The aim of this post is not to teach you every last detail about unit testing, but if you're new to this area, you'll probably need some information about how unit testing is used.
Let's cover some basics of pytest that will help to explain the rest of this post.

### Test function naming

Test functions should be named starting with `test_` to be automatically discovered by pytest.
Naming them by what they test makes the output from testing much more meaningful and easier to scope out the failures if they happen.

### Asserting truthiness

Use a plain `assert` statement to check if a condition is true.

```python
def test_value_is_positive():
    value = 5
    assert value > 0
```

### Asserting falseness

Similar to truth checks, you can assert that something is not true.

```python
def test_value_is_not_zero():
    value = 5
    assert value != 0
```

### Checking expected return values

Verify that your functions return the expected output.

```python
def add(x, y):
    return x + y

def test_add_sums_its_arguments():
    assert add(2, 3) == 5
```

### Asserting exceptions for bad input

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

### Combining multiple asserts

You can have multiple assertions in one test function as long as they check the same logical behaviour.

```python
def test_values():
    x, y = 3, 4
    assert x < y
    assert x - y < 0
```

### Keep tests focused

While you can have multiple asserts in one test, make sure the test covers a single piece of functionality.
Avoid combining unrelated checks that test different behaviours in the same test function.

---

## Wrapping up

Now that we have completed testing of our existing functionality, we can continue developing our solution in the knowledge that what we've already created will not drift into a broken state.
By running our tests after future changes and adding new tests for new functionality, we can protect ourselves from subtle bugs.

Have you added tests to your own projects?
Does this post help you to know how to do more of it?
If so, remember to share it with others using the buttons at the top of the post so more people can benefit!
