---
title: "AWS Elastic Beanstalk vs ECS vs EKS — 무엇을, 언제, 어떻게 쓰나"
description: "Elastic Beanstalk·ECS·EKS 세 가지 컨테이너/배포 서비스 비교, PaaS·IaaS·CaaS 분류, 그리고 사용자가 컨테이너(Pod)를 배포하는 절차까지 한 번에 정리"
excerpt: "세 솔루션의 추상화 수준과 책임 경계, IaaS·PaaS·CaaS 어디에 속하는지, 그리고 EKS에서 Pod가 실제로 배포되는 7단계 절차를 실전 기준으로 비교한다"
date: 2026-06-08
categories: K8s
tags: [AWS, Kubernetes, EKS, ECS, ElasticBeanstalk, Fargate, PaaS, IaaS, CaaS, Pod, container, 배포, 클라우드]
ref: aws-eb-ecs-eks-comparison
---

:bulb: AWS에서 애플리케이션·컨테이너를 굴리는 대표 서비스 세 가지 — **Elastic Beanstalk, ECS, EKS** — 를 비교한다. ① 무엇이 다른지, ② PaaS/IaaS/CaaS 중 어디에 속하는지, ③ 사용자가 컨테이너(Pod)를 실제로 어떻게 배포하는지까지 순서대로 다룬다.
{: .notice--info}

---

# [01] 한눈에 보는 비교

| 구분 | Elastic Beanstalk | ECS (Elastic Container Service) | EKS (Elastic Kubernetes Service) |
|---|---|---|---|
| 핵심 정체 | 애플리케이션 배포 플랫폼 | AWS 자체 컨테이너 오케스트레이터 | 관리형 Kubernetes |
| 표준/엔진 | AWS 독자 (내부적으로 EC2/ECS 활용) | AWS 독자 (task/service 개념) | **표준 Kubernetes** (Pod/Deployment) |
| 추상화 수준 | **가장 높음** (코드만 올리면 됨) | 중간 | **가장 낮음** (가장 많은 제어권) |
| 사용자 책임 | 코드/설정 | 태스크 정의 + (EC2면) 노드 | 매니페스트 + (자체 노드면) 워커 노드 |
| 이식성(Portability) | 낮음 (AWS 종속) | 낮음 (AWS 종속) | **높음** (어디서나 동일 K8s API) |
| 러닝 커브 | 낮음 | 중간 | **높음** |
| 대표 사용처 | 단순/전통 웹앱, 빠른 배포 | AWS 안에서만 도는 컨테이너 워크로드 | 멀티클라우드·복잡한 MSA·생태계(헬름 등) 필요 |

:bulb: 한 문장 요약 — **"빨리 올리고 싶다 → Beanstalk", "AWS 안에서 컨테이너만 굴린다 → ECS", "표준 쿠버네티스 생태계가 필요하다 → EKS".**
{: .notice--info}

---

# [02] 각 서비스 깊게 보기

## 2-1. Elastic Beanstalk — "코드만 던져"

코드(또는 Docker 이미지)를 업로드하면 **EC2 인스턴스, 로드 밸런서, 오토 스케일링 그룹, 헬스 체크**까지 AWS가 자동으로 프로비저닝한다. 사용자는 인프라를 거의 신경 쓰지 않는다.

- 지원 런타임: Java, .NET, Node.js, Python, PHP, Go, Ruby + **Docker**
- 인프라가 숨겨져 있지만 **완전히 잠겨 있지는 않다** — 필요하면 생성된 EC2/보안그룹을 직접 만질 수 있다.
- 컨테이너 오케스트레이션 도구가 **아니다.** "애플리케이션 배포"를 자동화하는 플랫폼이다.

:warning: 멀티 컨테이너를 정교하게 다루거나, 세밀한 스케줄링·서비스 메시·헬름 같은 생태계가 필요하면 Beanstalk은 금방 한계에 부딪힌다. 그럴 땐 ECS/EKS로 넘어가야 한다.
{: .notice--warning}

## 2-2. ECS — "AWS표 컨테이너 오케스트레이터"

쿠버네티스가 아닌 **AWS 자체 오케스트레이터**다. `Task Definition`(컨테이너 스펙)과 `Service`(원하는 개수 유지) 개념으로 동작한다. 실행 방식이 두 가지다.

| 실행 방식(Launch Type) | 설명 | 성격 |
|---|---|---|
| **EC2** | 내가 EC2 노드를 직접 관리, 그 위에 컨테이너 배치 | IaaS에 가까움 |
| **Fargate** | 서버리스 — 노드 관리 없이 컨테이너만 실행 | PaaS(서버리스)에 가까움 |

- 장점: AWS 서비스(IAM, ALB, CloudWatch 등)와 **매끄럽게 통합**, 쿠버네티스를 몰라도 됨, 컨트롤 플레인 비용 없음.
- 단점: AWS **종속**(다른 클라우드로 이식 불가), 쿠버네티스 생태계(헬름/오퍼레이터 등)를 못 씀.

## 2-3. EKS — "관리형 쿠버네티스"

