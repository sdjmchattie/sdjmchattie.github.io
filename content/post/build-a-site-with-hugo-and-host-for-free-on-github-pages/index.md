+++
date = '2025-01-20T21:20:13Z'
draft = true
title = 'How I built my website and host it for free on GitHub Pages'
toc = true
+++

## Introduction

There's that now old adage that if you're not online, you're no-one.
Perhaps that's a bit harsh when it comes to a personal presence on the world wide web, but it certainly applies to businesses.
In any case, I decided I wanted to get my own site up as it's about time I shared my experiences in the hope that they're useful to at least someone.
What better way to start my new blog than to tell you how I set it up.
Which tools did I use and why?
How do I get to host it for free?

### Which tools to use

You can use anything you want to create a website, but for most people, simplicity is key.
It's also important to choose something that can be hosted with static contents if you aim is to host it for free.
That's why I chose [Hugo](https://gohugo.io)!
Here are just a few of the reasons I choose this over other options:

- It's simple to get running on your machine.
- It's fast!
- It has loads of free themes to choose from.
- The content is all written as Markdown and Hugo does the rest.
- You can export all your content as a static site.

### Where to host for free

Free hosting of a whole site is kind of rare these days, but thankfully options still exist.
The one this blog post is going to focus on is GitHub Pages.
Every user on GitHub gets to host pages for their projects and one for their user.
Maybe you're not a developer, but you can still use this functionality.
You will need to use some Git commands though to push your contents up to the server.
I'll try to keep things as simple as possible.

## Step-by-step guide

Let's take it step-by-step.
If you find there's anything missing from here that you thought should be included, please [let me know]({{< ref "/contact" >}} "Contact Me") and I will aim to fix it.
I personally use macOS, so I apologise if you're using Windows and the instructions don't work on your computer.
Hopefully you can get the gist of what's going on or you can ask a techie friend for help.

### Installing Hugo

First of all, you need to get Hugo installed.
Thanksfully, [Hugo has instructions](https://gohugo.io/installation/) on how to do this on various operating systems.
In my case, I used [Homebrew](https://brew.sh) which I already had on my computer.
On a Mac, you should be able to open a terminal window by entering "Terminal" in a spotlight search (press Cmd + Space to access Spotlight).
Then to check for Homebrew, try the command

    brew --version

which should say something like

    Homebrew 4.4.16

It doesn't matter if your version number is different from mine.

If Homebrew isn't installed, you need to copy the command from the Homebrew website and paste it into your Terminal application to get it installed.

Once Homebrew is installed, you can install Hugo using

    brew install hugo

And that's it!

You can confirm it's installed by trying

    hugo version

in the Terminal where you should be told the version that's installed.
Mine says

    hugo v0.141.0+extended+withdeploy darwin/arm64 BuildDate=2025-01-16T13:11:18Z VendorInfo=brew

### Setting up your user's GitHub Pages

### Prepare GitHub to build your site

### Prepare a new website

### Get GitHub hosting your new site

### Add pages and posts to your site
