---
title: "Ubuntu 22.04 한글 입력기 설치 및 한영 전환 설정"
description: "Ubuntu 22.04에서 fcitx, ibus 한글 입력기 설치 방법과 한영 전환 단축키 설정 가이드"
excerpt: "Ubuntu 22.04 LTS 영어 설치 후 fcitx-hangul, ibus-hangul 한글 입력기 설치 및 한영 전환 단축키 설정 방법"
date: 2026-03-16
categories: Linux
tags: [Ubuntu, Ubuntu-22.04, fcitx, fcitx-hangul, ibus, ibus-hangul, 한글입력, 한영전환, Linux-한글, Korean-input]
---

:bulb: Ubuntu 22.04 LTS를 영어로 설치한 후 한글 입력이 필요한 경우, 별도로 한글 입력기를 설치하고 한영 전환 단축키를 설정해야 합니다. fcitx 기반과 ibus 기반 두 가지 방법을 모두 다룹니다.
{: .notice--info}

# [01] 사전 준비: 한국어 언어팩 설치

## 1-1. GUI로 설치하기

1. **Settings** > **Region & Language** 로 이동
2. **Manage Installed Languages** 클릭
3. "The language support is not installed completely" 메시지가 나타나면 **Install** 클릭
4. **Install / Remove Languages** 클릭
5. 목록에서 **Korean** 체크 후 **Apply** 클릭

## 1-2. 터미널로 설치하기

```bash
sudo apt update
sudo apt install language-pack-ko language-pack-ko-base
```

한국어 로케일을 생성합니다.

```bash
sudo locale-gen ko_KR.UTF-8
```

# [02] 방법 1: fcitx-hangul (권장)

:star: fcitx는 가볍고 안정적인 입력기 프레임워크로, 한글 입력에 널리 사용됩니다.
{: .notice--info}

## 2-1. 패키지 설치

```bash
sudo apt install fcitx fcitx-hangul fcitx-config-gtk
```

## 2-2. 입력기 프레임워크를 fcitx로 변경

```bash
im-config -n fcitx
```

또는 GUI에서 설정하려면:

```bash
im-config
```

실행 후 **OK** > **Yes** 를 클릭하고, 목록에서 **fcitx**를 선택합니다.

## 2-3. 환경 변수 설정

`~/.profile` 파일 하단에 다음을 추가합니다.

```bash
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
```

## 2-4. 재부팅

```bash
sudo reboot
```

## 2-5. fcitx에 한글 입력기 추가

1. 시스템 트레이의 **키보드 아이콘** 우클릭 > **Configure** 선택
2. 또는 터미널에서 실행:

```bash
fcitx-config-gtk3
```

3. **Input Method** 탭에서 좌측 하단 **+** 버튼 클릭
4. **Only Show Current Language** 체크 해제
5. 검색창에 **Hangul** 입력 후 선택 > **OK** 클릭

설정 완료 후, Input Method 목록:

```
1. Keyboard - English (US)
2. Hangul
```

:warning: 순서가 중요합니다. 영문 키보드가 1번, Hangul이 2번이어야 합니다.
{: .notice--warning}

# [03] 방법 2: ibus-hangul

:bulb: ibus는 Ubuntu에 기본 내장된 입력기 프레임워크입니다.
{: .notice--info}

## 3-1. 패키지 설치

```bash
sudo apt install ibus-hangul
```

## 3-2. ibus 재시작

```bash
ibus restart
```

## 3-3. 한글 입력 소스 추가

1. **Settings** > **Keyboard** 이동
2. **Input Sources** 에서 **+** 클릭
3. **Korean** 선택
4. **Korean (Hangul)** 선택 후 **Add** 클릭

Input Sources 목록:

```
1. English (US)
2. Korean (Hangul)
```

# [04] 한영 전환 단축키 설정

## 4-1. fcitx 한영 전환 단축키

### 방법 A: fcitx 설정에서 변경

1. `fcitx-config-gtk3` 실행
2. **Global Config** 탭 이동
3. **Trigger Input Method** 항목을 찾아 원하는 키로 변경
   - **한영키 사용**: 해당 항목 클릭 후 `한/영` 키 입력
   - **Right Alt 사용**: `Ralt`로 설정
   - **Shift+Space**: `Shift+Space`로 설정

### 방법 B: 설정 파일 직접 편집

```bash
nano ~/.config/fcitx/config
```

