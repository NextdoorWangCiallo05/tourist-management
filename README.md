# 智游云管 · 旅游业务管理系统

> 基于 Vue 3 + Flask 3 的全栈旅游业务管理系统 — 面向旅行社提供旅游团管理、申请审批、路线维护、订金计算、财务导出、AI 智能助手等核心业务功能。

<p align="center">
  <img src="https://img.shields.io/badge/Frontend-Vue_3-4FC08D?logo=vue.js" alt="Vue 3">
  <img src="https://img.shields.io/badge/Backend-Flask_3-000000?logo=flask" alt="Flask 3">
  <img src="https://img.shields.io/badge/UI-Element_Plus-409EFF?logo=element" alt="Element Plus">
  <img src="https://img.shields.io/badge/Build-Vite_5-646CFF?logo=vite" alt="Vite 5">
  <img src="https://img.shields.io/badge/Auth-JWT-FF4081?logo=json-web-tokens" alt="JWT">
  <img src="https://img.shields.io/badge/DB-SQLite/MySQL-4479A1?logo=sqlite" alt="Database">
  <img src="https://img.shields.io/badge/i18n-中文/English-409EFF?logo=googletranslate" alt="i18n">
  <img src="https://img.shields.io/badge/AI-OpenAI/GPT-412991?logo=openai" alt="AI">
</p>

---

## 📋 功能总览

| 模块 | 核心功能 | 亮点 |
|------|---------|------|
| **📊 数据大屏** | 核心指标 + ECharts 图表（饼图/折线图） | 实时统计 + 待办提醒 |
| **🏕️ 旅游团** | 增删改查 / 价格管理 / 公开控制 | 价格历史追踪 + 名额实时检查 |
| **🗺️ 路线** | 增删改查 / 版本管理 | 启用/停用 + 版本历史 |
| **📝 申请** | 报名 / 参加者批量导入 / 付费 / 取消 | 新增参加者自动创建新申请 + 订金计算 + 自动退款 |
| **🖨️ 确认书** | 确认书列表 + 余额交款单 + PDF 下载 | ReportLab 中文 PDF + 余额通知单 |
| **💰 财务** | 日结汇总 / Excel 导出 / CSV 导出 | 手动/自动导出 + 订金/余款分类统计 |
| **🤖 AI 助手** | 自然语言查询 / 异常检测 / 智能客服 | 规则引擎 + 可选 GPT-4o 集成 |
| **🌙 深色模式** | 一键切换 / CSS 变量驱动 | Element Plus 全组件适配 |
| **🌐 多语言** | 中文 / English | vue-i18n 全组件覆盖 |
| **👥 用户管理** | 注册 / 角色管理 / 权限控制 | 管理员 + 操作员双角色 |
| **📋 审计** | 全量操作日志 | 按类型筛选 + 分页 + 时间倒序 |

## 💻 技术栈

### 前端

| 技术 | 用途 | 版本 |
|------|------|------|
| **Vue 3** | 渐进式前端框架（Composition API + `<script setup>`） | ^3.5 |
| **Vue Router 4** | 路由管理与导航守卫 | ^4.6 |
| **Pinia** | 状态管理（语言/主题/用户） | ^3.0 |
| **Element Plus** | 企业级 UI 组件库 | ^2.13 |
| **ECharts 6 + vue-echarts** | 数据可视化图表 | ^8.0 |
| **vue-i18n 9** | 国际化（中/英双语） | ^9.0 |
| **Axios** | HTTP 请求封装（拦截器 + 统一错误处理） | ^1.7 |
| **Vite 5** | 构建工具（HMR < 1s） | ^5.0 |

### 后端

| 技术 | 用途 | 版本 |
|------|------|:----:|
| **Flask** | Python Web 框架 | **3.0.3** |
| **Flask-SQLAlchemy** | ORM 数据库操作 | 3.1.1 |
| **Flask-JWT-Extended** | JWT Token 认证 | 4.7.4 |
| **Flask-CORS** | 跨域资源共享 | 4.0.2 |
| **Flask-Migrate** | 数据库版本迁移 | 4.1.0 |
| **Flask-SocketIO** | WebSocket 实时通知 | 5.6.1 |
| **Flask-Swagger-UI** | OpenAPI 交互式文档 | 5.32.6 |
| **Werkzeug** | 密码哈希与验证 | **3.0.6** |
| **OpenAI** | AI 对话集成（可选） | 2.30.0 |
| **reportlab** | PDF 文档生成（微软雅黑字体） | 4.5.1 |
| **openpyxl** | Excel 文件导出 | 3.1.5 |
| **SQLite / MySQL** | 数据库（环境变量切换） | - |

