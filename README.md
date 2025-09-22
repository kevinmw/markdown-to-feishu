# 飞书开发工具集

一个用于飞书开放平台开发的Python工具集，支持文档创建、Markdown转换、内容插入和AI集成等功能。

## 项目意义

### 背景：AI辅助开发的新范式

在现代软件开发中，AI辅助编程已成为主流趋势。无论是Cursor、Trae、IDEA等AI加持的IDE，还是Claude Code、Gemini CLI、Codex这样的命令行Agent，都倡导一种以**文档驱动**的开发模式：

1. **充分沟通**：与AI工具详细描述问题、需求和技术框架
2. **文档记录**：将解决方案、开发计划、进展等记录在Markdown文档中（如CLAUDE.md）
3. **版本控制**：将文档纳入Git管理，便于团队协作和知识传承

这种模式让AI能够有序可控地开展工作，同时完整保留从问题分析到解决方案的全过程。

### 现实挑战：两个世界的割裂

**飞书文档**是小米内部协作的核心载体，承载着：
- 需求讨论与产品设计
- 前后端协作沟通  
- 知识沉淀与架构设计
- 项目进展汇报

**Markdown文档**（如CLAUDE.md）是文档驱动的载体记录着：
- 完整的技术实现过程
- AI辅助开发的思路和方案
- 有价值的技术知识和经验

这两个重要的知识载体之间缺乏有效连接，使得AI辅助开发成果转化为团队共享飞书文档的过程繁琐低效。

### 解决方案：一键式无缝转换

本项目通过**MCP（Model Context Protocol）**集成，实现了Markdown到飞书文档的一键转换：

**核心价值**：
- ✅ **开发完成即文档完成**：一句话将工作成果转化为美观的飞书文档
- ✅ **自然融入AI工作流**：无需改变现有开发习惯，AI工具原生支持
- ✅ **跨平台兼容**：支持VS Code、Vim、IDEA等主流开发环境
- ✅ **团队协作增强**：技术知识快速转化为可共享的企业文档

**实际效果**：让AI辅助开发的价值从个人延伸到团队，从开发阶段延伸到后续的产品迭代和知识传承。

## 技术方案

### 可行性调研

在项目启动时，我们查阅了飞书开发者平台的文档，发现飞书提供了一些文档操作的API。经过测试和比较，我们选择了三个核心接口来实现Markdown转换功能：

### 核心API选型

**1. 文档创建API (`/open-apis/docx/v1/documents`)**
- **功能**：创建新的飞书云文档
- **输入**：文档标题、文件夹位置（可选）
- **输出**：文档ID，作为后续操作的唯一标识
- **技术特点**：支持指定文档位置，便于组织管理

**2. Markdown转换API (`/open-apis/docx/v1/documents/convert`)**  
- **功能**：将Markdown文本转换为飞书文档块结构
- **输入**：原始Markdown文本内容
- **输出**：具有父子关系的文档块树状结构
- **技术特点**：自动识别Markdown语法，生成对应的飞书格式

**3. 内容插入API (`/open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/descendants`)**
- **功能**：将文档块批量插入到指定文档位置
- **输入**：目标文档ID、块结构数据、插入位置
- **输出**：插入操作结果和文档版本号
- **技术特点**：支持批量操作，保持文档结构完整性

### 技术架构设计

采用两层架构设计，实现了完整的转换流程：

```
Claude Code    Gemini CLI    Cursor/Trae    Cherry Studio
     │              │            │               │
     └──────────────┼────────────┼───────────────┘
                    │            │
                    └─────┬──────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        第二层：MCP封装层                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │           MCP工具接口 (AI工具兼容层)                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      第一层：核心转换逻辑                         │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│ │  Document   │  │  Markdown   │  │   Content   │             │
│ │   Creator   │─▶│  Converter  │─▶│  Inserter   │             │
│ │             │  │             │  │             │             │
│ │ 创建飞书文档 │  │MD→文档块转换 │  │ 块结构插入   │             │
│ └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                            飞书开放平台API
                                   │
                                   ▼
                              飞书云盘
```

