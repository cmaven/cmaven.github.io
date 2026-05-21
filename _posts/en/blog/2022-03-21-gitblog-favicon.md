---
title: "Creating and Applying a Favicon to Your GitHub Blog"
description: "Guide to generating a favicon and applying it to a GitHub blog running the Minimal Mistakes Jekyll theme"
excerpt: "Generate a favicon with favicon-generator and apply it to a Jekyll blog"
date: 2022-03-21
categories: Github_Blog
tags: [Favicon, Jekyll, Minimal-Mistakes, blog-setup]
ref: gitblog-favicon
---


:bulb: This post walks through generating and applying a favicon to a GitHub blog.
{: .notice--info}

# [01]  What is a Favicon?

> A portmanteau of "Favorites + Icon" — the small icon shown in a browser's address bar and tabs that represents the site.

We will replace the small icon shown on the left of the browser tab below.

![favicon not yet configured](https://user-images.githubusercontent.com/76153041/159212163-a60549fa-e776-454a-bb03-a1c9d7de688b.png)

# [02]  Prepare the Image and Generate the Favicon

- Source image

  A square image works best.

  ![image for favicon](https://user-images.githubusercontent.com/76153041/159210308-0e238928-1658-4216-bfcd-aa0df9f463cb.png){: width="20%" height="20%"}


- Generate the favicon

  [(link) favicon-generator](https://www.favicon-generator.org/){:target="_blank"}


  Upload the image (File Selection) and click **Create Favicon**.

  ![favicon-generator](https://user-images.githubusercontent.com/76153041/159210975-16270ef4-88b8-47d6-8a3b-41426ad20374.png)

  Download the generated files (Download the generated favicon).
  Copy the HTML document snippet separately — you'll paste it into the blog configuration later.


  ![favicon-generator-02](https://user-images.githubusercontent.com/76153041/159210983-4ea54f53-5f99-437a-a0fd-de3664433f08.png)

  Rename the downloaded file (optional).
  Keep the `.ico` extension.
  e.g. rename `ed00c6...` to `favicon.ico`.

  ![creating the favicon file](https://user-images.githubusercontent.com/76153041/159211993-91ae9936-55da-40ce-8a29-f9c973a00f67.png)

# [03]  Apply the Favicon to the Blog

- Unzip the downloaded archive and copy the files into the blog's `/assets/` folder.

  ![uploading the favicon-ico folder](https://user-images.githubusercontent.com/76153041/159212363-25f845a9-0804-4a28-b939-040b5aab36df.png)

- Paste the HTML document snippet from the favicon generator into `_includes/head/custom/html`.

  Minimal Mistakes theme.
  Update the `href` attribute in each tag to point to the file you uploaded (`/assets/favicon.ico/`).

  ![setting favicon.ico in _includes/head/custom.html](https://user-images.githubusercontent.com/76153041/159212365-3d2f69cd-28dc-4d6e-84c3-7e0910994404.png)


# [04]  Result
![favicon applied](https://user-images.githubusercontent.com/76153041/159212719-0bfccb72-1cca-4d16-ae90-491a39c4d55e.png)
