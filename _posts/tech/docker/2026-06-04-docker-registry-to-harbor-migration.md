---
title: "Docker Registry(registry:2)를 거의 무중단으로 Harbor로 마이그레이션하기"
description: "운영 중인 registry:2를 같은 호스트·같은 포트 그대로 Harbor로 교체한 실전 기록 — 임시 포트 공존, skopeo 이관, 짧은 컷오버, 그리고 컨테이너명 충돌·project 세그먼트·public 프로젝트 3가지 함정"
excerpt: "임시 포트에 Harbor를 먼저 띄워 이미지를 옮긴 뒤, 짧은 컷오버로 기존 포트를 넘겨받는다 — 노드 설정 변경 없이 registry:2 → Harbor 전환"
date: 2026-06-04
categories: Docker
tags: [Docker, Harbor, Registry, registry2, skopeo, Kubernetes, containerd, Migration, OCI, ContainerRegistry, DevOps]
ref: docker-registry-to-harbor-migration
---

:bulb: 운영 중인 `registry:2`(Docker Distribution)를 **같은 호스트·같은 포트**(`:5100`) 그대로 **Harbor**로 교체한 실전 기록이다. 임시 포트(`:5101`)에 Harbor를 먼저 띄워 이미지를 옮긴 뒤, 짧은 컷오버로 `:5100`을 넘겨받는다. Kubernetes 클러스터가 이 레지스트리에서 이미지를 pull 하는 상태에서, **노드 설정 변경 없이** 전환하는 것이 목표다.
{: .notice--info}

---

# [01] TL;DR

<pre class="mermaid">
graph LR
    A["1. :5101에<br/>Harbor 설치"] --> B["2. skopeo로<br/>이미지 이관"]
    B --> C["3. 검증"]
    C --> D["4. registry 중지<br/>Harbor를 :5100으로"]
    D --> E["5. 이미지 경로<br/>(project) 갱신"]

    style A fill:#e3f2fd,stroke:#1565c0
    style D fill:#fff3e0,stroke:#e65100
    style E fill:#e8f5e9,stroke:#2e7d32
</pre>

**핵심 함정 3가지**

| # | 함정 | 회피 |
|---|------|------|
| ① | Harbor 내부 컨테이너명 `registry` 충돌 | 기존 컨테이너를 `rename`(무중단) |
| ② | Harbor는 경로에 **project 세그먼트** 강제 | prefix를 한 변수로 모음 |
| ③ | 프로젝트를 **public**으로 두면 노드/시크릿 변경 불필요 | public 프로젝트 + 동일 host:port·HTTP |

---

# [02] 왜 Harbor인가

`registry:2`는 가볍고 OCI(Helm 차트 포함)도 잘 서빙하지만, **이미지 목록을 `curl`로 봐야 하고**, 삭제/GC가 번거롭고, RBAC·취약점 스캔·proxy-cache가 없다. Harbor(CNCF, Apache-2.0, 무료)는 **Web GUI, 보존정책/GC, RBAC, Trivy 스캔, 업스트림 proxy-cache**를 제공한다.

:warning: **Helm 차트 호스팅 때문이라면 Harbor가 필수는 아니다.** `registry:2`도 OCI 아티팩트(Helm 차트)를 서빙한다. Harbor는 "거버넌스/가시성"이 필요할 때의 선택이다.
{: .notice--warning}

---

# [03] 전제 / 환경

- 레지스트리 호스트: Ubuntu 22.04, `docker` + `docker compose v2` 설치됨, 디스크·메모리 여유.
- 기존 `registry:2`가 **HTTP(평문, insecure)** 로 동작 중. (TLS 미사용 → 노드는 이미 insecure 신뢰 설정됨)
- 클러스터 노드(containerd)에 해당 레지스트리가 **insecure/HTTP**로 등록되어 있음.
- 이 글은 HTTP 유지 + **public 프로젝트**(pull 무인증) 시나리오. (사내 CA/TLS가 있으면 노드 CA 배포로 바꿀 것.)

## 3-1. 변수 (본인 환경에 맞게 치환)

