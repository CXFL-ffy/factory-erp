# 🏭 食品加工厂 ERP 管理系统

## 快速部署指南

### 第一步：创建 Supabase 项目 (5 分钟)

1. 访问 https://supabase.com 注册账号
2. 点击 "New Project" 创建新项目
3. 设置数据库密码 (请妥善保管)
4. 等待项目创建完成

### 第二步：初始化数据库 (3 分钟)

1. 在 Supabase 左侧菜单点击 "SQL Editor"
2. 复制 `init_db.sql` 全部内容
3. 粘贴到 SQL Editor 中
4. 点击 "Run" 执行

### 第三步：创建管理员账号 (2 分钟)

1. 在 Supabase 左侧菜单点击 "Authentication" → "Users"
2. 点击 "Add user" → "Create new user"
3. 邮箱：`admin@factory.com`
4. 密码：`admin123`
5. 点击 "Create user"

### 第四步：获取 API 密钥 (1 分钟)

1. 在 Supabase 左侧菜单点击 "Settings" → "API"
2. 复制 "Project URL"
3. 复制 "anon/public" key
4. 保存这两个值

### 第五步：部署到 Streamlit Cloud (5 分钟)

1. 访问 https://github.com 创建账号
2. 创建新仓库 `factory-erp`
3. 上传所有文件 (app.py, crawler.py, requirements.txt, .env.example)
4. 创建 `.env` 文件，填入 Supabase 配置：
