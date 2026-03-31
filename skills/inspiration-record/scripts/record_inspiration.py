#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵感记录脚本 - 快速记录想法、创意、笔记
支持智能关联召回功能

用法:
    python record_inspiration.py "想法内容" --tags 标签 1 标签 2 --type 想法类型
    python record_inspiration.py --file 输入文件.md

示例:
    python record_inspiration.py "算力平权是未来趋势" --tags AI 战略 --type 想法
    python record_inspiration.py --file meeting_notes.md --type 会议
"""

import argparse
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# 默认存储路径
DEFAULT_MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory" / "inbox"
MEMORY_SEARCH_DIR = Path.home() / ".openclaw" / "workspace" / "memory"

# 记忆类型
MEMORY_TYPES = {
    "想法": "💡",
    "会议": "📋",
    "笔记": "📝",
    "目标": "🎯",
    "数据": "📊",
    "感悟": "💭",
    "灵感": "💡",
}

# 关联召回阈值（余弦相似度）
SIMILARITY_THRESHOLD = 0.35
MAX_RELATED_COUNT = 3


def generate_filename(memory_type: str) -> str:
    """生成文件名"""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    type_prefix = MEMORY_TYPES.get(memory_type, "📝").replace(" ", "_")
    return f"{type_prefix}_{timestamp}.md"


def create_memory_content(content: str, memory_type: str, tags: list, source: str = "飞书私聊") -> str:
    """创建记忆文件内容"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    emoji = MEMORY_TYPES.get(memory_type, "📝")
    tags_str = " ".join([f"#{tag}" for tag in tags]) if tags else "#未分类"
    
    template = f"""# {emoji} {content[:50]}{'...' if len(content) > 50 else ''}

**时间**: {timestamp}
**来源**: {source}
**类型**: {memory_type}
**标签**: {tags_str}

---

## 内容

{content}

---

## 关联

- [[相关记忆 1]]
- [[相关记忆 2]]

---

## 行动项

- [ ] 需要跟进的事项

---

*由 OpenClaw 灵感记录技能自动创建*
"""
    return template


def search_memory(query: str, max_results: int = 10) -> List[Dict]:
    """
    搜索记忆库，返回相关结果
    
    使用 OpenClaw 的 memory_search 工具进行语义检索
    """
    try:
        # 调用 OpenClaw 的 memory_search 工具
        import subprocess
        import tempfile
        
        # 创建一个临时脚本来调用 memory_search
        search_script = f"""
import sys
sys.path.insert(0, r'{Path.home() / ".openclaw"}')

# 模拟 memory_search 调用
query = '''{query}'''
max_results = {max_results}

# 搜索 memory 目录下的所有 md 文件
results = []
memory_dir = r'{MEMORY_SEARCH_DIR}'

if Path(memory_dir).exists():
    for md_file in Path(memory_dir).rglob("*.md"):
        if md_file.name.startswith('~') or md_file.name.startswith('.'):
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8')
            # 简单的相关性评分：基于关键词匹配
            query_words = set(query.lower().split())
            content_lower = content.lower()
            
            match_count = sum(1 for word in query_words if word in content_lower)
            score = match_count / len(query_words) if query_words else 0
            
            if score > 0.1:  # 最低阈值
                results.append({{
                    'path': str(md_file),
                    'score': score,
                    'content': content[:500]  # 只取前 500 字符
                }})
        except Exception as e:
            continue

# 按分数排序
results.sort(key=lambda x: x['score'], reverse=True)
print(json.dumps(results[:max_results], ensure_ascii=False, indent=2))
"""
        
        # 执行搜索（简化版本，实际应该调用 memory_search 工具）
        # 这里使用简单的文件搜索作为替代
        results = []
        if MEMORY_SEARCH_DIR.exists():
            for md_file in MEMORY_SEARCH_DIR.rglob("*.md"):
                if md_file.name.startswith('~') or md_file.name.startswith('.'):
                    continue
                
                try:
                    content = md_file.read_text(encoding='utf-8')
                    # 简单的相关性评分
                    query_words = query.lower().split()
                    content_lower = content.lower()
                    
                    match_count = sum(1 for word in query_words if len(word) > 2 and word in content_lower)
                    score = match_count / len([w for w in query_words if len(w) > 2]) if query_words else 0
                    
                    if score > SIMILARITY_THRESHOLD:
                        results.append({
                            'path': str(md_file),
                            'score': round(score, 3),
                            'content': content[:800],
                            'title': md_file.stem
                        })
                except Exception as e:
                    continue
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]
        
    except Exception as e:
        print(f"⚠️  搜索失败：{e}")
        return []


