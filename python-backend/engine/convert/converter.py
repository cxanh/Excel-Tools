#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Format Converter - 格式转换器
负责 Excel 文件的格式转换（PDF、CSV）
"""

import os
import sys
import platform
import pandas as pd
from typing import Dict, Any, List


def send_progress(progress: int, message: str = ""):
    """发送进度消息到 stdout"""
    progress_msg = {
        "type": "progress",
        "progress": progress,
        "message": message
    }
    import json
    print(json.dumps(progress_msg), flush=True)


class FormatConverter:
    """格式转换器"""
    
    def __init__(self):
        """初始化转换器"""
        self.platform = platform.system()
    
    def excel_to_csv(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        将 Excel 转换为 CSV
        
        Args:
            params: {
                'file_path': str,  # Excel 文件路径
                'output_dir': str,  # 输出目录
                'sheet_names': List[str],  # 要转换的工作表名称列表（可选，默认所有）
                'encoding': str,  # 编码格式（默认 'utf-8'）
                'delimiter': str,  # 分隔符（默认 ','）
                'include_index': bool  # 是否包含索引（默认 False）
            }
        
        Returns:
            dict: 操作结果
        """
        # 验证参数
        file_path = params.get('file_path')
        output_dir = params.get('output_dir')
        sheet_names = params.get('sheet_names')
        encoding = params.get('encoding', 'utf-8')
        delimiter = params.get('delimiter', ',')
        include_index = params.get('include_index', False)
        
        if not file_path:
            return {
                "type": "result",
                "status": "error",
                "error_code": "MISSING_FILE_PATH",
                "message": "缺少文件路径"
            }
        
        if not output_dir:
            return {
                "type": "result",
                "status": "error",
                "error_code": "MISSING_OUTPUT_DIR",
                "message": "缺少输出目录"
            }
        
        if not os.path.exists(file_path):
            return {
                "type": "result",
                "status": "error",
                "error_code": "FILE_NOT_FOUND",
                "message": f"文件不存在: {file_path}"
            }
        
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            send_progress(10, "正在读取 Excel 文件...")
            
            # 读取 Excel 文件
            excel_file = pd.ExcelFile(file_path)
            
            # 确定要转换的工作表
            if sheet_names:
                sheets_to_convert = [s for s in sheet_names if s in excel_file.sheet_names]
                if not sheets_to_convert:
                    return {
                        "type": "result",
                        "status": "error",
                        "error_code": "SHEET_NOT_FOUND",
                        "message": "指定的工作表不存在"
                    }
            else:
                sheets_to_convert = excel_file.sheet_names
            
            total_sheets = len(sheets_to_convert)
            output_files = []
            
            # 获取文件名（不含扩展名）
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            for idx, sheet_name in enumerate(sheets_to_convert):
                send_progress(
                    10 + int((idx / total_sheets) * 80),
                    f"正在转换工作表 {idx + 1}/{total_sheets}: {sheet_name}"
                )
                
                # 读取工作表
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # 生成输出文件名
                if total_sheets == 1:
                    output_file = os.path.join(output_dir, f"{base_name}.csv")
                else:
                    # 清理工作表名称中的非法字符
                    safe_sheet_name = "".join(c for c in sheet_name if c.isalnum() or c in (' ', '-', '_')).strip()
                    output_file = os.path.join(output_dir, f"{base_name}_{safe_sheet_name}.csv")
                
                # 保存为 CSV
                df.to_csv(
                    output_file,
                    index=include_index,
                    encoding=encoding,
                    sep=delimiter
                )
                
                output_files.append({
                    "sheet_name": sheet_name,
                    "file_name": os.path.basename(output_file),
                    "path": output_file,
                    "rows": len(df),
                    "columns": len(df.columns)
                })
            
            send_progress(100, "转换完成")
            
            return {
                "type": "result",
                "status": "success",
                "message": f"成功转换 {total_sheets} 个工作表",
                "data": {
                    "total_sheets": total_sheets,
                    "output_dir": output_dir,
                    "output_files": output_files,
                    "encoding": encoding,
                    "delimiter": delimiter
                }
            }
        
        except Exception as e:
            return {
                "type": "result",
                "status": "error",
                "error_code": "CONVERSION_ERROR",
                "message": f"转换失败: {str(e)}"
            }
    
    def excel_to_pdf(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        将 Excel 转换为 PDF
        
        Args:
            params: {
                'file_path': str,  # Excel 文件路径
                'output_path': str,  # 输出 PDF 文件路径
                'sheet_names': List[str],  # 要转换的工作表名称列表（可选，默认所有）
                'method': str  # 转换方法：'com'（Windows）、'libreoffice'、'image'（默认自动选择）
            }
        
        Returns:
            dict: 操作结果
        """
        # 验证参数
        file_path = params.get('file_path')
        output_path = params.get('output_path')
        sheet_names = params.get('sheet_names')
        method = params.get('method', 'auto')
        
        if not file_path:
            return {
                "type": "result",
                "status": "error",
                "error_code": "MISSING_FILE_PATH",
                "message": "缺少文件路径"
            }
        
        if not output_path:
            return {
                "type": "result",
                "status": "error",
                "error_code": "MISSING_OUTPUT_PATH",
                "message": "缺少输出文件路径"
            }
        
        if not os.path.exists(file_path):
            return {
                "type": "result",
                "status": "error",
                "error_code": "FILE_NOT_FOUND",
                "message": f"文件不存在: {file_path}"
            }
        
        # 自动选择转换方法
        if method == 'auto':
            if self.platform == 'Windows':
                method = 'com'
            elif self._check_libreoffice():
                method = 'libreoffice'
            else:
                method = 'image'
        
        # 根据方法调用相应的转换函数
        if method == 'com':
            return self._excel_to_pdf_com(file_path, output_path, sheet_names)
        elif method == 'libreoffice':
            return self._excel_to_pdf_libreoffice(file_path, output_path, sheet_names)
        elif method == 'image':
            return self._excel_to_pdf_image(file_path, output_path, sheet_names)
        else:
            return {
                "type": "result",
                "status": "error",
                "error_code": "INVALID_METHOD",
                "message": f"无效的转换方法: {method}"
            }
    
    def _excel_to_pdf_com(self, file_path: str, output_path: str, sheet_names: List[str] = None) -> Dict[str, Any]:
        """使用 Windows COM 组件转换 Excel 为 PDF"""
        if self.platform != 'Windows':
            return {
                "type": "result",
                "status": "error",
                "error_code": "PLATFORM_NOT_SUPPORTED",
                "message": "COM 方法仅支持 Windows 平台"
            }
        
        try:
            import win32com.client
            
            send_progress(10, "正在启动 Excel...")
            
            # 转换为绝对路径
            file_path = os.path.abspath(file_path)
            output_path = os.path.abspath(output_path)
            
            # 创建 Excel 应用实例
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False
            
            try:
                send_progress(30, "正在打开文件...")
                
                # 打开工作簿
                wb = excel.Workbooks.Open(file_path)
                
                send_progress(50, "正在转换为 PDF...")
                
                # 如果指定了工作表，只导出这些工作表
                if sheet_names:
                    # 隐藏其他工作表
                    for sheet in wb.Worksheets:
                        if sheet.Name not in sheet_names:
                            sheet.Visible = False
                
                # 导出为 PDF (0 = xlTypePDF)
                wb.ExportAsFixedFormat(0, output_path)
                
                send_progress(90, "正在关闭文件...")
                
                # 关闭工作簿
                wb.Close(False)
                
                send_progress(100, "转换完成")
                
                return {
                    "type": "result",
                    "status": "success",
                    "message": "成功转换为 PDF",
                    "data": {
                        "output_path": output_path,
                        "method": "com",
                        "file_size": os.path.getsize(output_path)
                    }
                }
            
            finally:
                # 确保 Excel 被关闭
                excel.Quit()
        
        except ImportError:
            return {
                "type": "result",
                "status": "error",
                "error_code": "PYWIN32_NOT_INSTALLED",
                "message": "未安装 pywin32 库，请运行: pip install pywin32"
            }
        except Exception as e:
            return {
                "type": "result",
                "status": "error",
                "error_code": "COM_CONVERSION_ERROR",
                "message": f"COM 转换失败: {str(e)}"
            }
    
    def _excel_to_pdf_libreoffice(self, file_path: str, output_path: str, sheet_names: List[str] = None) -> Dict[str, Any]:
        """使用 LibreOffice 转换 Excel 为 PDF"""
        import subprocess
        
        # 检查 LibreOffice 是否安装
        if not self._check_libreoffice():
            return {
                "type": "result",
                "status": "error",
                "error_code": "LIBREOFFICE_NOT_FOUND",
                "message": "未找到 LibreOffice，请先安装 LibreOffice"
            }
        
        try:
            send_progress(10, "正在准备转换...")
            
            # 转换为绝对路径
            file_path = os.path.abspath(file_path)
            output_dir = os.path.dirname(os.path.abspath(output_path))
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            send_progress(30, "正在调用 LibreOffice...")
            
            # 构建 LibreOffice 命令
            cmd = [
                self._get_libreoffice_path(),
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', output_dir,
                file_path
            ]
            
            # 执行转换
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                return {
                    "type": "result",
                    "status": "error",
                    "error_code": "LIBREOFFICE_CONVERSION_ERROR",
                    "message": f"LibreOffice 转换失败: {result.stderr}"
                }
            
            send_progress(80, "正在重命名文件...")
            
            # LibreOffice 会生成与原文件同名的 PDF
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            generated_pdf = os.path.join(output_dir, f"{base_name}.pdf")
            
            # 如果输出路径不同，重命名文件
            if generated_pdf != output_path:
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(generated_pdf, output_path)
            
            send_progress(100, "转换完成")
            
            return {
                "type": "result",
                "status": "success",
                "message": "成功转换为 PDF",
                "data": {
                    "output_path": output_path,
                    "method": "libreoffice",
                    "file_size": os.path.getsize(output_path)
                }
            }
        
        except subprocess.TimeoutExpired:
            return {
                "type": "result",
                "status": "error",
                "error_code": "CONVERSION_TIMEOUT",
                "message": "转换超时（超过 60 秒）"
            }
        except Exception as e:
            return {
                "type": "result",
                "status": "error",
                "error_code": "LIBREOFFICE_CONVERSION_ERROR",
                "message": f"LibreOffice 转换失败: {str(e)}"
            }
    
    def _excel_to_pdf_image(self, file_path: str, output_path: str, sheet_names: List[str] = None) -> Dict[str, Any]:
        """将 Excel 工作表导出为图片后合成 PDF（降级方案）"""
        return {
            "type": "result",
            "status": "error",
            "error_code": "METHOD_NOT_IMPLEMENTED",
            "message": "图片转 PDF 方法尚未实现，请使用 COM 或 LibreOffice 方法"
        }
    
    def _check_libreoffice(self) -> bool:
        """检查 LibreOffice 是否安装"""
        try:
            import subprocess
            libreoffice_path = self._get_libreoffice_path()
            result = subprocess.run([libreoffice_path, '--version'], 
                                    capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _get_libreoffice_path(self) -> str:
        """获取 LibreOffice 可执行文件路径"""
        if self.platform == 'Windows':
            # Windows 常见安装路径
            possible_paths = [
                r'C:\Program Files\LibreOffice\program\soffice.exe',
                r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
            return 'soffice'  # 尝试从 PATH 查找
        elif self.platform == 'Darwin':  # macOS
            return '/Applications/LibreOffice.app/Contents/MacOS/soffice'
        else:  # Linux
            return 'libreoffice'
    
    def check_dependencies(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        检查格式转换依赖
        
        Returns:
            dict: 依赖状态
        """
        dependencies = {
            "platform": self.platform,
            "excel_to_csv": {
                "available": True,
                "method": "pandas",
                "status": "已安装"
            },
            "excel_to_pdf": {
                "available": False,
                "methods": []
            }
        }
        
        # 检查 PDF 转换方法
        pdf_methods = []
        
        # 检查 COM（Windows）
        if self.platform == 'Windows':
            try:
                import win32com.client
                pdf_methods.append({
                    "name": "com",
                    "available": True,
                    "description": "Windows COM 组件（推荐）",
                    "requirements": "需要安装 Microsoft Excel"
                })
            except ImportError:
                pdf_methods.append({
                    "name": "com",
                    "available": False,
                    "description": "Windows COM 组件",
                    "requirements": "需要安装: pip install pywin32"
                })
        
        # 检查 LibreOffice
        libreoffice_available = self._check_libreoffice()
        pdf_methods.append({
            "name": "libreoffice",
            "available": libreoffice_available,
            "description": "LibreOffice（跨平台）",
            "requirements": "需要安装 LibreOffice" if not libreoffice_available else "已安装",
            "download_url": "https://www.libreoffice.org/download/download/"
        })
        
        dependencies["excel_to_pdf"]["methods"] = pdf_methods
        dependencies["excel_to_pdf"]["available"] = any(m["available"] for m in pdf_methods)
        
        return {
            "type": "result",
            "status": "success",
            "message": "依赖检查完成",
            "data": dependencies
        }
