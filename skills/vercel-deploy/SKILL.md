# Vercel 部署 PC-Roadmap 项目技能

## 项目概述

本技能记录将 HP 产品可视化平台（PC-Roadmap）部署到 Vercel 的完整流程，包括：
- 前后端分离架构
- Vercel Serverless Functions 作为 API
- Turso (SQLite 云端数据库)
- 常见问题及解决方案

## 技术架构

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│   前端 (静态)    │ ──▶ │  Vercel Serverless │ ──▶ │  Turso DB   │
│  HTML/CSS/JS    │     │      Functions     │     │  (SQLite)   │
└─────────────────┘     └──────────────────┘     └─────────────┘
```

## 部署步骤

### 1. 项目准备

#### 1.1 创建 Vercel 专用项目目录结构

```
pc-roadmap-vercel/
├── frontend/           # 前端静态文件
│   ├── index.html
│   ├── scripts/
│   │   ├── api.js     # API 调用模块（关键！）
│   │   └── app.js
│   └── styles/
├── api/               # Serverless Functions
│   ├── _lib/
│   │   └── db.js      # 数据库连接配置
│   ├── products/
│   │   ├── index.js   # GET/POST /api/products
│   │   ├── brands.js  # GET /api/products/brands
│   │   └── [id].js    # GET/PUT/DELETE /api/products/:id
│   └── package.json
├── vercel.json        # Vercel 路由配置
└── README.md
```

#### 1.2 前端 API 配置要点

**⚠️ 关键：API_BASE 不能包含 /api 后缀！**

```javascript
// frontend/scripts/api.js
const API_BASE = (typeof window !== 'undefined' && window.ENV && window.ENV.API_BASE)
  ? window.ENV.API_BASE
  : 'http://localhost:3001';
```

```html
<!-- frontend/index.html 的 <head> 中 -->
<script>
  window.ENV = {
    API_BASE: 'https://your-project.vercel.app'
  };
</script>
```

**❌ 错误写法：**
```javascript
API_BASE: 'https://your-project.vercel.app/api'  // 会导致 /api/api/products 双重路径
```

### 2. Vercel 项目创建

1. 打开 https://vercel.com
2. 用 GitHub 账号登陆
3. 点击 "Add New..." → "Project"
4. Import 你的 GitHub 仓库
5. 配置：
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: 留空
   - **Output Directory**: 留空

### 3. 环境变量配置

在 Vercel Project Settings → Environment Variables 添加：

| Name | Value | 说明 |
|------|-------|------|
| TURSO_DATABASE_URL | libsql://xxx.turso.io | Turso 数据库地址 |
| TURSO_AUTH_TOKEN | eyJhbGci... | Turso 认证令牌 |

### 4. vercel.json 路由配置

```json
{
  "framework": null,
  "routes": [
    { "src": "/api/products/brands", "dest": "/api/products/brands.js" },
    { "src": "/api/products/[^/]+$", "dest": "/api/products/[id].js" },
    { "src": "/api/products", "dest": "/api/products/index.js" },
    { "src": "/(.*)", "dest": "/frontend/$1" }
  ]
}
```

### 5. 数据库设置

#### 5.1 Turso 注册与创建

1. 访问 https://turso.tech
2. 用 GitHub 登陆
3. 创建数据库，记下 Database URL 和 Auth Token
4. 在 Turso 控制台执行建表 SQL：

```sql
CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  brand TEXT,
  category TEXT,
  price REAL,
  performance_score INTEGER,
  cpu TEXT,
  gpu TEXT,
  ram TEXT,
  storage TEXT,
  screen_size REAL,
  image_url TEXT,
  source_url TEXT,
  source TEXT DEFAULT 'manual',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### 5.2 数据导入

从本地 SQLite 导出并导入到 Turso：

```bash
# 导出 INSERT 语句
sqlite3 local.db "SELECT 'INSERT INTO products (...) VALUES (...);' FROM products;" > inserts.sql

# 批量执行（使用 curl 直接调用 Turso HTTP API）
TOKEN="your-turso-auth-token"
DB_URL="https://your-db.turso.io/v2/pipeline"

while IFS= read -r sql; do
  curl -s -X POST "$DB_URL" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"requests\":[{\"type\":\"execute\",\"stmt\":{\"sql\":\"$sql\"}},{\"type\":\"close\"}]}"
done < inserts.sql
```

### 6. API 实现要点

#### 6.1 数据库连接（使用原生 fetch 避免 @libsql/client 问题）

