# 智游云管 - 旅游业务管理系统

基于 Vue 3 + Flask 的全栈旅游业务管理系统，面向旅行社/旅游公司提供旅游团管理、申请管理、路线管理、订金计算、财务导出等核心业务功能。

---

## 技术栈

### 前端
| 技术 | 用途 |
|------|------|
| **Vue 3** (Composition API + `<script setup>`) | 渐进式前端框架 |
| **Vue Router 4** | 路由管理与导航守卫 |
| **Element Plus** | 企业级 UI 组件库 |
| **ECharts + vue-echarts** | 数据可视化图表 |
| **Axios** | HTTP 请求封装 |

### 后端
| 技术 | 用途 |
|------|------|
| **Flask 2.3** | Python Web 框架 |
| **Flask-SQLAlchemy** | ORM 数据库操作 |
| **Flask-JWT-Extended** | JWT Token 认证 |
| **Flask-CORS** | 跨域资源共享 |
| **Werkzeug** | 密码哈希 |
| **openpyxl** | Excel 文件处理 |
| **SQLite** | 数据库 |

## 项目结构

```
Travel/
├── backend/
│   ├── app.py              # Flask 应用入口 + 所有 API 路由
│   ├── models.py           # 数据库模型 (8个表)
│   ├── config.py           # 应用配置
│   ├── requirements.txt    # Python 依赖
│   ├── .flake8             # Python 代码规范
│   └── instance/
│       └── tourist.db      # SQLite 数据库
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AppLayout.vue       # 公共布局组件
│   │   │   └── AppSidebar.vue      # 侧边栏组件
│   │   ├── router/
│   │   │   └── index.js            # 路由配置 (11条路由)
│   │   ├── utils/
│   │   │   └── request.js          # Axios 封装 (拦截器+统一错误处理)
│   │   └── views/
│   │       ├── Login.vue                    # 登录页
│   │       ├── Dashboard.vue                # 首页概览 (ECharts大屏)
│   │       ├── CreateApplication.vue        # 新建申请
│   │       ├── ApplicationList.vue          # 申请管理
│   │       ├── ApplicationDetail.vue        # 申请详情
│   │       ├── TourGroupList.vue            # 旅游团查询
│   │       ├── TourGroupManagement.vue      # 旅游团管理
│   │       ├── RouteManagement.vue          # 路线管理
│   │       ├── ConfirmationPrint.vue        # 确认书打印
│   │       ├── DailyExport.vue              # 财务导出
│   │       └── AuditLogs.vue                # 操作日志审计
│   ├── .eslintrc.js              # JavaScript 代码规范
│   ├── package.json
│   └── vue.config.js
├── 示例数据_参加者导入.csv     # CSV 批量导入示例
├── .gitignore
├── UML建模说明.md               # UML 模型文档
└── README.md
```

## 功能模块

### 1. 登录认证
- JWT Token 认证 + 路由守卫自动跳转
- 记住密码功能
- 登录日志审计

### 2. 数据可视化大屏 (Dashboard)
- 4 项核心指标：申请总数、参加者总数、总收款、旅游团总数
- **申请状态分布饼图** (已处理/已完成/已取消)
- **近7日申请趋势折线图**
- 待办提醒、快捷操作入口

### 3. 旅游团管理
- 旅游团的增删改查
- 成人/儿童价格设置（含价格历史记录）
- 公开/取消公开控制
- 截止日期、出发日期、最大容量设置

### 4. 旅游团查询
- 查看已公开旅游团
- 按路线名称/代码搜索
- 实时剩余名额检查
- 一键报名跳转

### 5. 路线管理
- 路线增删改查
- 路线版本历史追踪
- 启用/停用控制（含审计日志）

### 6. 申请管理
- 创建申请 → 选择旅游团 + 添加参加者 + 费用预估
- **CSV/Excel 批量导入参加者**
- 支付订金 / 支付余款
- 完成申请 / 取消申请（自动计算手续费与退款）
- 申请列表搜索与筛选

