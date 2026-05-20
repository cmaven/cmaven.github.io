---
title: "GitLab Markdown LaTeX Math Rendering Limit Issue"
description: "Cause and fix for LaTeX inline math expression rendering limits in GitLab markdown"
excerpt: "Disabling math_rendering_limits_enabled in the GitLab Rails console to remove LaTeX rendering limits"
date: 2025-01-10
categories: Git
tags: [Gitlab, LaTex, Math-Rendering, Docker, gitlab-rails, rendering-limits, markdown]
ref: gitlab-limit-latex
---

:bulb: When using GitLab, this post fixes the issue where LaTeX inline math expressions (mathematical notation and formatting commands written in LaTeX syntax) in markdown files (.md) are not rendered correctly past a certain count and instead appear as raw commands.
{: .notice--info}

# [01] The LaTeX Rendering Limits Issue

## Symptom

- Using LaTeX inline math expressions to apply colors in GitLab markdown documents:
  ```markdown
  1. I only **$`\textcolor{orange}{\textsf{use}}`$** smartphone these days.
  ```

  - Past a certain count, color rendering stops working and the raw commands are printed:

  ![2025-01-10 13 46 22](https://github.com/user-attachments/assets/3959c5d2-7d30-432e-b189-6e90dc2288e8)


## Cause
- Excessive use of LaTeX inline math expressions can cause performance issues during page rendering.
- GitLab limits this by default; if needed, the limit can be removed via a setting change.
  - [Reference - GitLab Issue](https://gitlab.com/gitlab-org/gitlab/-/issues/368009){:target="_blank"}
  - [Reference - GitLab Docs](https://docs.gitlab.com/ee/administration/instance_limits.html#math-rendering-limits){:target="_blank"}


# [02] Fix (Disabling the Rendering Limit)

This is based on a GitLab instance running locally.
The environment runs inside a Docker container.

## Access the GitLab Container

```shell
docker exec -it <gitlab-container-name> /bin/bash
```

## Change the Setting (via GitLab Rails Console)

```shell
gitlab-rails console

# Console prompt
console> ApplicationSetting.update(math_rendering_limits_enabled: false)
# Verify the change
console> ApplicationSetting.current.math_rendering_limits_enabled
console> exit

# Reconfigure
gitlab-ctl reconfigure
```

- Process reference (screenshots):

  ![2025-01-09 22 04 23](https://github.com/user-attachments/assets/1bac8242-e704-4638-abb0-c28bfa9bb474)

  ![2025-01-09 22 05 03](https://github.com/user-attachments/assets/e37c1635-e211-4b7a-96b1-ee484834c72a)


## Restart the GitLab Container

```shell
docker restart <gitlab-container-name>
```


# [03] Result

- Properly rendered output (with color):

  ![2025-01-09 22 05 29](https://github.com/user-attachments/assets/b4c58e0a-63c1-4aa2-a990-8f66b2ea3fe0)
