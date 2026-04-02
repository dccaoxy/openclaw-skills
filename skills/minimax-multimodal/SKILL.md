---
name: minimax-multimodal
description: MiniMax 多模态生成技能 - 语音合成、图片生成、视频生成，并支持直接发送到飞书。支持中英文、多种音色、多种分辨率。
metadata:
  openclaw:
    emoji: "🎭"
    requires:
      bins: [python3]
      env: [MINIMAX_API_KEY]
      pip: [requests]
    primaryEnv: MINIMAX_API_KEY
    envHelp:
      MINIMAX_API_KEY:
        required: true
        description: MiniMax API Key (Token Plan Key)
        howToGet: |
          1. 打开 https://platform.minimaxi.com
          2. 登录并进入 用户中心 -> 接口密钥
          3. 创建 Token Plan Key 或 API Key
          4. 复制密钥并设置到此环境变量
author: openclaw
category: generation
---

# MiniMax 多模态生成技能

集语音合成、图片生成、视频生成于一体的全能技能，支持直接发送到飞书。

## 功能概览

| 功能 | 模型 | 说明 |
|------|------|------|
| 语音合成 | speech-2.8-hd | 支持40+语言，多种音色 |
| 图片生成 | image-01 | 最高4K分辨率 |
| 视频生成 | MiniMax-Hailuo-2.3 | 6秒/10秒，768P/1080P |

## 配置

### 环境变量

```bash
export MINIMAX_API_KEY="your-api-key-here"
```

### 飞书配置（可选，用于发送）

技能会自动从 `~/.openclaw/openclaw.json` 读取飞书凭证。

## 使用方式

### 1. 语音合成

```bash
# 基本用法
python3 ~/.openclaw/skills/minimax-multimodal/scripts/tts.py "你好，这是测试语音"

# 指定音色和参数
python3 ~/.openclaw/skills/minimax-multimodal/scripts/tts.py "你好" \
  --voice Chinese_Male_Adult \
  --model speech-2.8-hd \
  --speed 1.0 \
  --emotion happy \
  --output test.mp3

# 发送到飞书
python3 ~/.openclaw/skills/minimax-multimodal/scripts/tts.py "你好" --send-to-feishu
```

### 2. 图片生成

```bash
# 基本用法
python3 ~/.openclaw/skills/minimax-multimodal/scripts/image_gen.py "一个赛博朋克城市"

# 指定参数
python3 ~/.openclaw/skills/minimax-multimodal/scripts/image_gen.py \
  --prompt "一个中年韩国男性站在实验室中" \
  --aspect-ratio 16:9 \
  --output test.png

# 发送到飞书
python3 ~/.openclaw/skills/minimax-multimodal/scripts/image_gen.py "赛博朋克城市" --send-to-feishu
```

### 3. 视频生成

```bash
# 基本用法（异步，需要等待）
python3 ~/.openclaw/skills/minimax-multimodal/scripts/video_gen.py "一个机器人在街上行走"

# 指定参数
python3 ~/.openclaw/skills/minimax-multimodal/scripts/video_gen.py \
  --prompt "两个数字人在虚拟UI中相见" \
  --duration 6 \
  --resolution 768P

# 发送到飞书
python3 ~/.openclaw/skills/minimax-multimodal/scripts/video_gen.py "机器人行走" --send-to-feishu
```

## 可用音色

### 推荐音色（经测试可用）
- `male-qn-qingse` - 男声-青年-清澈（推荐）
- `female-qn-qingse` - 女声-青年-清澈
- `male-qn-jingdian` - 男声-经典
- `female-qn-bidu` - 女声-播音

### 其他音色
- `Chinese_Male_Adult` - 中文男声
- `Chinese_Female_Adult` - 中文女声
- `English_Male_Adult` - 英文男声
- `English_Female_Adult` - 英文女声

## 情绪选项

`emotion` 参数支持: `happy`, `sad`, `angry`, `neutral`, `fearful`, `disgusted`, `surprised`

## 纵横比选项

`aspect-ratio` 参数支持: `1:1`, `3:4`, `4:3`, `16:9`, `9:16`

## 分辨率选项

视频 `resolution` 参数: `512P`, `768P`, `1080P`

## API 文档

- MiniMax 开放平台: https://platform.minimaxi.com/docs
- 语音合成: https://platform.minimaxi.com/docs/api-reference/speech-t2a-http
- 图片生成: https://platform.minimaxi.com/docs/guides/image-generation
- 视频生成: https://platform.minimaxi.com/docs/guides/video-generation

## 注意事项

1. **视频生成是异步的**，需要等待1-2分钟才能获取结果
2. **Token Plan** 支持全部模态，普通 API Key 可能只支持部分
3. **发送视频到飞书** 需要同时提供视频文件和封面图片
4. **下载链接有效期** 视频为9小时，请及时使用
