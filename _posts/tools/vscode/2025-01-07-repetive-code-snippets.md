---
title: "반복적인 구문 입력을 간편하게(repetive code-snippets)"
date: 2025-01-07
categories: VScode
tags: [Repetive_code, Snippets]
---

:bulb: VSCode 사용 시, 반복적인 구문을 `특정 구문` + `Tap` 키로 자동 입력되게 설정하려 한다.  
VSCode 에서 제공하는 snippets 기능을 살펴보고, 이를 적용해 본다.
{: .notice--info}  

# [01] 반복구문 예  

- Markdown 형식의 문서(Gitlab, Github의 Readme.md 작성 중)에서, 특정 문자열에 색상 및 굵게(Bold)처리 필요

```shell
# red 에 원하는 색상
# apple 에 원하는 문자열

# 색상만 적용
$`\textcolor{red}{\textsf{apple}}`$

# 색상+굵게 적용
**$`\textcolor{red}{\textsf{apple}}`$**
```

# [02] 적용방법

## Tab 키 지정  
- VSCode에서 `Ctrl + Shift + P`
- 검색 `>preferences: Open ... settings.json`

  ![2025-01-07 23 27 07](https://github.com/user-attachments/assets/9a687de5-acb4-480f-a730-f3c0c8111157)    

- Emmet와 Tab Completion 설정 확인
  - `Emmet`: HTML/CSS에서 주로 쓰이는 도구로, 간단한 약어를 입력하면 지정된 문자열이 입력되는 것

    ```json
    "editor.tabCompletion": "on",
    "emmet.includeLanguages": {
      "markdown": "html"
    }
    ```  

## 반복구문 지정
- VSCode에서 `Ctrl + Shift + P`
- 검색 `Snippets: Configure Snippets`
- 선택  
  ![2025-01-07 23 14 21](https://github.com/user-attachments/assets/45924839-af30-4d05-9d1b-94ec1fa4eafb)    

  - `markdown.json` 있다면, 이를 수정
  - `markdown.json` 이 없다면, `New Global Snippets file..` 또는 `New Global Snippets file for 'xxx'`
    - 이 때, Remote에서 실행하는 VSCode에 적용하고 싶다면, `New Global Snippets file for 'xxx'`으로 신규 생성해야 한다.

      ![2025-01-08 00 02 13](https://github.com/user-attachments/assets/e574a715-6b3e-431e-9615-75c35ba51119)  

- json 파일 수정
  - `prefix`에 작성한 문자열을 입력 후, Tab 키를 눌러 자동완성 시킨다.
  - `body`에 입력할 반복문을 작성한다. 이 때, 사용자 입력이 필요한 부분을 `$1`로 입력
    - 이 때, json에서 `\textcolor`를 인식할 수 있도록, `\\textcolor` 입력 주의

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
      
        // 아래 내용 입력
      	"Color Bold Text": {
      		"prefix": "cb",
      		"body": "**$`\\textcolor{red}{\\textsf{$1}}`$**",
      		"description": "Insert bold text with orange color"
      	}	
      }
      ```  

## 재시작 또는 Reload Windows

- VSCode에서 `Ctrl + Shift + P`
- 검색 `Reload Windows` 후, 실행

# [03] 적용 예

- markdown 파일에서 `cb` 입력 후, `Tab` 키를 누르면, 지정했던 내용이 자동으로 입력되는 것을 확인할 수 있다.

  ![2025-01-08 00 03 23](https://github.com/user-attachments/assets/1992d9d7-733b-4a4e-a1c5-517ed422aae2)  

  ![2025-01-08 00 03 41](https://github.com/user-attachments/assets/74cdf751-c647-4cfc-8edb-8eacdf599936)  
