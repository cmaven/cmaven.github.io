---
title: "Pip Error-ERROR: No moudle named pip"
date: 2022-02-16
categories: Python
tags: [Error, Pip, Venv]
---

Pip 명령어 실행이 갑자기 동작하지 않을 때
------

### 상황

- pip 명령어로 패키지 설치 후, `pip install --upgrdae pip`를 수행하면 `액세스가 거부되었습니다.`라는 Error 발생  
- `python -m pip install --upgrdae pip`를 수행하면, No module named pip


![01_pip 가 갑자기 안될 때  get-pip 설치](https://user-images.githubusercontent.com/76153041/154236547-701486e1-087f-49a5-ba01-889958cadbc4.png)


### 원인
`pip install --upgrade pip` 명령어를 수행하면, 삭제 후 재설치를 하는데, 재설치에 문제가 발생하여 해당 오류를 출력한다.

### 해결방안

#### pip 재설치
- get-pip.py 을 다운 받거나, [링크](https://bootstrap.pypa.io/get-pip.py)의 소스를 복사하여 직접 get-pip.py를 생성
- get-pip.py 파일의 실행

``` shell
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

![02_pip 가 갑자기 안될 때  get-pip 설치](https://user-images.githubusercontent.com/76153041/154235531-dd61c88a-1c63-4e0a-a85e-a26e400d549e.png)



