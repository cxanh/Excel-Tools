#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel Toolkit Backend - 主入口
负责接收命令、路由到相应模块、返回结果
"""

import sys
import json
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入引擎模块
from engine.core.loader import FileLoader
from engine.core.saver import FileSaver
from engine.content.processor import ContentProcessor
from engine.sheet.manager import SheetManager
from engine.batch.processor import BatchProcessor

# ===== 强制 UTF-8 =====
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def send(msg: dict):
    """发送消息到前端"""
    print(json.dumps(msg, ensure_ascii=False), flush=True)


def log(*args):
    """输出日志到 stderr"""
    print("[BACKEND]", *args, file=sys.stderr, flush=True)


class CommandRouter:
    """命令路由器"""
    
    def __init__(self):
        """初始化路由器和引擎模块"""
        self.file_loader = FileLoader()
        self.file_saver = FileSaver()
        self.content_processor = ContentProcessor()
        self.sheet_manager = SheetManager()
        self.batch_processor = BatchProcessor(
            self.file_loader,
            self.file_saver,
            self  # 传入自己作为 operation_handler
        )
        
        # 命令路由表
        self.routes = {
            # 文件操作
            'load_file': self.handle_load_file,
            'close_file': self.handle_close_file,
            'save_file': self.handle_save_file,
            
            # 内容处理
            'remove_blank_rows': self.handle_remove_blank_rows,
            'clear_blank_cells': self.handle_clear_blank_cells,
            'remove_formulas': self.handle_remove_formulas,
            'remove_duplicate_rows': self.handle_remove_duplicate_rows,
            'replace_content': self.handle_replace_content,
            
            # 工作表管理
            'insert_sheet': self.handle_insert_sheet,
            'delete_sheet': self.handle_delete_sheet,
            'rename_sheet': self.handle_rename_sheet,
            
            # 批量操作
            'batch_process': self.handle_batch_process,
            'cancel_batch': self.handle_cancel_batch,
        }
    
    def route(self, command: dict) -> dict:
        """
        路由命令到相应的处理器
        
        Args:
            command: dict, 包含 action 和 params
        
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
                "message": "缺少 action 参数"
            }
        
        # 查找路由
        handler = self.routes.get(action)
        
        if not handler:
            return {
                "type": "result",
                "status": "error",
                "error_code": "UNKNOWN_ACTION",
                "message": f"未知的操作: {action}",
                "suggested_action": f"支持的操作: {', '.join(self.routes.keys())}"
            }
        
        # 执行处理器
        try:
            return handler(params)
        except Exception as e:
            log(f"Error handling action '{action}': {str(e)}")
            return {
                "type": "result",
                "status": "error",
                "error_code": "HANDLER_ERROR",
                "message": f"处理命令时发生错误: {str(e)}"
            }
    
    # ===== 文件操作处理器 =====
    
    def handle_load_file(self, params: dict) -> dict:
        """处理加载文件命令"""
        return self.file_loader.load(params)
    
    def handle_close_file(self, params: dict) -> dict:
        """处理关闭文件命令"""
        return self.file_loader.close(params)
    
    def handle_save_file(self, params: dict) -> dict:
        """处理保存文件命令"""
        # 获取当前工作簿
        workbook = self.file_loader.get_current_workbook()
        
        if not workbook:
            return {
                "type": "result",
                "status": "error",
                "error_code": "NO_FILE_LOADED",
                "message": "没有加载的文件",
                "suggested_action": "请先加载一个 Excel 文件"
            }
        
        # 如果没有指定文件路径，使用当前文件路径
        if not params.get('file_path'):
            params['file_path'] = self.file_loader.get_current_file_path()
        
        # 添加工作簿到参数
        params['workbook'] = workbook
        
        return self.file_saver.save(params)
    
    # ===== 内容处理处理器 =====
    
    def handle_remove_blank_rows(self, params: dict) -> dict:
        """处理删除空白行命令"""
        return self._process_all_sheets(
            self.content_processor.remove_blank_rows,
            params,
            "删除空白行"
        )
    
    def handle_clear_blank_cells(self, params: dict) -> dict:
        """处理清除空白单元格命令"""
        return self._process_all_sheets(
            self.content_processor.clear_blank_cells,
            params,
            "清除空白单元格"
        )
    
    def handle_remove_formulas(self, params: dict) -> dict:
        """处理删除公式命令"""
        return self._process_all_sheets(
            self.content_processor.remove_formulas,
            params,
            "删除公式"
        )
    
    def handle_remove_duplicate_rows(self, params: dict) -> dict:
        """处理删除重复行命令"""
        return self._process_all_sheets(
            self.content_processor.remove_duplicate_rows,
            params,
            "删除重复行"
        )
    
    def handle_replace_content(self, params: dict) -> dict:
        """处理替换内容命令"""
        return self._process_all_sheets(
            self.content_processor.replace_content,
            params,
            "替换内容"
        )
    
    # ===== 工作表管理处理器 =====
    
    def handle_insert_sheet(self, params: dict) -> dict:
        """处理插入工作表命令"""
        # 获取当前工作簿
        workbook = self.file_loader.get_current_workbook()
        
        if not workbook:
            return {
                "type": "result",
                "status": "error",
                "error_code": "NO_FILE_LOADED",
                "message": "没有加载的文件",
                "suggested_action": "请先加载一个 Excel 文件"
            }
        
        # 添加工作簿到参数
        params['workbook'] = workbook
        
        # 调用工作表管理器
        result = self.sheet_manager.insert_sheet(params)
        
        # 如果成功，更新文件信息
        if result['status'] == 'success':
            # 重新获取文件信息
            file_info = self.file_loader.get_file_info()
            if file_info:
                result['data']['file_info'] = file_info
        
        return result
    
    def handle_delete_sheet(self, params: dict) -> dict:
        """处理删除工作表命令"""
        # 获取当前工作簿
        workbook = self.file_loader.get_current_workbook()
        
        if not workbook:
            return {
                "type": "result",
                "status": "error",
                "error_code": "NO_FILE_LOADED",
                "message": "没有加载的文件",
                "suggested_action": "请先加载一个 Excel 文件"
            }
        
        # 添加工作簿到参数
        params['workbook'] = workbook
        
        # 调用工作表管理器
        result = self.sheet_manager.delete_sheet(params)
        
        # 如果成功，更新文件信息
        if result['status'] == 'success':
            # 重新获取文件信息
            file_info = self.file_loader.get_file_info()
            if file_info:
                result['data']['file_info'] = file_info
        
        return result
    
    def handle_rename_sheet(self, params: dict) -> dict:
        """处理重命名工作表命令"""
        # 获取当前工作簿
        workbook = self.file_loader.get_current_workbook()
        
        if not workbook:
            return {
                "type": "result",
                "status": "error",
                "error_code": "NO_FILE_LOADED",
                "message": "没有加载的文件",
                "suggested_action": "请先加载一个 Excel 文件"
            }
        
        # 添加工作簿到参数
        params['workbook'] = workbook
        
        # 调用工作表管理器
        result = self.sheet_manager.rename_sheet(params)
        
        # 如果成功，更新文件信息
        if result['status'] == 'success':
            # 重新获取文件信息
            file_info = self.file_loader.get_file_info()
            if file_info:
                result['data']['file_info'] = file_info
        
        return result
    
    # ===== 批量操作处理器 =====
    
    def handle_batch_process(self, params: dict) -> dict:
        """处理批量处理命令"""
        return self.batch_processor.process(params)
    
    def handle_cancel_batch(self, params: dict) -> dict:
        """处理取消批量处理命令"""
        self.batch_processor.cancel()
        return {
            "type": "result",
            "status": "success",
            "message": "已请求取消批量处理"
        }
    
    def _process_all_sheets(self, processor_func, params: dict, operation_name: str) -> dict:
        """
        对所有工作表执行处理操作
        
        Args:
            processor_func: 处理函数
            params: 参数
            operation_name: 操作名称（用于日志）
        
        Returns:
            dict, 处理结果
        """
        # 获取当前工作簿
        workbook = self.file_loader.get_current_workbook()
        
        if not workbook:
            return {
                "type": "result",
                "status": "error",
                "error_code": "NO_FILE_LOADED",
                "message": "没有加载的文件",
                "suggested_action": "请先加载一个 Excel 文件"
            }
        
        try:
            # 获取所有工作表
            sheet_names = workbook.sheetnames
            total_sheets = len(sheet_names)
            
            log(f"Processing {total_sheets} sheets for operation: {operation_name}")
            
            # 处理每个工作表
            results = []
            
            for idx, sheet_name in enumerate(sheet_names):
                log(f"Processing sheet {idx + 1}/{total_sheets}: {sheet_name}")
                
                # 发送进度
                progress = int((idx / total_sheets) * 100)
                send({
                    "type": "progress",
                    "progress": progress,
                    "message": f"正在处理工作表: {sheet_name} ({idx + 1}/{total_sheets})"
                })
                
                # 获取工作表
                worksheet = workbook[sheet_name]
                
                # 添加工作表到参数
                sheet_params = params.copy()
                sheet_params['worksheet'] = worksheet
                sheet_params['sheet_name'] = sheet_name
                
                # 执行处理
                result = processor_func(sheet_params)
                
                if result['status'] == 'success':
                    results.append(result.get('data', {}))
                else:
                    # 如果某个工作表处理失败，记录但继续处理其他工作表
                    log(f"Error processing sheet {sheet_name}: {result.get('message')}")
                    results.append({
                        "sheet_name": sheet_name,
                        "error": result.get('message')
                    })
            
            # 汇总结果
            success_count = sum(1 for r in results if 'error' not in r)
            
            return {
                "type": "result",
                "status": "success",
                "message": f"{operation_name}完成，成功处理 {success_count}/{total_sheets} 个工作表",
                "data": {
                    "operation": operation_name,
                    "total_sheets": total_sheets,
                    "success_count": success_count,
                    "results": results
                }
            }
            
        except Exception as e:
            log(f"Error in _process_all_sheets: {str(e)}")
            return {
                "type": "result",
                "status": "error",
                "error_code": "PROCESS_ERROR",
                "message": f"{operation_name}失败: {str(e)}"
            }


def main():
    """主函数"""
    log("Excel Toolkit Backend starting...")
    
    # 创建路由器
    router = CommandRouter()
    
    # 发送启动成功消息
    send({
        "type": "startup",
        "status": "ready",
        "message": "Backend initialized successfully"
    })
    
    # 主循环：持续监听 stdin
    for line in sys.stdin:
        line = line.strip()
        
        if not line:
            continue
        
        try:
            # 解析 JSON 命令
            command = json.loads(line)
            action = command.get('action', 'unknown')
            
            log(f"Received command: {action}")
            
            # 路由并处理命令
            result = router.route(command)
            
            # 输出结果到 stdout
            send(result)
            
        except json.JSONDecodeError as e:
            log(f"JSON decode error: {str(e)}")
            send({
                "type": "result",
                "status": "error",
                "error_code": "INVALID_JSON",
                "message": f"无效的 JSON 格式: {str(e)}"
            })
        
        except Exception as e:
            log(f"Unexpected error: {str(e)}")
            send({
                "type": "result",
                "status": "error",
                "error_code": "INTERNAL_ERROR",
                "message": f"内部错误: {str(e)}"
            })
    
    log("Backend shutting down...")


if __name__ == "__main__":
    main()
