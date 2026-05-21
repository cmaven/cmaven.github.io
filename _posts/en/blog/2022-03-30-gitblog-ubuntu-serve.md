---
title: "Serving a Jekyll-based GitHub Blog from Ubuntu"
description: "Install Ruby and Jekyll on Ubuntu, then preview a GitHub blog locally or expose it on the local network"
excerpt: "Install Ruby and Jekyll on Ubuntu, then run a GitHub blog as a local server to preview it"
date: 2022-06-16
categories: Github_Blog
tags: [Jekyll, Ubuntu, Ruby, GEM, Bundler, local-server, blog-preview]
ref: gitblog-ubuntu-serve
---

:bulb: This post explains how to preview a blog on Ubuntu — either locally or from another machine on the same network.
{: .notice--info}

# [01]  Setting Up Jekyll on Ubuntu

> A service for registering websites with Google's search engine so they can be discovered, and for monitoring search results. It works through web crawling.

- Install Ruby and the related packages.

```shell
sudo apt-get update
sudo apt-get install ruby-full build-essential zlib1g-dev
```  

- Configure GEM so you don't have to run it with `sudo` — i.e., for convenience.
  > GEM is Ruby's library manager. Think of it as `apt-get` specialized for Ruby.
- The configuration below should be done as a non-root user.
```shell
echo '# Install Ruby Gems to ~/gems' >> ~/.bashrc
echo 'export GEM_HOME="$HOME/gems"' >> ~/.bashrc
echo 'export PATH="$HOME/gems/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```  

- Install Jekyll and Bundler.
```shell
gem isntall jekyll bundler
```

# [02]  Building or Downloading the GitBlog Site

- Clone an existing GitBlog site (git clone) and install the required packages.

```shell
# example
cd gitblog
bundle install
```  
- Run the GitBlog service.
```shell
''' Run locally '''
jekyll serve
''' Run bound to the server IP so external clients can connect '''
jekyll serve --host=${Server IP address}
```
