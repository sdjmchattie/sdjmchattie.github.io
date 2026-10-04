---
date: 2026-09-12
title: "Revisiting Gorillas in Godot 4: Gemini 3.1 Pro Takes the Challenge"
description: |-
  Earlier this year I benchmarked Claude Code and OpenAI's Codex on recreating QBasic Gorillas in Godot 4.
  Now, Google's flagship Gemini 3.1 Pro model takes on the exact same challenge.
slug: revisiting-gorillas-with-gemini-3-1-pro
image: /images/posts/2026/09-12-revisiting-gorillas-with-gemini-3-1-pro.png
tags:
  - Agentic AI
  - Generative AI
  - Developer Tools
---

{{< tldr >}}
Benchmarking Gemini 3.1 Pro against the 1991 [QBasic Gorillas](https://en.wikipedia.org/wiki/Gorillas_(video_game)) challenge yields a bug-free build on the first attempt, but Claude Opus remains the undisputed champion.
Gemini achieves working gameplay only by quietly cutting corners: stripping pixel art, ignoring terrain destruction, and bypassing Godot's visual scene editor with imperative code.

- **Claude Opus remains champion:** Anthropic's model retained the nostalgic soul of Gorillas with authentic pixel art and destructible scenery.
- **Flawless first run:** Gemini executed cleanly with zero crashes, perfect turn alternation, and accurate projectile math out of the box.
- **Silent compromises:** Gemini replaced pixel art with flat coloured boxes and omitted wind and crater destruction without consulting the user.
- **Un-idiomatic Godot architecture:** Building the entire UI imperatively in [GDScript](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_basics.html) rather than using `.tscn` scene files makes the project painful to maintain.
- **The verdict:** Gemini acts as a "corner-cutting pragmatist" that prioritises a functioning build over visual fidelity and collaborative transparency.
{{< /tldr >}}

A few months ago, I ran an experiment asking two leading AI coding tools to recreate the classic 1991 QBasic game [Gorillas](https://en.wikipedia.org/wiki/Gorillas_(video_game)) in [Godot 4](https://godotengine.org/).
In my [previous Gorillas post]({{< ref "03-28-claude-code-vs-codex-gorillas" >}}), I pitted Anthropic's Claude Opus 4.6 against OpenAI's GPT 5.3 Codex.
Both generated playable games from a single prompt, though their architectural philosophies and visual fidelities diverged significantly.

Since that test, Google has released Gemini 3.1 Pro, showcasing substantial leaps in reasoning and agentic programming capabilities.
I wanted to see how Gemini 3.1 Pro handles the exact same brief when held to the same standards.
Does it lean towards the monolithic retro charm of Claude Code or the modular enterprise structure of Codex?

## The Prompt and Setup

To ensure a fair comparison, I gave Gemini 3.1 Pro the identical starting prompt used in the original challenge:

> Do you remember the game for Quick Basic with gorillas hurling bananas across a city scape?
> I want to recreate that in Godot and support dynamic generation of the city skyline.
> However, I'm happy to use a constant cityscape while getting the banana flight and explosion correct if that's easier.
> Ask questions.

Just like the earlier runs, I targeted Godot 4.5.1, this time running Gemini 3.1 Pro at high effort.
I did not provide any extra hints about architecture, physics formulas, or scene layout.

You can inspect the full transcripts, code, and live builds in the [comparison repository on GitHub](https://github.com/sdjmchattie/claude-code-vs-codex).
You can also play each version directly in your browser:

- [Claude Code's Gorillas](https://stuart.mchattie.net/claude-code-vs-codex/claude-code/)
- [Codex's Gorillas](https://stuart.mchattie.net/claude-code-vs-codex/codex/)
- [Gemini's Gorillas](https://stuart.mchattie.net/claude-code-vs-codex/gemini/)

## Clarification and Planning

Before generating any [GDScript](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_basics.html) files, each tool had the chance to ask clarifying questions.
Observing how an agent clarifies scope reveals a lot about its problem-solving style.

In the original benchmark, both Codex and Claude Code output plain text lists of questions and expected me to manually type out answers to everything in freeform text.
Codex split this across three rounds of three questions, while Claude Code dumped all nine questions into a single batch upfront.

### How Gemini structured its inquiry

Gemini 3.1 Pro took a noticeably more polished, interactive approach.
Instead of dumping raw text prompts, it rendered an interactive multiple-choice interface with clear recommended defaults:

1. **Godot Version**: Confirming the engine version (Godot 4.5).
2. **Perspective**: Asking whether to stick to classic 2D or attempt a modern 3D take (recommended: 2D Classic Gorillas style).
3. **Input Method**: How players should input shots (recommended: classic text input for angle and velocity).
4. **Initial Scope**: Whether to start with a constant cityscape first or jump straight into procedural generation (recommended: start with a constant cityscape to focus on physics and explosions).

You could select the recommended option with a single click or type an alternative response if you wanted something custom.
This made alignment significantly faster and felt far more like a modern developer tooling workflow than typing out paragraphs in response to a terminal prompt.

## Architectural Choices

When building a 2D game in Godot, developers face key decisions around node organisation, physics simulation, and rendering pipelines.
Here is how Gemini 3.1 Pro tackled the core mechanics.

### Scene structure and programmatic UI

Codex produced a heavily componentised design across several scenes and resource files, whereas Claude Code created a single 500-line monolithic script.
Gemini 3.1 Pro chose a two-script structure: `main.gd` (around 200 lines) and `banana.gd` (under 40 lines).

One architectural choice I disliked was how Gemini constructed the entire user interface and node tree imperatively in code.
Rather than using Godot's visual editor and scene files (`.tscn`), it instantiates `CanvasLayer`, `LineEdit` inputs, `Button`, and collision nodes dynamically inside `_ready()`.
It even generates the explosion animation by compiling an inline GDScript string at runtime using `GDScript.new()`.

Bypassing Godot's visual scene tools might make code generation easier for an LLM in a single shot, but it works against the grain of the engine.
It makes the UI tedious to maintain, style, and inspect in the editor.
If you want to adjust layout padding, font sizes, or node hierarchies later, you are forced to dig through imperative script logic rather than tweaking properties visually in Godot.

### Visual presentation: purely geometric

This is where Gemini took a distinctly naive approach compared to the other models.
Where Claude Code delivered charming EGA-style pixel art with animated gorillas and detailed skyscraper windows, Gemini represented every element using basic geometric primitives:

- **Skyline**: Flat grey rectangles drawn directly to the canvas (`draw_rect`).
- **Gorillas**: Solid brown 40×40 squares perched on building tops.
- **Banana**: A simple 10×10 yellow square.
- **Background**: A solid dark blue canvas.

It is functional and legible, but visually plain.
If you were hoping for a nostalgic visual hit of the 1991 DOS classic, Gemini's aesthetic feels more like an early prototyping blockout than a finished retro homage.

### Trajectory physics and wind

Getting the banana arc to feel right requires careful handling of gravity.
Codex relied on Godot's built-in `RigidBody2D` physics node, which caused projectiles to rocket across the screen far too quickly.
Claude Code used parametric equations with wind arrows to create a smooth, deliberate arc.

Gemini took a custom kinematic approach in `banana.gd`.
It applies a constant gravity force (`velocity.y += GRAVITY * delta`) and updates position manually each frame.
The flight path feels natural and predictable, although it omitted wind simulation in this initial version to keep the trajectory purely deterministic.

### Collision detection and explosions

In original Gorillas, blasting circular craters out of the skyline is half the fun.
Codex attempted to dynamically recalculate collision polygons on impact, which proved glitchy.
Claude Code manipulated pixel alpha values on a viewport texture.

Gemini handled collision cleanly using standard Godot nodes: `StaticBody2D` for the buildings and `Area2D` for the gorillas and banana.
However, its explosions are purely cosmetic.
When a banana strikes a surface, an orange circle expands for half a second before removing itself, leaving the underlying building geometry completely untouched.

## Bugs and First-Run Experience

A key metric for agentic coding tools is whether the output actually works without manual debugging.
This is where Gemini 3.1 Pro shone.

In the previous benchmark, Codex was unplayable out of the box due to self-hitting projectiles and gorillas spawning off-screen.
Claude Code ran on the first launch, but suffered from a gameplay bug where winning gorillas vanished permanently for subsequent rounds.

Gemini's game ran on the very first attempt with zero bugs:

- The turn alternation between Player 1 and Player 2 worked seamlessly.
- Text inputs grabbed focus properly and fired projectiles accurately based on typed angles and velocities.
- Gorilla hit detection registered immediately, declaring the winner ("Player X Wins!") before cleanly resetting the match after three seconds.
- Out-of-bounds projectiles were caught and cleaned up reliably.

While the graphics are basic, the logic and state management were rock-solid.

## How the Three Models Compare

Testing all three flagship models against the exact same Godot challenge highlights three very distinct agentic personalities:

- **Claude Opus 4.6**: The Creative Craftsman (and clear winner). It delivered an authentic retro experience with pixel art, destructible buildings, and wind mechanics in a single monolithic file, capturing the soul of the original game on the first attempt.
- **GPT 5.3 Codex**: The Enterprise Architect. Focuses on modular design patterns and built-in engine systems, but over-engineers the solution and introduces game-breaking bugs that require iterative manual fixes.
- **Gemini 3.1 Pro**: The Corner-Cutting Pragmatist. Delivers immediate, bug-free execution, but makes unilateral compromises on graphics, terrain destruction, and editor workflows without consulting you.

## Wrapping Up

Even after giving the ecosystem several months to advance, Claude Opus remains the undisputed champion of this challenge.
Anthropic set a remarkably high bar for creative coding tasks, and with Claude Fable now out in the wild, I would expect that lead to be even more pronounced once I get access to test it.

Gemini 3.1 Pro's result ultimately felt underwhelming.
Technically, it delivered a playable game on the first attempt without crashing.
However, it achieved that by quietly stripping out almost everything that makes Gorillas memorable: no pixel art, no wind forces, no terrain destruction, and a programmatic UI that sidesteps Godot's visual scene editor.

Crucially, those compromises were never presented as choices during the questioning phase.
This touches on a long-standing frustration of mine with Gemini: it frequently makes major architectural and gameplay assumptions, then executes them without asking if you agree.
Its interactive multiple-choice prompt had the perfect opportunity to ask about visual fidelity or terrain destruction, but it simply bypassed those features in silence.

If an AI agent is going to cut corners to guarantee a working build, it should be upfront about the trade-offs.

You can inspect the full source code and transcripts for all three models in the [comparison repository on GitHub](https://github.com/sdjmchattie/claude-code-vs-codex).
You can also follow along with future agentic benchmarks under the [Agentic AI]({{< ref "/tags/agentic-ai" >}}) tag.

Happy coding!

