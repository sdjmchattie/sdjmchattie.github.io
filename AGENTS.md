# Repository Guidelines

## Project Structure & Module Organization

- `content/` houses the Hugo pages and blog posts; year folders (e.g., `content/posts/2026/02-28-.../index.md`) group articles by month and use `kebab-case` slugs.
- `config/` stores environment-specific YAML (`_default/hugo.yaml`, `params.yaml`, `menus.yaml`); edit these files for global theme settings, navigation, and metadata.
- `static/` delivers static assets (images, favicons, JS) that ship verbatim; drop new files under `static/images` or `static/fonts` to keep URLs stable.
- `layouts/`, `themes/`, and `data/` contain presentation overrides, the `hugo-profile` theme, and structured data (menus, snippets); edit here only when you need a layout tweak.
- Generated output lives in `public/` and `resources/`—do not commit these directories unless explicitly requested.
- `.github/workflows/` defines CI: `hugo.yaml` builds and deploys to GitHub Pages, while `merge-prs.yaml` drives scheduled PR merges; treat these workflows as the production gatekeepers for `main`.

## Build, Test, and Development Commands

- `hugo server --renderToMemory` spins up a local server; keep an eye on the command output for warnings and confirm the site renders before pushing.

## Coding Style & Naming Conventions

- Markdown files use YAML front matter with two-space indentation and keys like `title`, `description`, `date`, `tags`, `slug`, and `image`. Keep values concise and wrap multi-line content in `|-` blocks.
- Post directories follow `YYYY/MM-DD-slug` inside `content/posts`; keep slugs lowercase, hyphenated, and free of spaces so Hugo resolves permalinks cleanly.
- Use `static/images/posts/YYYY/MM-DD-slug.jpg` for featured art and reference it via `/images/posts/...` in front matter.
- When targeting layout changes, prefer editing `layouts/partials` or overriding templates in `themes/hugo-profile` rather than forking the whole theme.

## Blog Post Writing Guide

### Front Matter Requirements

Every post must have a complete YAML front matter block:

- `date`: Publication date in `YYYY-MM-DD` format (e.g., `2026-02-28`)
- `title`: Concise, descriptive title. Use Title Case and keep to a reasonable length.
- `description`: A brief 2-3 sentence summary of the post content, wrapped in `|-` for multi-line text. This appears in social shares and search results, so make it compelling and accurate.
- `slug`: URL-friendly identifier matching the directory name (lowercase, hyphens only, no spaces)
- `image`: Featured image path, format: `/images/posts/YYYY/MM-DD-slug.jpg`
- `tags`: Array of relevant tags (e.g., `Python`, `Go`, `Software Architecture`). For series posts, include a dedicated series tag (e.g., `Go Series` or `Sudoku Series`).

### Heading Format & Styling

- **Level 2 headings** (`##`): Use **Title Case** (capitalize major words). Example: `## What is Ruff and Why Should You Use It?`
- **Level 3+ headings** (`###`): Use **Sentence case** (capitalize only the first word and proper nouns). Example: `### Key benefits of ruff`

### Post Structure & Tone

- **Opening hook** (1-3 sentences): Grab reader attention by explaining why the topic matters or what problem it solves.
- **Quick context/intro** (1-2 paragraphs): For series posts, include a cross-link to the series tag (e.g., `{{< ref "/tags/go-series" >}}`).
- **Content sections**: Structure with level 2 headings for major topics and level 3 headings for subtopics. Keep sections focused and logically ordered.
- **Tone**: Conversational yet professional. Explain concepts clearly and assume readers may be new to the topic. Avoid jargon without definition.
- **Closing** (1-2 paragraphs): Summarize key takeaways and optionally suggest related posts via tag links (e.g., `[Python]({{< ref "/tags/python" >}})`). End on an encouraging or forward-looking note (e.g., "Happy coding!").

### Code Examples

- Use triple-backtick fences with language specification (e.g., ` ```python`, ` ```go`, ` ```bash`, ` ```yaml`).
- Keep examples concise and focused on the specific concept being explained.
- Include explanatory text after code blocks to clarify what the code demonstrates.
- For shell commands, prefix with context (e.g., "To check your code for issues:") so readers understand the intent.
- Code should be readable; prefer breaking long lines rather than forcing horizontal scrolling.

### Cross-References & Links

- Link to related posts using `{{< ref "YYYY-MM-DD-slug" >}}` syntax.
- Link to tag pages using `{{< ref "/tags/tag-name" >}}` syntax.
- External links use standard markdown: `[Link Text](https://example.com)`.
- Series posts should reference the series tag to help readers discover other posts in the series.

### Paragraph Style

- Each sentence goes on its own line in the markdown source. This keeps line length manageable and makes diffs easier to read.
- Paragraphs are typically 2-5 sentences; use shorter paragraphs to break up dense information.
- Lead with the main idea, then support with details or examples.
- Use lists (bulleted or numbered) to organize related points, keeping list items concise.

### Images

- Featured images should be relevant, high-quality JPGs saved to `static/images/posts/YYYY/MM-DD-slug.jpg`.
- Inline images (if used) should be saved in the post directory and referenced with relative paths (e.g., `![Alt text](image-name.png)`).
- Always include descriptive alt text for accessibility.

### Proofreading Checklist

- [ ] Date, slug, and directory name match (e.g., `2026-02-28` in both front matter and directory).
- [ ] Featured image exists at the correct path.
- [ ] All cross-references and tag links use correct syntax and resolve properly (test with `hugo server --renderToMemory`).
- [ ] Heading formatting follows conventions (Title Case for ##, Sentence case for ###).
- [ ] Code examples are syntactically correct and relevant.
- [ ] Tone is conversational and accessible to the target audience.
- [ ] No orphaned markdown formatting or typos.
- [ ] First and last sentences are strong and compelling.

## Testing Guidelines

- There is no separate test suite; a successful `hugo --gc --minify` build serves as the acceptance gate. Re-run that command if you touch templates, data files, or site-wide params.
- Visual regression is manual: compare the local `hugo server --renderToMemory` instance to the production preview after building.
- Draft posts live under `drafts/` or are toggled via `draft: true` front matter; `hugo server -D` must be used to view them until they are ready for publishing.

## Commit & Pull Request Guidelines

- Keep commits short and imperative (e.g., `Fix code block copy behavior`). Reference the scope (content, layout, config) when helpful.
- PRs should explain the change, link any related issue, and note whether a force build (`hugo --gc --minify`) was run. Mention if you added/updated assets so reviewers can inspect `static/`.
- Since CI deploys `main` automatically, ensure the PR description highlights any story or layout changes that warrant manual QA and include screenshots for visual edits.
