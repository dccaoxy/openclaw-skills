#!/bin/bash
# OpenClaw 关键文件备份脚本

DATE=$(date +%Y-%m-%d_%H-%M)
BACKUP_DIR="/Users/caoxy/Desktop/openclaw_backup_$DATE"

echo "=== OpenClaw 备份开始 ==="
echo "时间: $DATE"
echo "目标: $BACKUP_DIR"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份关键配置文件
cp ~/.openclaw/openclaw.json "$BACKUP_DIR/"
cp ~/.openclaw/openclaw.json.bak* "$BACKUP_DIR/" 2>/dev/null

# 备份 credentials
cp -r ~/.openclaw/credentials "$BACKUP_DIR/"

# 备份 agent 配置
cp -r ~/.openclaw/agents "$BACKUP_DIR/"

# 备份 workspace 关键文件
mkdir -p "$BACKUP_DIR/workspace"
cp ~/.openclaw/workspace/SOUL.md "$BACKUP_DIR/workspace/" 2>/dev/null
cp ~/.openclaw/workspace/AGENTS.md "$BACKUP_DIR/workspace/" 2>/dev/null
cp ~/.openclaw/workspace/USER.md "$BACKUP_DIR/workspace/" 2>/dev/null
cp ~/.openclaw/workspace/IDENTITY.md "$BACKUP_DIR/workspace/" 2>/dev/null

# 备份 skills
cp -r ~/.openclaw/workspace/skills "$BACKUP_DIR/workspace/"

# 备份复盘记录
cp -r ~/.openclaw/agent_review "$BACKUP_DIR/"

# 备份 memory
cp -r ~/.openclaw/memory "$BACKUP_DIR/" 2>/dev/null

echo "=== 备份完成 ==="
echo "备份位置: $BACKUP_DIR"

# 清理 7 天前的备份（保留最新 7 份）
find ~/Desktop -maxdepth 1 -name "openclaw_backup_*" -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null
echo "已清理 7 天前的旧备份"
