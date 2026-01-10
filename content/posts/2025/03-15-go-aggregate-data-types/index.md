---
date: 2025-03-15
title: "Go Series: Aggregate Data Types"
description: |-
  In this third post in the Go series, let's take a look at aggregate data types which can be used to create collections of simple data types.
slug: go-series-aggregate-data-types
image: /images/posts/2025/03-15-go-aggregate-data-types.jpg
tags:
  - Go
  - Go Series
  - Learning
---

This is the third post in the Go series.
You can see a list of all of the posts in this series by visiting the [Go Series]({{< ref "/tags/go-series" >}}) tag.
This week we look at aggregate data types which are how you can store lots of related data together, much like how directories work on your computer.

In other languages you may be familiar with arrays and dictionaries or hashes as the primary collection types.
These are similar concepts in Go as well, but they have slightly different names and may not behave the way you're used to.
This is mostly so that Go can run lightning fast.

## Aggregate Data Types

The main aggregate data types in Go are as follows:

- **Arrays** are able to hold a fixed number of items of data which must all be of the same type.
- **Slices** are similar to arrays, but they are dynamically sized, so you can add and remove items from them.
- **Maps** are the name Go gives to dictionaries or hashes.
  They store values of one type, using unique keys of another type.
- **Structs** are able to combine named variables which can be of different types.

Let's look at each type, one-by-one.

### Arrays

Arrays are often dynamically size in other languages, but remember that Go is an iteration on C; and C declares arrays with a size.
This is an efficient way for the language to handle arrays because the memory required to store it is fixed and known in advance.

For these reasons, when declaring an array, its size needs to be declared as well.
This can either be done by giving the size explicitly, or by implicitly defining the size from a list of values:

```go
// Explicit size declaration
weekTemperaturesExplicit := [7]float64{12.5, 8.5, 9.0, 10.5, 11.0, 13.5, 12.0}

// Implicit size declaration
weekTemperaturesImplicit := [...]float64{12.5, 8.5, 9.0, 10.5, 11.0, 13.5, 12.0}
```

