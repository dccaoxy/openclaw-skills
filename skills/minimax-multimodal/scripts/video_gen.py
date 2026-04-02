#!/usr/bin/env python3
"""
MiniMax 视频生成脚本
支持直接发送视频到飞书
"""

import argparse
import os
import sys
import requests
import time
import json

# MiniMax API 配置
MINIMAX_API_URL = "https://api.minimaxi.com/v1"
VIDEO_GENERATION_URL = f"{MINIMAX_API_URL}/video_generation"
VIDEO_QUERY_URL = f"{MINIMAX_API_URL}/query/video_generation"
FILE_RETRIEVE_URL = f"{MINIMAX_API_URL}/files/retrieve"

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


def generate_video(prompt, duration=6, resolution="768P", model="MiniMax-Hailuo-2.3"):
    """生成视频（异步）"""
    api_key = get_minimax_key()
    
    payload = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"正在提交视频生成任务...")
    print(f"  描述: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
    print(f"  时长: {duration}秒")
    print(f"  分辨率: {resolution}")
    
    response = requests.post(VIDEO_GENERATION_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"❌ 请求失败: {response.status_code} - {response.text}")
        return None
    
    result = response.json()
    if result.get("base_resp", {}).get("status_code") != 0:
        print(f"❌ API 错误: {result}")
        return None
    
    task_id = result.get("task_id")
    print(f"✅ 任务提交成功!")
    print(f"  Task ID: {task_id}")
    print(f"  正在等待视频生成（预计1-2分钟）...")
    
    # 轮询查询视频状态
    video_path = poll_video_status(task_id)
    return video_path


def poll_video_status(task_id, max_wait=180):
    """轮询视频生成状态"""
    api_key = get_minimax_key()
    headers = {"Authorization": f"Bearer {api_key}"}
    
    start_time = time.time()
    poll_interval = 5
    
    while time.time() - start_time < max_wait:
        url = f"{VIDEO_QUERY_URL}?task_id={task_id}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"  查询请求失败，等待重试...")
            time.sleep(poll_interval)
            continue
        
        result = response.json()
        
        # 检查状态
        status = result.get("status")
        
        if status == "Success":
            file_id = result.get("file_id")
            print(f"\n✅ 视频生成成功!")
            print(f"  File ID: {file_id}")
            
            # 获取下载链接
            download_url = get_file_download_url(file_id)
            if download_url:
                # 下载视频
                video_path = download_and_save_video(download_url)
                return video_path
            return None
        
        elif status == "Fail":
            print(f"❌ 视频生成失败")
            return None
        
        else:
            elapsed = int(time.time() - start_time)
            print(f"  等待中... ({elapsed}s) 状态: {status}")
            time.sleep(poll_interval)
    
    print(f"❌ 等待超时（{max_wait}秒）")
    return None


def get_file_download_url(file_id):
    """获取文件下载链接"""
    api_key = get_minimax_key()
    headers = {"Authorization": f"Bearer {api_key}"}
    
    url = f"{FILE_RETRIEVE_URL}?file_id={file_id}"
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        print(f"❌ 获取下载链接失败: {response.status_code}")
        return None
    
    result = response.json()
    download_url = result.get("file", {}).get("download_url")
    
    if download_url:
        print(f"  下载链接获取成功")
    
    return download_url


def download_and_save_video(url, output="output.mp4"):
    """下载视频并保存"""
    print(f"  正在下载视频...")
    
    response = requests.get(url, stream=True, timeout=60)
    
    if response.status_code != 200:
        print(f"❌ 下载失败: {response.status_code}")
        return None
    
    total_size = 0
    with open(output, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                total_size += len(chunk)
    
    print(f"✅ 视频保存成功: {output}")
    print(f"  大小: {total_size} bytes")
    
    return output


def send_video_to_feishu(video_path, thumbnail_path=None, 
                         user_open_id="ou_b07ee03a908da23c663e6ae56cab046d"):
    """发送视频到飞书"""
    # 获取 token
    token = get_feishu_token()
    if not token:
        print("❌ 无法获取飞书 access token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 上传视频
    url = f"{FEISHU_API_URL}/im/v1/files"
    
    # 获取视频时长（默认6秒）
    duration_ms = 6000
    
    with open(video_path, "rb") as f:
        files = {
            "file_type": ("mp4", "video/mp4"),
            "file_name": (os.path.basename(video_path), open(video_path, "rb"), "video/mp4"),
            "duration": (None, str(duration_ms)),
        }
        resp = requests.post(url, headers=headers, files=files)
    
    result = resp.json()
    if result.get("code") != 0:
        print(f"❌ 视频上传失败: {result}")
        return False
    
    video_key = result["data"]["file_key"]
    print(f"✅ 视频上传成功: {video_key}")
    
    # 如果有封面图，先上传获取 image_key
    image_key = None
    if thumbnail_path and os.path.exists(thumbnail_path):
        img_url = f"{FEISHU_API_URL}/im/v1/images"
        with open(thumbnail_path, "rb") as f:
            img_files = {
                "image_type": (None, "message"),
                "image": (os.path.basename(thumbnail_path), f, "image/png")
            }
            img_resp = requests.post(img_url, headers=headers, files=img_files)
        img_result = img_resp.json()
        if img_result.get("code") == 0:
            image_key = img_result["data"]["image_key"]
            print(f"✅ 封面上传成功: {image_key}")
    
    # 发送视频消息（使用 media 类型）
    msg_url = f"{FEISHU_API_URL}/im/v1/messages?receive_id_type=open_id"
    msg_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # media 类型的 content 需要包含 file_key 和 image_key
    content = {"file_key": video_key}
    if image_key:
        content["image_key"] = image_key
    
    msg_data = {
        "receive_id": user_open_id,
        "msg_type": "media",
        "content": json.dumps(content)
    }
    
    msg_resp = requests.post(msg_url, headers=msg_headers, json=msg_data)
    msg_result = msg_resp.json()
    
    if msg_result.get("code") == 0:
        print(f"✅ 视频消息发送成功!")
        return True
    else:
        print(f"❌ 发送失败: {msg_result}")
        return False


def main():
    parser = argparse.ArgumentParser(description="MiniMax 视频生成")
    parser.add_argument("prompt", help="视频描述提示词")
    parser.add_argument("--duration", "-d", type=int, default=6,
                       help="时长（秒）: 6 或 10 (默认: 6)")
    parser.add_argument("--resolution", "-r", default="768P",
                       help="分辨率: 512P, 768P, 1080P (默认: 768P)")
    parser.add_argument("--model", "-m", default="MiniMax-Hailuo-2.3",
                       help="模型 (默认: MiniMax-Hailuo-2.3)")
    parser.add_argument("--output", "-o", default="output.mp4",
                       help="输出文件 (默认: output.mp4)")
    parser.add_argument("--send-to-feishu", action="store_true",
                       help="生成后发送到飞书")
    parser.add_argument("--thumbnail", "-t", 
                       help="视频封面图片路径（发送时需要）")
    parser.add_argument("--user-id", default="ou_b07ee03a908da23c663e6ae56cab046d",
                       help="飞书用户 open_id (默认: 曹晓雨)")
    
    args = parser.parse_args()
    
    # 生成视频
    output_file = generate_video(
        args.prompt,
        duration=args.duration,
        resolution=args.resolution,
        model=args.model
    )
    
    if output_file and args.send_to_feishu:
        print("\n正在发送到飞书...")
        send_video_to_feishu(output_file, args.thumbnail, args.user_id)


if __name__ == "__main__":
    main()
