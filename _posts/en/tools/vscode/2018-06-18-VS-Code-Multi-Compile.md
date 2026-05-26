---
title: "VS Code — Compile Multiple C/C++ Files in One Directory"
description: "How to compile all C/C++ source files in the same directory at once using VS Code tasks.json and the fileDirname/*fileExtname glob pattern."
excerpt: "Use the ${fileDirname}/*${fileExtname} variable in tasks.json to pass every source file in the active directory to g++ or gcc in a single build task."
date: 2018-06-18
last_modified_at: 2026-05-26
categories: VScode
tags: [VSCode, tasks.json, C++, gcc, g++, multi-file-compile, Variables-Reference, build-task, workspace]
ref: VS-Code-Multi-Compile
---

:bulb: This post covers how to compile multiple C/C++ source files that live in the same directory using a single VS Code build task — no Makefile required.
{: .notice--info}

**Environment**: Visual Studio Code (any recent version), `gcc` / `g++` installed and on `PATH`

---

# [01] The Problem — Single-File vs. Multi-File Compilation

By default, VS Code's C/C++ quick-build shortcuts compile only the **currently open file** (`${file}`). When a project is split across several `.cpp` or `.c` files in one directory, that produces linker errors because the other translation units are never passed to the compiler.

**Example — two-file project:**

```text
project/
├── main.cpp      ← entry point, calls helper()
└── helper.cpp    ← defines helper()
```

Compiling only `main.cpp` fails:

```text
/tmp/ccXXXX.o: undefined reference to `helper()'
collect2: error: ld returned 1 exit status
```

The fix is to pass `project/*.cpp` to the compiler — and VS Code's Variables Reference makes this easy to express without hard-coding the path.

---

# [02] Variables Reference

VS Code exposes a set of predefined variables that can be used inside `tasks.json`, `launch.json`, and `settings.json`. The two variables used in this recipe are:

| Variable | Expands to |
|---|---|
| `${fileDirname}` | Absolute path of the directory containing the currently open file |
| `${fileExtname}` | Extension of the currently open file (e.g., `.cpp`) |
| `${file}` | Absolute path of the currently open file |
| `${fileBasenameNoExtension}` | Filename without path or extension — used as the output binary name |
| `${workspaceRoot}` | Absolute path of the workspace root folder |

Combining the first two: `"${fileDirname}/*${fileExtname}"` expands to something like `/home/user/project/*.cpp` — exactly what the compiler needs.

:small_blue_diamond: Full variable list: [VS Code Variables Reference](https://code.visualstudio.com/docs/editor/variables-reference){:target="_blank"}

---

# [03] Writing tasks.json

Place `tasks.json` inside `.vscode/` at your workspace root. The file below defines three build tasks and one run task.

```json
{
    "version": "2.0.0",
    "runner": "terminal",
    "type": "shell",
    "echoCommand": true,
    "presentation": { "reveal": "always" },
    "tasks": [
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
                "fileLocation": ["relative", "${workspaceRoot}"],
                "pattern": {
                    "regexp": "^(.*):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            }
        },
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
                "fileLocation": ["relative", "${workspaceRoot}"],
                "pattern": {
                    "regexp": "^(.*):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            }
        },
        {
            "label": "save_and_compile_for_C",
            "command": "gcc",
            "args": [
                "${file}",
                "-g",
                "-o",
                "${fileDirname}/${fileBasenameNoExtension}"
            ],
            "group": "build",
            "problemMatcher": {
                "fileLocation": ["relative", "${workspaceRoot}"],
                "pattern": {
                    "regexp": "^(.*):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            }
        },
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

---

# [04] Task Breakdown

| Task label | Compiler | Input files | Use case |
|---|---|---|---|
| `save_and_compile_for_C++-groups` | `g++` | All `*.cpp` in current dir | Multi-file C++ project |
| `save_and_compile_for_C++-single` | `g++` | Current file only | Single-file C++ sketch |
| `save_and_compile_for_C` | `gcc` | Current file only | Single-file C program |
| `execute` | `cmd /C` | Compiled binary | Run the output on Windows |

**Key argument — groups task:**

```json
"${fileDirname}/*${fileExtname}"
```

This glob expands at shell evaluation time to every file matching the extension of the open file inside its directory. If you have `main.cpp` open, VS Code sends `/absolute/path/to/project/*.cpp` to `g++`.

---

# [05] Running the Build Task

1. Open any `.cpp` file in the target directory.
2. Press `Ctrl+Shift+B` (or `Cmd+Shift+B` on macOS) to open the build task picker.
3. Select **save_and_compile_for_C++-groups** to compile all files in the directory.
4. Check the Terminal panel for compiler output and errors.

:bulb: To set one task as the default build (`Ctrl+Shift+B` runs it directly without a picker), add `"group": { "kind": "build", "isDefault": true }` to that task's `group` field.
{: .notice--info}

---

# [06] Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `g++: command not found` | `g++` not on PATH | Install `build-essential` (Linux) or MinGW (Windows) |
| Glob not expanding | Shell does not support glob | Use `"type": "shell"` and wrap the arg in quotes |
| Only one file compiled | Wrong task selected | Pick the `-groups` task, not `-single` |
| Binary not found after compile | Output path mismatch | Check `${fileDirname}/${fileBasenameNoExtension}` resolves correctly in the terminal |

---

# [07] Reference

:small_blue_diamond: [VS Code Variables Reference](https://code.visualstudio.com/docs/editor/variables-reference){:target="_blank"}

:small_blue_diamond: [VS Code Tasks documentation](https://code.visualstudio.com/docs/editor/tasks){:target="_blank"}
