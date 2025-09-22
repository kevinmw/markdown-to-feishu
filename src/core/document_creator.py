#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
飞书文档创建模块
提供创建新文档的功能
"""

import lark_oapi as lark
from lark_oapi.api.docx.v1 import *
from typing import Optional


class DocumentCreator:
    """飞书文档创建器"""
    
    def __init__(self, user_access_token: str):
        """
        初始化文档创建器
        
        Args:
            user_access_token: 用户访问令牌
        """
        self.user_access_token = user_access_token
        self.client = lark.Client.builder() \
            .enable_set_token(True) \
            .log_level(lark.LogLevel.INFO) \
            .build()
    
    def create_document(self, title: str, folder_token: Optional[str] = None) -> Optional[str]:
        """
        创建新的飞书文档
        
        Args:
            title: 文档标题
            folder_token: 文件夹token，为空则在根目录创建
            
        Returns:
            创建成功返回document_id，失败返回None
        """
        try:
            # 构造请求对象
            request_body = CreateDocumentRequestBody.builder().title(title)
            
            if folder_token:
                request_body = request_body.folder_token(folder_token)
                
            request = CreateDocumentRequest.builder() \
                .request_body(request_body.build()) \
                .build()

            # 发起请求
            option = lark.RequestOption.builder().user_access_token(self.user_access_token).build()
            response = self.client.docx.v1.document.create(request, option)

            # 处理结果
            if response.success():
                document_id = response.data.document.document_id
                print(f"文档创建成功: {title}")
                print(f"Document ID: {document_id}")
                return document_id
            else:
                print(f"文档创建失败: {response.msg}")
                return None
                
        except Exception as e:
            print(f"创建文档时发生错误: {e}")
            return None


# 便捷函数
def create_document(title: str, user_access_token: str, folder_token: Optional[str] = None) -> Optional[str]:
    """
    便捷函数：创建文档
    
    Args:
        title: 文档标题
        user_access_token: 用户访问令牌
        folder_token: 文件夹token
        
    Returns:
        文档ID或None
    """
    creator = DocumentCreator(user_access_token)
    return creator.create_document(title, folder_token)


if __name__ == "__main__":
    # 测试代码
    from ..utils.config import get_default_config
    config = get_default_config()
    token = config.get_access_token()
    doc_id = create_document("测试文档创建模块", token)
    if doc_id:
        print(f"测试成功，文档ID: {doc_id}")
    else:
        print("测试失败")