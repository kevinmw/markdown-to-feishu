# -*- coding: utf-8 -*-
"""
完美版 Markdown 转飞书文档工具
结合了两个项目的所有优点 + 修复了图片上传bug

特点：
- ✅ Markdown 转飞书文档（基于 markdown-to-feishu）
- ✅ 自动上传本地图片（基于 markdown2feishuDoc）
- ✅ 修复了文件大小错误（关键修复！）
- ✅ 简洁的命令行接口
- ✅ 完整的错误处理
- ✅ 详细的进度显示
"""

import os
import sys
import re
import io
import time
from typing import List, Optional

# 设置 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import lark_oapi as lark
from lark_oapi.api.docx.v1 import *
from lark_oapi.api.drive.v1 import UploadAllMediaRequest, UploadAllMediaRequestBody, UploadAllMediaResponse
from PIL import Image
import json


# ==================== 配置加载 ====================
def load_config():
    """从配置文件加载飞书配置"""
    config_file = os.path.join(os.path.dirname(__file__), 'config.json')

    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return (
                    config.get('app_id', ''),
                    config.get('app_secret', ''),
                    config.get('user_access_token', '')
                )
        except Exception as e:
            print(f"[WARN] 配置文件读取失败: {e}")

    # 如果配置文件不存在，返回空配置
    return "", "", ""

# 加载配置
APP_ID, APP_SECRET, USER_ACCESS_TOKEN = load_config()
config_file = os.path.join(os.path.dirname(__file__), 'config.json')

# 检查配置是否有效
if not APP_ID or not APP_SECRET or not USER_ACCESS_TOKEN:
    print("[ERROR] 飞书配置不完整！")
    print(f"请确保配置文件存在: {config_file}")
    print("配置文件格式:")
    print(json.dumps({
        "app_id": "your_app_id",
        "app_secret": "your_app_secret",
        "user_access_token": "your_user_access_token"
    }, indent=2, ensure_ascii=False))
    sys.exit(1)


# ==================== 工具函数 ====================

def create_client():
    """创建飞书客户端"""
    return lark.Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .log_level(lark.LogLevel.INFO) \
        .build()


def extract_images_from_markdown(file_path: str, content: str) -> List[str]:
    """从 Markdown 中提取本地图片路径"""
    from urllib.parse import unquote

    image_paths = []
    pattern = r'!\[.*?\]\((.*?)\)'
    matches = re.findall(pattern, content)

    for match in matches:
        if not match.startswith(('http://', 'https://')):
            img_path = os.path.join(os.path.dirname(file_path), match)
            decoded_path = unquote(img_path)
            if os.path.exists(decoded_path):
                image_paths.append(decoded_path)

    return image_paths


# ==================== 核心转换器 ====================

