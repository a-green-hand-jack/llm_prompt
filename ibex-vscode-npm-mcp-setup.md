# 在 IBEX-VSCode 服务器上配置 npm/npx 和 MCP 工具的完整解决方案

## 问题背景
在 KAUST IBEX 集群的 VSCode 服务器上，用户没有 sudo 权限，无法通过常规方式安装 npm/npx。同时，Cursor 编辑器的 MCP (Model Context Protocol) 工具依赖 npx 来激活，但在远程服务器环境下无法正常工作。

## 实施步骤

### 1. 安装 Node Version Manager (nvm)
由于没有 sudo 权限，使用 nvm 在用户目录下安装 Node.js：

```bash
# 下载并安装 nvm
ssh ibex-vscode 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash'
```

nvm 自动配置了 `~/.bashrc`，添加了以下内容：
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
```

### 2. 安装 Node.js LTS 版本
```bash
# 安装 Node.js LTS 版本
ssh ibex-vscode 'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm install --lts && nvm use --lts && nvm alias default lts/*'
```

安装结果：
- Node.js: v22.19.0 (LTS)
- npm: v10.9.3
- npx: v10.9.3

### 3. 配置 zsh 支持（如果使用 zsh）
```bash
# 添加 nvm 配置到 .zshrc
ssh ibex-vscode 'echo "export NVM_DIR=\"\$HOME/.nvm\"" >> ~/.zshrc && echo "[ -s \"\$NVM_DIR/nvm.sh\" ] && \. \"\$NVM_DIR/nvm.sh\"" >> ~/.zshrc && echo "[ -s \"\$NVM_DIR/bash_completion\" ] && \. \"\$NVM_DIR/bash_completion\"" >> ~/.zshrc'
```

### 4. 解决 MCP 工具激活问题

#### 问题分析
MCP 工具在 Cursor 启动时加载，此时 nvm 环境变量尚未初始化，导致找不到 npx 命令。

#### 解决方案：全局安装 MCP 包并使用绝对路径

1. **全局安装所需的 MCP 包：**
```bash
# 安装 MCP 服务器包
npm install -g @modelcontextprotocol/server-memory@latest
npm install -g @modelcontextprotocol/server-sequential-thinking@latest
npm install -g @upstash/context7-mcp@latest
```

2. **更新 MCP 配置文件 (`~/.cursor/mcp.json`)：**
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
        "/home/wuj0c/.nvm/versions/node/v22.19.0/lib/node_modules/@upstash/context7-mcp/dist/index.js"
      ],
      "command": "/home/wuj0c/.nvm/versions/node/v22.19.0/bin/node"
    },
    "git": {
      "args": [
        "mcp-server-git"
      ],
      "command": "uvx"
    },
    "memory": {
      "args": [
        "/home/wuj0c/.nvm/versions/node/v22.19.0/lib/node_modules/@modelcontextprotocol/server-memory/dist/index.js"
      ],
      "command": "/home/wuj0c/.nvm/versions/node/v22.19.0/bin/node"
    },
    "sequential-thinking": {
      "args": [
        "/home/wuj0c/.nvm/versions/node/v22.19.0/lib/node_modules/@modelcontextprotocol/server-sequential-thinking/dist/index.js"
      ],
      "command": "/home/wuj0c/.nvm/versions/node/v22.19.0/bin/node"
    },
    "interactive-feedback-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/wuj0c/Cursor/MCPs/interactive-feedback-mcp",
        "run",
        "server.py"
      ],
      "timeout": 600,
      "autoApprove": [
        "interactive_feedback"
      ]
    },
    "time": {
        "command": "uvx",
        "args": ["mcp-server-time"]
      }
  }
}
```

### 5. 创建包装脚本（备选方案）
如果需要，可以创建包装脚本来确保环境正确：

```bash
# 创建 npx 包装脚本
cat > ~/bin/npx-wrapper << 'EOF'
#!/bin/bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
export PATH="/home/wuj0c/.nvm/versions/node/v22.19.0/bin:$PATH"
exec /home/wuj0c/.nvm/versions/node/v22.19.0/bin/npx "$@"
EOF
chmod +x ~/bin/npx-wrapper

# 创建 node 包装脚本
cat > ~/bin/node-wrapper << 'EOF'
#!/bin/bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
export PATH="/home/wuj0c/.nvm/versions/node/v22.19.0/bin:$PATH"
export NODE_PATH="/home/wuj0c/.nvm/versions/node/v22.19.0/lib/node_modules"
exec /home/wuj0c/.nvm/versions/node/v22.19.0/bin/node "$@"
EOF
chmod +x ~/bin/node-wrapper
```

## 关键要点

1. **无需 sudo 权限：** 使用 nvm 可以在用户目录下完整安装 Node.js 生态系统
2. **路径问题：** MCP 工具需要使用绝对路径来确保能找到可执行文件
3. **环境变量：** 远程服务器环境下，需要特别注意环境变量的初始化时机
4. **配置更改：**
   - 从 `"command": "npx", "args": ["-y", "@package"]`
   - 改为 `"command": "/path/to/node", "args": ["/path/to/package/index.js"]`

## 验证安装

```bash
# 验证 npm/npx 安装
ssh ibex-vscode 'source ~/.bashrc && which npm && npm --version && which npx && npx --version'

# 测试 MCP 服务器
ssh ibex-vscode 'timeout 2 /home/wuj0c/.nvm/versions/node/v22.19.0/bin/node /home/wuj0c/.nvm/versions/node/v22.19.0/lib/node_modules/@modelcontextprotocol/server-memory/dist/index.js'
```

## 文件位置
- nvm 安装目录：`~/.nvm/`
- Node.js 安装目录：`~/.nvm/versions/node/v22.19.0/`
- 全局 npm 包目录：`~/.nvm/versions/node/v22.19.0/lib/node_modules/`
- MCP 配置文件：`~/.cursor/mcp.json`

## 后续维护

1. **更新 Node.js 版本：**
   ```bash
   nvm install --lts
   nvm alias default lts/*
   ```
   注意：更新后需要相应更新 MCP 配置文件中的路径

2. **安装新的 MCP 工具：**
   ```bash
   npm install -g @new-mcp-tool
   # 然后在 mcp.json 中添加相应配置，使用绝对路径
   ```

3. **备份：**
   配置文件已备份至 `~/.cursor/mcp.json.backup`

## 最终效果
- ✅ 可以在 bash/zsh 中直接使用 npm/npx 命令
- ✅ MCP 工具在 Cursor 中正常激活和运行
- ✅ 无需 sudo 权限即可管理 Node.js 环境
- ✅ 支持多版本 Node.js 切换（通过 nvm）