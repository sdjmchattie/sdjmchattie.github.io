---
date: 2025-03-01
title: "Go Series: Simple Data Types"
description: |-
  For the second post in the Go series, let's take a look at some of the simple data types and how Go handles variable declarations.
slug: go-series-simple-data-types
image: /images/posts/2025-03-01-go-simple-data-types.jpg
tags:
  - Go
  - Go Series
  - Learning
---

This is the second post in the Go series.
You can see a list of all of the posts in this series by visiting the [Go Series]({{< ref "/tags/go-series" >}}) tag.
This week we look at simple data types and how Go handles variable assignments.

Go is a strongly typed language.
What this means is that variables you set have to have a type when declared and they cannot store any other data type later in the program.
For this reason, it's important that we understand the types available and how to use them.
With that in mind, let's take a look at some of the simple types, what they represent and how we can use them when declaring variables.

## Simple Data Types

What are simple data types?
They are the types that hold simple data.
The sort of data you might store in an Excel spreadsheet for example.
Let's look at each type, one-by-one.

### Strings

Like in other languages, strings are really just a complicated name for text.
Strings can be declared directly in your program, or they can come from things like the user typing in responses.
They're very flexible because almost any other type of data can be stored as a string, but it's better to use the correct type to use them in more useful ways.

The Go language has a [`strings` package](https://pkg.go.dev/strings) with useful functions that can be used on string types.
Functions like [`ToUpper()`](https://pkg.go.dev/strings#ToUpper), [`ToTitle()`](https://pkg.go.dev/strings#ToTitle) and [`Contains()`](https://pkg.go.dev/strings#Contains) allow you to work with strings, manipulating the case of their characters, or looking for other strings inside them.

There is also a [`strconv` package](https://pkg.go.dev/strconv) which has functions for things like converting a string to an integer ([Atoi()](https://pkg.go.dev/strconv#Atoi)) or vice versa ([Itoa()](https://pkg.go.dev/strconv#Itoa)).

### Numbers

There are two main types of number in Go; integer and float.
In case you're new to programming, let's see a quick description of each:

- Integers are whole numbers that do not need any decimal places.
  They can be zero, positive or negative.
  Numbers like `-999`, `0`, `42` or `2025` are all integers.
- Floats are numbers that are represented including decimal places.
  That's not to say a float cannot be used to store an integer, but if it is used this way, the integer is still considered a float value.
  Numbers like `-2.5`, `0.0`, `3.141592` or `365.25` are all floats.

Within each number type above, there are various choices of type you can use in Go, depending on the size of the numbers you will store in a variable.

#### Integers

- `int8` for 8-bit integers ranging -128 to 127
- `int16` for 16-bit integers ranging -32768 to 32767
- `int32` for 32-bit integers ranging -2147483648 to 2147483647
- `int64` for 64-bit integers ranging -9223372036854775808 to 9223372036854775807

Although these sub-types are available, you're likely to only use `int` without a number after it.
This type automatically uses the largest integer type your system can support, `int32` on a 32-bit system and `int64` on a 64-bit system.
The other types are only really useful if you need to save memory and know the numbers being stored are constrained to the range shown.

Each of the integer types above can also be turned into `uint8`, `uint16`, `uint32` and `uint64` which are unsigned versions.
Unsigned means that they cannot store negative numbers, which also doubles the range of positive numbers they can store.
Like with the types above, `uint` without a number after it, uses the largest unsigned integer type the system can support.

#### Floats

- `float32` for 32-bit floats ranging -3.4e+38 to 3.4e+38
- `float64` for 64-bit floats ranging -1.7e+308 to +1.7e+308

Unlike integers, you cannot just use `float`.
You must specify which type you want to use.

### Booleans

Thankfully, booleans are much less complicated.
They simply store either the value `true` or the value `false`.
Their main purpose is to control the flow of the program.
Do one thing if a condition is `true`, or do something else if that condition was `false`.
Control of flow will come up in a future post.

### Errors

Unlike a lot of languages, Go uses a specific type for errors.
It's mostly a wrapper around a string, but it allows it to be distinguished from normal strings.
Where a function might not be able to complete due to an error condition, it will return a value and an error.
Only where the error is `nil` can the value be used.
One example of this is the [`ReadAll()` function from the `io` package](https://pkg.go.dev/io#ReadAll) where the file may not be available, for example.

## Variable Assignment

Variables can be declared and assigned to later, or they can be declared and assigned at the same time.
If they are declared first, it's compulsory to specify the type.
For example:

```go
var message string
message = "Hello, World!"
```

This can be all on one line when you are declaring and assigning the value at the same time:

```go
var message string = "Hello, World!"
```

Go is smart enough to know that `"Hello, World!"` represents a string, so you can skip the type:

```go
var message = "Hello, World!"
```

Or alternatively, use the shorthand version where you don't even use the `var` keyword:

```go
message := "Hello, World!"
```

Hopefully you've been trying out some of these examples, but you'll find they won't compile.
The reason for this is that Go doesn't allow you to define a variable that isn't used.
The simple solution is to use the [`fmt`](https://pkg.go.dev/fmt) package to print the string to the screen:

```go
package main

import "fmt"

func main() {
  message := "Hello, World!"
  fmt.Println(message)
}
```

Let's look at an example of declaring, assigning and outputting each data type:

```go
package main

import (
  "errors"
  "fmt"
)

func main() {
  stringVar := "Hello, World!"
  fmt.Println(stringVar)

  intVar := 42
  fmt.Println(intVar)

  floatVar := 3.141592
  fmt.Println(floatVar)

  boolVar := true
  fmt.Println(boolVar)

  errorVar := errors.New("This is an error")
  fmt.Println(errorVar)
}
```

### Constants

The variables we've looked at so far have all been mutable.
What this means is that you can assign a value to them over and over again.
For example:

```go
package main

import "fmt"

func main() {
  stringVar := "Hello, World!"
  fmt.Println(stringVar)

  stringVar = "Hello, Go!"
  fmt.Println(stringVar)
}
```

Note how the second time we assign a value, we don't use the `:=`, instead using `=`.
This is because `:=` can only be used where there are new variables on the left that need to be created in memory.

However, there are times where you don't want a variable to be able to be reassigned.
This might be because you need to refer to a specific key or phrase in your program, and you don't want it to be possible that the phrase might change after the program has started.
In this case, you want to use the `const` keyword instead of `var`.

```go
package main

import "fmt"

func main() {
  const stringVar = "Hello, World!"
  fmt.Println(stringVar)

  stringVar = "Hello, Go!"
  fmt.Println(stringVar)
}
```

This will not compile and Go will tell you that `stringVar` is `neither addressable nor a map index expression`.
Constants are handled a bit differently than variables.
Instead of providing memory space for a variable, the compiler literally takes the value you assigned to the constant and injects it everywhere you used it in your code.
So you can see why the line that says `stringVar = "Hello, Go!"` cannot work, because the compiler tries to turn it into `"Hello, World!" = "Hello, Go!"` which makes no sense at all.

### Pointers

If you've come from a language like C or C++, you'll probably be familiar with pointers.
Every language uses them, but they can seem a bit daunting and lots of languages hide them from you.

Variables seem like a magic box you can put values into, but in reality they are all pointers.
When you declare a new variable, a space in memory is allocated and the address of that space is what the variable stores.
If you assign a new value to the variable, the language writes it to the memory space at the address.
When you read the variable, the language goes to the memory space at the address to get the value.

So what has this got to do with writing code in Go?
Let's say you wanted to copy a value from one variable to another.
You could write that code like this:

```go
package main

import "fmt"

func main() {
  a := 10
  b := a
  fmt.Println(a, b)

  b = 20
  fmt.Println(a, b)
}
```

This sets `a` to `10`, copies the value to `b`, outputs both, then changes `b` to `20` before outputting them again.
The output from this code is as follows, and hopefully won't be overly surprising:

```text
10 10
10 20
```

However, you can access the pointer for `a` by referring to it as `&a`.
If you assign `b` using that syntax, you would have `b := &a`.
The type of `b` is no longer an integer, but instead an address.
If you want to get the value at the address, you need to use the syntax `*b`.
And, more importantly, if you change the value of `*b` you're actually changing the value at `a` as well.
For an example, take a look at this code:

```go
package main

import "fmt"

func main() {
  a := 10
  b := &a
  fmt.Println(a, *b)

  *b = 20
  fmt.Println(a, *b)
}
```

The result from this being run is now as below where we can see the value of `a` changes between the first and the second print statements.

```text
10 10
20 20
```

But why would you want to do this?
It's a good question as it seems to add a lot of complexity.
However it also provides a lot of power.

When you call a function, usually that function can return values, but it can't do anything to change the values you passed into it.
However, if you pass a value in using a pointer address, the function can use the same tricks we've just seen to modify the value.

One example of this is the [Scanln() function](https://pkg.go.dev/fmt#Scanln) in the `fmt` package.
It accepts the pointer address to a `string` variable as an argument and puts the contents of what the user typed into the variable for you.
It also returns the number of characters that were scanned in and an error if one occurred.

If this has been a bit confusing, don't worry too much.
It's not that often that you need to use pointer addresses, and when you do, you mostly just need to know to put `&` in front of your variable name when passing it to a function.

## Wrapping Up

Hopefully this quick review of simple data types in Go has been helpful to you.
In the next post we'll be looking at aggregate data types like arrays, slices maps and structs.