**표준 쿠버네티스**를 AWS가 운영해 준다. 컨트롤 플레인(API 서버, etcd 등)은 AWS가 관리하고, 사용자는 **워커 노드**와 **워크로드(Pod)**에 집중한다.

| 노드 운영 방식 | 설명 |
|---|---|
| 관리형 노드 그룹 | AWS가 EC2 워커 노드 라이프사이클 관리 |
| 자체 관리형 노드 | 워커 노드를 직접 운영 (최대 제어권) |
| **Fargate** | 노드 없이 Pod를 서버리스로 실행 |

- 장점: **표준 K8s API** → 온프레미스/타 클라우드와 동일하게 운영(이식성), 거대한 생태계(Helm, Operator, Istio, ArgoCD…) 사용 가능.
- 단점: 러닝 커브 높음, 컨트롤 플레인 **시간당 비용** 발생, 운영 복잡도 큼.

---

# [03] PaaS인가 IaaS인가? — 정확한 분류

흔히 "Beanstalk=PaaS, ECS/EKS=?"로 묻지만, 정확히는 셋 다 **IaaS와 PaaS 사이의 CaaS(Container as a Service)** 스펙트럼 위에 있다. 핵심은 **"어디까지를 사용자가 책임지는가(추상화 수준)"** 다.

```
관리 책임 많음(IaaS) ←─────────────────────────────→ 적음(PaaS/서버리스)

  EC2          ECS(EC2) / EKS(자체노드)      ECS(Fargate) / EKS(Fargate)      Beanstalk        Lambda
 [IaaS]            [CaaS, IaaS 쪽]              [CaaS, 서버리스/PaaS 쪽]        [PaaS에 근접]    [FaaS]
```

| 서비스 | 분류 | 한 줄 설명 |
|---|---|---|
| Elastic Beanstalk | **PaaS에 가장 근접** | 코드를 주면 플랫폼이 실행 환경 전체를 책임짐 |
| ECS / EKS (EC2·자체노드) | **CaaS** (IaaS 쪽) | 노드를 직접 관리 → 인프라 책임이 남아 IaaS 성격 |
| ECS / EKS (Fargate) | **CaaS** (PaaS/서버리스 쪽) | 노드 관리가 사라져 PaaS에 근접 |

:bulb: 즉 ECS·EKS는 **"실행 방식(Launch Type)"에 따라 IaaS↔PaaS 사이를 움직인다.** Fargate를 쓰면 서버(노드)를 안 보게 되므로 PaaS/서버리스에 가까워지고, EC2/자체 노드를 쓰면 인프라 책임이 늘어 IaaS에 가까워진다. "EKS는 PaaS다/IaaS다"라고 단정하면 틀린 이유가 여기 있다.
{: .notice--info}

---

# [04] 사용자가 컨테이너(Pod)를 배포하는 절차 — EKS(쿠버네티스) 기준

쿠버네티스에서 배포의 최소 실행 단위는 **Pod**다. 하지만 Pod를 직접 만들지 않고, 보통 **Deployment**(원하는 상태 선언)로 관리한다. 전체 흐름은 다음 7단계다.

```
[1] 코드          [2] 이미지 빌드        [3] 레지스트리(ECR) push
  app.py    ──▶   docker build    ──▶   <acct>.dkr.ecr...amazonaws.com/app:v1
                                              │
                                              ▼
[4] 매니페스트 작성     [5] kubectl apply        [6] 스케줄러가 노드에 Pod 배치
 deployment.yaml  ──▶   API 서버에 제출   ──▶   Node A: [Pod] [Pod]
                                              Node B: [Pod]
                                                  │
                                                  ▼
[7] Service/Ingress 로 외부 노출 + HPA 오토스케일 + 롤링 업데이트
```

## 4-1. 이미지 빌드 → 레지스트리 push

```bash
# 1) 컨테이너 이미지 빌드
docker build -t my-app:v1 .

# 2) ECR 로그인 + 태그 + push
aws ecr get-login-password --region ap-northeast-2 \
  | docker login --username AWS --password-stdin <acct>.dkr.ecr.ap-northeast-2.amazonaws.com
docker tag my-app:v1 <acct>.dkr.ecr.ap-northeast-2.amazonaws.com/my-app:v1
docker push <acct>.dkr.ecr.ap-northeast-2.amazonaws.com/my-app:v1
```

## 4-2. 매니페스트(Deployment) 작성

Pod를 직접 만들지 않고 **Deployment**로 "Pod를 몇 개, 어떤 이미지로 유지할지"를 **선언**한다.

```yaml
# deployment.yaml — 원하는 상태(desired state)를 선언
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3                 # Pod를 항상 3개 유지
  selector:
    matchLabels:
      app: my-app
  template:                   # ↓ 이 부분이 Pod 템플릿
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: <acct>.dkr.ecr.ap-northeast-2.amazonaws.com/my-app:v1
          ports:
            - containerPort: 8080
```

## 4-3. 클러스터에 적용 → 스케줄링

