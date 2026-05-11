#!/usr/bin/env python3
"""
Second Brain — Obsidian知识库写入工具

用法:
  # 创建笔记
  python3 second-brain-writer.py \\
    --title "笔记标题" \\
    --type meeting-note \\
    --tags "tag1,tag2,tag3" \\
    --content "笔记内容(结构化markdown)" \\
    --entities "实体1,实体2" \\
    --thinking "AI推理过程"
  
  # 统计知识库
  python3 second-brain-writer.py --stats

  # 输出到指定目录
  python3 second-brain-writer.py --title "笔记" --type idea --content "内容" --dir "/mnt/d/知识库"
"""

import argparse
import os
import json
import re
from datetime import datetime
from pathlib import Path

VAULT_PATH = os.environ.get("OBSIDIAN_VAULT_PATH", str(Path.home() / "Documents" / "second-brain"))

def resolve_vault_path(custom_dir=None):
    """Return the effective vault path. Prefer custom_dir if provided."""
    if custom_dir:
        return custom_dir
    return VAULT_PATH

TYPE_DIR_MAP = {
    "meeting-note": "meetings",
    "reading-note": "readings",
    "insight": "insights",
    "idea": "ideas",
    "technical-note": "technical",
    "retrospective": "retrospectives",
    "person": "people",
    "concept": "concepts",
    "default": "inbox",
}

def ensure_vault_structure(vault_path=None):
    """Ensure the vault directory structure exists."""
    vp = Path(resolve_vault_path(vault_path))
    dirs = set(TYPE_DIR_MAP.values()) | {"logs", "inbox"}
    for d in dirs:
        (vp / d).mkdir(parents=True, exist_ok=True)
    # Create .index.md if not exists
    index_path = vp / ".index.md"
    if not index_path.exists():
        index_path.write_text(
            f"# Second Brain Index\n\n*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        )

def slugify(text: str) -> str:
    """Convert text to a URL-friendly filename."""
    text = text.strip().lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:80].rstrip('-')

def generate_filename(title: str) -> str:
    """Generate a filename from title."""
    return slugify(title) + ".md"

def get_target_dir(content_type: str) -> str:
    """Get the target subdirectory for a content type."""
    return TYPE_DIR_MAP.get(content_type, TYPE_DIR_MAP["default"])

def update_index(title: str, filepath: Path, tags: list, content_type: str, vault_path=None):
    """Update .index.md with new entry."""
    vp = Path(resolve_vault_path(vault_path))
    index_path = vp / ".index.md"
    relative_path = filepath.relative_to(VAULT_PATH)
    date = datetime.now().strftime("%Y-%m-%d")
    
    entry = f"- {date} | [[{title}]] | `{content_type}` | Tags: {' '.join(tags)}\n"
    
    with open(index_path, "a", encoding="utf-8") as f:
        f.write(entry)

def update_changelog(title: str, action: str = "created", vault_path=None):
    """Update changelog."""
    vp = Path(resolve_vault_path(vault_path))
    log_path = vp / "logs" / "changelog.md"
    if not log_path.exists():
        log_path.write_text("# Changelog\n\n")
    
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"- {date} | {action}: [[{title}]]\n")

def write_note(title: str, content_type: str, tags: list, 
               content: str, entities: list, thinking: str = "", vault_path=None):
    """Create a formatted Obsidian note."""
    vp = resolve_vault_path(vault_path)
    ensure_vault_structure(vault_path)
    
    date = datetime.now().strftime("%Y-%m-%d")
    target_dir = Path(vp) / get_target_dir(content_type)
    filename = generate_filename(title)
    filepath = target_dir / filename
    
    tag_lines = "\n".join(f"  - #{tag}" for tag in tags)
    entity_links = ", ".join(f"[[{e}]]" for e in entities) if entities else ""
    
    frontmatter = f"""---
tags:
{tag_lines}
date: {date}
type: {content_type}
aliases:
  - {slugify(title)}
sources: []
---

"""
    
    body = f"""# {title}

> *自动录入于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*

---

{content}

---

"""
    
    if entity_links:
        body += f"""## 🔗 关联实体

{entity_links}

"""
    
    if thinking:
        body += f"""## 🤖 AI 推理笔记

{thinking}

"""
    
    body += f"""---
*由 Second Brain Skill 于 {datetime.now().strftime('%Y-%m-%d %H:%M')} 自动生成*
"""
    
    filepath.write_text(frontmatter + body, encoding="utf-8")
    update_index(title, filepath, tags, content_type, vault_path)
    update_changelog(title, "created", vault_path)
    
    return filepath

