#!/bin/bash
# Synapse 一键部署脚本

set -e

echo "=== Synapse 智枢部署脚本 ==="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "安装 Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 创建配置目录
mkdir -p /opt/synapse/{config,data,logs}

# 复制配置文件
cp config/*.yaml /opt/synapse/config/

# 构建镜像
echo "构建 Docker 镜像..."
docker-compose build

# 启动服务
echo "启动服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查健康状态
echo "检查服务状态..."
curl -f http://localhost:8000/health || echo "服务启动中..."

echo ""
echo "=== 部署完成 ==="
echo "API 地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
