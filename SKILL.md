---
name: second-brain
description: Transform any unstructured input (meeting notes, articles, chat logs, ideas) into structured Obsidian knowledge nodes. Builds and maintains your personal knowledge base with bidirectional links, tags, and knowledge graphs.
version: 1.0.0
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
| `@brain` | 通用启动：处理一段知识输入 |
| `帮我整理\|帮我记录\|记下来\|保存这个` | 用户有内容需要存入知识库 |
| 用户发送**文件路径**（.docx/.pdf/.txt/.md） | 自动检测扩展名，读取并处理 |
| 用户粘贴/输入一段**非结构化文本**（会议记录、笔记、灵感、文章片段） | 自动识别并处理 |
| `查一下\|搜索\|我记得\|关于 [[某概念]]` | 查询知识库模式 |

---

## 核心工作流

### Step 0：环境初始化
每次启动时，先执行以下检查：

1. **检查知识库路径**：
   ```bash
   # 如果 OBSIDIAN_VAULT_PATH 未设置，尝试探测 Windows 知识库
   if [ -z "$OBSIDIAN_VAULT_PATH" ]; then
     if [ -d "/mnt/d/知识库" ]; then
       export OBSIDIAN_VAULT_PATH="/mnt/d/知识库"
     elif [ -d "/mnt/c/Users/$USER/Desktop/知识库" ]; then
       export OBSIDIAN_VAULT_PATH="/mnt/c/Users/$USER/Desktop/知识库"
     fi
   fi
   echo "知识库路径: ${OBSIDIAN_VAULT_PATH:-$HOME/Documents/second-brain}"
   ```

2. **检查依赖工具**：
   ```bash
   # 检查 python-docx（用于读取 .docx 文件）
   python3 -c "import docx" 2>/dev/null || pip install python-docx 2>/dev/null || true
   ```

3. **确保知识库目录存在**：
   ```bash
   mkdir -p "${OBSIDIAN_VAULT_PATH:-$HOME/Documents/second-brain}"/{meetings,readings,ideas,insights,technical,people,concepts,retrospectives,inbox,logs}
   ```

### Step 1：读取与解析输入

#### 从文件读取（如果用户提供了文件路径）
检测文件扩展名，用对应方式读取：

| 文件类型 | 读取方式 |
|----------|----------|
| `.docx` | `python3 -c "import zipfile, xml.etree.ElementTree as ET; ..."`（内置库，不需额外依赖） |
| `.txt`, `.md` | 直接 `read_file` 工具 |
| `.pdf` | `python3 -c "import PyPDF2; ..."` 或 ocr 工具 |
### 模式一：知识录入（默认模式）

当用户提供非结构化输入时，按以上 Step 0 → Step 1 → Step 2 顺序执行，然后继续：

#### Step 3：知识建模

| 类型 | 特征 | 输出笔记type |
|------|------|-------------|
| 会议/沟通记录 | 有对话、决议、待办 | `meeting-note` |
| 学习笔记/阅读摘录 | 有知识点、概念、引用 | `reading-note` |
| 行业资讯/文章 | 有事实、数据、观点 | `insight` |
| 个人灵感/想法 | 主观、未成型、发散 | `idea` |
| 经验教训/复盘 | 有因果、反思、结论 | `retrospective` |
| 技术文档/教程 | 有步骤、代码、参数 | `technical-note` |

#### Step 2：知识建模

自动执行以下分析：

1. **标签生成**：生成 3-5 个层级标签（从宽到窄）
   - 主领域标签：`#programming` `#design` `#business` `#AI` 等
   - 次级标签：`#architecture` `#会议纪要` 等
   - 状态标签：`#inbox`（待整理）`#seedling`（新笔记）`#evergreen`（成熟笔记）

2. **实体提取**：识别文本中的关键实体
   - 人物：将人名转为 `[[人名]]` WikiLink
   - 公司/组织：`[[公司名]]`
   - 专业术语：`[[术语]]`
   - 核心概念/理论：`[[概念名]]`
   - 项目名：`[[项目名]]`

3. **关联发现**：识别当前内容与知识库中已有内容的潜在关联
   - 检查是否有相同实体出现
   - 检查是否有相同标签
   - 记录关联关系用于后续检索

#### Step 4：生成 Obsidian Markdown

执行写入工具生成标准化的笔记文件：

```bash
python3 ${HERMES_SKILL_DIR}/scripts/second-brain-writer.py \
  --title "{{自动生成的标题}}" \
  --type "{{内容类型}}" \
  --tags "{{tag1,tag2,tag3}}" \
  --content "{{处理后的结构化内容}}" \
  --entities "{{entity1,entity2}}" \
  --thinking "{{AI的推理笔记}}"
```

如果需要输出到非默认目录（如 Windows D 盘），加上 `--dir` 参数：