### 7. 确认书打印
- 昨日完成的申请确认书列表
- 单份打印 / 全部打印
- 余额缴费通知单

### 8. 财务导出
- 昨日收款数据汇总
- 按订金/余款分类统计
- CSV 文件导出（UTF-8 BOM 编码）

### 9. 操作日志审计
- 全量操作记录：登录、申请、支付、管理操作
- 按操作类型筛选
- 分页展示，时间倒序

## 业务规则

### 订金计算
| 距出发天数 | 订金比例 |
|-----------|---------|
| ≥ 60 天 | 10% |
| ≥ 30 天 | 20% |
| < 30 天 | 100% |

### 取消手续费
| 距出发天数 | 手续费比例 |
|-----------|-----------|
| ≥ 30 天 | 免费 |
| ≥ 10 天 | 20% |
| ≥ 1 天 | 50% |
| 当天 | 100% |

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

首次启动自动创建数据库和默认管理员账户。

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
| admin | admin123 |

## API 接口文档

| 方法 | 路径 | 说明 |
|------|------|------|
| **认证** | | |
| POST | `/api/login` | 登录获取 Token |
| | | |
| **旅游团** | | |
| GET | `/api/tour_groups` | 获取已公开旅游团 |
| GET | `/api/tour_groups/all` | 获取所有旅游团 |
| POST | `/api/tour_groups` | 创建旅游团 |
| PUT | `/api/tour_groups/<id>` | 更新旅游团 |
| GET | `/api/tour_groups/<id>/check_availability` | 检查剩余名额 |
| PUT | `/api/tour_groups/<id>/price` | 修改价格 |
| POST | `/api/tour_groups/<id>/publish` | 公开 |
| POST | `/api/tour_groups/<id>/unpublish` | 取消公开 |
| | | |
| **路线** | | |
| GET | `/api/routes` | 获取所有路线 |
| POST | `/api/routes` | 创建路线 |
| PUT | `/api/routes/<id>` | 更新路线 |
| POST | `/api/routes/<id>/deactivate` | 停用路线 |
| POST | `/api/routes/<id>/activate` | 启用路线 |
| | | |
| **申请** | | |
| GET | `/api/applications` | 申请列表（支持搜索） |
| POST | `/api/applications` | 创建申请 |
| GET | `/api/applications/<appNo>` | 申请详情 |
| POST | `/api/applications/<appNo>/participants` | 添加参加者 |
| POST | `/api/applications/<appNo>/participants/import` | CSV批量导入参加者 |
| POST | `/api/applications/<appNo>/deposit` | 支付订金 |
| POST | `/api/applications/<appNo>/balance` | 支付余款 |
| POST | `/api/applications/<appNo>/complete` | 完成申请 |
| POST | `/api/applications/<appNo>/cancel` | 取消申请 |
| | | |
| **参加者** | | |
| PUT | `/api/participants/<id>` | 更新参加者 |
| POST | `/api/participants/<id>/cancel` | 取消参加者 |
| | | |
| **财务与统计** | | |
| GET | `/api/daily_export` | 昨日财务导出 |
| GET | `/api/confirmations` | 昨日确认书列表 |
| GET | `/api/stats` | 统计数据（Dashboard用） |
| | | |
| **审计** | | |
| GET | `/api/audit_logs` | 操作日志（支持分页+筛选） |

## 数据模型

系统包含以下 9 个数据库表：

| 表名 | 说明 |
|------|------|
| `users` | 用户账户（密码哈希存储） |
| `routes` | 旅游路线 |
| `route_history` | 路线版本历史 |
| `tour_groups` | 旅游团 |
| `price_history` | 价格变更历史 |
| `applications` | 申请单 |
| `participants` | 参加者信息 |
| `payment_records` | 支付记录 |
| `audit_logs` | 操作审计日志 |
| `system_config` | 系统配置项 |

## 代码规范

项目配置了代码规范工具：
- 前端：`.eslintrc.js` — ESLint + Vue 3 推荐规则
- 后端：`.flake8` — Flake8 规则 (line length=120)
