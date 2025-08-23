# 述格 (ScriptGrid) Web 应用

FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码（.dockerignore会自动排除不需要的文件）
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
# 使用 uvicorn 启动 FastAPI 应用
# --host 0.0.0.0 使得应用可以在 Docker 容器外被访问
# --port 8000 指定监听端口
# app:app 指的是 app.py 文件中的 FastAPI 实例 app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]       