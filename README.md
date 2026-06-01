# 🧠 Second Brain · 第二大脑

> *把 AI Agent 变成你的第二大脑——碎片信息自动转化为结构化 Obsidian 知识网络。*

[![Hermes Agent](https://img.shields.io/badge/Hermes-Agent%20Skill-blueviolet)](https://github.com/neolaf2/hermes)
[![Obsidian](https://img.shields.io/badge/Obsidian-Compatible-7C3AED)](https://obsidian.md)
[![Chinese](https://img.shields.io/badge/文档-中文-red)](README.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 是什么

Second Brain 是 Hermes Agent 的知识管理中枢。你和 AI 聊完天、读完文章、开完会——它自动把有价值的内容提炼成永久笔记，存入你的 Obsidian 知识库。**理论/案例二分，双向链接，智能评分，定时复习推送。**

## 模块体系

```
second-brain/          ← 主脑：知识录入 + 查询 + 维护
brain-auto-save/       ← 副脑：对话自动存档 + 价值审查
brain-enhance/         ← 增强：间隔复习 + 知识合成 + 评分 + 飞书推送
```

## 能力矩阵

| 命令 | 模块 | 做什么 |
|------|------|--------|
| `@brain` + 内容/文件/链接 | 主脑 | 碎片信息 → 去噪 → 建模 → Obsidian 笔记 |
| `@brain save` | 副脑 | 分析对话 → 价值审查 → 理论/案例分类存入 |
| `@brain review` | 增强 | 抽高优先级旧笔记推送复习 |
| **自动** | 增强 | **被动 RAG：提问时自动检索知识库，注入相关笔记** |
| `@brain connect` | 增强 | 扫描关联笔记簇 → AI 合成综合笔记 |
| `@brain score [笔记] [1-5]` | 增强 | 修改笔记优先级评分 |
| `@brain stats` | 增强 | 知识增长仪表盘 |
| `@brain feishu on\|off` | 增强 | 飞书每晚 8 点自动推送复习卡片 |
| `@brain maintain` | 主脑 | 坏链检查、索引重建、孤立笔记清理 |
| 自然提问 | 主脑 | 搜索知识库 → 关联展开 → 综合回答 |

## 核心设计

### 价值审查（不什么都存）

| 标准 | 通过 | 不通过 |
|------|------|--------|
| 新颖性 | 新概念、新发现 | 反复聊的老话题 |
| 可复用性 | 以后还会用到 | 一次性操作指令 |
| 结构化潜力 | 能提炼成要点/原则 | 纯闲聊、情绪表达 |

查重 + 脱敏 + 去噪 → 展示清单 → **用户确认后才写入**。

### 间隔复习 · 飞书推送

笔记自动评分（1-5），高分笔记按间隔推送复习：
- ⭐5：每 3 天 | ⭐4：每 7 天 | ⭐3：每 14 天 | 低分：不推

开启飞书推送后，每晚 8 点自动发送 3 条复习卡片。未配置飞书则在对话内展示。

### 知识库结构

```
D:\知识库\
├── 理论/       ← 概念、原理、框架、方法论
├── 案例/       ← 项目经验、踩坑记录、面试准备
└── meetings/   ← 会议记录（已有，不动）
```

## 快速开始

**一行命令安装：**

```bash
curl -fsSL https://raw.githubusercontent.com/Detachment5879/second-brain/main/install.sh | bash
```

**然后设置知识库路径（可选，自动探测 `D:\知识库`）：**

```bash
export OBSIDIAN_VAULT_PATH="/mnt/d/知识库"
```

**开始使用：**

```bash
@brain KSTAR熔断机制的核心是预测试≥80%跳过...
@brain save                    # 存档当前对话
@brain review                  # 今日复习
@brain connect agent记忆       # 合成相关笔记
@brain stats                   # 知识仪表盘
@brain feishu on               # 开启飞书推送
```

> 非 Hermes 用户看下方「非 Hermes 用户使用指南」

## 扩展模块

| 模块 | 说明 |
|------|------|
| brain-auto-save | 对话自动存档 + 价值审查 |
| brain-enhance | 间隔复习 + 知识合成 + 智能评分 + 飞书推送 |

> 三个模块共用同一知识库，标签和链接体系互通。

## 原理

```
用户输入 → AI Agent + Second Brain 体系
    ↓ 判断类型 → 提取实体 → 建模标签 → 价值审查 + 评分
    ↓ 用户确认
second-brain-writer.py → Obsidian Vault (.md 文件)
    ↓
后续：检索 / 复习推送 / 知识合成 / 仪表盘
```

## 已知限制

- 不能处理纯音频文件
- 旧版 `.ppt` 需先用 `strings` 提取文本
- 飞书推送需配置 webhook 或应用凭证

## 非 Hermes 用户使用指南

如果你用的是 **Codex CLI / OpenClaw / ChatGPT / 终端**，没有 `@brain` 命令体系：

```bash
# 1. 拿到脚本
git clone https://github.com/Detachment5879/second-brain.git
cd second-brain/brain-enhance/scripts

# 2. 设知识库路径
export OBSIDIAN_VAULT_PATH="/mnt/d/知识库"

# 3. 直接用
python3 brain-scheduler.py review    # 今日复习
python3 brain-scheduler.py stats     # 知识仪表盘
python3 brain-scheduler.py connect   # 合成建议
```

**配定时任务（Linux/macOS）：**
```bash
crontab -e
0 20 * * * cd ~/second-brain/brain-enhance/scripts && python3 brain-scheduler.py review
```

**配定时任务（Windows）：**
```powershell
schtasks /create /tn "BrainReview" /tr "python D:\second-brain\brain-enhance\scripts\brain-scheduler.py review" /sc daily /st 20:00
```

**配飞书推送（可选）：**
```bash
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
python3 brain-scheduler.py review
```

**配合 CC/OpenClaw：** 直接让 Agent 执行 `python3 brain-scheduler.py review`，读取 stdout 即可。零集成成本。

---

## License

MIT © Detachment5879