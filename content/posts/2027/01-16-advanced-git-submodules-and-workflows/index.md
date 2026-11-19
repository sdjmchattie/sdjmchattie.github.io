---
date: 2027-01-16
title: "Beyond Branching: Git Submodules and Uncommon Commands Worth Knowing"
description: |-
  Once you're comfortable with commits, branches, and rebasing, Git offers powerful tools for modular repositories and complex histories.
  Learn how to assemble multi-repository packages with Git submodules, switch contexts instantly with worktrees, hunt down bugs with bisect, and recover lost commits with reflog.
slug: advanced-git-submodules-and-workflows
image: /images/posts/2027/01-16-advanced-git-submodules-and-workflows.png
tags:
  - Developer Tools
  - Software Architecture
  - Git
math: true
---

{{< tldr >}}
Before exploring advanced workflows, treat [Learn Git Branching](https://learngitbranching.js.org/) as your foundational benchmark for visualising commits and pointers.
Once that mental model is solid, [Git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules), [`git worktree`](https://git-scm.com/docs/git-worktree), [`git bisect`](https://git-scm.com/docs/git-bisect), and [`git reflog`](https://git-scm.com/docs/git-reflog) solve real problems that everyday branching cannot touch.

- **Set your pointer benchmark first:** Play through [Learn Git Branching](https://learngitbranching.js.org/) to master `HEAD`, relative references, and rebasing before tackling multi-repository setups.
- **Assemble modular packages cleanly:** Use [`git submodule`](https://git-scm.com/docs/git-submodule) to combine independent module repositories into one parent package, and always push module commits before parent commits.
- **Keep parallel branches open:** Spin up sibling folders with [`git worktree`](https://git-scm.com/docs/git-worktree) to handle urgent hotfixes or reviews without juggling stashes.
- **Debug and recover with confidence:** Isolate regressions in $O(\log N)$ steps using [`git bisect`](https://git-scm.com/docs/git-bisect) and rescue overwritten history through [`git reflog`](https://git-scm.com/docs/git-reflog).
{{< /tldr >}}

Most developers settle into a comfortable five-command [Git](https://git-scm.com/) loop: stage, commit, branch, pull, and push.
That routine handles single-repository feature work smoothly until a codebase splits across repositories, an urgent hotfix interrupts an unfinished refactor, or a subtle bug slips into a release.

I previously covered terminal workflows in my [Lazygit Series]({{< ref "/tags/lazygit-series" >}}), where visual panels take the friction out of daily staging and branch switching.
In this guide, I focus on the command-line features that unlock Git's trickier edges, starting with an interactive readiness benchmark before walking through [Git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules), [`git worktree`](https://git-scm.com/docs/git-worktree), [`git bisect`](https://git-scm.com/docs/git-bisect), and [`git reflog`](https://git-scm.com/docs/git-reflog).

## Setting Your Benchmark with Learn Git Branching

Before trying any advanced Git workflow, I recommend testing your foundational knowledge with [Learn Git Branching](https://learngitbranching.js.org/).
It's a free, browser-based interactive game that visualises every command you type against an animated commit tree.

Using this game as your personal benchmark matters because advanced Git features become predictable once you stop picturing branches as copies of folders.
Instead, you start seeing a repository as a [directed acyclic graph (DAG)](https://en.wikipedia.org/wiki/Directed_acyclic_graph) of immutable snapshots, with movable labels pointing at specific nodes.

If you want to know whether you're ready for submodules, worktrees, and history recovery, aim to finish both the "Main" and "Remote" tracks in the game.
Four concepts from those levels directly underpin every technique later in this article:

- **Branches and `HEAD` as pointers:** A branch is just a lightweight label pointing to one commit hash, while `HEAD` indicates whichever branch or commit you've currently checked out.
- **Relative commit navigation:** Operators like `~` (moving back along linear ancestors, such as `HEAD~3`) and `^` (choosing a parent on a merge commit) let you reference commits cleanly without copying raw hashes.
- **History manipulation:** Commands like [`git cherry-pick`](https://git-scm.com/docs/git-cherry-pick) copy individual commits across branches, while interactive [`git rebase`](https://git-scm.com/docs/git-rebase) (`git rebase -i`) lets you reorder, squash, or rewrite commits.
- **Remote tracking references:** Seeing how local branches diverge from remote-tracking pointers like `origin/main` makes [`git fetch`](https://git-scm.com/docs/git-fetch), [`git pull`](https://git-scm.com/docs/git-pull) `--rebase`, and [`git push`](https://git-scm.com/docs/git-push) intuitive rather than mysterious.

If terms like detached `HEAD` or rebasing still feel hazy, spend an hour working through those interactive puzzles first.
Once the visual graph clicks, the commands below will make far more sense.

## Assembling Modular Packages with Git Submodules

When a monolith outgrows a single codebase, teams often split it into independent repositories for separate modules (such as `auth-module`, `billing-module`, and `reporting-module`) that still need to come together inside an umbrella repository (`platform-package`) to form a complete release.
A [`git submodule`](https://git-scm.com/docs/git-submodule) lets you nest each module repository inside a subdirectory of the parent package while keeping every module's commit history completely separate.

Instead of copying source files from each module into `platform-package`, the parent repository tracks two things: a [`.gitmodules`](https://git-scm.com/docs/gitmodules) configuration file mapping each directory to its remote URL, and the exact commit hash pinned for each module.
Because the parent locks each subdirectory to a specific commit rather than a moving branch name, building an older release tag of `platform-package` always checks out the exact module versions that shipped together.

### Adding module repositories to a parent package

To assemble `platform-package` from its component repositories, navigate into the parent repository and attach each module using `git submodule add`.
You pass the remote repository URL followed by the local folder path where you want the module mounted.

```bash
# Run inside the platform-package root directory
git submodule add https://github.com/example/auth-module.git modules/auth
git submodule add https://github.com/example/billing-module.git modules/billing
git submodule add https://github.com/example/reporting-module.git modules/reporting
```

Running those commands clones each module repository into `modules/` and generates a `.gitmodules` file at the root of `platform-package`.
Opening `.gitmodules` shows the mapping between your local paths and the upstream repositories:

```ini
[submodule "modules/auth"]
	path = modules/auth
	url = https://github.com/example/auth-module.git
[submodule "modules/billing"]
	path = modules/billing
	url = https://github.com/example/billing-module.git
[submodule "modules/reporting"]
	path = modules/reporting
	url = https://github.com/example/reporting-module.git
```

Git automatically stages both `.gitmodules` and the pinned commit pointers for each `modules/*` path.
From there, a normal commit in the parent repository records the package composition for the rest of your team:

```bash
git commit -m "Attach auth, billing, and reporting module submodules"
```

### Cloning and pulling submodule updates

One of the first surprises teammates hit with submodules happens right after running a standard [`git clone`](https://git-scm.com/docs/git-clone) on `platform-package`.
By default, cloning the parent repository creates empty `modules/auth`, `modules/billing`, and `modules/reporting` directories without downloading any of their files.

To clone the umbrella package and populate every module in one pass, include the `--recurse-submodules` flag.
If you've already cloned the parent repository (or just pulled a commit that introduced a new module), initialise and fetch the nested repositories manually:

```bash
# Clone the parent package along with all nested modules
git clone --recurse-submodules https://github.com/example/platform-package.git

# Or populate submodules inside an already cloned repository
git submodule update --init --recursive
```

I also recommend turning on two global Git settings so [`git status`](https://git-scm.com/docs/git-status) and [`git diff`](https://git-scm.com/docs/git-diff) clearly summarise which modules have moved between commits.
Without them, Git prints only raw commit hashes when a module pointer changes.

```bash
git config --global status.submoduleSummary true
git config --global diff.submodule log
```

When `auth-module` ships new features upstream and you want `platform-package` to adopt them, pull the latest commits into the module and commit the updated pointer in the parent repository.
Testing the combined package before committing that pointer ensures all modules still integrate cleanly.

```bash
# Fetch and check out the latest commit from the auth module's default branch
git submodule update --remote modules/auth

# Stage and record the new module version in platform-package
git add modules/auth
git commit -m "Update auth-module to include MFA improvements"
```

### Navigating detached HEAD when editing a module

If you step into `modules/auth` right after cloning `platform-package` and run `git status`, you'll see a `HEAD detached at ...` notice.
Remember the pointer model from [Learn Git Branching](https://learngitbranching.js.org/): the parent package locks the submodule to a raw commit hash, not a branch name, so `HEAD` points directly to that commit.

That detached `HEAD` state is the biggest trap when you need to fix a bug in `auth-module` while working inside `platform-package`.
If you edit files and commit directly inside `modules/auth` without checking out a branch first, your new commit sits orphaned on a detached `HEAD` and disappears the next time someone runs `git submodule update`.

Whenever you plan to modify a module, check out a real branch inside that module first using [`git switch`](https://git-scm.com/docs/git-switch).
Then follow a strict two-step push order: publish the module's commits to its own remote before pushing the updated pointer in `platform-package`.

```bash
# 1. Enter the module and attach HEAD to a real branch first
cd modules/auth
git switch -c fix/session-timeout

# 2. Make your edits, test, commit, and push the module repository
git add src/session.py
git commit -m "Extend token refresh grace period"
git push -u origin fix/session-timeout

# 3. Return to the parent package, commit the new pointer, and push
cd ../..
git add modules/auth
git commit -m "Bump auth-module for session timeout fix"
git push --recurse-submodules=check origin main
```

Pushing the module first is crucial because `platform-package` only stores a commit hash.
If you push `platform-package` while the new `auth-module` commit exists solely on your laptop, teammates and [continuous integration (CI)](https://en.wikipedia.org/wiki/Continuous_integration) runners won't be able to fetch that hash and every build will fail.

Adding `--recurse-submodules=check` (or `on-demand` to push submodules automatically) instructs `git push` to verify that every referenced module commit is already on a remote before accepting the parent push.
Finally, keep an eye on coupling: if every single feature forces simultaneous commits across `platform-package` and all three modules, a single monorepo or a language-specific package manager will usually serve you better than submodules.

## Parallel Working Directories with Git Worktree

Imagine you're halfway through rewriting `billing-module` on a feature branch, with half-edited files scattered across your working tree, when an urgent production bug lands in your inbox.
Reaching for [`git stash`](https://git-scm.com/docs/git-stash) works for small pauses, but stashing large edits, switching branches, rebuilding dependencies, and popping the stash later is slow and error-prone.

[`git worktree`](https://git-scm.com/docs/git-worktree) eliminates that shuffle by letting you check out multiple branches of the same repository into separate directories at once.
Every worktree shares the same underlying `.git` object database, so creating one takes a second and avoids maintaining duplicate clones on disk.

To fix a bug without touching your unfinished feature work, spin up a sibling folder checked out to a new hotfix branch off `main`:

```bash
# Create a parallel directory at ../platform-hotfix on a new branch
git worktree add -b hotfix/token-expiry ../platform-hotfix main
```

You can now open `../platform-hotfix` in a second editor window or terminal tab, fix the bug, run tests, commit, and push while your primary directory stays untouched.
Git also enforces a helpful safety rail here: it refuses to check out the same branch in two worktrees simultaneously, preventing two folders from overwriting each other's branch tip.

Once your hotfix is merged and pushed, list your active working trees and clean up the temporary directory cleanly:

```bash
# Inspect all active working directories tied to this repository
git worktree list

# Remove the temporary directory and clean up its tracking metadata
git worktree remove ../platform-hotfix
```

If you ever delete a worktree folder manually with `rm -rf`, run `git worktree prune` afterwards so Git removes the stale reference.

## Automated Bug Hunting with Git Bisect

Picture an integration test failing on `HEAD` today when you know for certain it passed at tag `v2.1.0`, roughly 250 commits ago.
Manually checking out commits one by one to find where the test broke is an $O(N)$ linear scan, as I explored in [Understanding Big-O Notation: Why Algorithm Complexity Matters]({{< ref "01-09-understanding-big-o-notation" >}}).

[`git bisect`](https://git-scm.com/docs/git-bisect) turns that tedious hunt into an $O(\log N)$ [binary search](https://en.wikipedia.org/wiki/Binary_search) over your commit history.
Across 250 commits, Git checks out the midpoint repeatedly and narrows down the exact breaking commit in around eight steps.

To run an interactive search, mark a known broken commit (`HEAD`) and a known working commit (`v2.1.0`):

```bash
git bisect start
git bisect bad HEAD
git bisect good v2.1.0
```

Git checks out the commit halfway between those two points in a detached `HEAD` state.
You test your code, type `git bisect good` or `git bisect bad` based on the result, and repeat until Git prints the exact commit hash that introduced the regression, finishing with `git bisect reset` to return to your branch.

### Automating the search with a test command

Interactive bisecting is already fast, but `git bisect run` removes human involvement completely whenever you can express the bug as an automated test or shell script.
Using [`pytest`](https://docs.pytest.org/) as an example, you can pass the bad and good boundaries straight to `start` and let Git execute the test suite at every midpoint:

```bash
git bisect start HEAD v2.1.0
git bisect run pytest tests/test_billing_totals.py
```

Under the hood, Git inspects the [POSIX](https://en.wikipedia.org/wiki/POSIX) [exit code](https://en.wikipedia.org/wiki/Exit_status) returned by your command at each step.
An exit code of `0` marks the commit as good, `1` through `127` (excluding `125`) marks it as bad, and `125` tells Git to skip a commit if the project couldn't compile or run at that point.

Wait a few seconds while Git walks the tree, read the guilty commit printed at the end, and always run `git bisect reset` afterwards to exit the detached `HEAD` state:

```bash
git bisect reset
```

## Recovering Lost History with Git Reflog

Anyone who practises interactive rebasing or resets branches aggressively eventually hits a sinking feeling: you run [`git reset`](https://git-scm.com/docs/git-reset) `--hard HEAD~3` on the wrong branch, or drop a crucial commit during a rebase, and watch your work vanish from [`git log`](https://git-scm.com/docs/git-log).
Fortunately, Git doesn't delete those snapshots immediately; it simply moved the branch label away from them, leaving the commits orphaned in its local object database.

Every time `HEAD` or a local branch tip moves (through commits, branch switches, resets, or rebases), Git records the previous position in a local reference log called [`git reflog`](https://git-scm.com/docs/git-reflog).
If you prefer a visual terminal interface like [Lazygit](https://github.com/jesseduffield/lazygit), I showed how to inspect and restore entries from this exact history in [Lazygit Series: The Commits Panel]({{< ref "../2025/06-28-lazygit-commits-panel" >}}).

From the command line, run `git reflog` right after a mistaken reset to inspect recent movements of `HEAD`:

```bash
git reflog
```

Git prints a reverse-chronological list of every recent state, tagged with relative selectors like `HEAD@{0}` and `HEAD@{1}`:

```text
b7d14e2 (HEAD -> main) HEAD@{0}: reset: moving to HEAD~3
9f2a8c1 HEAD@{1}: commit: Add currency rounding validation
4c10e7b HEAD@{2}: commit: Handle invoice credit memos
1a8d5f0 HEAD@{3}: rebase (finish): returning to refs/heads/main
```

Because `HEAD@{1}` points straight to the commit that sat at the tip of `main` right before your reset, recovering your work takes a single command.
You can either snap your current branch back immediately or create a fresh recovery branch so you can inspect what happened safely:

```bash
# Option A: Restore your branch directly to the pre-reset commit
git reset --hard HEAD@{1}

# Option B: Create a separate recovery branch without altering main
git switch -c rescued-work HEAD@{1}
```

Keep one caveat in mind when relying on the reflog: unlike commits and tags, reflog entries are strictly local to your machine and aren't pushed to remotes.
Git also expires old unreachable entries during periodic garbage collection (after 90 days for reachable commits and 30 days for unreachable ones by default), so recover lost work promptly rather than weeks later.

## Wrapping Up

Git feels intimidating mostly when commands appear to mutate files mysteriously behind the scenes.
Building your pointer intuition with [Learn Git Branching](https://learngitbranching.js.org/) removes that guesswork, turning submodules, worktrees, bisect, and reflog into predictable tools you can reach for whenever a project outgrows basic branching.

If you'd like to explore more workflow tips and visual tooling, browse the [Developer Tools]({{< ref "/tags/developer-tools" >}}), [Software Architecture]({{< ref "/tags/software-architecture" >}}), and [Git]({{< ref "/tags/git" >}}) tags, or check out my [Lazygit Series]({{< ref "/tags/lazygit-series" >}}) starting with [Managing Git Repositories with Lazygit]({{< ref "../2025/05-31-lazygit-repository-management" >}}).
Pick one technique from this guide and test it in a scratch repository this week before you need it under release pressure.
