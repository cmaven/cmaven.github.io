---
title: "Visual Studio Code(VS Code) 파일 분할 컴파일"
description: "VS Code tasks.json에서 Variables Reference를 활용하여 동일 디렉토리 내 분할된 C/C++ 파일을 컴파일하는 방법"
excerpt: "VS Code tasks.json으로 같은 디렉토리의 분할 파일을 한 번에 컴파일하기"
date: 2018-06-18
categories: VScode
tags: [VSCode, tasks.json, C++, gcc, g++, 분할컴파일, Variables-Reference]
---

:bulb: Visual Studio Code에서 동일 디렉토리 내의 분할된 파일 컴파일에 대해 정리한다.
{: .notice--info}

# [01] Variables Reference

- VS Code의 tasks.json 내부에 작성 가능한 Variables Reference
  - [VS Code Variables Reference](https://code.visualstudio.com/docs/editor/variables-reference){:target="_blank"}

# [02] tasks.json 작성

- 핵심: `"${fileDirname}/*${fileExtname}"`으로 동일 디렉토리의 같은 확장자 파일을 모두 포함

```json
{
    "version": "2.0.0",
    "runner": "terminal",
    "type": "shell",
    "echoCommand": true,
    "presentation" : { "reveal": "always" },
    "tasks": [
          //C++ 컴파일 - groups
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
          //C++ 컴파일 - single
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
        //C 컴파일
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
        // 바이너리 실행
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
