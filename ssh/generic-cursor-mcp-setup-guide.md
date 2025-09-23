# 通用 Cursor MCP 配置指南：无 Root 权限服务器环境

## 概述
本指南提供了在无 sudo/root 权限的远程服务器环境下配置 Cursor 编辑器 MCP (Model Context Protocol) 工具的通用解决方案。该方案适用于各类受限权限的服务器环境，如高性能计算集群、共享开发服务器等。

## 适用场景
- 用户无 sudo/root 权限
- 无法使用系统包管理器（apt、yum 等）
- 需要在用户空间完成所有配置
- Cursor 通过 Remote SSH 连接到服务器

## 核心原理
MCP 工具在 Cursor 启动时加载，此时远程服务器的环境变量可能未完全初始化。解决方案是：
1. 使用绝对路径替代依赖 PATH 的命令
2. 在用户目录下安装所有依赖
3. 手动配置环境变量

## 前置准备

### 检查系统环境
```bash
# 检查主机信息
ssh <your-server> 'hostname && whoami && pwd'

# 检查默认 shell
ssh <your-server> 'echo $SHELL'

# 检查 Python 版本（如需要）
ssh <your-server> 'which python3 && python3 --version'
```

### 创建必要目录
```bash
ssh <your-server> 'mkdir -p ~/.cursor'
```

## 安装步骤

### 步骤 1：安装 Node.js 环境（通过 nvm）

#### 1.1 安装 nvm
```bash
# 安装 nvm（Node Version Manager）
ssh <your-server> 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash'
```

nvm 会自动在 `~/.bashrc` 中添加以下配置：
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
```

#### 1.2 安装 Node.js LTS
```bash
# 加载 nvm 并安装 Node.js LTS
ssh <your-server> 'export NVM_DIR="$HOME/.nvm" && \
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && \
    nvm install --lts && \
    nvm use --lts && \
    nvm alias default lts/*'
```

#### 1.3 配置其他 Shell（可选）
如果使用 zsh：
```bash
ssh <your-server> 'echo "export NVM_DIR=\"\$HOME/.nvm\"" >> ~/.zshrc && \
    echo "[ -s \"\$NVM_DIR/nvm.sh\" ] && \\. \"\$NVM_DIR/nvm.sh\"" >> ~/.zshrc && \
    echo "[ -s \"\$NVM_DIR/bash_completion\" ] && \\. \"\$NVM_DIR/bash_completion\"" >> ~/.zshrc'
```

### 步骤 2：安装 Python 工具链（如需要）

#### 2.1 安装 uv/uvx
用于管理和运行 Python 基础的 MCP 服务：
```bash
# 安装 uv
ssh <your-server> 'curl -LsSf https://astral.sh/uv/install.sh | sh'

# 添加到 PATH
ssh <your-server> 'echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.bashrc'

# 如果使用 zsh
ssh <your-server> 'echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.zshrc'
```

### 步骤 3：安装 MCP 包

#### 3.1 Node.js 基础的 MCP 包
```bash
# 加载 nvm 环境并安装包
ssh <your-server> 'export NVM_DIR="$HOME/.nvm" && \
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && \
    npm install -g \
        @modelcontextprotocol/server-memory@latest \
        @modelcontextprotocol/server-sequential-thinking@latest \
        @upstash/context7-mcp@latest'
```

#### 3.2 Python 基础的 MCP 项目（可选）
如有自定义 Python MCP 项目：
```bash
# 创建项目目录
ssh <your-server> 'mkdir -p ~/Cursor/MCPs/<project-name>'

