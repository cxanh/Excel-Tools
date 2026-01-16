#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Content Processor - 内容处理模块
负责 Excel 内容的各种处理操作
"""

import sys
import re
from typing import Dict, Any, List, Set, Optional
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter


def log(message):
    """将日志输出到 stderr"""
    sys.stderr.write(f"[PROCESSOR] {message}\n")
    sys.stderr.flush()


def send_progress(progress, message="", data=None):
    """发送进度消息"""
    import json
    progress_msg = {
        "type": "progress",
        "progress": progress,
        "message": message
    }
    if data:
        progress_msg["data"] = data
    
    print(json.dumps(progress_msg), flush=True)


class ContentProcessor:
    """内容处理器"""
    
    def __init__(self):
        """初始化内容处理器"""
        pass
    
    def remove_blank_rows(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        删除空白行
        
        Args:
            params: dict, 包含以下字段：
                - worksheet: Worksheet 对象（必需）
                - sheet_name: str, 工作表名称（用于日志）
        
        Returns:
            dict, 处理结果
        """
        worksheet = params.get('worksheet')
        sheet_name = params.get('sheet_name', 'Unknown')
        
        if not worksheet:
            return self._error_response(
                "MISSING_WORKSHEET",
                "缺少工作表对象"
            )
        
        try:
            log(f"Removing blank rows from sheet: {sheet_name}")
            
            # 获取所有行
            max_row = worksheet.max_row
            max_col = worksheet.max_column
            
            # 标记要删除的行
            rows_to_delete = []
            
            for row_idx in range(1, max_row + 1):
                # 检查该行是否为空
                is_blank = True
                for col_idx in range(1, max_col + 1):
                    cell_value = worksheet.cell(row_idx, col_idx).value
                    if cell_value is not None and str(cell_value).strip() != '':
                        is_blank = False
                        break
                
                if is_blank:
                    rows_to_delete.append(row_idx)
                
                # 发送进度
                if row_idx % 100 == 0:
                    progress = int(row_idx / max_row * 100)
                    send_progress(progress, f"正在扫描第 {row_idx}/{max_row} 行")
            
            # 从后往前删除行（避免索引变化）
            deleted_count = 0
            for row_idx in reversed(rows_to_delete):
                worksheet.delete_rows(row_idx, 1)
                deleted_count += 1
            
            log(f"Removed {deleted_count} blank rows from sheet: {sheet_name}")
            
            return {
                "type": "result",
                "status": "success",
                "message": f"成功删除 {deleted_count} 个空白行",
                "data": {
                    "sheet_name": sheet_name,
                    "deleted_count": deleted_count,
                    "original_rows": max_row,
                    "remaining_rows": max_row - deleted_count
                }
            }
            
        except Exception as e:
            log(f"Error removing blank rows: {str(e)}")
            return self._error_response(
                "PROCESS_ERROR",
                f"删除空白行失败: {str(e)}"
            )
    
    def clear_blank_cells(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        清除空白单元格内容（保留结构）
        
        Args:
            params: dict, 包含以下字段：
                - worksheet: Worksheet 对象（必需）
                - sheet_name: str, 工作表名称（用于日志）
        
        Returns:
            dict, 处理结果
        """
        worksheet = params.get('worksheet')
        sheet_name = params.get('sheet_name', 'Unknown')
        
        if not worksheet:
            return self._error_response(
                "MISSING_WORKSHEET",
                "缺少工作表对象"
            )
        
        try:
            log(f"Clearing blank cells from sheet: {sheet_name}")
            
            max_row = worksheet.max_row
            max_col = worksheet.max_column
            cleared_count = 0
            
            for row_idx in range(1, max_row + 1):
                for col_idx in range(1, max_col + 1):
                    cell = worksheet.cell(row_idx, col_idx)
                    if cell.value is not None and str(cell.value).strip() == '':
                        cell.value = None
                        cleared_count += 1
                
                # 发送进度
                if row_idx % 100 == 0:
                    progress = int(row_idx / max_row * 100)
                    send_progress(progress, f"正在处理第 {row_idx}/{max_row} 行")
            
            log(f"Cleared {cleared_count} blank cells from sheet: {sheet_name}")
            
            return {
                "type": "result",
                "status": "success",
                "message": f"成功清除 {cleared_count} 个空白单元格",
                "data": {
                    "sheet_name": sheet_name,
                    "cleared_count": cleared_count
                }
            }
            
        except Exception as e:
            log(f"Error clearing blank cells: {str(e)}")
            return self._error_response(
                "PROCESS_ERROR",
                f"清除空白单元格失败: {str(e)}"
            )
    
    def remove_formulas(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        删除公式（保留计算结果值）
        
        Args:
            params: dict, 包含以下字段：
                - worksheet: Worksheet 对象（必需）
                - sheet_name: str, 工作表名称（用于日志）
        
        Returns:
            dict, 处理结果
        """
        worksheet = params.get('worksheet')
        sheet_name = params.get('sheet_name', 'Unknown')
        
        if not worksheet:
            return self._error_response(
                "MISSING_WORKSHEET",
                "缺少工作表对象"
            )
        
        try:
            log(f"Removing formulas from sheet: {sheet_name}")
            
            max_row = worksheet.max_row
            max_col = worksheet.max_column
            formula_count = 0
            
            for row_idx in range(1, max_row + 1):
                for col_idx in range(1, max_col + 1):
                    cell = worksheet.cell(row_idx, col_idx)
                    
                    # 如果单元格包含公式
                    if cell.data_type == 'f':
                        # 保存当前值
                        current_value = cell.value
                        # 将公式替换为值
                        cell.value = current_value
                        formula_count += 1
                
                # 发送进度
                if row_idx % 100 == 0:
                    progress = int(row_idx / max_row * 100)
                    send_progress(progress, f"正在处理第 {row_idx}/{max_row} 行")
            
            log(f"Removed {formula_count} formulas from sheet: {sheet_name}")
            
            return {
                "type": "result",
                "status": "success",
                "message": f"成功删除 {formula_count} 个公式",
                "data": {
                    "sheet_name": sheet_name,
                    "formula_count": formula_count
                }
            }
            
        except Exception as e:
            log(f"Error removing formulas: {str(e)}")
            return self._error_response(
                "PROCESS_ERROR",
                f"删除公式失败: {str(e)}"
            )
    
    def remove_duplicate_rows(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        删除重复行
        
        Args:
            params: dict, 包含以下字段：
                - worksheet: Worksheet 对象（必需）
                - sheet_name: str, 工作表名称（用于日志）
                - key_columns: list, 用于判断重复的关键列索引（可选，默认使用所有列）
                - keep_first: bool, 是否保留第一次出现的行（可选，默认 True）
        
        Returns:
            dict, 处理结果
        """
        worksheet = params.get('worksheet')
        sheet_name = params.get('sheet_name', 'Unknown')
        key_columns = params.get('key_columns')
        keep_first = params.get('keep_first', True)
        
        if not worksheet:
            return self._error_response(
                "MISSING_WORKSHEET",
                "缺少工作表对象"
            )
        
        try:
            log(f"Removing duplicate rows from sheet: {sheet_name}")
            
            max_row = worksheet.max_row
            max_col = worksheet.max_column
            
            # 如果没有指定关键列，使用所有列
            if not key_columns:
                key_columns = list(range(1, max_col + 1))
            
            # 记录已见过的行
            seen_rows: Set[tuple] = set()
            rows_to_delete = []
            
            for row_idx in range(1, max_row + 1):
                # 提取关键列的值
                row_key = tuple(
                    str(worksheet.cell(row_idx, col_idx).value) if worksheet.cell(row_idx, col_idx).value is not None else ''
                    for col_idx in key_columns
                )
                
                if row_key in seen_rows:
                    # 重复行
                    rows_to_delete.append(row_idx)
                else:
                    # 第一次出现
                    seen_rows.add(row_key)
                
                # 发送进度
                if row_idx % 100 == 0:
                    progress = int(row_idx / max_row * 50)  # 扫描阶段占 50%
                    send_progress(progress, f"正在扫描第 {row_idx}/{max_row} 行")
            
            # 从后往前删除行
            deleted_count = 0
            total_to_delete = len(rows_to_delete)
            
            for idx, row_idx in enumerate(reversed(rows_to_delete)):
                worksheet.delete_rows(row_idx, 1)
                deleted_count += 1
                
                # 发送进度
                if idx % 10 == 0:
                    progress = 50 + int(idx / total_to_delete * 50)  # 删除阶段占 50%
                    send_progress(progress, f"正在删除第 {idx + 1}/{total_to_delete} 个重复行")
            
            log(f"Removed {deleted_count} duplicate rows from sheet: {sheet_name}")
            
            return {
                "type": "result",
                "status": "success",
                "message": f"成功删除 {deleted_count} 个重复行",
                "data": {
                    "sheet_name": sheet_name,
                    "deleted_count": deleted_count,
                    "original_rows": max_row,
                    "remaining_rows": max_row - deleted_count,
                    "key_columns": key_columns
                }
            }
            
        except Exception as e:
            log(f"Error removing duplicate rows: {str(e)}")
            return self._error_response(
                "PROCESS_ERROR",
                f"删除重复行失败: {str(e)}"
            )
    
    def replace_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        按规则替换内容
        
        Args:
            params: dict, 包含以下字段：
                - worksheet: Worksheet 对象（必需）
                - sheet_name: str, 工作表名称（用于日志）
                - find_text: str, 要查找的文本（必需）
                - replace_text: str, 替换为的文本（必需）
                - use_regex: bool, 是否使用正则表达式（可选，默认 False）
                - case_sensitive: bool, 是否区分大小写（可选，默认 False）
                - whole_word: bool, 是否全词匹配（可选，默认 False）
        
        Returns:
            dict, 处理结果
        """
        worksheet = params.get('worksheet')
        sheet_name = params.get('sheet_name', 'Unknown')
        find_text = params.get('find_text')
        replace_text = params.get('replace_text', '')
        use_regex = params.get('use_regex', False)
        case_sensitive = params.get('case_sensitive', False)
        whole_word = params.get('whole_word', False)
        
        if not worksheet:
            return self._error_response(
                "MISSING_WORKSHEET",
                "缺少工作表对象"
            )
        
        if find_text is None:
            return self._error_response(
                "MISSING_FIND_TEXT",
                "缺少查找文本参数"
            )
        
        try:
            log(f"Replacing content in sheet: {sheet_name}")
            
            max_row = worksheet.max_row
            max_col = worksheet.max_column
            replace_count = 0
            
            # 编译正则表达式（如果使用）
            if use_regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                try:
                    pattern = re.compile(find_text, flags)
                except re.error as e:
                    return self._error_response(
                        "INVALID_REGEX",
                        f"无效的正则表达式: {str(e)}"
                    )
            
            for row_idx in range(1, max_row + 1):
                for col_idx in range(1, max_col + 1):
                    cell = worksheet.cell(row_idx, col_idx)
                    
                    if cell.value is None:
                        continue
                    
                    cell_value = str(cell.value)
                    
                    # 执行替换
                    if use_regex:
                        # 正则表达式替换
                        new_value = pattern.sub(replace_text, cell_value)
                        if new_value != cell_value:
                            cell.value = new_value
                            replace_count += 1
                    else:
                        # 普通文本替换
                        if whole_word:
                            # 全词匹配
                            pattern = r'\b' + re.escape(find_text) + r'\b'
                            flags = 0 if case_sensitive else re.IGNORECASE
                            new_value = re.sub(pattern, replace_text, cell_value, flags=flags)
                        else:
                            # 普通替换
                            if case_sensitive:
                                new_value = cell_value.replace(find_text, replace_text)
                            else:
                                # 不区分大小写的替换
                                pattern = re.compile(re.escape(find_text), re.IGNORECASE)
                                new_value = pattern.sub(replace_text, cell_value)
                        
                        if new_value != cell_value:
                            cell.value = new_value
                            replace_count += 1
                
                # 发送进度
                if row_idx % 100 == 0:
                    progress = int(row_idx / max_row * 100)
                    send_progress(progress, f"正在处理第 {row_idx}/{max_row} 行")
            
            log(f"Replaced {replace_count} cells in sheet: {sheet_name}")
            
            return {
                "type": "result",
                "status": "success",
                "message": f"成功替换 {replace_count} 个单元格",
                "data": {
                    "sheet_name": sheet_name,
                    "replace_count": replace_count,
                    "find_text": find_text,
                    "replace_text": replace_text,
                    "use_regex": use_regex,
                    "case_sensitive": case_sensitive,
                    "whole_word": whole_word
                }
            }
            
        except Exception as e:
            log(f"Error replacing content: {str(e)}")
            return self._error_response(
                "PROCESS_ERROR",
                f"替换内容失败: {str(e)}"
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
