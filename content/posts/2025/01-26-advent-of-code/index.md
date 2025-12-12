---
aliases:
  - /posts/practice-and-learn-programming-with-advent-of-code
date: 2025-01-26
title: I play Advent of Code, and you should too!
description: |-
  For the past 5 years, I've been playing Advent of Code.
  Every year Eric Wastl creates 25 puzzles with an associated story about Santa.
  Each puzzle has two parts and can be solved in any programming language you prefer.
  If you get all the answers right, collecting all 50 stars, you can consider yourself one of a very select group of people!
slug: practice-programming-with-advent-of-code
image: /images/posts/2025/01-26-advent-of-code.jpg
tags:
  - Advent of Code
  - Puzzles
  - Python
  - C#
  - Ruby
  - JavaScript
  - Rust
  - Go
---

One of the hardest parts of learning a language's fundamentals is having enough meaningful problems to solve.
"Hello World!" is all well and good, but when do you ever have to use that code in an application you're building?
That's where Advent of Code comes in for me.
Here I'm going to discuss what Advent of Code is, how to get started on Advent of Code, a brief look at some of my favourite puzzle types on there, and which languages I've attempted to use each year.

## What is Advent of Code?

[Advent of Code](https://adventofcode.com) is a website and annual event created and maintained by [Eric Wastl](https://hachyderm.io/@ericwastl).
Like it sounds, it runs throughout December, up to and including Christmas Day on the 25th.
Absolutely anyone can take part.
Each day, a new puzzle is made available at exactly 05:00 UTC (midnight on the US East coast).

In each puzzle, there is a part 1 and a part 2.
Usually both parts have the same input, but part 2 is a development on part 1 that makes it a lot harder to solve with a naive solution.
Often part 1 tempts you to apply a simple solution, and you probably should!
However, part 2 will need you to find efficiencies and short cuts to your approach.
Trimming down the problem space becomes essential.

The puzzles generally increase in complexity over the event, but complexity is very much linked to your skill set.
There is a global leaderboard for the fastest solvers, but it is really very competitive and not worth worrying about while you're trying to learn new things.
Instead, focus on the Stats page which shows you how many people got the first and second star each day.
The people who get all 50 stars in a year matches those who got the second star on day 25, so, if you can complete them all, you will find you're in the top ~5% of players worldwide who tried Advent of Code that year.

## How to get started

This is the easy bit!
Visiting the site, you'll see there is a simple design and a menu at the top.
If you choose to Log In, you'll have several options for how to identify yourself, but I choose to use my GitHub account as I feel it ties my identity to the place where I store my solutions.
Once you're logged in, you can choose the Events menu and select which year you want to solve puzzles from.
It doesn't really matter which year you choose unless you're wanting to solve puzzles in December, of course!

Once you've selected a year, you'll face a list of numbered puzzles.
It's probably best to solve them in day order since, in some years, solutions from one day are relevant to those in later days.
Plus, of course, earlier days are easier to solve which is a good way to escalate your understanding of the language you're working in.

Take some time to read the puzzle introduction story.
They are very well written and often contain a lot of humour you might enjoy.
The text will explain the problem and give an example of how you would solve a simple input.
The real input is then accessible via a link at the bottom of the text.
You should take this and start writing some code to apply your solution to it.

Once you think you have the correct answer, paste it into the website and check if it's correct.
One of a few things will happen here:

- You've got the right answer.
  Well done!
  Now check out part 2 and try to solve that as well.
- You got the wrong answer.
  - If this is your first attempt, or one of the first 5 or so attempts, you'll be told if your answer is too low or too high.
    You'll also be blocked from trying another answer for a minute or two, to stop people spam guessing.
  - If you've had quite a few attempts at this point, you'll not be given any more clues about whether you need to go higher or lower and the wait time to try another answer could be quite a few minutes between attempts.

If you find yourself struggling, be sure to check out the [hints and tips](#hints-and-tips) on this post.

## Some of my favourite types of puzzles

The puzzles in Advent of Code can be quite varied, but there are certain puzzles that I particularly enjoy.
Here are three examples along with approaches I tend to use.

### Build a computer using code

This has been a theme in some years, and in others it appears as a single puzzle.
2019, for example, got you building a computer processor over the course of the event.
Many people did not like this format but I really enjoy them!

Most of the time, using object-oriented programming isn't necessary to solve Advent of Code puzzles, but this, I feel, is the exception.
You really do benefit from breaking up the complexity of your solution by having a class representing the computer and separate classes that extend a base operation class.
As the complexity of `if`s and `case`es build up, you can capture that in a single class, or you can use [composition](https://en.wikipedia.org/wiki/Function_composition_(computer_science)) to apply the new complexity progressively.

The satisfaction of processing input through such a complex but explainable system is highly satisfying.
The drawback in 2019 is that if you didn't manage a previous day, it can be a blocker to future days.

### Find the shortest path

These are often grid-based puzzles and they ask you to find a way to reach some goal position on the map.
My go to for these is the [Djikstra algorithm](https://en.wikipedia.org/wiki/Dijkstra's_algorithm) which provides the shortest path between two points on a map with penalty scores per movement.
If your grid is basic and you can freely move in any direction, your penalties should be 1 per move you make.
If you can more easily move downwards than you can upwards, for example, then you should vary the penalty for moving by the direction you are moving in.

It's worth double-checking the puzzle text before going for this algorithm though as there are often faster and simpler algorithms you can apply.
For example, if the path has only one known solution, like a labyrinth without loops, there's no point in following Djikstra and, instead, you should use a [depth-first-search](https://en.wikipedia.org/wiki/Depth-first_search) approach, stopping when you find the goal.

### Parsing text input for patterns

OK, so I have a confession to make.
I really love [regular expressions](https://en.wikipedia.org/wiki/Regular_expression)!
When I see a problem in Advent of Code that requires finding text of a particular form, whether that be 5 digits followed by 2 to 4 alphabetic characters, or even something more complicated, my head goes straight to regular expressions.
This is not usually the fastest way to find these patterns, but the extra running time is more than made up for by the shorter development time.

This does involve you needing to get familiar with regular expression syntax however, and the language you use should have good regular expression support (Hi there [Ruby](#ruby)!).
Keep an eye out for a blog post from me about regular expressions and how I use them.

## Choice of language

Below is a list of the languages I've used in past years and what I thought of them for this sort of challenge.
It's worth noting that I have a tendency to go for scripting languages over more formally compiled languages as I find them to be more dynamic when working with the sorts of puzzles you typically get from Advent of Code.

| Year | Stars | Languages |
| ---- | ----: | --------- |
| 2019 |    27 | [Python](https://github.com/sdjmchattie/AdventOfCode2019) |
| 2020 |    48 | [Ruby](https://github.com/sdjmchattie/AdventOfCode2020) |
| 2021 |    38 | [JavaScript](https://github.com/sdjmchattie/AdventOfCode2021) |
| 2022 |    50 | [Python](https://github.com/sdjmchattie/AdventOfCode2022) |
| 2023 |    50 | [C#](https://github.com/sdjmchattie/AdventOfCode2023) and [Rust](https://github.com/sdjmchattie/AdventOfCode2023Rust) |
| 2024 |    50 | [Ruby](https://github.com/sdjmchattie/AdventOfCode2024) |

In 2020, there was just one puzzle that got the better of me.
Because the second star on day 25 expects you to have all 49 other stars, it leaves me two stars short of completion!
I should go back to the unsolved puzzle and see if I can do it with my new skills.

In 2023 I attempted the puzzles twice but my initial attempt was in C#.
I decided if I wanted to try some Rust, I should apply it to a year I'd already solved as I knew Rust was going to challenge me!

### Python

Python is a go to and a really good one to use if you've not yet experienced it.
It's very user friendly and rather readable most of the time, even if you don't already know the language.
It also lends itself really well to Advent of Code, which is why you'll find almost all the fastest solvers each year are using it.
As it's so widely used for Advent of Code, you'll also find getting help for it really simple.

### C Sharp (C#)

This was an odd choice for me to make for this as C# isn't typically known for being fast to iterate with and it has a rather verbose syntax for data management called [LINQ](https://learn.microsoft.com/en-us/dotnet/csharp/linq/).
I mostly chose to use this in 2023 because I wanted to re-kindle my knowledge of the language.
I'm not sure I'd pick it again in future.
I obviously did alright with it since I've got all 50 stars that year, but one of the puzzles really benefited from having a good library available for finding loosly coupled areas of a larger network and I had to use Python for that one day.

### Ruby

Ruby's a bit old now and mostly unused by anyone starting a new project these days.
Finding developers who can work on it is challenging in 2025, most people preferring [Python](#python).
These downsides are a shame because it's a really powerful language in my experience.
Sure, it doesn't have as many libraries as Python and it has some odd naming choices and patterns like implicit returning values from functions.
But it is ridiculously dynamic and works so well with the sorts of problems you see in Advent of Code.

This is why I've solved more days with this language than any other.
It is able to manipulate data in memory like a dream and offers really powerful functions that allow you to map things back and forth between data types with ease.
I love Ruby ... but I also recognise that I should keep my feelers on the pulse of more mainstream languages.

### JavaScript

JavaScript has always felt to me like the language that should have stuck with existing in a browser.
It doesn't really lend itself well to Advent of Code, even though it is capable.
The core language feels like it does so little when it comes to data handling, requiring a library every time you want to do something other languages just do without help.
Finding the right library is then a challenge in itself, with so many all doing the same thing and no obvious winners unless you're familiar with the landscape.

But, all that aside, JavaScript is an incredibly important language these days.
It is probably the most used language for web applications where it excels at managing the DOM and making websites feel fluid and dynamic.
Without JavaScript, we wouldn't have AJAX, which, if you're unaware, is what allows things like Gmail to update the emails in your Inbox without refreshing the whole page.
Not just a client side language these days, it doubles up as the server side language as well, reducing the overhead for a team working with it.

As you can see, I used JavaScript on the 2019 puzzles and I eventually stopped with them because I was finding it tedious due to the nature of the puzzles and my relative inexperience with JavaScript at the time.
I would like to go back and see how I get on with JavaScript again now that it's been a number of years and I've used it in professional project more often!

### Rust

Rust, I'm told, is a revolution in programming languages.
It's ridiculously fast!
It is memory-safe, refusing to compile if something you're doing in the code runs any risk of leaking memory.
It is type-safe, stopping you from compiling if the types don't match.
It is mutability-safe, stopping you from compiling if you try to change a value that's not been declared as mutable.

It's too safe for me with my current skills, unfortunately.
I find it very hard to write code in Rust that will execute without refusing to compile.
It's not because I don't understand the things they've built a safety net for, but because I find the syntax highly difficult to follow.
In most languages, for example, sub-strings of strings are just other strings.
But in Rust, there are various types that all contain a string in one form or another and I cannot seem to get my head around when each one is being used or how to use the right one in my variable declarations.

I did at least complete a couple of days in Rust for the 2023 puzzles, but I wasn't enjoying how long it took me to get right.
I think I could benefit loads by working with someone who already uses Rust, but that opportunity hasn't presented itself yet.

### Go

OK, so I haven't used Go for Advent of Code and I really think I should!
I hear it's also incredibly fast and, having recently created this website using a framework based on Go, I feel like the syntax is accessible.
I have no idea how good it is at processing the sort of data you encounter in Advent of Code, but I do know of colleagues who used it in 2024, so I guess it's a reasonable choice.

I will write blog posts about Go as and when I learn it!

## Hints and tips

Ideally, you get to solve all the puzzles using your own knowledge.
But that's not usually how learning works!
My advice is to have a go yourself, but don't do so until you're bored of trying or completely lost.

There are a great number of people who post their solutions on [GitHub](https://github.com) and a few also post a stream of them solving the puzzles on [YouTube](https://youtube.com).
There is also a [community of people on Reddit](https://www.reddit.com/r/adventofcode/) who are very keen to show their solutions and try to help others, so try posting on there.
Just bear in mind that every puzzle has a wide number of inputs that get assigned to players, so the person you're talking to probably has a different solution than you.

If you find yourself failing to get the right answer after a couple of attempts it's usually a good idea to quickly switch to the example in the story.
This usually lets you iterate quickly on a solution and you know if you have the right answer because it's shown in the story text (usually, but not always).
Just remember to switch to the real input before making a new attempt!

Finally, if you just want to get the star today, perhaps try a language you're more experienced in this one time.
There are days that have languages better suited to them than others.
The site doesn't specify which language you should use because you can use anything you prefer.
