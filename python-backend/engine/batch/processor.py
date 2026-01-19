#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Processor - 批量处理器
负责批量处理多个 Excel 文件
"""

import sys
import time
from typing import Dict, Any, List


def log(message):
    """将日志输出到 stderr"""
    sys.stderr.write(f"[BATCH_PROCESSOR] {message}\n")
    sys.stderr.flush()


def send_progress(progress, message="", data=None):
    """发送进度消息"""
    import json
    progress_msg = {
        "type": "batch_progress",
        "progress": progress,
        "message": message
    }
    if data:
        progress_msg["data"] = data
    
    print(json.dumps(progress_msg, ensure_ascii=False), flush=True)


class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, file_loader, file_saver, operation_handler):
        """
        初始化批量处理器
        
        Args:
            file_loader: 文件加载器
            file_saver: 文件保存器
            operation_handler: 操作处理器（CommandRouter）
        """
        self.file_loader = file_loader
        self.file_saver = file_saver
        self.operation_handler = operation_handler
        self.cancelled = False
    
    def process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        批量处理文件
        
        Args:
            params: dict, 包含以下字段：
                - files: list, 文件路径列表
                - operation: str, 操作类型
                - operation_params: dict, 操作参数
                - save_files: bool, 是否保存文件（可选，默认 True）
        
        Returns:
            dict, 批量处理结果
        """
        files = params.get('files', [])
        operation = params.get('operation')
        operation_params = params.get('operation_params', {})
        save_files = params.get('save_files', True)
        
        if not files:
            return {
                "type": "result",
                "status": "error",
                "error_code": "MISSING_FILES",
                "message": "缺少文件列表"
            }
        
        if not operation:
            return {
                "type": "result",
                "status": "error",
                "error_code": "MISSING_OPERATION",
                "message": "缺少操作类型"
            }
        
        log(f"Starting batch processing: {len(files)} files, operation: {operation}")
        
        total_files = len(files)
        results = []
        success_count = 0
        error_count = 0
        start_time = time.time()
        
        self.cancelled = False
        
        for index, file_path in enumerate(files):
            if self.cancelled:
                log("Batch processing cancelled by user")
                break
            
            file_name = file_path.split('\\')[-1].split('/')[-1]
            log(f"Processing file {index + 1}/{total_files}: {file_name}")
            
            # 发送整体进度
            overall_progress = int((index / total_files) * 100)
            send_progress(
                overall_progress,
                f"正在处理第 {index + 1}/{total_files} 个文件: {file_name}",
                {
                    "current_file": file_name,
                    "current_file_index": index + 1,
                    "total_files": total_files
                }
            )
            
            file_start_time = time.time()
            
            try:
                # 1. 加载文件
                load_result = self.file_loader.load({
                    "file_path": file_path
                })
                
                if load_result['status'] != 'success':
                    results.append({
                        "file": file_path,
                        "file_name": file_name,
                        "status": "error",
                        "message": load_result['message'],
                        "duration": int((time.time() - file_start_time) * 1000)
                    })
                    error_count += 1
                    continue
                
                # 2. 执行操作
                operation_result = self.operation_handler.route({
                    "action": operation,
                    "params": operation_params
                })
                
                if operation_result['status'] != 'success':
                    results.append({
                        "file": file_path,
                        "file_name": file_name,
                        "status": "error",
                        "message": operation_result['message'],
                        "duration": int((time.time() - file_start_time) * 1000)
                    })
                    error_count += 1
                    
                    # 关闭文件
                    self.file_loader.close()
                    continue
                
                # 3. 保存文件（如果需要）
                if save_files:
                    save_result = self.file_saver.save({
                        "workbook": self.file_loader.get_current_workbook(),
                        "file_path": file_path,
                        "overwrite": True,
                        "create_backup": True
                    })
                    
                    if save_result['status'] != 'success':
                        results.append({
                            "file": file_path,
                            "file_name": file_name,
                            "status": "error",
                            "message": f"保存失败: {save_result['message']}",
                            "duration": int((time.time() - file_start_time) * 1000)
                        })
                        error_count += 1
                        
                        # 关闭文件
                        self.file_loader.close()
                        continue
                
                # 4. 关闭文件
                self.file_loader.close()
                
                # 5. 记录成功结果
                results.append({
                    "file": file_path,
                    "file_name": file_name,
                    "status": "success",
                    "message": operation_result['message'],
                    "duration": int((time.time() - file_start_time) * 1000)
                })
                success_count += 1
                
            except Exception as e:
                log(f"Error processing file {file_name}: {str(e)}")
                results.append({
                    "file": file_path,
                    "file_name": file_name,
                    "status": "error",
                    "message": f"处理失败: {str(e)}",
                    "duration": int((time.time() - file_start_time) * 1000)
                })
                error_count += 1
                
                # 确保文件被关闭
                try:
                    self.file_loader.close()
                except:
                    pass
        
        # 发送完成进度
        send_progress(100, "批量处理完成")
        
        total_duration = int((time.time() - start_time) * 1000)
        
        log(f"Batch processing completed: {success_count} success, {error_count} errors")
        
        return {
            "type": "result",
            "status": "success" if error_count == 0 else "partial_success",
            "message": f"批量处理完成: 成功 {success_count}/{total_files} 个文件",
            "data": {
                "total_files": total_files,
                "success_count": success_count,
                "error_count": error_count,
                "cancelled": self.cancelled,
                "duration": total_duration,
                "results": results
            }
        }
    
    def cancel(self):
        """取消批量处理"""
        self.cancelled = True
        log("Batch processing cancellation requested")
