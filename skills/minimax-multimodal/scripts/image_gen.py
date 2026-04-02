#!/usr/bin/env python3
"""
MiniMax 图片生成脚本
支持直接发送图片到飞书
"""

import argparse
import os
import sys
import requests
import base64
import json

# MiniMax API 配置
MINIMAX_API_URL = "https://api.minimaxi.com/v1/image_generation"

# 默认 API Key
# API Key 从环境变量读取

# 飞书配置
FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
FEISHU_API_URL = "https://open.feishu.cn/open-apis"


def get_minimax_key():
    """获取 MiniMax API Key"""
    return os.environ.get("MINIMAX_API_KEY", "")


def get_feishu_token():
    """获取飞书 access token"""
    url = f"{FEISHU_API_URL}/auth/v3/tenant_access_token/internal"
    data = {"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
    resp = requests.post(url, json=data)
    result = resp.json()
    return result.get("tenant_access_token")


def generate_image(prompt, aspect_ratio="16:9", model="image-01", output="output.png"):
    """生成图片"""
    api_key = get_minimax_key()
    
    payload = {
        "model": model,
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "response_format": "base64"
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"正在生成图片...")
    print(f"  描述: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
    print(f"  纵横比: {aspect_ratio}")
    
    response = requests.post(MINIMAX_API_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"❌ 请求失败: {response.status_code} - {response.text}")
        return None
    
    result = response.json()
    if result.get("base_resp", {}).get("status_code") != 0:
        print(f"❌ API 错误: {result}")
        return None
    
    # 解析 base64 编码的图片
    image_b64 = result["data"]["image_base64"]
    if isinstance(image_b64, list):
        image_b64 = image_b64[0]
    
    image_data = base64.b64decode(image_b64)
    
    with open(output, "wb") as f:
        f.write(image_data)
    
    print(f"✅ 图片生成成功: {output}")
    print(f"  大小: {len(image_data)} bytes")
    
    return output


def send_image_to_feishu(image_path, user_open_id="ou_b07ee03a908da23c663e6ae56cab046d"):
    """发送图片到飞书"""
    # 获取 token
    token = get_feishu_token()
    if not token:
        print("❌ 无法获取飞书 access token")
        return False
    
    # 上传图片
    url = f"{FEISHU_API_URL}/im/v1/images"
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(image_path, "rb") as f:
        files = {
            "image_type": (None, "message"),
            "image": (os.path.basename(image_path), f, "image/png")
        }
        resp = requests.post(url, headers=headers, files=files)
    
    result = resp.json()
    if result.get("code") != 0:
        print(f"❌ 上传失败: {result}")
        return False
    
    image_key = result["data"]["image_key"]
    print(f"✅ 图片上传成功: {image_key}")
    
    # 发送消息
    msg_url = f"{FEISHU_API_URL}/im/v1/messages?receive_id_type=open_id"
    msg_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    msg_data = {
        "receive_id": user_open_id,
        "msg_type": "image",
        "content": json.dumps({"image_key": image_key})
    }
    
    msg_resp = requests.post(msg_url, headers=msg_headers, json=msg_data)
    msg_result = msg_resp.json()
    
    if msg_result.get("code") == 0:
        print(f"✅ 图片消息发送成功!")
        return True
    else:
        print(f"❌ 发送失败: {msg_result}")
        return False


def main():
    parser = argparse.ArgumentParser(description="MiniMax 图片生成")
    parser.add_argument("prompt", help="图片描述提示词")
    parser.add_argument("--aspect-ratio", "-a", default="16:9",
                       help="纵横比: 1:1, 3:4, 4:3, 16:9, 9:16 (默认: 16:9)")
    parser.add_argument("--model", "-m", default="image-01",
                       help="模型 (默认: image-01)")
    parser.add_argument("--output", "-o", default="output.png",
                       help="输出文件 (默认: output.png)")
    parser.add_argument("--send-to-feishu", action="store_true",
                       help="生成后发送到飞书")
    parser.add_argument("--user-id", default="ou_b07ee03a908da23c663e6ae56cab046d",
                       help="飞书用户 open_id (默认: 曹晓雨)")
    
    args = parser.parse_args()
    
    # 生成图片
    output_file = generate_image(
        args.prompt,
        aspect_ratio=args.aspect_ratio,
        model=args.model,
        output=args.output
    )
    
    if output_file and args.send_to_feishu:
        print("\n正在发送到飞书...")
        send_image_to_feishu(output_file, args.user_id)


if __name__ == "__main__":
    main()