## 📁 项目结构

```
Travel/
├── backend/
│   ├── app.py                  # 应用入口（9个Blueprint + Swagger）
│   ├── config.py               # 双配置：Config / MySQLConfig
│   ├── models.py               # 9 个数据库模型
│   ├── requirements.txt        # Python 依赖清单
│   ├── seed_data.py            # 示例数据（5路线 + 7旅游团 + 3申请）
│   ├── .flake8                 # Flake8 规范
│   ├── blueprints/
│   │   ├── auth.py             # 登录/注册/用户管理（JWT）
│   │   ├── agent.py            # AI 助手（规则引擎 + GPT 集成）
│   │   ├── groups.py           # 旅游团 CRUD + 名额检查
│   │   ├── routes_bp.py        # 路线管理 + 版本历史
│   │   ├── applications.py     # 申请全流程 + CSV导入 + 新参加者→新申请
│   │   ├── participants.py     # 参加者管理 + 责任人转移
│   │   ├── finance.py          # 财务导出 + Excel + PDF确认书
│   │   ├── stats.py            # Dashboard 统计
│   │   ├── logs.py             # 审计日志（分页）
│   │   ├── socket.py           # WebSocket 通知
│   │   └── response.py         # 统一响应 {code, msg, data}
│   └── instance/
│       └── tourist.db          # SQLite 数据库
├── frontend/
│   ├── index.html              # Vite 入口
│   ├── vite.config.js          # Vite 配置（proxy + port）
│   ├── package.json
│   ├── .eslintrc.js
│   ├── src/
│   │   ├── main.js             # 应用启动（Pinia + Router + Element + i18n）
│   │   ├── style.css           # 全局 CSS 变量 + 深色模式 + Element 覆盖
│   │   ├── App.vue
│   │   ├── locales/
│   │   │   ├── zh-CN.js        # 中文语言包（100+ 条翻译）
│   │   │   └── en.js           # 英文语言包
│   │   ├── stores/
│   │   │   ├── user.js         # Pinia 用户状态 + 登录持久化
│   │   │   └── settings.js     # 语言/主题状态 + vue-i18n 实例
│   │   ├── router/
│   │   │   └── index.js        # 13 条路由 + 导航守卫
│   │   ├── utils/
│   │   │   └── request.js      # Axios 封装 + 统一响应处理
│   │   ├── components/
│   │   │   ├── AppLayout.vue   # 公共布局（56px 顶栏 + i18n日期）
│   │   │   ├── AppSidebar.vue  # 纯白极简侧边栏（i18n标签）
│   │   │   └── AiChat.vue      # 浮动 AI 聊天面板（右下角气泡）
│   │   └── views/
│   │       ├── Login.vue               # 卡片登录 + 注册弹窗
│   │       ├── Dashboard.vue           # 数据大屏（ECharts + i18n）
│   │       ├── CreateApplication.vue   # 新建申请（i18n表单）
│   │       ├── ApplicationList.vue     # 申请列表（分页 + i18n）
│   │       ├── ApplicationDetail.vue   # 申请详情（i18n + 增强确认弹窗）
│   │       ├── TourGroupList.vue       # 旅游团查询（i18n）
│   │       ├── TourGroupManagement.vue # 旅游团管理（i18n）
│   │       ├── RouteManagement.vue     # 路线管理（i18n）
│   │       ├── ConfirmationPrint.vue   # 确认书打印 + PDF（i18n）
│   │       ├── DailyExport.vue         # 财务导出 + Excel（i18n）
│   │       ├── AuditLogs.vue           # 操作日志审计（i18n）
│   │       ├── Settings.vue            # 系统设置（语言切换 + 深色模式）
│   │       └── UserManagement.vue      # 用户管理（管理员专属）
├── 示例数据_参加者导入.csv      # CSV 批量导入模板
├── UML建模说明.md               # 完整 UML 文档
├── 验收文档.md                  # 70 项验收测试用例
└── README.md
```

## 🚀 快速开始

### 环境要求

| 工具 | 最低版本 |
|------|---------|
| Python | 3.8+ |
| Node.js | 16+ |
| npm | 8+ |

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python seed_data.py    # （可选）初始化示例数据
python app.py
```

后端默认运行在 **http://localhost:5000**

> 首次启动自动创建 SQLite 数据库和默认管理员账户。
> 如需切换 MySQL，修改 `config.py` 中的配置类即可。

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 **http://localhost:8081**

### 默认账号

| 用户名 | 密码 | 角色 | 权限 |
|--------|------|------|------|
| `admin` | `admin123` | 管理员 | 全部权限（含用户管理） |
| 注册用户 | 自设 | 操作员 | 业务操作权限 |

## 🎯 核心业务场景

### 场景一：创建旅游团 → 公开

```
admin 登录 → 旅游团管理 → 新增旅游团
    设置路线、价格、容量 → 公开 → 前台可见