**第一层：核心转换逻辑**
- 封装了创建、转换、插入的完整业务流程
- DocumentCreator、MarkdownConverter、ContentInserter三个模块协同工作
- 处理飞书API调用和错误重试机制

**第二层：MCP封装层**  
- 将底层转换逻辑封装成标准MCP工具接口
- 提供极好的兼容性，支持各种AI工具（开发工具和通用AI工具）
- 实现了"一句话完成转换"的用户体验

### MCP集成方案

使用Model Context Protocol协议，我们将API功能封装成AI工具可以调用的服务：

**服务架构**：
```
AI工具(Claude Code/Cursor) 
        ↕ MCP Protocol
MCP Server (FastMCP框架)
        ↕ 
核心转换模块 (Python SDK)
        ↕
飞书开放平台API
```

**集成优势**：
- **标准接口**：使用MCP协议，兼容主流AI工具
- **广泛适用**：支持开发工具（Claude Code、Cursor）和通用AI工具（Cherry Studio）
- **简单集成**：AI工具不需要修改，只要配置一下就能用
- **实时反馈**：转换过程中可以看到进度

### 一键安装体验

为了方便使用，我们提供了简单的配置方法：

**配置文件示例**：
```json
{
  "mcpServers": {
    "feishu": {
      "command": "python",
      "args": ["/path/to/feishu_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/your/feishu"
      }
    }
  }
}
```

**部署流程**：
1. 克隆项目到本地
2. 安装Python依赖 (`pip install -r requirements.txt`)
3. 配置飞书应用凭据到环境变量 (`~/.zshrc`)
4. 添加MCP配置到AI工具
5. 重启AI工具，即可使用

这套方案能够保证转换质量，同时使用起来很简单，配置一次就能一直用。

## 项目结构

```
feishu/
├── CLAUDE.md                   # 项目说明文档
├── VERSION                     # 版本管理
├── pyproject.toml              # 项目配置文件
├── requirements.txt            # 项目依赖
├── src/                        # 源代码目录
│   ├── __init__.py
│   ├── core/                   # 核心功能模块
│   │   ├── __init__.py
│   │   ├── document_creator.py # 文档创建功能
│   │   ├── markdown_converter.py # Markdown转换功能
│   │   └── content_inserter.py # 内容插入功能
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       └── config.py          # 配置管理
├── examples/                   # 示例脚本
│   └── simple_message.py      # 发送消息示例
├── apps/                       # 应用程序目录
│   ├── README.md               # 应用使用说明
│   └── markdown_to_feishu_doc.py # Markdown转飞书文档应用
├── mcp_server/                 # MCP服务器目录
│   ├── README.md               # MCP使用说明
│   ├── feishu_mcp_server.py    # MCP服务器主文件
│   └── mcp_config_example.json # MCP配置示例
├── docs/                       # 文档目录
│   ├── api_notes.md           # API使用笔记
│   └── examples/              # 示例文件
│       ├── sample.md          # 示例Markdown文件
│       └── simple_test.md     # 简单测试文件
└── tests/                     # 测试目录
    ├── __init__.py            # 测试包初始化
    ├── run_tests.py           # 测试运行器
    ├── test_document_creator.py # 文档创建模块测试
    ├── test_markdown_converter.py # Markdown转换模块测试
    ├── test_content_inserter.py # 内容插入模块测试
    └── test_config.py         # 配置管理模块测试
```

## 核心功能

### 1. 文档创建模块 (src/core/document_creator.py)

**核心类：`DocumentCreator`**
```python
class DocumentCreator:
    def __init__(self, user_access_token: str)
    def create_document(self, title: str, folder_token: Optional[str] = None) -> Optional[str]
```

**方法说明：**
- `create_document()`: 创建新的飞书文档，返回document_id

**便捷函数：**
- `create_document(title, user_access_token, folder_token=None)`: 快速创建文档

**功能特性：**
- 创建新的飞书文档
- 支持自定义标题和文件夹位置
- 返回文档ID供后续操作
- 完整的错误处理和日志记录

### 2. Markdown转换模块 (src/core/markdown_converter.py)

