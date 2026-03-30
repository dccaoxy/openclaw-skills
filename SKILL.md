# Economist 新闻获取 - 升级版

## 技能说明

从《经济学人》网站抓取新闻内容，翻译成中文并写入飞书文档。

**核心升级点（相比旧版）：**
1. ✅ 支持用户登录态 — 世界简报等付费内容需要已登录浏览器 session
2. ✅ 内置去重机制 — 各板块重复文章自动合并
3. ✅ 灵活排序 — 用户可指定顺序，默认世界简报→中国→美国→金融→欧洲→英国
4. ✅ 增量写入 — 每板块完成即写入文档，不必等全部完成
5. ✅ 超时重试 — 子代理超时/失败自动重试（最多2次）

---

## 触发条件

用户发送以下内容时激活：
- "经济学人"、"economist"
- "获取新闻"、"新闻推送"
- "抓取 economist"

---

## 📋 执行流程

### 流程概览

```
1. 检查是否有存量文档 token
2. 打开浏览器 → 用户登录（如需）
3. 等待用户确认登录完成
4. 并行子代理抓取各板块（去重）
5. 增量写入飞书文档
6. 发送完成通知
```

---

## 🔐 登录态处理（关键！）

### 为什么需要登录

| 页面 | 免费内容 | 付费内容 |
|------|---------|---------|
| 话题页（美国/中国/欧洲等） | ✅ 完整文章 | 部分深度文章 |
| **世界简报** | ❌ 几乎全部付费墙 | **需要登录** |
| 周刊版 | ✅ 部分 | 部分 |

**经验**：世界简报页面即使付费订阅者也需要登录才能看完整内容。话题页大多数文章免费。

### 登录操作流程

```
1. 主代理：openclaw browser open "https://www.economist.com/the-world-in-brief"
2. 主代理：发消息给用户"浏览器已打开，请登录"
3. 用户登录
4. 用户发消息"登录好了"
5. 主代理：snapshot 验证登录成功（检查是否有 Subscriber only）
6. 验证成功后，启动子代理抓取
```

### 验证登录状态

```bash
openclaw browser snapshot | grep -i "subscriber only"
```

- 有输出 → 仍为访客态，需要等待用户登录
- 无输出 → 登录成功，可以继续

---

## 🌐 浏览器操作规范

### 标准抓取流程（单板块）

```bash
# 1. 打开板块页面
openclaw browser open "https://www.economist.com/topics/china"
sleep 8

# 2. 获取快照
openclaw browser snapshot

# 3. 解析文章链接（从 snapshot 的 link 元素提取 /url 字段）
# 格式如：https://www.economist.com/finance-and-economics/...

# 4. 逐一点击每篇文章
openclaw browser click "ref=e123"   # ref 来自 snapshot
sleep 6

# 5. 获取文章全文
openclaw browser snapshot
# → 解析 heading + paragraph 元素获取正文

# 6. 返回列表（继续下一篇）
openclaw browser navigate "back"
sleep 3

# 7. 重复 4-6 直到所有文章完成

# 8. 关闭当前板块
openclaw browser close
```

### 等待时间参考

| 操作 | 等待时长 |
|------|---------|
| 打开页面 | 8 秒 |
| 点击文章进入 | 6 秒 |
| 后退返回列表 | 3 秒 |
| 关闭页面 | 无需等待 |

---

## 📄 飞书文档操作

### 文档结构

```markdown
# 📰 The Economist - 经济学人新闻汇总
更新日期：2026-03-30

---

## 🌍 世界简报
[每条新闻一段，2-4句话核心摘要]

---

## 🇨🇳 中国
[每篇文章 200-300 字详细摘要]

---

## 🇺🇸 美国
[每篇文章 200-300 字详细摘要]

---

[其他板块...]
```

### 排序规则（默认）

```
世界简报 → 中国 → 美国 → 金融与经济 → 欧洲 → 英国 → 科技 → 商业
```

用户可自定义顺序。

---

## 🤖 子代理并行抓取

### 架构

```
主代理
├── 子代理 1：世界简报
├── 子代理 2：美国
├── 子代理 3：中国
├── 子代理 4：欧洲
├── 子代理 5：英国
├── 子代理 6：商业
├── 子代理 7：金融与经济
└── 子代理 8：科技
```

**设计原则：**
- 每个子代理只处理 1 个板块，避免上下文膨胀
- 子代理完成后立即终止（cleanup="delete"）
- 超时/失败自动重试，最多重试 2 次

### 子代理任务模板

```
## 任务：抓取 [板块名称] 新闻

URL: [板块 URL]

**重要：每个文章都要点进去看完整内容！不只抓板块页面摘要！**

操作步骤：
1. openclaw browser open "[板块URL]"
2. sleep 8
3. openclaw browser snapshot → 解析所有文章链接（link 元素的 /url 字段）
4. 对每个文章链接：
   a. openclaw browser open "[完整URL]"
   b. sleep 6
   c. openclaw browser snapshot → 解析 heading + paragraph 获取正文
   d. 生成 200-300 字中文摘要
   e. 保存标题+摘要
   f. openclaw browser navigate "back"
   g. sleep 3
5. openclaw browser close
6. 返回 JSON：
{
  "板块": "🇨🇳 中国",
  "数量": N,
  "文章列表": [
    {"序号": 1, "标题": "中文标题", "摘要": "200-300字..."}
  ]
}
```

