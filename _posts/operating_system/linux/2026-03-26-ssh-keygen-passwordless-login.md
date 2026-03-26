---
title: "SSH 키 인증으로 패스워드 없이 서버 접속하기"
description: "ssh-keygen으로 키 쌍을 생성하고 ssh-copy-id로 원격 서버에 등록하여 패스워드 없이 SSH 접속하는 방법"
excerpt: "SSH 키 생성(ssh-keygen), 공개키 등록(ssh-copy-id), 권한 설정, config 파일 활용까지 정리"
date: 2026-03-26
categories: Linux
tags: [SSH, ssh-keygen, ssh-copy-id, 공개키인증, 패스워드없이접속, authorized_keys, ssh-config]
---

:bulb: Ubuntu에서 외부 서버에 패스워드 없이 접속하기 위한 SSH 키 인증 설정 방법을 정리한다.
{: .notice--info}

# [01] SSH 키 인증 원리

SSH 키 인증은 **공개키(public key)**와 **개인키(private key)** 쌍을 사용한다.

```
┌─────────────────┐                    ┌─────────────────┐
│   로컬 PC        │                    │   원격 서버       │
│                 │                    │                 │
│  ~/.ssh/id_rsa  │ ── 개인키(비공개) ──  │                 │
│  ~/.ssh/id_rsa  │                    │ ~/.ssh/         │
│         .pub    │ ── 공개키 복사 ───→ │ authorized_keys │
└─────────────────┘                    └─────────────────┘
```

| 키 | 위치 | 역할 |
|---|---|---|
| **개인키** (`id_rsa`) | 로컬 PC | 본인 증명용. 절대 외부에 공개하지 않는다 |
| **공개키** (`id_rsa.pub`) | 원격 서버 | 서버에 등록해두면, 개인키를 가진 사람만 접속 허용 |

:warning: 개인키(`id_rsa`)는 절대 다른 사람이나 서버에 복사하지 않는다. 공개키(`.pub`)만 서버에 등록한다.
{: .notice--warning}

---

# [02] SSH 키 생성

## 2-1. ssh-keygen 실행

```bash
ssh-keygen -t rsa -b 4096
```

| 옵션 | 설명 |
|---|---|
| `-t rsa` | RSA 알고리즘 사용 |
| `-b 4096` | 키 길이 4096비트 (기본 3072, 보안상 4096 권장) |

## 2-2. 대화형 입력

```
Generating public/private rsa key pair.
Enter file in which to save the key (/home/user/.ssh/id_rsa):    ← Enter (기본 경로 사용)
Enter passphrase (empty for no passphrase):                      ← Enter (패스워드 없이 사용)
Enter same passphrase again:                                     ← Enter
```

| 질문 | 권장 입력 |
|---|---|
| 저장 경로 | Enter (기본 `~/.ssh/id_rsa`) |
| passphrase | Enter (비워두면 접속 시 추가 입력 없음) |

:bulb: passphrase를 설정하면 키 파일 자체에 암호가 걸려 보안이 강화되지만, 접속할 때마다 입력해야 한다. 자동화 목적이라면 비워둔다.
{: .notice--info}

## 2-3. 생성 결과 확인

```bash
ls -la ~/.ssh/
```

```
-rw-------  1 user user  3381  Mar 26 10:00  id_rsa        ← 개인키 (600 권한)
-rw-r--r--  1 user user   741  Mar 26 10:00  id_rsa.pub    ← 공개키
```

---

# [03] 공개키를 서버에 등록

## 3-1. ssh-copy-id 사용 (권장)

```bash
ssh-copy-id user@xxx.xxx.xxx
```

**실행 결과:**

```
/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s)
user@xxx.xxx.xxx's password:          ← 서버 패스워드 입력 (이번이 마지막)

Number of key(s) added: 1
```

이 명령 하나로 공개키가 서버의 `~/.ssh/authorized_keys`에 자동 등록된다.

## 3-2. 수동 등록 (ssh-copy-id가 없는 경우)

