---
title: "Pip Error — ERROR: No module named pip"
description: "How to recover when 'No module named pip' appears during a pip upgrade — reinstall pip using get-pip.py."
excerpt: "How to recover when 'No module named pip' appears during a pip upgrade — reinstall pip using get-pip.py."
date: 2022-02-16
last_modified_at: 2026-05-26
categories: Python
tags: [Error, Pip, Venv]
ref: pip-error-no-module
---

When pip suddenly stops working
------

### Situation

- After installing packages with pip, running `pip install --upgrdae pip` raises an `Access is denied.` error.
- Running `python -m pip install --upgrdae pip` raises `No module named pip`.


![01_get-pip install when pip suddenly stops working](https://user-images.githubusercontent.com/76153041/154236547-701486e1-087f-49a5-ba01-889958cadbc4.png)


### Cause
`pip install --upgrade pip` uninstalls the existing pip and reinstalls it. If the reinstall step fails, the error above is printed.

### Solution

#### Reinstall pip
- Download `get-pip.py`, or copy the source from this [link](https://bootstrap.pypa.io/get-pip.py) and create `get-pip.py` manually.
- Run the `get-pip.py` file.

``` shell
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

![02_get-pip install when pip suddenly stops working](https://user-images.githubusercontent.com/76153041/154235531-dd61c88a-1c63-4e0a-a85e-a26e400d549e.png)
