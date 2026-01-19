#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试删除空白行功能
"""

import sys
import json
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python-backend'))

from engine.core.loader import FileLoader
from engine.content.processor import ContentProcessor

# 测试文件路径
test_file = r"C:\Users\12607\Desktop\excel工具箱—kiro版\test.xlsx"

print("=== 测试删除空白行功能 ===\n")

# 1. 加载文件
print("1. 加载文件...")
loader = FileLoader()
result = loader.load({'file_path': test_file})

if result['status'] != 'success':
    print(f"❌ 加载失败: {result['message']}")
    sys.exit(1)

print(f"✅ 加载成功: {result['data']['file_name']}")
print(f"   工作表数量: {result['data']['sheet_count']}")

# 2. 获取工作簿
workbook = loader.get_current_workbook()
if not workbook:
    print("❌ 无法获取工作簿")
    sys.exit(1)

print(f"✅ 获取工作簿成功")

# 3. 测试删除空白行
print("\n2. 测试删除空白行...")
processor = ContentProcessor()

for sheet_name in workbook.sheetnames:
    print(f"\n处理工作表: {sheet_name}")
    worksheet = workbook[sheet_name]
    
    result = processor.remove_blank_rows({
        'worksheet': worksheet,
        'sheet_name': sheet_name
    })
    
    if result['status'] == 'success':
        print(f"✅ 成功: {result['message']}")
        print(f"   删除行数: {result['data']['deleted_count']}")
    else:
        print(f"❌ 失败: {result['message']}")

print("\n=== 测试完成 ===")
