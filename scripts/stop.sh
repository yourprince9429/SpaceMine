#!/bin/bash

set -e

echo "========================================="
echo "  SpaceMine 停止脚本"
echo "========================================="

echo ""
echo "🛑 停止所有服务..."
docker-compose down

echo ""
echo "✅ 所有服务已停止"
echo ""
echo "💾 如需删除数据卷（清空数据库），请运行:"
echo "   docker-compose down -v"
echo ""
