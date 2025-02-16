---
date: 2025-02-22
title: "Go Series: Introduction to Go"
description: |-
  Go was introduced by Google in 2009.
  As programming languages go, it's actually quite an interesting one.
  In this post we take a look at what it can do and why you might want to consider using it for an upcoming project.
slug: go-series-what-is-go-lang
image: /images/posts/2025-02-22-introduction-to-go.jpg
tags:
  - Go
  - Learning
---

This post is the first in a series of posts I will be making about the programming language Go.
I've been meaning to learn a new language for a while and I wanted to share what I'm learning with others.
The posts may not be back to back, but I needed a common thread to write about and I think this one will be interesting.

To set the tone about this series, I do expect you to have some experience with programming and to know your way around the terminal.
It may be hard to follow if either of these isn't true, but have a Go (get it?)!

## What is Go?

Go was introduced by Google in 2009.
It is said to be a new iteration of the C language, while adding modern paradigms.
That's not to say that it follows the history of C++, Java and C# who all develop on the technology of each other.
Instead Go is going back to the roots of C and avoiding forcing the object-oriented programming approach on the developer.

Go removes some of the worst parts of C while retaining much of the speed and efficiency that C can achieve.
For example, garbage collection is automatic in Go and you can choose to use modules, packages and classes.
It compiles native binaries for any system you want to deploy to, and your application is a single binary file; no external libraries needed.
There are no header files either, which are very C-centric.

## How do I get Go installed?

You can either download and install Go from [the website](https://go.dev), or you can use something like [`goenv`](https://github.com/go-nv/goenv) which lets you control which versions of Go you have installed and switch between them seamlessly.
Once it's installed, you should be able to run the command `go version` in a terminal and you'll be shown which version you have installed.

Once you have it installed, assuming you're working in Visual Studio Code, you should also install the [Go language support extension](https://marketplace.visualstudio.com/items?itemName=golang.go) to get code completion functionality and syntax checking.

## Hello World

Let's just straight in and try making the usual program to see if everything is working:

- From a terminal, create an empty directory and change into the directory.

  ```shell
  mkdir hello-world
  cd hello-world
  ```

- Initialise a new module for your application.

  ```shell
  go mod init hello-world
  ```

  This should create a file called `go.mod`.
  Take a look inside if you're interested, but don't fiddle with the contents.

- Create a new file `main.go` and put the Hello World application code inside:

  ```go
  package main

  import "fmt"

  func main() {
    fmt.Println("Hello World!")
  }
  ```

- Try running the application:

  ```shell
  go run .
  ```

If all has gone well, all you'll see it the words "Hello World!" on the command line and then the program exits.
What happened when you executed the last command was that Go built a binary that does this and ran the binary.
The binary is not retained however.
If you run `go build` instead, you will find there's a new binary file `hello-world` that you can execute with `./hello-world` and it will do the same thing as `go run .` did.
You can pass this binary file to any other person, whether they have Go installed or not, and as long as their computer is the same architecture as yours, it will run.

## Documentation

Don't worry, the other articles in this series will explain fundamentals of Go programming, but any developer knows that there are times you need to refer to the documentation.
Go has good documentation for both its built in functionality, and that of packages you can include to achieve specific goals.
There are the [Go docs](https://go.dev/doc/) which go through much of the same things my blog will aim to.
There is also the [package documentation](https://pkg.go.dev) which is useful on a day to day basis.

Try searching for `strings` to see the strings package from the standard library.
Everything marked with the "Standard Library" tag is pre-installed in the Go language.
Clicking into the strings package, you can see all the functions that you can execute on the package to work with strings.
Things like [`ToTitle(s string)`](https://pkg.go.dev/strings#ToTitle) to convert a string into Title Case.
Note that these functions are not called on the string itself like you might expect coming from another language.
In this case, you would use code like `strings.ToTitle("i want a title")` and you'd get "I Want A Title" come back.

## Wrapping Up

Clearly this is a very quick intro to Go, and that is intentional.
There's a lot to discuss and it's best to go through it one by one.
In the next article, we'll talk about simple data types and how you can assign values to variables using those types.