```javascript
// api/_lib/db.js
function getApiUrl(libsqlUrl) {
  return libsqlUrl.replace('libsql://', 'https://');
}

const BASE_URL = getApiUrl(process.env.TURSO_DATABASE_URL);
const AUTH_TOKEN = process.env.TURSO_AUTH_TOKEN;

async function execute(sql, params = []) {
  const response = await fetch(`${BASE_URL}/v2/pipeline`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${AUTH_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      requests: [{
        type: 'execute',
        stmt: { sql, args: params }
      }, {
        type: 'close'
      }]
    })
  });

  const result = await response.json();
  // 处理结果...
  return result;
}

module.exports = {
  execute: async (sql, params) => {
    try {
      return await execute(sql, params);
    } catch (error) {
      console.error('DB Error:', error.message);
      throw error;
    }
  }
};
```

#### 6.2 API 函数模板

```javascript
// api/products/index.js
module.exports = async (req, res) => {
  // CORS 头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    if (req.method === 'GET') {
      // 处理 GET 请求
      const result = await client.execute('SELECT * FROM products');
      return res.status(200).json({ success: true, data: result.rows });
    }

    if (req.method === 'POST') {
      // 处理 POST 请求
      const { name, brand, category, price } = req.body;
      const result = await client.execute(
        'INSERT INTO products (name, brand, category, price) VALUES (?, ?, ?, ?)',
        [name, brand, category, price]
      );
      return res.status(201).json({ success: true, data: { id: result.lastInsertRowid } });
    }

    return res.status(405).json({ success: false, error: 'Method not allowed' });

  } catch (err) {
    console.error('API Error:', err);
    return res.status(500).json({ success: false, error: err.message });
  }
};
```

## 常见问题与解决方案

### 问题 1: /api/api/products 双重路径

**症状：** 浏览器 Console 显示 404，API 请求变成 `/api/api/products`

**原因：** `API_BASE` 配置成了 `https://xxx.vercel.app/api`，然后代码又拼接了 `/api`

**解决：** 
```javascript
// ❌ 错误
API_BASE: 'https://xxx.vercel.app/api'

// ✅ 正确
API_BASE: 'https://xxx.vercel.app'
```

### 问题 2: Turso @libsql/client migration jobs 错误

**症状：** API 返回 400 错误，body 包含 "jobs" 相关错误信息

**原因：** @libsql/client 0.6+ 有自动迁移检查 bug

**解决：** 使用原生 fetch 直接调用 Turso HTTP API，不使用 @libsql/client

### 问题 3: 前端显示"暂无数据"

**排查步骤：**
1. 检查浏览器 Console 有无错误
2. 确认 `/api/products` 是否返回正确 JSON
3. 确认 CORS 配置正确
4. 检查 API_BASE 配置

### 问题 4: Vercel 路由 404

**症状：** 部署后访问返回 404

**解决：** 检查 vercel.json 配置，确保 routes 顺序正确

```json
{
  "framework": null,
  "routes": [
    { "src": "/api/(.*)", "dest": "/api/$1" },
    { "src": "/(.*)", "dest": "/frontend/$1" }
  ]
}
```

### 问题 5: Vercel 国内访问慢

**原因：** Vercel 在部分中国网络环境下访问不稳定

**解决方案：**
1. 等待网络恢复
2. 使用代理/VPN
3. 绑定自己的域名（配合 Cloudflare CDN 加速）
4. 考虑其他国内可访问的平台

## GitHub 推送与自动部署

```bash
cd ~/pc-roadmap-vercel
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/username/PC-Roadmap-Vercel.git
git branch -M main
git push -u origin main
```

Vercel 会自动检测 GitHub 仓库，之后每次推送到 main 分支都会自动部署。

## 项目仓库

- **本地版本**: https://github.com/dccaoxy/PC-Roadmap
- **Vercel 版本**: https://github.com/dccaoxy/PC-Roadmap-Vercel
- **在线地址**: https://pc-roadmap-vercel.vercel.app

## 相关文件路径

- 本地前端: `~/Roadmap/frontend/`
- Vercel 版本: `~/pc-roadmap-vercel/`
- 建表 SQL: 见上方 5.1 节

## 总结

部署要点：
1. **API_BASE 不能带 /api 后缀**
2. **使用原生 fetch 调用 Turso**（避免 @libsql/client 问题）
3. **vercel.json 路由配置要完整**
4. **环境变量要正确配置**
5. **建表 SQL 要在 Turso 控制台执行**
