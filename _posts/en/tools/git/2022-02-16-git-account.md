---
title: "Changing Git Account (User) in a Local Shell Environment"
description: "How to view and change the Git user name and email in a local environment using the git config command"
excerpt: "How to change your Git account (user.name, user.email) with git config --global"
date: 2022-02-16
categories: Git
tags: [Git, git-config, User, account-switch, user.name, user.email]
ref: git-account
---

:bulb: When you use two Git accounts on a single system and need to work against a remote repository as a specific account.
{: .notice--info}

# [01]  Check Current Settings

Check all settings.

``` shell
git config -l
```
- Sample output  
![git-config check-01](https://user-images.githubusercontent.com/76153041/154203932-08c2ccee-1154-47e5-9de2-c4a89ed00e18.png)


Check specific settings (user name, user email).
``` shell
git config user.name
git config user.email
```
- Sample output  
![git-config check-02](https://user-images.githubusercontent.com/76153041/154203935-2d0f7c70-01ff-46df-b9df-a7a8a2c06080.png)

# [02]  Change Settings

Change the user account and email.

``` shell
git config --global user.name $(username)
git config --global user.email $(useremail)
```

- Sample output  
![git-config update](https://user-images.githubusercontent.com/76153041/154203940-6bce8ce9-827d-449a-9b02-7c781b3ce793.png)