def find_related_inspirations(content: str, tags: list, current_file: str) -> List[Dict]:
    """
    查找与当前灵感相关的历史灵感
    
    策略：
    1. 基于内容语义搜索
    2. 基于标签匹配
    3. 排除当前文件
    """
    # 合并搜索查询（内容 + 标签）
    search_query = f"{content} {' '.join(tags)}"
    
    # 搜索相关记忆
    results = search_memory(search_query, max_results=MAX_RELATED_COUNT + 5)
    
    # 过滤掉当前文件
    results = [r for r in results if r['path'] != current_file]
    
    # 限制返回数量
    return results[:MAX_RELATED_COUNT]


def format_related_results(results: List[Dict]) -> str:
    """格式化相关结果输出"""
    if not results:
        return ""
    
    output = "\n\n🔗 **发现相关灵感**:\n\n"
    for i, r in enumerate(results, 1):
        score = r['score']
        path = Path(r['path'])
        title = path.stem
        output += f"{i}. **{title}** (相关度：{score:.0%})\n"
        output += f"   路径：`{path.relative_to(MEMORY_SEARCH_DIR) if str(path).startswith(str(MEMORY_SEARCH_DIR)) else path.name}`\n"
        # 提取内容的前 100 字作为摘要
        content_preview = r['content'][:200].replace('\n', ' ').strip()
        if len(r['content']) > 200:
            content_preview += "..."
        output += f"   摘要：{content_preview}\n\n"
    
    return output


def record_inspiration(content: str, memory_type: str = "想法", tags: list = None, 
                       source: str = "飞书私聊", output_dir: Path = None,
                       enable_related: bool = True) -> Dict:
    """
    记录灵感，并自动查找相关历史灵感
    
    Returns:
        Dict with 'filepath' and 'related' (list of related inspirations)
    """
    if output_dir is None:
        output_dir = DEFAULT_MEMORY_DIR
    
    # 确保目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    filename = generate_filename(memory_type)
    filepath = output_dir / filename
    
    # 创建内容
    content_md = create_memory_content(content, memory_type, tags or [], source)
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_md)
    
    # 查找相关灵感
    related = []
    if enable_related:
        related = find_related_inspirations(content, tags or [], str(filepath))
    
    return {
        'filepath': filepath,
        'related': related
    }


def main():
    parser = argparse.ArgumentParser(description="灵感记录工具", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("content", nargs="?", help="要记录的内容")
    parser.add_argument("--file", "-f", help="从文件读取内容")
    parser.add_argument("--type", "-t", default="想法", choices=list(MEMORY_TYPES.keys()), help="记忆类型")
    parser.add_argument("--tags", nargs="+", default=[], help="标签列表")
    parser.add_argument("--source", "-s", default="飞书私聊", help="来源")
    parser.add_argument("--output", "-o", help="输出目录")
    parser.add_argument("--no-related", action="store_true", help="禁用相关灵感查找")
    
    args = parser.parse_args()
    
    # 获取内容
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    elif args.content:
        content = args.content
    else:
        parser.print_help()
        return
    
    # 记录灵感
    output_dir = Path(args.output) if args.output else None
    result = record_inspiration(
        content, 
        args.type, 
        args.tags, 
        args.source, 
        output_dir,
        enable_related=not args.no_related
    )
    
    # 输出结果
    filepath = result['filepath']
    print(f"✅ 灵感已记录：{filepath}")
    
    # 输出相关灵感
    if result['related']:
        print(format_related_results(result['related']))
    else:
        print("\n💡 未找到相关历史灵感（这是新方向！）")


if __name__ == "__main__":
    main()