def get_stats(vault_path=None):
    """Show knowledge base statistics."""
    vp = Path(resolve_vault_path(vault_path))
    ensure_vault_structure(vault_path)
    vault = vp
    
    total = 0
    type_counts = {}
    orphan_count = 0
    broken_links = []
    backlinks = {}
    
    all_md_files = list(vault.rglob("*.md"))
    visible_md = [f for f in all_md_files if not f.name.startswith(".") 
                  and "logs" not in f.parts]
    
    for f in visible_md:
        content = f.read_text(encoding="utf-8")
        total += 1
        
        type_match = re.search(r'type:\s*(\S+)', content)
        if type_match:
            t = type_match.group(1)
            type_counts[t] = type_counts.get(t, 0) + 1
        
        links = re.findall(r'\[\[([^\]]+)\]\]', content)
        for link in links:
            target_exists = False
            for md_file in all_md_files:
                if link == md_file.stem:
                    target_exists = True
                    break
            if not target_exists:
                broken_links.append((f.name, link))
        
        backlinks[f.name] = backlinks.get(f.name, 0)
        for link in links:
            backlinks[link] = backlinks.get(link, 0) + 1
    
    for f in visible_md:
        if backlinks.get(f.stem, 0) == 0:
            orphan_count += 1
    
    print(f"📊 Second Brain 知识库统计")
    print(f"{'='*40}")
    print(f"📁 知识库路径: {VAULT_PATH}")
    print(f"📄 笔记总数: {total}")
    print(f"\n📂 按类型分布:")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")
    print(f"\n🔗 孤立笔记(无反向链接): {orphan_count}")
    if broken_links:
        print(f"\n⚠️ 损坏的 WikiLink ({len(broken_links)}):")
        for src, target in broken_links[:5]:
            print(f"  {src} → [[{target}]]")
        if len(broken_links) > 5:
            print(f"  ...还有 {len(broken_links)-5} 个")
    print(f"\n✅ 知识库状态: {'健康' if broken_links == 0 and orphan_count == 0 else '需要维护'}")

def main():
    parser = argparse.ArgumentParser(description="Second Brain - Obsidian知识库写入工具")
    parser.add_argument("--title", help="笔记标题")
    parser.add_argument("--type", default="default", help="内容类型")
    parser.add_argument("--tags", default="", help="标签列表(逗号分隔)")
    parser.add_argument("--content", default="", help="笔记内容(Markdown)")
    parser.add_argument("--entities", default="", help="实体列表(逗号分隔)")
    parser.add_argument("--thinking", default="", help="AI推理过程")
    parser.add_argument("--stats", action="store_true", help="显示知识库统计")
    parser.add_argument("--dir", default=None, help="输出目录（覆盖 OBSIDIAN_VAULT_PATH）")
    
    args = parser.parse_args()
    
    vault_path = args.dir
    
    if args.stats:
        get_stats(vault_path)
        return
    
    if not args.title or not args.content:
        print(json.dumps({"error": "需要提供 --title 和 --content"}))
        return
    
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    entities = [e.strip() for e in args.entities.split(",") if e.strip()]
    
    filepath = write_note(args.title, args.type, tags, args.content, entities, args.thinking, vault_path)
    
    result = {
        "status": "ok",
        "filepath": str(filepath),
        "title": args.title,
        "type": args.type,
        "tags": tags,
    }
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
