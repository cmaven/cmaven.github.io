---
title: "Jekyll 기반 Github Blog를 Ubuntu에서 서비스 하기"
description: "Ubuntu 환경에서 Ruby, Jekyll을 설치하고 GitHub 블로그를 로컬 또는 외부에서 미리보기하는 방법"
excerpt: "Ubuntu에서 Ruby, Jekyll 설치 후 GitHub 블로그를 로컬 서버로 실행하여 미리보기하는 방법"
date: 2022-06-16
categories: Github_Blog
tags: [Jekyll, Ubuntu, Ruby, GEM, Bundler, 로컬서버, 블로그미리보기]
---

:bulb: 작성한 블로그를 Ubuntu 환경에서 Local 또는 외부 접근(동일 네트워크 망)에서 확인하는 방법을 작성한다.
{: .notice--info}

# [01]  Jekyll on Ubuntu 환경 구성 

> 구글 검색 엔진에서 등록된 웹사이트가 검색되도록 등록하고, 검색 결과를 모니터링 할 수 있는 서비스로, 웹 크롤링 형태로 동작한다.  

- Ruby 및 관련 패키지 설치  

```shell
sudo apt-get update
sudo apt-get install ruby-full build-essential zlib1g-dev
```  

- GEM 설정 시, `sudo` 명령어를 사용하지 않기 위해 = 사용 편의성을 높이기 위해 환경설정
  > Ruby에서 사용하는 라이브러리 관리 툴로 Ruby에 특화된 apt-get 툴로 생각하면 된다.  
- 아래 설정은 `root`를 제외한 사용자 계정에서 하는 것이 권장된다.
```shell
echo '# Install Ruby Gems to ~/gems' >> ~/.bashrc
echo 'export GEM_HOME="$HOME/gems"' >> ~/.bashrc
echo 'export PATH="$HOME/gems/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```  

- Jekyll 과, Bundler 설치
```shell
gem isntall jekyll bundler
```

# [02]  GitBlog Site 구성 혹은 다운로드  

- 기 구성된 GitBlog 사이트를 다운 받아(git clone) 필요 패키지 설치

```shell
# 예)
cd gitblog
bundle install
```  
- GitBlog 서비스 실행
```shell
''' Local 실행 '''
jekyll serve
''' 외부접속 가능하도록 서버 IP기반 실행 '''
jekyll serve --host=${Server IP address}
```