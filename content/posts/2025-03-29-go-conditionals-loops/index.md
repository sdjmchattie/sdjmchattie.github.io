---
date: 2025-03-29
title: "Go Series: Conditional Statements and Loops"
description: |-
  In this fourth post in the Go series, let's take a look at how we can control the flow of the application by using conditional statements and loops; responding to the data we encounter at run time.
slug: go-series-conditionals-and-loops
image: /images/posts/2025-03-29-go-conditionals-loops.jpg
tags:
  - Go
  - Go Series
  - Learning
---

This is the fourth post in the Go series.
You can see a list of all of the posts in this series by visiting the [Go Series]({{< ref "/tags/go-series" >}}) tag.
This week we look at conditional statements and loops in Go.
These allow us to change the flow of the process according to data we encounter at run time and to iterate over all the items in an aggregate data type.

Control flow is an essential part of any programming language, and Go provides a clean and efficient way to handle decision-making and looping constructs.
In this article, we’ll explore conditionals (`if`, `switch`) and loops (`for`), along with real-world examples to demonstrate their usage.

## Conditionals

### The `if` statement

The if statement allows you to execute code based on a condition.
Here’s a basic example:

```go
package main
import "fmt"

func main() {
    num := 10
    if num % 2 == 0 {
        fmt.Println("Even number")
    }
}
```

In this example, a variable called `num` is declared and defined with the value `10`.
An `if` statement checks whether there is a left over when dividing the number by `2`.
If there is not, it must mean the number was even, and that is output to the screen for even numbers like `10`.

### The `if-else` statement

`if-else` lets you define two blocks.
One is identical to the `if` block which performs some actions when the condition is `true`.
The second one, marked `else`, is a block which is performed when the conditional was `false`.
Only one or the other block will be performed as the check is only done one time at the `if` line.

To refine the `main()` function of our example:

```go
func main() {
    num := 7
    if num % 2 == 0 {
        fmt.Println("Even number")
    } else {
        fmt.Println("Odd number")
    }
}
```

The same check as before is performed to identify whether `num` is even or not.
When it is (`if`), we state that it is an even number, and when it is not (`else`) we state that it is an odd number.

### The `if-else if-else` ladder

When there are multiple possible truths that should be checked, you can use a pattern of `if`, followed by one or more `else if` checks and one final optional `else`.
All but the `else` block must also provide another condition to check against.
Only one of the blocks will be executed (or perhaps none, if there was no `else` block).
Once a block has successfully matched the situation, all the others are ignored.

To give an example:

```go
func main() {
    age := 25
    if age < 18 {
        fmt.Println("Minor")
    } else if age < 65 {
        fmt.Println("Adult")
    } else {
        fmt.Println("Senior")
    }
}
```

In this `main()` function, an age is set on a variable which will be used in the conditions.
On the `if` line, a check is done to find out whether the age is lower than `18`, and when it is, the word "Minor" is output to the screen.
On the `else if` line, a new condition is applied to see whether the age is lower than 65, and when it is, the word "Adult" is output to the screen.
Finally, the `else` block is used when neither of the previous conditions was true, and this outputs the word "Senior" to the screen.

Note that an age of `16` would only trigger the "Minor" output and not the "Adult" output, even though the conditional for "Adult" also matches the age.
Only one block can be performed in this pattern.

### Short variable declaration in `if`

You'll recall, and have seen in the above examples, that variables can be defined in shorthand by using `variableName := "value"`.
This syntax can also be used as part of the conditional check in an `if` statement.
Let's look at an example:

```go
func main() {
    if num := 10; num > 5 {
        fmt.Printf("%d is greater than 5", num)
    }
}
```

In this `main()` function, the first part of the `if` line is setting the value of `num` to `10`.
The second part, after the semi-colon, checks of `num` is greater than `5`.
Obviously it is and the text is output to the screen.

What this allows you to do is to assign the value during the conditional check and then use the assigned value inside the block.
This can be seen in the example where we're able to refer to `num` in the text output to the screen.

### The `switch` statement

The `if`, `else if`, `else` ladder can get clumsy quite quickly.
For this another conditional statement, `switch`, is available.
It lets you match against lots of different values in a very similar manner, but is easier to read.

Let's look at an example:

```go
func main() {
    day := "Monday"
    switch day {
    case "Monday":
        fmt.Println("Start of the workweek!")
    case "Friday":
        fmt.Println("Almost the weekend!")
    default:
        fmt.Println("Just another day.")
    }
}
```

Here, the `switch` statement is declaring that we will use the value in the variable `day` to do the switching.
After this, a number of `case` labels define the start of each possible block to run.
The first `case` declares that if the switched value is "Monday", the program should output that it is the start of the workweek.
The second `case` declares that if the switched value is "Friday", the program should then output that it is almost the weekend.
Like an `else` statement, there is a `default` label for `switch` which outputs that it's just another day for all other days that might be switched on.

Only one block from the `switch` will be executed.
The first matching `case` gets priority over all others.

### Switching without an expression

As well as defining a value to switch against, Go allows you to enter a `switch` block without providing a value.
In this instance, each `case` statement will be a condition that must return `true` or `false`.
The first to return `true` gets the priority and its block is run.

```go
func main() {
    num := 15
    switch {
    case num % 2 == 0:
        fmt.Println("Even")
    case num % 2 != 0:
        fmt.Println("Odd")
    }
}
```

