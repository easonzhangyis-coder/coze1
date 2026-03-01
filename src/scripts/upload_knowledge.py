#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
上传知识库文件到对象存储并解析入库

支持文件格式：.txt, .md, .json
"""

import os
import sys
import json

# 添加项目路径
sys.path.insert(0, '/workspace/projects/src')

from storage.database.db import get_session
from storage.database.knowledge_manager import KnowledgeManager, KnowledgeCreate
from storage.s3.s3_storage import S3SyncStorage


def read_file_content(file_path: str) -> tuple:
    """读取文件内容"""
    # 根据文件扩展名选择不同的读取方式
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return os.path.basename(file_path), content
    
    elif file_path.endswith('.md'):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return os.path.basename(file_path), content
    
    elif file_path.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 假设 JSON 格式为 {"title": "", "content": "", "category": "", "tags": ""}
        title = data.get('title', os.path.basename(file_path))
        content = data.get('content', '')
        category = data.get('category')
        tags = data.get('tags')
        
        return title, content, category, tags
    
    else:
        raise ValueError(f"不支持的文件格式：{file_path}。支持的格式：.txt, .md, .json")


def upload_to_knowledge_base(file_path: str, category: str = None, tags: str = None, title: str = None):
    """
    上传文件到知识库
    
    Args:
        file_path: 文件路径
        category: 知识分类（可选）
        tags: 标签，多个标签用逗号分隔（可选）
        title: 知识标题（可选，默认使用文件名）
    """
    
    # 1. 读取文件内容
    print(f"正在读取文件：{file_path}")
    
    if file_path.endswith('.json'):
        file_name, content, file_category, file_tags = read_file_content(file_path)
        category = category or file_category
        tags = tags or file_tags
        title = title or file_name
    else:
        file_name, content = read_file_content(file_path)
        title = title or file_name.replace('.txt', '').replace('.md', '')
    
    # 2. 上传文件到对象存储
    print(f"正在上传文件到对象存储...")
    storage = S3SyncStorage(
        endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
        access_key="",
        secret_key="",
        bucket_name=os.getenv("COZE_BUCKET_NAME"),
        region="cn-beijing",
    )
    
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    file_key = storage.upload_file(
        file_content=file_content,
        file_name=file_name,
        content_type="text/plain",
    )
    
    print(f"✓ 文件已上传到对象存储，Key: {file_key}")
    
    # 3. 保存到数据库
    print(f"正在保存到知识库数据库...")
    db = get_session()
    try:
        manager = KnowledgeManager()
        
        knowledge_data = KnowledgeCreate(
            title=title,
            content=content,
            category=category,
            file_name=file_name,
            file_key=file_key,
            tags=tags
        )
        
        knowledge = manager.create_knowledge(db, knowledge_data)
        print(f"✓ 知识已成功保存到数据库，ID: {knowledge.id}")
        print(f"✓ 标题：{knowledge.title}")
        if knowledge.category:
            print(f"✓ 分类：{knowledge.category}")
        
    except Exception as e:
        print(f"✗ 保存到数据库失败：{str(e)}")
        raise
    finally:
        db.close()
    
    print("\n✅ 上传完成！")


def main():
    """主函数"""
    print("=" * 60)
    print("知识库文件上传工具")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\n使用方法：")
        print("  python upload_knowledge.py <文件路径> [分类] [标签]")
        print("\n示例：")
        print("  python upload_knowledge.py law.txt 劳动法 '劳动合同,赔偿标准'")
        print("  python upload_knowledge.py case.json")
        print("\n支持的文件格式：.txt, .md, .json")
        print("\nJSON 文件格式示例：")
        print("""{
  "title": "法律知识标题",
  "content": "法律知识内容",
  "category": "劳动法",
  "tags": "标签1,标签2"
}""")
        sys.exit(1)
    
    file_path = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else None
    tags = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(file_path):
        print(f"✗ 错误：文件不存在：{file_path}")
        sys.exit(1)
    
    try:
        upload_to_knowledge_base(file_path, category, tags)
    except Exception as e:
        print(f"\n✗ 上传失败：{str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
