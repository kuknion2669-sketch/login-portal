#!/bin/bash
# Login Portal - 一键安装脚本
set -e

# 检测系统
if [ -f /etc/debian_version ]; then
    OS="debian"
elif [ -f /etc/redhat-release ]; then
    OS="centos"
else
    echo -e "\033[31m不支持的系统\033[0m"
    exit 1
fi

echo -e "\033[36m=== Login Portal 安装 ===\033[0m"

# 安装依赖
if [ "$OS" = "debian" ]; then
    DEBIAN_FRONTEND=noninteractive apt-get update -qq
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3-pip curl netcat-openbsd 2>/dev/null
    pip3 install flask --quiet 2>/dev/null
elif [ "$OS" = "centos" ]; then
    yum install -y -q epel-release 2>/dev/null || true
    yum install -y -q python3 python3-pip curl nmap-ncat 2>/dev/null
    pip3 install flask --quiet 2>/dev/null
fi

# 下载代码
cd /root
curl -sL -o /root/login_portal.py \
    https://raw.githubusercontent.com/kuknion2669-sketch/login-portal/main/login_portal.py

# 创建 systemd 服务
cat > /usr/lib/systemd/system/login-portal.service << 'EOF'
[Unit]
Description=Login Portal
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /root/login_portal.py
WorkingDirectory=/root
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable login-portal
systemctl restart login-portal

echo -e "\033[32m=== 安装完成 ===\033[0m"
IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "服务器IP")
echo -e "访问: http://$IP:8081/"
echo -e "账号: admin"
echo -e "密码: admin123"
echo ""
echo -e "面板地址默认 http://127.0.0.1:8080，可在设置页修改"