```

### 场景二：客户报名 → 完成

```
客户咨询 → 新建申请 → 选择旅游团
    → 填写参加者 → 提交申请 → 生成新申请编号
    → 支付订金 → 补齐参加者信息
    → 完成申请 → 生成确认书 → 下载PDF
    → 新增参加者 → 自动创建独立新申请
```

### 场景三：财务日结

```
每日经营结束 → 财务导出
    → 查看订金/余款汇总
    → 导出 Excel 或 CSV
```

### 场景四：AI 智能助手

```
点击右下角 AI 助手 → 输入自然语言
    → "查旅游团"     → 列出可报名旅游团
    → "系统概览"     → 统计数据一览
    → "异常检测"     → 检查待处理异常
    → "取消手续费规则" → 显示计费规则
```

## 📊 业务规则

### 订金计算

| 距出发天数 | 订金比例 |
|-----------|:-------:|
| ≥ 60 天 | **10%** |
| ≥ 30 天 | **20%** |
| < 30 天 | **100%** |

### 取消手续费

| 距出发天数 | 手续费比例 |
|-----------|:---------:|
| ≥ 30 天 | **免费** |
| ≥ 10 天 | **20%** |
| ≥ 1 天 | **50%** |
| 当天 | **100%** |

### 余款支付期限

| 条件 | 截止日期 |
|------|---------|
| 正常情况 | 出发前 30 天 |
| 交款单发送后 < 10 天 | 发送后第 10 天 |

## 🎨 深色模式

在设置页面一键切换浅色/深色模式：

| 元素 | 浅色 | 深色 |
|------|:----:|:----:|
| 背景色 | `#f8f9fc` | `#0f1117` |
| 卡片色 | `#ffffff` | `#1a1d27` |
| 主文字 | `#0b0f1a` | `#e8eaed` |
| 主色调 | `#4f6ef7` | `#6b8aff` |
| 阴影 | 浅灰 | 深黑 |

Element Plus 全组件（表格/弹窗/输入框/分页/日期选择器）深色适配。

## 🌐 多语言

设置页面一键切换中/英文：

- **中文**：全界面中文（默认）
- **English**：全界面英文，含导航/按钮/表格列/标签/弹窗

切换由 vue-i18n 驱动，即时生效，持久化保存。

## 🤖 AI 智能助手

系统内置 `POST /api/agent/chat` 接口，支持二种模式：

### 模式一：规则引擎（免 API Key，内置可用）

| 你问 | 系统回答 |
|------|---------|
| "查旅游团" | 列出所有可报名旅游团及余位 |
| "去云南的旅游团" | 按路线名称搜索 |
| "查申请 AP12345678" | 显示申请详情 |
| "张伟的申请" | 按责任人查询 |
| "系统概览" | 申请/旅游团统计数据 |
| "异常检测" | 订金超期未完成、出发过期未处理、名额将满等 |
| "取消手续费怎么算" | 显示完整手续费规则 |

### 模式二：GPT 集成（需 API Key）

```bash
$env:OPENAI_API_KEY = "sk-xxx"
```

规则引擎未命中时自动调用 GPT-4o-mini 回答。

## 🔌 API 文档

> 启动后端后访问 **http://localhost:5000/api/docs** 查看交互式 Swagger UI 文档

### 认证与用户

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|:----:|
| POST | `/api/login` | 登录获取 JWT Token | 公开 |
| POST | `/api/register` | 注册新账户（操作员） | 公开 |
| GET | `/api/users` | 查看所有用户 | 管理员 |
| PUT | `/api/users/:id/role` | 修改用户角色 | 管理员 |
| DELETE | `/api/users/:id` | 删除用户 | 管理员 |

### AI 助手

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/agent/chat` | AI 对话（规则引擎 / GPT） |
| GET | `/api/agent/anomalies` | 获取系统异常列表 |

### 旅游团

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tour_groups` | 获取已公开旅游团 |
| GET | `/api/tour_groups/all` | 获取所有旅游团 |
| POST | `/api/tour_groups` | 创建旅游团 |
| PUT | `/api/tour_groups/:id` | 更新旅游团信息 |
| GET | `/api/tour_groups/:id/check_availability` | 检查剩余名额 |
| PUT | `/api/tour_groups/:id/price` | 修改价格 |
| POST | `/api/tour_groups/:id/publish` | 公开旅游团 |
| POST | `/api/tour_groups/:id/unpublish` | 取消公开 |

