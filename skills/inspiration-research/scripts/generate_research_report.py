#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵感深度研究报告生成脚本

用法:
    python generate_research_report.py --input "灵感内容" --output report.md
    python generate_research_report.py --inspiration-file inbox/2026-02-26-001.md

功能:
    - 拆解灵感中的核心问题
    - 搜索相关资料
    - 建立资料与思考的映射
    - 生成结构化研究报告
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

# 默认配置
DEFAULT_OUTPUT_DIR = Path.home() / ".openclaw" / "workspace" / "memory" / "reports"
DEFAULT_INBOX_DIR = Path.home() / ".openclaw" / "workspace" / "memory" / "inbox"
DESKTOP_BASE_DIR = Path.home() / "Desktop" / "灵感与研究报告"
DESKTOP_INBOX_DIR = DESKTOP_BASE_DIR / "原始灵感"
DESKTOP_REPORT_DIR = DESKTOP_BASE_DIR / "研究报告"
SEARCH_DELAY_SECONDS = 2  # 搜索间隔，避免 API 限流


def parse_inspiration(text: str) -> Dict:
    """
    解析灵感内容，提取核心问题和待探索方向
    
    返回：
    {
        "core_questions": ["问题 1", "问题 2"],
        "tags": ["#标签 1", "#标签 2"],
        "待探索": ["方向 1", "方向 2"]
    }
    """
    # TODO: 实际应该用 LLM 解析
    # 这里简化处理
    
    questions = []
    tags = []
    to_explore = []
    
    # 提取问题（包含"？"的句子）
    for line in text.split('\n'):
        if '？' in line or '?' in line:
            questions.append(line.strip())
        if line.startswith('#'):
            tags.append(line.strip())
    
    # 提取待探索（包含"待探索"、"需要"的部分）
    in_to_explore = False
    for line in text.split('\n'):
        if '待探索' in line:
            in_to_explore = True
            continue
        if in_to_explore and line.startswith('-'):
            to_explore.append(line.strip())
    
    return {
        "core_questions": questions[:5],  # 最多 5 个问题
        "tags": tags,
        "to_explore": to_explore
    }


def generate_search_queries(questions: List[str]) -> List[str]:
    """
    根据问题生成搜索词
    
    每个问题生成 1-2 个搜索词（中英文混合）
    """
    queries = []
    
    for question in questions:
        # 提取关键词（简化处理）
        keywords = question.replace('？', '').replace('?', '').replace('是不是', '').replace('应该', '')
        
        # 生成中英文搜索词
        queries.append(keywords.strip()[:50])  # 限制长度
        
        # 如果是中文问题，添加英文搜索词
        if any('\u4e00' <= c <= '\u9fff' for c in keywords):
            queries.append(f"{keywords} AI enterprise 2026"[:50])
    
    return queries[:10]  # 最多 10 个搜索词


def search_web(query: str, count: int = 5) -> List[Dict]:
    """
    使用 web_search 搜索
    
    返回：[{"title": "...", "url": "...", "description": "..."}, ...]
    """
    # TODO: 实际调用 web_search API
    # 这里返回模拟数据
    return []


def map_to_inspiration(search_result: Dict, inspiration: str) -> str:
    """
    建立搜索结果与灵感的映射关系
    
    返回："验证"、"驳斥"、"部分回答"、"新视角"
    """
    # TODO: 实际应该用 LLM 分析
    # 这里简化处理
    return "验证"


