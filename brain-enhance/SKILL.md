---
name: brain-enhance
description: Second Brain 增强套件 — 间隔复习（飞书推送）、跨笔记知识合成、笔记优先度评分。@brain review / @brain connect / @brain score / @brain stats / @brain feishu
version: 1.0.0
---

# 🧠 Second Brain 增强套件

> 给第二大脑装上复习系统、知识合成引擎和智能评分。

## 依赖

本模块是 Second Brain 的扩展。需先安装 second-brain 和 brain-auto-save。
知识库路径：`D:\知识库`（理论/ + 案例/ + meetings/）

## 触发

| 触发词 | 功能 |
|--------|------|
| `@brain review` | 从知识库随机抽取高优先级旧笔记，推送复习 |
| `@brain connect [主题词]` | 扫描知识库，发现关联笔记簇，生成综合笔记 |
| `@brain score [笔记名] [1-5]` | 修改笔记优先级评分 |
| `@brain stats` | 知识增长仪表盘 |
| `@brain feishu on\|off` | 飞书定时推送复习卡片开关 |

---

## 功能一：间隔复习 · 飞书推送

### 评分系统

每条笔记 frontmatter 中存储：

```yaml
score: 4
review_count: 2
last_review: 2026-06-01
```

**自动评分**（首次存入时按内容密度和类型判断）：

| 条件 | 基础分 |
|------|--------|
| 理论类 + 含 ≥3 个实体链接 | 5 |
| 理论类 | 4 |
| 案例类 + 含方法论/原则 | 4 |
| 案例类 | 3 |
| 临时对话、无结构化内容 | 2 |
| `#inbox` 标记 | 1 |

用户可随时 `@brain score 笔记名 分数` 修改。评分决定复习频率：5分=每3天 / 4分=每7天 / 3分=每14天 / 1-2分=不推送。

### 复习抽取

```
扫描 → 过滤(score≥3 且超间隔) → 随机抽3条 → 按score降序 → 推送
推送后更新 review_count 和 last_review
```

### 飞书推送

**优先级链**（自动降级）：

```
用户说 @brain feishu on
        ↓
1. 检测飞书配置
   ├── FEISHU_WEBHOOK_URL 存在？ → 飞书自定义机器人
   ├── FEISHU_APP_ID + FEISHU_APP_SECRET 存在？ → 飞书应用
   └── 都没有 → 跳步骤 3
        ↓
2. 飞书可用 → 注册 Hermes cron job（每晚 20:00）
   → 每天推送 3 条复习卡片到飞书
        ↓
3. 飞书不可用 → 使用 Hermes 内置通知
   → 注册 Hermes cron job
   → 每天在对话中自动发送复习卡片
   （效果：打开 Hermes 就能看到今天的复习内容）
        ↓
4. 连 cron 都不可用 → 仅手动模式
   → 用户说 @brain review 时，对话内展示
```

**开启** `@brain feishu on`：按上述链自动选择最佳推送方式。

**关闭** `@brain feishu off`：删除 cron job。

**手动模式**：任何情况下 `@brain review` 都可用——直接在对话中展示今日复习卡片，不依赖任何外部平台。

**推送时间**：默认 20:00，`@brain feishu time 09:00` 可改。

---

## 功能二：知识合成

`@brain connect [主题词]`

1. 按标签+实体重叠度聚类
2. ≥3篇且实体重叠≥2的簇触发合成
3. LLM 生成综合笔记：共识点 / 互补点 / 矛盾点 / 演进过程
4. 存入 `理论/`，链接回所有源笔记

---

## 功能三：仪表盘

`@brain stats`

```
📊 知识库统计

笔记 47 | 理论18 案例29 | 未评分12
本周+5 | 本月+12

🔥 活跃: #agent(23) #llm(15) #面试(8)
⏰ 待复习: 18篇 | ⚠️ 孤岛: 3篇
💡 5篇 #agent 笔记未互链，试试 @brain connect
```

---

## 实现

- 评分写入 frontmatter（`score`/`review_count`/`last_review`）
- 飞书推送通过 Hermes cronjob + 飞书 webhook
- `FEISHU_WEBHOOK_URL` 环境变量或复用小洛项目飞书配置

---

## 跨平台自动化

### Hermes

内置 cronjob 自动调度，无需额外配置。`@brain feishu on` 即可。

### Codex CLI / OpenClaw / 任何终端 Agent

使用独立调度脚本 `scripts/brain-scheduler.py`，配合系统 cron：

**Linux / macOS / WSL：**
```bash
# 编辑 crontab
crontab -e

# 每晚 20:00 执行复习
0 20 * * * cd ~/.hermes/skills/note-taking/brain-enhance/scripts && python3 brain-scheduler.py review

# 每周一早 9:00 发送仪表盘
0 9 * * 1 cd ~/.hermes/skills/note-taking/brain-enhance/scripts && python3 brain-scheduler.py stats
```

**Windows（任务计划程序）：**
```powershell
# 创建每日任务
schtasks /create /tn "BrainReview" /tr "python C:\path\to\brain-scheduler.py review" /sc daily /st 20:00
```

**飞书推送（任何平台）：**
```bash
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
python3 brain-scheduler.py review   # 自动推送到飞书
```

不设 webhook 则输出到终端（stdout），Agent 可以直接读取。

### 命令一览

```bash
python3 brain-scheduler.py review    # 今日复习
python3 brain-scheduler.py stats     # 知识仪表盘
python3 brain-scheduler.py connect   # 合成建议
```

所有 Agent 平台都可直接调用这个脚本，输出纯文本，无需任何适配。