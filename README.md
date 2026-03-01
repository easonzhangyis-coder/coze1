# 项目结构说明

# 本地运行

## 0. 安装 Python 和 pip（尚未安装时）

本项目需要 **Python 3.10 或更高版本**。pip 会随 Python 一起安装。

### Windows 安装步骤

1. **下载 Python（请下载 Windows 安装包，不要下源码包）**
   - 打开 [Python 官网下载页](https://www.python.org/downloads/)
   - 点击页面上的 **“Download Python 3.x.x”** 按钮，会下载到 **`.exe`** 安装程序（例如 `python-3.12.10-amd64.exe`）。
   - **不要下载** 扩展名为 **`.tar.xz`** 或 **`.tgz`** 的文件——那是 Linux 源码包，在 Windows 上无法直接安装。若你看到的是 `Python-3.12.12.tar.xz`，说明当前 3.12.12 只提供源码，Windows 可改用 **3.12.10**（[直接下载 3.12.10 Windows 64 位](https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe)）或官网首页的最新版（如 3.14.x）。

2. **运行安装程序**
   - 双击下载的 **`.exe`**
   - **务必勾选** “**Add python.exe to PATH**”（把 Python 加到系统路径）
   - 可选：选择 “Install for all users”
   - 点击 “Install Now” 完成安装

3. **验证安装**
   - 重新打开一个 **PowerShell** 或 **命令提示符** 窗口
   - 执行：
   ```powershell
   python --version
   pip --version
   ```
   - 若能看到版本号（如 `Python 3.12.x`、`pip 24.x`），说明安装成功

若 `python` 或 `pip` 提示“不是内部或外部命令”，说明未加入 PATH，可重新运行安装程序并勾选 “Add python.exe to PATH”，或手动将 Python 安装目录（如 `C:\Users\你的用户名\AppData\Local\Programs\Python\Python312`）和其 `Scripts` 子目录加入系统环境变量 PATH。

## 1. 环境要求

- **Python 3.10+**（及随附的 pip）
- （可选）Git Bash 或 WSL，用于直接执行 `.sh` 脚本；在 Windows 下也可用下面提供的 PowerShell 命令

## 2. 安装依赖

在项目根目录执行：

```bash```

## 3. 运行方式

### 方式一：使用脚本（Git Bash / WSL / Linux）

```bash
# 运行流程
bash scripts/local_run.sh -m flow

# 带输入运行流程
bash scripts/local_run.sh -m flow -i '{"text": "你好"}'

# 运行单个节点（需替换 node_name 为实际节点 ID）
bash scripts/local_run.sh -m node -n node_name

# 启动 HTTP 服务（默认端口 8000，可用 -p 指定）
bash scripts/http_run.sh -p 5000
```

### 方式二：直接用 Python（Windows PowerShell / CMD 通用）

在项目根目录下执行（确保当前目录为项目根目录，以便 `src` 被正确识别）：

```powershell
# 运行流程
python src/main.py -m flow

# 运行单个节点
python src/main.py -m node -n node_name

# 启动 HTTP 服务，端口 5000
python src/main.py -m http -p 5000
```

启动 HTTP 服务后，在浏览器访问 `http://localhost:5000`（或你指定的端口）即可。

## 4. 运行模式说明

| 模式 | 说明 |
|------|------|
| `flow` | 运行完整工作流 |
| `node` | 运行指定节点，需配合 `-n 节点ID` |
| `http` | 启动 FastAPI HTTP 服务，可用 `-p 端口` 指定端口 |
| `agent` | Agent 模式（见脚本帮助） |

更多参数可查看帮助：`bash scripts/local_run.sh -h`