```bash
REG_HOST=192.0.2.10            # 레지스트리 호스트 IP (예시 문서용 IP)
PORT_FINAL=5100               # 최종 서비스 포트(기존 registry와 동일)
PORT_TEMP=5101                # 마이그레이션용 임시 포트
HARBOR_VER=v2.14.4            # Harbor 버전(최신 릴리스 확인)
PROJECT=myproject            # Harbor 프로젝트명
ADMIN_PW='<관리자비밀번호>'    # Harbor admin 비밀번호
```

---

# [04] Step 1. Harbor 설치 (임시 포트 `:5101`)

:bulb: 기존 registry는 `:5100`에서 계속 서비스 중이므로, Harbor를 **다른 포트**에 먼저 올려야 충돌 없이 공존한다.
{: .notice--info}

## 4-1. 설치 파일 내려받기

```bash
mkdir -p /opt/harbor-install && cd /opt/harbor-install
curl -fSL -o harbor-offline-installer-$HARBOR_VER.tgz \
  https://github.com/goharbor/harbor/releases/download/$HARBOR_VER/harbor-offline-installer-$HARBOR_VER.tgz
tar xzf harbor-offline-installer-$HARBOR_VER.tgz
cd harbor
cp harbor.yml.tmpl harbor.yml
```

> 인터넷이 안 되는 호스트라면, 외부에서 받아 `scp`로 옮긴다. (offline installer는 Harbor 이미지를 모두 포함)

## 4-2. `harbor.yml` 편집 (임시 5101 + HTTP)

`https:` 블록을 통째로 주석 처리하고 HTTP만 사용한다.

```bash
awk 'BEGIN{h=0} /^https:/{h=1} h&&/^[a-zA-Z]/&&!/^https:/{h=0} {if(h) print "# "$0; else print}' harbor.yml.tmpl \
 | sed "s/^hostname: .*/hostname: $REG_HOST/" \
 | sed "s/^  port: 80\$/  port: $PORT_TEMP/" \
 | sed "s/^harbor_admin_password: .*/harbor_admin_password: $ADMIN_PW/" \
 | sed "s#^data_volume: .*#data_volume: /data/harbor#" > harbor.yml

# 확인
grep -E "^hostname:|^  port:|^# https:|^harbor_admin_password:|^data_volume:" harbor.yml
```

## 4-3. 설치

```bash
sudo ./prepare
sudo ./install.sh        # (선택) --with-trivy 로 취약점 스캔 활성화
```

## :warning: 함정 ① — 컨테이너명 `registry` 충돌

Harbor의 **내부 레지스트리 컨테이너 이름도 `registry`** 라서, 기존 `registry:2` 컨테이너와 충돌한다.

```
Error response from daemon: Conflict. The container name "/registry" is already in use ...
```

**해결**: 기존 컨테이너를 **rename**(실행 중 rename은 중단 없음 — `:5100` 계속 서비스)한 뒤 다시 올린다.

```bash
docker rename registry registry-legacy     # 기존 registry:2, 중단 없이 이름만 변경
curl -s -o /dev/null -w "5100 still up -> %{http_code}\n" http://localhost:$PORT_FINAL/v2/   # 200 확인
cd /opt/harbor-install/harbor && docker compose up -d
```

## 4-4. 헬스 체크 + 프로젝트 생성(public)

```bash
# 헬스
curl -s http://localhost:$PORT_TEMP/api/v2.0/health | grep -o '"status":"healthy"' | head -1

# 프로젝트 myproject 를 public 으로 생성 (pull 무인증 → 노드/시크릿 변경 불필요)
curl -s -u admin:$ADMIN_PW -X POST http://localhost:$PORT_TEMP/api/v2.0/projects \
  -H "Content-Type: application/json" \
  -d "{\"project_name\":\"$PROJECT\",\"public\":true}" -w "\nHTTP %{http_code}\n"
```

---

# [05] Step 2. 이미지 이관 (`:5100` → `:5101/myproject/...`)

`skopeo`로 레지스트리 간 직접 복사한다(로컬 docker 저장소를 거치지 않아 빠름).

