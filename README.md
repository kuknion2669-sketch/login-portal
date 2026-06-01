# Login Portal

TCP Forward Panel 前置登录网关。

## 架构

```
用户 → Login Portal（端口 8081，需登录）
          ↓ 认证后反向代理
       后端管理面板（端口 8080，无需登录）
```

## 一键部署

```bash
bash <(curl -sL https://raw.githubusercontent.com/kuknion2669-sketch/login-portal/main/install.sh)
```

## 手动部署

```bash
# 安装依赖
pip3 install flask

# 下载代码
curl -sL -o /root/login_portal.py \
  https://raw.githubusercontent.com/kuknion2669-sketch/login-portal/main/login_portal.py

# 运行
python3 /root/login_portal.py
```

## 功能

- **登录认证** - Session 加密，默认 admin / admin123
- **反向代理** - 登录后所有请求转发到后端面板
- **设置页** - 修改端口、账号密码、后端面板地址

## 文件结构

```
login-portal/
├── login_portal.py    # 主程序
├── install.sh         # 一键安装脚本
└── README.md          # 说明文档
```

## 默认账号

| 项目 | 值 |
|------|-----|
| 端口 | 8081 |
| 账号 | admin |
| 密码 | admin123 |
| 面板地址 | http://127.0.0.1:8080 |

## 前后端关系

1. 先部署 **Login Portal**（对外暴露 8081）
2. 再部署 **TCP Forward Panel**（对内 8080）
3. 用户访问 8081 → 登录 → 代理到 8080 → 管理面板

Panel 本身不需要登录认证，由 Login Portal 统一管理。
