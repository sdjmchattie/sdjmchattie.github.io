---
aliases:
  - /posts/tips-and-tricks-when-working-in-visual-studio-code
date: 2025-02-08
title: Tricks I use in Visual Studio Code to work more efficiently
description: |-
  Visual Studio Code is an incredibly competent development tool, but it can be hard to know how to use it efficiently.
  This post looks at some of the extensions I use; how to work with files in a workspace and how to manipulate file contents with some advanced shortcuts.
slug: tips-and-tricks-in-visual-studio-code
image: /images/posts/2025/02-08-vscode-tricks.jpg
tags:
  - VSCode
  - Tips and Tricks
---

Visual Studio Code is an incredibly competent development tool from Microsoft and amazingly it's free.
I use it every day in my professional career and, through years of use, I've become very familiar with how it works.
When you gain this sort of familiarity with a piece of software, you forget the struggles you had initially and the optimisations you apply to get more out of the tool.
I recognised this recently when I was working with fellow engineers and performing these tricks in front of them.
They were saying "How did you do that?" and "I had no idea you could do that!".
So I thought I'd share some of the tips I'm aware of so that others can get that warm fuzzy feeling of knowing how to shortcut typical problems during development.

## Recommended extensions

For all that Visual Studio Code can do out of the box, a huge amount of the power available comes from extensions.
These allow you to do things like shuffle or sort lines, support syntax highlighting in a number of languages, and bring the power of GitHub Copilot into your work.

Installing extensions is easy.
You can click the extensions button on the left hand navigation panel:

![Extensions navigation item](extensions-navigation.png)

Or you can choose the View menu and select Extensions.

The side panel that opens has search functionality, then you just click the Install button for any you want to try.
Uninstalling is as simple as finding the extension in this panel again, selecting this small gear icon and choosing the Uninstall.

Here are a few of the extensions I use and why I think they make Visual Studio Code even better.

### GitHub Copilot

I have a whole article on this blog about [GitHub Copilot in Visual Studio Code]({{< relref "02-02-github-copilot-in-vscode" >}}).
What this allows you to do is get help from AI when you aren't sure how to do what you want to do in a programming language.
You can discuss with GitHub Copilot in a chat window, and it will also make suggestions while you are writing code, which can dramatically reduce the time to write the more mundane boilerplate code.

### Markdown All in One

The [Markdown All in One](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one) extension is very popular, and makes writing Markdown a lot easier.
I use this one all the time and it's mostly automatic.
When you highlight a word and press Ctrl + B (Cmd + B on Mac) it will apply the markdown needed to make the text bold.
When you start a list of numbered items, it adds new numbers after you press enter so that you don't have to.
It also provides some extra commands to Visual Studio Code to format Markdown with.

### Language support extensions

This is a rather general category and every language will have a different extensions that helps support it.
Typically what you get from these extensions is automatic highlighting for language keywords and syntax.
Some of them will also give you snippets and auto-completion for common built-in functions.

