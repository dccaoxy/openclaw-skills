# Agent 技能库

> 根据复盘记录整理的实际验证过的方法和代码片段

---

## 1. 飞书文档

### 创建文档
```javascript
feishu_doc({
  action: 'create',
  title: '文档标题',
  owner_open_id: 'ou_xxx'  // 用户 open_id
})
```

### 写入内容（API）
```javascript
// 1. 获取 token
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
Body: { app_id, app_secret }

// 2. 添加内容块（每批 ≤3 个 blocks）
POST https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{block_id}/children
Body: { children: [{ block_type: 2, text: { elements: [{ text_run: { content }}]}}]}
```

### block_type 对照
- 2 = 文本
- 3 = heading1
- 4 = heading2
- 12 = bullet
- 14 = code

---

## 2. Cron 任务

### 查看任务
```bash
openclaw cron list
```

### 手动触发
```bash
openclaw cron run <job-id>
```

### 修改 cron 表达式
```bash
openclaw cron edit <job-id> --cron "0 */3 * * *"
```

### 查看历史
```bash
openclaw cron runs --id <job-id> --limit 5
```

---

## 3. Session 管理

### 列出 session
```javascript
sessions_list({
  limit: 50,
  activeMinutes: 180,  // 最近 3 小时
  messageLimit: 1
})
```

### 发送消息
```javascript
sessions_send({
  sessionKey: 'agent:xxx',
  message: '内容',
  timeoutSeconds: 30
})
```

### 获取历史
```javascript
sessions_history({
  sessionKey: 'agent:xxx',
  limit: 20,
  includeTools: true
})
```

---

## 4. 浏览器操作

### 打开页面
```javascript
browser(action: 'open', url: 'http://xxx')
```

### 提取页面数据
```javascript
page.evaluate(() => {
  return document.documentElement.innerHTML
})
```

### 等待
```bash
sleep 5
```

---

## 5. macOS 截图

### 获取窗口 ID
```bash
osascript -e 'tell application "Chrome" to id of front window'
```

### 窗口截图
```bash
/usr/sbin/screencapture -l <windowID> output.png
```

---

## 6. 子代理限制

- 子代理无法使用 `feishu_doc` 等注册工具
- 解决：用 `exec` 调用 Node.js 脚本

---

## 7. 经济学人新闻爬取（news-officer）

### 技能触发
```
feishu_doc({action:'create', title:'📰 The Economist - 经济学人新闻汇总', owner_open_id:'ou_xxx'})
```

### 爬取批次（8个）
1. 世界简报 - https://www.economist.com/the-world-in-brief
2. 周刊版 - https://www.economist.com/weeklyedition/
3. 美国 - https://www.economist.com/topics/united-states
4. 中国 - https://www.economist.com/topics/china（详细摘要）
5. 商业 - https://www.economist.com/topics/business
6. 金融与经济 - https://www.economist.com/topics/finance-and-economics
7. 欧洲 - https://www.economist.com/topics/europe
8. 英国 - https://www.economist.com/topics/britain

### 浏览器操作
```javascript
browser({action:'open', url:'https://...'})  // 打开页面
browser({action:'snapshot'})                  // 获取内容
browser({action:'close'})                    // 关闭页面
```

### 间隔要求
- 每批间隔 10-15 秒，避免请求过频

### 输出格式
- 世界简报：10条简洁概括
- 中国：200-300字详细摘要
- 其他：简短列表

---

## 8. 飞书 CLI（lark-cli）

> ⚠️ 待授权，周一曹晓雨协助

### 安装
```bash
npm install -g @larksuite/cli
lark-cli --version  # 验证安装
```

### 认证
```bash
lark-cli auth login
```

### 常用命令

| 功能 | 命令 |
|------|------|
| **日历** | `lark-cli calendar +agenda` |
| **日历列表** | `lark-cli calendar events list --params '{"calendar_id":"primary"}'` |
| **搜索用户** | `lark-cli contact +search-user --query "姓名"` |
| **文档列表** | `lark-cli docs +list` |
| **消息发送** | `lark-cli chat +send --data '{"open_id":"ou_xxx","msg_type":"text","content":"内容"}'` |

### 输出格式
```bash
lark-cli <command> --format pretty  # 人类可读
lark-cli <command> --format json    # JSON
```

### 参考链接
- GitHub: https://github.com/larksuite/cli
- 文档：200+ 命令，11 个业务领域

---

## 9. 复盘流程

```
每 3 小时 (agent-review)
    ↓
各 Agent 写本地日志 → ~/.openclaw/agent_review/daily/
    ↓
每 6 小时 (agent-aggregate) 第 2 分钟执行
    ↓
汇总去重 → 写入飞书文档
```

---

*最后更新：2026-03-27*
