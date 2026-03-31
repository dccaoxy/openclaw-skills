# Agent Review Skill - 复盘技能

## 用途
每个 Agent 定期回顾自己的工作，记录完成的任务、使用的工具和方法，汇总到共享文件。

---

## 复盘要求

### 1. 遍历复盘文件
- 读取 `~/.openclaw/agent_review/daily/processed/test_*.md` 所有测试复盘文件
- 读取 `~/.openclaw/agents/{agent_id}/*/` 下各 Agent 的工作记录

### 2. 汇报项目信息
对于每个正在处理的项目，记录：
- **项目名称**：项目叫什么
- **项目路径**：文件存放目录
- **项目功能**：这个项目能做什么
- **当前进展**：完成了什么

### 3. 汇报任务信息
对于每个完成的任务，记录：
- **任务名称**：做了什么
- **具体方法**：怎么做的（带代码）
- **使用的工具**：exec, read, feishu_doc 等

### 4. 格式要求
```markdown
### 项目名称
**路径**：`~/xxx/`
**功能**：做什么
**进展**：完成了什么

### 任务名称
**方法**：
\`\`\`javascript
// 具体代码或命令
\`\`\`
```

---

## 复盘流程

```
每 3 小时 (agent-review)
    ↓
遍历 ~/.openclaw/agent_review/daily/processed/test_*.md
    ↓
遍历 ~/.openclaw/agents/{agent_id}/ 查看工作记录
    ↓
提取：项目信息 + 任务信息 + 具体方法
    ↓
写入 ~/.openclaw/agent_review/daily/review_{date}.md
```

---

## 共享文件路径

| 文件 | 路径 | 说明 |
|------|------|------|
| **各 Agent 复盘** | `~/.openclaw/agent_review/daily/test_{agent}_{timestamp}.md` | 原始复盘 |
| **汇总报告** | `~/.openclaw/agent_review/daily/review_{date}.md` | 合并摘要 |
| **已处理归档** | `~/.openclaw/agent_review/daily/processed/` | 汇总后移入 |
| **飞书文档** | `LkmldObEfoewtBxqkQHcs2GGnif` | 技能库汇总 |

---

## 飞书文档
- **文档名称**：「Agent 技能库 & 复盘记录」
- **文档 ID**：`LkmldObEfoewtBxqkQHcs2GGnif`
- **链接**：https://xxx.feishu.cn/docx/LkmldObEfoewtBxqkQHcs2GGnif

---

## 执行步骤

1. `sessions_list` - 查询近 3 小时 session
2. `sessions_history` - 获取各 session 详情
3. `read` - 读取 processed/ 下所有 test_*.md
4. `exec` - 遍历 agents/ 目录查看工作记录
5. 提取项目信息和任务方法
6. `write` - 写入 review_{date}.md

---

## 注意事项

- 只记录「怎么做成的」，不记录闲聊
- 代码块要完整可执行
- 项目路径要具体到目录
- 完成后回复「复盘完成」
