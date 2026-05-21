---
title: "VSCode — Auto-Insert Repeated Code with Snippets"
description: "How to configure VSCode Snippets to auto-insert repeated code with a single shortcut"
excerpt: "Configure VSCode snippets to expand repeated code via prefix + Tab"
date: 2025-01-07
categories: VScode
tags: [VSCode, Snippets, auto-completion, Markdown, Emmet, Tab-Completion, productivity]
ref: repetive-code-snippets
---

:bulb: When using VSCode, I wanted repeated code to be auto-inserted via `a specific prefix` + the `Tab` key.  
This post walks through VSCode's snippets feature and how to apply it.
{: .notice--info}  

# [01] Example of Repeated Code  

- In Markdown documents (writing a Readme.md for GitLab/GitHub), I sometimes need to apply color and bold to a specific string.

```shell
# red is the desired color
# apple is the desired text

# Color only
$`\textcolor{red}{\textsf{apple}}`$

# Color + bold
**$`\textcolor{red}{\textsf{apple}}`$**
```

# [02] How to Apply

## Configure the Tab Key  
- In VSCode, press `Ctrl + Shift + P`
- Search `>preferences: Open ... settings.json`

  ![2025-01-07 23 27 07](https://github.com/user-attachments/assets/9a687de5-acb4-480f-a730-f3c0c8111157)    

- Check Emmet and Tab Completion settings
  - `Emmet`: a tool primarily used for HTML/CSS where typing a short abbreviation expands into a longer pre-defined string

    ```json
    "editor.tabCompletion": "on",
    "emmet.includeLanguages": {
      "markdown": "html"
    }
    ```  

## Define the Snippet
- In VSCode, press `Ctrl + Shift + P`
- Search `Snippets: Configure Snippets`
- Select  
  ![2025-01-07 23 14 21](https://github.com/user-attachments/assets/45924839-af30-4d05-9d1b-94ec1fa4eafb)    

  - If `markdown.json` exists, edit it
  - If `markdown.json` does not exist, choose `New Global Snippets file..` or `New Global Snippets file for 'xxx'`
    - If you want the snippet to apply to a Remote VSCode session, create it via `New Global Snippets file for 'xxx'`.

      ![2025-01-08 00 02 13](https://github.com/user-attachments/assets/e574a715-6b3e-431e-9615-75c35ba51119)  

- Edit the json file
  - Type the string set in `prefix`, then press Tab to trigger auto-completion.
  - In `body`, write the repeated text. Use `$1` for places where user input is needed.
    - Note: in JSON, to make `\textcolor` recognized, you must escape it as `\\textcolor`.

      ```json
      {
      	// Place your snippets for markdown here. 
      	// Each snippet is defined under a snippet name and has a prefix, body and 
      	// description. The prefix is what is used to trigger the snippet 
      	// and the body will be expanded and inserted. Possible variables are:
      	// $1, $2 for tab stops, $0 for the final cursor position, 
      	// and ${1:label}, ${2:another} for placeholders. Placeholders with the 
      	// same ids are connected.
      	// Example:
      	// "Print to console": {
      	// 	"prefix": "log",
      	// 	"body": [
      	// 		"console.log('$1');",
      	// 		"$2"
      	// 	],
      	// 	"description": "Log output to console"
      	// }
      
        // Add the snippet below
      	"Color Bold Text": {
      		"prefix": "cb",
      		"body": "**$`\\textcolor{red}{\\textsf{$1}}`$**",
      		"description": "Insert bold text with orange color"
      	}	
      }
      ```  

## Restart or Reload Window

- In VSCode, press `Ctrl + Shift + P`
- Search `Reload Windows` and run it

# [03] Example

- In a Markdown file, type `cb` and press `Tab` — the configured content is inserted automatically.

  ![2025-01-08 00 03 23](https://github.com/user-attachments/assets/1992d9d7-733b-4a4e-a1c5-517ed422aae2)  

  ![2025-01-08 00 03 41](https://github.com/user-attachments/assets/74cdf751-c647-4cfc-8edb-8eacdf599936)  
