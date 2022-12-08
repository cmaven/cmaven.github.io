---
title: "장고 관리자 페이지 패스워드 간단하게 만들기"
date: 2022-12-08
categories: Python
tags: [Django, Password]
---

장고 (django)의 관리자 페이지에서 패스워드 (password) 검증 과정 중지  

------

django로 개발을 진행할 경우, 관리자 페이지에서 신규 유저(user)를 생성해야 할 때가 있다.
django 1.9 이후 부터, 관리자 페이지에서 신규 유저 생성 시, 패스워드 검증 과정을 거친다.  

- 개인정보와 비슷한 문자 불가
- 적어도 8개 이상의 문자 불가
- 일반적인 패스워드 불가
- 숫자로만 이루어진 패스워드 불가

![2022-12-08 23 42 27](https://user-images.githubusercontent.com/76153041/206478505-00bfcd9a-91e9-4485-8c45-b5a51f6305c1.png)

빠르게 테스트하고 개발하여야 할 때는 매우.. 불편한 기능이므로, 해당 기능을 중단시키고자 한다.  

> 장고 간단한 패스워드 사용하기  

- settings.py
  - `AUTH_PASSWORD_VALIDATORS` 부분을 모두 주석 처리
  - 빈 list 생성  

  ```python
  # ...
  
  '''
  AUTH_PASSWORD_VALIDATORS = [
      {
          'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
      },
      {
          'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
      },
      {
          'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
      },
      {
          'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
      },
  ]
  '''
  
  AUTH_PASSWORD_VALIDATORS = []
  
  # ...
  ```  

프로젝트를 새로 시작하면 (`python manage.py runserver`) 검증 기능이 중단된 것을 확인할 수 있다.  

![2022-12-08 23 41 57](https://user-images.githubusercontent.com/76153041/206478515-017fc3e2-660f-4b6e-aa93-d89b406e237a.png)  


