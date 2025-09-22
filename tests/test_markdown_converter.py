#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Markdown转换模块单元测试
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os
import tempfile

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.markdown_converter import MarkdownConverter


class TestMarkdownConverter(unittest.TestCase):
    """Markdown转换器测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.test_token = "test_token_123"
        self.converter = MarkdownConverter(self.test_token)
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.converter.user_access_token, self.test_token)
        self.assertIsNotNone(self.converter.client)
    
    @patch('core.markdown_converter.lark.Client')
    def test_convert_text_to_blocks_success(self, mock_client_class):
        """测试成功转换文本为块"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.success.return_value = True
        mock_response.data.first_level_block_ids = ["block1", "block2"]
        mock_response.data.blocks = [Mock(), Mock()]
        
        mock_client = Mock()
        mock_client.docx.v1.document.convert.return_value = mock_response
        mock_client_class.builder.return_value.enable_set_token.return_value.log_level.return_value.build.return_value = mock_client
        
        # 重新创建实例以使用模拟的客户端
        converter = MarkdownConverter(self.test_token)
        result = converter.convert_text_to_blocks("# 测试标题")
        
        self.assertIsNotNone(result)
        self.assertIn('first_level_block_ids', result)
        self.assertIn('blocks', result)
    
    @patch('core.markdown_converter.lark.Client')
    def test_convert_text_to_blocks_failure(self, mock_client_class):
        """测试转换失败"""
        # 模拟失败响应
        mock_response = Mock()
        mock_response.success.return_value = False
        mock_response.code = 400
        mock_response.msg = "Invalid content"
        
        mock_client = Mock()
        mock_client.docx.v1.document.convert.return_value = mock_response
        mock_client_class.builder.return_value.enable_set_token.return_value.log_level.return_value.build.return_value = mock_client
        
        # 重新创建实例以使用模拟的客户端
        converter = MarkdownConverter(self.test_token)
        result = converter.convert_text_to_blocks("# 测试标题")
        
        self.assertIsNone(result)
    
    def test_convert_file_to_blocks_file_not_exists(self):
        """测试文件不存在的情况"""
        result = self.converter.convert_file_to_blocks("non_existent_file.md")
        self.assertIsNone(result)
    
    @patch('core.markdown_converter.MarkdownConverter.convert_text_to_blocks')
    def test_convert_file_to_blocks_success(self, mock_convert_text):
        """测试成功从文件转换"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# 测试文档\n\n这是测试内容。")
            temp_file = f.name
        
        try:
            # 模拟转换成功
            mock_convert_text.return_value = {
                'first_level_block_ids': ['block1'],
                'blocks': [Mock()]
            }
            
            result = self.converter.convert_file_to_blocks(temp_file)
            
            self.assertIsNotNone(result)
            mock_convert_text.assert_called_once()
        finally:
            # 清理临时文件
            os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()