# Skill: Write Blog Post

This skill guides the agent through the complete lifecycle of drafting, researching, aligning, formatting, and validating a new blog post for this personal website.

## Phase 1: Date & Path Calculation
1. Recursively scan `content/posts/` to locate the most recent post.
2. Parse its publication date.
3. Schedule the new post's date exactly **7 days (one week) after** the latest post.
4. Calculate the target slug (lowercase, hyphenated, no spaces) and directory path: `content/posts/YYYY/MM-DD-slug/index.md`.

## Phase 2: Deep Research
1. Perform deep research on the target topic using the available web search tools.
2. Synthesize key concepts and common pitfalls that a developer would encounter.

## Phase 3: Alignment & Grilling
1. Propose the post's structure and outline to the user.
2. Actively suggest using the `/grill-me` slash command or ask targeted, deep questions to clarify:
   - Technical preferences (e.g., specific libraries or tools to showcase).
   - The depth of the code snippets.
   - Whether the post belongs to a series and requires a dedicated series tag (e.g., `Go Series`).
3. **DO NOT** generate post content or write code until the user approves the initial plan.

## Phase 4: Image Placeholder
1. **DO NOT** attempt to generate a post-specific featured image.
2. Copy the pre-existing repository placeholder image from `static/images/placeholder.png` to the post-specific featured image path: `static/images/posts/YYYY/MM-DD-slug.png`.
3. If inline images are used, save them directly in the post's directory and reference them using relative paths (e.g., `![Alt text](image-name.png)`). Always include descriptive alt text.

## Phase 5: Drafting & Formatting
1. Draft the post strictly following the structure, tone, British English spelling, heading casing, code block, paragraph, and link guidelines in the **Blog Post Writing Guide** section of [AGENTS.md](file:///Users/stuart/Source/personal-website/AGENTS.md).
2. Key procedural requirements during drafting:
   - Begin the body with the `{{< tldr >}}...{{< /tldr >}}` shortcode containing a 1–2 sentence summary and actionable bullet points.
   - Write in **British English** (UK spelling and grammar).
   - Format with **one sentence per line** in the markdown source file.
   - Use **Title Case** for Level 2 headings (`##`) and **Sentence case** for Level 3+ headings (`###`).
   - Place the closing section under an explicit `## Wrapping Up` heading.

## Phase 6: Validation & Proofreading
1. Verify front matter matches the **Front Matter Requirements** in [AGENTS.md](file:///Users/stuart/Source/personal-website/AGENTS.md).
2. Confirm the `{{< tldr >}}` block is present at the start of the body with accurate takeaways.
3. Run through all items in the **Proofreading Checklist** in [AGENTS.md](file:///Users/stuart/Source/personal-website/AGENTS.md).
4. Test locally using `hugo server --renderToMemory` to visually inspect rendering and verify all links resolve.
5. Run `hugo --gc --minify` to confirm the production build completes with zero errors.
