# SpaceMine - 挖矿管理系统

## 项目概述

这是一个基于Flask的挖矿管理系统，使用Python后端和JavaScript前端。项目完全参考网站 https://ccyzz.com/ui/ ，页面结构及内容与该网站完全一致。

## 技术栈

- **后端**: Flask 2.3.3, SQLAlchemy, Flask-Bcrypt, Flask-Migrate
- **前端**: 原生JavaScript, HTML5, CSS3
- **数据库**: MySQL (通过PyMySQL)
- **任务调度**: APScheduler
- **其他**: QRCode, Pandas, OpenPyXL

## 项目结构

```
SpaceMine/
├── app.py                    # 主应用程序文件
├── config.py                 # 配置文件
├── README.md                 # 项目README文档
├── requirements.txt          # Python依赖文件
├── requirements-prod.txt     # 生产环境依赖文件
├── scripts/                  # 脚本目录
│   ├── run.sh                # 本地运行脚本
│   ├── start.sh              # Docker启动脚本
│   ├── stop.sh               # Docker停止脚本
│   ├── restart.sh            # Docker重启脚本
│   ├── encode_js.py          # JS文件编码脚本
│   ├── build_package.sh      # 构建包脚本
│   └── deploy.sh             # 部署脚本
├── data/                     # 初始化数据目录
│   ├── create_admin.py       # 创建管理员脚本
│   ├── init_admin_user.py    # 初始化管理员用户脚本
│   ├── init_config.py        # 初始化配置脚本
│   ├── init_mining_rules.py  # 挖掘规则初始化脚本
│   ├── init_roles.py         # 初始化角色脚本
│   └── update_config_descriptions.py  # 更新配置描述脚本
├── docs/                     # 文档目录
│   ├── 信用卡充值模块.md       # 信用卡充值模块需求文档
│   ├── 充值记录模块.md         # 充值记录模块需求文档
│   ├── 提现审核模块.md         # 提现审核模块需求文档
│   ├── 用户管理模块.md         # 用户管理模块需求文档
│   ├── 管理员模块.md           # 管理员模块需求文档
│   ├── 能量提现模块.md         # 能量提现模块需求文档
│   ├── 部署指南-小白版.md       # 部署指南
│   └── 项目说明.md            # 项目说明文档
├── handlers/                 # 处理程序目录
│   ├── __init__.py
│   ├── auth.py                # 用户认证处理
│   ├── balance.py             # 用户余额处理
│   ├── invite.py              # 邀请系统处理
│   ├── messages.py            # 消息处理
│   ├── mine.py                # 挖矿处理
│   ├── notice.py              # 通知处理
│   ├── recharge.py            # 充值处理
│   ├── scheduler.py           # 任务调度处理
│   ├── security.py            # 安全处理
│   ├── support.py             # 客服支持处理
│   └── withdraw.py            # 提现处理
├── migrations/               # 数据库迁移目录
│   ├── versions/              # 迁移版本文件
│   ├── README
│   ├── alembic.ini
│   ├── env.py
│   └── script.py.mako
├── models/                   # 数据模型目录
│   ├── __init__.py
│   ├── config.py             # 配置模型
│   ├── credit_card.py        # 信用卡模型
│   ├── credit_card_generation_record.py  # 信用卡生成记录模型
│   ├── file.py               # 文件模型
│   ├── mine_user_relation.py # 挖矿用户关系模型
│   ├── mining_rule.py        # 挖矿规则模型
│   ├── notice.py             # 通知模型
│   ├── notification.py       # 消息通知模型
│   ├── recharge.py           # 充值模型
│   ├── user.py               # 用户模型
│   └── withdrawal.py         # 提现模型
├── routes/                   # 路由目录
│   ├── __init__.py
│   ├── admin/                # 管理员路由
│   │   ├── __init__.py
│   │   ├── configs.py
│   │   ├── credit_cards.py
│   │   ├── notices.py
│   │   ├── recharges.py
│   │   ├── support.py
│   │   ├── users.py
│   │   └── withdrawals.py
│   ├── auth.py               # 认证路由
│   ├── dashboard.py          # 仪表板路由
│   ├── encoded_js.py         # 编码JS路由
│   ├── invite.py             # 邀请路由
│   ├── message.py            # 消息路由
│   ├── notice.py             # 通知路由
│   ├── recharge.py           # 充值路由
│   ├── ui.py                 # UI路由
│   ├── user.py               # 用户路由
│   └── withdraw.py           # 提现路由
├── static/                   # 静态文件目录
│   ├── css/                  # CSS样式文件
│   │   ├── admin.css
│   │   ├── auth.css
│   │   ├── back-button.css
│   │   ├── home.css
│   │   ├── intro.css
│   │   ├── invite.css
│   │   ├── messages.css
│   │   ├── notices.css
│   │   ├── recharge.css
│   │   ├── recharge_card.css
│   │   ├── recharge_history.css
│   │   ├── recharge_usdt.css
│   │   ├── security.css
│   │   ├── style.css
│   │   └── withdraw.css
│   ├── js/                   # JavaScript文件
│   │   ├── account_security.page.js
│   │   ├── admin.js
│   │   ├── back-button.js
│   │   ├── dashboard.js
│   │   ├── invite.js
│   │   ├── js-loader.js
│   │   ├── login.js
│   │   ├── messages.js
│   │   ├── notices.js
│   │   ├── recharge.js
│   │   ├── recharge_card.js
│   │   ├── recharge_history.js
│   │   ├── recharge_usdt.js
│   │   ├── register.js
│   │   ├── ui.js
│   │   └── withdraw.page.js
│   └── img/                  # 图片文件
├── templates/                # HTML模板目录
│   ├── admin.html
│   ├── base.html
│   ├── dashboard.html
│   ├── intro.html
│   ├── invite.html
│   ├── login.html
│   ├── messages.html
│   ├── notices.html
│   ├── recharge.html
│   ├── recharge_card.html
│   ├── recharge_history.html
│   ├── recharge_usdt.html
│   ├── register.html
│   ├── security.html
│   └── withdraw.html
├── tests/                    # 测试文件
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_mine_handlers.py
│   ├── test_recharge_handlers.py
│   ├── test_user_handlers.py
│   └── test_user_routes.py
├── .dockerignore             # Docker忽略文件
├── .env.example              # 环境变量示例文件
├── .gitignore                # Git忽略文件
├── Dockerfile                # Docker构建文件
├── docker-compose.yml        # Docker Compose配置文件
└── gunicorn_config.py        # Gunicorn配置文件
```

## 主要功能模块

- **用户管理模块**: 用户注册、登录、个人信息管理
- **信用卡充值模块**: 信用卡绑定和充值功能
- **充值记录模块**: 查看充值历史记录
- **管理员模块**: 系统设置和用户管理
- **能量提现模块**: 挖矿能量提现功能

## 数据库管理

- 使用Alembic进行数据库迁移管理
- 禁止自行建表，必须统一使用alembic进行数据库表管理

## 运行项目

### Docker方式（推荐）
```bash
# 一键启动（包含初始化）
./scripts/start.sh

# 重启服务
./scripts/restart.sh

# 停止服务
./scripts/stop.sh
```

### 本地开发方式
```bash
# 安装依赖
pip install -r requirements.txt

# 运行项目
./scripts/run.sh
```

## 开发规范

- **Python**: 遵循PEP 8规范
- **JavaScript**: 使用现代ES6+语法
- **HTML/CSS**: 使用语义化标签，响应式设计
- **数据库操作**: 使用SQLAlchemy ORM

## 安全要求

- 密码使用Flask-Bcrypt加密
- 敏感操作需要身份验证
- 防止SQL注入和XSS攻击
