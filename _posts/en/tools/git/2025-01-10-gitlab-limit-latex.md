---
title: "GitLab Markdown LaTeX Math Rendering Limit Issue"
description: "Cause and fix for LaTeX inline math expression rendering limits in GitLab markdown — disable math_rendering_limits_enabled via the Rails console"
excerpt: "Fix GitLab's LaTeX rendering cutoff by disabling math_rendering_limits_enabled through the GitLab Rails console"
date: 2025-01-10
last_modified_at: 2026-05-26
categories: Git
tags: [Gitlab, LaTex, Math-Rendering, Docker, gitlab-rails, rendering-limits, markdown]
ref: gitlab-limit-latex
---

:bulb: GitLab enforces a default limit on LaTeX inline math expressions per page; beyond that limit, expressions render as raw text rather than formatted math or color.
{: .notice--info}

# [01] The LaTeX Rendering Limits Issue

## Symptom

When using LaTeX inline math to apply colors in GitLab markdown documents:

```markdown
1. I only **$`\textcolor{orange}{\textsf{use}}`$** smartphone these days.
```

Past a certain count of such expressions on a single page, color rendering stops and the raw LaTeX commands are printed instead:

*Figure 1. LaTeX expressions rendered as raw text past the limit*

![2025-01-10 13 46 22](https://github.com/user-attachments/assets/3959c5d2-7d30-432e-b189-6e90dc2288e8)

## Cause

Excessive LaTeX inline math expressions can cause significant CPU overhead during page rendering. GitLab protects server performance by imposing a rendering limit by default.

| Setting | Default value | Effect |
|---------|--------------|--------|
| `math_rendering_limits_enabled` | `true` | Stops rendering LaTeX after a threshold |

References:
- [GitLab Issue #368009](https://gitlab.com/gitlab-org/gitlab/-/issues/368009){:target="_blank"}
- [GitLab Docs — Math rendering limits](https://docs.gitlab.com/ee/administration/instance_limits.html#math-rendering-limits){:target="_blank"}

# [02] Fix (Disabling the Rendering Limit)

This procedure applies to a self-hosted GitLab instance running inside a Docker container.

## 2-1. Access the GitLab container

```shell
docker exec -it <gitlab-container-name> /bin/bash
```

## 2-2. Disable the limit via the GitLab Rails console

```shell
gitlab-rails console
```

Once inside the Rails console:

```shell
# Disable the rendering limit
console> ApplicationSetting.update(math_rendering_limits_enabled: false)

# Verify the change took effect
console> ApplicationSetting.current.math_rendering_limits_enabled

# Exit the console
console> exit
```

Then reconfigure GitLab:

```shell
gitlab-ctl reconfigure
```

*Figure 2. Disabling the setting in the Rails console*

![2025-01-09 22 04 23](https://github.com/user-attachments/assets/1bac8242-e704-4638-abb0-c28bfa9bb474)

*Figure 3. Verifying the setting was applied*

![2025-01-09 22 05 03](https://github.com/user-attachments/assets/e37c1635-e211-4b7a-96b1-ee484834c72a)

## 2-3. Restart the GitLab container

```shell
docker restart <gitlab-container-name>
```

> After restarting, allow 1–2 minutes for GitLab services to fully come back online before testing.

# [03] Result

After disabling the limit and restarting, all LaTeX color expressions render correctly regardless of count:

*Figure 4. LaTeX color expressions now rendered properly*

![2025-01-09 22 05 29](https://github.com/user-attachments/assets/b4c58e0a-63c1-4aa2-a990-8f66b2ea3fe0)

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Rails console command returns `false` | Setting not saved | Re-run `ApplicationSetting.update(...)` and check for errors |
| Still rendering raw text after restart | Cache not cleared | Run `gitlab-ctl reconfigure` again, then restart |
| `docker exec` fails | Container name mismatch | Run `docker ps` to confirm the container name |

# [06] Notes

If you maintain a fleet of GitLab instances, codify the `math_rendering_limits_enabled` setting in your provisioning scripts (Ansible/Terraform via the GitLab Rails console) so the override survives upgrades. After each upgrade, re-verify the setting since some patch releases reset operator preferences. For projects that need long LaTeX expressions, consider pre-rendering with MathJax or KaTeX in CI and committing the output as images.
