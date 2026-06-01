"""
Second Brain 独立调度器
======================
不依赖 Hermes / CC / OpenClaw，系统 cron 直接调。

用法:
  python brain-scheduler.py review     # 输出今日复习卡片
  python brain-scheduler.py stats      # 知识库仪表盘
  python brain-scheduler.py connect    # 扫描并生成合成建议

配置:
  环境变量 OBSIDIAN_VAULT_PATH 或自动探测 D:\\知识库
  可选: FEISHU_WEBHOOK_URL 用于飞书推送
"""
import os
import sys
import json
import random
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter


def find_vault() -> Path:
    """自动探测知识库路径"""
    env = os.environ.get("OBSIDIAN_VAULT_PATH")
    if env:
        return Path(env)
    
    candidates = [
        Path("/mnt/d/知识库"),
        Path("/mnt/c/Users").glob("*/Desktop/知识库"),
        Path.home() / "Documents" / "second-brain",
        Path.home() / "知识库",
    ]
    for c in candidates:
        if isinstance(c, Path) and c.exists():
            return c
        elif hasattr(c, '__iter__'):
            for p in c:
                if p.exists():
                    return p
    
    print("错误: 未找到知识库。请设置 OBSIDIAN_VAULT_PATH 环境变量。")
    sys.exit(1)


def scan_notes(vault: Path) -> list[dict]:
    """扫描知识库所有笔记，提取 frontmatter 和内容"""
    notes = []
    for md in vault.rglob("*.md"):
        if ".obsidian" in str(md) or ".trash" in str(md):
            continue
        
        content = md.read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(content)
        
        notes.append({
            "path": md,
            "name": md.stem,
            "relative": str(md.relative_to(vault)),
            "frontmatter": fm,
            "content": content,
            "mtime": datetime.fromtimestamp(md.stat().st_mtime),
        })
    return notes


def parse_frontmatter(content: str) -> dict:
    """解析 YAML frontmatter"""
    if not content.startswith("---"):
        return {}
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    
    fm = {}
    for line in parts[1].strip().split("\n"):
        line = line.strip()
        if ":" in line:
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip()
            # 简单类型转换
            if v.isdigit():
                v = int(v)
            elif v.replace(".", "").isdigit():
                v = float(v)
            fm[k] = v
    return fm


def ensure_scored(notes: list[dict], vault: Path):
    """给缺少 score 的笔记自动评分"""
    for note in notes:
        if "score" in note["frontmatter"]:
            continue
        
        content = note["content"]
        # 实体链接数量
        entities = len(re.findall(r'\[\[([^\]]+)\]\]', content))
        # 判断类型
        relative = note["relative"]
        if "理论" in relative:
            score = 5 if entities >= 3 else 4
        elif "案例" in relative:
            score = 4 if "方法论" in content or "原则" in content else 3
        elif "inbox" in note["frontmatter"].get("tags", ""):
            score = 1
        else:
            score = 2
        
        note["frontmatter"]["score"] = score
        note["frontmatter"]["review_count"] = 0
        note["frontmatter"]["last_review"] = ""
        
        # 写入文件
        update_frontmatter(note["path"], "score", score)
        update_frontmatter(note["path"], "review_count", 0)
        update_frontmatter(note["path"], "last_review", "")


def update_frontmatter(path: Path, key: str, value):
    """更新单条 frontmatter 字段"""
    content = path.read_text(encoding="utf-8")
    
    if not content.startswith("---"):
        return
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return
    
    fm_lines = parts[1].split("\n")
    new_fm = []
    found = False
    
    for line in fm_lines:
        if line.strip().startswith(f"{key}:"):
            new_fm.append(f"{key}: {value}")
            found = True
        else:
            new_fm.append(line)
    
    if not found:
        new_fm.append(f"{key}: {value}")
    
    new_content = f"---\n{chr(10).join(new_fm)}\n---{parts[2]}"
    path.write_text(new_content, encoding="utf-8")


def get_review_cards(notes: list[dict], count: int = 3) -> list[dict]:
    """抽取待复习笔记"""
    now = datetime.now()
    candidates = []
    
    for note in notes:
        score = note["frontmatter"].get("score", 0)
        if score < 3:
            continue
        
        last_review_str = note["frontmatter"].get("last_review", "")
        if last_review_str:
            try:
                last_review = datetime.fromisoformat(last_review_str)
            except:
                last_review = datetime.min
        else:
            last_review = datetime.min
        
        # 间隔
        intervals = {5: 3, 4: 7, 3: 14}
        interval_days = intervals.get(score, 999)
        days_since = (now - last_review).days
        
        if days_since >= interval_days:
            candidates.append(note)
    
    if not candidates:
        return []
    
    selected = random.sample(candidates, min(count, len(candidates)))
    selected.sort(key=lambda n: n["frontmatter"].get("score", 0), reverse=True)
    return selected


def extract_summary(note: dict, max_len: int = 60) -> str:
    """提取笔记摘要"""
    content = note["content"]
    # 去掉 frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        content = parts[2] if len(parts) > 2 else content
    
    # 取第一个非空段落
    lines = content.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            if len(line) > max_len:
                line = line[:max_len] + "..."
            return line
    return note["name"]


