---
date: 2025-04-12
title: "Go Series: Functions and their Parameters / Return Values"
description: |-
  In this fifth post in the Go series, let's take a look at functions, what they are, how we can call them and what to expect them to return.
slug: go-series-functions
image: /images/posts/2025-04-12-go-functions.jpg
tags:
  - Go
  - Go Series
  - Learning
---

This is the fifth post in the Go series.
You can see a list of all of the posts in this series by visiting the [Go Series]({{< ref "/tags/go-series" >}}) tag.
This week we look at functions in Go.

Functions are fundamental building blocks in Go, allowing developers to encapsulate code for reuse and clarity.
They enable the definition of a set of instructions that can be called multiple times throughout your program.

## Defining a Function

In Go, you define a function using the `func` keyword, followed by the function name, parameters (if any), return type (if any), and the function body enclosed in curly braces {}.

Here's a simple example:

```go
package main

import "fmt"

func greet(name string) {
    fmt.Printf("Hello, %s!\n", name)
}

func main() {
    greet("Alice")
}
```

In this example:

`greet` is a function that takes a single parameter `name` of type `string`.
Inside `greet`, we use `fmt.Printf` to print a greeting message.
In the `main` function, we call `greet` with the argument `"Alice"`.
The `main` function is the entry point of the Go application and is what is called first.

## Function Parameters

Functions can have multiple parameters, each with a specific type.
When defining multiple parameters of the same type, you can list the names first, followed by the type.

For example:

```go
func add(a, b int) int {
    return a + b
}
```

Here, `add` takes two parameters `a` and `b`, both of type `int`, and returns an `int` representing their sum.

## Variadic Parameters

Go allows you to define functions with variadic parameters, enabling you to pass a variable number of arguments of the same type.
You define a variadic parameter by using an ellipsis `...` before the type.

For instance:

```go
func sum(numbers ...int) int {
    total := 0
    for _, number := range numbers {
        total += number
    }
    return total
}
```

In this `sum` function:

- `numbers ...int` indicates that `sum` can accept any number of `int` arguments.
- Inside the function, we iterate over `numbers` using a `for` loop and accumulate the total.

Examples of calling `sum` with any number of integer arguments are like so:

```go
func main() {
    fmt.Println(sum(1, 2, 3))        // Outputs: 6
    fmt.Println(sum(10, 20, 30, 40)) // Outputs: 100
}
```

## Return Values

Functions in Go can return multiple values, which is a powerful feature that allows for elegant error handling and results reporting.

Here's an example of a function that returns two values:

```go
func divide(dividend, divisor float64) (float64, error) {
    if divisor == 0 {
        return 0, fmt.Errorf("cannot divide by zero")
    }
    return dividend / divisor, nil
}
```

In this `divide` function:

- We take two `float64` parameters: dividend and divisor.
- The function returns two values: a `float64` result and an `error`.
- If the `divisor` is zero, we return an error using `fmt.Errorf`.
- Otherwise, we return the result of the division and `nil` for the error.

You can use this function as follows:

```go
func main() {
    result, err := divide(10, 2)
    if err != nil {
        fmt.Println("Error:", err)
    } else {
        fmt.Println("Result:", result)
    }
}
```

This will output:

```text
Result: 5
```

If you attempt to divide by zero:

```go
func main() {
    result, err := divide(10, 0)
    if err != nil {
        fmt.Println("Error:", err)
    } else {
        fmt.Println("Result:", result)
    }
}
```

The output will be:

```text
Error: cannot divide by zero
```

## Named Return Values

Go also supports named return values, which can make your functions more readable by specifying the names of the return variables in the function signature.

For example:

```go
func rectangleDimensions(length, width float64) (area, perimeter float64) {
    area = length * width
    perimeter = 2 * (length + width)
    return
}
```

In this `rectangleDimensions` function:

We define two named return values: `area` and `perimeter`, both of type float64.
Inside the function, we assign values to area and perimeter.
The return statement without arguments returns the named values.
You can call this function and use the returned values:

```go
func main() {
    area, perimeter := rectangleDimensions(5, 3)
    fmt.Printf("Area: %.2f\n", area)
    fmt.Printf("Perimeter: %.2f\n", perimeter)
}
```

This will output:

```text
Area: 15.00
Perimeter: 16.00
```

## Wrapping Up

Functions are a cornerstone of Go programming, enabling you to write modular and reusable code.
Understanding how to define functions, use parameters (including variadic parameters), and handle return values will significantly enhance your Go programming skills.
As you continue exploring Go, you'll find that functions provide a robust foundation for building efficient and maintainable applications.
