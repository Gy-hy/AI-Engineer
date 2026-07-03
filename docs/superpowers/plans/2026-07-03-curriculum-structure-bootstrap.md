# Curriculum Structure Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在仓库中落地方案 C 的基础目录骨架与最小占位文件，为后续 MkDocs 接入和内容迁移建立稳定结构。

**Architecture:** 保留现有 `Learning objectives/` 作为过渡内容，不做迁移；新增中文目录结构 `内容/`、`项目/`、`共享/` 及最小主题样板，用少量索引文件明确目录职责。所有占位文件保持轻量，仅说明用途与后续填充方向。

**Tech Stack:** Markdown, repository file structure

---

### Task 1: 创建顶层目录骨架

**Files:**
- Create: `内容/指南/README.md`
- Create: `内容/主题/README.md`
- Create: `项目/README.md`
- Create: `共享/README.md`

- [ ] **Step 1: 创建 `内容/指南/README.md`**

```md
# 指南

本目录用于承载面向读者的聚合页与入口页，例如：

- 课程总览
- 学习路径
- 习题索引
- 项目索引
- FAQ
- 贡献指南

该目录中的内容优先服务于“阅读视角”，用于组织课程网站导航与对外展示入口。
```

- [ ] **Step 2: 创建 `内容/主题/README.md`**

```md
# 主题

本目录用于承载课程主体内容。

内容按 Layer 与主题单元组织。

主题单元是最小维护单位，推荐包含：

- 01 学习目标.md
- 02 教程.md
- 03 习题.md
- 04 答案.md
- 资源/
- 示例代码/

后续每个主题目录都应尽量遵循统一结构，以便多人协作维护。
```

- [ ] **Step 3: 创建 `项目/README.md`**

```md
# 项目

本目录用于存放跨多个主题的大项目、阶段项目与综合项目。

组织原则：

- 小示例代码跟主题走
- 大项目统一放在本目录

每个项目后续建议至少包含：

- README.md
- 文档/
- 代码目录
- 部署说明（如适用）
```

- [ ] **Step 4: 创建 `共享/README.md`**

```md
# 共享

本目录用于存放可被多个主题复用的公共资源，例如：

- 通用图片
- 模板
- 可复用片段

如果某项资源只服务于单个主题，应优先放在该主题自己的 `资源/` 目录中。
```

- [ ] **Step 5: 验证目录骨架已建立**

Run: `find '/Volumes/MiniHy/code/AI Engineer' -maxdepth 2 -type d | sort`
Expected: 输出中包含 `内容`、`内容/指南`、`内容/主题`、`项目`、`共享`

### Task 2: 创建最小指南页占位文件

**Files:**
- Create: `内容/指南/课程总览.md`
- Create: `内容/指南/学习路径.md`
- Create: `内容/指南/习题索引.md`
- Create: `内容/指南/项目索引.md`
- Create: `内容/指南/贡献指南.md`

- [ ] **Step 1: 创建 `内容/指南/课程总览.md`**

```md
# 课程总览

本页用于向读者介绍整个课程体系。

后续将包含：

- 五层课程结构
- 学习目标概览
- 阶段项目概览
- 推荐学习方式
```

- [ ] **Step 2: 创建 `内容/指南/学习路径.md`**

```md
# 学习路径

本页用于组织按阶段推进的学习顺序。

后续将包含：

- Layer 1 到 Layer 5 的推进顺序
- 各阶段前置要求
- 阶段项目与综合项目关系
```

- [ ] **Step 3: 创建 `内容/指南/习题索引.md`**

```md
# 习题索引

本页用于汇总所有主题中的习题入口。

后续将按 Layer 与主题整理练习题导航。
```

- [ ] **Step 4: 创建 `内容/指南/项目索引.md`**

```md
# 项目索引

本页用于汇总阶段项目、综合项目与独立大项目。

后续将链接到 `项目/` 目录下的具体项目说明。
```

- [ ] **Step 5: 创建 `内容/指南/贡献指南.md`**

```md
# 贡献指南

本页用于说明多人协作时的内容维护方式。

后续将包含：

- 目录规范
- 命名规范
- 主题单元模板
- 文档提交流程
```

- [ ] **Step 6: 验证指南页已创建**

Run: `find '/Volumes/MiniHy/code/AI Engineer/内容/指南' -maxdepth 1 -type f | sort`
Expected: 输出包含 `README.md` 与 5 个指南页文件

### Task 3: 创建主题层级骨架与样板主题

**Files:**
- Create: `内容/主题/第1层 软件工程/README.md`
- Create: `内容/主题/第2层 后端工程/README.md`
- Create: `内容/主题/第3层 AI工程/README.md`
- Create: `内容/主题/第4层 AI基础设施/README.md`
- Create: `内容/主题/第5层 架构与职业发展/README.md`
- Create: `内容/主题/第3层 AI工程/3.2 RAG/01 学习目标.md`
- Create: `内容/主题/第3层 AI工程/3.2 RAG/02 教程.md`
- Create: `内容/主题/第3层 AI工程/3.2 RAG/03 习题.md`
- Create: `内容/主题/第3层 AI工程/3.2 RAG/04 答案.md`
- Create: `内容/主题/第3层 AI工程/3.2 RAG/资源/README.md`
- Create: `内容/主题/第3层 AI工程/3.2 RAG/示例代码/README.md`

