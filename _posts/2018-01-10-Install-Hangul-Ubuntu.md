---
layout: post
title: "Ubuntu 16.04 한글 설치 및 단축키 지정"
category: Linux
tags: ubuntu
---

영문으로 설치된 우분투 환경에서 한글 입력을 설정하는 방법을 정리한다.

------



## 환경

- 운영체제: Ubuntu 16.04 64bit
- 영문 키보드, 언어 설치





## 설치

1. 한글 패키지 설치

   ```shell
   sudo apt-get install fcitx-hangul
   ```

2. System Setting - Language Support 실행 후, 미설치분 설치 완료

   ![ubuntu-install-hangul-01](https://user-images.githubusercontent.com/29933947/34772116-4cdefb18-f64a-11e7-9621-8251f2ef3162.png)

   ![ubuntu-install-hangul-02](https://user-images.githubusercontent.com/29933947/34772118-4e410d48-f64a-11e7-8633-a8f067c0141b.png)

3. Keyboard input method system 부문 fcitx로 설정

   ![ubuntu-install-hangul-03](https://user-images.githubusercontent.com/29933947/34772121-503ac382-f64a-11e7-9d94-2c7d66a2743f.png)

4. 시스템 재부팅






## 단축키 (한/영) 전환 설정

### Ubuntu Setting 사용

1. AllSettings - Keyboard - Shortcuts Tab - Typing

   ![ubuntu-hangul-shortcut-01](https://user-images.githubusercontent.com/29933947/34804760-a64df03c-f6bd-11e7-9bbf-0860cf65fcfd.png)

2. Disable 설정

   Switch to Next source / Switch to Previous source
   Compose Key / Alternative Characters Key

   ![ubuntu-hangul-shortcut-02](https://user-images.githubusercontent.com/29933947/34804761-a67d064c-f6bd-11e7-8c06-27985eb1cf92.png)

   * 옵션 부분 클릭 후, 백스페이스 키를 누르면 Disalbe로 변경 가능함

3. Compose Key 옵션 = Right Alt 및 Switch to next source 옵션 = Multikey

   ![ubuntu-hangul-shortcut-03](https://user-images.githubusercontent.com/29933947/34804762-a6ab6762-f6bd-11e7-9d12-076456ef47a9.png)

   * 한영키를 누르면 Multikey로 설정 가능함
   * Compose Key가 설정된 상태에서 수행해야함

4. 바탕화면 키보드 레이아웃 설정(오른쪽 상단의 키보드 표시) - Configure Current Input Method

   ![ubuntu-hangul-shortcut-04](https://user-images.githubusercontent.com/29933947/34804764-a6edaef6-f6bd-11e7-88ab-de5419941f37.png)

5. Input Method에 Hangul이 추가되어 있지 않으면, `+` 버튼을 클릭 후 Hangul을 추가함

   * Only Show Current Language의 체크를 해제해 주면 검색이 가능함

   ![ubuntu-hangul-shortcut-05](https://user-images.githubusercontent.com/29933947/34804765-a71aa55a-f6bd-11e7-9e5d-6f3f6d860b42.png)

6. Global Config 설정

   * Trigger Input Method 부분을 Multikey 로 지정
   * Extra key for trigger input method 을 Disabled 로 지정

   ![ubuntu-hangul-shortcut-06](https://user-images.githubusercontent.com/29933947/34804766-a7473ad4-f6bd-11e7-98e3-45d875d46585.png)





### 프로그램 사용

Ubuntu Setting을 통해 단축키 지정 시, Switch to next source의 옵션이 정상적으로 변경되지 않을 경우,    별도로 제공되는 프로그램을 설치 후, 직접 설정하는 방법을 사용한다.

> Error 
>

![1](https://user-images.githubusercontent.com/29933947/34805598-4ba6cb36-f6c2-11e7-8160-e6f0ef090d01.png)



1. dconf-Editor 설치

   ```shell
   sudo apt-get install dconf-tools
   ```

2. dconf Editor 실행

   ![4](https://user-images.githubusercontent.com/29933947/34805760-0d54b96e-f6c3-11e7-9134-33114d11ea9a.png)

3. org - gnome - desktop - wm - keybindings

   * switch-input-source : Hangul
   * switch-input-source-backward : Hangul

   ![5](https://user-images.githubusercontent.com/29933947/34805802-36293dec-f6c3-11e7-8fc7-59e5c4f002be.png)