### 超时重试机制

```python
# 每个子代理超时 900 秒（15 分钟）
# 失败自动重试，最多 2 次
# 重试时覆盖旧会话：sessions_spawn(..., resumeSessionId=旧session_id)

for name, url in batch_urls:
    success = False
    retries = 0
    while not success and retries <= 2:
        sa = sessions_spawn(
            task=f"抓取 {name}",
            runtime="subagent",
            mode="session",
            runTimeoutSeconds=900,
            cleanup="delete"
        )
        try:
            result = sessions_yield(sa, timeout=900)
            # 验收检查
            if isinstance(result, dict) and "文章列表" in result:
                write_to_doc(name, result)
                success = True
            else:
                raise Exception("返回格式无效")
        except Exception as e:
            retries += 1
            if retries > 2:
                # 记录失败，跳过
                pass
            else:
                # 重试
                pass
```

---

## 🔄 去重机制

### 重复类型识别

**完全重复**（同一事件不同角度报道）：
- "伊朗如何从特朗普战争大发横财" → 出现在：美国、中国、金融与经济、欧洲
- "罗马货币帝国的衰落" → 出现在：金融与经济、商业
- "拉加德警告" → 出现在：中国、金融与经济
- "全球通胀能涨多高" → 出现在：中国、金融与经济
- "西方人移民外流" → 出现在：中国、金融与经济
- "英国移民政策数据问题" → 出现在：欧洲、英国

### 去重策略

```
1. 抓取完成后，主代理收集所有文章
2. 计算标题相似度（编辑距离或关键词重叠）
3. 同主题文章保留"最完整版本"（字数最多的）
4. 其他板块相同主题只保留一句话提及
```

### 去重优先级（保留哪篇）

| 板块 | 优先级 | 说明 |
|------|--------|------|
| 美国 | 最高 | 伊朗战争报道最全面 |
| 金融与经济 | 高 | 深度分析最完整 |
| 中国 | 中 | 视角不同可保留 |
| 欧洲/英国 | 低 | 区域视角 |

---

## 📤 飞书消息推送

### 进度通知

每完成一个板块即发送进度：
```
📍 世界简报 完成 (1/8)
📍 美国 完成 (2/8)
...
```

### 最终通知

```
✅ 经济学人新闻更新完成！

📄 文档：https://feishu.cn/docx/xxx
📊 共计 N 篇文章（去重后 M 篇）
⏱️ 耗时约 X 分钟
```

---

## ⚠️ 重要经验教训

### 1. 世界简报页面结构特殊

**问题**：世界简报页面不是普通文章列表页，而是短段落摘要合集。大部分内容标注"Subscriber only"。

**解决**：
- 免费用户：只能获取页头几条免费摘要（约 9 条，每条 2-4 句话）
- 登录后：可获取完整的世界简报文章（约 6 篇深度报道）

**关键**：必须让用户在浏览器中登录后，才能获取完整世界简报内容。

### 2. 子代理独立 session 的局限性

**问题**：并行子代理各自有独立 browser session，不继承主代理的登录态。

**解决**：
- 方案 A（推荐）：主代理打开浏览器 → 用户登录 → 保持该 session → 再启动子代理
- 方案 B：各子代理独立处理，登录态问题由用户订阅解决

### 3. 超时返回中间态

**问题**：子代理超时时常返回非 JSON 内容（如页面快照的中间状态）。

**解决**：验收检查返回格式，无效则自动重试。

### 4. 内容重复严重

**问题**：经济学人按 topic 划分板块，同一事件（如伊朗战争）会在多个板块重复出现。

**解决**：内置去重步骤，抓取完成后按主题合并。

---

## 🛠️ 工具清单

| 操作 | 命令 |
|------|------|
| 打开浏览器 | `openclaw browser open <url>` |
| 获取快照 | `openclaw browser snapshot` |
| 截图 | `openclaw browser screenshot` |
| 点击元素 | `openclaw browser click <ref>` |
| 后退 | `openclaw browser navigate "back"` |
| 关闭 | `openclaw browser close` |
| 发送消息 | `openclaw message send --channel feishu --target <id> --message <text>` |
| 创建文档 | `lark-cli docs create --title <title> --owner-open-id <id>` |
| 更新文档 | `lark-cli docs +update --doc <token> --markdown <content> --mode overwrite` |

---

## 📁 文件结构

```
skills/economist-news/
└── SKILL.md                    # 本文件

agents/news-officer/
├── economist_config.json       # 文档 token 和执行历史
└── economist_job_list.json     # 批次进度状态
```
