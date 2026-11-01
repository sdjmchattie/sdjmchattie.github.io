---
date: 2026-11-28
title: "Advent of Code 2026: Preparations and the AI Challenge"
description: |-
  December is almost here, kicking off another 12 days of Advent of Code puzzles in Python.
  This year I'm adding a twist: solving each puzzle myself before pitting Gemini Flash 3.8 Medium and Argon 4 Medium against the exact same challenge.
slug: aoc-2026-python-prep
image: /images/posts/2026/11-28-aoc-2026-python-prep.png
tags:
  - Python
  - Advent of Code
  - Puzzles
  - Agentic AI
math: true
---

{{< tldr >}}
This December, I'll be tackling all 12 days of [Advent of Code](https://adventofcode.com/) 2026 in [Python](https://www.python.org/) and publishing daily walkthroughs comparing my own code against AI-generated solutions.
Once the puzzles wrap up mid-month, I'll be taking a winter break from the blog before returning in January 2027.

- **Human vs AI head-to-head:** I'll solve every puzzle solo first, then hand the problem to [Google Gemini](https://deepmind.google/technologies/gemini/) Flash 3.8 Medium (escalating to Argon 4 Medium if Flash fails) to compare algorithmic choices and execution times.
- **Proven Python tooling:** Solutions will live in my [AdventOfCode2026 GitHub repository](https://github.com/sdjmchattie/AdventOfCode2026), powered by [`uv`](https://docs.astral.sh/uv/) and [`ruff`](https://docs.astral.sh/ruff/).
- **Daily December posts:** Expect a post each day covering the puzzle logic, my Python implementation, and how the AI's approach stacks up.
- **Winter break:** After Advent of Code finishes, I'll pause publishing over Christmas and New Year before kicking off my 2027 schedule.
{{< /tldr >}}

December is just days away, which means [Advent of Code](https://adventofcode.com/) is about to return for another twelve days of festive algorithmic puzzles.
Last year I focused purely on execution speed in [Python](https://www.python.org/), documenting my setup in [Advent of Code 2025: Preparations]({{< ref "../2025/11-22-aoc-2025-python-prep" >}}) and publishing daily walkthroughs under the [Advent of Code]({{< ref "/tags/advent-of-code" >}}) tag.
This year I'm returning with Python to tackle all twelve days again, but I'm adding a head-to-head AI comparison to every daily post before taking a winter break until 2027.

## From Retrospective Question to 2026 Experiment

In my [Advent of Code 2025 retrospective]({{< ref "../2025/12-18-aoc-2025-python-retrospective" >}}), I reflected on having [GitHub Copilot](https://github.com/features/copilot) enabled while writing my puzzle solutions.
Having AI autocomplete repetitive boilerplate saved plenty of typing while still leaving the algorithm design to me, and I noticed myself wondering what would happen if I handed the entire puzzle over to an agentic coding tool instead.
As I noted at the end of last year, describing what an application needs to do and verifying the generated code increasingly mirrors how senior engineers work.

For 2026, I'm turning that curiosity into a side-by-side experiment.
I'll still design and write my own solutions first (keeping AI autocomplete on to save writing boilerplate), and once I've solved the day's puzzle, I'll ask an AI model to solve the whole thing independently from scratch.
That way, I still get the full mental workout of working out the algorithms myself, while turning each daily blog post into a practical benchmark of human-designed code versus autonomous AI problem-solving.

## The Human vs AI Format

### The model lineup: Gemini Flash 3.8 and Argon 4

For the AI side of the experiment, I'm using a two-tier escalation strategy rather than jumping straight to the heaviest frontier model on day one.
Every day, the first model in the hot seat will be [Google Gemini](https://deepmind.google/technologies/gemini/) Flash 3.8 Medium.
Lightweight reasoning models have made huge leaps in speed and coding accuracy this year, so I'm keen to see how many Advent of Code puzzles a fast model can clear on its own.

If Gemini Flash 3.8 Medium gets stuck, hallucinates an invalid approach, or fails to produce the right star on either part, I'll step up to Argon 4 Medium.
Testing a fast model first and keeping a heavier model in reserve mirrors how I use AI tools in day-to-day development.
It'll also reveal exactly which puzzle mechanics trip up smaller models as the difficulty ramps up across the twelve days.

### Rules of engagement

To keep the comparison fair and enjoyable, I'm sticking to a strict order of operations each day:

1. Design and code my own Python solution for Part 1 and Part 2 first, using AI autocomplete only to speed up repetitive boilerplate.
2. Record my solution's runtime and commit the working code.
3. Hand the puzzle description and input to Gemini Flash 3.8 Medium (and Argon 4 Medium if needed) to generate a standalone Python solution.
4. Benchmark the AI's code on the same puzzle input and compare the two implementations for that day's blog post.

### What I'll be comparing

Getting the right answer is only half the story in Advent of Code, especially when Part 2 scales the input size up by several orders of magnitude.
As I covered recently in [Understanding Big-O Notation]({{< ref "11-21-understanding-big-o-notation" >}}), an $O(N^2)$ brute-force loop that finishes Part 1 in milliseconds will often grind to a halt on Part 2.
In each daily post, I'll compare my code against the AI's across three main dimensions:

- **Algorithmic approach:** Did the model spot the underlying mathematical shortcut, [graph traversal](https://en.wikipedia.org/wiki/Graph_traversal), or [dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming) state, or did it try to brute-force the problem?
- **Execution speed:** Using Python's [`time.perf_counter`](https://docs.python.org/3/library/time.html#time.perf_counter), how many milliseconds does each solution take to run both parts?
- **Readability and style:** Which solution is cleaner, more Pythonic, and easier to understand when you read it back?

## Tooling and Repository Setup

I'm keeping the streamlined project structure that served me well in [last year's preparations]({{< ref "../2025/11-22-aoc-2025-python-prep" >}}).
All of my code and the AI-generated solutions will be published in my [AdventOfCode2026 GitHub repository](https://github.com/sdjmchattie/AdventOfCode2026) so you can follow along and run the benchmarks yourself.

The project uses [`uv`](https://docs.astral.sh/uv/) for dependency management and script execution, paired with [`ruff`](https://docs.astral.sh/ruff/) to keep formatting consistent.
If you want to learn more about either tool, you can check out my earlier guides on [migrating to uv]({{< ref "../2025/07-19-sudoku-solver-move-to-uv" >}}) and [using Ruff for Python code quality]({{< ref "02-28-ruff-for-python-code-quality" >}}).
Just like last year, the test runner reloads the raw input file between Part 1 and Part 2 so that any in-place list or grid mutations in Part 1 never cause subtle bugs in Part 2.

## Daily Posts and a Winter Break

Ever since creator [Eric Wastl](https://hachyderm.io/@ericwastl) streamlined Advent of Code to twelve days of puzzles in 2025, keeping up with a daily December blog series has become much more manageable.
Starting on 1st December, I'll aim to publish a post each day breaking down the puzzle, walking through my Python solution, and analysing how Gemini Flash 3.8 Medium or Argon 4 Medium tackled the same problem.

Once the Advent of Code series concludes, I'll be taking a break from blogging over the Christmas holidays and New Year.
After a full year of weekly posts and twelve daily puzzle write-ups, I'm looking forward to recharging before kicking off my 2027 articles in January.

## Wrapping Up

I'm really looking forward to kicking off Advent of Code 2026, sharpening my Python skills, and seeing where Gemini Flash 3.8 Medium shines or stumbles when Argon 4 Medium has to step in.
If you're taking part this December, feel free to star or fork my [AdventOfCode2026 repository](https://github.com/sdjmchattie/AdventOfCode2026) and compare your own solutions along the way.

You can catch up on all of my previous puzzle write-ups under the [Advent of Code]({{< ref "/tags/advent-of-code" >}}) tag, or browse my other AI experiments under the [Agentic AI]({{< ref "/tags/agentic-ai" >}}) tag.
Look out for my Day 1 solution and the first human-versus-AI showdown on the 1st of December!