Like in one of our earlier examples, the value of `num` is checked to see whether it can be divided by `2` without having any remainder.
When this is `true`, the word "Even" is output to the screen.
When this is `not true` and the `!=` inverts the `false` into a `true`, the word "Odd" is output to the screen.

## Loops

### The `for` loop

The `for` keyword is the only way to create loops in Go.
In its simplest form, you specify some start condition, a check to perform before each loop, and an action to perform immediately after each loop.
This is very similar to a traditional form of loop in something like C, which Go is quite close to.

```go
func main() {
    for i := 1; i <= 5; i++ {
        fmt.Println(i)
    }
}
```

Here, `i` is set to `1` which is checked by the `i <= 5` which is `true` because `1` is less than or equal to `5`.
The loop begins and the value `1` is output to the screen.
After the loop, `i` is incremeneted by `1` up to `2` and the check is performed again.
This continues until the loop where `5` increments to `6` and the check is performed.
`6` is not less than or equal to `5` and the loop no longer triggers.

### Using `for` in place of `while`

Go does not have a `while` loop, but `for` loop syntax can create the equivalent logic.

```go
func main() {
    i := 1
    for i <= 5 {
        fmt.Println(i)
        i++
    }
}
```

This example is identical to the one above, but the logic is spread out more and the only argument to the `for` loop is the conditional check for repeating the loop.

### Using `for` to create an infinite loop

An infinite loop in programming is one that never ends.
It simply doesn't ever fail the conditional check for looping again.
In Go, this is achieved by not even giving a condition to the `for` loop.

```go
func main() {
    for {
        fmt.Println("Running...")
    }
}
```

This program will output the word "Running..." forever.
The only way to stop it will be to interrupt the application that is running.
This is usually done by holding the `Ctrl` key and pressing `C`.

### The `break` control statement

When a loop is executing, you might need to stop it early before it reaches its end condition.
This can be done by simply writing `break` inside the loop.

```go
func main() {
    for i := 1; i <= 10; i++ {
        if i == 5 {
            break
        }
        fmt.Println(i)
    }
}
```

The loop in the example is expecting to carry on until `i` is `11` or more.
But a check inside the loop determines whether the value is `5` on this occassion.
When it is, it breaks out of the loop early, `5` does not get output to the screen, and the rest of the values are never looped over.

### The `continue` control statement

Very much like `break`, but instead of exiting the loop entirely, it only stops the remainder of this instance of the loop from going on.

```go
func main() {
    for i := 1; i <= 5; i++ {
        if i == 3 {
            continue
        }
        fmt.Println(i)
    }
}
```

In the example, the values `1` through `5` are due to be looped over and output to the screen.
However, when `3` comes around, the `continue` control statement means that the loop carries on with `4` and the rest of the the loop for `3` does not occur.
In other words, the output will contain `1`, `2`, `4` and `5` only, while `3` never reached the output statement.

### The `goto` control statement

Generally, `goto` is a code smell and there are better ways to structure your code so that it is not needed.
It can make it hard to debug a problem in the loops and someone reviewing the code quickly gets lost in how the flow works.
However, it does exist, so here's an example of how it works.

```go
func main() {
    i := 1
Loop:
    if i <= 5 {
        fmt.Println(i)
        i++
        goto Loop
    }
}
```

The line containing `Loop:` is a label for the name given; referring to this label means to refer to that point in the code.
The `goto Loop` at the end of the `if` block means that the code execution should jump back to that point in the code.
This is the equivalent of a `for` loop going up to `5` and that would be a much smarter choice here than using `goto`.

One area where `goto` can be useful is when you have nested loops.
This is where you have a `for` loop inside another `for` loop, or maybe even several layers deep.
When you want to break out of all of them, the `break` control statement isn't good enough.
It only breaks out of one layer of loops, which wasn't what you wanted.

Instead, you can have a label after all the loops and use `goto` to jump to it when you would have used `break`.
This is somewhat acceptable, but you should still look for better patterns where you can.

### Nested loops

Nested loops were mentioned above and so here's an example to help understanding them better.

```go
func main() {
    for i := 1; i <= 3; i++ {
        for j := 1; j <= 3; j++ {
            fmt.Printf("(%d, %d) ", i, j)
        }
        fmt.Println()
    }
}
```

In this case, the value of `i` is set to `1` and will be incremented up to and including `3` by the end of the program.
Each time `i` has a new value, a second loop is applied to the value of `j`, starting at `1` and going up to `3`.

After each value of `j`, the output shows the value of `i` and `j` in brackets.
After `j` reaches `4` and its loop completes, a blank line is output before `i` is increased in value.

The output for this program is therefore the following.

```text
(1, 1)
(1, 2)
(1, 3)

(2, 1)
(2, 2)
(2, 3)

(3, 1)
(3, 2)
(3, 3)
```

## Wrapping Up

Today we've taken a look at how conditionals and loops can be performed in Go.
To summarise:

- Use `if-else` for simple decisions and `switch` for multiple cases.
- `for` is the only loop in Go, but it can replace `while` and infinite loops.
- Loop control statements (`break`, `continue`, `goto`) help manage execution flow.
- Nesting loops allows handling complex logic.

If you've enjoyed what you've learned today, perhaps it would be a good opportunity to go back to the previous article about [aggregate data types]({{< ref "2025-03-15-go-aggregate-data-types" >}}) and see if you can use loops to go over the books in the shop, instead of writing separate lines of code to output each one.