`[Hotkey]` 섹션에서 `TriggerKey`를 수정합니다.

```ini
[Hotkey]
# 한영키 사용 시
TriggerKey=HANGUL
# 또는 Right Alt 사용 시
# TriggerKey=RALT
# 또는 Ctrl+Space 사용 시 (기본값)
# TriggerKey=CTRL_SPACE
```

저장 후 fcitx 재시작:

```bash
fcitx -r
```

## 4-2. ibus 한영 전환 단축키

### 방법 A: GNOME 설정에서 변경

1. **Settings** > **Keyboard** > **Input Sources** 이동
2. **Keyboard Shortcuts** 메뉴에서 **Typing** 항목
3. **Switch to next input source** 를 원하는 키로 변경 (일반적으로 `Super+Space` 또는 `Alt+Shift`)

### 방법 B: 터미널에서 설정

```bash
# 한영키로 전환
gsettings set org.gnome.desktop.wm.keybindings switch-input-source "['Hangul']"
gsettings set org.gnome.desktop.wm.keybindings switch-input-source-backward "['Hangul']"
```

```bash
# 또는 Super+Space로 전환 (기본값)
gsettings set org.gnome.desktop.wm.keybindings switch-input-source "['<Super>space']"
```

## 4-3. 한영키가 인식되지 않을 때 (Right Alt → 한영키 매핑)

일부 키보드에서는 `한/영` 키가 `Right Alt`로 인식됩니다.

### xkb 옵션으로 설정

```bash
# 현재 세션에 즉시 적용
setxkbmap -option "korean:ralt_hangul"
```

영구 적용하려면 `~/.profile`에 추가합니다.

```bash
echo 'setxkbmap -option "korean:ralt_hangul"' >> ~/.profile
```

### GNOME Tweaks로 설정

```bash
sudo apt install gnome-tweaks
```

1. **Tweaks** 실행 > **Keyboard & Mouse** 이동
2. **Additional Layout Options** 클릭
3. **Korean Hangul/Hanja keys** 항목 펼침
4. **Make right Alt as Hangul, right Ctrl as Hanja** 선택

# [05] 트러블슈팅

## 5-1. 한글이 특정 앱에서만 입력되지 않는 경우

환경 변수가 올바르게 설정되어 있는지 확인합니다.

```bash
echo $GTK_IM_MODULE
echo $QT_IM_MODULE
echo $XMODIFIERS
```

fcitx 사용 시 세 값 모두 `fcitx`(XMODIFIERS는 `@im=fcitx`)으로 출력되어야 합니다.

:warning: Snap이나 Flatpak으로 설치된 앱은 별도의 환경 변수 전달이 필요할 수 있습니다.
{: .notice--warning}

```bash
# Snap 앱에 환경 변수 전달 예시
sudo snap set <앱이름> environment.GTK_IM_MODULE=fcitx
```

## 5-2. 한자 변환 창이 계속 뜨는 경우

```bash
nano ~/.config/fcitx/conf/fcitx-hangul.config
```

다음 항목을 `False`로 변경합니다.

```ini
HanjaMode=False
```

fcitx 재시작:

```bash
fcitx -r
```

## 5-3. fcitx가 자동 실행되지 않는 경우

시작 프로그램에 fcitx를 등록합니다.

```bash
cp /usr/share/applications/fcitx.desktop ~/.config/autostart/
```

## 5-4. ibus와 fcitx 충돌

하나의 입력기 프레임워크만 사용하는 것을 권장합니다.

```bash
# ibus-hangul 제거 (fcitx 사용 시)
sudo apt remove ibus-hangul

# 또는 fcitx 제거 (ibus 사용 시)
sudo apt remove fcitx fcitx-hangul
```

# [06] 비교 요약

| 항목 | fcitx-hangul | ibus-hangul |
|------|-------------|-------------|
| 설치 난이도 | 별도 설치 필요 | Ubuntu 기본 내장 |
| 안정성 | 높음 | 보통 |
| 설정 유연성 | 높음 (설정 파일 직접 편집 가능) | 보통 (GUI 위주) |
| 권장 환경 | 개발자, 파워 유저 | 일반 사용자 |

:star: 설정이 유연하고 안정적인 **fcitx-hangul**을 권장합니다. 한영 전환 단축키는 본인의 키보드와 사용 습관에 맞게 설정하면 됩니다.
{: .notice--info}
