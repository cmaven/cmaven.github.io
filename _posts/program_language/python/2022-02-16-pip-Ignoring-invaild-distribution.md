---
title: "Pip WARNING — Ignoring invalid distribution -ip 해결"
description: "pip 실행 시 'Ignoring invalid distribution -ip' 경고가 발생하는 원인과 임시 디렉토리 삭제로 해결하는 방법을 설명합니다."
excerpt: "pip 실행 시 'Ignoring invalid distribution -ip' 경고가 발생하는 원인과 임시 디렉토리 삭제로 해결하는 방법을 설명합니다."
date: 2022-02-16
last_modified_at: 2026-05-26
categories: Python
tags: [Error, Pip, Venv]
ref: pip-Ignoring-invaild-distribution
---

:bulb: pip 명령어 실행 시 나타나는 `Ignoring invalid distribution -ip` 경고는 임시 디렉토리가 삭제되지 않고 남아 있어서 발생하며, 해당 디렉토리를 직접 삭제하면 해결됩니다.
{: .notice--info}

---

# [01] Warning 상황

pip install selenium 실행 시, 아래와 같은 Warning 발생  

![python-warning, Ignoring invaild distribution -ip](https://user-images.githubusercontent.com/76153041/154229759-3a872fbd-370d-4303-bd15-e053eb2827ed.png)

*그림 1. pip install 실행 시 나타나는 Ignoring invalid distribution -ip 경고 화면*

---

# [02] 원인

뒤에 명시된 경로에, `-ip` 로 시작되는 필요 없는 디렉토리가 존재함  
해당 디렉토리는 임시로 생성된 후, 아직 삭제하지 않았거나 잘못된 이름이 배정되어 있는 상태

![python-warning, Ignoring invaild distribution -ip 을 표시한 디렉토리 확인](https://user-images.githubusercontent.com/76153041/154229906-59930097-fce2-42a9-9c88-acb1fca67dab.png)

*그림 2. 경고 메시지에 명시된 경로에서 `-ip`로 시작하는 임시 디렉토리 확인*

경고 메시지에 포함된 경로를 탐색기나 터미널에서 직접 열어 해당 디렉토리를 확인한다.

---

# [03] 해결방안

`-ip`로 시작하는 디렉토리를 직접 삭제

![python-warning, Ignoring invaild distribution -ip 을 표시한 디렉토리 삭제](https://user-images.githubusercontent.com/76153041/154229784-99ba096e-8645-45e5-96e6-fe45bcccd276.png)

*그림 3. 해당 임시 디렉토리를 선택하여 삭제*

** 해당 디렉토리를 삭제하면, WARNING이 사라짐 **

![python-warning, Ignoring invaild distribution -ip 을 표시한 디렉토리 삭제 후 WARNING 해결됨](https://user-images.githubusercontent.com/76153041/154229799-47af874e-e7a2-4d7e-8d1f-82affd7dc51e.png)

*그림 4. 디렉토리 삭제 후 pip install 재실행 시 경고가 사라진 화면*
