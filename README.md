# 🧠 Second Brain · 第二大脑

> *把 AI Agent 变成你的第二大脑——碎片信息自动转化为结构化 Obsidian 知识网络。*

[![Hermes Agent](https://img.shields.io/badge/Hermes-Agent%20Skill-blueviolet)](https://github.com/neolaf2/hermes)
[![Obsidian](https://img.shields.io/badge/Obsidian-Compatible-7C3AED)](https://obsidian.md)
[![Chinese](https://img.shields.io/badge/文档-中文-red)](README.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 是什么

Second Brain 是 Hermes Agent 的知识管理中枢。你和 AI 聊完天、读完文章、开完会——它自动把有价值的内容提炼成永久笔记，存入你的 Obsidian 知识库。**理论/案例二分，双向链接，随时检索。**

## 能力矩阵

| 模式 | 触发 | 做什么 |
|------|------|--------|
| 📥 **知识录入** | `@brain` + 内容/文件/链接 | 碎片信息 → 去噪 → 建模 → Obsidian 笔记 |
| 💬 **对话存档** | `@brain save` | 分析整段对话 → 价值审查 → 理论/案例分类存入 |
| 🔍 **智能检索** | 提问时自动 | 搜索知识库 → 关联展开 → 综合回答 |
| 🛠 **知识维护** | `@brain maintain` | 坏链检查、索引重建、孤立笔记清理 |

## 核心设计

### 价值审查（不什么都存）

存入前三条标准过滤：

| 标准 | 通过 | 不通过 |
|------|------|--------|
| 新颖性 | 新概念、新发现 | 反复聊的老话题 |
| 可复用性 | 以后还会用到 | 一次性操作指令 |
| 结构化潜力 | 能提炼成要点/原则 | 纯闲聊、情绪表达 |

查重 + 脱敏 + 去噪，展示清单，**用户确认后才写入**。

### 知识库结构

```
D:\知识库\
├── 理论/       ← 概念、原理、框架、方法论
├── 案例/       ← 项目经验、踩坑记录、面试准备
└── meetings/   ← 会议记录（已有，不动）
```

## 快速开始

```bash
# 1. 安装 Skill
# 将 SKILL.md 放入 Hermes Agent 的 skills 目录

# 2. 设置知识库路径（可选，自动探测）
export OBSIDIAN_VAULT_PATH="/mnt/d/知识库"

# 3. 开始使用
@brain 今天和张三讨论了微服务架构，决定后端用Go...
@brain save              # 存档当前对话
@brain 查一下微服务      # 搜索知识库
@brain maintain           # 维护知识库
```

## 扩展模块

| 模块 | 说明 |
|------|------|
| [brain-auto-save](https://github.com/Detachment5879/hermes-agent/tree/main/skills/note-taking/brain-auto-save) | 对话自动存档扩展，对话结束时的价值审查与归档 |
| `second-brain-writer.py` | Obsidian 写入工具（已内置） |

> Second Brain 负责「你主动给我的」，brain-auto-save 负责「聊完天后自动提取的」。两者共用同一知识库。

## 原理

```
用户输入 → AI Agent + Second Brain 提示词
    ↓ 判断类型 → 提取实体 → 建模标签 → 价值审查
    ↓ 用户确认
second-brain-writer.py → Obsidian Vault (.md 文件)
    ↓
后续查询 → 检索知识库 → 关联展开(1-2跳) → 综合回答
```

## 已知限制

- 不能处理纯音频文件
- 旧版 `.ppt` 需先用 `strings` 提取文本
- 网页抓取依赖 curl，复杂页面需 browser 工具

## License

MIT © Detachment5879