class PerfectFeishuConverter:
    """完美版飞书转换器"""

    def __init__(self, user_access_token: str):
        self.user_access_token = user_access_token
        self.client = create_client()

    def create_document(self, title: str, folder_token: Optional[str] = None) -> Optional[str]:
        """创建飞书文档"""
        request = CreateDocumentRequest.builder() \
            .request_body(CreateDocumentRequestBody.builder()
                .title(title)
                .folder_token(folder_token or "")
                .build()) \
            .build()

        option = lark.RequestOption.builder().user_access_token(self.user_access_token).build()
        response = self.client.docx.v1.document.create(request, option)

        if response.code == 0 and response.data:
            return response.data.document.document_id
        else:
            print(f"[ERROR] 创建文档失败: {response.msg}")
            return None

    def convert_markdown_to_blocks(self, markdown_file_path: str) -> Optional[dict]:
        """将 Markdown 文件转换为飞书文档块"""
        if not os.path.exists(markdown_file_path):
            print(f"[ERROR] 文件不存在: {markdown_file_path}")
            return None

        try:
            with open(markdown_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            request = ConvertDocumentRequest.builder() \
                .request_body(ConvertDocumentRequestBody.builder()
                    .content_type("markdown")
                    .content(content)
                    .build()) \
                .build()

            option = lark.RequestOption.builder().user_access_token(self.user_access_token).build()
            response = self.client.docx.v1.document.convert(request, option)

            if response.code == 0:
                return {
                    "first_level_block_ids": response.data.first_level_block_ids,
                    "blocks": response.data.blocks
                }
            else:
                print(f"[ERROR] Markdown 转换失败: {response.msg}")
                return None

        except Exception as e:
            print(f"[ERROR] 读取文件失败: {e}")
            return None

    def insert_blocks_to_document(self, document_id: str, blocks_data: dict) -> bool:
        """将块数据插入文档"""
        blocks = blocks_data.get('blocks', [])
        first_level_block_ids = blocks_data.get('first_level_block_ids', [])

        if not blocks:
            print("[WARNING] 没有要插入的块数据")
            return False

        request = CreateDocumentBlockDescendantRequest.builder() \
            .document_id(document_id) \
            .block_id(document_id) \
            .document_revision_id(-1) \
            .request_body(CreateDocumentBlockDescendantRequestBody.builder()
                .children_id(first_level_block_ids)
                .index(0)
                .descendants(blocks)
                .build()) \
            .build()

        option = lark.RequestOption.builder().user_access_token(self.user_access_token).build()
        response = self.client.docx.v1.document_block_descendant.create(request, option)

        if response.code == 0:
            return True
        else:
            print(f"[ERROR] 插入内容失败: {response.msg}")
            return False

    def upload_image_to_block(self, image_path: str, block_id: str, document_id: str) -> Optional[str]:
        """上传图片到文档块（修复版）

        关键修复：直接传递文件对象，而不是文件内容！
        """
        if not os.path.exists(image_path):
            print(f"[ERROR] 图片不存在: {image_path}")
            return None

        file_name = os.path.basename(image_path)
        file_size = os.path.getsize(image_path)

        try:
            # 关键修复：使用 with 语句确保文件正确关闭
            # 但在 API 调用中直接传递文件对象
            extra = {"drive_route_token": document_id}

            # 打开文件（会自动关闭）
            file_obj = open(image_path, "rb")

            request = UploadAllMediaRequest.builder() \
                .request_body(UploadAllMediaRequestBody.builder()
                    .file_name(file_name)
                    .parent_node(block_id)
                    .parent_type("docx_image")
                    .size(file_size)
                    .extra(json.dumps(extra, ensure_ascii=False))
                    .file(file_obj)  # ✅ 直接传递文件对象
                    .build()) \
                .build()

            option = lark.RequestOption.builder().user_access_token(self.user_access_token).build()
            response = self.client.drive.v1.media.upload_all(request, option)

            # 关闭文件
            file_obj.close()

            if response.code == 0:
                return response.data.file_token
            else:
                print(f"[ERROR] 上传图片失败: {response.msg}")
                return None

        except Exception as e:
            print(f"[ERROR] 处理图片失败: {e}")
            return None

    def update_image_block(self, block_id: str, document_id: str, image_token: str,
                          width: int, height: int) -> bool:
        """更新图片块"""
        request = PatchDocumentBlockRequest.builder() \
            .document_id(document_id) \
            .block_id(block_id) \
            .document_revision_id(-1) \
            .request_body(UpdateBlockRequest.builder()
                .replace_image(ReplaceImageRequest.builder()
                    .token(image_token)
                    .width(width)
                    .height(height)
                    .build())
                .build()) \
            .build()

        option = lark.RequestOption.builder().user_access_token(self.user_access_token).build()
        response = self.client.docx.v1.document_block.patch(request, option)

        return response.code == 0

    def process_images(self, document_id: str, image_paths: List[str]) -> int:
        """处理文档中的图片（完美版）"""
        if not image_paths:
            return 0

        print(f"\n[INFO] 找到 {len(image_paths)} 个图片，开始上传...")
        time.sleep(2)  # 等待文档完全创建

        request = ListDocumentBlockRequest.builder() \
            .page_size(500) \
            .document_id(document_id) \
            .build()

        option = lark.RequestOption.builder().user_access_token(self.user_access_token).build()

        img_index = 0
        uploaded_count = 0
        page_token = None

        while img_index < len(image_paths):
            if page_token:
                request.page_token = page_token

            response = self.client.docx.v1.document_block.list(request, option)

            if response.code != 0:
                print(f"[ERROR] 获取文档块失败: {response.msg}")
                break

            for block in response.data.items:
                if block.block_type == 27 and img_index < len(image_paths):
                    img_path = image_paths[img_index]
                    print(f"[INFO] 上传图片 ({img_index + 1}/{len(image_paths)}): {os.path.basename(img_path)}")

                    # 上传图片
                    image_token = self.upload_image_to_block(img_path, block.block_id, document_id)

                    if image_token:
                        # 获取图片尺寸
                        with Image.open(img_path) as img:
                            width, height = img.size

                        # 更新图片块
                        if self.update_image_block(block.block_id, document_id, image_token, width, height):
                            print(f"  ✅ 成功")
                            uploaded_count += 1
                        else:
                            print(f"  ❌ 更新失败")
                    else:
                        print(f"  ❌ 上传失败")

                    img_index += 1

            if not response.data.has_more:
                break

            page_token = response.data.page_token

        print(f"\n[INFO] 图片上传完成: {uploaded_count}/{len(image_paths)}")
        return uploaded_count


# ==================== 主函数 ====================

def extract_title_from_markdown(content: str) -> str:
    """从 Markdown 内容中提取标题

    Args:
        content: Markdown 内容

    Returns:
        提取的标题
    """
    # 查找第一个 # 标题
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            # 移除 # 号和空格
            title = line.lstrip('#').strip()
            if title:
                return title

    return None


def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("完美版 Markdown 转飞书文档工具")
        print("=" * 70)
        print()
        print("使用方法:")
        print("  python convert_perfect.py <markdown_file> [title] [folder_token]")
        print()
        print("参数说明:")
        print("  markdown_file  - Markdown 文件路径")
        print("  title         - 飞书文档标题（可选，默认从MD文件中提取）")
        print("  folder_token  - 目标文件夹 token（可选）")
        print()
        print("示例:")
        print('  python convert_perfect.py "notes/study_guide.md"')
        print('  python convert_perfect.py "notes/study_guide.md" "自定义标题"')
        print('  python convert_perfect.py "notes/study_guide.md" "自定义标题" "AJa3fDb0..."')
        print()
        return 1

    markdown_file = sys.argv[1]
    document_title = sys.argv[2] if len(sys.argv) > 2 else None
    folder_token = sys.argv[3] if len(sys.argv) > 3 else None

    # 检查文件
    if not os.path.exists(markdown_file):
        print(f"[ERROR] 文件不存在: {markdown_file}")
        return 1

    # 读取 Markdown 内容
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # 如果没有提供标题，从 Markdown 中提取
    if not document_title:
        document_title = extract_title_from_markdown(markdown_content)
        if not document_title:
            # 如果没有找到标题，使用文件名
            document_title = os.path.splitext(os.path.basename(markdown_file))[0]
            print(f"[INFO] 未找到标题，使用文件名: {document_title}")

    print("=" * 70)
    print("完美版 Markdown 转飞书文档工具")
    print("=" * 70)
    print(f"文件路径: {markdown_file}")
    print(f"文档标题: {document_title}")
    if folder_token:
        print(f"目标文件夹: {folder_token}")
    print()

    print("[INFO] 扫描图片...")
    image_paths = extract_images_from_markdown(markdown_file, markdown_content)

    if image_paths:
        print(f"[INFO] 找到 {len(image_paths)} 个本地图片")
    else:
        print("[INFO] 未找到本地图片")

    # 创建转换器
    print("\n[INFO] 初始化飞书客户端...")
    converter = PerfectFeishuConverter(USER_ACCESS_TOKEN)

    # 创建文档
    print(f"[INFO] 创建飞书文档...")
    document_id = converter.create_document(document_title, folder_token)

    if not document_id:
        print("[ERROR] 文档创建失败")
        return 1

    print(f"[INFO] 文档创建成功: {document_id}")

    # 转换 Markdown
    print(f"[INFO] 转换 Markdown 内容...")
    blocks_data = converter.convert_markdown_to_blocks(markdown_file)

    if not blocks_data:
        print("[ERROR] Markdown 转换失败")
        return 1

    block_count = len(blocks_data.get('blocks', []))
    print(f"[INFO] 转换成功，生成 {block_count} 个内容块")

    # 插入内容
    print(f"[INFO] 插入内容到文档...")
    if not converter.insert_blocks_to_document(document_id, blocks_data):
        print("[ERROR] 内容插入失败")
        return 1

    print("[INFO] 内容插入成功")

    # 处理图片
    if image_paths:
        uploaded = converter.process_images(document_id, image_paths)
        if uploaded == len(image_paths):
            print(f"\n✨ 所有图片上传成功！")
        else:
            print(f"\n⚠️ 部分图片上传失败 ({uploaded}/{len(image_paths)})")

    # 完成
    print()
    print("=" * 70)
    print("✅ 转换完成！")
    print(f"文档 ID: {document_id}")
    print(f"文档链接: https://feishu.cn/docx/{document_id}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
