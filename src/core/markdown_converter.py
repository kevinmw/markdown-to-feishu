#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Markdown转换模块
提供将Markdown文件转换为飞书文档块的功能
"""

import os
import lark_oapi as lark
from lark_oapi.api.docx.v1 import *
from typing import Optional, Dict, Any


class MarkdownConverter:
    """Markdown转换器"""
    
    def __init__(self, user_access_token: str):
        """
        初始化Markdown转换器
        
        Args:
            user_access_token: 用户访问令牌
        """
        self.user_access_token = user_access_token
        self.client = lark.Client.builder() \
            .enable_set_token(True) \
            .log_level(lark.LogLevel.INFO) \
            .build()
    
    def convert_file_to_blocks(self, markdown_file_path: str) -> Optional[Dict[str, Any]]:
        """
        将Markdown文件转换为飞书文档块
        
        Args:
            markdown_file_path: Markdown文件路径
            
        Returns:
            转换结果包含blocks信息，失败返回None
        """
        # 检查文件是否存在
        if not os.path.exists(markdown_file_path):
            print(f"错误：文件 {markdown_file_path} 不存在")
            return None
        
        try:
            # 读取文件内容
            with open(markdown_file_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            return self.convert_text_to_blocks(markdown_content)
            
        except Exception as e:
            print(f"读取文件失败: {e}")
            return None
    
    def convert_text_to_blocks(self, markdown_content: str) -> Optional[Dict[str, Any]]:
        """
        将Markdown文本转换为飞书文档块
        
        Args:
            markdown_content: Markdown文本内容
            
        Returns:
            转换结果包含blocks信息，失败返回None
        """
        try:
            print(f"开始转换Markdown内容，长度: {len(markdown_content)} 字符")
            
            # 构造请求对象
            request = ConvertDocumentRequest.builder() \
                .request_body(ConvertDocumentRequestBody.builder()
                    .content_type("markdown")
                    .content(markdown_content)
                    .build()) \
                .build()

            # 发起请求
            option = lark.RequestOption.builder().user_access_token(self.user_access_token).build()
            response = self.client.docx.v1.document.convert(request, option)

            # 处理结果
            if response.success():
                print("Markdown转换成功")
                return {
                    "first_level_block_ids": response.data.first_level_block_ids,
                    "blocks": response.data.blocks
                }
            else:
                print(f"Markdown转换失败: {response.msg}")
                return None
                
        except Exception as e:
            print(f"转换Markdown时发生错误: {e}")
            return None


# 便捷函数
def convert_markdown_file(markdown_file_path: str, user_access_token: str) -> Optional[Dict[str, Any]]:
    """
    便捷函数：转换Markdown文件
    
    Args:
        markdown_file_path: Markdown文件路径
        user_access_token: 用户访问令牌
        
    Returns:
        转换结果或None
    """
    converter = MarkdownConverter(user_access_token)
    return converter.convert_file_to_blocks(markdown_file_path)


def convert_markdown_text(markdown_text: str, user_access_token: str) -> Optional[Dict[str, Any]]:
    """
    便捷函数：转换Markdown文本
    
    Args:
        markdown_text: Markdown文本
        user_access_token: 用户访问令牌
        
    Returns:
        转换结果或None
    """
    converter = MarkdownConverter(user_access_token)
    return converter.convert_text_to_blocks(markdown_text)


if __name__ == "__main__":
    # 测试代码
    from ..utils.config import get_default_config
    config = get_default_config()
    token = config.get_access_token()
    
    # 测试文本转换
    test_markdown = """
# 测试标题

这是一个**粗体**和*斜体*的测试。

## 列表测试

1. 第一项
2. 第二项

- 无序列表1
- 无序列表2

```python
def hello():
    print("Hello World")
```
"""
    
    result = convert_markdown_text(test_markdown, token)
    if result:
        print(f"测试成功，转换出 {len(result['blocks'])} 个块")
    else:
        print("测试失败")