**核心类：`MarkdownConverter`**
```python
class MarkdownConverter:
    def __init__(self, user_access_token: str)
    def convert_file_to_blocks(self, markdown_file_path: str) -> Optional[Dict[str, Any]]
    def convert_text_to_blocks(self, markdown_content: str) -> Optional[Dict[str, Any]]
```

**方法说明：**
- `convert_file_to_blocks()`: 从文件路径读取并转换Markdown
- `convert_text_to_blocks()`: 直接转换Markdown文本内容

**便捷函数：**
- `convert_markdown_file(file_path, user_access_token)`: 快速转换文件
- `convert_markdown_text(text, user_access_token)`: 快速转换文本

**功能特性：**
- 将Markdown文本转换为飞书文档块
- 支持标题、列表、表格、代码块、引用等
- 保持原有格式和结构
- 返回包含blocks和first_level_block_ids的数据结构
- **表格兼容性优化**: 自动处理API兼容性问题

### 3. 内容插入模块 (src/core/content_inserter.py)

**核心类：`ContentInserter`**
```python
class ContentInserter:
    def __init__(self, user_access_token: str)
    def insert_blocks_to_document(self, document_id: str, blocks_data: Dict[str, Any], 
                                  parent_block_id: Optional[str] = None, index: int = 0) -> bool
    def insert_simple_table(self, document_id: str, title: str = "简单表格", 
                           parent_block_id: Optional[str] = None) -> bool
```

**方法说明：**
- `insert_blocks_to_document()`: 将转换后的块数据插入到文档中
- `insert_simple_table()`: 插入预定义的简单表格

**便捷函数：**
- `insert_markdown_blocks(document_id, blocks_data, user_access_token)`: 快速插入Markdown块
- `insert_table(document_id, title, user_access_token)`: 快速插入表格

**功能特性：**
- 在指定文档中插入内容块
- 支持插入到文档开头或指定位置（index参数）
- 非覆盖式插入，保持原有内容
- 当parent_block_id等于document_id时，插入到文档根级别
- **表格自动修复**: 自动过滤表格块中的merge_info字段，解决API兼容性问题

### 4. 配置管理模块 (src/utils/config.py)

**核心类：`FeishuConfig`**
```python
class FeishuConfig:
    def __init__(self)
    @classmethod
    def from_env(cls) -> 'FeishuConfig'
    @classmethod  
    def from_dict(cls, config_dict: dict) -> 'FeishuConfig'
    def validate(self) -> bool
    def get_access_token(self) -> Optional[str]
```

**方法说明：**
- `from_env()`: 从环境变量加载配置
- `from_dict()`: 从字典加载配置
- `validate()`: 验证配置完整性
- `get_access_token()`: 获取可用的访问令牌

**便捷函数：**
- `get_default_config()`: 获取默认测试配置

**功能特性：**
- 统一的配置管理
- 支持环境变量和字典配置
- 自动令牌选择（优先用户令牌）
- 配置验证功能

## 表格功能增强

### 问题背景
飞书API中表格块的`merge_info`字段为只读属性，在批量插入时会引发"invalid param"错误，导致包含表格的Markdown文档无法正常转换。

### 解决方案
在`src/core/content_inserter.py`中实现了`_filter_table_merge_info`方法：

**技术实现：**
- **自动检测**: 识别表格块(block_type: 31)
- **字段过滤**: 移除merge_info字段，保留其他属性
- **对象重构**: 重新构建兼容的表格块对象
- **无缝集成**: 对用户透明，自动处理

**支持特性：**
- ✅ 复杂表格结构
- ✅ 表头设置(header_row, header_column)
- ✅ 列宽自定义(column_width)
- ✅ 多行多列表格
- ✅ 表格内容格式化

### 使用效果
```python
# 现在可以正常处理包含表格的Markdown
markdown_with_table = """
# 项目状态

| 功能 | 状态 | 备注 |
|------|------|------|
| 文档创建 | ✅ | 完成 |
| 表格支持 | ✅ | 已修复 |
"""

# 自动处理表格兼容性，无需额外配置
result = create_feishu_document_from_markdown(markdown_with_table, "项目报告")
```

