---
name: second-brain
description: 🧠 Second Brain · 第二大脑 — 知识录入/对话存档/被动RAG/间隔复习/知识合成/智能评分/飞书推送。一键把你的碎片信息变成结构化 Obsidian 知识网络。
version: 2.0.0
allowed-tools: Read, Write, Edit, Bash, Web
---

> **Language**: This skill supports English and Chinese. Detect user's language from first message and respond consistently.
>
> **语言**：本 Skill 支持中英文。根据用户第一条消息的语言，全程使用同一语言回复。

# 🧠 Second Brain · 第二大脑

> *把你的碎片信息变成永久的、可检索的、互联的知识网络。*

**Your AI knowledge architect — turns chaos into structure.**

## 触发条件

当用户说以下任意内容时启动：

| 触发词 | 模式 |
|--------|------|
| `@brain` + 内容/文件/链接 | 通用启动：处理知识输入 |
| `@brain save` / `帮我保存对话` | 对话存档：价值审查后存入 |
| `@brain review` | 间隔复习：推送高优先级旧笔记 |
| `@brain connect [主题词]` | 知识合成：跨笔记综合 |
| `@brain score [笔记] [1-5]` | 修改笔记评分 |
| `@brain stats` | 知识仪表盘 |
| `@brain feishu on\|off` | 飞书推送开关 |
| `@brain maintain` | 知识库维护 |
| `查一下\|搜索\|我记得` | 查询知识库 |
| **自动（无需触发）** | **被动 RAG：提问时自动检索知识库** |

> **自动提示**：深度对话结束时主动询问是否需要 `@brain save`。

---

## 核心工作流

### Step 0：环境初始化
每次启动时，先执行以下检查：

1. **检查知识库路径**：
   ```bash
   if [ -z "$OBSIDIAN_VAULT_PATH" ]; then
     if [ -d "/mnt/d/知识库" ]; then
       export OBSIDIAN_VAULT_PATH="/mnt/d/知识库"
     fi
   fi
   ```

2. **确保目录存在**：
   ```bash
   mkdir -p "${OBSIDIAN_VAULT_PATH:-$HOME/Documents/second-brain}"/{理论,案例}
   ```

### Step 1：读取与解析输入

| 文件类型 | 读取方式 |
|----------|----------|
| `.docx` | zipfile + xml.etree（内置库） |
| `.txt`, `.md` | read_file 工具 |
| `.pdf` | PyPDF2 或 ocr |

---

### 模式一：知识录入（`@brain` + 内容）

分析 → 去噪 → 建模 → 价值审查 → 用户确认 → 写入。

#### 价值审查

| 标准 | 通过 | 不通过 |
|------|------|--------|
| 新颖性 | 新概念、新发现 | 反复聊的老话题 |
| 可复用性 | 以后还会用到 | 一次性操作指令 |
| 结构化潜力 | 能提炼成要点 | 纯闲聊 |

查重 + 脱敏 → **用户确认后才写入**。

#### 笔记模板

```markdown
---
tags: [#主标签, #次标签]
date: YYYY-MM-DD
score: 4
review_count: 0
last_review: ""
---

# 标题

> 一句话摘要

## 要点
- 要点一
- 要点二

## 关联
- [[相关笔记1]]
```

---

### 模式二：知识查询（提问时自动 / 手动 `查一下`）

1. 检索知识库：`find + grep`
2. 关联展开（1-2跳深度）
3. 综合回答，引用 `[[WikiLink]]`
4. 可选：同步更新相关笔记

---

### 模式三：知识维护（`@brain maintain`）

1. 坏链检查（`[[xxx]]` 指向不存在）
2. 孤岛笔记检测（无反链）
3. 索引重建
4. 图谱优化建议

---

### 模式四：对话存档（`@brain save`）

分析当前对话 → 价值审查 → 理论/案例分类 → 用户确认 → 存入 Obsidian。

存入路径：理论类 → `理论/`，案例类 → `案例/`。

---

### 模式五：被动 RAG（自动，无需触发）

每次用户提问时自动执行：
1. 提取实体词（项目名、术语、人名）
2. `grep` 搜索知识库
3. 命中 → 提取段落 → 注入回答
4. 引用 `[[笔记名]]`

不触发：纯闲聊、一次性操作、知识库无匹配。

---

### 模式六：间隔复习（`@brain review`）

#### 评分系统

每条笔记 frontmatter 存储 `score`(1-5) / `review_count` / `last_review`。

自动评分：理论+多实体=5 / 理论=4 / 案例+方法论=4 / 案例=3 / 临时=2 / inbox=1。

用户可 `@brain score 笔记名 分数` 修改。5分每3天推 / 4分每7天 / 3分每14天 / 低分不推。

#### 飞书推送

优先级链：飞书 webhook → 飞书应用 → Hermes cron → 手动。

`@brain feishu on` 开启，`off` 关闭。默认 20:00 推送。

---

### 模式七：知识合成（`@brain connect`）

按标签+实体重叠聚类 → ≥3篇触发 → LLM 合成综合笔记（共识/互补/矛盾/演进）→ 存入 `理论/`。

---

### 模式八：仪表盘（`@brain stats`）

```
📊 知识库统计

笔记 47 | 理论18 案例29 | 未评分12
本周+5 | 本月+12

🔥 活跃: #agent(23) #llm(15)
⏰ 待复习: 18篇 | ⚠️ 孤岛: 3篇
💡 建议 @brain connect agent
```

---

## 跨平台自动化

### Hermes
内置 cronjob。`@brain feishu on` 即可。

### Codex CLI / OpenClaw / 终端
使用 `scripts/brain-scheduler.py`：

```bash
python3 brain-scheduler.py review    # 今日复习
python3 brain-scheduler.py stats     # 知识仪表盘
python3 brain-scheduler.py connect   # 合成建议
```

**配定时任务：**
```bash
# Linux/macOS crontab
0 20 * * * python3 brain-scheduler.py review

# Windows 任务计划程序
schtasks /create /tn "BrainReview" /tr "python brain-scheduler.py review" /sc daily /st 20:00
```

**飞书推送：**
```bash
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
python3 brain-scheduler.py review
```

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OBSIDIAN_VAULT_PATH` | 知识库路径 | 自动探测 `D:\知识库` |
| `FEISHU_WEBHOOK_URL` | 飞书推送 | 无 |

---

## 已知限制

- 不能处理纯音频
- 旧版 `.ppt` 需 `strings` 提取
- 飞书推送需配置 webhook

---

## 安全边界

1. 仅处理用户主动提供的信息
2. 本地存储，不自动上传
3. 修改已有笔记前确认
4. 写入前价值审查 + 用户确认