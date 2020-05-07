---
layout: post
title: "CPU 개수 확인"
date: 2018-01-04 16:45:00 +8000
categories: Linux
tags: Linux
---
# CPU 개수 확인

## 리눅스 명령어

* **하이퍼스레딩으로 운영체제에서 코어 수가 실제 코어의 2배로 표시된다.**
  - ex) 싱글코어 = 2 코어, 듀얼코어 = 4 코어

------

###### 시스템 전체 코어 수

```c
grep -c processor /proc/cpuinfo
```

```ruby
root# grep -c processor /proc/cpuinfo
24
```




















