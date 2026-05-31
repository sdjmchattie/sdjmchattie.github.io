# Skill: Write Blog Post

This skill guides the agent through the complete lifecycle of drafting, researching, aligning, formatting, and validating a new blog post for this personal website.

## Phase 1: Date & Path Calculation
1. Recursively scan `content/posts/` to locate the most recent post.
2. Parse its publication date.
3. Schedule the new post's date exactly **7 days (one week) after** the latest post.
4. Calculate the target slug (lowercase, hyphenated) and directory path: `content/posts/YYYY/MM-DD-slug/index.md`.

## Phase 2: Deep Research
1. Perform deep research on the target topic using the available web search tools.
2. Synthesize key concepts and common pitfalls that a developer would encounter.

## Phase 3: Alignment & Grilling
1. Propose the post's structure and outline to the user.
2. Actively suggest using the `/grill-me` slash command or ask targeted, deep questions to clarify:
   - Technical preferences (e.g., specific libraries or tools to showcase).
   - The depth of the code snippets.
3. **DO NOT** generate post content or write code until the user approves the initial plan.

## Phase 4: Image Placeholder & External Prompt
1. Formulate a creative, high-quality image generation prompt for the featured artwork.
2. Specify a 16:10 landscape aspect ratio and a minimum width of 1200 pixels in the prompt so the user can copy and run it externally.
3. Drop a placeholder JPEG file at the correct path: `static/images/posts/YYYY/MM-DD-slug.jpg` so the Hugo build succeeds without breaking reference validations.

## Phase 5: Drafting & Formatting
1. Draft the post following the pronoun and formatting standards:
   - **One sentence per line** in the markdown source.
   - **No collective pronouns** ("we", "let's").
   - **First-person singular** (`I`, `I'll`, `I'm`, `my`) exclusively for personal opinions, recommendations, and introductions.
   - **Second-person** (`you`, `you'll`, `you're`, `you can`) for all tutorial walkthrough steps and demonstrations.
   - Use natural contractions/truncations throughout to keep a conversational voice.
   - Level 2 headings (`##`) in **Title Case**; Level 3 headings (`###`) in **Sentence case**.

## Phase 6: Validation
1. Verify the front matter contains `date`, `title`, `description`, `slug`, `image`, and `tags`.
2. Run `hugo --gc --minify` to confirm the site builds with zero compilation errors.
