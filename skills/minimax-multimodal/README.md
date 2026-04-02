# MiniMax 多模态生成技能

集语音合成、图片生成、视频生成于一体的 OpenClaw 技能，支持直接发送到飞书。

## 功能概览

| 功能 | 模型 | 说明 |
|------|------|------|
| 语音合成 | speech-2.8-hd | 支持 40+ 语言，多种音色 |
| 图片生成 | image-01 | 最高 4K 分辨率 |
| 视频生成 | MiniMax-Hailuo-2.3 | 6 秒/10 秒，768P/1080P |

## 安装

### 方法一：从 GitHub 安装

```bash
npx clawhub@latest install minimax-multimodal
```

### 方法二：手动安装

1. 克隆此仓库
2. 将技能文件夹复制到 `~/.openclaw/skills/`

## 配置

### 环境变量

使用前需要设置以下环境变量：

```bash
# MiniMax API Key（必须）
export MINIMAX_API_KEY="your-minimax-api-key"

# 飞书应用配置（必须，用于发送消息到飞书）
export FEISHU_APP_ID="your-feishu-app-id"
export FEISHU_APP_SECRET="your-feishu-app-secret"
```

### 获取 API Key

**MiniMax API Key：**
1. 打开 https://platform.minimaxi.com
2. 登录并进入 **用户中心 -> 接口密钥**
3. 创建 Token Plan Key 或 API Key
4. 复制密钥

**飞书应用配置：**
1. 打开 https://open.feishu.cn/app
2. 创建或选择你的应用
3. 获取 **App ID** 和 **App Secret**
4. 确保应用已开通 **发消息** 权限

## 使用方法

### 语音合成

```bash
cd ~/.openclaw/skills/minimax-multimodal/scripts
python3 tts.py "你好世界" --voice male-qn-qingse --send-to-feishu
```

### 图片生成

```bash
python3 image_gen.py "赛博朋克城市" --aspect-ratio 16:9 --send-to-feishu
```

### 视频生成

```bash
python3 video_gen.py "机器人在街上行走" --duration 6 --send-to-feishu
```

## 可用音色

- `male-qn-qingse` - 男声-青年-清澈（推荐）
- `female-qn-qingse` - 女声-青年-清澈
- `male-qn-jingdian` - 男声-经典
- `female-qn-bidu` - 女声-播音

## API 文档

- [MiniMax 开放平台](https://platform.minimaxi.com/docs)
- [语音合成](https://platform.minimaxi.com/docs/api-reference/speech-t2a-http)
- [图片生成](https://platform.minimaxi.com/docs/guides/image-generation)
- [视频生成](https://platform.minimaxi.com/docs/guides/video-generation)

## 许可

MIT License
