# Agent 技能库

> 所有 Agent 共享的技能和方法积累，持续更新

---

更新时间：2026-03-30 09:28

---

## 系统管理

### Cron 任务管理
**来源**：main Agent | 2026-03-27
**方法**：
```bash
# 查看任务
openclaw cron list

# 手动触发
openclaw cron run <job-id>

# 修改 cron
openclaw cron edit <job-id> --cron "0 */3 * * *"
```

### Cron 调度错开策略
**来源**：main Agent | 2026-03-28
**方法**：
```bash
# 复盘任务：整点触发
# 汇总任务：复盘后 2 分钟触发
# 避免同一时刻大量任务同时运行
```

### Agent 状态测试
**来源**：main Agent | 2026-03-27
**方法**：
```bash
# 列出所有 agent
openclaw agents list

# 向其他 agent 发送消息
sessions_send(sessionKey: "agent:xxx:main", message: "...")
```

---

## 飞书操作

### 创建文档
**来源**：news-officer | 2026-03-27
**方法**：
```javascript
// 1. 获取 token
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
Body: { app_id, app_secret }

// 2. 创建文档
POST https://open.feishu.cn/open-apis/docx/v1/documents
Headers: Authorization: Bearer {token}
Body: { title: "文档标题" }

// 3. 添加内容块
POST https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children
Body: { children: [{ block_type: 2, text: { elements: [{ text_run: { content: "内容" }}]}}]}
```

### block_type 对照
**来源**：main Agent | 2026-03-28
- 2 = 文本
- 3 = heading1
- 4 = heading2
- 5 = heading3
- 12 = bullet（列表）
- 13 = code（⚠️ 批量插入会失败）
- 22 = horizontal_line（⚠️ 批量插入会失败）

### 飞书文档批量写入限制与策略
**来源**：main Agent | 2026-03-28
**发现**：
- `block_type: 13`（code）和 `block_type: 22`（horizontal_line）通过 API 批量插入会返回 `invalid param`
- 当某一批次中的单个 block 插入失败时，后续 block 的 index 会错位

**方法**：
```javascript
// 1. 批量清空文档内容
DELETE https://open.feishu.cn/open-apis/docx/v1/documents/${DOC_TOKEN}/blocks/${DOC_TOKEN}/children/batch_delete
Body: { "start_index": 0, "end_index": childrenCount }

// 2. 分批插入新 blocks（每批 3-5 个，避免 API 超时）
POST https://open.feishu.cn/open-apis/docx/v1/documents/${DOC_TOKEN}/blocks/${DOC_TOKEN}/children
Body: { "children": [blocks], "index": i }

// 3. 采用"逐个插入 + 失败跳过"策略
// 确保即使部分失败不影响整体
```

**注意**：
- 避免在批量写入中使用代码块（block_type: 13）和水平线（block_type: 22）
- 可用普通文本段落（block_type: 2）替代，或逐个插入尝试

### 飞书消息通知发送
**来源**：news-officer | 2026-03-28
**方法**：
```javascript
// 使用 message 工具发送飞书消息
message send channel="ou_xxx" content="内容"

// 注意：跨应用 open_id 限制（错误码 99992361）
// 解决：确保使用正确的应用权限和配置
```

---

## 浏览器操作

### 页面抓取
**来源**：news-officer | 2026-03-27
**方法**：
```javascript
// 打开页面
browser({action: 'open', url: 'https://www.economist.com/'})

// 获取内容
browser({action: 'snapshot'})

// 关闭页面
browser({action: 'close'})
```

### macOS 窗口截图
**来源**：main Agent | 2026-03-27
**方法**：
```bash
# 获取 Chrome 窗口 ID
osascript -e 'tell application "Chrome" to id of front window'

# 截图（需屏幕录制权限）
/usr/sbin/screencapture -l <windowID> output.png

# Swift ScreenCaptureKit（macOS 15+）
swift -e 'import ScreenCaptureKit'
```

### 浏览器资源管理
**来源**：news-officer | 2026-03-28
**方法**：
```javascript
// 每个页面抓取后必须关闭，避免标签页堆积
browser({action: 'close'})

// 使用 profile 保持会话一致性
browser open url="..." profile="openclaw"
```

### 子代理执行模式
**来源**：main Agent | 2026-03-28
**方法**：
```javascript
// 复杂多步骤任务使用子代理隔离执行
sessions_spawn({ task: "具体任务", runtime: "subagent" })

// 等待子代理完成
sessions_yield()

// 向子代理发送消息
sessions_send(sessionKey: "agent:xxx:main", message: "...")
```

**注意**：子代理无法访问 `feishu_doc` 等内部工具，需通过 `exec` + Node.js 脚本调用飞书 API

---

## 文件搜索

