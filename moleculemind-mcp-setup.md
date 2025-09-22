# 在 Moleculemind 服务器上配置 Cursor MCP 工具的完整解决方案

## 背景
在 moleculemind 远程服务器上配置 Cursor 编辑器的 MCP (Model Context Protocol) 工具。该服务器与 IBEX 类似，用户没有 sudo 权限，需要在用户空间完成所有配置。

## 服务器信息
- **主机名**: moleculemind (UUID: 0198c27b-a2ed-7810-b64b-b00fdc46c9d5)
- **用户**: jiekewu
- **Python版本**: 3.12.3
- **默认Shell**: /bin/bash

## 实施步骤

### 1. 安装 Node Version Manager (nvm)
通过 nvm 在用户目录下安装 Node.js 环境：

```bash
# 下载并安装 nvm v0.39.0
ssh moleculemind 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash'
```

安装完成后，nvm 自动在 `~/.bashrc` 中添加了必要的环境变量配置。

### 2. 安装 Node.js LTS 版本

```bash
# 安装并设置 Node.js LTS 为默认版本
ssh moleculemind 'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm install --lts && nvm use --lts && nvm alias default lts/*'
```

安装结果：
- **Node.js**: v22.19.0 (LTS)
- **npm**: v10.9.3
- **npx**: v10.9.3

### 3. 配置 zsh 支持
为 zsh 用户添加 nvm 支持（moleculemind 上存在 .zshrc 文件）：

```bash
# 添加 nvm 配置到 .zshrc
ssh moleculemind 'echo "export NVM_DIR=\"\$HOME/.nvm\"" >> ~/.zshrc && \
echo "[ -s \"\$NVM_DIR/nvm.sh\" ] && \\. \"\$NVM_DIR/nvm.sh\"" >> ~/.zshrc && \
echo "[ -s \"\$NVM_DIR/bash_completion\" ] && \\. \"\$NVM_DIR/bash_completion\"" >> ~/.zshrc'
```

### 4. 安装 MCP 相关工具

#### 4.1 安装 Node.js 基础的 MCP 包
```bash
# 全局安装 MCP 服务器包
ssh moleculemind 'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && \
npm install -g @modelcontextprotocol/server-memory@latest \
@modelcontextprotocol/server-sequential-thinking@latest \
@upstash/context7-mcp@latest'
```

#### 4.2 安装 Python 工具管理器 (uv)
用于运行 Python 基础的 MCP 服务：

```bash
# 安装 uv 和 uvx
ssh moleculemind 'curl -LsSf https://astral.sh/uv/install.sh | sh'

# 添加到 PATH
ssh moleculemind 'echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.bashrc && \
echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.zshrc'
```

安装位置：
- uv: `/home/jiekewu/.local/bin/uv`
- uvx: `/home/jiekewu/.local/bin/uvx`

#### 4.3 复制 Python MCP 项目
将本地的 interactive-feedback-mcp 项目复制到服务器：

```bash
# 创建项目目录
ssh moleculemind 'mkdir -p ~/Cursor/MCPs/interactive-feedback-mcp'

# 复制必要文件
scp /Users/jieke/cursor_mcp/interactive-feedback-mcp/{server.py,feedback_ui.py,pyproject.toml,README.md} \
    moleculemind:~/Cursor/MCPs/interactive-feedback-mcp/
```

### 5. 创建 MCP 配置文件

创建 `~/.cursor/mcp.json` 配置文件，使用绝对路径确保远程环境下正常工作：

