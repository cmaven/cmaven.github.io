---
title: "Fixing the Django Serializer Not null constraint failed Error"
description: "Cause and fix for the Not null constraint failed error in a Django Serializer where a ForeignKey value is treated as NULL."
excerpt: "Cause and fix for the Not null constraint failed error in a Django Serializer where a ForeignKey value is treated as NULL."
date: 2024-06-04
last_modified_at: 2026-05-26
categories: Python
tags: [Django, Serializer]
ref: not-null-constraint-failed
---


:bulb: I was trying to insert data into the database via a Django Serializer.
The value bound to a ForeignKey was being treated as NULL, so the insert failed.
The usual fix is to allow the field to accept NULL, but here I went a step further and looked at how to keep the ForeignKey from being interpreted as NULL in the first place — and explain why this happens.
{: .notice--info}

# [01] Not NULL constraint failed: client_testclient.host_server_id

## Reading the error

- The model field is NOT NULL but a NULL value was inserted
- client_testclient.host_server_id
  - client = the app name
  - testclient = the table name defined in the client app's `models.py`
  - host_server = the field on testclient
  - id = host_server is a ForeignKey referencing another table's id

> The value to be inserted into testclient.host_server is NULL, hence the error.

## Common fix — add `null=True` to the field

- If incoming data can legitimately be `null`, modify the table so the field accepts NULL.

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
# ex) Apply the model changes
# Run inside the Django project folder
python manage.py makemigrations
python manage.py migrate
```  

# [02] Django Model ForeignKey

- The `host_server` field on the `testclient` table is a ForeignKey
  - A field/column on one table references the primary key of another table
  - Typically used for one-to-many relationships
    - Customer table (one) ↔ Order table (many — one customer can have many orders)
    - The customer ID is the primary key on the customer table; the order table holds a ForeignKey referencing it
  - Common options
    ```python
    # Behavior for objects referencing a parent that is deleted
    # Delete together
    on_delete=models.CASCADE
    # Prevent deletion of the parent
    on_delete=models.PROTECT
    # Set referencing foreign keys to NULL when the parent is deleted
    on_delete=models.SET_NULL
    # Set the foreign key to a specific value when the parent is deleted
    on_delete=models.SET_DEFAULT

    # Allow NULL
    null=True

    # Disallow duplicates
    unique=True
    ```

- In the structure in [01], the `host_server` field on TestClient references the ID of HostServer
  - In Django, even if you don't define one, an `id` field is auto-generated and used like an index.


# [03] Serializers in Django REST Framework

- `serializers.py` is used by Django REST Framework (DRF)
  - A module for serializing and deserializing API request and response data
  - Serialization converts data structures into formats like JSON or XML
  - Deserialization is the reverse
  - DRF's serializer module makes this convenient
    - It also validates data when reading from or saving to database models
- `class Meta:`
  - Defines table metadata
    - Specifies which model/fields to serialize, read-only fields, and so on
    - With `extra_kwargs`, you can set defaults, mark fields read-only, etc., so you can create/save DB objects without those fields

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
            model = MyModel  # The model to serialize
            fields = '__all__'  # Serialize all fields
            # fields = ['name', 'age']  # Serialize specific fields only
            read_only_fields = ['age']  # Mark fields as read-only
            extra_kwargs = {  # Extra settings                    
            'name': {'required': True},  # Make the name field required
            'address': {'read_only': True},  # Make address read-only
            'email': {'write_only': True},  # Make email write-only
            'is_active': {'default': False},  # Default is_active to False
        }

    # Example usage in views.py
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
  - Use when you want to serialize a particular field with custom logic
  - Used to define read-only fields
    - On a serializer for the `User` model, you might add a `full_name` field
      - that combines `first_name` and `last_name` from the User model
  - Use the `get_<field_name>(self, obj)` method
    - to define how the `SerializerMethodField()` value is computed
    - the field name part must match the field name declared as `SerializerMethodField`

    ```python
    '''
    Add a `full_name` field to the User model's serializer.
    It combines first_name and last_name from the User model.
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
  - Defines table metadata
    - Specifies which model/fields to serialize, read-only fields, and so on

    ```python
    # models.py
    ```  


# [04] Why the Not NULL constraint failed error happens when using Serializers

## Incorrect TestClientSerializer

- We wanted reading `host_server` to return the `address` from HostServer
- Reading `host_server` directly would return the id stored in HostServer
  - So we changed it to expose the address for better readability

  > However, as shown above, if you remap a field via `SerializerMethodField()`,
  > that field becomes **read-only**.
  > So when `views.py` tries to write to it, it errors out (NULL).

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

## Fix

- If you want reads to surface the `address` instead of the id,
  - it's better to use the model's `__str__` method
  - and remove the `SerializerMethodField()` code from the serializer.

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