### 搜索本地文件
**来源**：coder1 | 2026-03-27
**方法**：
```bash
find /Users/caoxy/.openclaw/workspace -type d -name "*roadmap*"
find /Users/caoxy -maxdepth 4 -type d -name "*roadmap*"
ls ~/code
ls ~/projects
```

---

## 复盘机制

### 路径结构
```
~/.openclaw/agent_review/
├── daily/           # 每日复盘
│   ├── review_2026-03-27.md
│   └── processed/    # 已归档
└── skills_library.md  # 技能库（累加）
```

### 共享文档
- **飞书**：`LkmldObEfoewtBxqkQHcs2GGnif`
- **本地**：`~/.openclaw/agent_review/skills_library.md`

---

## 项目

### 经济学人新闻抓取
**路径**：`~/.openclaw/agents/news-officer/`
**功能**：从 The Economist 网站抓取新闻，翻译成中文，写入飞书文档
**进展**：✅ 已完成

### Roadmap
**路径**：`~/caoxy/Roadmap/`
**功能**：京东商品配置展示平台

### Data_analysis
**路径**：`~/caoxy/Data_analysis/`
**功能**：销售数据分析

---

## 飞书 CLI（lark-cli）

> ✅ 已配置，2026-03-30 完成认证和测试

### 安装
```bash
npm install -g @larksuite/cli
# 或 Homebrew: brew install larksuite/tap/lark-cli
```

### 认证
```bash
lark-cli config init --new    # 首次配置（会输出认证 URL）
lark-cli auth status          # 查看认证状态
lark-cli auth login           # 用户登录（需要 user 身份的功能）
```
**当前状态**：bot 身份已配置（`cli_a94373a41e391bda`），可使用 95 个权限 scope

### 功能模块（21 个）

| 模块 | 功能 | bot 可用 | 备注 |
|------|------|---------|------|
| `docs` | 文档读写 | ✅ | 创建/读取/更新/追加 |
| `docx` | 文档操作 | ✅ | |
| `wiki` | 知识库 | ✅ | 需指定 node token |
| `sheets` | 电子表格 | ✅ | 创建/读写/导出 |
| `base` | 多维表格 | ✅ | 字段/记录/视图/仪表盘 |
| `im` | 即时通讯 | ⚠️ | 发消息有跨应用限制 |
| `calendar` | 日历 | ❌ | 需申请 `calendar:calendar.event:read` |
| `contact` | 通讯录 | ⚠️ | 搜索需 user 身份 |
| `drive` | 云盘/权限 | ✅ | 上传/下载/权限管理 |
| `mail` | 邮箱 | ⚠️ | 需 user 身份 |
| `task` | 任务 | ⚠️ | 需 user 身份 |
| `vc` | 视频会议 | ⚠️ | 需 user 身份 |
| `minutes` | 会议纪要 | ⚠️ | 需 user 身份 |
| `event` | 事件订阅 | ✅ | WebSocket 方式 |
| `board` | 白板 | ✅ | |
| `api` | 通用 API | ✅ | 可直接调任何飞书 API |

### 常用命令示例

```bash
# 文档操作
lark-cli docs +create --title "标题" --markdown "# 内容" --as bot
lark-cli docs +fetch --doc "token" --format pretty
lark-cli docs +update --doc "token" --markdown "新内容" --mode append

# 表格操作
lark-cli sheets +create --title "表格名" --headers '["列1","列2"]' --data '[["值1","值2"]]' --as bot
lark-cli sheets +read --spreadsheet-token "token" --sheet-id "sid" --range "A1:D10"
lark-cli sheets +write --spreadsheet-token "token" --sheet-id "sid" --range "A1:D4" --values '[[...]]'

# 权限管理
lark-cli drive permission.members create \
  --params '{"token":"doc_token","type":"docx","need_notification":false}' \
  --data '{"member_id":"ou_xxx","member_type":"openid","perm":"full_access","type":"user"}'

# 云盘
lark-cli drive +upload --file "./filename" --as bot
lark-cli drive +download --file "file_token"

# 消息（有限制）
lark-cli im +messages-send --user-id "ou_xxx" --text "消息内容"
lark-cli im +chat-search --query "关键词"
lark-cli im +chat-create --name "群名" --users "ou_xxx"

# 通用 API（直接调飞书开放平台 API）
lark-cli api GET /open-apis/bot/v3/info --as bot
lark-cli api POST /open-apis/im/v1/messages --data '{...}'
```

### 权限申请（针对 calendar）
```
https://open.feishu.cn/page/scope-apply?clientID=cli_a94373a41e391bda&scopes=calendar%3Acalendar.event%3Aread
```

### 参考
- GitHub: https://github.com/larksuite/cli
- 文档: https://open.feishu.cn/document/
