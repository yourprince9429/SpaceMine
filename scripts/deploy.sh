#!/bin/bash

set -e

echo "========================================="
echo "  SpaceMine 一键部署脚本"
echo "========================================="

# 检查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "⚠️  .env 文件不存在，从 .env.example 复制..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件"
    echo "⚠️  请修改 .env 文件中的 SECRET_KEY 后重新运行"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 加载本地 Docker 镜像（用于离线部署）
echo ""
echo "📦 1. 加载本地 Docker 镜像..."
if [ -d "images" ]; then
    echo "检测到本地镜像目录，开始加载镜像..."
    
    # 加载 MySQL 镜像
    if [ -f "images/mysql_8_0.tar" ]; then
        echo "加载 MySQL 镜像 (8.0)..."
        docker load -i "images/mysql_8_0.tar" 2>/dev/null || echo "⚠️ MySQL 镜像加载失败，将尝试从网络拉取"
        echo "✅ MySQL 镜像加载完成"
    else
        echo "⚠️ MySQL 镜像文件不存在，将尝试从网络拉取"
    fi
    
    # 加载服务镜像
    if [ -f "images/spacemine_service.tar" ]; then
        echo "加载服务镜像..."
        docker load -i "images/spacemine_service.tar" 2>/dev/null || echo "⚠️ 服务镜像加载失败，将尝试从网络拉取"
        echo "✅ 服务镜像加载完成"
    else
        echo "⚠️ 服务镜像文件不存在，将尝试从网络拉取"
    fi
else
    echo "⚠️ 本地镜像目录不存在，将尝试从网络拉取镜像"
fi


echo ""
echo "🚀 2. 启动服务..."
docker-compose up -d

echo ""
echo "⏳ 3. 等待 MySQL 服务就绪..."
source .env
for i in {1..30}; do
    if docker-compose exec -T mysql mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD} > /dev/null 2>&1; then
        echo "✅ MySQL 服务已就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ MySQL 服务启动超时"
        exit 1
    fi
    echo "   等待中... ($i/30)"
    sleep 2
done

echo ""
echo "🗄️  4. 运行数据库迁移..."
docker-compose exec -T web flask db upgrade
echo "✅ 数据库迁移完成"

echo ""
echo "👥 5. 初始化角色..."
docker-compose exec -T web python data/init_roles.pyc

echo ""
echo "👤 6. 初始化管理员用户..."
docker-compose exec -T web python data/init_admin_user.pyc

echo ""
echo "⚙️  7. 初始化配置..."
docker-compose exec -T web python data/init_config.pyc

echo ""
echo "⛏️  8. 初始化挖矿规则..."
docker-compose exec -T web python data/init_mining_rules.pyc

echo ""
echo "========================================="
echo "✅ SpaceMine 部署成功！"
echo "========================================="
echo ""
echo "📊 访问地址:"
echo "   - Web服务: http://localhost:${WEB_PORT:-5001}"
echo "   - MySQL:   localhost:${MYSQL_PORT:-3306}"
echo ""
echo "📝 查看日志:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 停止服务:"
echo "   ./stop.sh"
echo ""
echo "🔄 重启服务:"
echo "   ./restart.sh"
echo ""
