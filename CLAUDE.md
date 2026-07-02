# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is the **AI System Engineer Curriculum（AI 系统工程师完整培养计划）** — a structured, project-driven learning roadmap spanning 5 layers from software engineering fundamentals to production AI infrastructure. It is a documentation/curriculum repository, not a runnable code project.

`main.py` is a PyCharm placeholder and not part of the curriculum.

## Curriculum architecture

The 5-layer progression (each layer builds on the prior one):

```
Layer 1: Software Engineering → Layer 2: Backend Engineering → Layer 3: AI Engineering → Layer 4: AI Infrastructure → Layer 5: Architecture & Career
```

| Layer | Focus | Key topics |
|-------|-------|-----------|
| 1 — Software Engineering | Foundation | Python (advanced, OOP, typing, asyncio), Git, Linux, Docker, Network |
| 2 — Backend Engineering | Serve AI | FastAPI, Database (Postgres/Redis/Mongo), Message Queue, Object Storage, Search |
| 3 — AI Engineering | Core AI | LLM, RAG, Agent, MCP, AI Product, Evaluation |
| 4 — AI Infrastructure | Deploy at scale | GPU/CUDA, Inference (vLLM/SGLang), Kubernetes, Monitoring, CI/CD, Cloud |
| 5 — Architecture & Career | Senior-level | System design, Open source contribution, Source code reading, English, Career |

## File organization

All curriculum content lives in `Learning objectives/` as individual Markdown files. The index/roadmap is `AI_System_Engineer_Curriculum.md`. Topic files follow the naming pattern `<layer>.<number> <Topic>.md` (e.g., `3.1 LLM.md`, `1.1 Python高级.md`).

Each topic file follows a consistent structure:
- **Target/goal** at the top
- **Required knowledge** broken into sub-topics (each rated ★★★★★)
- **Hands-on project** for each sub-topic (labeled "必做项目")
- **Capstone project** at the end (labeled "综合毕业项目") with graduation criteria

## How to use this repo

- Follow layers sequentially — each layer's projects assume competence in prior layers.
- Every topic has mandatory hands-on projects. The curriculum is project-driven, not read-only.
- Cross-cutting skills apply throughout: math/AI fundamentals, engineering discipline, English reading (official docs, RFCs, papers), source code reading, and writing/teaching output.