```bash
python3 ${HERMES_SKILL_DIR}/scripts/second-brain-writer.py \
  --title "..." --type "..." --tags "..." \
  --content "..." --entities "..." \
  --dir "/mnt/d/知识库"
```

#### Step 5：存入知识库

知识库目录结构：

```
{{OBSIDIAN_VAULT_PATH:-$HOME/Documents/second-brain}}/
├── inbox/                    # 待处理的笔记
├── meetings/                 # 会议记录
├── readings/                 # 阅读笔记
├── ideas/                    # 灵感
├── insights/                 # 行业洞察
├── technical/                # 技术笔记
├── people/                   # 人物笔记
├── concepts/                 # 概念解释
├── retrospectives/           # 复盘
├── logs/                     # 操作日志
│   └── changelog.md          # 自动更新的变更记录
└── .index.md                 # 自动维护的知识索引
```

---

### 模式二：知识查询（`@brain query` 或自然语言提问）

当用户提问时：

1. **检索知识库**：
   ```bash
   VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/second-brain}"
   find "$VAULT" -name "*.md" -type f | xargs grep -l "{{关键词}}" 2>/dev/null
   ```

2. **关联展开**：
   根据当前问题的实体，递归检索关联笔记中的关联实体（1-2跳深度）

3. **综合回答**：
   基于检索结果生成回答，在回答中：
   - 用 `[[WikiLink]]` 指向知识库中的相关笔记
   - 标注信息来源（引用自哪篇笔记）
   - 指出知识空白（如果有）

4. **同步更新**（可选）：
   如果用户提供了新信息或修正，自动更新/追加到相关笔记

---

### 模式三：知识维护（`@brain maintain`）

定期或按需执行：

1. **lint 检查**：扫描所有笔记，检查：
   - 损坏的 WikiLink（`[[xxx]]` 指向不存在的笔记）
   - 孤立笔记（没有反向链接）
   - 过时的标签

2. **索引重建**：重新生成 `.index.md`

3. **图谱优化**：识别可以合并/拆分/链接的笔记

---

## 笔记模板

每篇笔记遵循以下格式：

```markdown
---
tags:
  - #{{主领域标签}}
  - #{{次级标签}}
  - #{{状态标签}}
date: {{YYYY-MM-DD}}
type: {{内容类型}}
aliases:
  - {{别名1}}
sources:
  - {{信息来源}}
---

# {{笔记标题}}

> {{一句话核心摘要}}

## 💡 核心内容

- 要点 1：...
- 要点 2：...

## 🔗 关联

- 相关人物：[[人物1]], [[人物2]]
- 相关概念：[[概念1]], [[概念2]]
- 相关笔记：[[笔记标题]]

## 📝 延伸思考

- ...

---

*由 Second Brain Skill 于 {{YYYY-MM-DD HH:mm}} 自动生成*
```

---

## 工具使用规则

| 任务 | 使用工具 |
|------|----------|
| 读取用户输入 | 直接从用户消息读取 |
| 生成笔记文件 | `Bash` → `python3 ${HERMES_SKILL_DIR}/scripts/second-brain-writer.py` |
| 知识库检索 | `Bash` → `find+grep` |
| 读取已有笔记 | `Read` 工具 |
| 更新已有笔记 | `Write` / `Edit` 工具 |
| 查看知识库统计 | `Bash` → `python3 ${HERMES_SKILL_DIR}/scripts/second-brain-writer.py --stats` |

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OBSIDIAN_VAULT_PATH` | Obsidian 知识库路径 | `$HOME/Documents/second-brain` |

---

## 安全边界

1. **仅处理用户主动提供的信息**，不主动搜索用户隐私数据
2. **本地优先**：所有知识库文件存储在本地，不自动上传
3. **透明更新**：修改已有笔记前向用户确认

---

## 示例

### 示例 1：会议记录

**用户输入**：
> 今天和张三讨论了新项目的架构。决定用微服务，每个团队负责一个模块。后端用 Go，前端继续 React。

**生成笔记**：
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

## 💡 核心决议
- 采用[[微服务架构]]，各团队独立负责模块
- 后端技术栈：[[Go]]
- 前端技术栈：[[React]]

## 🔗 关联
- 关键人物：[[张三]]
- 相关概念：[[微服务架构]]

## 📝 待办
- [ ] 各团队确认模块边界
```

### 示例 2：查询知识库

**用户**：`查一下微服务相关的内容`

**回答**：
> 知识库中有以下相关笔记：
> - [[新项目架构讨论]]（2026-05-11）— 你决定用微服务架构
> - [[微服务架构模式]]（2026-04-20）— 记录了 Service Mesh 相关内容
>
> 还关联到：[[Go]], [[Docker]], [[Kubernetes]]
>
> 要我展开讲讲某个具体方面吗？
