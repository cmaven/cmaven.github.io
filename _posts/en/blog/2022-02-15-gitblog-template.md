---
title: "How to Write a GitHub Blog Post"
description: "Guide to writing posts on a Jekyll-based GitHub blog — markdown syntax, image insertion, code blocks, and emoji usage"
excerpt: "A reference for markdown syntax, image uploads, code blocks, links, and emoji when writing GitHub blog posts"
date: 2022-02-15
categories: Github_Blog
tags: [Template, GithubBlog, Markdown, Jekyll, blog-writing, code-block, image-insertion]
ref: gitblog-template
---

:triangular_flag_on_post: Updated 2024-02-20
{: .notice--warning}

>Top-of-post frontmatter

- Indicates that the page is a Post

    ```python
    ---
    title: "GitBlog"
    date: 2022-02-15
    categories: Gitblog
    tags: [Temaplte]
    ---

    '''
    Post metadata

    * categories
    - Match against the categories you created
    - C / C++ / css / docker / excel / git / gitblog / html / k8s / linux / python /storage / vscode / windows
    - Capitalize the first letter
    * tags
    - Free-form
    '''
    ```  

:bulb: This document summarizes how to write a Post.
The text below is ***lorem ipsum***.
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
{: .notice--info}

# [01]  Content Sections

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed ac dolor sit amet purus malesuada congue. Duis molestie tincidunt orci a venenatis. Praesent vehicula lectus vel risus convallis, in faucibus erat luctus.

## Section 1

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas dignissim luctus dui, vitae cursus risus venenatis non. Praesent at vehicula erat. Donec ornare dapibus turpis, eu fringilla nibh fermentum a. Nullam eget metus a justo malesuada tristique.

### Section 2

Praesent vestibulum, lectus quis venenatis venenatis, nibh dui mattis tellus, eget feugiat orci ligula sed mauris. Phasellus blandit, mauris nec hendrerit faucibus, tortor nibh lobortis lectus, in lobortis dolor nisl in nisl.

#### Section 3

Vivamus a justo at urna sollicitudin auctor. Cras commodo, ipsum at consequat efficitur, ipsum massa congue justo, vel egestas sapien magna sed metus.


# [02]  Syntax

## Line Break

Two spaces at the end of the first line, then Enter: <u>Space, Space, Enter</u>

```python
This is the first line. #Space#Space#Enter
This is the second line.
```  

## Bold, Italic, Strikethrough, Underline

**bold**  `**bold**`
*italic*  `*italic*`
~~strikethrough~~  `~~strikethrough~~`
<u>underline</u>  `<u>underline</u>`


## Code Block

