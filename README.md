# Login Portal

TCP Forward Panel 前置登录网关。

## 架构

```
用户 → Login Portal（端口 8081）
          ↓ 登录认证
       反向代理 → TCP Forward Panel（端口 8080）
```

## 一键部署

```bash
bash <(curl -sL https://raw.githubusercontent.com/kuknion2669-sketch/login-portal/main/install.sh)
```

## 功能

- 登录认证（Session 加密）
- 反向代理到后端面板
- 设置页：改端口、账号密码、后端面板地址
- 配置存 SQLite

## 默认账号

- 账号：`admin`
- 密码：`admin123`
