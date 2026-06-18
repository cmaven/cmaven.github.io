<!-- 2026-06-11-linux-serial-terminal-programs.md: 리눅스 시리얼 터미널 프로그램 개요·설치·사용·비교·삭제 | 생성일: 2026-06-11 -->
---
title: "리눅스 시리얼 터미널 프로그램 총정리 — screen·minicom·picocom·tio 설치/사용/비교"
description: "Ubuntu에서 네트워크 장비·임베디드 콘솔에 접속하는 시리얼 터미널 프로그램(screen, minicom, picocom, tio, cu)의 개요·설치·시작/종료·장단점 비교·삭제를 한 번에 정리"
excerpt: "USB-시리얼 콘솔 케이블로 장비에 붙을 때 쓰는 screen·minicom·picocom·tio를 설치부터 종료 단축키, 장단점, 깔끔한 삭제까지 비교 정리"
date: 2026-06-11
categories: Etc
tags: [시리얼, serial, console, screen, minicom, picocom, tio, cu, Ubuntu, Linux, ttyUSB, 콘솔케이블, 네트워크장비]
ref: linux-serial-terminal-programs
---

:bulb: 네트워크 장비(스위치·라우터)나 임베디드 보드의 **콘솔 포트**에 USB-시리얼 케이블로 접속할 때 쓰는 리눅스 시리얼 터미널 프로그램들을 개요·설치·사용(시작/종료)·장단점·삭제까지 한 번에 정리한다.
{: .notice--info}

**환경**: Ubuntu 22.04+ / USB-to-Serial 콘솔 케이블(FTDI·PL2303 등)

---

# [01] 개요 — 시리얼 터미널이란

네트워크 장비의 **Console 포트**는 IP가 없어도 직접 CLI에 접근할 수 있는 통로다. USB-시리얼 케이블로 PC에 연결하면 리눅스에서 보통 다음 장치로 잡힌다.

- `/dev/ttyUSB0` — FTDI, PL2303 등 USB-Serial 변환 칩
- `/dev/ttyACM0` — CDC-ACM 계열(일부 보드 내장 USB)

이 장치를 열어 **baud rate**(예: 9600) 등 시리얼 파라미터로 통신하는 프로그램이 "시리얼 터미널"이다. 대표적으로 `screen`, `minicom`, `picocom`, `tio`가 있다.

:warning: 일반 사용자는 시리얼 포트 접근 권한이 없어 `Permission denied`가 날 수 있다. 사용자를 `dialout` 그룹에 추가하면 sudo 없이 접속할 수 있다(재로그인 필요).
{: .notice--warning}

```bash
# 장치 확인
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
dmesg | grep -iE 'ttyUSB|ttyACM' | tail   # 케이블 꽂는 순간의 장치명 확인
lsusb                                       # 시리얼 칩(FTDI/Prolific) 확인

# 권한 부여(한 번만, 이후 로그아웃→로그인)
sudo usermod -aG dialout $USER
```

> 이하 예시는 모두 **9600 8N1, 흐름제어 없음**(Arista 등 네트워크 장비 기본값) 기준이다. 장비에 맞게 baud만 바꾸면 된다.

---

# [02] screen

가장 널리 깔려 있어 "일단 붙고 보자"에 좋은 만능 도구. 시리얼 전용은 아니지만 시리얼도 지원한다.

```bash
# 설치
sudo apt update && sudo apt install -y screen

# 시작: screen <장치> <baud>
screen /dev/ttyUSB0 9600
```

- **시작 후**: 화면이 비면 `Enter`로 프롬프트를 깨운다.
- **종료**: `Ctrl + a` 뒤 `k` → `y` (세션 강제 종료).
- **분리(백그라운드 유지)**: `Ctrl + a` 뒤 `d`, 재접속 `screen -r`.

---

# [03] minicom

시리얼 전용 프로그램. 메뉴로 설정을 저장하고 **파일 전송(X/Y/Zmodem)**·로그 기능을 제공한다.

```bash
# 설치
sudo apt install -y minicom

# 시작: 장치/baud 직접 지정
sudo minicom -D /dev/ttyUSB0 -b 9600

# 설정 메뉴(저장형)
sudo minicom -s
```

- `Serial port setup`에서 **Serial Device**(`/dev/ttyUSB0`), **Bps/Par/Bits**(`9600 8N1`), **Hardware/Software Flow Control**(`No`) 설정 → `Save setup as dfl`.
- **종료**: `Ctrl + a` 뒤 `x` → `Yes`.

---

# [04] picocom

이름처럼 가볍고 명령행 옵션이 명확해 **스크립트·자동화**에 적합하다. UI 기능은 거의 없다.