```bash
sudo apt-get install -y skopeo    # 없으면 설치
```

## :warning: 함정 ② — Harbor는 경로에 **project 세그먼트**가 강제됨

`registry:2`의 평면 경로 `…/my-operator`는 Harbor에서 `…/<project>/my-operator`가 된다. 그래서 복사 목적지를 `$PROJECT/<원경로>`로 지정한다.

```bash
SRC=localhost:$PORT_FINAL
DST=localhost:$PORT_TEMP

# 옮길 저장소 목록 (필요한 것만!). 전체를 옮기려면 /v2/_catalog 로 열거.
REPOS="my-operator my-agent my-driver-ds base/kubectl vendor/device-plugin"

for repo in $REPOS; do
  # 해당 repo의 태그 열거
  tags=$(curl -s http://$SRC/v2/$repo/tags/list \
         | tr ',' '\n' | sed 's/[]["{}]//g;s/tags://;s/name://;s/ //g' | grep -v '^$')
  for t in $tags; do
    [ "$t" = "$(basename $repo)" ] && continue   # 파서가 repo명을 태그로 오인하는 경우 스킵
    echo ">> $repo:$t"
    skopeo copy --quiet --all \
      --src-tls-verify=false --dest-tls-verify=false \
      --dest-creds admin:$ADMIN_PW \
      docker://$SRC/$repo:$t docker://$DST/$PROJECT/$repo:$t
  done
done
```

> 결과 경로 예: `…:5101/myproject/my-operator:v0.5.24`. Harbor는 project 하위 다단계 repo(`myproject/vendor/device-plugin`)를 허용한다.
> GUI 기반을 선호하면 **Harbor Replication**(Administration → Registries에 "Docker Registry" 엔드포인트 등록 → pull 규칙)도 가능하다.

---

# [06] Step 3. 이관 검증

```bash
# Harbor에 들어온 저장소/아티팩트 확인 (GUI: Projects → myproject → Repositories)
curl -s -u admin:$ADMIN_PW "http://localhost:$PORT_TEMP/api/v2.0/projects/$PROJECT/repositories?page_size=100" \
  | tr ',' '\n' | grep '"name"'

# 무인증 pull 테스트(public 프로젝트라 토큰 없이 docker가 익명 토큰을 받아 pull)
docker pull localhost:$PORT_TEMP/$PROJECT/my-operator:v0.5.24
```

:warning: `curl`로 `/v2/.../manifests/...`를 직접 치면 **401**이 난다(토큰 절차를 안 거쳐서). **`docker pull`이 정확한 검증**이다.
{: .notice--warning}

---

# [07] Step 4. 컷오버 — 기존 registry 중지하고 Harbor를 `:5100`으로

:warning: 여기서만 짧은(수 분) 다운타임이 발생한다. **이미 실행 중인 파드는 캐시로 무영향**, 단 그 사이의 파드 재시작/신규 스케줄은 일시적으로 pull 실패할 수 있으니 빠르게 진행한다.
{: .notice--warning}

```bash
# (1) 기존 registry 중지 (데이터는 보존 — 롤백 대비)
docker update --restart=no registry-legacy
docker stop registry-legacy
ss -ltn | grep -q ":$PORT_FINAL" && echo "아직 점유" || echo "5100 해제됨"

# (2) Harbor 포트 5101 → 5100 전환
cd /opt/harbor-install/harbor
sed -i "s/^  port: $PORT_TEMP\$/  port: $PORT_FINAL/" harbor.yml
sudo ./prepare
sudo docker compose down && sudo docker compose up -d

# (3) Harbor가 5100에서 응답하는지
curl -s http://localhost:$PORT_FINAL/api/v2.0/health | grep -o '"status":"healthy"' | head -1
```

---

# [08] Step 5. 클라이언트 갱신

## 8-1. 노드(containerd) — **변경 불필요**

같은 `호스트:포트`에 HTTP, 그리고 **public 프로젝트**이므로, 기존 insecure 설정이 그대로 동작한다. containerd는 Harbor의 익명 토큰 절차까지 자동 처리한다.

