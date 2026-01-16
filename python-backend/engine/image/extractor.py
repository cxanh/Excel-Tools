#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Extractor - 图片提取器
使用 zipfile 直接从 .xlsx 文件提取图片（推荐方案）
"""

import os
import sys
import zipfile
import mimetypes
from pathlib import Path


def log(message):
    """将日志输出到 stderr"""
    sys.stderr.write(f"[IMAGE_EXTRACTOR] {message}\n")
    sys.stderr.flush()


def send_progress(progress, message=""):
    """发送进度消息到 stdout"""
    import json
    progress_msg = {
        "type": "progress",
        "progress": progress,
        "message": message
    }
    print(json.dumps(progress_msg), flush=True)


class ImageExtractor:
    """图片提取器"""
    
    # 支持的图片格式
    SUPPORTED_FORMATS = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.tif': 'image/tiff',
        '.emf': 'image/x-emf',
        '.wmf': 'image/x-wmf'
    }
    
    def extract_images(self, params):
        """
        从 Excel 文件中提取所有图片
        
        Args:
            params: dict, 包含以下字段：
                - file_path: str, Excel 文件路径
                - output_dir: str, 输出目录路径
                - name_pattern: str, 文件命名模式（可选，默认：image_{index}{ext}）
        
        Returns:
            dict, 包含提取结果
        """
        file_path = params.get('file_path')
        output_dir = params.get('output_dir')
        name_pattern = params.get('name_pattern', 'image_{index}{ext}')
        
        # 验证参数
        if not file_path:
            return {
                "type": "result",
                "status": "error",
                "error_code": "MISSING_FILE_PATH",
                "message": "缺少文件路径参数"
            }
        
        if not output_dir:
            return {
                "type": "result",
                "status": "error",
                "error_code": "MISSING_OUTPUT_DIR",
                "message": "缺少输出目录参数"
            }
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {
                "type": "result",
                "status": "error",
                "error_code": "FILE_NOT_FOUND",
                "message": f"文件不存在: {file_path}"
            }
        
        # 检查文件格式
        if not file_path.lower().endswith(('.xlsx', '.xlsm')):
            return {
                "type": "result",
                "status": "error",
                "error_code": "UNSUPPORTED_FORMAT",
                "message": "仅支持 .xlsx 和 .xlsm 格式的文件",
                "suggested_action": "请使用 Excel 2007 或更高版本的文件格式"
            }
        
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            log(f"输出目录: {output_dir}")
            
            # 使用 zipfile 打开 Excel 文件
            send_progress(10, "正在打开 Excel 文件...")
            
            extracted_images = []
            image_index = 1
            
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # 列出所有文件
                all_files = zip_ref.namelist()
                
                # 查找 xl/media/ 目录下的图片
                media_files = [f for f in all_files if f.startswith('xl/media/')]
                
                if not media_files:
                    return {
                        "type": "result",
                        "status": "success",
                        "message": "文件中没有找到图片",
                        "data": {
                            "total_images": 0,
                            "extracted_images": []
                        }
                    }
                
                log(f"找到 {len(media_files)} 个图片文件")
                total_files = len(media_files)
                
                # 提取每个图片
                for idx, media_file in enumerate(media_files):
                    # 获取文件扩展名
                    _, ext = os.path.splitext(media_file)
                    ext = ext.lower()
                    
                    # 检查是否是支持的格式
                    if ext not in self.SUPPORTED_FORMATS:
                        log(f"跳过不支持的格式: {media_file}")
                        continue
                    
                    # 生成输出文件名
                    if '{index}' in name_pattern:
                        output_filename = name_pattern.replace('{index}', str(image_index))
                        output_filename = output_filename.replace('{ext}', ext)
                    else:
                        output_filename = f"image_{image_index}{ext}"
                    
                    output_path = os.path.join(output_dir, output_filename)
                    
                    # 提取文件
                    with zip_ref.open(media_file) as source:
                        with open(output_path, 'wb') as target:
                            target.write(source.read())
                    
                    # 获取文件大小
                    file_size = os.path.getsize(output_path)
                    
                    extracted_images.append({
                        "filename": output_filename,
                        "path": output_path,
                        "format": ext[1:].upper(),  # 去掉点号，转大写
                        "size": file_size,
                        "original_path": media_file
                    })
                    
                    image_index += 1
                    
                    # 发送进度
                    progress = int(10 + (idx + 1) / total_files * 80)
                    send_progress(progress, f"已提取 {idx + 1}/{total_files} 个图片")
                
                send_progress(100, "图片提取完成")
                
                return {
                    "type": "result",
                    "status": "success",
                    "message": f"成功提取 {len(extracted_images)} 个图片",
                    "data": {
                        "total_images": len(extracted_images),
                        "output_dir": output_dir,
                        "extracted_images": extracted_images
                    }
                }
        
        except zipfile.BadZipFile:
            return {
                "type": "result",
                "status": "error",
                "error_code": "FILE_CORRUPTED",
                "message": "文件已损坏或不是有效的 Excel 文件",
                "suggested_action": "请检查文件是否完整，或尝试使用 Excel 修复该文件"
            }
        
        except PermissionError:
            return {
                "type": "result",
                "status": "error",
                "error_code": "PERMISSION_DENIED",
                "message": "没有权限访问文件或输出目录",
                "suggested_action": "请检查文件和目录的访问权限"
            }
        
        except Exception as e:
            log(f"提取图片时发生错误: {str(e)}")
            return {
                "type": "result",
                "status": "error",
                "error_code": "EXTRACT_ERROR",
                "message": f"提取图片时发生错误: {str(e)}"
            }
    
    def get_image_info(self, params):
        """
        获取 Excel 文件中的图片信息（不提取）
        
        Args:
            params: dict, 包含以下字段：
                - file_path: str, Excel 文件路径
        
        Returns:
            dict, 包含图片信息
        """
        file_path = params.get('file_path')
        
        if not file_path:
            return {
                "type": "result",
                "status": "error",
                "error_code": "MISSING_FILE_PATH",
                "message": "缺少文件路径参数"
            }
        
        if not os.path.exists(file_path):
            return {
                "type": "result",
                "status": "error",
                "error_code": "FILE_NOT_FOUND",
                "message": f"文件不存在: {file_path}"
            }
        
        try:
            images_info = []
            
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # 查找 xl/media/ 目录下的图片
                media_files = [f for f in zip_ref.namelist() if f.startswith('xl/media/')]
                
                for media_file in media_files:
                    # 获取文件信息
                    file_info = zip_ref.getinfo(media_file)
                    _, ext = os.path.splitext(media_file)
                    ext = ext.lower()
                    
                    if ext in self.SUPPORTED_FORMATS:
                        images_info.append({
                            "filename": os.path.basename(media_file),
                            "format": ext[1:].upper(),
                            "size": file_info.file_size,
                            "compressed_size": file_info.compress_size,
                            "path": media_file
                        })
            
            return {
                "type": "result",
                "status": "success",
                "message": f"找到 {len(images_info)} 个图片",
                "data": {
                    "total_images": len(images_info),
                    "images": images_info
                }
            }
        
        except Exception as e:
            log(f"获取图片信息时发生错误: {str(e)}")
            return {
                "type": "result",
                "status": "error",
                "error_code": "INFO_ERROR",
                "message": f"获取图片信息时发生错误: {str(e)}"
            }