```bash
# 설치
sudo apt install -y picocom

# 시작
picocom -b 9600 /dev/ttyUSB0
```

- **종료**: `Ctrl + a` 뒤 `Ctrl + x`.
- 다른 단축키도 모두 `Ctrl + a` 접두키를 사용한다.

---

# [05] tio (추천)

현대적인 시리얼 터미널. 명령행이 깔끔하고 **장치가 빠졌다 다시 꽂히면 자동 재연결**되어 장비 콘솔을 자주 붙일 때 가장 편하다.

```bash
# 설치 (Ubuntu 22.04+ 기본 저장소)
sudo apt install -y tio

# 시작: tio 기본 baud는 115200이므로 9600 명시
tio -b 9600 /dev/ttyUSB0
```

- **종료**: `Ctrl + t` 뒤 `q` (모든 단축키 접두키는 `Ctrl + t`).
- **단축키 목록**: `Ctrl + t` 뒤 `?`.
- **프로필 저장**: `~/.config/tio/config`에 등록하면 이름으로 바로 접속.

```ini
# ~/.config/tio/config — "tio arista"로 접속
[arista]
device = /dev/ttyUSB0
baudrate = 9600
```

---

# [06] (참고) cu / putty

- **cu** : `sudo apt install -y cu` → `cu -l /dev/ttyUSB0 -s 9600`, 종료 `~.`. UUCP 계열의 오래된 도구로 간단한 용도에 쓰인다.
- **putty** : 리눅스에도 GUI/CLI 버전이 있다. `putty -serial /dev/ttyUSB0 -sercfg 9600`. 다만 콘솔 환경에서는 위 도구들이 더 편하다.

---

# [07] 장단점 비교

| 프로그램 | 장점 | 단점 | 추천 상황 |
|----------|------|------|-----------|
| **screen** | 거의 어디나 설치, 사용 단순 | 시리얼 전용 기능 부족, 종료 키 헷갈림, 로그 저장 불편 | 즉석·남의 서버에서 빠르게 콘솔 접속 |
| **minicom** | 시리얼 전용, 설정 저장, 로그·파일전송 | 초기 설정 UI가 번거로움 | 파일 전송 등 기능이 필요할 때 |
| **picocom** | 가볍고 옵션 명확, 자동화에 좋음 | UI 기능 거의 없음 | 스크립트로 깔끔하게 콘솔 볼 때 |
| **tio** | 현대적, 자동 재연결, 프로필 저장 | 기본 미설치인 경우 있음 | **내 장비 콘솔을 자주 붙일 때(개인 추천)** |
| **putty** | GUI에 익숙함 | 서버 CLI에서는 불편 | Ubuntu Desktop에서 GUI 접속 |

## 추천 순서

내 PC에서 네트워크 장비 콘솔을 붙인다면: **tio → picocom → screen → minicom** 순으로 추천한다.

- **내 장비/자주 사용** → `tio` (자동 재연결·프로필이 결정적)
- **즉석·현장·남의 서버(설치 권한 애매)** → `screen` (어디에나 이미 있음)
- **파일 전송이 필요** → `minicom`

> 요약: *"내 환경이면 tio, 즉석이면 screen"* 두 축으로 기억하면 충분하다.

---

# [08] 삭제

```bash
# 개별 삭제
sudo apt remove -y screen
sudo apt remove -y minicom
sudo apt remove -y picocom
sudo apt remove -y tio

# 설정 파일까지 완전 제거(purge)
sudo apt purge -y minicom

# 의존성 정리
sudo apt autoremove -y
```

- `remove`는 패키지만, `purge`는 `/etc`의 설정 파일까지 제거한다.
- 사용자 설정(`~/.config/tio/`, `~/.minirc.dfl` 등)은 직접 삭제해야 한다.

```bash
rm -f ~/.minirc.dfl              # minicom 사용자 설정
rm -rf ~/.config/tio             # tio 프로필
```

---

# [09] 요약

| 단계 | 명령 |
|------|------|
| 장치 확인 | `ls /dev/ttyUSB*`, `dmesg \| grep ttyUSB`, `lsusb` |
| 권한 | `sudo usermod -aG dialout $USER` (재로그인) |
| screen | `screen /dev/ttyUSB0 9600` / 종료 `Ctrl+a` `k` |
| minicom | `minicom -D /dev/ttyUSB0 -b 9600` / 종료 `Ctrl+a` `x` |
| picocom | `picocom -b 9600 /dev/ttyUSB0` / 종료 `Ctrl+a` `Ctrl+x` |
| tio | `tio -b 9600 /dev/ttyUSB0` / 종료 `Ctrl+t` `q` |
| 삭제 | `sudo apt remove/purge <pkg>` + `autoremove` |
