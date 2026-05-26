---
title: "Visual Studio Code (VS Code) — Multi-File Compilation"
description: "How to compile split C/C++ files within the same directory using Variables Reference in VS Code tasks.json"
excerpt: "Compile all files in the same directory at once using VS Code tasks.json"
date: 2018-06-18
last_modified_at: 2026-05-26
categories: VScode
tags: [VSCode, tasks.json, C++, gcc, g++, multi-file-compile, Variables-Reference]
ref: VS-Code-Multi-Compile
---

:bulb: This post covers how to compile split source files within the same directory in Visual Studio Code.
{: .notice--info}

# [01] Variables Reference

- Variables Reference that can be used inside VS Code's tasks.json
  - [VS Code Variables Reference](https://code.visualstudio.com/docs/editor/variables-reference){:target="_blank"}

# [02] Writing tasks.json

- Key idea: `"${fileDirname}/*${fileExtname}"` includes every file with the same extension in the same directory

```json
{
    "version": "2.0.0",
    "runner": "terminal",
    "type": "shell",
    "echoCommand": true,
    "presentation" : { "reveal": "always" },
    "tasks": [
          //C++ compile - groups
          {
            "label": "save_and_compile_for_C++-groups",
            "command": "g++",
            "args": [
                "${fileDirname}/*${fileExtname}",
                "-o",
                "${fileDirname}/${fileBasenameNoExtension}"
            ],
            "group": "build",
            "problemMatcher": {
                "fileLocation": [
                    "relative",
                    "${workspaceRoot}"
                ],
                "pattern": {
                    "regexp": "^(.*):(\\d+):(\\d+):\\s+(warning error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            }
        },
          //C++ compile - single
          {
            "label": "save_and_compile_for_C++-single",
            "command": "g++",
            "args": [
                "${file}",
                "-o",
                "${fileDirname}/${fileBasenameNoExtension}"
            ],
            "group": "build",
            "problemMatcher": {
                "fileLocation": [
                    "relative",
                    "${workspaceRoot}"
                ],
                "pattern": {
                    "regexp": "^(.*):(\\d+):(\\d+):\\s+(warning error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            }
        },
        //C compile
        {
            "label": "save_and_compile_for_C",
            "command": "gcc",
            "args": [
                "${file}",
                "-g -o",
                "${fileDirname}/${fileBasenameNoExtension}"
            ],
            "group": "build",
            "problemMatcher": {
                "fileLocation": [
                    "relative",
                    "${workspaceRoot}"
                ],
                "pattern": {
                    "regexp": "^(.*):(\\d+):(\\d+):\\s+(warning error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            }
        },
        // Run the binary
        {
            "label": "execute",
            "command": "cmd",
            "group": "test",
            "args": [
               "/C", "${fileDirname}\\${fileBasenameNoExtension}"
            ]
        }
    ]
}
```
