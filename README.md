# chromark-mcp

一个用于读取、搜索本机 Chrome 书签的 MCP 服务器，同时提供简单的命令行工具。

## 功能

- 自动定位当前用户的 Chrome 书签文件（支持 Windows / macOS / Linux 常见路径）
- MCP 工具：
	- `get_bookmarks(limit=20)`：获取最新书签列表
	- `search_bookmarks(query, limit=10)`：按标题 / URL / 文件夹关键字搜索
- MCP 资源：
	- `chrome://bookmarks`：以 JSON 形式返回部分书签数据
- 命令行模式：
	- 列出前 N 条书签
	- 关键字搜索书签

## 环境要求

- Python `>= 3.14`
- 操作系统：Windows / macOS / Linux
- 已安装 Google Chrome，并存在默认用户配置目录（`Default/Bookmarks`）
- 使用 [uv](https://github.com/astral-sh/uv) 进行虚拟环境和依赖管理

## 安装 uv

可以任选一种方式安装 uv：

1. 官方一键安装脚本（推荐，需具备基础网络访问能力）：

```bash
# Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. 通过 `pipx` 安装（如果你更习惯 Python 工具链）：

```bash
pipx install uv
```

安装完成后，确认版本：

```bash
uv --version
```

## 使用 uv 创建虚拟环境并安装依赖

在项目根目录下执行：

```bash
# 创建并激活虚拟环境（uv 会自动管理）
uv venv

# 安装项目依赖（读取 pyproject.toml）
uv sync
```

如果你只是想快速安装运行所需依赖，也可以：

```bash
uv pip install -e .
```

当前最核心依赖可参考 [pyproject.toml](pyproject.toml)：

- `mcp>=1.26.0`

## 作为 MCP 服务器使用

`chrome_bookmarks_mcp.py` 使用 `mcp.server.fastmcp.FastMCP` 实现了一个标准 MCP 服务器，默认通过 `stdio` 运行。

启动方式（一般由 MCP 客户端调用）：

```bash
python chrome_bookmarks_mcp.py --serve
```

在你的 MCP 客户端（例如支持 MCP 协议的聊天工具）中，将该脚本配置为一个基于 `stdio` 的服务器即可使用：

- 服务器命令：`python`
- 参数示例：`["chrome_bookmarks_mcp.py", "--serve"]`

工具与资源：

- 工具 `get_bookmarks(limit: int = 20) -> list`
	- 用于获取最多 `limit` 条书签，返回为字符串列表，适合直接展示。
- 工具 `search_bookmarks(query: str, limit: int = 10) -> list`
	- 根据关键字在标题、URL、文件夹路径中搜索。
- 资源 `chrome://bookmarks`
	- 返回 JSON 字符串，内容为部分书签的精简信息，可用于自定义处理或前端展示。

## 命令行使用

脚本本身也可以独立作为命令行工具使用：

```bash
python chrome_bookmarks_mcp.py --list --limit 20
```

常用参数：

- `--list`：以列表形式打印书签后退出
- `--search, -q <关键词>`：搜索书签
- `--limit <N>`：限制返回条数（默认 20）
- `--serve`：强制以 MCP 服务器模式运行（通过 stdio）

示例：

```bash
# 列出前 50 条书签
python chrome_bookmarks_mcp.py --list --limit 50

# 搜索标题或 URL 中包含 "dify" 的书签
python chrome_bookmarks_mcp.py --search dify --limit 10
```

## 示例数据

仓库中包含一个示例书签导出文件：

- [chrome_bookmarks_sorted.html](chrome_bookmarks_sorted.html)

该文件是从 Chrome 导出的 HTML 书签，主要用于手动查看和测试，不参与 MCP 服务运行逻辑。

## 开发与维护

- 项目入口：
	- MCP 服务器与 CLI 均在 [chrome_bookmarks_mcp.py](chrome_bookmarks_mcp.py) 中实现
- 依赖管理：
	- 使用 [pyproject.toml](pyproject.toml) 维护依赖
- 可以根据需要扩展：
	- 支持多 profile / 多浏览器
	- 增强搜索逻辑（模糊匹配、拼音匹配等）
	- 输出为 HTML / Markdown 等格式

欢迎根据个人使用习惯自由修改和扩展。
