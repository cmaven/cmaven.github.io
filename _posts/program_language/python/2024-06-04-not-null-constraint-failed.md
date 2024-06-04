---
title: "장고(Django)에서 Serializer 활용 시, Not null constraint failed 오류"
date: 2024-06-04
categories: Python
tags: [Django, Serializer]
---


:bulb: 장고(Django) 환경에서 Serializer를 활용하여 데이터베이스에 데이터를 입력하려 한다.  
이 때, ForeignKey에 해당하는 값이 NULL로 인식되며 입력이 되지 않는 상황이 발생했다.  
일반적인 해결책은 해당 필드를 NULL이 입력되도록 수정하는 방법이나,  
null=True 대신, ForeignKey가 NULL로 인식되지 않게 하는 방법을 찾아보았다.  
그리고, 왜 이런 현상이 발생했는지 정리한다.  
{: .notice--info}

# [01]  Not NULL constraint failed: client_testclient.host_server_id

## 오류해석  

- Model의 Field가 NOT NULL인데, NULL 값을 입력
- client_testclient.host_server_id
  - client = App 이름
  - testclient = Client App의 models.py에 작성한 table 명
  - host_server = testclient의 필드명
  - id = host_server는 ForeignKey로 다른 테이블의 id 값을 연결

> testclient의 host_server에 입력할 값이 NULL이라 오류 발생

## 일반적인 해결법 = 해당 필드에 `null=True` 추가

- 입력되는 데이터가 `null`일 경우가 있다면, 필드가 null 값을 입력 받을 수 있도록 table 수정

```python
# ex) client/models.py

class HostServer(models.Model):
    address = models.GenericIPAddressField(unique=True, verbose_name='IP Address on Host SErver')

    def __str__(self):
        return self.address
    
class TestClient(models.Model):
    address = models.GenericIPAddressField(null=True, verbose_name='Client IP')
    # host_server = models.ForeignKey(HostServer, on_delete=models.CASCADE)
    host_server = models.ForeignKey(HostServer, null=True, on_delete=models.CASCADE)
```

```shell
# ex) Model 수정사항 적용
# django 프로젝트 폴더 경로에서 실행
python manage.py makemigrations
python manage.py migrate
```  

# [02]  Django Model ForeignKey

- testclient 이름의 table의 host_server 필드는 ForeignKey로 구성
  - 한 테이블의 필드나 컬럼이 다른 테이블의 기본 키(Primary Key)를 참조
  - 주로 일 대 다 (One-to-Many) 관계에서 사용
    - 고객 테이블 (하나) ↔ 주문 테이블(여러 개, 한 고객이 여러 주문을 할 수 있다.)
    - 고객 테이블의 고객ID가 기본키, 주문 테이블에는 이 고객ID를 참조하는 ForeignKey 생성
  - 주요 옵션
    ```python
    # 부모 객체가 삭제될 때, 이를 참조하는 모든 객체의 처리
    # 함께 삭제
    on_delete=models.CASCADE
    # 부모 객체가 삭제되지 않도록 함
    on_delete=models.PROTECT
    # 부모 객체가 삭제되면 이를 참조하는 외래 키를 Null 설정
    on_delete=models.SET_NULL
    # 부모 객체가 삭제되면 외래 키를 특정 값으로 설정
    on_delete=models.SET_DEFAULT

    # Null 값 허용
    null=True

    # 중복 값 허용하지 않음
    unique=True
    ```

- [01]의 구조에서는 TestClient 테이블의 host_server 필드가 HostServer의 ID 값을 참조
  - Django에서는 사용자가 정의하지 않아도 id 필드를 생성하여 index 처럼 활용한다.


# [03]  Django REST Framework의 Serializers 

- `serializers.py`는 Django REST Framework(DRF)에서 활용
  - API 요청과 응답 데이터를 직렬화, 역직렬화하는 모듈
  - 직렬화(serialization)은 데이터 구조를 JSON, XML 등 특정 포맷으로 변환하는 것
  - 역직렬화는 그 반대
  - DRF의 serializer 모듈은 이 작업을 간편하게 수행하도록 함
    - 데이터베이스 모델에서 데이터를 가져오거나, 저장할 때, 데이터 유효성 검사
