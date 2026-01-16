#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Router - 命令路由器
负责解析命令并分发到相应的处理模块
"""

import sys
import json


def log(message):
    """将日志输出到 stderr"""
    sys.stderr.write(f"[ROUTER] {message}\n")
    sys.stderr.flush()


def send_progress(progress, message="", data=None):
    """
    发送进度消息到 stdout
    
    Args:
        progress: int, 进度百分比 (0-100)
        message: str, 进度描述信息
        data: dict, 额外的进度数据
    """
    progress_msg = {
        "type": "progress",
        "progress": progress,
        "message": message
    }
    if data:
        progress_msg["data"] = data
    
    print(json.dumps(progress_msg), flush=True)


class CLIRouter:
    """命令路由器"""
    
    def __init__(self):
        """初始化路由器，注册所有处理模块"""
        self.handlers = {}
        self._register_handlers()
    
    def _register_handlers(self):
        """注册命令处理器"""
        # 导入功能模块
        from engine.core.loader import FileLoader
        from engine.core.saver import FileSaver
        from engine.content.processor import ContentProcessor
        from engine.image.extractor import ImageExtractor
        from engine.image.watermark import WatermarkProcessor
        from engine.sheet.manager import SheetManager
        from engine.merge_split.engine import MergeSplitEngine
        from engine.convert.converter import FormatConverter
        
        # 创建模块实例
        self.file_loader = FileLoader()
        self.file_saver = FileSaver()
        self.content_processor = ContentProcessor()
        self.image_extractor = ImageExtractor()
        self.watermark_processor = WatermarkProcessor()
        self.sheet_manager = SheetManager()
        self.merge_split_engine = MergeSplitEngine()
        self.format_converter = FormatConverter()
        
        # 注册文件操作处理器
        self.handlers['load_file'] = self.file_loader.load
        self.handlers['close_file'] = self.file_loader.close
        self.handlers['save_file'] = self._handle_save_file
        self.handlers['restore_file'] = self.file_saver.restore
        self.handlers['list_backups'] = self.file_saver.list_backups
        self.handlers['delete_backup'] = self.file_saver.delete_backup
        
        # 注册内容处理器
        self.handlers['remove_blank_rows'] = self._handle_content_process('remove_blank_rows')
        self.handlers['clear_blank_cells'] = self._handle_content_process('clear_blank_cells')
        self.handlers['remove_formulas'] = self._handle_content_process('remove_formulas')
        self.handlers['remove_duplicate_rows'] = self._handle_content_process('remove_duplicate_rows')
        self.handlers['replace_content'] = self._handle_content_process('replace_content')
        
        # 注册图像处理器
        self.handlers['extract_images'] = self.image_extractor.extract_images
        self.handlers['get_image_info'] = self.image_extractor.get_image_info
        self.handlers['add_text_watermark'] = self.watermark_processor.add_text_watermark
        self.handlers['add_image_watermark'] = self.watermark_processor.add_image_watermark
        
        # 注册工作表管理器
        self.handlers['insert_sheet'] = self._handle_sheet_operation('insert_sheet')
        self.handlers['delete_sheet'] = self._handle_sheet_operation('delete_sheet')
        self.handlers['rename_sheet'] = self._handle_sheet_operation('rename_sheet')
        self.handlers['get_sheet_info'] = self._handle_sheet_operation('get_sheet_info')
        
        # 注册合并拆分引擎
        self.handlers['merge_excel_files'] = self.merge_split_engine.merge_excel_files
        self.handlers['merge_csv_files'] = self.merge_split_engine.merge_csv_files
        self.handlers['split_excel_file'] = self.merge_split_engine.split_excel_file
        self.handlers['split_csv_file'] = self.merge_split_engine.split_csv_file
        
        # 注册格式转换器
        self.handlers['excel_to_csv'] = self.format_converter.excel_to_csv
        self.handlers['excel_to_pdf'] = self.format_converter.excel_to_pdf
        self.handlers['check_dependencies'] = self.format_converter.check_dependencies
        
        # 注册测试处理器
        self.handlers['ping'] = self._handle_ping
        self.handlers['echo'] = self._handle_echo
        self.handlers['test_progress'] = self._handle_test_progress
    
    def _handle_content_process(self, method_name):
        """创建内容处理的包装函数"""
        def wrapper(params):
            # 获取当前加载的工作簿
            workbook = self.file_loader.get_current_workbook()
            
            if not workbook:
                return {
                    "type": "result",
                    "status": "error",
                    "error_code": "NO_FILE_LOADED",
                    "message": "没有加载的文件，请先加载文件"
                }
            
            # 获取工作表名称（如果指定）
            sheet_name = params.get('sheet_name')
            
            if sheet_name:
                # 处理指定的工作表
                if sheet_name not in workbook.sheetnames:
                    return {
                        "type": "result",
                        "status": "error",
                        "error_code": "SHEET_NOT_FOUND",
                        "message": f"工作表不存在: {sheet_name}"
                    }
                
                worksheet = workbook[sheet_name]
                params['worksheet'] = worksheet
                params['sheet_name'] = sheet_name
                
                # 调用处理方法
                method = getattr(self.content_processor, method_name)
                return method(params)
            else:
                # 处理所有工作表
                results = []
                total_sheets = len(workbook.sheetnames)
                
                for idx, sheet_name in enumerate(workbook.sheetnames):
                    worksheet = workbook[sheet_name]
                    sheet_params = params.copy()
                    sheet_params['worksheet'] = worksheet
                    sheet_params['sheet_name'] = sheet_name
                    
                    # 调用处理方法
                    method = getattr(self.content_processor, method_name)
                    result = method(sheet_params)
                    results.append(result)
                    
                    # 发送总体进度
                    overall_progress = int((idx + 1) / total_sheets * 100)
                    send_progress(overall_progress, f"已处理 {idx + 1}/{total_sheets} 个工作表")
                
                # 汇总结果
                success_count = sum(1 for r in results if r.get('status') == 'success')
                
                return {
                    "type": "result",
                    "status": "success" if success_count == total_sheets else "partial",
                    "message": f"处理完成: {success_count}/{total_sheets} 个工作表成功",
                    "data": {
                        "total_sheets": total_sheets,
                        "success_count": success_count,
                        "results": results
                    }
                }
        
        return wrapper
    
    def _handle_save_file(self, params):
        """处理保存文件命令（需要从 loader 获取 workbook）"""
        # 获取当前加载的工作簿
        workbook = self.file_loader.get_current_workbook()
        
        if not workbook:
            return {
                "type": "result",
                "status": "error",
                "error_code": "NO_FILE_LOADED",
                "message": "没有加载的文件，请先加载文件"
            }
        
        # 添加 workbook 到参数
        params['workbook'] = workbook
        
        # 调用保存器
        return self.file_saver.save(params)
    
    def _handle_sheet_operation(self, method_name):
        """创建工作表操作的包装函数"""
        def wrapper(params):
            # 获取当前加载的工作簿
            workbook = self.file_loader.get_current_workbook()
            
            if not workbook:
                return {
                    "type": "result",
                    "status": "error",
                    "error_code": "NO_FILE_LOADED",
                    "message": "没有加载的文件，请先加载文件"
                }
            
            # 添加 workbook 到参数
            params['workbook'] = workbook
            
            # 调用工作表管理器方法
            method = getattr(self.sheet_manager, method_name)
            return method(params)
        
        return wrapper
    
    def route(self, command):
        """
        路由命令到相应的处理器
        
        Args:
            command: dict, 包含 'action' 和 'params' 字段
        
        Returns:
            dict, 处理结果
        """
        action = command.get('action')
        params = command.get('params', {})
        
        if not action:
            return {
                "type": "result",
                "status": "error",
                "error_code": "MISSING_ACTION",
                "message": "Command must include 'action' field"
            }
        
        # 查找处理器
        handler = self.handlers.get(action)
        
        if not handler:
            log(f"Unknown action: {action}")
            return {
                "type": "result",
                "status": "error",
                "error_code": "UNKNOWN_ACTION",
                "message": f"Unknown action: {action}",
                "available_actions": list(self.handlers.keys())
            }
        
        # 调用处理器
        try:
            result = handler(params)
            return result
        except Exception as e:
            log(f"Handler error for action '{action}': {str(e)}")
            return {
                "type": "result",
                "status": "error",
                "error_code": "HANDLER_ERROR",
                "message": f"Error executing action '{action}': {str(e)}"
            }
    
    def _handle_ping(self, params):
        """测试处理器：ping"""
        return {
            "type": "result",
            "status": "success",
            "message": "pong",
            "data": {"timestamp": params.get('timestamp', 0)}
        }
    
    def _handle_echo(self, params):
        """测试处理器：echo"""
        return {
            "type": "result",
            "status": "success",
            "message": "echo",
            "data": params
        }
    
    def _handle_test_progress(self, params):
        """测试处理器：模拟长时间操作并发送进度"""
        import time
        
        total_steps = params.get('steps', 5)
        delay = params.get('delay', 0.5)
        
        for i in range(total_steps):
            progress = int((i + 1) / total_steps * 100)
            send_progress(
                progress=progress,
                message=f"处理步骤 {i + 1}/{total_steps}",
                data={"step": i + 1, "total": total_steps}
            )
            time.sleep(delay)
        
        return {
            "type": "result",
            "status": "success",
            "message": "进度测试完成",
            "data": {"total_steps": total_steps}
        }
