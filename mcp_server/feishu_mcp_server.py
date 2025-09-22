#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
飞书MCP服务器

该MCP服务器将现有的飞书应用功能暴露为MCP工具，包括：
1. 创建飞书文档
2. 将Markdown内容转换为飞书文档块
3. 插入内容到飞书文档
4. 完整的Markdown文件转换为飞书文档

使用方法：
    python feishu_mcp_server.py

然后在Claude Desktop配置中添加此MCP服务器
"""

import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from mcp.server.fastmcp import FastMCP
from mcp import types

# 导入我们的核心模块
from src.core.document_creator import DocumentCreator
from src.core.markdown_converter import MarkdownConverter
from src.core.content_inserter import ContentInserter
from src.utils.config import FeishuConfig


class FeishuMCPServer:
    """飞书MCP服务器类"""
    
    def __init__(self):
        """初始化MCP服务器和飞书组件"""
        # 获取配置（从环境变量）
        config = FeishuConfig.from_env()
        if not config.validate():
            raise ValueError("飞书配置无效，请检查环境变量：FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_USER_ACCESS_TOKEN")
        
        self.user_token = config.get_access_token()
        
        # 初始化核心组件
        self.creator = DocumentCreator(self.user_token)
        self.converter = MarkdownConverter(self.user_token)
        self.inserter = ContentInserter(self.user_token)


# 创建MCP服务器实例
mcp = FastMCP("Feishu MCP Server")
feishu_server = FeishuMCPServer()


# @mcp.tool()
def create_feishu_document(title: str, folder_token: Optional[str] = None) -> Dict[str, Any]:
    """
    创建一个新的飞书文档
    
    Args:
        title: 文档标题
        folder_token: 可选的文件夹token，如果不提供则创建在默认位置
    
    Returns:
        包含文档ID和标题的字典
    """
    try:
        document_id = feishu_server.creator.create_document(title, folder_token)
        if document_id:
            return {
                "success": True,
                "document_id": document_id,
                "title": title,
                "message": f"成功创建文档: {title}"
            }
        else:
            return {
                "success": False,
                "error": "文档创建失败"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"创建文档时出错: {str(e)}"
        }


# @mcp.tool()
def convert_markdown_to_blocks(markdown_text: str) -> Dict[str, Any]:
    """
    将Markdown文本转换为飞书文档块
    
    Args:
        markdown_text: 要转换的Markdown文本内容
    
    Returns:
        包含转换结果的字典
    """
    try:
        blocks_data = feishu_server.converter.convert_text_to_blocks(markdown_text)
        if blocks_data:
            block_count = len(blocks_data.get('blocks', []))
            return {
                "success": True,
                "block_count": block_count,
                "message": f"成功转换为 {block_count} 个内容块"
            }
        else:
            return {
                "success": False,
                "error": "Markdown转换失败"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"转换Markdown时出错: {str(e)}"
        }


# @mcp.tool()
def insert_content_to_document(document_id: str, markdown_text: str) -> Dict[str, Any]:
    """
    将Markdown内容转换并插入到飞书文档中
    
    Args:
        document_id: 目标文档的ID
        markdown_text: 要插入的Markdown文本内容
    
    Returns:
        插入结果的字典
    """
    try:
        # 首先转换Markdown为blocks
        blocks_data = feishu_server.converter.convert_text_to_blocks(markdown_text)
        if not blocks_data:
            return {
                "success": False,
                "error": "Markdown转换失败"
            }
        
        # 然后插入到文档
        success = feishu_server.inserter.insert_blocks_to_document(document_id, blocks_data)
        if success:
            block_count = len(blocks_data.get('blocks', []))
            return {
                "success": True,
                "document_id": document_id,
                "block_count": block_count,
                "message": f"成功插入 {block_count} 个内容块"
            }
        else:
            return {
                "success": False,
                "error": "内容插入失败"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"插入内容时出错: {str(e)}"
        }


@mcp.tool()
def convert_markdown_file_to_feishu_document(
    markdown_file_path: str, 
    document_title: str,
    folder_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    完整的工作流：将Markdown文件转换为飞书文档
    
    这是一个高级工具，执行完整的转换流程：
    1. 创建新的飞书文档
    2. 读取并转换Markdown文件
    3. 将转换后的内容插入到文档中
    
    Args:
        markdown_file_path: Markdown文件的路径
        document_title: 新建文档的标题
        folder_token: 可选的文件夹token
    
    Returns:
        完整操作结果的字典
    """
    try:
        # 1. 验证文件存在
        if not os.path.exists(markdown_file_path):
            return {
                "success": False,
                "error": f"文件不存在: {markdown_file_path}"
            }
        
        # 2. 创建文档
        document_id = feishu_server.creator.create_document(document_title, folder_token)
        if not document_id:
            return {
                "success": False,
                "error": "文档创建失败"
            }
        
        # 3. 转换Markdown文件
        blocks_data = feishu_server.converter.convert_file_to_blocks(markdown_file_path)
        if not blocks_data:
            return {
                "success": False,
                "error": "Markdown转换失败",
                "document_id": document_id
            }
        
        # 4. 插入内容
        insert_success = feishu_server.inserter.insert_blocks_to_document(document_id, blocks_data)
        if not insert_success:
            return {
                "success": False,
                "error": "内容插入失败",
                "document_id": document_id
            }
        
        # 5. 返回成功结果
        block_count = len(blocks_data.get('blocks', []))
        return {
            "success": True,
            "document_id": document_id,
            "document_title": document_title,
            "markdown_file": markdown_file_path,
            "block_count": block_count,
            "message": f"成功将 {os.path.basename(markdown_file_path)} 转换为飞书文档 '{document_title}'，包含 {block_count} 个内容块"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"转换过程中出错: {str(e)}"
        }