- [MagicPython](https://marketplace.visualstudio.com/items?itemName=magicstack.MagicPython)for Python
- [Ruby Syntax Highlighting](https://marketplace.visualstudio.com/items?itemName=SarahRidge.vscode-ruby-syntax) for Ruby
- [C/C++](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools) from Microsoft for C/C++

This list is purely a few of the languages I tend to use and by no means either complete or the only extension you can use for each language.
Extensions are updated all the time, so be sure to look for ones that help with your work.
One thing I always do is check how many people have downloaded the extension before choosing it.
Generally, if an extension is popular, it's probably good.

## Working with workspaces

Workspaces are how Visual Studio Code keeps projects together so you can work on the project in a single space.
That's doesn't mean that you can only have one program's source code in a workspace though.
It's more a collection of folders with some settings associated with them as well.

If you're working on more than a couple of source files, you really should consider setting up a workspace for your work.
It's super easy!
Starting with a new window, select the Explorer icon in the navigation; it's the top item.
Or select Explorer from the View menu.
Now choose the blue Open Folder button as shown.

![Open a Folder in a new Workspace](add-folder-to-new-workspace.png)

From here, you can choose the folder that contains your project or source code.
This will provide a view of the files and folders inside that folder in place of the blue button that was there.
It will also add a title to the top of the Explorer that says WORKSPACE.
If you have more folders you want to see in the workspace, you can use the File menu and choose Add Folder to Workspace.
Each of these is collapsible in the explorer.

Now that you have a workspace, you can do things like search across the files in your workspace using the global search function in the left navigator.
Or choose Search from the View menu.
You can not only find things this way, but also replace things across the whole project.
If you only want to find from a single folder you added to the workspace, use the "files to include" option in this search.
For example, if you have a folder called `my-amazing-project` added to the workspace, you can put `./my-amazing-project/` in that field and only results from there will come up.
There will be more articles on this blog soon about how I use regular expressions while I work on files.

Now that you have a workspace, why not save it alongside your source code?
I check mine into Git as well, but that's optional.
You can save a workspace by using the File menu and choosing Save Workspace As.
Once created, a workspace file can be double clicked to re-open all of the folders you were working on.

What else can you do with a workspace?
You can open a Terminal window right here in Visual Studio Code and run things from the workspace.
Choose the Terminal menu and choose New Terminal to have it open a Terminal panel and automatically go to the folder your workspace belongs to.

You can also specify settings for Visual Studio Code that should only be used in this workspace.
Go to the Settings for Visual Studio Code and you'll notice that there's a sub-tab called Workspace.
I've got it selected in the screenshot below.

![Workspace Settings](workspace-settings.png)

Anything you change in here will only apply while you use this workspace in Visual Studio Code.
This is great if your project uses a language you don't normally work in.
You can enabled features from your extensions in this workspace and now have them kick in when you work on other things.

Speaking of extensions, you can even have extensions be recommended to someone opening your workspace.
Looking back at your extensions list, you can choose the gear icon for any extension you've already got installed and choose the Add to Workspace Recommendations menu item.
Now when someone else opens the workspace, which could even be you in the future of course, if those extensions are not already installed, it will recommend you install them.
This is great if you have extensions that really should be installed to work on the project.

There are so many more reasons why workspaces are useful in Visual Studio Code, like adding build commands to the workspace so they're readily available.
But I want to keep this blog article short, so perhaps spend some more time looking online if you want to know more.

## Advanced ways of manipulating files

I work so much in Visual Studio Code that I end up learning and using all sorts of tricks that I take for granted.
Then I work in front of others and they keep stopping me to ask how I did one thing or another.
So I've put together some of the key things I tend to do which makes my life a lot easier.

### Move your cursor one word at a time

This is a simple one, but if you hold Alt (Option on Mac), you can now press left and right to move the cursor one whole word at a time.
You can use this to quickly get through the text if you're not using the mouse, and it's really very useful when you are using the following trick.

### Working on multiple lines at once

This may surprise you, but you can work on more than one line at once.
If you hold the Alt + Shift keys (Option + Shift on Mac) and drag your mouse over the text, you'll notice that the highlighting is a bit different.
Instead of highlighting whole lines, you draw a rectangle of selection in the text.
Once you've got things highlighed this way, if you start typing or using the arrow keys, you'll be editing all of the selections at once.

If you only want to set the cursor without highlighting, hold Ctrl + Alt (Cmd + Option on Mac) while pushing up or down on the arrow keys, and your cursor will grow taller in either the upward or downward direction.
Try pressing Home or End (Cmd + Left or Cmd + Right on Mac) to move the cursors on all those lines to the far end of a line.
Now you can add the same text to the start or end of all of those lines at once.
Remember the trick from above?
Try Alt (Option on Mac) with left or right and you'll move all the cursors on all of the lines one word at a time, even if the words are different lengths on all of the lines.

### Moving lines up and down

I often find I need to move a line, or even a whole block of lines up or down through the file.
Sure you can highlight, cut, move the cursor, paste.
But if you prefer, because it's faster, hold the Alt key (Option on Mac) and press up or down.
The whole line you're on moves up or down and the other text around is moves to the other side of it.
No more accidentally losing the contents of the clipboard while you were moving lines around.

**Bonus tip:** also hold Shift at the same time and the lines get duplicated instead of moved.

### Quick accurate highlights with the mouse

I was surprised this wasn't more common knowledge, as I don't think this is Visual Studio Code specified but here are a few tricks that really make highlighting a breeze when using the mouse.

- Select a whole word by double clicking it instead of dragging your highlight.
- Double click then start dragging and now any other words you pass over are highlighted entirely without missing any letters from the start or end of them.
- Triple click anywhere in a paragraph to select the whole paragraph.
- Triple click them start dragging to select more whole paragraphs along with the first.

### Edit all occurrences in a file

This is critical for some of the work I do.
This is mostly because I use regular expressions for a lot of the complex searches I do, otherwise find and replace is usually sufficient.
But let's say you have a file with things like "Phase 123", "Phase 456" and "Phase 678" and you want to get rid of the numbers without using regular expressions.

Highlight any single instance of the word `Phase` and right-click it.
You will have a menu appear with an option to Change All Occurrences.
Select that option and now you'll have all the copies of the word Phase highlighted.
Remember the tricks from before?

- Hold Alt (Option on Mac) then tap right one time.
  All the cursors will now be immediately after the numbers that follow the word Phase.
- Hold Alt + Shift (Option + Shift on Mac) and tap left one time.
  All the digits are now selected regardless of how many there are after each instance of Phase.
- Press backspace to remove them all, then backspace to remove the extra space before them.

There are caveats to this approach.
If you have the word Phase anywhere else in your file, this is going to mess those instances up, so it's worth checking your work!

## Wrapping Up

This post has shown you some of the more poweruser things you can do with Visual Studio Code.
We've looked at some extensions which enhance the power of Visual Studio Code and how they can be installed or uninstalled easily.
We've looked at workspaces and some of the benefits they bring to your projects, especially when working with others.
We've looked at some of the tricks you can do when navigating your files to speed up common actions you might need to take.

I hope these tricks are useful to you.
If you have a specific problem you're having in Visual Studio Code, do get in touch.
I'm confident there's a solution to the problem and I would hope to be able to send you in the right direction with it.
