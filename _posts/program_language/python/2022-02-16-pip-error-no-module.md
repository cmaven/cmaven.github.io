---
title: "Pip Error-ERROR: No moudle named pip"
description: "pip 업그레이드 중 'No module named pip' 오류가 발생했을 때 get-pip.py로 pip를 재설치하여 해결하는 방법을 안내합니다."
excerpt: "pip 업그레이드 중 'No module named pip' 오류가 발생했을 때 get-pip.py로 pip를 재설치하여 해결하는 방법을 안내합니다."
date: 2022-02-16
last_modified_at: 2026-05-26
categories: Python
tags: [Error, Pip, Venv]
ref: pip-error-no-module
---

:bulb: pip 업그레이드 명령 실행 중 `No module named pip` 오류가 발생하면, `get-pip.py`를 다운로드해 pip를 직접 재설치하면 해결됩니다.
{: .notice--info}

---

# [01] 상황

- pip 명령어로 패키지 설치 후, `pip install --upgrdae pip`를 수행하면 `액세스가 거부되었습니다.`라는 Error 발생  
- `python -m pip install --upgrdae pip`를 수행하면, No module named pip

![01_pip 가 갑자기 안될 때  get-pip 설치](https://user-images.githubusercontent.com/76153041/154236547-701486e1-087f-49a5-ba01-889958cadbc4.png)

*그림 1. pip 업그레이드 시도 시 발생하는 `No module named pip` 오류 화면*

---

# [02] 원인

`pip install --upgrade pip` 명령어를 수행하면, 삭제 후 재설치를 하는데, 재설치에 문제가 발생하여 해당 오류를 출력한다.

업그레이드 과정에서 기존 pip가 먼저 제거된 뒤 재설치가 실패하면 pip 모듈 자체가 사라진 상태가 된다.

---

# [03] 해결방안

## pip 재설치

- get-pip.py 을 다운 받거나, [링크](https://bootstrap.pypa.io/get-pip.py)의 소스를 복사하여 직접 get-pip.py를 생성
- get-pip.py 파일의 실행

```shell
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

![02_pip 가 갑자기 안될 때  get-pip 설치](https://user-images.githubusercontent.com/76153041/154235531-dd61c88a-1c63-4e0a-a85e-a26e400d549e.png)

*그림 2. get-pip.py 실행 후 pip가 정상적으로 재설치된 화면*