```bash
# 클러스터 접속 설정 (EKS)
aws eks update-kubeconfig --name my-cluster --region ap-northeast-2

# 매니페스트 적용 — API 서버에 "원하는 상태" 제출
kubectl apply -f deployment.yaml
```

이후 흐름은 쿠버네티스가 알아서 처리한다.

1. **API 서버**가 요청을 받아 etcd에 "Pod 3개 필요" 상태를 저장한다.
2. **컨트롤러**가 현재 0개 → 3개가 되도록 Pod 생성을 요청한다.
3. **스케줄러**가 리소스 여유가 있는 노드에 각 Pod를 배치한다.
4. 각 노드의 **kubelet**이 컨테이너 런타임으로 이미지를 받아 컨테이너를 띄운다.

```bash
# 배포 상태 확인
kubectl get pods -o wide      # Pod가 어느 노드에서 Running인지
kubectl get deployment my-app # 3/3 READY 확인
```

## 4-4. 외부 노출 (Service / Ingress)

Pod는 IP가 수시로 바뀌므로, 안정적 진입점으로 **Service**(또는 Ingress)를 둔다.

```yaml
# service.yaml — Pod 묶음에 고정 진입점 + 로드밸런서 부여
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  type: LoadBalancer          # AWS LB 자동 생성 (EKS)
  selector:
    app: my-app               # label이 app=my-app인 Pod로 트래픽 분배
  ports:
    - port: 80
      targetPort: 8080
```

```bash
kubectl apply -f service.yaml
kubectl get svc my-app        # EXTERNAL-IP(LB 주소) 확인
```

## 4-5. 스케일링 & 무중단 업데이트

```bash
# 수동 스케일: Pod 3개 → 5개
kubectl scale deployment my-app --replicas=5

# 자동 스케일(HPA): CPU 50% 기준 2~10개로 자동 조절
kubectl autoscale deployment my-app --cpu-percent=50 --min=2 --max=10

# 새 버전 롤링 업데이트(무중단): 이미지만 교체하면 점진 교체
kubectl set image deployment/my-app my-app=<acct>.dkr.ecr.ap-northeast-2.amazonaws.com/my-app:v2
kubectl rollout status deployment/my-app   # 진행 상황 추적
kubectl rollout undo deployment/my-app     # 문제 시 롤백
```

:bulb: 핵심은 **선언형(declarative)** 이다. 사용자는 "이렇게 만들어라"가 아니라 **"이런 상태이길 원한다"(replicas: 3, image: v2)** 를 선언하고, 쿠버네티스가 현재 상태를 그 목표로 **수렴**시킨다. ECS도 task/service로 개념은 유사하고, Beanstalk은 이 모든 과정을 한 번 더 감싸 `eb deploy` 한 번으로 끝낸다.
{: .notice--info}

---

# [05] 그래서 무엇을 고를까

| 상황 | 추천 |
|---|---|
| 쿠버네티스/컨테이너를 잘 모르고, 전통 웹앱을 빨리 올리고 싶다 | **Elastic Beanstalk** |
| AWS 안에서만 컨테이너를 굴리고, K8s 운영 부담은 피하고 싶다 | **ECS** (+ 노드 관리 싫으면 Fargate) |
| 멀티클라우드·이식성·헬름/오퍼레이터 등 표준 K8s 생태계가 필요하다 | **EKS** |
| 노드(서버)를 아예 안 보고 싶다 | **Fargate** (ECS/EKS 공통) |

:warning: "남들이 EKS 쓰니까 우리도" 는 흔한 함정이다. 쿠버네티스는 **운영 복잡도와 컨트롤 플레인 비용**을 동반한다. 단일 AWS 환경에서 컨테이너 몇 개만 굴린다면 ECS(Fargate)가 더 싸고 단순한 경우가 많다.
{: .notice--warning}

---

# [06] 핵심 요약

| # | 요약 |
|---|------|
| 1 | **Beanstalk**=애플리케이션 배포 플랫폼, **ECS**=AWS 자체 오케스트레이터, **EKS**=관리형 표준 쿠버네티스 |
| 2 | 셋 다 엄밀히는 IaaS와 PaaS 사이의 **CaaS** — Beanstalk이 PaaS에 가장 근접 |
| 3 | ECS·EKS는 **실행 방식**에 따라 위치가 이동 — Fargate면 PaaS/서버리스 쪽, EC2/자체노드면 IaaS 쪽 |
| 4 | EKS 이식성 ⬆ (표준 K8s API), ECS·Beanstalk은 AWS 종속 ⬆ |
| 5 | Pod 배포 7단계: **빌드 → ECR push → 매니페스트 → `kubectl apply` → 스케줄러 배치 → Service 노출 → 스케일/롤링업데이트** |
| 6 | 쿠버네티스의 본질은 **선언형** — "원하는 상태"를 선언하면 시스템이 그 상태로 수렴시킨다 |

:bulb: 선택 기준 한 줄 — **빠른 배포는 Beanstalk, AWS 전용 컨테이너는 ECS, 표준 쿠버네티스 생태계가 필요하면 EKS.**
{: .notice--info}
