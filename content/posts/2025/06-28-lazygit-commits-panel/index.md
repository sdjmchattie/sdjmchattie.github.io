---
date: 2025-06-28
title: "Lazygit Series: The Commits Panel"
description: |-
  The fifth post in this Lazygit series takes a look at the fourth panel in the application.
  The commits panel is where you track your commits across all branches and take action on individual commits in your history.
slug: lazygit-commits-panel
image: /images/posts/2025/06-28-lazygit-commits-panel.jpg
tags:
  - Git
  - Lazygit Series
  - Developer Tools
---

This is the fifth post in the Lazygit series.
You can see a list of all of the posts in this series by visiting the [Lazygit Series]({{< ref "/tags/lazygit-series" >}}) tag.
This week, we'll look at how to best use the commits panel.

Lazygit's commits panel allows you to track the hierarchy of commits in your repository's history.
You can see all commits across all branches and how they relate to each other.
You can inspect the code that was included as part of a commit, as well switch to the state of the code at a commit.
You can also rewrite history with actions like rewording, dropping and amending specific commits.

The other tab on the commits panel allows you to review the reflog, which is a git term for a log of all the actions that have taken place on the repository.
This can be useful if you have made unintended changes to your repository and you need to get back to the state of the repository at some time in the recent past.

---

## Navigating the Commits Panel

The commits panel is accessed by pressing `4` in Lazygit.
It displays the commit history for the currently checked-out branch by default, but you can also view all commits across branches.
To see more information and search through commits, you can expand the commits panel to half-screen or full-screen with the `+` key.
Maybe surprisingly, the `_` key, rather than the `-` key, reduces the size of the panel again.
You can search for commits using `/` and cycle through results with `n` (next) and `N` (previous).
Press `esc` to leave search mode.

Pressing `enter` on a commit shows all the files that were modified by that commit.
Simultaneously, the details panel, currently labelled "Patch", shows the lines within the selected file that were changed using standard git diff syntax.

---

## Actions You Can Take on Commits

Lazygit lets you perform a range of actions on commits, from inspecting them to rewriting your commit history.
Here are some of the key actions you can take on commits:

- **Checkout a Commit**
  Pressing `space` on a selected commit lets you check out that commit via a dialog with selectable actions to take.
  This updates your working directory to the state of the repository at that commit.

- **Revert a Commit**
  By pressing `t`, you activate the revert action.
  This creates a new commit that un-does the changes introduced by the selected commit.
  This is useful for undoing changes while preserving the history of that action for others to refer to in future.

- **Amend a Commit**
  With staged changes in your files panel, navigate to a commit and press `Shift + A` to amend that commit with your staged changes.
  If amending an older commit, Lazygit performs an interactive rebase to rewrite history accordingly.

- **Reword Commit Message**
  Press `r` on a commit to change its commit message directly in Lazygit.
  Alternatively, press `R` to open your external editor for editing the commit message.

- **Delete a Commit**
  Pressing `d` deletes the selected commit.
  Lazygit will guide you through the necessary steps, often involving an interactive rebase.

- **Reset to a Commit**
  Select a commit and press `g` to open the reset options.
  Reset is a bit like checking out, but instead of moving away from the branch you were on, you move the branch to the selected commit.
  You can choose between mixed, hard, or soft reset depending on how you want to adjust your working directory and index.

- **Create Tags**
  Press `T` to create a tag at the selected commit.
  This can be useful for marking a commit as the release point for a version of your software.
  Be aware that tags are intended to be permanent, so once you've pushed it, you should never change that tag again.
  This is why, when picking tag names, extra care should be taken.

These actions make it easy to manage your commit history without leaving the terminal.

---

## Using the Reflog Tab

The commits panel has a second tab dedicated to the Git reflog.
This shows a log of all recent actions in the repository, including branch switches and resets.
It’s invaluable when you need to recover from unintended changes, as you can navigate to an earlier state recorded in the reflog and check it out.
In Lazygit, you toggle between the commits and reflog tabs within the commits panel using the `[` and `]` keys.

---

## Tips for Efficient Workflow in the Commits Panel

- **Keyboard Shortcuts**
  Lazygit’s keybindings are intuitive and context-sensitive, allowing you to guess common operations.
  For example, pressing `c` in a related panel generally invokes a commit operation, while `4` takes you straight to commits.

- **Interactive Rebase Made Easy**
  Amending old commits and deleting commits trigger interactive rebases through Lazygit’s interface, simplifying these otherwise complex Git operations.

- **Search**
  Using the search feature, you can quickly locate commits by message, author, or hash.

- **Amend Before Pushing**
  Use the amend action to fix mistakes or add changes to recent commits before pushing your branch to remote.

---

## Wrapping Up

The commits panel in Lazygit is a powerful tool for exploring and managing your Git commit history.
Its intuitive interface offers a way to inspect commits, switch between different commit states, and rewrite history with ease — all without leaving your terminal.
Whether you want to amend a commit, revert changes, or reset your branch, the commits panel streamlines these workflows.

If you haven’t already, give it a try to experience how Lazygit can speed up your Git management.
For more tips and deeper dives into other Lazygit panels, check out the rest of the [Lazygit Series]({{< ref "/tags/lazygit-series" >}}).
