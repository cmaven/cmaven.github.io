---
title: "Object Storage"
description: "Concept of object storage, its advantages (scalability/efficiency/availability), and how IDA distributed storage works"
excerpt: "Object storage concept and operation, suited for unstructured data"
date: 2018-02-23
last_modified_at: 2026-05-26
categories: Storage
tags: [Object-Storage, storage, IDA, unstructured-data, distributed-storage, cloud-storage]
ref: object-storage
---

:bulb: A summary of Object Storage.
{: .notice--info}

# [01] Definition

> A storage system that assigns a unique ID (identifiable by the user or server) to data regardless of its physical location, stores it in a container or bucket, and retrieves it on demand using that ID.

- Modern data is split into **structured data** (classifiable by some criteria: student ID, name, age, etc.) and **unstructured data** (typically large images, videos, etc.) that can't be neatly classified.
- Existing storage methods — file systems (file-based, hierarchical) and block storage (block-based with sectors/tracks) — suit structured data. **Object storage** suits unstructured data.
- Analogy: a valet parking service. If the data object is your car, the unique ID is your receipt. You hand over the receipt and you get your car back — you don't have to know where it was parked.

# [02] Advantages

## 2-1. Scalability
- No need to partition
- Holds data regardless of capacity

## 2-2. Efficiency
- No hierarchical directory system → no inter-layer bottleneck

## 2-3. Availability
- Auto-replication and rolling updates supported
- No downtime

# [03] How It Works (IDA)

## 3-1. IDA (Information Dispersal Algorithm)
- Splits data into pieces
- Distributes pieces across local or globally distributed storage nodes over the network
- The distributed nodes form a single namespace storage

:small_blue_diamond: Reference: [IBM Tech Forum — Object Storage](https://developer.ibm.com/kr/developer-%EA%B8%B0%EC%88%A0-%ED%8F%AC%EB%9F%BC/2017/02/22/%EC%98%A4%EB%B8%8C%EC%A0%9D%ED%8A%B8-%EC%8A%A4%ED%86%A0%EB%A6%AC%EC%A7%80%EB%8A%94-%EB%AC%B4%EC%97%87%EC%9D%B8%EA%B0%80-%EA%B7%B8%EB%A6%AC%EA%B3%A0-%EC%96%B4%EB%96%BB%EA%B2%8C-%EB%8F%99%EC%9E%91/){:target="_blank"}
