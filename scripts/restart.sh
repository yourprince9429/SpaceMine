#!/bin/bash

echo "========================================="
echo "  SpaceMine 重启脚本"
echo "========================================="

echo ""
echo "🛑 停止服务..."
docker-compose down

echo ""
echo "🚀 重新启动服务..."
docker-compose up -d

echo ""
echo "⏳ 等待服务就绪..."
sleep 5

echo ""
echo "✅ 服务已重启"
echo ""
echo "📊 访问地址: http://localhost:5001"
echo "📝 查看日志: docker-compose logs -f"
echo ""