There's no standard library package for arrays, but there are packages from third parties to help with managing arrays.
Remember you can find packages for Go on the [Go package directory](https://pkg.go.dev).

Once the array has been declared, you can refer to values in it using indexing.
You can use the indexing to change values to new values, but you cannot add or remove values from the array as that would change its size.

```go
weekTemperatures := [7]float64{12.5, 8.5, 9.0, 10.5, 11.0, 13.5, 12.0}

fmt.Println(weekTemperatures[0])  // Outputs the first temperature, 12.5
weekTemperatures[1] = 9.5  // Updates the second temperature
```

You can also query how many items are in the array at run time using the built-in `len` function.

```go
weekTemperatures := [7]float64{12.5, 8.5, 9.0, 10.5, 11.0, 13.5, 12.0}

fmt.Println(len(weekTemperatures))  // Outputs 7
```

### Slices

Slices are like arrays, but they can change in size after being declared.
If you take a range of values from an array, that range is automatically a slice.

```go
weekTemperatures := [7]float64{12.5, 8.5, 9.0, 10.5, 11.0, 13.5, 12.0}
weekDayTemperatures := weekTemperatures[0:5]  // The first 5 temperatures as a slice
```

In fact, the zero at the start of that range is redundant.
Where a range is selected from an array, leaving a value out means from or up to the end of the array.

```go
weekTemperatures := [7]float64{12.5, 8.5, 9.0, 10.5, 11.0, 13.5, 12.0}
firstTemperatures := weekTemperatures[:5]  // The first 5 temperatures as a slice
lastTemperatures := weekTemperatures[2:]  // The last 5 temperatures as a slice
```

It's important to understand that the slice from an array is not a new object in memory.
If you update values on the slice, you also update those values in the original array.

```go
weekTemperatures := [7]float64{12.5, 8.5, 9.0, 10.5, 11.0, 13.5, 12.0}
firstTemperatures := weekTemperatures[:5]
firstTemperatures[2] = 25.0
fmt.Println(weekTemperatures)  // Outputs [12.5 8.5 25.0 10.5 11.0 13.5 12.0]
```

Slices don't have to be generated from an array.
You can also declare a new slice using syntax that's similar to an array, but without the size mentioned at all.
Or you can create an empty one using the `make` function.

```go
mySlice := []string{"One", "Two", "Three"}

// Make an empty slice of strings with length of 3 and pre-allocated memory for 5 entries
madeSlice := make([]string, 3, 5)
```

You can append new values to the end of a slice with the built-in `append` function.

```go
mySlice := []string{"One", "Two", "Three"}
mySlice = append(mySlice, "Four", "Five")
fmt.Println(mySlice)  // Outputs [One Two Three Four Five]
```

As with arrays, you can use the `len` function to find out the current size of the slice.
Although slices can grow in size as needed, they are actually allocated a fixed amount of memory.
The `cap` function will let you know the current size of the slice in memory.
If you append more values to it than the current capacity, a new memory allocation will be made, although you don't need to worry too much as Go will do this silently for you.

There is a [slices package](https://pkg.go.dev/slices) in the standard library which provides functions for working with slices.
This includes functions for searching the slice for particular values and sorting the values in the slice using a provided function.

### Maps

Maps are what Go uses to refer to dictionaries or hashes, depending on which terminology you're most familiar with.
They are declared with a type for the keys and a type for the values.

```go
numberNames := map[int]string {
  1: "one",
  5: "five",
  9: "nine",
}
```

Note that the final comma is required unlike in some languages.

As you might expect, the values can be both retrieved and overwritten using the keys assigned.
Or you can put new numbers in the map by using keys which haven't been declared yet.

```go
fmt.Println(numberNames[5])  // Outputs five

numberNames[5] = "cinq"
numberNames[20] = "vingt"
fmt.Println(numberNames)  // Outputs map[1:one 5:cinq 9:nine 20:vingt]
```

The order of items in the map are not deterministic, so they could actually be output in a different order from above.

There is a [maps package](https://pkg.go.dev/maps) in the standard library which provides all sorts of functionality for manipulating maps.
For example, you can get an iterable sequence of the keys for the map with the `Keys()` function.
Or you can compare two maps for equality with the `Equal` function.

### Structs

Structs in go are very similar to those you might find in other languages.
In effect, they are a way of keeping related data together.

So if you need to keep records about students in a class and their ages, you might create a struct for that.

```go
type Student struct {
  FirstName string
  LastName  string
  Age       int
}
```

Now you can create instances of students by using curly brace syntax.
The names of the variables are optional when creating an instance, but they do make it clearer to other developers.

```go
students := []Student{
  {FirstName: "Sarah", LastName: "Goodfellow", Age: 17},
  {"Charlie", "Bingham", 18},
}
```

Values stored in a struct are easily retrieved through the use of dot-notation.

```go
student = {"Charlie", "Bingham", 18}

fmt.Println(student.LastName)  // Outputs Bingham
```

There is a [structs package](https://pkg.go.dev/structs) in the standard library, but it isn't nearly as useful as some of the other packages we've discussed.

## Putting them all together

What better way to understand how we might use all these data types than with an example?
This example is a very basic book store with a small number of books.
You can copy this to your own Go environment if you wish and then run it.
You should get the same output as described below.

```go
package main

import "fmt"

// Book struct represents a book in the store.
type Book struct {
  Title  string
  Author string
  ISBN   string
  Price  float64
}

func main() {
  // 1. Array of top-selling books (fixed-size)
  topSelling := [3]string{"978-0134190440", "978-1492077213", "978-1617291784"}

  // 2. Slice of books (dynamic list)
  books := []Book{
    {"The Go Programming Language", "Alan A. A. Donovan", "978-0134190440", 42.99},
    {"Programming in Go", "Mark Summerfield", "978-0321774637", 35.50},
    {"Go in Action", "William Kennedy", "978-1617291784", 39.99},
  }

  // 3. Map to track book stock (ISBN -> Quantity)
  stock := map[string]int{
    "978-0134190440": 5,
    "978-0321774637": 2,
    "978-1617291784": 7,
  }

  // Display inventory
  // Note that this is a very clumsy way to do this, but we haven't gone over loops before now.
  fmt.Println("Bookstore Inventory:")
  fmt.Printf("%s by %s (ISBN: %s) - $%.2f, Stock: %d\n",
    books[0].Title, books[0].Author, books[0].ISBN, books[0].Price, stock[books[0].ISBN])
  fmt.Printf("%s by %s (ISBN: %s) - $%.2f, Stock: %d\n",
    books[1].Title, books[1].Author, books[1].ISBN, books[1].Price, stock[books[1].ISBN])
  fmt.Printf("%s by %s (ISBN: %s) - $%.2f, Stock: %d\n",
    books[2].Title, books[2].Author, books[2].ISBN, books[2].Price, stock[books[2].ISBN])

  // Display top-selling books
  fmt.Println("\nTop Selling Books:")
  fmt.Printf("ISBN: %s\n", topSelling[0])
  fmt.Printf("ISBN: %s\n", topSelling[1])
  fmt.Printf("ISBN: %s\n", topSelling[2])

  // Simulate selling a book
  isbnToSell := "978-0134190440"
  if stock[isbnToSell] > 0 {
    stock[isbnToSell]--
    fmt.Printf("\nSold 1 copy of ISBN %s. Remaining stock: %d\n", isbnToSell, stock[isbnToSell])
  } else {
    fmt.Println("\nOut of stock for", isbnToSell)
  }
}
```

So what's going on here?

Well first we define a struct that we will use to hold on to information about Books in our book store.
This contains four values, three of which are strings, and the last one is a floating-point value.

The `main()` function starts out with a definition of an `array` of top-selling ISBN numbers.
This array cannot change size throughout the rest of the application, but the top-selling list does not change often, so this is fine.

We then define a `slice` of books which we usually have available in stock.
This is a slice, so we could, in theory, add new books to our inventory, or remove books that are no longer going to be stocked.
Each book is a declaration of `Book` struct type we declared earlier.

Lastly, we define a `map` of stock levels for each of our books.
The keys are `string`s containing the ISBN number, while the values are `int`s for the stock level.

We go over some output functionality next, first by displaying the inventory we hold.
This is quite a clumsy way to do this and would not scale to any larger number of books, but we haven't covered loops yet, so we'll stick with this way for now.
Each call to `fmt.Printf` gets a title, and author, an ISBN, a price and the stock level for a book.
These are all concatenated together into output on the screen.

In a similar fashion, we then go over the top-selling books and output each one of those to the screen.

Finally we build a little functionality demonstrating how a book might be sold.
This checks to see whether we have enough stock of the book to make the sale.
If we do, it reduces the stock level by one and prints a message showing the ISBN number of the book sold and the new stock level.
If we do not have stock, a message is shown indicating that there is no more stock.

The output when running this example is as follows.

```text
Bookstore Inventory:
The Go Programming Language by Alan A. A. Donovan (ISBN: 978-0134190440) - $42.99, Stock: 5
Programming in Go by Mark Summerfield (ISBN: 978-0321774637) - $35.50, Stock: 2
Go in Action by William Kennedy (ISBN: 978-1617291784) - $39.99, Stock: 7

Top Selling Books:
ISBN: 978-0134190440
ISBN: 978-1492077213
ISBN: 978-1617291784

Sold 1 copy of ISBN 978-0134190440. Remaining stock: 4
```

## Wrapping Up

As we've seen, aggregate data types are very useful when you're dealing with anything more than small quantities of data.
Most applications you might build will need to store data in aggregate forms.
Even reading in the contents of a text file can produce a slice of lines rather than a single string containing new line characters.

In a future post, we will take a look at how we can use loops to apply functions to each item in an aggregate data type.
