---
title: "Gitlab md 파일의 수식 렌더링 제한 문제(LaTex, Math Rendering limts)"
date: 2025-01-10
categories: VScode
tags: [Gitlab, LaTex, Math_Rendering_Limits]
---

:bulb: Gitlab 사용 시, 마크다운 파일(.md)에서 Math 관련 VSCode 사용 시,   
LaTex Inline Math Experession (LaTex 문법 수학적 표현, 포맷팅 명령)의 제한으로  
제대로 렌더링 되지 않고, 명령어 자체로 출력되는 문제를 해결한다.  
{: .notice--info}  

# [01] LaTex Rendering Limits 문제

## 현상  

- Gitlab의 마크다운 문서에서 색상을 적용하기 위해, LaTex Inline Math Expression 사용
  ```markdown  
  1. I only **$`\textcolor{orange}{\textsf{use}}`$** smartphone these days.
  ```   

  - 일정 수를 넘어가면, 색상이 렌더링되지 않고, 명령어가 출력되는 현상 확인
  ![2025-01-10 13 46 22](https://github.com/user-attachments/assets/3959c5d2-7d30-432e-b189-6e90dc2288e8)  


## 원인  
- 과도한 LaTex Inline Math Expression 사용은 페이지 렌더링 시, 성능 문제가 있을 수 있음
- GitLab에서는 이를 기본적으로 제한하고 있으며, 필요 시, 설정 변경을 통해 제한을 해제해야함
  - [참조-Gitlab Issue](https://gitlab.com/gitlab-org/gitlab/-/issues/368009){:target="_blank"}   
  - [참조-Gitlab Docs](https://docs.gitlab.com/ee/administration/instance_limits.html#math-rendering-limits){:target="_blank"}  


# [02] 해결 방법(렌더링 제한 해제)  

로컬 환경에서 실행 중인 Gitlab을 기준으로 한다.  
해당 환경은 Docker Container 기반으로 실행 중이다.  

## Gitlab 실행 컨테이너 접근  

```shell
docker exec -it <gitlab-container-name> /bin/bash
```

## 설정 변경 (Gitlab Rails console 활용)  

```shell
gitlab-rails console

# 콘솔 명령어 입력 창
console> ApplicationSetting.update(math_rendering_limits_enabled: false)
# 적용 확인 
console> ApplicationSetting.current.math_rendering_limits_enabled
console> exit

# 재설정
gitlab-ctl reconfigure
```  

- 과정 참조(스크린샷)
  ![2025-01-09 22 04 23](https://github.com/user-attachments/assets/1bac8242-e704-4638-abb0-c28bfa9bb474)  

  ![2025-01-09 22 05 03](https://github.com/user-attachments/assets/e37c1635-e211-4b7a-96b1-ee484834c72a)  


## Gitlab 컨테이너 재시작

```shell
docker restart <gitlab-container-name>
```


# [03] 적용 예

- 정상적으로 적용된 렌더링(컬러 출력)
  ![2025-01-09 22 05 29](https://github.com/user-attachments/assets/b4c58e0a-63c1-4aa2-a990-8f66b2ea3fe0)