```python
# Wrap code with triple backticks as shown below

# ```
# code
# ```
```  

- Major supported languages:
  - bash, bat, console,
  - c, cpp, go, java, python,
  - cmake, console, make, vim
  - css, html, js, jsp, markdown, r, sass
  - sql, sqlite3,
  - xml, yaml

- Example:

    ```python
    ### --- file created/modified

    # comment
    import os

    class Class():
        value1 = 0

        def __str__(self):
            return self.value1
        
        def function(parm1, parm2):
            values = 0
            return

    if __name__ == '__main__':
        main()
    ```  

## Emoji

:bulb: is written as `:bulb:`

:small_blue_diamond: Reference: [https://gist.github.com/rxaviers/7360908](https://gist.github.com/rxaviers/7360908){:target="_blank"}

### Common Emoji

:exclamation:  `:exclamation:`
:fire:  `:fire:`
:star:  `:star:`
:cloud:  `:cloud:`
:sunny:  `:sunny:`
:zap:  `:zap:`
:milky_way:  `:milky_way:`
:computer:  `:computer:`
:loudspeaker:  `:loudspeaker:`
:scroll:  `:scroll:`
:page_with_curl:  `:page_with_curl:`
:clipboard:  `:clipboard:`
:closed_book:	`:closed_book:`
:green_book:  `:green_book:`
:memo:  `:memo:`
:rocket:  `:rocket:`
:beginner:  `:beginner:`
:round_pushpin:  `:round_pushpin:`
:triangular_flag_on_post:  `:triangular_flag_on_post:`
:arrow_forward:  `:arrow_forward:`
:arrow_backward:  `:arrow_backward:`
:arrow_left:  `:arrow_left:`
:arrow_right:  `:arrow_right:`
:red_circle:  `:red_circle:`
:diamonds:  `:diamonds:`
:large_blue_circle:  `:large_blue_circle:`
:large_blue_diamond:  `:large_blue_diamond:`
:large_orange_diamond:  `:large_orange_diamond:`
:small_blue_diamond:  `:small_blue_diamond:`
:small_orange_diamond:  `:small_orange_diamond:`
:ballot_box_with_check:  `:ballot_box_with_check:`


## Links

> Open in the same window

:small_blue_diamond: Reference: [Open in the same window](http://google.co.kr)

> Open in a new window

:small_blue_diamond: Reference: [Open in a new window](http://google.co.kr){:target="_blank"}

```python
# Open in the same window
:small_blue_diamond: Reference: [Open in the same window](http://google.co.kr)

# Open in a new window
:small_blue_diamond: Reference: [Open in a new window](http://google.co.kr){:target="_blank"}
```  

## Images

Images are hosted via GitHub Issues.
The repository hosting the Issues must be *public*.

### Uploading an Image

Issues :arrow_forward: New Issue :arrow_forward: Open a blank issue :arrow_forward: paste the image into the Write field.
Then copy the generated link and paste it into the page.

![2024-02-20 18 15 52](https://github.com/cmaven/cmaven.github.io/assets/76153041/0916505a-27a7-496f-8525-145e8cd32d76)

![2024-02-20 18 16 11](https://github.com/cmaven/cmaven.github.io/assets/76153041/e1914280-8128-4b96-8e33-b152247a4f6e)

![2024-02-20 18 17 39](https://github.com/cmaven/cmaven.github.io/assets/76153041/bfc1d8fc-da33-467d-9fe4-b0800c881fb2)

![2024-02-20 18 18 02](https://github.com/cmaven/cmaven.github.io/assets/76153041/e858e82d-96af-425d-a4c3-9e4d4e588d81)

- Example:
![unsplash-image-9](https://github.com/cmaven/cmaven.github.io/assets/76153041/0ed9c920-d723-4edd-8c72-60f58514875f)

### Wrapping an Image in a Link

Make the image clickable to navigate to another URL.
- `description` is the tooltip shown when hovering over the image.

[![unsplash-image-9](https://github.com/cmaven/cmaven.github.io/assets/76153041/0ed9c920-d723-4edd-8c72-60f58514875f "description")](http://google.com){:target="_blank"}

```python
# Open in the same window
[![unsplash-image-9](https://github.com/cmaven/cmaven.github.io/assets/76153041/0ed9c920-d723-4edd-8c72-60f58514875f "description")](http://google.com)

# Open in a new window
[![unsplash-image-9](https://github.com/cmaven/cmaven.github.io/assets/76153041/0ed9c920-d723-4edd-8c72-60f58514875f "description")](http://google.com){:target="_blank"}
```

### Image Sizing and Alignment

- Resize

    ```python
    # Resize (using html)
    <img src="https://github.com/cmaven/cmaven.github.io/assets/76153041/0ed9c920-d723-4edd-8c72-60f58514875f" width="100px" height="100px">{: .align-center}
    ```

- Alignment

    ```python
    # Center
    ![unsplash-image-9](https://76153041/0ed9c920-d723-4edd-8c72-60f58514875f)
    {: .align-center} 
    # Left
    ![unsplash-image-9](https://76153041/0ed9c920-d723-4edd-8c72-60f58514875f)
    {: .align-left} 
    # Right
    ![unsplash-image-9](https://76153041/0ed9c920-d723-4edd-8c72-60f58514875f)
    {: .align-right} 
    ```  

- Example (300px, centered)
<img src="https://github.com/cmaven/cmaven.github.io/assets/76153041/0ed9c920-d723-4edd-8c72-60f58514875f" width="300px" height="300px">{: .align-center}



## Lists

- list
  - list
    - list

1. list
   1. list
      - list
   1. list
   2. list
2. list

- [ ] unchecked
- [x] checked

```python
- list
  - list
    - list

1. list
   1. list
      - list
   2. list
   3. list
2. list

- [ ] unchecked
- [x] checked
```  


## BlockQuote

> Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed ac dolor sit amet purus malesuada congue.

>> Nested block quote. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Donec velit neque, auctor sit amet aliquam vel.

```python
> Lorem ipsum dolor sit amet, consectetur adipiscing elit.

>> Nested block quote. Vestibulum ante ipsum primis in faucibus orci luctus.
```  

## Footnotes

Here is a simple footnote[^1].

A footnote can also have multiple lines[^2].

[^1]: My reference.
[^2]: To add line breaks within a footnote, prefix new lines with 2 spaces.

This is a second line.

```python
Here is a simple footnote[^1].

A footnote can also have multiple lines[^2].

[^1]: My reference.
[^2]: To add line breaks within a footnote, prefix new lines with 2 spaces.

This is a second line.
```  