```bash
# 공개키 내용을 서버의 authorized_keys에 추가
cat ~/.ssh/id_rsa.pub | ssh user@xxx.xxx.xxx "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

---

# [04] 접속 테스트

```bash
ssh user@xxx.xxx.xxx
```

패스워드 입력 없이 바로 접속되면 성공이다.

```
Welcome to Ubuntu 22.04.x LTS
Last login: Wed Mar 26 10:05:00 2026 from 192.168.x.x
user@server:~$
```

---

# [05] 권한 설정 확인

SSH 키 인증이 동작하지 않는 가장 흔한 원인은 **파일 권한 문제**다.

## 5-1. 로컬 PC

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

## 5-2. 원격 서버

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

| 대상 | 권한 | 설명 |
|---|---|---|
| `~/.ssh/` | `700` (drwx------) | 소유자만 접근 |
| `id_rsa` | `600` (-rw-------) | 소유자만 읽기/쓰기 |
| `id_rsa.pub` | `644` (-rw-r--r--) | 공개키이므로 읽기 허용 |
| `authorized_keys` | `600` (-rw-------) | 소유자만 읽기/쓰기 |

:warning: 권한이 너무 열려 있으면(예: 644인 개인키) SSH가 키 파일 사용을 거부한다.
{: .notice--warning}

---

# [06] SSH config로 편하게 접속하기

매번 `ssh user@xxx.xxx.xxx`를 입력하는 대신, `~/.ssh/config` 파일에 별칭을 등록할 수 있다.

```bash
vi ~/.ssh/config
```

```
Host myserver
    HostName xxx.xxx.xxx
    User user
    IdentityFile ~/.ssh/id_rsa
    Port 22
```

이후 별칭으로 접속한다.

```bash
ssh myserver
```

**여러 서버를 등록하는 예시:**

```
Host dev
    HostName 10.254.202.91
    User kcloud

Host prod
    HostName 10.254.202.92
    User deploy
    Port 2222

Host gpu
    HostName 10.254.203.10
    User ml
    IdentityFile ~/.ssh/id_rsa_gpu
```

```bash
ssh dev     # → kcloud@10.254.202.91:22
ssh prod    # → deploy@10.254.202.92:2222
ssh gpu     # → ml@10.254.203.10 (별도 키 사용)
```

:bulb: `scp`, `rsync` 등 SSH 기반 명령어에서도 config 별칭을 그대로 사용할 수 있다.
{: .notice--info}

```bash
scp file.txt myserver:~/
rsync -avz ./project/ myserver:~/project/
```

---

# [07] 트러블슈팅

## 7-1. 패스워드를 계속 물어보는 경우

```bash
# 서버에서 SSH 디버그 확인
ssh -v user@xxx.xxx.xxx
```

출력에서 아래 내용을 확인한다.

```
debug1: Offering public key: /home/user/.ssh/id_rsa RSA
debug1: Server accepts key: /home/user/.ssh/id_rsa RSA     ← 이 줄이 있으면 키 인식 성공
```

키가 거부되면 아래를 점검한다.

| 점검 항목 | 확인 명령 |
|---|---|
| 로컬 개인키 권한 | `ls -la ~/.ssh/id_rsa` → 600이어야 함 |
| 서버 authorized_keys 권한 | `ls -la ~/.ssh/authorized_keys` → 600이어야 함 |
| 서버 .ssh 디렉토리 권한 | `ls -la -d ~/.ssh` → 700이어야 함 |
| 서버 홈 디렉토리 권한 | `ls -la -d ~` → 755 이하여야 함 |
| 서버 sshd 설정 | `PubkeyAuthentication yes` 확인 |

## 7-2. 서버에서 공개키 인증이 비활성화된 경우

```bash
# 서버에서 확인
sudo grep PubkeyAuthentication /etc/ssh/sshd_config
```

```
PubkeyAuthentication yes     ← yes여야 함
```

`no`로 되어 있으면 `yes`로 변경 후 SSH 재시작한다.

```bash
sudo vi /etc/ssh/sshd_config
sudo systemctl restart sshd
```

---

# [08] 전체 과정 요약

```bash
# 1. 키 생성 (로컬)
ssh-keygen -t rsa -b 4096

# 2. 공개키 등록 (서버로 전송)
ssh-copy-id user@xxx.xxx.xxx

# 3. 접속 테스트
ssh user@xxx.xxx.xxx

# 4. (선택) config 등록
echo "Host myserver
    HostName xxx.xxx.xxx
    User user" >> ~/.ssh/config

# 5. 별칭으로 접속
ssh myserver
```
