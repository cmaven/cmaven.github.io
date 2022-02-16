---
title: "Pip Error-WARNING: Ignoring invaild distribution -ip"
date: 2022-02-16
categories: Python
tags: [Error, Pip, Venv]
---

Pip 명령어 실행 시, `Ignoring invaild distribution -ip` 경고문 없애기
------

### Warning 상황

pip install selenium 실행 시, 아래와 같은 Warning 발생  

![python-warning, Ignoring invaild distribution -ip](https://user-images.githubusercontent.com/76153041/154229759-3a872fbd-370d-4303-bd15-e053eb2827ed.png)  


### 원인

뒤에 명시된 경로에, `-ip` 로 시작되는 필요 없는 디렉토리가 존재함  
해당 디렉토리는 임시로 생성된 후, 아직 삭제하지 않았거나 잘못된 이름이 배정되어 있는 상태

![python-warning, Ignoring invaild distribution -ip 을 표시한 디렉토리 확인](https://user-images.githubusercontent.com/76153041/154229906-59930097-fce2-42a9-9c88-acb1fca67dab.png)  

### 해결방안

`-ip`로 시작하는 디렉토리를 직접 삭제

![python-warning, Ignoring invaild distribution -ip 을 표시한 디렉토리 삭제](https://user-images.githubusercontent.com/76153041/154229784-99ba096e-8645-45e5-96e6-fe45bcccd276.png)  

** 해당 디렉토리를 삭제하면, WARNING이 사라짐 **

![python-warning, Ignoring invaild distribution -ip 을 표시한 디렉토리 삭제 후 WARNING 해결됨](https://user-images.githubusercontent.com/76153041/154229799-47af874e-e7a2-4d7e-8d1f-82affd7dc51e.png)



