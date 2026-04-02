#!/usr/bin/env python3
"""
MiniMax 语音合成脚本
支持直接发送语音到飞书
"""

import argparse
import os
import sys
import requests
import binascii
import json
import subprocess

# MiniMax API 配置
MINIMAX_API_URL = "https://api.minimaxi.com/v1/t2a_v2"

# 默认 API Key（如果没有设置环境变量）
DEFAULT_API_KEY = "sk-cp-d-Yq48OkLtw3m7ip6yIpT11DJoC7nChNJ5JGTblW6T5feNi2IYP1hM9CTvtFX9H3v1SzMby0HyNN3O09Ewh3m8joPZU70X5J2jICElJXdsTuBir2AciA6kA"

# 飞书配置
FEISHU_APP_ID = "cli_a93d390a55f99cca"
FEISHU_APP_SECRET = "hnXqsu6Y4stY2FQMh0AIEBRNzu5q1ijN"
FEISHU_API_URL = "https://open.feishu.cn/open-apis"


def get_minimax_key():
    """获取 MiniMax API Key"""
    return os.environ.get("MINIMAX_API_KEY", DEFAULT_API_KEY)


def get_feishu_token():
    """获取飞书 access token"""
    url = f"{FEISHU_API_URL}/auth/v3/tenant_access_token/internal"
    data = {"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
    resp = requests.post(url, json=data)
    result = resp.json()
    return result.get("tenant_access_token")


def generate_speech(text, voice="Chinese_Male_Adult", model="speech-2.8-hd", 
                    speed=1.0, emotion="neutral", output="output.mp3"):
    """生成语音"""
    api_key = get_minimax_key()
    
    # 构建音色 ID
    voice_id = voice
    
    payload = {
        "model": model,
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": speed,
            "vol": 1,
            "pitch": 0,
            "emotion": emotion
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1
        }
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"正在生成语音...")
    print(f"  文本: {text[:50]}{'...' if len(text) > 50 else ''}")
    print(f"  音色: {voice}")
    print(f"  情绪: {emotion}")
    
    response = requests.post(MINIMAX_API_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"❌ 请求失败: {response.status_code} - {response.text}")
        return None
    
    result = response.json()
    if result.get("base_resp", {}).get("status_code") != 0:
        print(f"❌ API 错误: {result}")
        return None
    
    # 解析 hex 编码的音频
    audio_hex = result["data"]["audio"]
    audio_data = binascii.unhexlify(audio_hex)
    
    with open(output, "wb") as f:
        f.write(audio_data)
    
    duration_ms = result.get("extra_info", {}).get("audio_length", 0)
    print(f"✅ 语音生成成功: {output}")
    print(f"  时长: {duration_ms}ms")
    print(f"  大小: {len(audio_data)} bytes")
    
    return output


def send_audio_to_feishu(audio_path, user_open_id="ou_b07ee03a908da23c663e6ae56cab046d"):
    """发送音频到飞书"""
    # 获取 token
    token = get_feishu_token()
    if not token:
        print("❌ 无法获取飞书 access token")
        return False
    
    # 上传音频
    url = f"{FEISHU_API_URL}/im/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(audio_path, "rb") as f:
        files = {
            "file_type": ("opus", f, "audio/mp3"),
            "file_name": (os.path.basename(audio_path), f, "audio/mpeg"),
            "file": (os.path.basename(audio_path), f, "audio/mpeg")
        }
        
        # 重新打开文件
        f.seek(0)
        files["file"] = (os.path.basename(audio_path), f, "audio/mpeg")
        
        resp = requests.post(url, headers=headers, files=files)
    
    result = resp.json()
    if result.get("code") != 0:
        print(f"❌ 上传失败: {result}")
        return False
    
    file_key = result["data"]["file_key"]
    print(f"✅ 音频上传成功: {file_key}")
    
    # 发送消息
    msg_url = f"{FEISHU_API_URL}/im/v1/messages?receive_id_type=open_id"
    msg_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    msg_data = {
        "receive_id": user_open_id,
        "msg_type": "audio",
        "content": json.dumps({"file_key": file_key})
    }
    
    msg_resp = requests.post(msg_url, headers=msg_headers, json=msg_data)
    msg_result = msg_resp.json()
    
    if msg_result.get("code") == 0:
        print(f"✅ 音频消息发送成功!")
        return True
    else:
        print(f"❌ 发送失败: {msg_result}")
        return False


def main():
    parser = argparse.ArgumentParser(description="MiniMax 语音合成")
    parser.add_argument("text", help="要转语音的文本")
    parser.add_argument("--voice", "-v", default="Chinese_Male_Adult", 
                       help="音色 ID (默认: Chinese_Male_Adult)")
    parser.add_argument("--model", "-m", default="speech-2.8-hd",
                       help="模型 (默认: speech-2.8-hd)")
    parser.add_argument("--speed", "-s", type=float, default=1.0,
                       help="语速 0.5-2.0 (默认: 1.0)")
    parser.add_argument("--emotion", "-e", default="neutral",
                       help="情绪: happy, sad, angry, neutral 等 (默认: neutral)")
    parser.add_argument("--output", "-o", default="output.mp3",
                       help="输出文件 (默认: output.mp3)")
    parser.add_argument("--send-to-feishu", action="store_true",
                       help="生成后发送到飞书")
    parser.add_argument("--user-id", default="ou_b07ee03a908da23c663e6ae56cab046d",
                       help="飞书用户 open_id (默认: 曹晓雨)")
    
    args = parser.parse_args()
    
    # 生成语音
    output_file = generate_speech(
        args.text,
        voice=args.voice,
        model=args.model,
        speed=args.speed,
        emotion=args.emotion,
        output=args.output
    )
    
    if output_file and args.send_to_feishu:
        print("\n正在发送到飞书...")
        send_audio_to_feishu(output_file, args.user_id)


if __name__ == "__main__":
    main()
