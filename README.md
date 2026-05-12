# 智游云管 - 旅游业务管理系统

基于 Vue 3 + Flask 的全栈旅游业务管理系统，支持旅游团管理、申请管理、路线管理、订金计算、财务导出等核心业务功能。

## 技术栈

### 前端
- **Vue 3** (Composition API + `<script setup>`)
- **Vue Router 4** (路由守卫、导航守卫)
- **Element Plus** (UI 组件库)
- **Axios** (HTTP 请求)
- **Vue CLI 5** (项目构建)

### 后端
- **Flask 2.3** (Web 框架)
- **Flask-SQLAlchemy** (ORM)
- **Flask-JWT-Extended** (JWT 认证)
- **Flask-CORS** (跨域支持)
- **SQLite** (数据库)

## 项目结构

```
Tourist/
├── backend/
│   ├── app.py              # Flask 应用入口，所有 API 路由
│   ├── models.py           # 数据库模型定义
│   ├── config.py           # 应用配置
│   ├── requirements.txt    # Python 依赖
│   └── instance/
│       └── tourist.db      # SQLite 数据库文件
├── frontend/
│   ├── public/
│   │   └── index.html      # HTML 入口
│   ├── src/
│   │   ├── main.js         # Vue 应用入口
│   │   ├── App.vue         # 根组件
│   │   ├── router/
│   │   │   └── index.js    # 路由配置
│   │   └── views/
│   │       ├── Login.vue                 # 登录页
│   │       ├── Dashboard.vue             # 首页概览
│   │       ├── CreateApplication.vue     # 新建申请
│   │       ├── ApplicationList.vue       # 申请管理
│   │       ├── ApplicationDetail.vue     # 申请详情
│   │       ├── TourGroupList.vue         # 旅游团查询
│   │       ├── TourGroupManagement.vue   # 旅游团管理
│   │       ├── RouteManagement.vue       # 路线管理
│   │       ├── ConfirmationPrint.vue     # 确认书打印
│   │       └── DailyExport.vue           # 财务导出
│   ├── package.json
│   └── vue.config.js
└── README.md
```

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 8+

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python app.py
```

后端默认运行在 `http://localhost:5000`

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://localhost:8081`

### 默认登录账号

| 用户名 | 密码 |
|--------|------|
| admin  | admin123 |

## 功能模块

### 1. 登录认证
- JWT Token 认证
- 路由守卫保护，未登录自动跳转登录页

### 2. 首页概览 (Dashboard)
- 今日申请数、参加者数、进行中团数统计
- 待办提醒（待支付订金、待支付余款）
- 快捷操作入口

### 3. 旅游团管理 (TourGroupManagement)
- 旅游团的新增、编辑、删除
- 成人/儿童价格设置（含价格历史记录）
- 公开/取消公开控制
- 截止日期、出发日期、最大容量设置

### 4. 旅游团查询 (TourGroupList)
- 查看已公开的旅游团
- 按路线名称搜索
- 查看剩余名额

### 5. 路线管理 (RouteManagement)
- 路线的新增、编辑、删除
- 路线版本历史追踪
- 路线启用/停用控制

### 6. 新建申请 (CreateApplication)
- 选择旅游团
- 录入参加者信息（姓名、证件类型、证件号码、电话）
- 自动区分成人和儿童
- 费用预估（总费用、订金金额）
- 提交申请后自动跳转详情页

### 7. 申请管理 (ApplicationList)
- 申请列表展示（申请编号、路线、责任人、状态等）
- 按申请编号搜索
- 取消申请操作

### 8. 申请详情 (ApplicationDetail)
- 申请基本信息展示
- 参加者列表
- 订金支付
- 余款支付
- 申请完成/取消操作

### 9. 确认书打印 (ConfirmationPrint)
- 昨日完成的申请列表
- 打印确认书
- 余额缴费通知

### 10. 财务导出 (DailyExport)
- 昨日收款汇总
- 按支付类型统计
- CSV 文件导出

## 业务规则

### 订金计算
| 距出发天数 | 订金比例 |
|-----------|---------|
| >= 60 天  | 10%     |
| >= 30 天  | 20%     |
| < 30 天   | 100%    |

### 取消手续费
| 距出发天数 | 手续费比例 |
|-----------|-----------|
| >= 30 天  | 免费      |
| >= 10 天  | 20%       |
| >= 1 天   | 50%       |
| 当天      | 100%      |

## API 接口

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/login` | 登录获取 Token |

### 旅游团
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tour_groups` | 获取已公开旅游团 |
| GET | `/api/tour_groups/all` | 获取所有旅游团 |
| POST | `/api/tour_groups` | 创建旅游团 |
| PUT | `/api/tour_groups/<id>` | 更新旅游团 |
| GET | `/api/tour_groups/<id>/check_availability` | 检查名额 |
| PUT | `/api/tour_groups/<id>/price` | 更新价格 |
| POST | `/api/tour_groups/<id>/publish` | 公开旅游团 |
| POST | `/api/tour_groups/<id>/unpublish` | 取消公开 |

### 路线
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/routes` | 获取所有路线 |
| POST | `/api/routes` | 创建路线 |
| PUT | `/api/routes/<id>` | 更新路线 |
| DELETE | `/api/routes/<id>` | 删除路线 |

### 申请
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/applications` | 获取申请列表 |
| POST | `/api/applications` | 创建申请 |
| GET | `/api/applications/<appNo>` | 获取申请详情 |
| POST | `/api/applications/<appNo>/participants` | 添加参加者 |
| POST | `/api/applications/<appNo>/deposit` | 支付订金 |
| POST | `/api/applications/<appNo>/balance` | 支付余款 |
| POST | `/api/applications/<appNo>/complete` | 完成申请 |
| POST | `/api/applications/<appNo>/cancel` | 取消申请 |

### 参加者
| 方法 | 路径 | 说明 |
|------|------|------|
| PUT | `/api/participants/<id>` | 更新参加者信息 |
| POST | `/api/participants/<id>/cancel` | 取消参加者 |

### 财务
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/daily_export` | 昨日财务导出 |
| GET | `/api/confirmations` | 昨日确认书列表 |
