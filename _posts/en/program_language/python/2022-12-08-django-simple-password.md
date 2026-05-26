---
title: "Using a Simple Password on the Django Admin Page"
description: "How to disable password validation on the Django admin page so you can use a simple password."
excerpt: "How to disable password validation on the Django admin page so you can use a simple password."
date: 2022-12-08
last_modified_at: 2026-05-26
categories: Python
tags: [Django, Password]
ref: django-simple-password
---

Disable password validation on the Django admin page

------

When developing with Django, you sometimes need to create a new user from the admin page.
Since Django 1.9, creating a new user from the admin page goes through password validation:

- Cannot be too similar to personal information
- Must be at least 8 characters
- Cannot be a common password
- Cannot be entirely numeric

![2022-12-08 23 42 27](https://user-images.githubusercontent.com/76153041/206478505-00bfcd9a-91e9-4485-8c45-b5a51f6305c1.png)

When you need to test and iterate quickly, this is very inconvenient, so we want to disable the feature.

> Using simple passwords in Django

- settings.py
  - Comment out the entire `AUTH_PASSWORD_VALIDATORS` block
  - Assign an empty list

  ```python
  # ...
  
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
  
  # ...
  ```  

Restart the project (`python manage.py runserver`) and you can confirm that validation is disabled.

![2022-12-08 23 41 57](https://user-images.githubusercontent.com/76153041/206478515-017fc3e2-660f-4b6e-aa93-d89b406e237a.png)  

