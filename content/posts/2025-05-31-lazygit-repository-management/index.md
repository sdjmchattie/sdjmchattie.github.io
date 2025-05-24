---
date: 2025-05-31
title: "Managing Git Repositories with Lazygit: The Terminal UI Powerhouse"
description: |-
  Git is hard, but LazyGit makes it easy.
  It is freely available and provides a user interface in the terminal that behaves like a full GUI.
sslug: managing-git-repositories-with-lazygit
image: /images/posts/2025-05-31-lazygit-repository-management.jpg
tags:
  - Git
  - Developer Tools
---

Let’s face it: managing Git repositories via command-line commands can sometimes feel cumbersome and repetitive.
You might be familiar with the basic commands, but as your projects grow, so do your Git management tasks — staging, branching, rebasing, merging, resolving conflicts, and more.

Imagine a tool that brings a visual, interactive interface right into your terminal, making Git operations faster, clearer, and more intuitive — all without leaving your command line environment.

Enter **Lazygit**, a terminal-based Git UI that simplifies and streamlines Git management, transforming your workflow into a more relaxed and efficient experience.

In this guide, we'll explore what Lazygit is, how to install it, and how to leverage its features to supercharge your Git process — whether you're a beginner or a seasoned developer.

---

## What is Lazygit?

Lazygit is a lightweight, open-source terminal UI for Git.
It provides a visual, easy-to-understand interface that allows you to perform common Git operations — like staging files, creating branches, rebasing, and pushing — with simple keystrokes.

Think of Lazygit as your Git dashboard right inside your terminal.
It displays commit history, branch trees, status updates, and diffs visually, so you understand your repository’s state at a glance.

One of its standout features is that it lets you see your commands executing in real-time, helping you learn Git commands as you use the tool.
This makes Lazygit an excellent choice for developers looking to deepen their understanding of Git workflows while keeping things straightforward.

---

## Why Use Lazygit?

Traditional Git commands are powerful but can be intimidating, especially when managing complex repositories.
Lazygit offers several benefits:

- **Visual interface:** Clear panels for files, branches, commits, and stashes.
- **Keyboard-driven:** Perform actions rapidly without typing long commands.
- **Context-aware:** See unstaged and staged changes, diffs, and logs instantly.
- **Conflict resolution:** Guides users through resolving conflicts step-by-step.
- **Learn with convenience:** Commands are displayed and executed visually, easing learning curve.
- **Customization:** Supports setting shortcuts and creating custom commands.

Many developers find that Lazygit reduces mistakes, speeds up workflow, and minimises frustration with Git’s CLI syntax.

---

## How to Install Lazygit

Installing Lazygit varies slightly depending on your operating system. Here are the most common methods:

### macOS

```bash
brew install lazygit
```

### Ubuntu / Debian

```bash
sudo apt install lazygit
```

### Windows

Using [winget](https://github.com/microsoft/winget-cli):

```bash
winget install --id=JesseDuffield.lazygit
```

### Pre-built Binaries

Alternatively, download prebuilt binaries from the [Releases page](https://github.com/jesseduffield/lazygit/releases).

---

## Using Lazygit: An Overview of Key Panels

Once installed, navigate to your repository folder and run:

```bash
lazygit
```

This opens the interactive terminal UI, divided into several key panels:

1. **Status Panel** — Displays your current branch, staged, unstaged, and untracked files. Press `1` to toggle.
1. **Files Panel** — Shows all modified files with options to stage/unstage individual lines or entire files. Press `2` to toggle.
1. **Branches Panel** — Lists local and remote branches with options to create, switch, delete, or rebase branches. Press `3` to toggle.
1. **Commits Panel** — Shows recent commit history. Press `4` to toggle.
1. **Stash Panel** — Manage your stash: save changes or apply stashed content. Press `5` to toggle.
1. **Preview / Diff Panel** — Allows you to preview changes, diffs, or logs, helping you understand exactly what’s being committed or changed.

---

## Core Operations Made Easy

### Staging and Unstaging Files

Highlight files in the Files panel.
Press `Space` to toggle staging.
You can also select specific hunks or lines with `V` and stage individually — perfect for precise commits.

### Committing Changes

In the commits panel, select the current branch, then press `c` to open the commit message editor.
Confirm with Enter, and your commit is recorded.

### Branching and Merging

Navigate to the Branches panel (`3`).
Use shortcuts to create (`a`), delete (`d`), or switch branches (`Enter`).
To rebase onto another branch, select your branch, press `r`, and choose the upstream branch.

### Rebasing and Amends

Press `Shift+A` on a commit to amend it with staged changes.
Rebase interactively with `r`, selecting commits to reapply as needed.

### Pushing and Pulling

Push your current branch: press `P`.
Pull latest changes: press `f` to fetch, then `r` to rebase.

### Conflict Resolution

Lazygit detects conflicts during merges.
It guides you through resolving conflicts by showing markers and offering commands — all within the UI.

---

## Customizing Lazygit

Lazygit can be tailored to your workflow:

- **Bindings:** Change key shortcuts in `.config/lazygit/config.toml`.
- **Commands & Aliases:** Automate recurring tasks.
- **Theme & layout:** Adjust colours and layout for personal comfort.

Check the [Official Documentation](https://github.com/jesseduffield/lazygit/wiki) for comprehensive customization.

---

## Practical Tips for Maximising Lazygit Efficiency

- **Use the search feature (`/`)** to filter commits, branches, or files.
- **Preview diffs before acting** to avoid mistakes.
- **Stage individual lines or hunks** for clean commits.
- **Integrate with editors:** Use plugins like [neovim's lazygit.nvim](https://github.com/kdheepak/lazygit.nvim) for seamless workflows.

---

## Wrapping Up

Lazygit elevates Git from a command-line chore into a visual, manageable process right inside your terminal.
Its intuitive interface, combined with powerful features like staging, rebasing, conflict resolution, and branch management, makes Git workflows faster and less error-prone.

If you spend significant time working with Git, give Lazygit a try — you might wonder how you ever managed without it.

Explore its capabilities, customize to your needs, and see how your Git productivity skyrockets.

For further learning, visit the [Lazygit GitHub repository](https://github.com/jesseduffield/lazygit) and the community wiki.
If you want to share your experiences or ask questions, feel free to reach out on your preferred developer community or connect with me.

Happy Git managing!
