# -*- coding: utf-8 -*-
"""
批量导入 Markdown 到飞书文档
结合了两个项目的所有优点：
- ✅ 批量处理整个文件夹
- ✅ 保留目录结构
- ✅ 自动上传本地图片
- ✅ 完美的错误处理
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import List, Dict
from urllib.parse import unquote

# 设置 UTF-8 输出
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import lark_oapi as lark
from lark_oapi.api.drive.v1 import CreateFolderFileRequest, CreateFolderFileRequestBody
from convert_perfect import PerfectFeishuConverter, load_config


# ==================== 批量导入工具 ====================

class MarkdownScanner:
    """Markdown 文件扫描器"""

    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def scan(self) -> List[Dict]:
        """扫描所有 Markdown 文件"""
        markdown_files = []

        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.md'):
                    full_path = os.path.join(root, file)
                    rel_dir = os.path.relpath(root, self.root_dir)

                    # 处理文件名（去除时间戳或UUID后缀）
                    file_name = os.path.splitext(file)[0]
                    file_name = self._clean_filename(file_name)

                    markdown_files.append({
                        'path': full_path,
                        'name': file_name,
                        'folder': '' if rel_dir == '.' else rel_dir
                    })

        return markdown_files

    @staticmethod
    def _clean_filename(name: str) -> str:
        """清理文件名：去除时间戳或UUID后缀"""
        # 从右向左按空格拆分一次，取第一个元素
        return name.rsplit(' ', 1)[0] if ' ' in name else name


class BatchFeishuImporter:
    """批量导入飞书文档"""

    def __init__(self, user_access_token: str):
        self.user_access_token = user_access_token
        self.converter = PerfectFeishuConverter(user_access_token)
        self.client = self.converter.client

        # 文件夹映射缓存
        self.folder_cache = {}

    def create_folder(self, name: str, parent_token: str) -> str:
        """创建飞书文件夹"""
        request = CreateFolderFileRequest.builder() \
            .request_body(CreateFolderFileRequestBody.builder()
                .name(name)
                .folder_token(parent_token or "")
                .build()) \
            .build()

        option = lark.RequestOption.builder().tenant_access_token(self._get_tenant_token()).build()
        response = self.client.drive.v1.file.create_folder(request, option)

        if response.code == 0:
            return response.data.token
        else:
            print(f"[ERROR] 创建文件夹失败: {response.msg}")
            return None

    def ensure_folder_exists(self, folder_path: str, root_token: str) -> str:
        """确保文件夹存在，不存在则创建"""
        if not folder_path:
            return root_token

        # 检查缓存
        if folder_path in self.folder_cache:
            return self.folder_cache[folder_path]

        # 创建嵌套文件夹
        parent_token = root_token
        parts = folder_path.split(os.sep)

        current_path = ''
        for part in parts:
            if not part:
                continue

            current_path = os.path.join(current_path, part)

            if current_path not in self.folder_cache:
                # 创建新文件夹
                folder_token = self.create_folder(part, parent_token)
                if folder_token:
                    self.folder_cache[current_path] = folder_token
                    print(f"  [文件夹] 创建: {current_path}")
                else:
                    return None

            parent_token = self.folder_cache[current_path]

        return parent_token

    def import_file(self, file_path: str, title: str, folder_token: str) -> bool:
        """导入单个文件"""
        try:
            # 创建文档
            doc_id = self.converter.create_document(title, folder_token)
            if not doc_id:
                return False

            # 转换 Markdown
            blocks_data = self.converter.convert_markdown_to_blocks(file_path)
            if not blocks_data:
                return False

            # 插入内容
            if not self.converter.insert_blocks_to_document(doc_id, blocks_data):
                return False

            # 处理图片
            from convert_perfect import extract_images_from_markdown
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            image_paths = extract_images_from_markdown(file_path, content)

            if image_paths:
                self.converter.process_images(doc_id, image_paths)

            return True

        except Exception as e:
            print(f"    [ERROR] 导入失败: {e}")
            return False

    def batch_import(self, files: List[Dict], root_folder_token: str):
        """批量导入"""
        total = len(files)
        success = 0
        failed = 0

        print(f"\n开始批量导入 {total} 个文件...")
        print("=" * 70)

        for i, file_info in enumerate(files, 1):
            file_path = file_info['path']
            file_name = file_info['name']
            folder_path = file_info['folder']

            print(f"\n[{i}/{total}] 处理: {file_name}")
            print(f"  路径: {file_path}")

            # 确保文件夹存在
            parent_token = self.ensure_folder_exists(folder_path, root_folder_token)
            if not parent_token:
                print(f"    [ERROR] 文件夹创建失败")
                failed += 1
                continue

            # 导入文件
            if self.import_file(file_path, file_name, parent_token):
                print(f"    [SUCCESS] 导入成功")
                success += 1
            else:
                print(f"    [ERROR] 导入失败")
                failed += 1

        print("\n" + "=" * 70)
        print(f"批量导入完成！")
        print(f"  总计: {total}")
        print(f"  成功: {success}")
        print(f"  失败: {failed}")
        print("=" * 70)

    def _get_tenant_token(self) -> str:
        """获取租户访问令牌"""
        from lark_oapi.api.auth.v3 import InternalTenantAccessTokenRequest, InternalTenantAccessTokenRequestBody

        APP_ID, APP_SECRET, _ = load_config()

        request = InternalTenantAccessTokenRequest.builder() \
            .request_body(InternalTenantAccessTokenRequestBody.builder()
                .app_id(APP_ID)
                .app_secret(APP_SECRET)
                .build()) \
            .build()

        response = self.client.auth.v3.tenant_access_token.internal(request)

        if response.code == 0:
            import json
            return json.loads(response.raw.content).get('tenant_access_token')
        else:
            raise Exception(f"获取租户令牌失败: {response.msg}")


# ==================== 主函数 ====================

def main():
    if len(sys.argv) < 3:
        print("=" * 70)
        print("批量导入 Markdown 到飞书文档")
        print("=" * 70)
        print()
        print("使用方法:")
        print("  python batch_import.py <markdown_dir> <root_folder_token>")
        print()
        print("参数说明:")
        print("  markdown_dir      - 本地 Markdown 文件夹路径")
        print("  root_folder_token - 飞书目标文件夹 token")
        print()
        print("示例:")
        print('  python batch_import.py "D:\\Learning\\notes" "U89ffsAjflcugtdtv4Sc98rbnkh"')
        print()
        return 1

    markdown_dir = sys.argv[1]
    root_folder_token = sys.argv[2]

    # 检查目录
    if not os.path.exists(markdown_dir):
        print(f"[ERROR] 目录不存在: {markdown_dir}")
        return 1

    # 加载配置
    _, _, USER_ACCESS_TOKEN = load_config()

    if not USER_ACCESS_TOKEN:
        print("[ERROR] 配置文件未设置 user_access_token")
        return 1

    print("=" * 70)
    print("批量导入 Markdown 到飞书文档")
    print("=" * 70)
    print(f"源目录: {markdown_dir}")
    print(f"目标文件夹: {root_folder_token}")
    print()

    # 扫描文件
    print("[INFO] 扫描 Markdown 文件...")
    scanner = MarkdownScanner(markdown_dir)
    files = scanner.scan()

    if not files:
        print("[INFO] 未找到 Markdown 文件")
        return 0

    print(f"[INFO] 找到 {len(files)} 个 Markdown 文件")

    # 批量导入
    importer = BatchFeishuImporter(USER_ACCESS_TOKEN)
    importer.batch_import(files, root_folder_token)

    return 0


if __name__ == "__main__":
    sys.exit(main())