# 复制项目文件
scp -r /local/path/to/mcp-project/* <your-server>:~/Cursor/MCPs/<project-name>/
```

### 步骤 4：获取安装路径
```bash
# 获取 Node.js 路径
ssh <your-server> 'export NVM_DIR="$HOME/.nvm" && \
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && \
    echo "Node path: $(which node)" && \
    echo "NPM modules path: $(npm root -g)"'

# 获取 Python 工具路径（如已安装）
ssh <your-server> 'export PATH="$HOME/.local/bin:$PATH" && \
    echo "uv path: $(which uv)" && \
    echo "uvx path: $(which uvx)"'
```

### 步骤 5：配置 MCP

创建 `~/.cursor/mcp.json` 配置文件。以下是模板，请根据实际路径替换：

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
        "/home/<username>/.nvm/versions/node/<version>/lib/node_modules/@upstash/context7-mcp/dist/index.js"
      ],
      "command": "/home/<username>/.nvm/versions/node/<version>/bin/node"
    },
    "git": {
      "args": ["mcp-server-git"],
      "command": "/home/<username>/.local/bin/uvx"
    },
    "memory": {
      "args": [
        "/home/<username>/.nvm/versions/node/<version>/lib/node_modules/@modelcontextprotocol/server-memory/dist/index.js"
      ],
      "command": "/home/<username>/.nvm/versions/node/<version>/bin/node"
    },
    "sequential-thinking": {
      "args": [
        "/home/<username>/.nvm/versions/node/<version>/lib/node_modules/@modelcontextprotocol/server-sequential-thinking/dist/index.js"
      ],
      "command": "/home/<username>/.nvm/versions/node/<version>/bin/node"
    },
    "time": {
      "command": "/home/<username>/.local/bin/uvx",
      "args": ["mcp-server-time"]
    }
  }
}
```

**关键点**：
- 将 `<username>` 替换为实际用户名
- 将 `<version>` 替换为实际 Node.js 版本（如 v22.19.0）
- 所有路径必须是绝对路径
- Node.js MCP 服务：使用 node 二进制文件直接执行 .js 文件
- Python MCP 服务：使用 uv/uvx 的绝对路径

### 步骤 6：创建配置备份
```bash
ssh <your-server> 'cp ~/.cursor/mcp.json ~/.cursor/mcp.json.backup'
```

## 包装脚本方案（备选）

如果绝对路径方案不工作，可以创建包装脚本：

```bash
# 创建 bin 目录
ssh <your-server> 'mkdir -p ~/bin'

# 创建 npx 包装脚本
ssh <your-server> 'cat > ~/bin/npx-wrapper << '\''EOF'\''
#!/bin/bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
exec npx "$@"
EOF
chmod +x ~/bin/npx-wrapper'

# 创建 node 包装脚本
ssh <your-server> 'cat > ~/bin/node-wrapper << '\''EOF'\''
#!/bin/bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
exec node "$@"
EOF
chmod +x ~/bin/node-wrapper'
```

然后在 mcp.json 中使用包装脚本路径。

## 验证安装

### 验证 Node.js 环境
```bash
ssh <your-server> 'export NVM_DIR="$HOME/.nvm" && \
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && \
    which node && node --version && \
    which npm && npm --version && \
    which npx && npx --version'
```

### 验证 Python 工具（如已安装）
```bash
ssh <your-server> 'export PATH="$HOME/.local/bin:$PATH" && \
    which uv && which uvx'
```

### 测试 MCP 服务器
```bash
# 测试 Node.js MCP 服务（以 memory 为例）
ssh <your-server> 'timeout 2 /home/<username>/.nvm/versions/node/<version>/bin/node \
    /home/<username>/.nvm/versions/node/<version>/lib/node_modules/@modelcontextprotocol/server-memory/dist/index.js \
    2>&1 || true'
```

### 列出配置的 MCP 服务
```bash
ssh <your-server> 'cat ~/.cursor/mcp.json | jq -r ".mcpServers | keys[]" | sort'
```

## 常见 MCP 服务说明

| 服务名 | 类型 | 功能描述 | 运行方式 |
|--------|------|----------|----------|
| context7 | Node.js | 上下文管理服务 | node + 模块路径 |
| memory | Node.js | 内存/知识图谱服务 | node + 模块路径 |
| sequential-thinking | Node.js | 顺序思维服务 | node + 模块路径 |
| git | Python | Git 操作服务 | uvx + 包名 |
| time | Python | 时间服务 | uvx + 包名 |
| 自定义 Python 项目 | Python | 自定义功能 | uv run + 脚本 |

## 目录结构参考

```
$HOME/
├── .nvm/                          # nvm 安装目录
│   └── versions/
│       └── node/
│           └── <version>/
│               ├── bin/           # node、npm、npx 二进制文件
│               └── lib/
│                   └── node_modules/  # 全局 npm 包
├── .local/
│   └── bin/                      # uv、uvx 二进制文件
├── .cursor/
│   ├── mcp.json                  # MCP 配置文件
│   └── mcp.json.backup           # 配置备份
├── Cursor/
│   └── MCPs/                     # Python MCP 项目目录
│       └── <project-name>/
├── bin/                          # 可选：包装脚本目录
│   ├── node-wrapper
│   └── npx-wrapper
├── .bashrc                       # bash 配置（含 nvm 和 PATH）
└── .zshrc                        # zsh 配置（如有）
```

## 故障排查

### 问题 1：MCP 工具无法激活
- **检查路径**：确保 mcp.json 中的所有路径都是绝对路径且正确
- **验证权限**：确保所有可执行文件有执行权限
- **查看日志**：检查 Cursor 输出窗口的错误信息

### 问题 2：找不到 npx/node 命令
- **原因**：环境变量未加载
- **解决**：使用绝对路径或包装脚本

### 问题 3：Python MCP 服务启动失败
- **检查 uv 安装**：确保 uv/uvx 已正确安装
- **验证项目文件**：确保所有必要的项目文件都已复制

### 问题 4：配置更新后不生效
- **重启 Cursor**：配置更改后需要重启 Cursor
- **清理缓存**：有时需要清理 Cursor 的缓存

## 维护建议

### 更新 Node.js 版本
```bash
# 安装新版本
nvm install --lts
nvm alias default lts/*

# 重新安装全局包
npm install -g @modelcontextprotocol/server-memory@latest ...

# 更新 mcp.json 中的路径
```

### 添加新的 MCP 服务
1. 安装包：`npm install -g @new-package`
2. 获取路径：`npm root -g`
3. 更新 mcp.json，使用绝对路径

### 备份和恢复
```bash
# 备份
cp ~/.cursor/mcp.json ~/.cursor/mcp.json.$(date +%Y%m%d)

# 恢复
cp ~/.cursor/mcp.json.backup ~/.cursor/mcp.json
```

## 安全注意事项
1. **不要在配置文件中硬编码敏感信息**（如 token、密码）
2. **定期更新依赖包**以获取安全补丁
3. **限制配置文件权限**：`chmod 600 ~/.cursor/mcp.json`
4. **使用 SSH 密钥**而非密码进行服务器连接

## 总结
本方案的核心是通过使用绝对路径来解决远程服务器环境变量加载时机的问题。通过 nvm 管理 Node.js 环境，通过 uv 管理 Python 环境，实现了在无 root 权限环境下的完整 MCP 工具链配置。