---
title: "Creating a Git Remote Repository from a Local Host"
description: "How to create a remote repository from the local CLI using curl and the GitHub API"
excerpt: "How to create a remote repository from the CLI using the GitHub API and a Personal Access Token"
date: 2022-08-25
last_modified_at: 2026-05-26
categories: Git
tags: [Git, GitHub-API, curl, Remote-Repository, Token, create-remote-repository]
ref: git-remoterepo-by-local
---

:bulb: This note explains how to create a remote repository from the CLI without using the GitHub web UI.
{: .notice--info}

# [01] Prerequisites

- Use `curl` to create the remote repository via the `GitHub API`.
- To call the GitHub API remotely, a User Token must be issued from GitHub.

# [02] Issue a Token

User Profile → Settings → Developer settings → Personal access tokens

- To create a new token: click `Generate new token`.
  - For Select scopes, check the entire `repo` section.
- To regenerate an existing token: select the token name, then click `Regenerate token`.
- The generated token will be used for API calls.

Reference screenshots:

![doit_django_09](https://user-images.githubusercontent.com/76153041/186601949-d98457be-e591-4cd0-88ba-d1b5afbcdcb3.png){: width="200px" }

![doit_django_02](https://user-images.githubusercontent.com/76153041/186601994-d07dbb55-5450-443e-9862-2e62249a0a4d.png)

![doit_django_03](https://user-images.githubusercontent.com/76153041/186602003-bb8e12d7-deb6-463b-a97a-c3a348a4572f.png)

![doit_django_04](https://user-images.githubusercontent.com/76153041/186602019-ec0fa3f2-2ecb-4ee7-9fa4-9c0f6f83ce3a.png)

# [03] Using the API

:small_blue_diamond:Reference: [GitHub API — Create an organization repository](https://docs.github.com/en/rest/repos/repos#create-an-organization-repository){:target="_blank"}

## 3-1. Verify the API works

```shell
curl -i -u cmaven:${user_token} https://api.github.com/user

# example
E:\Coding\Python\doit_djngo>curl -i -u cmaven:${user_token} https://api.github.com/user
HTTP/1.1 200 OK
Server: GitHub.com
Date: Thu, 25 Aug 2022 03:01:21 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 1264
Cache-Control: private, max-age=60, s-maxage=60
Vary: Accept, Authorization, Cookie, X-GitHub-OTP
# ...
```

## 3-2. Create the remote repository

- `name` is the repository name to create.
- When `private` is set to `true`, the repository is created as private.

```shell
# Windows cmd
curl -i -u cmaven:${user_token} https://api.github.com/user/repos -d "{\"name\":\"doit_django\", \"private\":\"true\"}"

# Linux bash shell
curl -i -u cmaven:${user_token} https://api.github.com/user/repos -d '{"name":"doit_django", "private":"true"}'
```

Creation example:

![doit_django_08](https://user-images.githubusercontent.com/76153041/186613043-ed07ae08-d5e6-49b8-ad21-f3ef91d5ce19.png){: width="70%" }

Created repository view:

![doit_django_07](https://user-images.githubusercontent.com/76153041/186612457-9d0a9387-1751-4256-96c8-2cfef27c5f9d.png){: width="60%" }
