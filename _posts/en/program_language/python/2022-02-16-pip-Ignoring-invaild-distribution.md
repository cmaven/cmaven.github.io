---
title: "Pip WARNING — Resolving 'Ignoring invalid distribution -ip'"
description: "Explains why pip emits the 'Ignoring invalid distribution -ip' warning and how to resolve it by deleting the leftover temporary directory."
excerpt: "Explains why pip emits the 'Ignoring invalid distribution -ip' warning and how to resolve it by deleting the leftover temporary directory."
date: 2022-02-16
last_modified_at: 2026-05-26
categories: Python
tags: [Error, Pip, Venv]
ref: pip-Ignoring-invaild-distribution
---

Removing the `Ignoring invaild distribution -ip` warning when running pip
------

### Warning situation

When running `pip install selenium`, the following warning is emitted.

![python-warning, Ignoring invaild distribution -ip](https://user-images.githubusercontent.com/76153041/154229759-3a872fbd-370d-4303-bd15-e053eb2827ed.png)


### Cause

In the path shown after the message, there is a leftover directory whose name starts with `-ip` that should not be there.
The directory was created temporarily and either was not cleaned up or was assigned an invalid name.

![python-warning, Ignoring invaild distribution -ip directory check](https://user-images.githubusercontent.com/76153041/154229906-59930097-fce2-42a9-9c88-acb1fca67dab.png)

### Solution

Manually delete the directory whose name starts with `-ip`.

![python-warning, Ignoring invaild distribution -ip directory deleted](https://user-images.githubusercontent.com/76153041/154229784-99ba096e-8645-45e5-96e6-fe45bcccd276.png)

** Once the directory is deleted, the WARNING disappears. **

![python-warning, Ignoring invaild distribution -ip WARNING resolved after deletion](https://user-images.githubusercontent.com/76153041/154229799-47af874e-e7a2-4d7e-8d1f-82affd7dc51e.png)
