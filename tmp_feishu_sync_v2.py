#!/usr/bin/env python3
"""同步技能库到飞书文档 - 添加缺失的技能"""
import urllib.request
import json
import os
import re

DOC_ID = "LkmldObEfoewtBxqkQHcs2GGnif"
APP_ID = "cli_a94e7271c4fa9bd3"
APP_SECRET = "Spy8MoaoiDhYAheKRchLIf2mHUPsz7f6"
SKILLS_FILE = os.path.expanduser("~/.openclaw/agent_review/skills_library.md")

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())["tenant_access_token"]

def read_all_text(token, doc_id):
    """读取文档所有文本内容"""
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks?page_size=500"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
        items = result.get("data", {}).get("items", [])
        all_text = []
        for item in items:
            for key in ['text', 'heading1', 'heading2', 'heading3', 'bullet']:
                if key in item and item[key]:
                    for elem in item[key].get("elements", []):
                        if "text_run" in elem:
                            all_text.append(elem["text_run"].get("content", ""))
        return "".join(all_text)

def add_block_after(token, doc_id, after_block_id, block_data):
    """在指定block后插入新block"""
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{after_block_id}/children"
    req = urllib.request.Request(
        url,
        data=json.dumps({"children": [block_data], "index": 0}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"    Error: {e}")
        return None

def make_text_block(content):
    return {"block_type": 2, "text": {"elements": [{"text_run": {"content": content, "text_element_style": {}}}], "style": {}}}

def make_heading2(content):
    return {"block_type": 4, "heading1": {"elements": [{"text_run": {"content": content, "text_element_style": {}}}], "style": {}}}

def make_bullet(content):
    return {"block_type": 12, "bullet": {"elements": [{"text_run": {"content": content, "text_element_style": {}}}], "style": {}}}

def make_code_block(content):
    return {"block_type": 14, "code": {"elements": [{"text_run": {"content": content, "text_element_style": {}}}], "style": {"language": 1}}}

def parse_skills(content):
    """解析skills_library.md，返回技能列表"""
    skills = []
    current_cat = None
    current_skill = None
    current_content_lines = []
    in_code = False
    
    lines = content.split('\n')
    for line in lines:
        if line.startswith('## ') and not line.startswith('### '):
            if current_skill and current_content_lines:
                skills.append((current_cat, current_skill, '\n'.join(current_content_lines)))
            current_cat = line.replace('## ', '').strip()
            current_skill = None
            current_content_lines = []
        elif line.startswith('### '):
            if current_skill and current_content_lines:
                skills.append((current_cat, current_skill, '\n'.join(current_content_lines)))
            current_skill = line.replace('### ', '').strip()
            current_content_lines = []
        elif line.startswith('```'):
            in_code = not in_code
            current_content_lines.append(line)
        else:
            current_content_lines.append(line)
    
    if current_skill and current_content_lines:
        skills.append((current_cat, current_skill, '\n'.join(current_content_lines)))
    
    return skills

def main():
    print("=== 飞书技能库同步 v2 ===")
    
    # 1. 获取token
    print("1. 获取token...")
    token = get_token()
    print("   OK")
    
    # 2. 读取文档全文
    print("2. 读取飞书文档...")
    existing_text = read_all_text(token, DOC_ID)
    print(f"   文档文本长度: {len(existing_text)}")
    
    # 3. 读取本地技能库
    print("3. 读取本地技能库...")
    with open(SKILLS_FILE, 'r') as f:
        local_content = f.read()
    
    local_skills = parse_skills(local_content)
    print(f"   本地技能数: {len(local_skills)}")
    
    # 4. 找出新增
    new_skills = []
    skipped = []
    for cat, skill, content in local_skills:
        # 检查是否已存在（通过关键词匹配）
        if skill in existing_text or f"{cat}\n{skill}" in existing_text:
            skipped.append((cat, skill))
        else:
            new_skills.append((cat, skill, content))
    
    print(f"4. 新增技能: {len(new_skills)}, 跳过: {len(skipped)}")
    
    # 5. 找到插入点 - 在 block 93 (浏览器操作 section 末尾) 之后
    # 实际上，我们应该在现有技能库 section 末尾添加新内容
    # 查看 blocks 找到合适的插入位置 - 在"浏览器操作"之后
    insert_after_block = "doxcnqGKzzt65rh6b7VP4ekaCBd"  # 浏览器操作 section 的最后已知block
    
    # 找到浏览器操作 section 后第一个非空block的位置
    # 我们会在文档末尾添加（简单可靠）
    insert_after_block = DOC_ID  # 在根block下添加
    
    print(f"5. 开始写入新技能...")
    
    # 按分类组织新技能
    by_category = {}
    for cat, skill, content in new_skills:
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append((skill, content))
    
    added_count = 0
    for cat, items in by_category.items():
        print(f"   添加分类: {cat} ({len(items)} 个技能)")
        
        # 添加分类 heading
        result = add_block_after(token, DOC_ID, insert_after_block, make_heading2(cat))
        insert_after_block = DOC_ID  # 继续在根级别添加
        if result:
            try:
                new_block_id = result["data"]["children"][0]["block_id"]
                insert_after_block = new_block_id
            except:
                pass
        added_count += 1
        
        for skill, content in items:
            print(f"     + {skill}")
            added_count += 1
            
            # 添加技能标题
            title_block = {"block_type": 2, "text": {"elements": [{"text_run": {"content": f"**{skill}**", "text_element_style": {}}}], "style": {}}}
            add_block_after(token, DOC_ID, insert_after_block, title_block)
            insert_after_block = DOC_ID
            
            # 处理内容 - 分离普通文本和代码块
            lines = content.split('\n')
            for line in lines:
                line = line.rstrip()
                if line.startswith('```'):
                    continue  # 跳过代码块标记
                elif line.startswith('**来源**'):
                    src_block = {"block_type": 2, "text": {"elements": [{"text_run": {"content": line, "text_element_style": {"italic": True}}}], "style": {}}}
                    add_block_after(token, DOC_ID, insert_after_block, src_block)
                    insert_after_block = DOC_ID
                elif line.startswith('#'):
                    h_block = {"block_type": 4, "heading1": {"elements": [{"text_run": {"content": line, "text_element_style": {}}}], "style": {}}}
                    add_block_after(token, DOC_ID, insert_after_block, h_block)
                    insert_after_block = DOC_ID
                elif line.startswith('- '):
                    b_block = make_bullet(line)
                    add_block_after(token, DOC_ID, insert_after_block, b_block)
                    insert_after_block = DOC_ID
                elif line.strip():
                    t_block = make_text_block(line)
                    add_block_after(token, DOC_ID, insert_after_block, t_block)
                    insert_after_block = DOC_ID
    
    print(f"\n汇总完成")
    print(f"新增技能数: {len(new_skills)}")
    print(f"跳过数: {len(skipped)}")
    print(f"总写入blocks: {added_count}")

if __name__ == "__main__":
    main()
