#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文档创建模块单元测试
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.document_creator import DocumentCreator


class TestDocumentCreator(unittest.TestCase):
    """文档创建器测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.test_token = "test_token_123"
        self.creator = DocumentCreator(self.test_token)
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.creator.user_access_token, self.test_token)
        self.assertIsNotNone(self.creator.client)
    
    @patch('core.document_creator.lark.Client')
    def test_create_document_success(self, mock_client_class):
        """测试成功创建文档"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.success.return_value = True
        mock_response.data.document.document_id = "test_doc_id_123"
        
        mock_client = Mock()
        mock_client.docx.v1.document.create.return_value = mock_response
        mock_client_class.builder.return_value.enable_set_token.return_value.log_level.return_value.build.return_value = mock_client
        
        # 重新创建实例以使用模拟的客户端
        creator = DocumentCreator(self.test_token)
        result = creator.create_document("测试文档")
        
        self.assertEqual(result, "test_doc_id_123")
    
    @patch('core.document_creator.lark.Client')
    def test_create_document_failure(self, mock_client_class):
        """测试创建文档失败"""
        # 模拟失败响应
        mock_response = Mock()
        mock_response.success.return_value = False
        mock_response.code = 400
        mock_response.msg = "Bad Request"
        
        mock_client = Mock()
        mock_client.docx.v1.document.create.return_value = mock_response
        mock_client_class.builder.return_value.enable_set_token.return_value.log_level.return_value.build.return_value = mock_client
        
        # 重新创建实例以使用模拟的客户端
        creator = DocumentCreator(self.test_token)
        result = creator.create_document("测试文档")
        
        self.assertIsNone(result)
    
    def test_create_document_with_folder_token(self):
        """测试使用文件夹令牌创建文档"""
        # 这里可以添加更多具体的测试逻辑
        pass


if __name__ == '__main__':
    unittest.main()