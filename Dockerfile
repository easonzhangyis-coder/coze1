# 使用 Python 3.12 官方镜像（与项目 requirements 兼容）
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖：部分包（如 cryptography、psycopg、opencv、dbus-python）需编译或系统库
# - gcc / g++: 编译 C 扩展
# - libpq-dev: PostgreSQL 客户端开发库
# - pkg-config, libdbus-1-dev, libglib2.0-dev: 构建 dbus-python 所需
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libpq-dev pkg-config libdbus-1-dev libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 升级 pip/setuptools，减少元数据与构建错误；使用国内镜像加速并提高成功率
RUN pip install --no-cache-dir -U pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

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
