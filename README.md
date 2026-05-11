# 🧠 Second Brain Skill

> *把 AI Agent 变成你的第二大脑——自动将碎片信息转化为结构化的 Obsidian 知识库。*

[![Hermes Agent](https://img.shields.io/badge/Hermes-Agent%20Skill-blueviolet)](https://github.com/neolaf2/hermes)
[![Obsidian](https://img.shields.io/badge/Obsidian-Compatible-7C3AED)](https://obsidian.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 这是什么

**Second Brain** 是一个专为 Hermes Agent 设计的 Skill——让你的 AI Agent 充当你的**知识架构师**，把碎片信息变成永久的、可检索的、互联的知识网络。

## 核心能力

| 能力 | 说明 |
|------|------|
| **知识录入** | 输入任何碎片信息 → 自动去噪、建模、生成 Obsidian 笔记 |
| **智能检索** | 基于知识库回答问题，关联展开，同步更新知识库 |
| **知识维护** | lint 检查、索引重建、图谱优化 |

## 效果预览

**你输入：**

> 今天和张三讨论新项目架构。决定用微服务，后端 Go，前端 React。

**自动生成的笔记：**

```markdown
---
tags:
  - #programming
  - #architecture
  - #meeting-note
date: 2026-05-11
type: meeting-note
---

# 新项目架构讨论

## 核心决议
- 采用 [[微服务架构]]
- 后端：[[Go]]
```

然后用 Obsidian 打开知识库目录，就能看到完整的双向链接知识图谱。

## 知识库结构

```
~/Documents/second-brain/
├── meetings/         # 会议记录
├── readings/         # 阅读笔记
├── ideas/            # 灵感
├── insights/         # 行业洞察
├── technical/        # 技术笔记
├── people/           # 人物笔记
├── concepts/         # 概念解释
├── inbox/            # 待整理
├── logs/             # 操作日志
└── .index.md         # 自动维护的索引
```

直接用 Obsidian 打开这个目录即可。

## 安装

### 方式一：Hermes Agent 用户

```bash
# 克隆到 Hermes skills 目录
git clone https://github.com/Detachment5879/second-brain ~/.hermes/skills/second-brain

# 设置知识库路径（可选，默认 ~/Documents/second-brain）
echo 'OBSIDIAN_VAULT_PATH="$HOME/Documents/my-brain"' >> ~/.hermes/.env
```

### 方式二：其他 AI Agent（Claude Code / OpenCode 等）

本 Skill 的核心是 `SKILL.md` 中的提示词。你可以把 `SKILL.md` 的内容作为 System Prompt 给任何 AI Agent 使用：

```bash
# 直接引用 SKILL.md 作为提示词
cat SKILL.md | your-cli-agent --prompt-stdin
```

## 使用

```
@brain 今天和张三讨论了项目架构，决定用微服务...

@brain 查一下微服务相关的内容

@brain maintain
```

## 文件结构

```
second-brain/
├── SKILL.md                      # Hermes Agent Skill 核心提示词
├── scripts/
│   └── second-brain-writer.py    # Obsidian 知识库写入工具
├── README.md                     # 本文件
└── LICENSE                       # MIT
```

## 原理

```
用户输入碎片信息
    ↓
AI Agent + Second Brain 提示词
    ↓  判断类型 → 提取实体 → 建模标签 → 生成笔记
    ↓
second-brain-writer.py 写入文件
    ↓
Obsidian Vault（本地 Markdown 文件）
    ↓
后续查询 → 检索知识库 → 关联展开 → 综合回答
```

## License

MIT
