# AI System Engineer Ultimate Roadmap（2026）

整个 Roadmap 分成五层。

```
Layer 1
Software Engineering

↓

Layer 2
Backend Engineering

↓

Layer 3
AI Engineering

↓

Layer 4
AI Infrastructure

↓

Layer 5
Architecture & Career
```

为什么？

因为所有 AI 产品都是这样构成的。

---

# Layer 1 Software Engineering

★★★★★

这是根。

## Python

★★★★★

必须：

* Python高级
* OOP
* typing
* asyncio
* Context Manager
* Decorator
* Generator
* Logging
* Packaging
* Testing
* Performance

---

## Git

★★★★★

必须：

```
Branch
Merge
Rebase
Cherry Pick
Tag
Release
Fork Workflow
PR
Conflict
```

---

## Linux

★★★★★

必须：

```
Shell

SSH

tmux

systemd

journalctl

grep

sed

awk

权限

网络

CPU

Memory
```

---

## Docker

★★★★★

```
Dockerfile

Compose

Network

Volume

GPU

Registry
```

---

## Network

★★★★★

```
HTTP

HTTPS

REST

WebSocket

SSE

JWT

OAuth

Nginx
```

---

## 第一阶段项目

必须：

```
Python CLI

↓

FastAPI API

↓

Docker部署

↓

CI
```

---

# Layer 2 Backend Engineering

★★★★★

为什么第二层？

因为：

Agent

RAG

MCP

都需要后端。

---

## FastAPI

★★★★★

包括：

Streaming

Middleware

DI

Background

WebSocket

Upload

OpenAPI

---

## Database

★★★★★

SQL

Postgres

SQLite

Redis

MongoDB

---

## Message Queue

★★★★★

Kafka

RabbitMQ

Redis Stream

Celery

---

## Object Storage

★★★★★

S3

MinIO

OSS

---

## Search

ElasticSearch

OpenSearch

---

## 第二阶段项目

```
AI Chat Backend
```

要求：

支持：

```
登录

JWT

聊天

Streaming

Redis

Postgres

文件上传

Docker

WebSocket
```

---

# Layer 3 AI Engineering

★★★★★

整个路线最核心。

分六块。

---

## 3.1 LLM

★★★★★

必须：

Prompt

Structured Output

Function Calling

Tool Calling

Streaming

Memory

Reasoning

Context

Cost

Latency

Model Routing

---

## 3.2 RAG

★★★★★

Embedding

Chunk

Retriever

Hybrid Search

Rerank

Citation

Evaluation

Vector Database

GraphRAG

Agentic RAG

Knowledge Graph

---

## 3.3 Agent

★★★★★

Planning

Reflection

Memory

Workflow

Task

State

Scheduler

Executor

Hierarchy

Multi Agent

Deep Research

Browser Agent

Computer Use

Coding Agent

A2A

---

## 3.4 MCP

★★★★★

Client

Server

Tool

Prompt

Resource

Transport

Gateway

Registry

Security

---

## 3.5 AI Product

★★★★★

聊天

知识库

Workspace

Memory

Plugin

Multi User

Permission

同步

Version

UX

---

## 3.6 Evaluation

★★★★★

Prompt Eval

RAG Eval

Agent Eval

Benchmark

A/B Test

Tracing

Observability

---

## 第三阶段项目

按顺序：

```
ChatGPT Clone

↓

Knowledge Base

↓

Agent

↓

Browser Agent

↓

Computer Agent

↓

MCP Server

↓

AI Companion
```

---

# Layer 4 AI Infrastructure

★★★★★

这是未来最值钱的一层。

很多人不会。

---

## GPU

★★★★★

CUDA

VRAM

Tensor Parallel

Batch

Quantization

KV Cache

Speculative Decoding

---

## Inference

★★★★★

vLLM

SGLang

Ollama

Triton

LiteLLM

OpenRouter

Model Gateway

Prompt Cache

---

## Kubernetes

★★★★★

Pod

Deployment

Ingress

Service

Helm

Autoscaling

---

## Monitoring

★★★★★

Prometheus

Grafana

OpenTelemetry

Langfuse

LangSmith

Sentry

---

## CI/CD

★★★★★

GitHub Actions

GitLab CI

Docker Registry

Release

Deploy

---

## Cloud

★★★★☆

AWS

Azure

Google Cloud

阿里云

腾讯云

---

## 第四阶段项目

```
AI Gateway

↓

GPU Deployment

↓

Monitoring

↓

Kubernetes

↓

Production
```

---

# Layer 5 Architecture & Career

★★★★★

最后一层。

真正拉开人与人的差距。

---

## Architecture

★★★★★

SOLID

Clean Architecture

DDD

Hexagonal

Microservice

Monolith

Event Driven

CQRS

Scaling

Caching

Security

Rate Limit

HA

Cost

---

## Open Source

★★★★★

GitHub

Issue

PR

Release

Roadmap

Docs

---

## Source Code Reading

★★★★★

必须：

FastAPI

LangGraph

LiteLLM

vLLM

SGLang

OpenHands

OpenWebUI

Continue

Qdrant

---

## English

★★★★★

官方文档

RFC

Paper

GitHub

Blog

---

## Career

★★★★★

Blog

Resume

Portfolio

Tech Talk

System Design

Interview

Leadership

---

## 最终项目

也是唯一的大项目。

```
AI Companion Platform
```

包含：

```
聊天

Agent

RAG

MCP

A2A

Browser

Computer

Coding

Workflow

Memory

Knowledge

Search

Multi Agent

Workspace

Plugin

AI Gateway

Deployment

Monitoring

Dashboard

Docker

Kubernetes

CI/CD
```

---

# 最终学习路线（唯一版本）

```
Software Engineering
        │
        ▼
Backend Engineering
        │
        ▼
LLM
        │
        ▼
RAG
        │
        ▼
Agent
        │
        ▼
MCP
        │
        ▼
AI Product
        │
        ▼
AI Infrastructure
        │
        ▼
Architecture
        │
        ▼
Open Source
        │
        ▼
AI Companion Platform
```

---

# 我认为还应该增加一条贯穿全程的主线（这是前面所有版本都没有完整表达的）

如果你的目标是 **Senior AI System Engineer**，那么除了技术层级之外，还要有一条**横向能力主线**，它贯穿五个 Layer：

| 横向能力          | 为什么必须掌握                                                               |
| ------------- | --------------------------------------------------------------------- |
| **数学与 AI 基础** | 不需要重新系统学高数，但要理解 Transformer、Embedding、Attention、向量检索等核心原理，能够解释而不是背公式。 |
| **工程规范**      | 代码风格、测试、文档、版本管理、CI/CD，从第一天开始执行。                                       |
| **英文阅读**      | 官方文档、RFC、GitHub Discussions、Issue、Paper 是第一手信息来源。                     |
| **源码阅读**      | 每进入一个新领域，都至少阅读一个优秀开源项目的源码。                                            |
| **输出能力**      | 写博客、整理文档、录 Demo、维护 README，把知识沉淀下来。                                    |

---

## 这就是我愿意长期和你一起执行的最终版本。

我甚至建议我们不要把它称为 **Roadmap**，而叫：

> **AI System Engineer Curriculum（AI 系统工程师完整培养计划）**

因为它已经不是一张学习路线图，而是一套从入门到高级、从工程能力到 AI 产品、从部署到职业发展的完整培养体系。只要持续按照它推进，并把每个阶段的项目真正做出来，你就不仅是在学习技术，而是在逐步构建一份能够证明自己能力的长期工程资产。
