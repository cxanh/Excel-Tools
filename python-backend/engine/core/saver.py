#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Saver - 文件保存模块
负责保存 Excel 文件，包括备份和恢复功能
"""

import os
import sys
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime
import openpyxl


def log(message):
    """将日志输出到 stderr"""
    sys.stderr.write(f"[SAVER] {message}\n")
    sys.stderr.flush()


class FileSaver:
    """文件保存器"""
    
    # 备份配置
    MAX_BACKUPS = 5  # 最多保留 5 个备份
    BACKUP_SUFFIX = ".backup"
    
    def __init__(self):
        """初始化文件保存器"""
        self.backup_dir = None
    
    def save(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存 Excel 文件
        
        Args:
            params: dict, 包含以下字段：
                - workbook: Workbook 对象（必需）
                - file_path: str, 保存路径（必需）
                - create_backup: bool, 是否创建备份（可选，默认 True）
                - overwrite: bool, 是否覆盖已存在的文件（可选，默认 False）
        
        Returns:
            dict, 保存结果
        """
        workbook = params.get('workbook')
        file_path = params.get('file_path')
        create_backup = params.get('create_backup', True)
        overwrite = params.get('overwrite', False)
        
        # 验证参数
        if not workbook:
            return self._error_response(
                "MISSING_WORKBOOK",
                "缺少工作簿对象"
            )
        
        if not file_path:
            return self._error_response(
                "MISSING_FILE_PATH",
                "缺少文件路径参数"
            )
        
        # 检查文件是否已存在
        if os.path.exists(file_path) and not overwrite:
            return self._error_response(
                "FILE_EXISTS",
                f"文件已存在: {file_path}",
                suggested_action="请设置 overwrite=True 以覆盖文件，或选择其他文件名"
            )
        
        # 如果文件已存在且需要备份，先创建备份
        backup_path = None
        if os.path.exists(file_path) and create_backup:
            backup_result = self._create_backup(file_path)
            if backup_result['status'] == 'error':
                return backup_result
            backup_path = backup_result.get('backup_path')
        
        # 保存文件
        try:
            log(f"Saving file: {file_path}")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
            
            # 保存工作簿
            workbook.save(file_path)
            
            log(f"Successfully saved file: {file_path}")
            
            result_data = {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_size": os.path.getsize(file_path)
            }
            
            if backup_path:
                result_data["backup_created"] = True
                result_data["backup_path"] = backup_path
            
            return {
                "type": "result",
                "status": "success",
                "message": "文件保存成功",
                "data": result_data
            }
            
        except PermissionError:
            log(f"Permission denied: {file_path}")
            
            # 如果保存失败且创建了备份，尝试恢复
            if backup_path:
                self._restore_from_backup(backup_path, file_path)
            
            return self._error_response(
                "FILE_IN_USE",
                "文件正在被其他程序使用，无法保存",
                suggested_action="请关闭 Microsoft Excel 或其他正在使用该文件的程序"
            )
        
        except Exception as e:
            log(f"Error saving file: {str(e)}")
            
            # 如果保存失败且创建了备份，尝试恢复
            if backup_path:
                self._restore_from_backup(backup_path, file_path)
            
            return self._error_response(
                "SAVE_ERROR",
                f"保存文件失败: {str(e)}"
            )
    
    def _create_backup(self, file_path: str) -> Dict[str, Any]:
        """
        创建文件备份
        
        Args:
            file_path: 原文件路径
        
        Returns:
            dict, 备份结果
        """
        try:
            # 生成备份文件名（带时间戳，包含微秒）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            file_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            file_base, file_ext = os.path.splitext(file_name)
            
            # 创建备份目录
            backup_dir = os.path.join(file_dir, f".{file_base}_backups")
            os.makedirs(backup_dir, exist_ok=True)
            self.backup_dir = backup_dir
            
            # 备份文件路径
            backup_name = f"{file_base}_{timestamp}{self.BACKUP_SUFFIX}{file_ext}"
            backup_path = os.path.join(backup_dir, backup_name)
            
            # 复制文件
            log(f"Creating backup: {backup_path}")
            shutil.copy2(file_path, backup_path)
            
            # 清理旧备份
            self._cleanup_old_backups(backup_dir, file_base, file_ext)
            
            log(f"Backup created successfully: {backup_path}")
            
            return {
                "status": "success",
                "backup_path": backup_path
            }
            
        except Exception as e:
            log(f"Error creating backup: {str(e)}")
            return self._error_response(
                "BACKUP_ERROR",
                f"创建备份失败: {str(e)}"
            )
    
    def _cleanup_old_backups(self, backup_dir: str, file_base: str, file_ext: str):
        """
        清理旧备份，只保留最近的 MAX_BACKUPS 个
        
        Args:
            backup_dir: 备份目录
            file_base: 文件基础名
            file_ext: 文件扩展名
        """
        try:
            # 获取所有备份文件
            backup_files = []
            for filename in os.listdir(backup_dir):
                if filename.startswith(file_base) and filename.endswith(file_ext):
                    file_path = os.path.join(backup_dir, filename)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            # 按修改时间排序（最新的在前）
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # 删除超过限制的备份
            if len(backup_files) > self.MAX_BACKUPS:
                for file_path, _ in backup_files[self.MAX_BACKUPS:]:
                    log(f"Removing old backup: {file_path}")
                    os.remove(file_path)
                    
        except Exception as e:
            log(f"Error cleaning up old backups: {str(e)}")
    
    def _restore_from_backup(self, backup_path: str, target_path: str) -> bool:
        """
        从备份恢复文件
        
        Args:
            backup_path: 备份文件路径
            target_path: 目标文件路径
        
        Returns:
            bool, 是否恢复成功
        """
        try:
            log(f"Restoring from backup: {backup_path} -> {target_path}")
            shutil.copy2(backup_path, target_path)
            log("File restored successfully")
            return True
        except Exception as e:
            log(f"Error restoring from backup: {str(e)}")
            return False
    
    def restore(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        从备份恢复文件
        
        Args:
            params: dict, 包含以下字段：
                - file_path: str, 原文件路径（必需）
                - backup_index: int, 备份索引（可选，默认 0 表示最新备份）
        
        Returns:
            dict, 恢复结果
        """
        file_path = params.get('file_path')
        backup_index = params.get('backup_index', 0)
        
        if not file_path:
            return self._error_response(
                "MISSING_FILE_PATH",
                "缺少文件路径参数"
            )
        
        # 获取备份列表
        backups = self._list_backups(file_path)
        
        if not backups:
            return self._error_response(
                "NO_BACKUPS",
                "没有找到备份文件",
                suggested_action="请确认文件是否曾经保存过"
            )
        
        if backup_index >= len(backups):
            return self._error_response(
                "INVALID_BACKUP_INDEX",
                f"备份索引超出范围: {backup_index}",
                suggested_action=f"可用的备份索引: 0-{len(backups)-1}"
            )
        
        # 获取指定的备份
        backup_path = backups[backup_index]['path']
        
        # 恢复文件
        try:
            log(f"Restoring file from backup: {backup_path}")
            shutil.copy2(backup_path, file_path)
            
            return {
                "type": "result",
                "status": "success",
                "message": "文件恢复成功",
                "data": {
                    "file_path": file_path,
                    "backup_path": backup_path,
                    "backup_time": backups[backup_index]['time']
                }
            }
            
        except Exception as e:
            log(f"Error restoring file: {str(e)}")
            return self._error_response(
                "RESTORE_ERROR",
                f"恢复文件失败: {str(e)}"
            )
    
    def list_backups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        列出文件的所有备份
        
        Args:
            params: dict, 包含以下字段：
                - file_path: str, 文件路径（必需）
        
        Returns:
            dict, 备份列表
        """
        file_path = params.get('file_path')
        
        if not file_path:
            return self._error_response(
                "MISSING_FILE_PATH",
                "缺少文件路径参数"
            )
        
        backups = self._list_backups(file_path)
        
        return {
            "type": "result",
            "status": "success",
            "message": f"找到 {len(backups)} 个备份",
            "data": {
                "file_path": file_path,
                "backup_count": len(backups),
                "backups": backups
            }
        }
    
    def _list_backups(self, file_path: str) -> List[Dict[str, Any]]:
        """
        获取文件的备份列表
        
        Args:
            file_path: 文件路径
        
        Returns:
            list, 备份信息列表
        """
        file_dir = os.path.dirname(file_path) or '.'
        file_name = os.path.basename(file_path)
        file_base, file_ext = os.path.splitext(file_name)
        
        # 备份目录
        backup_dir = os.path.join(file_dir, f".{file_base}_backups")
        
        if not os.path.exists(backup_dir):
            return []
        
        # 获取所有备份文件
        backups = []
        try:
            for filename in os.listdir(backup_dir):
                if filename.startswith(file_base) and filename.endswith(file_ext):
                    backup_path = os.path.join(backup_dir, filename)
                    mtime = os.path.getmtime(backup_path)
                    backups.append({
                        "path": backup_path,
                        "name": filename,
                        "time": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        "size": os.path.getsize(backup_path)
                    })
            
            # 按时间排序（最新的在前）
            backups.sort(key=lambda x: x['time'], reverse=True)
            
        except Exception as e:
            log(f"Error listing backups: {str(e)}")
        
        return backups
    
    def delete_backup(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        删除指定的备份
        
        Args:
            params: dict, 包含以下字段：
                - backup_path: str, 备份文件路径（必需）
        
        Returns:
            dict, 删除结果
        """
        backup_path = params.get('backup_path')
        
        if not backup_path:
            return self._error_response(
                "MISSING_BACKUP_PATH",
                "缺少备份文件路径参数"
            )
        
        if not os.path.exists(backup_path):
            return self._error_response(
                "BACKUP_NOT_FOUND",
                f"备份文件不存在: {backup_path}"
            )
        
        try:
            log(f"Deleting backup: {backup_path}")
            os.remove(backup_path)
            
            return {
                "type": "result",
                "status": "success",
                "message": "备份删除成功",
                "data": {
                    "backup_path": backup_path
                }
            }
            
        except Exception as e:
            log(f"Error deleting backup: {str(e)}")
            return self._error_response(
                "DELETE_ERROR",
                f"删除备份失败: {str(e)}"
            )
    
    def _error_response(self, error_code: str, message: str, suggested_action: Optional[str] = None) -> Dict[str, Any]:
        """
        生成错误响应
        
        Args:
            error_code: 错误代码
            message: 错误消息
            suggested_action: 建议的解决方案（可选）
        
        Returns:
            dict, 错误响应
        """
        response = {
            "type": "result",
            "status": "error",
            "error_code": error_code,
            "message": message
        }
        
        if suggested_action:
            response["suggested_action"] = suggested_action
        
        return response
