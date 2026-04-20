---
title: "cannot open display localhost:10.0 해결 — MobaXterm X11 포워딩으로 Snap Firefox 실행하기"
description: "MobaXterm X11 포워딩 시 'cannot open display localhost:10.0', 'Unsupported authorisation protocol' 오류의 원인과 XAUTHORITY 설정 해결법"
excerpt: "Error: cannot open display: localhost:10.0 — Snap Firefox의 XAUTHORITY 미설정이 원인, 환경변수 명시적 설정으로 해결"
date: 2026-04-15
categories: Etc
tags: [MobaXterm, X11, Firefox, Snap, xauth, XAUTHORITY, Ubuntu, cannot-open-display, 원격데스크톱, 한글폰트]
---

:bulb: Windows MobaXterm에서 SSH + X11 포워딩으로 Ubuntu 서버의 Snap Firefox를 실행하면서 겪은 인증 오류와 해결 과정을 정리한다.
{: .notice--info}

**환경**: Windows + MobaXterm(X11 proxy) → Ubuntu 22.04 서버 + Firefox snap 149.0.2

---

# [01] 문제 상황

MobaXterm에서 SSH로 Ubuntu 서버에 접속하고, X11 포워딩을 활성화한 상태에서 Firefox를 실행했다.

```bash
$ firefox &
libpxbackend-1.0.so: cannot open shared object file: No such file or directory
Failed to load module: /home/user/snap/firefox/common/.cache/gio-modules/libgiolibproxy.so
MobaXterm X11 proxy: Unsupported authorisation protocol
Error: cannot open display: localhost:10.0
```

오류 메시지가 말해주는 것:

| 오류 | 의미 |
|------|------|
| `libpxbackend-1.0.so` 없음 | Snap 샌드박스의 라이브러리 로딩 문제 |
| `Unsupported authorisation protocol` | X11 인증 프로토콜 불일치 |
| `cannot open display: localhost:10.0` | 최종적으로 화면 연결 실패 |

---

# [02] 원인 파악 — DISPLAY와 xauth 불일치

## 2-1. 환경 확인

```bash
$ echo $DISPLAY
localhost:10.0

$ xauth list
myserver/unix:10  MIT-MAGIC-COOKIE-1  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**핵심 문제가 여기에 있다:**

| 항목 | 값 | 형식 |
|------|---|------|
| `DISPLAY` | `localhost:10.0` | TCP 형식 |
| `xauth` 엔트리 | `myserver/unix:10` | Unix 소켓 형식 |

MobaXterm의 X11 proxy는 TCP 기반(`localhost:10.0`)으로 연결하는데, xauth에는 Unix 소켓 형식(`/unix:10`)의 쿠키만 존재한다. **두 형식이 일치하지 않는다.**

## 2-2. 다른 X11 앱은 되는데 왜 Firefox만 안 될까?

```bash
$ xdpyinfo
name of display:    localhost:10.0
version number:    11.0
vendor string:    The X.Org Foundation
...
```

`xdpyinfo`는 정상 작동한다. X11 서버 자체에는 문제가 없다.

---

# [03] 핵심 원인 — Snap 샌드박스의 환경변수 차단

## 3-1. Snap 내부 환경 조사

Firefox를 Snap으로 실행할 때 환경을 확인해보면:

```bash
$ snap run firefox env | grep -i xauth
XAUTHORITY=
```

**`XAUTHORITY`가 비어있다!** Snap 샌드박스가 부모 환경의 환경변수를 상속하지 않았다.

더 심각한 문제:

```bash
$ snap run firefox which xauth
(출력 없음)
```

**Snap 내부에는 `xauth` 바이너리 자체가 없다.** 인증 쿠키를 생성하거나 검증할 수 없는 상태다.

## 3-2. 문제 구조

```
일반 X11 앱 (xdpyinfo 등)
  → 시스템 xauth 사용 → 쿠키 검증 → ✅ 연결 성공

Snap Firefox
  → Snap 샌드박스 진입
  → XAUTHORITY 환경변수 비어있음
  → xauth 바이너리 없음
  → 쿠키 검증 불가
  → ❌ "Unsupported authorisation protocol"
```

---

# [04] 해결 시도 과정

## 4-1. 시도 1 — xauth add로 TCP 쿠키 추가

```bash
$ xauth add localhost:10 MIT-MAGIC-COOKIE-1 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xauth:  unable to write authority file /home/user/.Xauthority
```

xauth가 TCP 형식 엔트리 추가를 거부했다.

## 4-2. 시도 2 — xauth generate

```bash
$ xauth generate :10
xauth:  (null):0:  unable to resolve "SECURITY" extension to get random data
```

Security extension 쿼리도 실패했다.

## 4-3. 근본 해결 — XAUTHORITY 명시적 설정

문제의 근본 원인이 Snap 샌드박스의 XAUTHORITY 미설정이므로, **명시적으로 지정**한다.

```bash
$ XAUTHORITY=$HOME/.Xauthority firefox --no-remote &
```

MobaXterm 창에 Firefox 화면이 나타났다.

`xhost`를 통한 추가 권한 설정도 도움이 된다:

```bash
$ xhost +local:
access control enabled, only authorized clients can connect
LOCAL:
```

---

# [05] 영구 설정

매번 입력하기 번거로우므로 `~/.bashrc`에 추가한다.

```bash
# ~/.bashrc 끝에 추가
export XAUTHORITY="$HOME/.Xauthority"
```

```bash
$ source ~/.bashrc
$ firefox --no-remote &
# 이제 정상 작동한다
```

---

# [06] 추가 이슈 — 한글 폰트 깨짐

Firefox가 실행됐지만, 한글 텍스트가 네모(□)로 표시됐다.

```bash
$ fc-list | grep -i hangul
(거의 출력 없음)
```

시스템에 한글 폰트가 설치되어 있지 않았다.

**해결:**

```bash
$ sudo apt update
$ sudo apt install fonts-noto-cjk fonts-nanum -y
$ fc-cache -fv
```

Firefox를 다시 실행하면 한글이 정상 표시된다.

---

# [07] 정리

## 7-1. 최종 해결 명령어

```bash
# 1회성 실행
XAUTHORITY=$HOME/.Xauthority firefox --no-remote &

# 영구 설정 (~/.bashrc에 추가)
export XAUTHORITY="$HOME/.Xauthority"
```

## 7-2. 핵심 교훈

| 교훈 | 설명 |
|------|------|
| **Snap은 환경변수를 상속하지 않는다** | 보안을 위해 부모 환경의 `XAUTHORITY`를 자동 전달하지 않음 |
| **xauth 형식 불일치를 확인하라** | Unix 소켓(`/unix:10`)과 TCP(`localhost:10`)는 다르다 |
| **일반 X11 앱이 된다고 다 되는 건 아니다** | `xdpyinfo`는 되지만 Snap 앱은 샌드박스 제약으로 실패할 수 있다 |
| **Snap 내부에는 xauth가 없다** | 인증 처리를 위해 `XAUTHORITY` 경로를 명시적으로 제공해야 한다 |
| **한글 폰트는 별도 설치** | `fonts-noto-cjk`, `fonts-nanum` 설치 필요 |

:bulb: 이 문제는 단순한 X11 인증 문제가 아니라, **Snap 샌드박스와 원격 X11 포워딩의 불완전한 상호작용**이다. Snap이 아닌 일반 패키지로 설치한 Firefox라면 이 문제가 발생하지 않는다.
{: .notice--info}
