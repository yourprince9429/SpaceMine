# 第一阶段：构建阶段
FROM python:3.9-slim AS builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖（使用阿里云镜像源）
RUN echo 'deb http://mirrors.aliyun.com/debian/ bullseye main non-free contrib' > /etc/apt/sources.list && \
    echo 'deb http://mirrors.aliyun.com/debian-security/ bullseye-security main' >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libc-dev zlib1g-dev libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制所有必要的文件
COPY app.py .
COPY config.py .
COPY gunicorn_config.py .
COPY handlers/ ./handlers/
COPY models/ ./models/
COPY routes/ ./routes/
COPY templates/ ./templates/
COPY static/ ./static/
COPY migrations/ ./migrations/
COPY data/ ./data/
COPY requirements-prod.txt .

# 安装依赖（使用国内镜像源加速）
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir=/app/wheels -i https://mirrors.aliyun.com/pypi/simple/ -r requirements-prod.txt

# 删除 macOS 生成的隐藏文件（包含 null 字节，会导致编译失败）
RUN find . -name "._*" -type f -delete && \
    # 编译 Python 文件为 pyc
    python -m compileall -b .

# 保留必要的 Python 文件用于迁移
RUN find . -name "*.py" -type f ! -name "gunicorn_config.py" ! -path "./migrations/*" -delete

# 第二阶段：运行阶段
FROM python:3.9-slim AS runner

# 设置工作目录
WORKDIR /app

# 安装运行时依赖（使用阿里云镜像源）
RUN echo 'deb http://mirrors.aliyun.com/debian/ bullseye main non-free contrib' > /etc/apt/sources.list && \
    echo 'deb http://mirrors.aliyun.com/debian-security/ bullseye-security main' >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo zlib1g \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖并安装（使用国内镜像源加速）
RUN --mount=type=bind,from=builder,source=/app/wheels,target=/wheels \
    pip install --no-cache -i https://mirrors.aliyun.com/pypi/simple/ /wheels/*

# 复制必要的运行时文件
COPY --from=builder /app/app.pyc .
COPY --from=builder /app/config.pyc .
COPY --from=builder /app/gunicorn_config.py .

# 只复制运行时必需的代码文件
COPY --from=builder /app/handlers ./handlers/
COPY --from=builder /app/models ./models/
COPY --from=builder /app/routes ./routes/
COPY --from=builder /app/templates ./templates/
COPY --from=builder /app/static ./static/
COPY --from=builder /app/migrations ./migrations/
COPY --from=builder /app/data ./data/

# 设置环境变量
ENV FLASK_ENV=production
ENV FLASK_APP=app

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]