# 云服务器部署说明

本文档说明如何将本项目通过 Docker 部署到云服务器，并提供常见运维命令。

---

## 〇、本地先构建并运行（Windows / 本机）

在部署到云服务器前，可先在本地构建镜像并运行容器，确认无误后再上传部署。

**前提**：本机已安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)，并已**启动**（托盘图标显示 Docker 正在运行）。

在**项目根目录**打开 PowerShell 或终端，依次执行：

```powershell
# 1. 进入项目目录（若尚未在此目录）
cd "f:\代码\projects"

# 2. 构建镜像（首次或代码/依赖变更后执行，耗时可能几分钟）
docker build -t projects-app:latest .

# 3. 运行容器（后台运行，宿主机 8000 映射到容器 8000）
docker run -d --name projects-http -p 8000:8000 -e COZE_PROJECT_ENV=PROD projects-app:latest
```

或使用 **Docker Compose**（需先复制 `.env.example` 为 `.env`，可选修改）：

```powershell
cd "f:\代码\projects"
docker compose build
docker compose up -d
```

**验证**：浏览器打开 **http://localhost:8000/docs**，能看到 API 文档即表示成功。

**常用命令**：

```powershell
# 查看容器是否在运行
docker ps

# 查看最近日志
docker logs -f --tail 100 projects-http

# 停止并删除容器（之后可用上面 docker run 或 compose 再次启动）
docker stop projects-http
docker rm projects-http
```

若提示 `failed to connect to the docker API`，请先**启动 Docker Desktop** 再执行上述命令。

---

## 一、前置要求

### 1. 服务器环境

- **操作系统**：Linux（如 **OpenCloudOS**、Ubuntu 20.04+、CentOS 7+）
- **Docker**：已安装 Docker Engine（建议 20.10+）
- **Docker Compose**（可选）：若使用 `docker-compose` 部署，需已安装 Compose V2

### 2. 安装 Docker（未安装时）

**OpenCloudOS（与 CentOS/RHEL 同源）：**

若从官方源下载时报错（如 `SSL connect error`、`Connection reset by peer`），请改用**国内镜像**安装。

**方式 A：阿里云镜像（推荐，避免官方源连接失败）**

```bash
# 若未安装 dnf 插件，先安装
sudo dnf install -y dnf-plugins-core

# 移除可能已添加的官方 Docker 源（若之前装过）
sudo rm -f /etc/yum.repos.d/docker-ce.repo

# 添加阿里云 Docker CE 镜像源（适配 CentOS 9 / OpenCloudOS 9）
sudo dnf config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

# 若仓库里默认仍是官方地址，可改为阿里云（el9 对应 OpenCloudOS 9）
sudo sed -i 's+download.docker.com+mirrors.aliyun.com/docker-ce+' /etc/yum.repos.d/docker-ce.repo

# 安装 Docker 及 Compose 插件
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 启动并设置开机自启
sudo systemctl enable --now docker
```

**方式 B：仅用系统自带的 Docker（不依赖外网镜像站）**

```bash
# 使用系统仓库中的 docker 或 moby（版本可能略旧，但可避免下载官方 RPM 失败）
sudo dnf install -y docker
# 或：sudo dnf install -y moby-engine moby-cli

# Compose 需单独安装（可选）
sudo dnf install -y docker-compose-plugin
# 若没有此包，可后续用 pip 安装：pip3 install docker-compose

sudo systemctl enable --now docker
```

**方式 C：官方源（网络可达时再用）**

```bash
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

安装后执行 `docker --version` 和 `docker compose version`（或 `docker compose version`）确认。

**Ubuntu / Debian：**

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

**CentOS / RHEL：**

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl start docker && sudo systemctl enable docker
```

安装后执行 `docker --version` 和 `docker compose version` 确认。

---

## 二、部署方式概览

| 方式 | 适用场景 | 说明 |
|------|----------|------|
| **docker run** | 单机、脚本化部署 | 直接构建镜像并运行容器 |
| **docker compose** | 单机、多环境变量 | 使用 `docker-compose.yml` + `.env` 管理配置 |

以下两种方式二选一即可。

---

## 三、方式一：使用 docker run 部署

### 1. 上传项目到服务器

将项目根目录（含 `Dockerfile`、`requirements.txt`、`config`、`src`）上传到服务器，例如：

- 使用 `scp`、`rsync`、Git 克隆等
- 示例目录：`/home/ubuntu/projects`

### 2. 构建镜像

在**项目根目录**执行：

```bash
cd /home/ubuntu/projects
docker build -t projects-app:latest .
```

国内服务器若 pip 较慢，可先修改 `Dockerfile`，取消注释 pip 国内镜像行后重新构建。

### 3. 配置环境变量（可选）

若需数据库、Coze API 等，可创建 `.env` 文件（参考 `.env.example`），或直接在 `docker run` 中用 `-e` 传入。示例仅启动 HTTP 服务可不配置。

### 4. 运行容器

```bash
# 默认映射宿主机 8000 -> 容器 8000
docker run -d \
  --name projects-http \
  -p 8000:8000 \
  -e COZE_PROJECT_ENV=PROD \
  -e PORT=8000 \
  --restart unless-stopped \
  projects-app:latest
```

