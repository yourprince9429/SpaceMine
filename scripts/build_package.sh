#!/bin/bash

set -e

echo "========================================"
echo "SpaceMine 一键部署包脚本"
echo "========================================"

# 移除架构相关配置

# 设置变量
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"
PACKAGE_NAME="SpaceMine_${TIMESTAMP}"

cd "$PROJECT_DIR"

echo "当前工作目录: $(pwd)"
echo "包名: $PACKAGE_NAME"
echo ""

# 检查必要文件是否存在
if [ ! -f "docker-compose.yml" ]; then
    echo "错误: docker-compose.yml 文件不存在"
    exit 1
fi

if [ ! -f ".env.example" ]; then
    echo "错误: .env.example 文件不存在"
    exit 1
fi

# 创建临时目录
echo "1. 创建部署包..."
TMP_DIR="/tmp/${PACKAGE_NAME}"
mkdir -p "$TMP_DIR"
mkdir -p "$TMP_DIR/images"

# 下载并保存 Docker 镜像（用于离线部署）
echo "下载 Docker 镜像（用于离线部署）..."

# 构建服务镜像
echo "构建服务镜像..."
SERVICE_IMAGE="spacemine:latest"
echo "使用 Dockerfile 构建服务镜像: $SERVICE_IMAGE"

# 构建服务镜像
docker build -t "$SERVICE_IMAGE" .

# 保存服务镜像
echo "保存服务镜像..."
docker save -o "$TMP_DIR/images/spacemine_service.tar" "$SERVICE_IMAGE"

# 下载 MySQL 镜像
MYSQL_VERSION="8.0"
MYSQL_IMAGE="mysql:$MYSQL_VERSION"
MYSQL_TAR_NAME="mysql_${MYSQL_VERSION//./_}.tar"

echo "下载 MySQL 镜像: $MYSQL_IMAGE"
docker pull "$MYSQL_IMAGE"

# 保存 MySQL 镜像
echo "保存 MySQL 镜像..."
docker save -o "$TMP_DIR/images/$MYSQL_TAR_NAME" "$MYSQL_IMAGE"

cd "$PROJECT_DIR"
echo "✅ Docker 镜像下载和保存完成"

# 复制必要文件
echo "复制配置文件..."
cp -r "docker-compose.yml" "$TMP_DIR/docker-compose.yml"
cp -r ".env.example" "$TMP_DIR/.env"
cp -r "scripts/deploy.sh" "$TMP_DIR/"
cp -r "scripts/stop.sh" "$TMP_DIR/"
cp -r "scripts/restart.sh" "$TMP_DIR/"

# 生成部署说明文件
echo "生成部署说明..."
cat > "$TMP_DIR/README.md" << 'EOF'
# SpaceMine 部署说明

## 架构
- 构建时间: $(date)

## 部署步骤

1. **配置环境变量**
   编辑 `.env` 文件，设置数据库连接等参数

2. **启动服务**
   ```bash
   ./start.sh
   ```

3. **停止服务**
   ```bash
   ./stop.sh
   ```

4. **重启服务**
   ```bash
   ./restart.sh
   ```

## 离线部署说明

此部署包为**离线部署包**，包含以下特点：

- ✅ 包含完整的项目文件和依赖
- ✅ 包含离线所需的Docker镜像（MySQL和服务镜像）
- ✅ 无需网络连接即可完成部署
- ✅ 支持在隔离网络环境中使用

### 离线部署步骤

1. **将部署包复制到目标服务器**
   ```bash
   # 示例：使用scp复制到目标服务器
   scp SpaceMine_*.tar.gz user@server:/path/to/destination
   ```

2. **在目标服务器上解压部署包**
   ```bash
   tar -xzf SpaceMine_*.tar.gz
   cd SpaceMine_*
   ```

3. **配置环境变量**
   编辑 `.env` 文件，设置数据库连接等参数

4. **启动服务**
   ```bash
   ./start.sh
   ```
   脚本会自动加载本地Docker镜像，无需网络连接

## 注意事项
- 确保目标服务器已安装Docker和Docker Compose
- 确保端口5001未被占用
- 首次启动时会自动创建数据库表结构
- 此部署包包含完整的项目文件和离线所需的Docker镜像（MySQL和服务镜像），支持在无网络环境中直接部署和运行
- 离线环境下请确保Docker已正确安装且运行
EOF

# 替换README.md中的变量
date_str=$(date)
# 兼容macOS和Linux的sed语法
if [[ "$(uname)" == "Darwin" ]]; then
    # macOS需要空的备份文件扩展名参数
    sed -i '' "s/\$(date)/$date_str/g" "$TMP_DIR/README.md"
else
    # Linux直接使用
    sed -i "s/\$(date)/$date_str/g" "$TMP_DIR/README.md"
fi

# 打包
echo "2. 打包文件..."
cd "/tmp"
tar -czf "${PACKAGE_NAME}.tar.gz" "${PACKAGE_NAME}"

echo ""
echo "========================================"
echo "部署包生成完成!"
echo "文件路径: /tmp/${PACKAGE_NAME}.tar.gz"
echo "========================================"
echo ""
echo "使用说明:"
echo "1. 将部署包复制到目标服务器"
echo "2. 解压: tar -xzf ${PACKAGE_NAME}.tar.gz"
echo "3. 进入目录: cd ${PACKAGE_NAME}"
echo "4. 配置.env文件"
echo "5. 启动服务: ./start.sh"
echo ""
echo "提示: 此部署包包含离线所需的Docker镜像（MySQL和服务镜像），无需网络连接即可部署"
echo ""

# 清理临时目录
rm -rf "$TMP_DIR"
echo "✅ 临时文件清理完成"
echo ""
echo "========================================"
echo "脚本执行完成!"
echo "======================================="