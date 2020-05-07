---
layout: post
title: "Visual Studio Code(vs code) 파일 분할 컴파일"
date: 2018-06-18 12:00
categories: Utilities
tags: C++
---

Visual Studio Code 에서 동일 디렉토리 내의 분할된 파일 컴파일에 대해 정리한다.

------

1. Visual Studio Code 의 tasks.json 내부에 작성 가능한 Varialbes Reference

   - https://code.visualstudio.com/docs/editor/variables-reference

2. tasks.json 작성

   - 핵심 

     - ```json
       "${fileDirname}/*${fileExtname}"
       ```

```json
{
    // See https://go.microsoft.com/fwlink/?LinkId=733558
    // for the documentation about the tasks.json format
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

            //컴파일시 에러를 편집기에 반영
            //참고:   https://code.visualstudio.com/docs/editor/tasks#_defining-a-problem-matcher

            "problemMatcher": {
                "fileLocation": [
                    "relative",
                    "${workspaceRoot}"
                ],
                "pattern": {
                    // The regular expression. 
                   //Example to match: helloWorld.c:5:3: warning: implicit declaration of function 'prinft'
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

            //컴파일시 에러를 편집기에 반영
            //참고:   https://code.visualstudio.com/docs/editor/tasks#_defining-a-problem-matcher

            "problemMatcher": {
                "fileLocation": [
                    "relative",
                    "${workspaceRoot}"
                ],
                "pattern": {
                    // The regular expression. 
                   //Example to match: helloWorld.c:5:3: warning: implicit declaration of function 'prinft'
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

            //컴파일시 에러를 편집기에 반영
            //참고:   https://code.visualstudio.com/docs/editor/tasks#_defining-a-problem-matcher

            "problemMatcher": {
                "fileLocation": [
                    "relative",
                    "${workspaceRoot}"
                ],
                "pattern": {
                    // The regular expression. 
                   //Example to match: helloWorld.c:5:3: warning: implicit declaration of function 'prinft'
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

