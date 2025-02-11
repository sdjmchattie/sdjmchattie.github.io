---
date: {{ .Date }}
draft: true
title: {{ replace .File.ContentBaseName "-" " " | title }}
description: |-
  Description
slug: {{ .File.ContentBaseName }}
image: /images/posts/image.jpg
tags:
  - Blog Post
---