```json
{
  "inputs": [
    {
      "description": "GitHub Personal Access Token",
      "id": "github_token",
      "password": true,
      "type": "promptString"
    }
  ],
  "mcpServers": {
    "context7": {
      "args": [
        "/home/jiekewu/.nvm/versions/node/v22.19.0/lib/node_modules/@upstash/context7-mcp/dist/index.js"
      ],
      "command": "/home/jiekewu/.nvm/versions/node/v22.19.0/bin/node"
    },
    "git": {
      "args": [
        "mcp-server-git"
      ],
      "command": "/home/jiekewu/.local/bin/uvx"
    },
    "memory": {
      "args": [
        "/home/jiekewu/.nvm/versions/node/v22.19.0/lib/node_modules/@modelcontextprotocol/server-memory/dist/index.js"
      ],
      "command": "/home/jiekewu/.nvm/versions/node/v22.19.0/bin/node"
    },
    "sequential-thinking": {
      "args": [
        "/home/jiekewu/.nvm/versions/node/v22.19.0/lib/node_modules/@modelcontextprotocol/server-sequential-thinking/dist/index.js"
      ],
      "command": "/home/jiekewu/.nvm/versions/node/v22.19.0/bin/node"
    },
    "interactive-feedback-mcp": {
      "command": "/home/jiekewu/.local/bin/uv",
      "args": [
        "--directory",
        "/home/jiekewu/Cursor/MCPs/interactive-feedback-mcp",
        "run",
        "server.py"
      ],
      "timeout": 600,
      "autoApprove": [
        "interactive_feedback"
      ]
    },
    "time": {
        "command": "/home/jiekewu/.local/bin/uvx",
        "args": ["mcp-server-time"]
    }
  }
}
```

### 6. 备份配置
```bash
ssh moleculemind 'cp ~/.cursor/mcp.json ~/.cursor/mcp.json.backup'
```

## 关键要点

### 与 IBEX 配置的主要区别
1. **用户不同**: IBEX 使用 wuj0c，moleculemind 使用 jiekewu
2. **额外的 MCP 服务**: moleculemind 配置包含了 interactive-feedback-mcp (Python 项目)
3. **Python 工具链**: 需要额外安装 uv/uvx 来运行 Python 基础的 MCP 服务

### 路径配置策略
- **Node.js MCP 服务**: 使用绝对路径直接调用 node 执行器和模块文件
  - 从 `"command": "npx", "args": ["-y", "@package"]`
  - 改为 `"command": "/path/to/node", "args": ["/path/to/package/index.js"]`
- **Python MCP 服务**: 使用 uv 的绝对路径配合项目目录
- **uvx 命令服务**: 直接使用 uvx 的绝对路径

## 文件位置总结
- **nvm 安装目录**: `~/.nvm/`
- **Node.js 安装目录**: `~/.nvm/versions/node/v22.19.0/`
- **全局 npm 包**: `~/.nvm/versions/node/v22.19.0/lib/node_modules/`
- **uv/uvx 工具**: `~/.local/bin/`
- **Python MCP 项目**: `~/Cursor/MCPs/`
- **MCP 配置文件**: `~/.cursor/mcp.json`
- **配置备份**: `~/.cursor/mcp.json.backup`

## 验证命令

```bash
# 验证 Node.js 环境
ssh moleculemind 'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && \
which node && node --version && which npm && npm --version'

# 验证 Python 工具
ssh moleculemind 'export PATH="$HOME/.local/bin:$PATH" && which uv && which uvx'

# 测试 MCP 服务器
ssh moleculemind 'timeout 2 /home/jiekewu/.nvm/versions/node/v22.19.0/bin/node \
/home/jiekewu/.nvm/versions/node/v22.19.0/lib/node_modules/@modelcontextprotocol/server-memory/dist/index.js 2>&1 || true'

# 列出所有配置的 MCP 服务
ssh moleculemind 'cat ~/.cursor/mcp.json | jq -r ".mcpServers | keys[]" | sort'
```

## 已配置的 MCP 服务
- ✅ **context7** - 上下文管理服务 (Node.js)
- ✅ **git** - Git 操作服务 (Python/uvx)
- ✅ **memory** - 内存/知识图谱服务 (Node.js)
- ✅ **sequential-thinking** - 顺序思维服务 (Node.js)
- ✅ **interactive-feedback-mcp** - 交互反馈服务 (Python/uv)
- ✅ **time** - 时间服务 (Python/uvx)

## 注意事项
1. 重启 Cursor 编辑器以加载新的 MCP 配置
2. 首次使用时可能需要输入 GitHub Personal Access Token
3. 如需更新 Node.js 版本，记得同步更新 mcp.json 中的路径
4. Python MCP 项目首次运行时会自动安装依赖

## 故障排查
- 如果 MCP 工具无法激活，检查 `~/.cursor/mcp.json` 中的路径是否正确
- 确保所有可执行文件有正确的执行权限
- 查看 Cursor 的输出日志以获取详细错误信息