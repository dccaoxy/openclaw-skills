#!/usr/bin/env python3
"""同步技能库到飞书文档 LkmldObEfoewtBxqkQHcs2GGnif"""
import urllib.request
import json
import os

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

def read_doc_blocks(token, doc_id):
    """读取文档所有blocks"""
    blocks = []
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks?page_size=500"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
        items = result.get("data", {}).get("items", [])
        for item in items:
            block_id = item.get("block_id", "")
            block_type = item.get("block_type", 0)
            # 提取文本内容
            text_content = ""
            if "text" in item and item["text"]:
                for elem in item["text"].get("elements", []):
                    if "text_run" in elem and elem["text_run"]:
                        text_content += elem["text_run"].get("content", "")
            blocks.append({"id": block_id, "type": block_type, "content": text_content})
    return blocks

def add_block(token, doc_id, parent_block_id, block_data):
    """添加单个block"""
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{parent_block_id}/children"
    req = urllib.request.Request(
        url,
        data=json.dumps({"children": [block_data]}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"Error adding block: {e}")
        return None

def extract_heading1_text(content):
    """从markdown提取heading1"""
    lines = content.split('\n')
    for line in lines:
        if line.startswith('## ') and not line.startswith('### '):
            return line.replace('## ', '').strip()
    return None

def extract_heading2_text(content):
    """从markdown提取heading2"""
    lines = content.split('\n')
    for line in lines:
        if line.startswith('### '):
            return line.replace('### ', '').strip()
    return None

def parse_skills_md(content):
    """解析skills_library.md，提取技能分类"""
    skills = {}  # {category: {skill_name: full_content}}
    current_category = None
    current_skill = None
    current_content = []
    
    lines = content.split('\n')
    for line in lines:
        if line.startswith('## ') and not line.startswith('### '):
            if current_category and current_content:
                if current_skill:
                    if current_category not in skills:
                        skills[current_category] = {}
                    skills[current_category][current_skill] = '\n'.join(current_content)
            current_category = line.replace('## ', '').strip()
            current_skill = None
            current_content = []
        elif line.startswith('### '):
            if current_skill and current_content:
                if current_category not in skills:
                    skills[current_category] = {}
                skills[current_category][current_skill] = '\n'.join(current_content)
            current_skill = line.replace('### ', '').strip()
            current_content = []
        else:
            current_content.append(line)
    
    # 保存最后一个
    if current_category and current_skill and current_content:
        if current_category not in skills:
            skills[current_category] = {}
        skills[current_category][current_skill] = '\n'.join(current_content)
    
    return skills

def main():
    print("=== 飞书技能库同步 ===")
    
    # 1. 获取token
    print("1. 获取token...")
    token = get_token()
    print(f"   Token获取成功")
    
    # 2. 读取飞书文档
    print("2. 读取飞书文档...")
    blocks = read_doc_blocks(token, DOC_ID)
    print(f"   文档共有 {len(blocks)} 个blocks")
    
    # 3. 提取现有技能名称
    existing_skills = set()
    for block in blocks:
        content = block.get("content", "").strip()
        if content and len(content) < 100:  # 技能名称通常较短
            existing_skills.add(content)
    
    print(f"   现有技能条目: {len(existing_skills)}")
    
    # 4. 读取本地技能库
    print("3. 读取本地技能库...")
    with open(SKILLS_FILE, 'r') as f:
        local_content = f.read()
    
    local_skills = parse_skills_md(local_content)
    print(f"   本地技能分类: {list(local_skills.keys())}")
    
    # 5. 对比并找出新增
    print("4. 对比新旧内容...")
    new_skills_count = 0
    skipped_count = 0
    
    for category, skills in local_skills.items():
        print(f"   分类: {category}")
        for skill_name, skill_content in skills.items():
            if skill_name in existing_skills:
                skipped_count += 1
                print(f"     - {skill_name}: 已存在，跳过")
            else:
                new_skills_count += 1
                print(f"     + {skill_name}: 新增")
    
    print(f"\n汇总完成")
    print(f"新增技能数: {new_skills_count}")
    print(f"跳过数: {skipped_count}")
    
    # 保存结果供后续使用
    result = {
        "new_skills": new_skills_count,
        "skipped": skipped_count,
        "existing_count": len(existing_skills)
    }
    with open("/tmp/feishu_sync_result.json", 'w') as f:
        json.dump(result, f)

if __name__ == "__main__":
    main()
