#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Markdown转飞书文档应用

功能：
1. 接受Markdown文件路径和文档标题作为参数
2. 创建一个指定标题的飞书文档
3. 将Markdown内容转换为飞书文档块
4. 将转换后的内容插入到新创建的文档中

使用方法：
python markdown_to_feishu_doc.py /path/to/your/file.md "文档标题"
"""

import sys
import os
import argparse
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.document_creator import DocumentCreator
from core.markdown_converter import MarkdownConverter
from core.content_inserter import ContentInserter
from utils.config import get_default_config


class MarkdownToFeishuDocApp:
    """Markdown转飞书文档应用类"""
    
    def __init__(self, user_access_token: str):
        """
        初始化应用
        
        Args:
            user_access_token: 用户访问令牌
        """
        self.token = user_access_token
        self.creator = DocumentCreator(user_access_token)
        self.converter = MarkdownConverter(user_access_token)
        self.inserter = ContentInserter(user_access_token)
        
    def process_markdown_file(self, markdown_file_path: str, document_title: str) -> bool:
        """
        处理Markdown文件，完成完整的转换流程
        
        Args:
            markdown_file_path: Markdown文件路径
            document_title: 飞书文档标题
            
        Returns:
            处理成功返回True，失败返回False
        """
        try:
            # 1. 验证文件存在
            if not os.path.exists(markdown_file_path):
                print(f"❌ 错误：文件 {markdown_file_path} 不存在")
                return False
            
            # 2. 显示处理信息
            file_path = Path(markdown_file_path)
            
            print(f"🚀 开始处理文件: {file_path.name}")
            print(f"📝 文档标题: {document_title}")
            print()
            
            # 3. 创建飞书文档
            print("步骤 1/3: 创建飞书文档...")
            document_id = self.creator.create_document(document_title)
            
            if not document_id:
                print("❌ 文档创建失败")
                return False
            
            print(f"✅ 文档创建成功")
            print(f"📄 文档ID: {document_id}")
            print()
            
            # 4. 转换Markdown内容
            print("步骤 2/3: 转换Markdown内容...")
            blocks_data = self.converter.convert_file_to_blocks(markdown_file_path)
            
            if not blocks_data:
                print("❌ Markdown转换失败")
                return False
            
            block_count = len(blocks_data.get('blocks', []))
            print(f"✅ Markdown转换成功")
            print(f"📊 生成了 {block_count} 个内容块")
            print()
            
            # 5. 插入内容到文档
            print("步骤 3/3: 插入内容到文档...")
            success = self.inserter.insert_blocks_to_document(document_id, blocks_data)
            
            if not success:
                print("❌ 内容插入失败")
                return False
            
            print("✅ 内容插入成功")
            print()
            
            # 6. 完成提示
            print("🎉 转换完成!")
            print(f"📄 文档标题: {document_title}")
            print(f"🆔 文档ID: {document_id}")
            print("💡 请在飞书中查看生成的文档")
            
            return True
            
        except Exception as e:
            print(f"❌ 处理过程中发生错误: {e}")
            return False


def main():
    """主函数"""
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(
        description='将Markdown文件转换为飞书文档',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  python markdown_to_feishu_doc.py report.md "项目报告"
  python markdown_to_feishu_doc.py /path/to/my_document.md "我的文档"
  python markdown_to_feishu_doc.py ../docs/examples/sample.md "示例文档"

注意：
  - 第一个参数是Markdown文件路径
  - 第二个参数是新建飞书文档的标题
  - 需要确保已配置正确的飞书访问令牌
        """
    )
    
    parser.add_argument(
        'markdown_file', 
        help='要转换的Markdown文件路径'
    )
    
    parser.add_argument(
        'document_title', 
        help='新建飞书文档的标题'
    )
    
    parser.add_argument(
        '--token',
        help='用户访问令牌（可选，默认使用配置文件中的令牌）'
    )
    
    args = parser.parse_args()
    
    # 获取访问令牌
    if args.token:
        user_token = args.token
    else:
        config = get_default_config()
        if not config.validate():
            print("❌ 错误：配置不完整")
            print("请检查配置文件或使用 --token 参数指定访问令牌")
            return False
        user_token = config.get_access_token()
    
    # 转换为绝对路径
    markdown_path = os.path.abspath(args.markdown_file)
    
    print("=" * 60)
    print("🔄 Markdown转飞书文档应用")
    print("=" * 60)
    
    # 创建应用实例并处理文件
    app = MarkdownToFeishuDocApp(user_token)
    success = app.process_markdown_file(markdown_path, args.document_title)
    
    print("=" * 60)
    
    if success:
        print("🎯 任务执行成功！")
        return True
    else:
        print("💥 任务执行失败！")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)