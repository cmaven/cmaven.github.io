---
title: "Using a Simple Password on the Django Admin Page"
description: "How to disable password validation on the Django admin page so you can use a simple password during development."
excerpt: "How to disable password validation on the Django admin page so you can use a simple password."
date: 2022-12-08
last_modified_at: 2026-05-26
categories: Python
tags: [Django, Password, Admin, Development, settings]
ref: django-simple-password
---

:bulb: This post explains how to disable Django's built-in password validation during development so you can create admin users with simple passwords.
{: .notice--info}

:warning: **Never disable password validation in a production environment.** This change is intended for local development only.
{: .notice--warning}

# [01] Why Django Enforces Password Rules

Since Django 1.9, the admin interface applies password validation whenever you create a new user. This is controlled by `AUTH_PASSWORD_VALIDATORS` in `settings.py`. By default, four validators are active:

| Validator | What it checks |
|-----------|---------------|
| `UserAttributeSimilarityValidator` | Password must not resemble the username or email |
| `MinimumLengthValidator` | Password must be at least 8 characters |
| `CommonPasswordValidator` | Password must not be on a common-password list |
| `NumericPasswordValidator` | Password must not be entirely numeric |

These rules are sensible for real users. During development, however, you often need to spin up dozens of test accounts quickly, and typing `Password123!` every time is tedious.

![Django admin password validation error screen](https://user-images.githubusercontent.com/76153041/206478505-00bfcd9a-91e9-4485-8c45-b5a51f6305c1.png)

*Figure 1. Django admin rejecting a simple password — all four validators trigger at once.*

# [02] How to Disable Password Validation

Open `settings.py` and locate the `AUTH_PASSWORD_VALIDATORS` list. You have two options: **comment it out** or **replace it with an empty list**. The empty-list approach is cleaner because it is explicit and easy to reverse.

## Option A — Comment Out the Block

Wrap the entire list in a multi-line string (effectively a Python block comment):

```python
# settings.py

'''
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
'''

AUTH_PASSWORD_VALIDATORS = []
```

## Option B — Use an Environment Flag (Recommended)

A safer pattern keeps the validators in place for production and disables them only when `DEBUG` is `True`:

```python
# settings.py
import os

if DEBUG:
    AUTH_PASSWORD_VALIDATORS = []
else:
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]
```

This way you never accidentally ship a permissive configuration to production.

# [03] Verify the Change

Restart the development server after editing `settings.py`:

```shell
python manage.py runserver
```

Navigate to the Django admin at `http://127.0.0.1:8000/admin/` and create a new user. You should now be able to set any password — including short, all-numeric strings like `1234` — without triggering a validation error.

![Django admin accepting a simple password after disabling validation](https://user-images.githubusercontent.com/76153041/206478515-017fc3e2-660f-4b6e-aa93-d89b406e237a.png)

*Figure 2. Django admin now accepts a simple password with no validation errors.*

# [04] Quick Reference

| Step | Action |
|------|--------|
| 1 | Open `settings.py` |
| 2 | Set `AUTH_PASSWORD_VALIDATORS = []` (or guard with `if DEBUG`) |
| 3 | Restart with `python manage.py runserver` |
| 4 | Create an admin user with any password |
| 5 | Restore validators before deploying to production |
