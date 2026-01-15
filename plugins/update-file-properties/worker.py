#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改 Excel 文件属性插件
"""

import io
import json
from openpyxl import load_workbook


def process(input_data):
    """处理文件属性修改请求
    
    Args:
        input_data: 包含输入文件和设置的数据
    
    Returns:
        dict: 处理结果，包含处理后的文件buffer和日志
    """
    result = {
        "success": False,
        "logs": [],
        "buffer": None
    }
    
    try:
        # 解析输入数据
        file = input_data["file"]
        file_name = input_data["fileName"]
        settings = input_data.get("settings", {})
        
        properties = settings.get("properties", {})
        
        # 加载Excel文件
        result["logs"].append(f"正在加载文件: {file_name}")
        wb = load_workbook(io.BytesIO(file))
        
        # 获取文档属性对象
        doc_props = wb.properties
        
        # 保存原始属性
        original_props = {
            "title": doc_props.title,
            "subject": doc_props.subject,
            "creator": doc_props.creator,
            "description": doc_props.description,
            "keywords": doc_props.keywords,
            "category": doc_props.category,
            "status": doc_props.status,
            "company": getattr(doc_props, "company", None),
            "manager": getattr(doc_props, "manager", None),
        }
        
        result["logs"].append(f"原始属性: {json.dumps(original_props, ensure_ascii=False)}")
        
        # 修改文件属性
        updated_count = 0
        
        if "title" in properties and properties["title"] is not None:
            doc_props.title = properties["title"]
            result["logs"].append(f"  标题: {original_props['title']} -> {properties['title']}")
            updated_count += 1
        
        if "subject" in properties and properties["subject"] is not None:
            doc_props.subject = properties["subject"]
            result["logs"].append(f"  主题: {original_props['subject']} -> {properties['subject']}")
            updated_count += 1
        
        if "author" in properties and properties["author"] is not None:
            doc_props.creator = properties["author"]
            result["logs"].append(f"  作者: {original_props['creator']} -> {properties['author']}")
            updated_count += 1
        
        if "description" in properties and properties["description"] is not None:
            doc_props.description = properties["description"]
            result["logs"].append(f"  描述: {original_props['description']} -> {properties['description']}")
            updated_count += 1
        
        if "keywords" in properties and properties["keywords"] is not None:
            doc_props.keywords = properties["keywords"]
            result["logs"].append(f"  关键词: {original_props['keywords']} -> {properties['keywords']}")
            updated_count += 1
        
        if "category" in properties and properties["category"] is not None:
            doc_props.category = properties["category"]
            result["logs"].append(f"  分类: {original_props['category']} -> {properties['category']}")
            updated_count += 1
        
        if "status" in properties and properties["status"] is not None:
            doc_props.status = properties["status"]
            result["logs"].append(f"  状态: {original_props['status']} -> {properties['status']}")
            updated_count += 1
        
        if "company" in properties and properties["company"] is not None:
            doc_props.company = properties["company"]
            result["logs"].append(f"  公司: {original_props['company']} -> {properties['company']}")
            updated_count += 1
        
        if "manager" in properties and properties["manager"] is not None:
            doc_props.manager = properties["manager"]
            result["logs"].append(f"  经理: {original_props['manager']} -> {properties['manager']}")
            updated_count += 1
        
        result["logs"].append(f"共更新了 {updated_count} 个属性")
        
        # 保存处理后的文件
        result["logs"].append("保存处理后的文件")
        output_stream = io.BytesIO()
        wb.save(output_stream)
        output_stream.seek(0)
        
        result["buffer"] = output_stream.getvalue()
        result["success"] = True
        result["logs"].append("文件处理完成")
        
    except Exception as e:
        result["success"] = False
        result["logs"].append(f"处理错误: {str(e)}")
        result["error"] = str(e)
    
    return result