### 路线

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/routes` | 获取所有路线 |
| POST | `/api/routes` | 创建路线 |
| PUT | `/api/routes/:id` | 更新路线 |
| POST | `/api/routes/:id/activate` | 启用路线 |
| POST | `/api/routes/:id/deactivate` | 停用路线 |

### 申请

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/applications` | 申请列表（分页 + 搜索） |
| POST | `/api/applications` | 创建申请 |
| GET | `/api/applications/:no` | 申请详情 |
| POST | `/api/applications/:no/participants` | 新参加者→创建新申请 |
| POST | `/api/applications/:no/participants/import` | CSV 批量导入 |
| POST | `/api/applications/:no/deposit` | 支付订金 |
| POST | `/api/applications/:no/balance` | 支付余款 |
| POST | `/api/applications/:no/complete` | 完成申请 |
| POST | `/api/applications/:no/cancel` | 取消申请 |

### 参加者

| 方法 | 路径 | 说明 | 亮点 |
|------|------|------|------|
| PUT | `/api/participants/:id` | 更新参加者信息 | - |
| POST | `/api/participants/:id/cancel` | 取消参加 | 责任人自动转移 |

### 财务与统计

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/daily_export` | 财务数据导出（JSON） |
| GET | `/api/daily_export/excel` | 财务数据导出（.xlsx） |
| GET | `/api/confirmations` | 确认书列表 |
| GET | `/api/confirmations/:no/pdf` | 下载确认书 PDF（中文） |
| GET | `/api/stats` | Dashboard 统计数据 |

### 审计

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/audit_logs` | 操作日志（分页 + 筛选） |

## 🗄️ 数据模型

| 表名 | 说明 | 关键字段 |
|------|------|---------|
| `users` | 用户账户 | username, password_hash, display_name, role |
| `routes` | 旅游路线 | route_code, route_name, is_active, version |
| `route_history` | 路线版本历史 | route_id, version, change_type, snapshot |
| `tour_groups` | 旅游团 | group_code, route_id, departure_date, adult_price, is_public |
| `price_history` | 价格变更历史 | tour_group_id, adult_price, child_price, discount_rate |
| `applications` | 申请单 | application_no, tour_group_id, status |
| `participants` | 参加者 | application_id, name, id_number, is_adult, is_responsible, status |
| `payment_records` | 支付记录 | application_id, payment_type, amount, paid_at |
| `audit_logs` | 操作日志 | username, action, target_type, target_id, detail |
| `system_config` | 系统配置 | config_key, config_value |

## 🧪 Pro 亮点

| 亮点 | 说明 |
|------|------|
| **Flask 3.0** | 最新 Flask 版本，迁移兼容性 100% 验证 |
| **Vite 5 构建** | HMR < 1s，构建速度 10x |
| **Pinia 集中状态** | 用户/语言/主题统一管理，替代散落 localStorage |
| **Blueprint 架构** | app.py 拆分为 10 个模块，职责清晰 |
| **统一响应格式** | `{code, msg, data}` 全局统一，拦截器自动处理 |
| **Flask-Migrate** | 数据库版本迁移，支持 SQLite / MySQL 切换 |
| **CSS 变量体系** | 12 个 Token 驱动的设计系统，深色/浅色一键切换 |
| **深色模式** | Element Plus 全组件深色适配（表格/弹窗/输入框/分页/日期） |
| **vue-i18n 多语言** | 14/14 组件覆盖，中/英双语完整翻译包 |
| **AI 智能助手** | 规则引擎 + GPT 双模式，自然语言查询 + 异常检测 + 客服 |
| **用户注册与管理** | 注册/角色管理/权限控制，管理员+操作员双角色 |
| **参加者→新申请** | 新增参加者自动创建独立申请，符合真实业务 |
| **责任人转移** | 取消责任人参加者时，弹窗选择新责任人 |
| **增强确认弹窗** | 取消/删除/改角色弹窗含完整规则提示和不可撤销警告 |
| **Swagger 文档** | OpenAPI 3.0 + 交互式 UI |
| **PDF 确认书** | ReportLab + 微软雅黑中文 PDF |
| **ECharts 大屏** | 饼图 + 折线图动态可视化 |
| **WebSocket 通知** | SocketIO 实时推送 |
| **分页** | 申请列表 + 日志列表后端分页 |
| **代码规范** | ESLint + Flake8 |
| **示例数据** | 一键 seed_data.py 注入演示数据 |
| **验收文档** | 70 项测试用例覆盖全部模块 |
