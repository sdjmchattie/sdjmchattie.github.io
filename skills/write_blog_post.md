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
1. Draft the post following the layout, structure, and style guidelines:
   - **Language Style:**
     - Write in **British English** (UK spelling and grammar, e.g., "optimise", "colour", "behaviour", "organisation").
   - **Structure:**
     - **Opening hook:** A strong 1-3 sentence lead grabbing the reader's attention.
     - **Quick context/intro:** 1-2 paragraphs introducing the topic. Include a cross-link to the series tag using `{{< ref "/tags/go-series" >}}` if part of a series.
     - **Content sections:** Organised logically with H2 (`##`) and H3 (`###`) headings. Prefer a flatter hierarchy; Level 4 headings (`####`) are very rarely used and should be avoided in favour of a flatter structure.
     - **Closing:** 1-2 paragraphs summarizing key takeaways, suggesting related tags/posts, and ending on an encouraging note.
   - **Formatting & Style:**
     - **One sentence per line** in the markdown source.
     - Paragraphs should be short (typically 2-5 sentences), leading with the main idea.
     - Use concise bulleted or numbered lists.
     - Avoid emdashes (`—`); use colons, commas, or restructured sentences instead.
   - **Pronouns & Tone:**
     - **No collective pronouns** ("we", "let's").
     - **First-person singular** (`I`, `I'll`, `I'm`, `my`) exclusively for personal opinions, recommendations, and introductions.
     - **Second-person** (`you`, `you'll`, `you're`, `you can`) for all tutorial walkthrough steps and demonstrations.
     - Use natural contractions throughout to keep a conversational yet professional voice.
     - Level 2 headings (`##`) must use **Title Case**; Level 3 and 4 headings (`###` / `####`) must use **Sentence case**.
   - **Code Examples:**
     - Use triple-backtick fences with language specification.
     - Keep examples concise, focused, and followed by explanatory text.
     - Prefix shell commands with context (e.g., "To check your code for issues:").
     - Ensure code wraps/breaks instead of forcing horizontal scrolling.
   - **Links & Cross-References:**
     - Link to related posts using relative path syntax: `{{< ref "MM-DD-slug" >}}` if in the same year, or `{{< ref "../YYYY/MM-DD-slug" >}}` if in a different year.
     - Link to tag pages using `{{< ref "/tags/tag-name" >}}` syntax.
     - External links use standard `[Link Text](https://example.com)`.

## Phase 6: Validation & Proofreading
1. Verify the front matter uses two-space indentation and contains:
   - `date`: `YYYY-MM-DD`
   - `title`: Title Case, concise
   - `description`: 2-3 sentences wrapped in a `|-` block
   - `slug`: matching directory name
   - `image`: `/images/posts/YYYY/MM-DD-slug.png`
   - `tags`: Array of relevant tags (including any series tags)
2. Run through the final proofreading checklist:
   - [ ] Date, slug, and directory name match.
   - [ ] Featured image placeholder exists at `static/images/posts/YYYY/MM-DD-slug.png`.
   - [ ] Cross-references and tag links resolve properly.
   - [ ] Heading cases match standards (Title Case for ##, Sentence case for ###/####) and heading nesting hierarchy is logical.
   - [ ] Pronoun and contraction rules are followed.
   - [ ] Tone is conversational and code examples are syntactically correct.
   - [ ] Spelling is in British English (UK spelling) in both the article text and python code block comments (e.g., "initialise", "modularise", "organise", "behaviour").
   - [ ] Line-break constraints (one sentence per line in the source file) are strictly followed, even inside bulleted lists, numbered lists, or table cells.
   - [ ] No orphaned markdown formatting or typos.
   - [ ] Opening and closing lines are compelling.
3. Test locally using `hugo server --renderToMemory` to visually inspect rendering and verify all links resolve.
4. Run `hugo --gc --minify` to confirm the production build completes with zero errors.