@mcp.tool()
def create_feishu_document_from_markdown(
    markdown_text: str,
    document_title: str,
    folder_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    一键工具：直接将Markdown文本转换为飞书文档
    
    这是一个高级便捷工具，执行完整的工作流程：
    1. 创建新的飞书文档
    2. 将Markdown文本转换为飞书文档块
    3. 将转换后的内容插入到文档中
    
    Args:
        markdown_text: 要转换的Markdown文本内容
        document_title: 新建文档的标题
        folder_token: 可选的文件夹token
    
    Returns:
        完整操作结果的字典
    """
    try:
        # 1. 创建文档
        document_id = feishu_server.creator.create_document(document_title, folder_token)
        if not document_id:
            return {
                "success": False,
                "error": "文档创建失败"
            }
        
        # 2. 转换Markdown文本
        try:
            blocks_data = feishu_server.converter.convert_text_to_blocks(markdown_text)
            if not blocks_data:
                return {
                    "success": False,
                    "error": "Markdown转换失败",
                    "document_id": document_id
                }
        except Exception as convert_error:
            return {
                "success": False,
                "error": f"Markdown转换时出错: {str(convert_error)}",
                "document_id": document_id
            }
        
        # 3. 插入内容
        try:
            insert_success = feishu_server.inserter.insert_blocks_to_document(document_id, blocks_data)
            if not insert_success:
                return {
                    "success": False,
                    "error": "内容插入失败",
                    "document_id": document_id
                }
        except Exception as insert_error:
            return {
                "success": False,
                "error": f"内容插入时出错: {str(insert_error)}",
                "document_id": document_id
            }
        
        # 4. 返回成功结果
        block_count = len(blocks_data.get('blocks', []))
        return {
            "success": True,
            "document_id": document_id,
            "document_title": document_title,
            "block_count": block_count,
            "message": f"成功将Markdown文本转换为飞书文档 '{document_title}'，包含 {block_count} 个内容块"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"转换过程中出错: {str(e)}"
        }


# @mcp.tool()
def get_feishu_config_info() -> Dict[str, Any]:
    """
    获取当前飞书配置信息（不包含敏感数据）
    
    Returns:
        配置状态信息
    """
    try:
        config = FeishuConfig.from_env()
        return {
            "config_valid": config.validate(),
            "has_app_id": bool(config.app_id),
            "has_app_secret": bool(config.app_secret),
            "has_user_token": bool(config.user_access_token),
            "has_tenant_token": bool(config.tenant_access_token),
            "message": "配置检查完成"
        }
    except Exception as e:
        return {
            "config_valid": False,
            "error": f"配置检查出错: {str(e)}"
        }


if __name__ == "__main__":
    # 运行MCP服务器
    print("🚀 启动飞书MCP服务器...")
    print("📝 可用工具 (仅限两个核心功能):")
    print("  1️⃣ convert_markdown_file_to_feishu_document: 从Markdown文件创建飞书文档")
    print("  2️⃣ create_feishu_document_from_markdown: 从Markdown文本创建飞书文档")
    print()
    print("✨ 简化设计：只暴露两个最核心的工具，提供完整的Markdown转飞书文档功能！")
    print()
    
    mcp.run()