#!/bin/bash
# Second Brain 一键安装脚本
# 兼容 Hermes / CC / OpenClaw / 独立使用

set -e

SKILL_DIR="${HERMES_SKILL_DIR:-$HOME/.hermes/skills}"
REPO="https://github.com/Detachment5879/second-brain.git"
TMP=$(mktemp -d)

echo "🧠 Second Brain 安装中..."

# 克隆仓库
git clone --depth 1 "$REPO" "$TMP" 2>/dev/null

# 安装主脑 (second-brain)
mkdir -p "$SKILL_DIR/second-brain/scripts"
cp "$TMP/SKILL.md" "$SKILL_DIR/second-brain/"
cp -r "$TMP/scripts/"* "$SKILL_DIR/second-brain/scripts/" 2>/dev/null || true

# 安装增强模块 (brain-enhance)
mkdir -p "$SKILL_DIR/brain-enhance/scripts"
cp "$TMP/brain-enhance/SKILL.md" "$SKILL_DIR/brain-enhance/"
cp -r "$TMP/brain-enhance/scripts/"* "$SKILL_DIR/brain-enhance/scripts/" 2>/dev/null || true

# 清理
rm -rf "$TMP"

echo ""
echo "✅ Second Brain 安装完成！"
echo ""
echo "知识库路径: ${OBSIDIAN_VAULT_PATH:-自动探测 D:\知识库}"
echo ""
echo "试试这些命令:"
echo "  @brain          录入知识"
echo "  @brain save     存档对话"
echo "  @brain review   今日复习"
echo "  @brain stats    知识仪表盘"