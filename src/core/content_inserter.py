#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
内容插入模块
提供向飞书文档插入内容块的功能
"""

import lark_oapi as lark
from lark_oapi.api.docx.v1 import *
from typing import Optional, Dict, Any, List


class ContentInserter:
    """内容插入器"""
    
    def __init__(self, user_access_token: str):
        """
        初始化内容插入器
        
        Args:
            user_access_token: 用户访问令牌
        """
        self.user_access_token = user_access_token
        self.client = lark.Client.builder() \
            .enable_set_token(True) \
            .log_level(lark.LogLevel.INFO) \
            .build()
    
    def insert_blocks_to_document(self, document_id: str, blocks_data: Dict[str, Any], 
                                  parent_block_id: Optional[str] = None, 
                                  index: int = 0) -> bool:
        """
        将块数据插入到文档中
        
        Args:
            document_id: 目标文档ID
            blocks_data: 从markdown_converter获得的块数据
            parent_block_id: 父块ID，为None时使用document_id作为根级插入
            index: 插入位置索引
            
        Returns:
            插入成功返回True，失败返回False
        """
        try:
            # 如果没有指定父块ID，则插入到文档根级别
            if parent_block_id is None:
                parent_block_id = document_id
            
            blocks = blocks_data.get("blocks", [])
            first_level_block_ids = blocks_data.get("first_level_block_ids", [])
            
            if not blocks:
                print("警告：没有要插入的块数据")
                return False
            
            # 过滤表格块中的merge_info字段，避免API报错
            blocks = self._filter_table_merge_info(blocks)
            
            print(f"准备插入 {len(blocks)} 个块到文档 {document_id}")
            
            # 构造请求对象
            request = CreateDocumentBlockDescendantRequest.builder() \
                .document_id(document_id) \
                .block_id(parent_block_id) \
                .document_revision_id(-1) \
                .request_body(CreateDocumentBlockDescendantRequestBody.builder()
                    .children_id(first_level_block_ids)
                    .index(index)
                    .descendants(blocks)
                    .build()) \
                .build()

            # 发起请求
            option = lark.RequestOption.builder().user_access_token(self.user_access_token).build()
            response = self.client.docx.v1.document_block_descendant.create(request, option)

            # 处理结果
            if response.success():
                print("内容插入成功")
                print(f"文档版本更新为: {response.data.document_revision_id}")
                return True
            else:
                print(f"内容插入失败: {response.msg}")
                return False
                
        except Exception as e:
            print(f"插入内容时发生错误: {e}")
            return False
    
    def insert_simple_table(self, document_id: str, title: str = "简单表格", 
                           parent_block_id: Optional[str] = None) -> bool:
        """
        插入一个简单的表格示例
        
        Args:
            document_id: 目标文档ID
            title: 表格标题
            parent_block_id: 父块ID
            
        Returns:
            插入成功返回True，失败返回False
        """
        try:
            if parent_block_id is None:
                parent_block_id = document_id
                
            # 构造表格块数据
            request = CreateDocumentBlockDescendantRequest.builder() \
                .document_id(document_id) \
                .block_id(parent_block_id) \
                .document_revision_id(-1) \
                .request_body(CreateDocumentBlockDescendantRequestBody.builder()
                    .children_id(["headingid_1", "table_id_1"])
                    .index(0)
                    .descendants([
                        Block.builder()
                        .block_id("headingid_1")
                        .children([])
                        .block_type(3)
                        .heading1(Text.builder()
                            .elements([TextElement.builder()
                                .text_run(TextRun.builder()
                                    .content(title)
                                    .build())
                                .build()])
                            .build())
                        .build(),
                        Block.builder()
                        .block_id("table_id_1")
                        .children(["table_cell1", "table_cell2"])
                        .block_type(31)
                        .table(Table.builder()
                            .property(TableProperty.builder()
                                .row_size(1)
                                .column_size(2)
                                .build())
                            .build())
                        .build(),
                        Block.builder()
                        .block_id("table_cell1")
                        .children(["table_cell1_child"])
                        .block_type(32)
                        .table_cell(TableCell.builder().build())
                        .build(),
                        Block.builder()
                        .block_id("table_cell2")
                        .children(["table_cell2_child"])
                        .block_type(32)
                        .table_cell(TableCell.builder().build())
                        .build(),
                        Block.builder()
                        .block_id("table_cell1_child")
                        .children([])
                        .block_type(2)
                        .text(Text.builder()
                            .elements([TextElement.builder()
                                .text_run(TextRun.builder()
                                    .content("表格第一列")
                                    .build())
                                .build()])
                            .build())
                        .build(),
                        Block.builder()
                        .block_id("table_cell2_child")
                        .children([])
                        .block_type(2)
                        .text(Text.builder()
                            .elements([TextElement.builder()
                                .text_run(TextRun.builder()
                                    .content("表格第二列")
                                    .build())
                                .build()])
                            .build())
                        .build()
                    ])
                    .build()) \
                .build()

            # 发起请求
            option = lark.RequestOption.builder().user_access_token(self.user_access_token).build()
            response = self.client.docx.v1.document_block_descendant.create(request, option)

            # 处理结果
            if response.success():
                print(f"表格 '{title}' 插入成功")
                return True
            else:
                print(f"表格插入失败: {response.msg}")
                return False
                
        except Exception as e:
            print(f"插入表格时发生错误: {e}")
            return False
    
    def _filter_table_merge_info(self, blocks):
        """
        过滤表格块中的merge_info字段
        
        根据飞书官方文档说明，表格块中的merge_info字段为只读属性，
        在批量插入时传入该字段会引发报错，需要先移除。
        
        Args:
            blocks: 原始块列表
            
        Returns:
            过滤后的块列表
        """
        if not blocks:
            return blocks
        
        filtered_blocks = []
        for block in blocks:
            try:
                # 检查是否为表格块 (block_type: 31)
                if hasattr(block, 'block_type') and block.block_type == 31:
                    # 是表格块，需要处理merge_info
                    if hasattr(block, 'table') and hasattr(block.table, 'property') and hasattr(block.table.property, 'merge_info'):
                        print(f"检测到表格块包含merge_info字段，正在移除...")
                        # 由于SDK对象的复杂性，我们通过重新构造表格块来移除merge_info
                        # 这里需要导入相关的类
                        from lark_oapi.api.docx.v1.model.block import Block
                        from lark_oapi.api.docx.v1.model.table import Table  
                        from lark_oapi.api.docx.v1.model.table_property import TableProperty
                        
                        # 创建新的table property，不包含merge_info
                        new_property = TableProperty.builder() \
                            .row_size(block.table.property.row_size) \
                            .column_size(block.table.property.column_size)
                        
                        # 如果有column_width，也复制过来
                        if hasattr(block.table.property, 'column_width') and block.table.property.column_width:
                            new_property = new_property.column_width(block.table.property.column_width)
                        
                        # 如果有header_row，也复制过来
                        if hasattr(block.table.property, 'header_row'):
                            new_property = new_property.header_row(block.table.property.header_row)
                        
                        # 如果有header_column，也复制过来  
                        if hasattr(block.table.property, 'header_column'):
                            new_property = new_property.header_column(block.table.property.header_column)
                        
                        new_property = new_property.build()
                        
                        # 创建新的table对象
                        new_table = Table.builder() \
                            .property(new_property)
                        
                        # 如果有cells，也复制过来
                        if hasattr(block.table, 'cells') and block.table.cells:
                            new_table = new_table.cells(block.table.cells)
                        
                        new_table = new_table.build()
                        
                        # 创建新的block对象
                        new_block = Block.builder() \
                            .block_type(block.block_type) \
                            .table(new_table)
                        
                        # 复制其他属性
                        if hasattr(block, 'block_id') and block.block_id:
                            new_block = new_block.block_id(block.block_id)
                        
                        if hasattr(block, 'children') and block.children:
                            new_block = new_block.children(block.children)
                        
                        if hasattr(block, 'parent_id') and block.parent_id:
                            new_block = new_block.parent_id(block.parent_id)
                        
                        filtered_blocks.append(new_block.build())
                        print("表格块merge_info字段移除成功")
                    else:
                        # 表格块但没有merge_info，直接添加
                        filtered_blocks.append(block)
                else:
                    # 非表格块，直接添加
                    filtered_blocks.append(block)
            except Exception as e:
                print(f"过滤表格块时出错: {e}，保留原块")
                filtered_blocks.append(block)
        
        return filtered_blocks


# 便捷函数
def insert_markdown_blocks(document_id: str, blocks_data: Dict[str, Any], 
                          user_access_token: str) -> bool:
    """
    便捷函数：插入Markdown转换后的块
    
    Args:
        document_id: 文档ID
        blocks_data: Markdown转换结果
        user_access_token: 用户访问令牌
        
    Returns:
        插入成功返回True，失败返回False
    """
    inserter = ContentInserter(user_access_token)
    return inserter.insert_blocks_to_document(document_id, blocks_data)


def insert_table(document_id: str, title: str, user_access_token: str) -> bool:
    """
    便捷函数：插入简单表格
    
    Args:
        document_id: 文档ID
        title: 表格标题
        user_access_token: 用户访问令牌
        
    Returns:
        插入成功返回True，失败返回False
    """
    inserter = ContentInserter(user_access_token)
    return inserter.insert_simple_table(document_id, title)


if __name__ == "__main__":
    # 测试代码
    from ..utils.config import get_default_config
    config = get_default_config()
    token = config.get_access_token()
    test_doc_id = "V5HQdxo30ocXwNxT20KcJ20jn6b"
    
    success = insert_table(test_doc_id, "测试插入模块", token)
    if success:
        print("测试成功")
    else:
        print("测试失败")