## 快速开始

### 安装依赖
```bash
pip install lark-oapi
```

### 使用应用（推荐）
```bash
# 将Markdown文件转换为飞书文档（需要两个参数：文件路径和文档标题）
python apps/markdown_to_feishu_doc.py docs/examples/simple_test.md "我的文档标题"
```

### 使用核心模块开发
```python
from src.core.document_creator import create_document
from src.core.markdown_converter import convert_markdown_file
from src.core.content_inserter import insert_markdown_blocks

# 创建文档
doc_id = create_document("我的新文档", user_token)

# 转换Markdown文件
blocks = convert_markdown_file("path/to/your/file.md", user_token)

# 插入内容
insert_markdown_blocks(doc_id, blocks, user_token)
```

## 配置说明

需要在环境变量中设置（推荐在 `~/.zshrc` 中）：
- `FEISHU_APP_ID`: 应用ID
- `FEISHU_APP_SECRET`: 应用密钥
- `FEISHU_USER_ACCESS_TOKEN`: 用户访问令牌

## 开发计划

- [x] 基础功能开发
- [x] 项目结构设计
- [x] 核心模块重构
- [x] 完整工作流集成
- [x] 第一个应用开发（markdown_to_feishu_doc）
- [x] 错误处理优化
- [x] 配置管理系统
- [x] 文档完善
- [x] 单元测试覆盖
- [x] MCP服务器集成
- [x] 项目结构标准化
- [x] **表格功能修复**: 完美支持包含表格的Markdown文档转换
- [x] **MCP工具简化**: 优化为两个核心工具，提升易用性
- [ ] **Token自动刷新机制**: 实现OAuth 2.0 refresh_token自动刷新，解决token过期问题 🔥
- [ ] **Mermaid图表支持**: 开发云文档小组件实现Mermaid图表渲染 🎯
- [ ] 更多应用开发
- [ ] 性能优化

## AI集成 (MCP)

本项目支持Model Context Protocol (MCP)，可以与Claude Desktop等AI助手无缝集成。

### MCP功能 (简化版本)

**当前对外提供的两个核心工具：**

1. **`convert_markdown_file_to_feishu_document`** - 从Markdown文件创建飞书文档
   - 参数：`markdown_file_path`, `document_title`, `folder_token`(可选)
   - 功能：完整的文件转换工作流

2. **`create_feishu_document_from_markdown`** - 从Markdown文本创建飞书文档  
   - 参数：`markdown_text`, `document_title`, `folder_token`(可选)
   - 功能：直接文本转换工作流

**隐藏的内部工具** (用于复杂场景):
- `create_feishu_document`: 单独创建文档
- `convert_markdown_to_blocks`: 转换验证  
- `insert_content_to_document`: 插入内容
- `get_feishu_config_info`: 配置信息

注意：这些内部工具已在MCP服务器中被注释掉，当前只对外提供两个核心工具。

**特性优势：**
- ✅ **简洁接口**: 只暴露两个核心工具，易于理解和使用
- ✅ **完整功能**: 每个工具都提供端到端的解决方案
- ✅ **表格支持**: 完美支持包含表格的Markdown文档
- ✅ **自动修复**: 自动处理飞书API的兼容性问题

### 配置MCP服务器
参考 `mcp_server/mcp_config_example.json` 配置文件，将MCP服务器添加到支持MCP的AI应用中。

## 测试

项目包含完整的单元测试套件：

```bash
# 运行所有测试
python tests/run_tests.py

# 运行特定模块测试
python tests/test_document_creator.py
python tests/test_markdown_converter.py
python tests/test_content_inserter.py
python tests/test_config.py
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 未来发展路线图

### Token自动刷新机制 🔥
基于OAuth 2.0实现refresh_token自动刷新，彻底解决token过期问题，支持长期无人值守运行。

### Mermaid图表支持 🎯  
开发飞书云文档小组件，实现Mermaid图表自动渲染，用户无需手动复制即可在文档中直接展示流程图、序列图等图表。

## 许可证

MIT License