---
name: mac-media-control
description: Control Mac camera, microphone, speakers, and audio playback. Use when: (1) Taking photos or videos with webcam, (2) Recording audio from microphone, (3) Playing audio files, (4) Adjusting system volume, (5) Taking screenshots, (6) Sending voice messages via Feishu, (7) Generating audio with ElevenLabs or MiniMax TTS APIs. Triggers on phrases like "take a photo", "record audio", "play sound", "adjust volume", "send voice message", "control camera", "control microphone".
---

# Mac Media Control

## Prerequisites

Install required tools:
```bash
brew install ffmpeg imagesnap
```

## Camera (拍照/录像)

### List available cameras
```bash
ffmpeg -f avfoundation -list_devices true -i ""
```

### Take a photo (拍照)
```bash
imagesnap -d "MacBook Pro相机" /path/to/output.jpg
```

### Record video (录视频)
```bash
ffmpeg -f avfoundation -i "0" -t 10 -c:v libx264 output.mov
```

## Microphone (麦克风录音)

### List available microphones
```bash
ffmpeg -f avfoundation -list_devices true -i ""
```

### Record audio (录音)
```bash
# Record 10 seconds
ffmpeg -f avfoundation -i ":0" -t 10 -ar 44100 output.m4a

# Record until Ctrl+C
ffmpeg -f avfoundation -i ":0" -ar 44100 output.m4a
```

## Speakers (扬声器/音量控制)

### Play audio (播放音频)
```bash
afplay /path/to/audio.mp3
```

### Get current volume (获取音量)
```bash
osascript -e "output volume of (get volume settings)"
# Returns: 0-100
```

### Set volume (设置音量)
```bash
osascript -e "set volume output volume 50"
# Range: 0-100
```

## Screenshots (截图)

```bash
/usr/sbin/screencapture -x /path/to/screenshot.jpg
```

## Feishu Voice Messages (飞书语音消息)

### Upload audio file
```bash
# Get access token
APP_ID="your_app_id"
APP_SECRET="your_app_secret"
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tenant_access_token',''))")

# Upload file
UPLOAD_RESP=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=opus" \
  -F "file_name=audio.ogg" \
  -F "file=@/path/to/audio.m4a")

FILE_KEY=$(echo $UPLOAD_RESP | python3 -c "import json,sys; print(json.load(sys.stdin).get('data',{}).get('file_key',''))")
```

### Send voice message (发送语音)
```bash
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"user_open_id\",
    \"msg_type\": \"audio\",
    \"content\": \"{\\\"file_key\\\": \\\"$FILE_KEY\\\"}\"
  }"
```

### Using openclaw message command (更简单的方式)
```bash
openclaw message send --channel feishu --target <user_open_id> --media /path/to/audio.m4a --message "Voice message" --account default
```

## ElevenLabs TTS (语音合成)

### Generate audio with ElevenLabs
```bash
ELEVENLABS_API_KEY="your_api_key"
VOICE_ID="voice_id_from_elevenlabs"

curl -s -X POST "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text here",
    "voice_settings": {
      "stability": 0.5,
      "similarity_boost": 0.8,
      "style": 0.3
    }
  }' -o output.mp3
```

### Available voices
```bash
curl -s -X GET "https://api.elevenlabs.io/v1/voices" \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

## MiniMax TTS/Music (MiniMax 语音/音乐)

### Music generation (音乐生成)
```bash
MINIMAX_API_KEY="your_api_key"

curl -s -X POST "https://api.minimaxi.com/v1/music_generation" \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "music-2.5+",
    "prompt": "Your music description",
    "lyrics": "[Intro] lyrics here [Verse] more lyrics",
    "song_structure": "Intro, Verse, Chorus, Outro"
  }'
```

### Text-to-Speech (语音合成)
```bash
# Note: Requires TTS API permission
# 推荐模型: speech-2.8-hd (speech-02-hd 在 Max-极速版不支持)
curl -s -X POST "https://api.minimaxi.com/v1/t2a_v2" \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "speech-2.8-hd",
    "text": "Your text here",
    "voice_setting": {
      "voice_id": "female-tianmei",
      "speed": 1.0
    },
    "audio_setting": {
      "format": "mp3"
    }
  }' | python3 -c "
import sys, json
data = json.load(sys.stdin)
audio_hex = data['data']['audio']
audio_bytes = bytes.fromhex(audio_hex)
with open('/tmp/tts_output.mp3', 'wb') as f:
    f.write(audio_bytes)
print('Saved:', len(audio_bytes), 'bytes')
"

# 常用音色:
#   female-tianmei  - 甜美女性
#   female-yujie    - 御姐
#   male-qn-qingse  - 青年男性
#   presenter_male   - 主持人
#   audiobook_male_1 - 男性有声书
```

### 在 Mac 扬声器播放音频 (重要!)
```bash
# 问题: opus 格式音量偏低，afplay 可能只播1秒就"消失"
# 解决: 转换为 MP3 并放大音量

# 1. 转换为 MP3 并放大音量 3 倍
ffmpeg -i input.opus -af "volume=3" output_vol.mp3 -y

# 2. 设置系统音量后播放
osascript -e "set volume output volume 50"  # 50% 音量
afplay output_vol.mp3

# 或者一行命令:
afplay <(ffmpeg -i input.opus -af "volume=3" - - 2>/dev/null)
```

## Quick Reference

| Task | Command |
|------|---------|
| Take photo | `imagesnap -d "MacBook Pro相机" photo.jpg` |
| Record 10s audio | `ffmpeg -f avfoundation -i ":0" -t 10 audio.m4a` |
| Play audio (正常音量) | `afplay audio.mp3` |
| Play audio (放大音量) | `afplay <(ffmpeg -i audio.opus -af "volume=3" - 2>/dev/null)` |
| Set volume 50% | `osascript -e "set volume output volume 50"` |
| Screenshot | `/usr/sbin/screencapture -x screen.jpg` |
| Send Feishu voice | `openclaw message send --channel feishu --target <id> --media audio.m4a --account default` |
| TTS 生成语音 | `curl -X POST "https://api.minimaxi.com/v1/t2a_v2" -H "Authorization: Bearer $API_KEY" -d '{"model":"speech-2.8-hd","text":"文字","voice_setting":{"voice_id":"female-tianmei"}}'` |

## Permissions

On first use, macOS will prompt for camera/microphone permissions. Grant access in:
**System Settings → Privacy & Security → Camera/Microphone**

For terminal access, add Terminal (or your terminal app) to the allowed apps list.
