---
layout: post
title: "Windows 10 + Ubuntu 16.04 Multi Booting 환경 구성"
date: 2019-04-10 12:00
categories: Linux
tags: Linux, Windows
---



Windows 10이 설치된 컴퓨터에 Ubuntu 16.04를 설치하여 사용하는 방법에 대해 작성한다.

------

### Windows 10 + Ubuntu 16.04

##### Windows 10 초기 설정

1. 윈도우 빠른 시작 해제

   . "윈도우 빠른 시작" 을 활성화 시켜놓으면, 컴퓨터 부팅 시, CMOS에 진입할 수 없음

   . 활성화 되어 있는 상태에서는 PC가 완전히 종료되지 않고 하이브리드 절전모드로 진입하기 때문

   . CMOS 설정을 위해서 해당 옵션을 비활성화 시켜주어야 함

   ![이미지 20](https://user-images.githubusercontent.com/29933947/55859932-11a56580-5bae-11e9-8f11-ec14a7e43945.png)

   

   

   ![이미지 22](https://user-images.githubusercontent.com/29933947/55860487-4fef5480-5baf-11e9-8751-9bd3a5986c19.png)

   

   

   ![이미지 23](https://user-images.githubusercontent.com/29933947/55860491-51b91800-5baf-11e9-885a-02e3b205cc17.png)

   

2. Ubuntu를 위한 디스크 준비(파티션)

   . 아래 환경은 Ubuntu를 위한 별도의 디스크가 존재함

   . 해당 디스크는 "할당되지 않음" 으로 구성(모든 볼륨을 삭제)

   

   

   ![이미지 25](https://user-images.githubusercontent.com/29933947/55861485-70b8a980-5bb1-11e9-99de-8ce48dba23df.png)

   

   

   ![이미지 27](https://user-images.githubusercontent.com/29933947/55861488-71514000-5bb1-11e9-9815-d98fdb0feae4.png)

   

3. BIOS(CMOS) 설정

   . BIOS 고급모드 → 빠른 부팅 "비활성화"

   . BIOS 고급모드 → CSM "비활성화" 

   . BIOS 고급모드 → 안전모드 → OS 종류 "기타 OS"



##### Ubuntu 16.04 설치

1. Install type → Something else 선택

   ![이미지 28](https://user-images.githubusercontent.com/29933947/55862848-41f00280-5bb4-11e9-9ad6-06526ed49e9c.png)

   

   

2. 파티션 설정 - Swap - 64GB의 경우 16GB 정도 권장(16384MB)

   

   ![이미지 29](https://user-images.githubusercontent.com/29933947/55862850-41f00280-5bb4-11e9-8e2a-9e859de213b0.png)

   

   

3. 파티션 설정 - 루트(root)

   

   ![이미지 30](https://user-images.githubusercontent.com/29933947/55862851-41f00280-5bb4-11e9-9450-ab1859937a9b.png)

   

   

4. 파티션 설정 - 부트로더 설치 경로

   . Windows 10이 설치 되어 있는 디스크 선택(Default로 선택되어 있어 따로 수정할 필요 없음)

   

   ![이미지 31](https://user-images.githubusercontent.com/29933947/55863125-df4b3680-5bb4-11e9-8935-bcaa962b37cc.png)

   

   ##### 이 후 설치 과정은 기본 Ubuntu 설치 과정과 동일함







