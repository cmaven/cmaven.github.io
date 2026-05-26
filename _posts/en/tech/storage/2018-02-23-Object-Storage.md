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

:bulb: A summary of Object Storage — what it is, why it exists, and how it works under the hood.
{: .notice--info}

# [01] Definition

> A storage system that assigns a unique ID (identifiable by the user or server) to data regardless of its physical location, stores it in a container or bucket, and retrieves it on demand using that ID.

Modern data broadly falls into two categories:

| Type | Description | Examples |
|---|---|---|
| **Structured data** | Classifiable by defined criteria | Student ID, name, age, records |
| **Unstructured data** | Cannot be neatly classified | Large images, videos, logs, backups |

Traditional storage approaches handle structured data well:

- **File system storage** — file-based, hierarchical directories
- **Block storage** — block-based with sectors and tracks

Neither scales cleanly for unstructured data at volume. **Object storage** was designed specifically for this problem.

**Analogy:** Think of a valet parking service. Your car (the data object) is handed off with a receipt (the unique ID). You don't know where the car was parked — and you don't need to. Hand in the receipt and your car comes back.

# [02] Advantages

## 2-1. Scalability

- No need to partition storage volumes
- Holds data regardless of total capacity
- Adding new nodes is horizontal — no structural changes required

## 2-2. Efficiency

- No hierarchical directory system means **no inter-layer bottleneck**
- Metadata is stored alongside each object, enabling rich, fast lookups
- Retrieval is by ID, not by path traversal

## 2-3. Availability

| Feature | Benefit |
|---|---|
| Auto-replication | Data copied across multiple nodes automatically |
| Rolling updates | System stays online during upgrades |
| No single point of failure | Any node can serve a request |

# [03] How It Works (IDA)

## 3-1. IDA — Information Dispersal Algorithm

Object storage systems typically use IDA to distribute data reliably across nodes:

1. **Split** — incoming data is broken into pieces (shards)
2. **Distribute** — shards are sent across local or globally distributed storage nodes over the network
3. **Namespace** — all distributed nodes form a single unified namespace; clients see one logical storage pool

```text
Original Data
     │
     ▼
 [Shard 1] → Node A  (Region: US-East)
 [Shard 2] → Node B  (Region: EU-West)
 [Shard 3] → Node C  (Region: AP-South)
     │
     ▼
 Single Namespace (client sees one bucket)
```

A minimum number of shards is sufficient to reconstruct the original object — you don't need all nodes available simultaneously. This is what gives object storage its high durability.

## 3-2. Comparison with Other Storage Types

| Feature | File Storage | Block Storage | Object Storage |
|---|---|---|---|
| Structure | Hierarchical | Sector/track | Flat namespace |
| Scalability | Limited | Limited | Virtually unlimited |
| Best for | Small files, OS | Databases, VMs | Media, backups, logs |
| Metadata | Directory + name | Minimal | Rich, extensible |
| Access method | Path | Block address | Unique ID / API |

## 3-3. Common Use Cases

- Cloud media hosting (images, videos)
- Backup and archival storage
- Data lake storage (log files, analytics data)
- Static website hosting (S3-compatible buckets)
- AI/ML dataset storage

# [04] Troubleshooting / Things to Watch

:warning: Object storage is **eventually consistent** in some implementations — after a write, there may be a brief window where a read returns stale data. Design applications accordingly.
{: .notice--warning}

- **Large object uploads:** Use multipart upload APIs for files over a few hundred MB to avoid timeout errors.
- **Key naming:** In high-throughput scenarios, prefix keys with random characters to avoid hot-spotting on a single shard partition.
- **Lifecycle policies:** Most object storage platforms support automatic tiering (e.g., move to cold storage after 90 days) — configure these to control costs.

:small_blue_diamond: Reference: [IBM Tech Forum — Object Storage](https://developer.ibm.com/kr/developer-%EA%B8%B0%EC%88%A0-%ED%8F%AC%EB%9F%BC/2017/02/22/%EC%98%A4%EB%B8%8C%EC%A0%9D%ED%8A%B8-%EC%8A%A4%ED%86%A0%EB%A6%AC%EC%A7%80%EB%8A%94-%EB%AC%B4%EC%97%87%EC%9D%B8%EA%B0%80-%EA%B7%B8%EB%A6%AC%EA%B3%A0-%EC%96%B4%EB%96%BB%EA%B2%8C-%EB%8F%99%EC%9E%91/){:target="_blank"}
