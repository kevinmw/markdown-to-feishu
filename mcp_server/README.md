# 飞书MCP服务器

Model Context Protocol (MCP) 服务器组件，用于与飞书(Lark)文档系统集成。将飞书的文档操作功能暴露为MCP工具，可以在Claude Desktop等支持MCP的AI助手中使用。

> 注意：这是飞书开发工具集的MCP集成部分。完整项目文档请参见根目录的 [CLAUDE.md](../CLAUDE.md)。

## 功能特性

### 🔧 可用工具

1. **create_feishu_document** - 创建新的飞书文档
   - 参数：title (文档标题), folder_token (可选文件夹位置)
   - 返回：文档ID和创建状态

2. **convert_markdown_to_blocks** - 将Markdown文本转换为飞书文档块
   - 参数：markdown_text (Markdown内容)
   - 返回：转换后的文档块数据

3. **insert_content_to_document** - 向文档插入内容块
   - 参数：document_id (文档ID), blocks_data (内容块数据)
   - 返回：插入操作状态

4. **convert_markdown_file_to_feishu_document** - 完整工作流：文件转文档
   - 参数：markdown_file_path (文件路径), document_title (文档标题), folder_token (可选)
   - 返回：完整操作结果

5. **get_feishu_config_info** - 获取配置状态信息
   - 无参数
   - 返回：配置验证状态

## 安装和配置

### 1. 安装依赖

```bash
pip install "mcp[cli]" lark-oapi
```

### 2. 配置飞书访问令牌

确保项目根目录的 `src/utils/config.py` 中有正确的飞书配置：

```python
DEFAULT_CONFIG = {
    'app_id': 'your_app_id',
    'app_secret': 'your_app_secret',
    'user_access_token': 'your_user_access_token'
}
```

### 3. 运行MCP服务器

```bash
python feishu_mcp_server.py
```

## MCP客户端配置

此MCP服务器兼容所有支持Model Context Protocol的应用。参考配置文件：`mcp_config_example.json`

### Claude Desktop配置

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 其他MCP客户端

任何支持MCP的应用都可以使用类似的配置格式：

```json
{
  "mcpServers": {
    "feishu": {
      "command": "python",
      "args": ["/path/to/your/feishu/mcp_server/feishu_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/your/feishu"
      }
    }
  }
}
```

请将路径替换为实际的项目路径。

## 使用示例

配置完成后，你可以在Claude Desktop中使用这些功能：

### 创建文档
```
请帮我创建一个名为"项目计划"的飞书文档
```

### 转换Markdown文件
```
请将这个README.md文件转换为飞书文档，标题为"项目文档"
```

### 检查配置
```
请检查飞书MCP服务器的配置状态
```

## 项目结构

```
feishu/
├── mcp_server/
│   ├── feishu_mcp_server.py  # MCP服务器主文件
│   ├── pyproject.toml        # 项目配置
│   └── README.md             # 本文档
├── src/
│   ├── core/                 # 核心功能模块
│   └── utils/                # 工具模块
└── apps/                     # 独立应用
```

## 故障排除

### 常见问题

1. **令牌过期错误**
   - 检查 `src/utils/config.py` 中的 `user_access_token` 是否有效
   - 使用飞书开发者后台刷新令牌

2. **模块导入错误**
   - 确保在项目根目录运行MCP服务器
   - 检查Python路径设置

3. **连接问题**
   - 确保MCP服务器正在运行
   - 检查Claude Desktop配置文件中的路径是否正确

### 调试模式

运行服务器时可以看到详细的日志输出：

```bash
python feishu_mcp_server.py
```

## 开发说明

本MCP服务器基于现有的飞书开发工具包构建，重用了以下核心模块：

- `DocumentCreator`: 文档创建功能
- `MarkdownConverter`: Markdown转换功能  
- `ContentInserter`: 内容插入功能

这些模块已经过测试，可以可靠地完成飞书文档操作。