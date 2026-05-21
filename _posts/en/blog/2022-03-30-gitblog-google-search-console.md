---
title: "Getting a GitHub Blog Indexed by Google — Search Console Registration"
description: "Register your GitHub blog with Google Search Console and configure sitemap.xml and robots.txt to make it discoverable in search results"
excerpt: "Register with Google Search Console, generate sitemap.xml, and configure robots.txt to expose your GitHub blog to search engines"
date: 2022-03-30
categories: Github_Blog
tags: [GoogleSearchConsole, sitemap, robots.txt, SEO, Jekyll, search-engine, crawling]
ref: gitblog-google-search-console
---

:bulb: This post summarizes how to expose GitHub blog posts to Google Search.
{: .notice--info}

# [01]  What is Google Search Console?

> A service for registering websites with Google's search engine so they can be discovered, and for monitoring search results. It works through web crawling.

- For blog posts to appear in Google Search, Google's crawler has to read the site (crawl it).
- You can register and monitor your site at [Google Search Console](https://search.google.com/search-console/about){:target="_blank"} (a Google account is required).


# [02]  Registering with Google Search Console


- After logging in with your Google account, visit the site and click **Start Now**.

  ![image 1](https://user-images.githubusercontent.com/76153041/160787269-37114862-a611-48e2-8be3-b05a8dad44c2.png)

- A GitBlog already has a URL, so enter the blog URL under **URL prefix**.

  ![image 2](https://user-images.githubusercontent.com/76153041/160787273-047d4228-b41d-43af-8517-a2373a3155ac.png)

- Complete **Ownership Verification** to prove the URL is yours.

  ![image 3](https://user-images.githubusercontent.com/76153041/160787274-021c4f7d-1044-4ea6-afb1-0723bfad4db4.png)

- Copy the HTML file shown in the popup (e.g., `google675xxxx.html`) into the root of the blog repository and push it.
- `git add *`, `git commit -m xxx`, `git push`

  ![image 20](https://user-images.githubusercontent.com/76153041/160791984-e5f45d05-608a-47ab-9d29-770cb259eb1d.png)

- After the file is uploaded, wait briefly — you'll see the ownership-confirmed popup.

  ![image 4](https://user-images.githubusercontent.com/76153041/160787277-033ea137-cc95-47d6-a6cf-fbe6a94605fd.png)


# [03]  Generating and Submitting sitemap.xml

- Ownership verification lets Google know the blog exists, but the crawler still needs structured data to read and serve information from the site.
- `sitemap.xml` lists every page on the website so search engines can surface them to users.
- There are two ways to generate `sitemap.xml`:
  - Write it manually
  - Generate it via Jekyll's `jekyll-sitemap` plugin
- The **Minimal Mistakes** theme used by this blog can generate it through the `jekyll-sitemap` plugin.
  - Confirm `jekyll-sitemap` is listed under `plugins` in `_config.yml`.

    ![image 12](https://user-images.githubusercontent.com/76153041/160787294-4786d5ba-2d5f-4de5-9d1d-07f6016cb2da.png)
  - Add `gem 'jekyll-sitemap` to the `Gemfile`.

    ![image 5](https://user-images.githubusercontent.com/76153041/160787278-7ecb90f0-ab1b-4b66-bfaa-2d950de598ea.png)

  - Run `bundle install` in the terminal.

    ![image 7](https://user-images.githubusercontent.com/76153041/160787284-00f0d880-a94d-40c3-bb10-d0d69ab76ea3.png)

  - After pushing to the Git repository, open `htpps://xxx.github.io/sitemap.xml` — the list will look like this:

    ![image 11](https://user-images.githubusercontent.com/76153041/160787293-7d14ee0d-3fe9-4eca-ae75-8cddccbc9fab.png)

- In Google Search Console, go to **Index → Sitemaps**.

  ![image 13](https://user-images.githubusercontent.com/76153041/160787299-ded6a8a4-2058-4646-96bd-3124e980759e.png)

- Enter `sitemap.xml` under "Add a new sitemap" and submit.

  ![image 14](https://user-images.githubusercontent.com/76153041/160787302-ca1d0463-ac41-416f-8b8c-a3ed6a311cca.png)

  ![image 15](https://user-images.githubusercontent.com/76153041/160787304-121e1694-eba1-4ded-ba09-e79aeeee999f.png)

# [04]  Generating and Applying robots.txt

- `robots.txt` defines the rules a web crawler must follow when crawling the site.
- It controls which parts of the site can be referenced.
- Create `robots.txt` in the root of the blog repository with the following content:

```python
# User-agent : the crawler the rules apply to (* allows all)
# - Google's crawler is Googlebot, Naver's is Yeti, etc. — each engine has its own crawler.
# Allow: paths to allow crawling (/ permits everything under /)
# Sitemap: location of the sitemap
# - The sitemap is a directory of pages on the site.

User-agent: *
Allow: /

Sitemap: https://eona1301.github.io/sitemap.xml
```
