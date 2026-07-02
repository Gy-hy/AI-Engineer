# AI System Engineer Curriculum

AI 系统工程师完整培养计划 — 从 Python 基础到生产级 AI 基础设施的工程化学习路线。

## 五层架构

```
Layer 1: Software Engineering → Python · Git · Linux · Docker · Network
Layer 2: Backend Engineering   → FastAPI · Database · MQ · Object Storage · Search
Layer 3: AI Engineering        → LLM · RAG · Agent · MCP · AI Product · Evaluation
Layer 4: AI Infrastructure     → GPU · Inference · K8s · Monitoring · CI/CD · Cloud
Layer 5: Architecture & Career → System Design · Open Source · Source Reading · English
```

每一层都包含**学习要点**、**必做项目**和**综合毕业项目**，完成后进入下一层。

## 快速开始

```bash
git clone https://github.com/Gy-hy/AI-Engineer.git
cd AI-Engineer

# 创建虚拟环境（需要 Python 3.12）
uv venv ai-engineer --python 3.12
source ai-engineer/bin/activate
uv pip install -r requirements.txt
```

## 目录结构

```
.
├── CLAUDE.md                                    # Claude Code 指引
├── requirements.txt                             # Python 开发依赖
├── Learning objectives/
│   ├── AI_System_Engineer_Curriculum.md         # 总纲 Roadmap
│   ├── 1.1 Python高级.md                        # Layer 1 各模块
│   ├── 1.2 Git.md
│   ├── ...
│   └── 5.5 Career.md                            # Layer 5 各模块
└── main.py                                      # 占位文件，非课程内容
```

## 学习方式

1. 从 `AI_System_Engineer_Curriculum.md` 开始，建立全局认知
2. 按层级顺序推进，不要跳层
3. 每个模块的「必做项目」必须动手完成
4. 每个阶段结束完成「综合毕业项目」再进入下一层

## 目标岗位

**Senior AI System Engineer** — 能够独立设计、开发、部署完整 AI 产品的工程师。