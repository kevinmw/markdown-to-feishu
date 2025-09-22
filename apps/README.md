# 飞书应用集合

这个目录包含了基于飞书开发工具集构建的实用应用程序。

## 应用列表

### 1. markdown_to_feishu_doc.py

**功能描述**：将Markdown文件转换为飞书文档

**使用方法**：
```bash
# 基本用法
python markdown_to_feishu_doc.py your_file.md

# 指定自定义访问令牌
python markdown_to_feishu_doc.py your_file.md --token your_token

# 使用绝对路径
python markdown_to_feishu_doc.py /full/path/to/your_file.md
```

**工作流程**：
1. 📁 读取指定的Markdown文件
2. 📝 创建与文件名同名的飞书文档
3. 🔄 将Markdown内容转换为飞书文档块
4. 📤 将转换后的内容插入到新文档中

**输入要求**：
- 有效的Markdown文件路径
- 配置好的飞书访问令牌

**输出结果**：
- 在飞书中创建新文档
- 文档标题为Markdown文件名（不含扩展名）
- 文档内容为转换后的Markdown内容

**示例**：
```bash
# 转换示例文档
python markdown_to_feishu_doc.py ../docs/examples/simple_test.md

# 输出：
# 🎉 转换完成!
# 📄 文档标题: simple_test
# 🆔 文档ID: F4SOdIaNzoawv7xGpHCc3e7Cnye
# 💡 请在飞书中查看生成的文档
```

**支持的Markdown语法**：
- ✅ 标题（1-6级）
- ✅ 粗体、斜体文本
- ✅ 有序和无序列表
- ✅ 代码块
- ✅ 引用
- ✅ 链接
- ✅ 简单表格
- ⚠️ 复杂表格可能需要调整

**注意事项**：
- 确保Markdown文件编码为UTF-8
- 文件名将作为飞书文档标题，避免使用特殊字符
- 复杂的Markdown语法可能需要简化后使用

## 快速开始

1. **配置环境**：
   ```bash
   cd /Users/orange/code/feishu
   pip install -r requirements.txt
   ```

2. **测试应用**：
   ```bash
   python apps/markdown_to_feishu_doc.py docs/examples/simple_test.md
   ```

3. **查看结果**：
   在飞书中找到新创建的文档

## 开发新应用

如果你想基于现有的核心工具开发新应用：

1. **导入核心模块**：
   ```python
   from src.core.document_creator import DocumentCreator
   from src.core.markdown_converter import MarkdownConverter
   from src.core.content_inserter import ContentInserter
   from src.utils.config import get_default_config
   ```

2. **参考现有应用**：
   查看 `markdown_to_feishu_doc.py` 的实现

3. **遵循命名规范**：
   - 应用文件名使用下划线分隔
   - 类名使用驼峰命名
   - 函数名使用下划线分隔

## 故障排除

**常见问题**：

1. **"配置不完整"错误**：
   - 检查 `src/utils/config.py` 中的配置
   - 确保访问令牌有效

2. **"文件不存在"错误**：
   - 检查文件路径是否正确
   - 使用绝对路径或相对路径

3. **"内容插入失败"错误**：
   - 可能是Markdown格式过于复杂
   - 尝试简化Markdown内容

4. **访问权限问题**：
   - 确保应用有足够的飞书权限
   - 检查访问令牌是否有效

**获取帮助**：
- 查看 `../docs/api_notes.md` 了解API特性
- 运行应用时加上 `--help` 参数查看使用说明