- [ ] **Step 1: 为五个 Layer 创建目录说明页**

每个 README 使用同一简洁结构，例如 `内容/主题/第3层 AI工程/README.md`：

```md
# 第3层 AI工程

本目录用于存放第 3 层的主题单元内容。

后续主题将围绕以下方向展开：

- LLM
- RAG
- Agent
- MCP
- AI Product
- Evaluation
```

其余四层 README 使用同样结构，只替换层级名称与主题方向。

- [ ] **Step 2: 创建样板主题 `3.2 RAG` 的 `01 学习目标.md`**

```md
# 学习目标

本文件用于承载 `3.2 RAG` 主题的学习目标、必学内容、必做项目与毕业标准。

后续内容将从现有 `Learning objectives/3.2 RAG.md` 逐步迁移或整理而来。
```

- [ ] **Step 3: 创建样板主题 `3.2 RAG` 的 `02 教程.md`**

```md
# 教程

本文件用于承载 `3.2 RAG` 的正式教程正文。

后续内容将围绕：

- RAG 基础原理
- 检索链路设计
- 向量库与重排
- 工程实践与项目实现
```

- [ ] **Step 4: 创建样板主题 `3.2 RAG` 的 `03 习题.md`**

```md
# 习题

本文件用于承载 `3.2 RAG` 的练习题。

后续可包含：

- 概念题
- 设计题
- 动手题
- 延伸题
```

- [ ] **Step 5: 创建样板主题 `3.2 RAG` 的 `04 答案.md`**

```md
# 答案

本文件用于承载 `3.2 RAG` 习题的参考答案与讲解。

说明：

- 本文件与教程同仓库维护
- 后续在站点导航中默认弱曝光
```

- [ ] **Step 6: 创建样板主题 `3.2 RAG` 的资源与代码说明页**

`资源/README.md`：

```md
# 资源

本目录用于存放 `3.2 RAG` 主题专属图片、图表、附件等资源。
```

`示例代码/README.md`：

```md
# 示例代码

本目录用于存放 `3.2 RAG` 主题的小示例、小实验与局部实现代码。
```

- [ ] **Step 7: 验证样板主题结构**

Run: `find '/Volumes/MiniHy/code/AI Engineer/内容/主题/第3层 AI工程/3.2 RAG' -maxdepth 2 | sort`
Expected: 输出包含 `01 学习目标.md`、`02 教程.md`、`03 习题.md`、`04 答案.md`、`资源`、`示例代码`

### Task 4: 创建大项目与共享目录占位结构

**Files:**
- Create: `项目/企业知识库/README.md`
- Create: `项目/Agent平台/README.md`
- Create: `共享/模板/README.md`
- Create: `共享/图片/README.md`

- [ ] **Step 1: 创建 `项目/企业知识库/README.md`**

```md
# 企业知识库

这是一个跨多个主题的大项目占位目录。

后续可用于承载：

- 项目说明
- 架构设计
- 实现代码
- 部署说明
```

- [ ] **Step 2: 创建 `项目/Agent平台/README.md`**

```md
# Agent平台

这是一个跨多个主题的大项目占位目录。

后续可用于承载：

- 项目说明
- 多 Agent 架构
- 工具调用与工作流实现
- 部署与观测
```

- [ ] **Step 3: 创建共享子目录说明页**

`共享/模板/README.md`：

```md
# 模板

本目录用于存放可复用的课程模板、文档模板与主题样板。
```

`共享/图片/README.md`：

```md
# 图片

本目录用于存放可跨多个主题复用的通用图片与图示资源。
```

- [ ] **Step 4: 验证项目与共享结构**

Run: `find '/Volumes/MiniHy/code/AI Engineer/项目' '/Volumes/MiniHy/code/AI Engineer/共享' -maxdepth 2 | sort`
Expected: 输出包含 `项目/企业知识库`、`项目/Agent平台`、`共享/模板`、`共享/图片`

### Task 5: 更新 README 的当前结构示例

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 更新 README 中的“目录结构”与现状说明**

将 README 中“当前仓库仍处于早期整理阶段，现状如下”一节的示例树更新为包含新增目录的实际现状，保留 `Learning objectives/` 的过渡说明。

- [ ] **Step 2: 运行检查**

Run: `sed -n '1,260p' '/Volumes/MiniHy/code/AI Engineer/README.md'`
Expected: README 中同时出现现有 `Learning objectives/` 与新增的 `内容/`、`项目/`、`共享/`

### Task 6: 最终验证

**Files:**
- Verify only

- [ ] **Step 1: 列出最终目录**

Run: `find '/Volumes/MiniHy/code/AI Engineer' -maxdepth 3 | sort`
Expected: 输出包含新增的中文目录骨架与样板文件

- [ ] **Step 2: 手动核对规范一致性**

检查以下要求是否全部满足：

- 使用中文顶层目录
- 主题单元模板已建立
- 答案页存在但只是占位
- 小示例代码目录跟主题走
- 大项目目录独立存在
- `Learning objectives/` 仍保留，未被强制迁移
