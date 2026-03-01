# 使用 Python 3.12 官方镜像（与项目 requirements 兼容）
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（按需取消注释，例如 PostgreSQL 客户端、构建依赖）
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖（使用国内镜像可加速，按需取消下一行注释）
# RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码（.dockerignore 会排除不需要的文件）
COPY config ./config
COPY src ./src

# 应用以 HTTP 模式运行，工作目录需为 src 以便加载 main 模块
WORKDIR /app/src

# 暴露端口（与下方 CMD 默认端口一致，可通过 -p 覆盖）
ENV PORT=8000
EXPOSE ${PORT}

# 启动 HTTP 服务；宿主机可通过 -e PORT=xxx 覆盖端口
CMD ["sh", "-c", "python main.py -m http -p ${PORT}"]
