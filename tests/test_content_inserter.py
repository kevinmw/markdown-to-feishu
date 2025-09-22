#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
内容插入模块单元测试
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.content_inserter import ContentInserter


class TestContentInserter(unittest.TestCase):
    """内容插入器测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.test_token = "test_token_123"
        self.inserter = ContentInserter(self.test_token)
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.inserter.user_access_token, self.test_token)
        self.assertIsNotNone(self.inserter.client)
    
    @patch('core.content_inserter.lark.Client')
    def test_insert_blocks_to_document_success(self, mock_client_class):
        """测试成功插入内容块"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.success.return_value = True
        mock_response.data.document_revision_id = 2
        
        mock_client = Mock()
        mock_client.docx.v1.document_block_descendant.create.return_value = mock_response
        mock_client_class.builder.return_value.enable_set_token.return_value.log_level.return_value.build.return_value = mock_client
        
        # 重新创建实例以使用模拟的客户端
        inserter = ContentInserter(self.test_token)
        
        # 模拟块数据
        blocks_data = {
            'first_level_block_ids': ['block1', 'block2'],
            'blocks': [Mock(), Mock()]
        }
        
        result = inserter.insert_blocks_to_document("test_doc_id", blocks_data)
        
        self.assertTrue(result)
    
    @patch('core.content_inserter.lark.Client')
    def test_insert_blocks_to_document_failure(self, mock_client_class):
        """测试插入内容块失败"""
        # 模拟失败响应
        mock_response = Mock()
        mock_response.success.return_value = False
        mock_response.code = 400
        mock_response.msg = "Invalid document"
        
        mock_client = Mock()
        mock_client.docx.v1.document_block_descendant.create.return_value = mock_response
        mock_client_class.builder.return_value.enable_set_token.return_value.log_level.return_value.build.return_value = mock_client
        
        # 重新创建实例以使用模拟的客户端
        inserter = ContentInserter(self.test_token)
        
        # 模拟块数据
        blocks_data = {
            'first_level_block_ids': ['block1'],
            'blocks': [Mock()]
        }
        
        result = inserter.insert_blocks_to_document("test_doc_id", blocks_data)
        
        self.assertFalse(result)
    
    def test_insert_blocks_invalid_data(self):
        """测试无效数据输入"""
        # 测试空数据
        result = self.inserter.insert_blocks_to_document("test_doc_id", {})
        self.assertFalse(result)
        
        # 测试None数据
        result = self.inserter.insert_blocks_to_document("test_doc_id", None)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()