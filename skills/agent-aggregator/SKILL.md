# Agent Aggregator Skill - 汇总技能

## 用途
定期汇总各 Agent 的复盘内容，同时维护两个文档：
1. **skills_library.md** - 技能库，累加不覆盖
2. **review_YYYY-MM-DD.md** - 每日复盘，当日更新

---

## 核心原则

**技能库累加不复盖，每日复盘当日更新**

---

## 两个文档

### 1. 技能库（累加）
- **路径**：`~/.openclaw/agent_review/skills_library.md`
- **结构**：按技能分类（系统管理、飞书操作、浏览器操作...）
- **行为**：每次只添加新技能，跳过已存在的

### 2. 每日复盘（当日更新）
- **路径**：`~/.openclaw/agent_review/daily/review_{date}.md`
- **结构**：按项目/任务组织
- **行为**：当日只更新当日文件

### 3. 飞书技能库（同步）
- **文档 ID**：`LkmldObEfoewtBxqkQHcs2GGnif`
- **同步**：与本地 skills_library.md 保持一致

---

## 执行步骤

1. **扫描新复盘文件**
   - 扫描 `~/.openclaw/agent_review/daily/` 所有 `test_*.md`
   - 读取 `~/.openclaw/agent_review/daily/review_*.md` 当日文件

2. **更新每日复盘**
   - 如果当日文件不存在，创建 `review_{date}.md`
   - 如果存在，更新（添加新内容）

3. **更新技能库**
   - 读取现有 `skills_library.md`
   - 对比新内容，去重
   - 只添加新技能/方法

4. **同步飞书**
   - 更新飞书技能库文档 `LkmldObEfoewtBxqkQHcs2GGnif`

5. **归档已处理文件**
   - 移动 `test_*.md` → `processed/`

---

## 文档结构

### skills_library.md
```
# Agent 技能库

更新时间：2026-03-27

## 系统管理
### Cron 任务管理
**方法**：...
**来源**：main | 2026-03-27

## 飞书操作
...
```

### review_YYYY-MM-DD.md
```
# Agent 复盘报告 - 2026-03-27

**复盘时间**: 2026-03-27 18:03

## 项目
### 项目名称
- 路径：...
- 功能：...
- 进展：...

## 任务
### 任务名称
**方法**：...
```

---

## 注意事项

- 代码块要完整可执行
- 注明出处（哪个 Agent 发现）
- 技能库只添加不覆盖
- 归档后删除原始文件
