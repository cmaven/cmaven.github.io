---
title: "Creating a Git Remote Repository from a Local Host"
description: "How to create a GitHub remote repository from the CLI using curl and the GitHub REST API with a Personal Access Token"
excerpt: "Create a GitHub remote repo from the terminal using curl, the GitHub API, and a Personal Access Token — no web UI needed"
date: 2022-08-25
last_modified_at: 2026-05-26
categories: Git
tags: [Git, GitHub-API, curl, Remote-Repository, Token, create-remote-repository]
ref: git-remoterepo-by-local
---

:bulb: You can create a GitHub remote repository entirely from the command line using `curl` and the GitHub REST API — no browser required.
{: .notice--info}

# [01] Prerequisites

To create a remote repository via the CLI, you need:

- `curl` installed on your system
- A GitHub **Personal Access Token** (PAT) with `repo` scope
- Your GitHub username

The GitHub REST API endpoint used is:

```text
POST https://api.github.com/user/repos
```

# [02] Issue a Personal Access Token

Navigate to: **User Profile → Settings → Developer settings → Personal access tokens**

Steps to generate a new token:

1. Click **Generate new token**.
2. Under **Select scopes**, check the entire **`repo`** section.
3. Click **Generate token** and copy the value — it is shown only once.

To regenerate an existing token: select the token name, then click **Regenerate token**.

*Figure 1. Navigate to Developer Settings*

![doit_django_09](https://user-images.githubusercontent.com/76153041/186601949-d98457be-e591-4cd0-88ba-d1b5afbcdcb3.png){: width="200px" }

*Figure 2. Personal access tokens list*

![doit_django_02](https://user-images.githubusercontent.com/76153041/186601994-d07dbb55-5450-443e-9862-2e62249a0a4d.png)

*Figure 3. Select repo scope when generating token*

![doit_django_03](https://user-images.githubusercontent.com/76153041/186602003-bb8e12d7-deb6-463b-a97a-c3a348a4572f.png)

*Figure 4. Copy the generated token*

![doit_django_04](https://user-images.githubusercontent.com/76153041/186602019-ec0fa3f2-2ecb-4ee7-9fa4-9c0f6f83ce3a.png)

# [03] Using the API

Reference: [GitHub API — Create a repository for the authenticated user](https://docs.github.com/en/rest/repos/repos#create-a-repository-for-the-authenticated-user){:target="_blank"}

## 3-1. Verify the API connection

Before creating a repo, confirm your token is valid by fetching your user info:

```shell
curl -i -u cmaven:${user_token} https://api.github.com/user
```

Expected response (truncated):

```text
HTTP/1.1 200 OK
Server: GitHub.com
Date: Thu, 25 Aug 2022 03:01:21 GMT
Content-Type: application/json; charset=utf-8
...
```

A `200 OK` response confirms the token works. A `401 Unauthorized` means the token is invalid or expired.

## 3-2. Create the remote repository

Send a `POST` request with the repository name and visibility:

```shell
# Windows cmd
curl -i -u cmaven:${user_token} https://api.github.com/user/repos -d "{\"name\":\"doit_django\", \"private\":\"true\"}"

# Linux / macOS bash
curl -i -u cmaven:${user_token} https://api.github.com/user/repos -d '{"name":"doit_django", "private":"true"}'
```

| Field | Description |
|-------|-------------|
| `name` | Repository name to create |
| `private` | `true` = private repo, `false` = public repo |

*Figure 5. Successful creation response*

![doit_django_08](https://user-images.githubusercontent.com/76153041/186613043-ed07ae08-d5e6-49b8-ad21-f3ef91d5ce19.png){: width="70%" }

*Figure 6. New repository visible on GitHub*

![doit_django_07](https://user-images.githubusercontent.com/76153041/186612457-9d0a9387-1751-4256-96c8-2cfef27c5f9d.png){: width="60%" }

## 3-3. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `401 Unauthorized` | Token invalid or expired | Regenerate the PAT and retry |
| `422 Unprocessable Entity` | Repository name already exists | Choose a different `name` value |
| `curl: command not found` | curl not installed | Install via `apt install curl` or `choco install curl` |

> Note: GitHub deprecated password-based authentication for API calls. Always use a PAT or OAuth token.