- `class Meta:`
  - 테이블 메타데이터 정의
    - 직렬화할 모델/필드, 읽기 전용 필드 등을 지정  
    - extra_kwargs로, default 값, 읽기전용 필드를 제외하고 DB 객체를 생성하고 저장할 수 있음

    ```python
    # models.py
    from django.db import models

    class MyModel(models.Model):
        name = models.CharField(max_length=100)
        age = models.IntegerField()
        address = models.CharField(max_length=100)
        email = models.EmailField()
        is_active = models.BooleanField(default=True)

    # serializers.py
    from rest_framework import serializers
    from myapp.models import MyModel

    class MyModelSerializer(serializers.ModelSerializer):
        class Meta:
            model = MyModel  # 직렬화할 모델을 지정
            fields = '__all__'  # 모든 필드를 직렬화
            # fields = ['name', 'age']  # 특정 필드만 직렬화
            read_only_fields = ['age']  # 읽기 전용 필드를 지정
            extra_kwargs = {  # 추가 설정을 지정                    
            'name': {'required': True},  # name 필드를 필수로 설정
            'address': {'read_only': True},  # age 필드를 읽기 전용으로 설정
            'email': {'write_only': True},  # email 필드를 쓰기 전용으로 설정
            'is_active': {'default': False},  # is_active 필드의 기본값을 False로 설정
        }

    # views.py 에서 사용 예
    data = {
      'name': 'John Doe',
      'email': 'john@example.com'
    }

    serializer = MyModelSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
        print(instance)
    else:
        print(serializer.errors)
    ```  

- `serializers.SerializerMethodField()`
  - 특정 필드를 사용자 정의 방식으로 직렬화하려는 경우 사용
  - 읽기 전용 필드를 정의하는데 사용
    - `User` 모델에 대한 시리얼라이저에서 `full_name`이라는 추가 필드를 생성하고
      - 이 필드는 `User`모델의 `first_name`과 `last_name`을 결합하여 데이터를 생성  
  - `get_필드명(self, obj)` 함수를 활용하여, 
    - `SerializerMethodField()`을 사용할 때 필드의 값 반환 메소드 정의
    - 필드명 부분은 SerializerMethodField로 정의한 필드의 이름과 일치해야함  

    ```python
    '''
    User 모델에 대한 Serializer에 `full_name`이라는 추가 필드를 생성
    이 필드는 User모델의 first_name과 last_name을 결합하여 데이터를 생성
    '''

    # serializers.py
    from rest_framework import serializers
    from django.contrib.auth.models import User

    class UserSerializer(serializers.ModelSerializer):
        full_name = serializers.SerializerMethodField()

        class Meta:
            model = User
            fields = ['username', 'email', 'full_name']

        def get_full_name(self, obj):
            return f'{obj.first_name} {obj.last_name}'
    ```  

- `serializers.PrimaryKeyRelatedField()`
  - 테이블 메타데이터 정의
    - 직렬화할 모델/필드, 읽기 전용 필드 등을 지정  

    ```python
    # models.py
    ```  


# [04]  Serializer를 활용할 때, Not NULL constraint failed 오류 이유

## TestClientSerializer의 잘못된 구성  

- host_server 필드를 읽어올 때 HostServer의 address 필드를 읽어오도록 구성
- host_server를 그냥 읽게 되면, HostServer 테이블에 저장된 값의 id 값을 출력
  - 따라서, 이를 address 값으로 변경하여 사용자 이해를 높이고자 하였음

  > 단, 위에서 살펴보았듯이 SerializerMethodField()로 필드 데이터를 수정하였을 경우,  
  > 이는 "읽기전용"이다.  
  > 따라서, 해당 값을 views.py에서 입력하려하면 오류가 발생함.(Null 값)

  ```python
  # client/models.py

  class HostServer(models.Model):
      address = models.GenericIPAddressField(unique=True, verbose_name='IP Address on Host SErver')


  class TestClient(models.Model):
      address = models.GenericIPAddressField(null=True, verbose_name='Client IP')
      host_server = models.ForeignKey(HostServer, on_delete=models.CASCADE)


  # client/serializers.py
  from rest_framework import serializers
  from .models import HostServer, Testclient

  class HostServerSerializer(serializers.ModelSerializer):
      class Meta:
          model = HostServer
          fields = ['address']


  class TestClientSerializer(serializers.ModelSerializer):
      host_server = serializers.SerializerMethodField()
      
      class Meta:
          model = TestClient
          fields = '__all__'

      def get_host_server(self, obj):
          return obj.host_server.address

  # client/views.py
  
  ```

## 오류 수정

- 위에서 원했던, 데이터를 읽을 때 id 값이 아닌 address 데이터가 출력되어야 한다면
  - model에 __str__ 함수를 활용하는 것이 좋음
  - 그리고, Serializer에서는 SerializerMethodField() 관련 코드를 삭제

  ```python
  # client/models.py

  class HostServer(models.Model):
      address = models.GenericIPAddressField(unique=True, verbose_name='IP Address on Host SErver')

      def __str__(self):
        return self.address

  class TestClient(models.Model):
      address = models.GenericIPAddressField(null=True, verbose_name='Client IP')
      host_server = models.ForeignKey(HostServer, on_delete=models.CASCADE)


  # client/serializers.py
  from rest_framework import serializers
  from .models import HostServer, Testclient

  class HostServerSerializer(serializers.ModelSerializer):
      class Meta:
          model = HostServer
          fields = ['address']
          

  class TestClientSerializer(serializers.ModelSerializer):
      class Meta:
          model = TestClient
          fields = '__all__'
  ```

