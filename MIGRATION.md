# 项目统一说明

## 概述

已将两个 Markdown 转飞书工具统一到 **markdown-to-feishu** 项目中：

- ✅ `markdown-to-feishu` - 核心转换工具（保留并增强）
- ✅ `markdown2feishuDoc` - 批量导入功能（已迁移）

## 统一后的项目结构

```
markdown-to-feishu/
├── convert_perfect.py      # 单文件转换（完美版）
├── batch_import.py         # 批量导入（新增）
├── config.json             # 配置文件（已 gitignore）
├── config.example.json     # 配置示例
└── src/                    # 核心模块
```

## 功能对比

### 1. 单文件转换 (`convert_perfect.py`)

**特点**：
- ✅ 自动提取标题（从 Markdown）
- ✅ 支持图片上传
- ✅ 完美错误处理
- ✅ 简洁命令行

**使用**：
```bash
python convert_perfect.py "path/to/file.md" ["标题"] ["folder_token"]
```

**应用场景**：
- 日常文档转换
- AI 工具集成（feishu-sync skill）
- 自动化脚本

---

### 2. 批量导入 (`batch_import.py`)

**特点**：
- ✅ 递归扫描整个文件夹
- ✅ 保留目录结构
- ✅ 自动创建飞书文件夹
- ✅ 清理文件名（去除时间戳）

**使用**：
```bash
python batch_import.py "D:\notes" "U89ffsAjflcugtdtv4Sc98rbnkh"
```

**应用场景**：
- 迁移大量文档
- 批量处理笔记
- 一次性导入项目文档

---

## feishu-sync Skill 更新

**版本**: 1.0.1

**改进**：
- ✅ 直接调用 `convert_perfect.py`
- ✅ 移除 `user_token` 参数（从配置文件读取）
- ✅ 简化使用：`/feishu-sync "file.md" ["标题"]`

**更新内容**：
- `skill.py` - 调用 markdown-to-feishu 的脚本
- `skill.md` - 更新文档说明
- `skill.json` - 更新参数定义
- 删除 `markdown2feishu_full.py`（不再需要）

---

## 配置统一

**位置**: `markdown-to-feishu/config.json`

```json
{
  "app_id": "cli_xxx",
  "app_secret": "xxx",
  "user_access_token": "u-xxx"
}
```

**说明**：
- ✅ 所有工具共享同一配置
- ✅ 已在 `.gitignore` 中忽略
- ✅ 提供 `config.example.json` 模板

---

## 使用建议

### 日常使用（推荐）
使用 **convert_perfect.py** 或 **feishu-sync skill**：
- 快速转换单个文件
- 集成到 AI 工作流
- 灵活控制输出

### 批量迁移
使用 **batch_import.py**：
- 一次性导入大量文档
- 保留原有目录结构
- 适合初始化或归档

---

## 优势

1. **代码复用**：一个项目，两份脚本，共享核心逻辑
2. **维护简单**：统一配置，统一依赖
3. **功能完整**：覆盖单文件和批量两种场景
4. **易于集成**：清晰的模块化设计

---

## 下一步

- [ ] 测试批量导入功能
- [ ] 更新文档
- [ ] 推送到远程仓库
