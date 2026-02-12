---
date: 2025-12-18
title: "Advent of Code 2025: A Retrospective"
description: |-
  Having completed Advent of Code 2025, let's do a retrospective.
slug: aoc-2025-python-retrospective
image: /images/posts/2025/12-18-aoc-2025-python-retrospective.jpg
tags:
  - Python
  - Advent of Code
  - Puzzles
---

In software engineering, it's typically very good to have a retrospective after a sprint of work.
The goal isn’t just to celebrate successes or catalogue frustrations, but to step back and deliberately reflect: what worked well, what didn’t, and what lessons are worth carrying forward?
Advent of Code makes for a surprisingly good candidate for this kind of reflection — it’s time-boxed, mentally demanding, and full of small design decisions that add up over the 12 days we had this year.
With Advent of Code 2025 now complete, this post is a retrospective on how it went for me.

If you want to follow the whole series, check out the tag page at [Advent of Code]({{< ref "/tags/advent-of-code" >}}), and you can browse the full code for 2025 in [my 2025 solutions repository](https://github.com/sdjmchattie/AdventOfCode2025).

## What Went Well?

I took the time to prepare for Advent of Code this year and so I had a good Python project set up that was ready to write an input parser and a method each for part 1 and part 2.
In past years there have been situations where part 1's implementation accidentally modifies the input and then part 2 is passed the modified input, which causes bugs.
I took care to ensure this wouldn't happen by reloading the input from the file and parsing it again before attempting part 2.

The first few days were a nice warm up and didn't introduce complexity too early on.
They included working out how many rotations were happening on a safe's dial, identifying out-of-date food items from ranges of identifiers and searching for ascending or descending sequences of numbers.
Often part 2 was a simple extension of part 1, allowing it to be solved without re-strategising.
This allowed me to get into the groove and to focus on setting myself up for the following days.

I decided not to compete on time with others because it adds a lot of stress to your December days.
Instead I focussed on making clean solutions that I could write about on my blog and I enjoyed that process.

I really enjoyed the Star Wars references in day 6.

I managed to complete all 12 days and get all the available stars, which was a nice way to end the first 12 days of December.

## What Could Have Gone Better?

If I'm completely honest, I think the story lacked depth this year.
In past years, the story was charming and suited the puzzle topics.
This year, for example, you're in a trash compactor and need to get out, and the way you do it is to … help a creature do its maths homework!?
Certainly not the best narrative we've seen from Advent of Code.

I think the difficulty ramped up way too quickly in the last three days of the puzzles.
Day 10 had me scratching my head over the part 2 which it turns out is only really solvable with linear equations.
There was no way I could sensibly implement a solution for that, and so I turned to Z3 as a library, which is less satisfying than working it out yourself.

Day 11 was very simple in part 1, but the number of routes through the graph were much bigger in part 2 and I wasn't ready for it.
I tried a few approaches, before accepting my fate and checking how others were solving it.
I was on the right tracks, but I didn't have the right amount of memoization.
Once you get the caching right, it's super easy to solve and I should have realised sooner.

Day 12 was a little unsatisfying despite being simple.
It was designed to sound complicated, and it would have been.
But fitting the polyominos together was basically unneeded and you could approximate the solution and still get the right answer.
I wonder if the designer, Eric, had to carefully implement the definitive solution to ensure the inputs had valid answers.

I did spend a lot of time optimising a `Grid` class and creating types for `Point2D` and `Point3D` which could be used with it.
I did this because, in past years, having a competent collection of grid storage and manipulation code meant having a big head start on some of the puzzles.
I did learn some things about generics in modern Python, which made it worthwhile, but I did over-engineer it and then not need it.

## What Would I Change In The Future?

When I was working on the `Grid` class I wish I'd used more composition patterns for storing the data.
The grid class I had made was working very quickly for day 4, then I changed it to handle unbounded grids and day 4's result is slower to calculate.
If I'd implemented an interfaceable storage class that had to be provided to a new grid, it could have used faster grid access when it wasn't unbounded.

I would really like to learn more Go or another up and coming language.
I was thinking about doing that here, but I needed to keep the implementations shorter as it was a very busy month for me in my day job.
If I have more time in future, I may take the leap!

I did try one year in JavaScript but I gave up when it was getting too tricky for my skills.
I've become more familiar with JavaScript over time, so maybe it would be worth having another go.
The main reason I haven't given it another try yet is because JavaScript feels to me like more of a frontend language, and I've found other languages are better suited to data processing.

I did have GitHub Copilot on while I was working on these puzzles.
On the one hand, it's very nice to not have to write so much boilerplate code.
Especially when sometimes you're just writing line after line to change data in a methodical way that you've already defined on the one line you wrote yourself.
But I do wonder if it's cheating a little bit.
I've not made a definitive decision on that.

If I do decide that using AI to help write the code is acceptable (and I do feel it's the only future that's coming for software engineering) then I would probably like to try out some of the other tools that are coming.
For example, OpenAI's Codex tool lets you describe what you need a whole application to do and it will write the code for you.
As I become more senior in my role at work, I realise that I'm more the decision maker while someone else does the code and I just verify it.
Perhaps this is the future we can expect as senior engineers, and Codex fits into that role quite well.

## Wrapping Up

Anyway, this is going to be my last post for 2025.
I hope you all enjoy a nice break as Christmas and the New Year approach!
Many happy returns and I'll continue with my blog in January 2026.