def do_review(vault: Path):
    """执行复习"""
    notes = scan_notes(vault)
    ensure_scored(notes, vault)
    cards = get_review_cards(notes)
    
    if not cards:
        print("🎉 没有待复习的笔记！知识库很新鲜。")
        return
    
    print("📖 今日复习\n")
    print("━" * 40)
    
    for card in cards:
        score = card["frontmatter"].get("score", "?")
        summary = extract_summary(card)
        last = card["frontmatter"].get("last_review", "从未")
        if last and last != "从未":
            try:
                last = datetime.fromisoformat(last).strftime("%m/%d")
            except:
                pass
        
        print(f"\n⭐{score} {card['name']}")
        print(f"   📁 {card['relative']}  |  上次: {last}")
        print(f"   {summary}")
    
    print("\n" + "━" * 40)
    
    # 更新 last_review
    now = datetime.now().isoformat()
    for card in cards:
        update_frontmatter(card["path"], "last_review", now)
        count = card["frontmatter"].get("review_count", 0) + 1
        update_frontmatter(card["path"], "review_count", count)
    
    # 飞书推送
    webhook = os.environ.get("FEISHU_WEBHOOK_URL")
    if webhook:
        send_feishu(webhook, cards)


def send_feishu(webhook: str, cards: list[dict]):
    """推送复习卡片到飞书"""
    import urllib.request
    
    lines = ["📖 今日复习\n"]
    for card in cards:
        score = card["frontmatter"].get("score", "?")
        summary = extract_summary(card, 80)
        lines.append(f"\n⭐{score} **{card['name']}**")
        lines.append(f"{summary}")
    
    payload = json.dumps({
        "msg_type": "text",
        "content": {"text": "\n".join(lines)}
    }).encode()
    
    try:
        urllib.request.urlopen(
            urllib.request.Request(webhook, data=payload, headers={"Content-Type": "application/json"}),
            timeout=5
        )
    except Exception as e:
        print(f"\n⚠️ 飞书推送失败: {e}")


def do_stats(vault: Path):
    """知识库仪表盘"""
    notes = scan_notes(vault)
    ensure_scored(notes, vault)
    
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    theory = sum(1 for n in notes if "理论" in n["relative"])
    case = sum(1 for n in notes if "案例" in n["relative"])
    unscored = sum(1 for n in notes if "score" not in n["frontmatter"])
    
    week_new = sum(1 for n in notes if n["mtime"] > week_ago)
    month_new = sum(1 for n in notes if n["mtime"] > month_ago)
    
    # 标签统计
    all_tags = []
    for n in notes:
        tags = n["frontmatter"].get("tags", "")
        if isinstance(tags, str):
            all_tags.extend([t.strip().lstrip("#") for t in tags.split(",")])
    
    tag_counts = Counter(all_tags).most_common(5)
    
    # 待复习
    cards = get_review_cards(notes)
    
    # 孤岛笔记
    orphans = sum(1 for n in notes if "[[" not in n["content"])
    
    print(f"📊 知识库统计 ({now.strftime('%Y-%m-%d')})\n")
    print(f"笔记总数：{len(notes)} 篇")
    print(f"├── 理论：{theory} 篇")
    print(f"├── 案例：{case} 篇")
    print(f"└── 未评分：{unscored} 篇\n")
    print(f"本周新增：{week_new} 篇")
    print(f"本月新增：{month_new} 篇\n")
    
    if tag_counts:
        print("🔥 最活跃领域：")
        for tag, count in tag_counts:
            print(f"   #{tag} ({count}篇)")
    
    print(f"\n⏰ 待复习：{len(cards)} 篇超过间隔期")
    print(f"⚠️ 孤岛笔记：{orphans} 篇无任何链接")
    
    if notes:
        agent_notes = [n for n in notes if "agent" in n["content"].lower() and "agent" in n["frontmatter"].get("tags", "").lower()]
        if len(agent_notes) >= 3:
            linked = sum(1 for n in agent_notes if n["name"] in n["content"])
            if linked < len(agent_notes) // 2:
                print(f"\n💡 {len(agent_notes)} 篇 agent 笔记尚未充分互链，试试 brain-scheduler.py connect")


def do_connect(vault: Path):
    """扫描并展示可合成的笔记簇"""
    notes = scan_notes(vault)
    
    # 按标签聚类
    clusters = {}
    for note in notes:
        tags_str = note["frontmatter"].get("tags", "")
        if isinstance(tags_str, str):
            tags = [t.strip().lstrip("#") for t in tags_str.split(",") if t.strip()]
        else:
            tags = []
        
        for tag in tags:
            if tag not in clusters:
                clusters[tag] = []
            clusters[tag].append(note)
    
    print("🔗 知识合成建议\n")
    
    found = False
    for tag, cluster in clusters.items():
        if len(cluster) >= 3:
            # 检查实体重叠
            all_entities = []
            for n in cluster:
                entities = re.findall(r'\[\[([^\]]+)\]\]', n["content"])
                all_entities.extend(entities)
            
            common = [e for e, c in Counter(all_entities).items() if c >= 2]
            
            if len(common) >= 2:
                found = True
                print(f"📦 #{tag} 簇 ({len(cluster)}篇) — 共享实体: {', '.join(common[:5])}")
                for n in cluster:
                    print(f"   · {n['name']}")
                print()
    
    if not found:
        print("未发现可合成的笔记簇。继续积累，知识之间会自然产生关联。")


# ── 入口 ──

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python brain-scheduler.py [review|stats|connect]")
        sys.exit(1)
    
    vault = find_vault()
    cmd = sys.argv[1]
    
    if cmd == "review":
        do_review(vault)
    elif cmd == "stats":
        do_stats(vault)
    elif cmd == "connect":
        do_connect(vault)
    else:
        print(f"未知命令: {cmd}")