如需挂载配置文件或日志目录：

```bash
docker run -d \
  --name projects-http \
  -p 8000:8000 \
  -e COZE_PROJECT_ENV=PROD \
  -e PORT=8000 \
  -v /home/ubuntu/projects/logs:/tmp/app/work/logs \
  --restart unless-stopped \
  projects-app:latest
```

### 5. 验证

- 浏览器访问：`http://<服务器公网IP>:8000/docs`
- 或：`curl http://localhost:8000/docs`

---

## 四、方式二：使用 Docker Compose 部署

### 1. 上传项目并准备 .env

确保项目根目录包含：

- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`
- `config/`、`src/`

复制环境变量示例并按需修改：

```bash
cp .env.example .env
# 编辑 .env，填写 PGDATABASE_URL、API Key 等（见 .env.example 内注释）
```

### 2. 构建并启动

```bash
cd /home/ubuntu/projects
docker compose build
docker compose up -d
```

### 3. 查看状态与日志

```bash
docker compose ps
docker compose logs -f app
```

### 4. 验证

访问 `http://<服务器公网IP>:8000/docs`。

---

## 五、环境变量说明

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `PORT` | 否 | 容器内 HTTP 端口，默认 8000，需与 Docker 映射一致 |
| `COZE_PROJECT_ENV` | 建议 | `PROD` 生产 / `DEV` 开发（开发可能开 reload） |
| `COZE_PROJECT_TYPE` | 否 | `workflow` 或 `agent`，与项目类型一致 |
| `LOG_LEVEL` | 否 | 日志级别，如 `INFO`、`DEBUG` |
| `PGDATABASE_URL` | 按需 | PostgreSQL 连接 URL，使用数据库/知识库时必填 |
| `COZE_BUCKET_ENDPOINT_URL` | 按需 | S3 兼容存储 endpoint |
| `COZE_BUCKET_NAME` | 按需 | S3 桶名 |
| `COZE_WORKLOAD_IDENTITY_API_KEY` | 按需 | Coze 集成 API Key（Agent 调模型等） |
| `COZE_INTEGRATION_MODEL_BASE_URL` | 按需 | 模型 API 基础 URL |
| `COZE_INTEGRATION_BASE_URL` | 按需 | 集成服务基础 URL |
| `COZE_LOOP_*`、`COZE_PROJECT_*` | 可选 | 追踪、空间等，见 `.env.example` |

未在表中列出的变量见项目内 `.env.example` 注释。

---

## 六、常用运维命令

### 容器管理（docker run 方式）

```bash
# 查看运行状态
docker ps | grep projects

# 查看日志（最近 200 行并持续输出）
docker logs -f --tail 200 projects-http

# 停止
docker stop projects-http

# 启动
docker start projects-http

# 删除容器（需先 stop）
docker rm -f projects-http
```

### Compose 方式

```bash
# 停止并删除容器
docker compose down

# 重新构建并启动
docker compose up -d --build

# 仅重启服务
docker compose restart app
```

### 更新应用

```bash
# 1. 拉取最新代码（若用 Git）
git pull

# 2. 重新构建镜像
docker build -t projects-app:latest .
# 或：docker compose build

# 3. 重启容器
docker rm -f projects-http && docker run -d ... # 同“运行容器”命令
# 或：docker compose up -d
```

---

## 七、端口与安全建议

1. **端口**：默认 8000，可通过 `-p 宿主机端口:8000` 或 compose 中 `ports` 修改。
2. **防火墙**：若对外提供访问，需在云控制台/安全组放行对应端口（如 8000）。
3. **反向代理**：生产环境建议在容器前加 Nginx/Caddy，做 HTTPS、限流与域名转发。
4. **敏感信息**：`PGDATABASE_URL`、API Key 等只放在 `.env` 或密钥管理系统中，不要提交到代码仓库。

---

## 八、故障排查

| 现象 | 可能原因 | 处理建议 |
|------|----------|----------|
| 无法访问 /docs | 端口未映射或防火墙未放行 | 检查 `docker run -p` 或 compose `ports`，以及云安全组 |
| 容器启动后退出 | 依赖缺失或环境变量错误 | `docker logs projects-http` 查看报错；核对 `.env` 与数据库连接 |
| 502 / 连接被拒 | 应用未监听 0.0.0.0 | 本项目已使用 `host="0.0.0.0"`，多为端口或代理配置问题 |
| 数据库连接失败 | PGDATABASE_URL 错误或网络不通 | 检查 URL、用户名密码、白名单；若 DB 在宿主机，注意使用宿主机 IP 或 `host.docker.internal`（部分环境） |

---

## 九、文件清单

部署相关文件：

- **Dockerfile**：构建运行 HTTP 服务的镜像
- **.dockerignore**：构建时排除无关文件，加快构建、减小镜像
- **docker-compose.yml**：Compose 编排示例
- **.env.example**：环境变量示例，复制为 `.env` 后按需修改
- **DEPLOY.md**：本部署说明文档

按上述步骤即可在云服务器上完成 Docker 化部署。若需接入 CI/CD，可在构建通过后执行 `docker build` 与 `docker run` 或 `docker compose up -d`。
