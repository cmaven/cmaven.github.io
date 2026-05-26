---
title: "Serving a Jekyll-based GitHub Blog from Ubuntu"
description: "Install Ruby and Jekyll on Ubuntu, then preview a GitHub blog locally or expose it on the local network."
excerpt: "Install Ruby and Jekyll on Ubuntu, then run a GitHub blog as a local server to preview it"
date: 2022-06-16
last_modified_at: 2026-05-26
categories: Github_Blog
tags: [Jekyll, Ubuntu, Ruby, GEM, Bundler, local-server, blog-preview]
ref: gitblog-ubuntu-serve
---

:bulb: This post explains how to preview a Jekyll-based GitHub Pages blog on Ubuntu — either locally or from another machine on the same network.
{: .notice--info}

# [01] Setting Up Jekyll on Ubuntu

Jekyll requires Ruby. The steps below install Ruby, configure RubyGems to avoid `sudo`, and then install Jekyll and Bundler.

## 1-1. Install Ruby and Dependencies

```shell
sudo apt-get update
sudo apt-get install ruby-full build-essential zlib1g-dev
```

`build-essential` and `zlib1g-dev` are needed to compile native gem extensions that some Jekyll plugins require.

## 1-2. Configure RubyGems (GEM) for the Current User

> **GEM** is Ruby's package manager — similar to `pip` for Python or `apt-get` for Ubuntu packages.

By default, installing gems system-wide requires `sudo`. The configuration below tells GEM to install gems into your home directory instead, so you can manage them without elevated privileges:

```shell
echo '# Install Ruby Gems to ~/gems' >> ~/.bashrc
echo 'export GEM_HOME="$HOME/gems"' >> ~/.bashrc
echo 'export PATH="$HOME/gems/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Run this as a **non-root user**. The `source` command applies the changes immediately without reopening the terminal.

## 1-3. Install Jekyll and Bundler

```shell
gem install jekyll bundler
```

Verify the installation:

```shell
jekyll --version
bundler --version
```

# [02] Clone and Install Your Blog

If you already have a GitHub Pages repository, clone it and install its gem dependencies:

```shell
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
bundle install
```

`bundle install` reads `Gemfile.lock` and installs the exact gem versions your blog requires, ensuring the local preview matches the GitHub Pages build.

# [03] Run the Local Preview Server

## 3-1. Local Access Only

```shell
jekyll serve
```

After the build completes, open `http://127.0.0.1:4000` in a browser on the same machine. Changes to source files trigger an automatic rebuild (watch mode is on by default).

## 3-2. Accessible from Other Machines on the Network

```shell
jekyll serve --host=<Server IP address>
```

Replace `<Server IP address>` with the Ubuntu machine's local IP (find it with `ip addr` or `hostname -I`). Any device on the same network can then open `http://<Server IP>:4000` to preview the blog — useful for checking the layout on a phone or tablet.

## 3-3. Useful Additional Flags

| Flag | Effect |
|------|--------|
| `--drafts` | Include posts in `_drafts/` in the preview |
| `--future` | Include posts with a future `date` |
| `--incremental` | Rebuild only changed files (faster for large sites) |
| `--port 5000` | Listen on a different port |

Example combining flags:

```shell
jekyll serve --host=192.168.1.10 --drafts --future
```

# [04] Stopping the Server

Press `Ctrl+C` in the terminal to stop the Jekyll server.

# [05] Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| `gem install` requires sudo | GEM_HOME not set | Run the `~/.bashrc` export steps from Section 1-2 and `source ~/.bashrc` |
| `bundle install` fails | Missing build tools | `sudo apt-get install build-essential` |
| Port 4000 already in use | Another process is listening | Use `--port 5000` or kill the process with `fuser -k 4000/tcp` |
| Live reload not working | Firewall blocking the LiveReload port | Allow port 35729, or use `--no-livereload` |

# [06] Quick Reference

| Step | Command |
|------|---------|
| Install Ruby | `sudo apt-get install ruby-full build-essential zlib1g-dev` |
| Configure GEM home | Add `GEM_HOME` and `PATH` exports to `~/.bashrc` |
| Install Jekyll | `gem install jekyll bundler` |
| Clone blog | `git clone https://github.com/<user>/<repo>.git` |
| Install gems | `bundle install` |
| Serve locally | `jekyll serve` |
| Serve on network | `jekyll serve --host=<IP>` |
