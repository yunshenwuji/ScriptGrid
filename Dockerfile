# 述格 (ScriptGrid) Web 应用

# 使用官方 Python 3.13 slim 基础镜像
FROM python:3.13-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai

# 安装系统依赖和清理缓存
RUN apt-get update && apt-get install -y \
    # OpenCV 所需的系统库（Debian Trixie 兼容版本）
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    # 额外的多媒体库支持
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制项目代码（.dockerignore会自动排除不需要的文件）
COPY . .

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/supported-languages', timeout=5)"

# 启动命令
# 使用 uvicorn 启动 FastAPI 应用
# --host 0.0.0.0 使得应用可以在 Docker 容器外被访问
# --port 8000 指定监听端口
# app:app 指的是 app.py 文件中的 FastAPI 实例 app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]