```bash
# 임의의 노드에서 (k8s 실제 pull 경로)
sudo crictl pull $REG_HOST:$PORT_FINAL/$PROJECT/my-operator:v0.5.24
```

> containerd 1.7+의 `/etc/containerd/certs.d/<host:port>/hosts.toml`에 `server="http://…"` + `skip_verify=true`가 있으면 OK.
> (private 프로젝트로 갔다면 여기서 노드 인증 + k8s `imagePullSecret`가 필요해진다.)

## 8-2. 애플리케이션의 이미지 경로 갱신 (project 세그먼트 추가)

이미지 경로가 `…/my-operator` → `…/myproject/my-operator`로 바뀌었으니, 매니페스트/Helm values를 갱신한다. 레지스트리 prefix를 한 변수로 모아두면 한 줄로 끝난다(예: Helm `global.registry`).

```bash
# 예: Helm 차트가 global.registry 로 prefix를 조립하는 경우
helm upgrade --install <release> <chart> -n <ns> \
  --set global.registry=$REG_HOST:$PORT_FINAL/$PROJECT
```

## :warning: 함정 ③ — `.env`의 공백 값은 따옴표로 감싸기

배포 래퍼가 `source deploy.env` 하는 구조라면, 공백이 들어간 값은 **반드시 따옴표**로 감싸야 한다. 안 그러면 `source` 시 첫 토큰만 변수에 들어가고 나머지를 명령으로 실행하려다 실패한다.

```bash
# 잘못: EXTRA_ARGS=--set a=b --set c=d        # → "c=d: 그런 파일이 없습니다" 류 오류
# 올바름:
EXTRA_ARGS="--set a=b --set c=d"
```

---

# [09] 최종 검증

```bash
kubectl get pods -A | grep -iE "ImagePull|ErrImage" || echo "ImagePull 오류 없음"
kubectl get pod -n <ns> -o jsonpath='{..image}' | tr ' ' '\n' | grep "$PROJECT/" | sort -u   # 새 경로 사용 확인
```

- 애플리케이션이 모두 `…/myproject/…` 경로에서 pull 되고, 정상 동작하면 성공이다.
- **Harbor 컨테이너는 `restart: always`** 라 호스트 재부팅 시 자동 기동된다.

---

# [10] 롤백 (문제 발생 시)

기존 데이터를 보존했으므로 즉시 되돌릴 수 있다.

```bash
cd /opt/harbor-install/harbor && sudo docker compose down       # Harbor 내림
docker start registry-legacy                                    # 기존 registry:2 재기동(:5100)
docker update --restart=always registry-legacy
# 애플리케이션 values의 레지스트리 경로를 원래(project 없는)대로 되돌리고 재배포
```

---

# [11] 마치며 — 배운 점(함정 정리)

1. **컨테이너명 충돌**: Harbor 내부 `registry`와 기존 `registry:2` 컨테이너명이 겹친다 → 기존을 `rename`(무중단)으로 회피.
2. **project 세그먼트**: Harbor는 모든 repo가 project 하위 → 이미지 경로가 바뀐다. prefix를 한 변수(`global.registry` 등)로 모아두면 전환이 한 줄.
3. **public 프로젝트의 가치**: pull 무인증을 유지하면 **노드 설정·imagePullSecret 변경이 전혀 필요 없다**(같은 host:port·HTTP 전제).
4. **TLS가 본질**: "노드 설정을 안 건드리고 싶다"의 답은 Harbor가 아니라 **신뢰된 CA 기반 TLS**. 제품과 무관.
5. **`.env` 따옴표**: 공백 포함 값은 반드시 quoting.
6. **검증은 `docker/crictl pull`로**: `curl`의 401은 토큰 절차 미수행 때문이며 오류가 아니다.

:bulb: 결과: 같은 주소(`:5100`)를 유지한 채 GUI·GC·스캔·RBAC를 얻었고, 실행 중인 워크로드는 무중단으로 넘어왔다.
{: .notice--success}