def generate_report(inspiration_text: str, search_results: List[Dict], inspiration_file_path: str = None) -> str:
    """
    生成研究报告
    
    格式与昨晚的报告一致
    强制要求：必须完整包含原始灵感
    """
    # 如果提供了灵感文件路径，读取文件内容（确保完整性）
    if inspiration_file_path:
        try:
            with open(inspiration_file_path, 'r', encoding='utf-8') as f:
                inspiration_text = f.read()
            print(f"✅ 已从文件加载原始灵感：{inspiration_file_path}")
        except Exception as e:
            print(f"⚠️ 读取灵感文件失败：{e}，使用传入的文本")
    
    parsed = parse_inspiration(inspiration_text)
    
    # 验证：确保灵感内容不为空
    if not inspiration_text or len(inspiration_text.strip()) < 10:
        raise ValueError("❌ 错误：原始灵感内容为空或过短，无法生成报告")
    
    report = f"""# 灵感研究报告：[标题]

**灵感来源**: 用户深度思考  
**报告生成**: {datetime.now().strftime("%Y-%m-%d %H:%M")}  
**搜索关键词**: {', '.join(generate_search_queries(parsed['core_questions']))}

---

## 💡 原始灵感记录

**⚠️ 重要**：以下内容为用户原始灵感，完整记录如下：

---

{inspiration_text}

---

**待探索**:
"""
    
    for item in parsed['to_explore']:
        report += f"- [ ] {item}\n"
    
    report += """
---

## 💡 核心问题拆解

"""
    
    for i, question in enumerate(parsed['core_questions'], 1):
        report += f"### 问题{i}：{question}\n\n"
    
    report += """---

## 📰 参考资料与你的思考映射

"""
    
    for i, result in enumerate(search_results[:7], 1):
        report += f"""### 资料{i}：[{result.get('title', '无标题')}]({result.get('url', '#')})
**来源**: {result.get('siteName', '未知')} | **时间**: {result.get('published', '未知')}

**摘要**:
- [要点 1]
- [要点 2]

**💡 与你的思考关联**:
> **验证/驳斥/部分回答**：[具体关联内容]

---

"""
    
    report += """## 💡 我的思考与建议

### 针对你的问题 1

**你的假设**：[用户的观点]

**资料的验证**：
| 你的假设 | 资料验证 | 结论 |
|---------|---------|------|
| ... | ... | ... |

**我的建议**：[具体建议]

---

## 📌 下一步行动

### 立即行动（本周）
- [ ] ...

### 中期行动（1-3 个月）
- [ ] ...

### 长期行动（3-12 个月）
- [ ] ...

---

*报告由 OpenClaw 自动生成 | 数据来源：Brave Search*
"""
    
    return report


def save_report(content: str, output_path: Path, desktop_path: Path = None) -> None:
    """保存报告到文件（双存储）"""
    # 保存到工作区
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 保存到桌面（如果指定了桌面路径）
    if desktop_path:
        desktop_path.parent.mkdir(parents=True, exist_ok=True)
        with open(desktop_path, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    parser = argparse.ArgumentParser(description="灵感深度研究报告生成工具")
    parser.add_argument("--input", "-i", type=str, help="灵感文本内容")
    parser.add_argument("--inspiration-file", type=Path, help="灵感文件路径")
    parser.add_argument("--output", "-o", type=Path, help="输出报告路径")
    
    args = parser.parse_args()
    
    # 获取灵感内容
    if args.input:
        inspiration_text = args.input
    elif args.inspiration_file:
        with open(args.inspiration_file, 'r', encoding='utf-8') as f:
            inspiration_text = f.read()
    else:
        print("错误：请提供 --input 或 --inspiration-file")
        return
    
    print(f"🚀 开始生成研究报告...")
    print(f"📝 灵感内容：{len(inspiration_text)} 字")
    
    # 解析灵感
    parsed = parse_inspiration(inspiration_text)
    print(f"❓ 核心问题：{len(parsed['core_questions'])} 个")
    
    # 生成搜索词
    queries = generate_search_queries(parsed['core_questions'])
    print(f"🔍 搜索词：{len(queries)} 个")
    
    # 搜索（模拟）
    search_results = []
    for i, query in enumerate(queries):
        if i > 0:
            print(f"⏳ 等待 {SEARCH_DELAY_SECONDS}秒...")
            time.sleep(SEARCH_DELAY_SECONDS)
        print(f"🔍 搜索：{query}")
        # results = search_web(query)
        # search_results.extend(results)
    
    # 生成报告
    report = generate_report(inspiration_text, search_results)
    
    # 保存报告（双存储）
    if args.output:
        desktop_path = DESKTOP_REPORT_DIR / args.output.name if args.output.name else None
        save_report(report, args.output, desktop_path)
        print(f"✅ 报告已保存到：{args.output}")
        if desktop_path:
            print(f"✅ 报告已同步到桌面：{desktop_path}")
    else:
        output_path = DEFAULT_OUTPUT_DIR / f"灵感研究报告_{datetime.now().strftime('%Y-%m-%d')}.md"
        desktop_path = DESKTOP_REPORT_DIR / output_path.name
        save_report(report, output_path, desktop_path)
        print(f"✅ 报告已保存到：{output_path}")
        print(f"✅ 报告已同步到桌面：{desktop_path}")


if __name__ == "__main__":
    main()
