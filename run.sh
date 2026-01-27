#!/bin/bash
# 激活虚拟环境并启动Flask应用
source .venv/bin/activate

# 确保依赖已安装
echo "正在检查并安装依赖..."
pip install -r requirements.txt

# 设置环境变量
export FLASK_ENV=development
export FLASK_DEBUG=0

echo "启动Flask应用..."
python app.py
