#!/usr/bin/env python3
"""
MiniMax 多模态生成 - 统一入口
支持语音、图片、视频生成，可选择直接发送到飞书
"""

import argparse
import sys

# 导入各模块
from tts import generate_speech, send_audio_to_feishu
from image_gen import generate_image, send_image_to_feishu
from video_gen import generate_video, send_video_to_feishu


def main():
    parser = argparse.ArgumentParser(
        description="MiniMax 多模态生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 语音合成
  python3 generate.py tts "你好世界"
  python3 generate.py tts "你好" --voice Chinese_Male_Adult --emotion happy --send-to-feishu
  
  # 图片生成
  python3 generate.py image "一个赛博朋克城市"
  python3 generate.py image "城市夜景" --aspect-ratio 16:9 --send-to-feishu
  
  # 视频生成
  python3 generate.py video "机器人在街上行走"
  python3 generate.py video "两个数字人相见" --duration 6 --send-to-feishu
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="生成类型")
    
    # TTS 子命令
    tts_parser = subparsers.add_parser("tts", help="语音合成")
    tts_parser.add_argument("text", help="要转语音的文本")
    tts_parser.add_argument("--voice", "-v", default="Chinese_Male_Adult",
                           help="音色 ID (默认: Chinese_Male_Adult)")
    tts_parser.add_argument("--model", "-m", default="speech-2.8-hd",
                           help="模型 (默认: speech-2.8-hd)")
    tts_parser.add_argument("--speed", "-s", type=float, default=1.0,
                           help="语速 0.5-2.0 (默认: 1.0)")
    tts_parser.add_argument("--emotion", "-e", default="neutral",
                           help="情绪 (默认: neutral)")
    tts_parser.add_argument("--output", "-o", default="output.mp3",
                           help="输出文件 (默认: output.mp3)")
    tts_parser.add_argument("--send-to-feishu", action="store_true",
                           help="发送到飞书")
    tts_parser.add_argument("--user-id", default="ou_b07ee03a908da23c663e6ae56cab046d",
                           help="飞书用户 ID")
    
    # Image 子命令
    img_parser = subparsers.add_parser("image", help="图片生成")
    img_parser.add_argument("prompt", help="图片描述")
    img_parser.add_argument("--aspect-ratio", "-a", default="16:9",
                           help="纵横比 (默认: 16:9)")
    img_parser.add_argument("--model", "-m", default="image-01",
                           help="模型 (默认: image-01)")
    img_parser.add_argument("--output", "-o", default="output.png",
                           help="输出文件 (默认: output.png)")
    img_parser.add_argument("--send-to-feishu", action="store_true",
                           help="发送到飞书")
    img_parser.add_argument("--user-id", default="ou_b07ee03a908da23c663e6ae56cab046d",
                           help="飞书用户 ID")
    
    # Video 子命令
    vid_parser = subparsers.add_parser("video", help="视频生成")
    vid_parser.add_argument("prompt", help="视频描述")
    vid_parser.add_argument("--duration", "-d", type=int, default=6,
                           help="时长 秒 (默认: 6)")
    vid_parser.add_argument("--resolution", "-r", default="768P",
                           help="分辨率 (默认: 768P)")
    vid_parser.add_argument("--model", "-m", default="MiniMax-Hailuo-2.3",
                           help="模型 (默认: MiniMax-Hailuo-2.3)")
    vid_parser.add_argument("--output", "-o", default="output.mp4",
                           help="输出文件 (默认: output.mp4)")
    vid_parser.add_argument("--send-to-feishu", action="store_true",
                           help="发送到飞书")
    vid_parser.add_argument("--thumbnail", "-t",
                           help="封面图片路径")
    vid_parser.add_argument("--user-id", default="ou_b07ee03a908da23c663e6ae56cab046d",
                           help="飞书用户 ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "tts":
        output = generate_speech(
            args.text,
            voice=args.voice,
            model=args.model,
            speed=args.speed,
            emotion=args.emotion,
            output=args.output
        )
        if output and args.send_to_feishu:
            send_audio_to_feishu(output, args.user_id)
    
    elif args.command == "image":
        output = generate_image(
            args.prompt,
            aspect_ratio=args.aspect_ratio,
            model=args.model,
            output=args.output
        )
        if output and args.send_to_feishu:
            send_image_to_feishu(output, args.user_id)
    
    elif args.command == "video":
        output = generate_video(
            args.prompt,
            duration=args.duration,
            resolution=args.resolution,
            model=args.model
        )
        if output and args.send_to_feishu:
            send_video_to_feishu(output, args.thumbnail, args.user_id)


if __name__ == "__main__":
    main()
