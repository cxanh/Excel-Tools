import sys
import os
from openpyxl import load_workbook
from io import BytesIO, StringIO
import json
import csv

# 设置标准输出为UTF-8
sys.stdout.reconfigure(encoding='utf-8')


def process(data):
    """
    从Excel文件中提取指定内容
    :param data: 包含file、fileName和settings的字典
    :return: 处理结果
    """
    try:
        # 获取输入参数
        file_content = data.get('file')
        settings = data.get('settings', {})
        extract_type = settings.get('extractType', 'columns')
        
        # 加载Excel文件
        workbook = load_workbook(filename=BytesIO(file_content))
        result = {}
        
        # 根据提取类型处理
        if extract_type == 'columns':
            result = extract_by_columns(workbook, settings)
        elif extract_type == 'rows':
            result = extract_by_rows(workbook, settings)
        elif extract_type == 'condition':
            result = extract_by_condition(workbook, settings)
        else:
            return {
                'success': False,
                'error': f'不支持的提取类型: {extract_type}'
            }
        
        return {
            'success': True,
            'data': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def extract_by_columns(workbook, settings):
    """
    按列提取内容
    :param workbook: Excel工作簿对象
    :param settings: 提取选项，包含：
        - sheetNames: 要处理的工作表名称列表
        - columns: 要提取的列索引列表（如：[0, 2, 4]）
    :return: 提取结果
    """
    sheet_names = settings.get('sheetNames', [])
    columns = settings.get('columns', [])
    result = {}
    
    # 如果没有指定工作表，处理所有工作表
    if not sheet_names:
        sheet_names = workbook.sheetnames
    
    for sheet_name in sheet_names:
        if sheet_name not in workbook.sheetnames:
            continue
        
        sheet = workbook[sheet_name]
        extracted_data = []
        
        # 获取表头
        header = []
        for col_idx in columns:
            header_cell = sheet.cell(row=1, column=col_idx + 1)
            header.append(header_cell.value or f'列{col_idx + 1}')
        extracted_data.append(header)
        
        # 获取数据行
        for row in sheet.iter_rows(min_row=2, values_only=True):
            extracted_row = []
            for col_idx in columns:
                if col_idx < len(row):
                    extracted_row.append(row[col_idx])
                else:
                    extracted_row.append('')
            extracted_data.append(extracted_row)
        
        result[sheet_name] = extracted_data
    
    return result


def extract_by_rows(workbook, settings):
    """
    按行提取内容
    :param workbook: Excel工作簿对象
    :param settings: 提取选项，包含：
        - sheetNames: 要处理的工作表名称列表
        - startRow: 开始行索引（从0开始）
        - endRow: 结束行索引（从0开始，-1表示到末尾）
    :return: 提取结果
    """
    sheet_names = settings.get('sheetNames', [])
    start_row = settings.get('startRow', 0)
    end_row = settings.get('endRow', -1)
    result = {}
    
    # 如果没有指定工作表，处理所有工作表
    if not sheet_names:
        sheet_names = workbook.sheetnames
    
    for sheet_name in sheet_names:
        if sheet_name not in workbook.sheetnames:
            continue
        
        sheet = workbook[sheet_name]
        extracted_data = []
        
        # 计算实际的开始行和结束行（openpyxl是从1开始的）
        actual_start_row = start_row + 1
        actual_end_row = sheet.max_row if end_row == -1 else end_row + 1
        
        # 提取指定行范围的数据
        for row in sheet.iter_rows(min_row=actual_start_row, max_row=actual_end_row, values_only=True):
            extracted_data.append(list(row))
        
        result[sheet_name] = extracted_data
    
    return result


def extract_by_condition(workbook, settings):
    """
    按条件提取内容
    :param workbook: Excel工作簿对象
    :param settings: 提取选项，包含：
        - sheetNames: 要处理的工作表名称列表
        - conditionColumn: 条件列索引（从0开始）
        - conditionType: 条件类型（eq, ne, gt, lt, ge, le, contains）
        - conditionValue: 条件值
    :return: 提取结果
    """
    sheet_names = settings.get('sheetNames', [])
    condition_column = settings.get('conditionColumn', 0)
    condition_type = settings.get('conditionType', 'eq')
    condition_value = settings.get('conditionValue', '')
    result = {}
    
    # 如果没有指定工作表，处理所有工作表
    if not sheet_names:
        sheet_names = workbook.sheetnames
    
    for sheet_name in sheet_names:
        if sheet_name not in workbook.sheetnames:
            continue
        
        sheet = workbook[sheet_name]
        extracted_data = []
        
        # 获取表头
        header = []
        for col in range(1, sheet.max_column + 1):
            header_cell = sheet.cell(row=1, column=col)
            header.append(header_cell.value or f'列{col}')
        extracted_data.append(header)
        
        # 提取符合条件的数据行
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if len(row) <= condition_column:
                continue
            
            cell_value = row[condition_column]
            if check_condition(cell_value, condition_value, condition_type):
                extracted_data.append(list(row))
        
        result[sheet_name] = extracted_data
    
    return result


def check_condition(cell_value, condition_value, condition_type):
    """
    检查单元格值是否符合条件
    :param cell_value: 单元格值
    :param condition_value: 条件值
    :param condition_type: 条件类型
    :return: 是否符合条件
    """
    try:
        # 尝试将字符串转换为数值进行比较
        if isinstance(cell_value, (int, float)) and isinstance(condition_value, str):
            condition_value = float(condition_value)
        elif isinstance(cell_value, str) and isinstance(condition_value, (int, float)):
            cell_value = float(cell_value)
    except (ValueError, TypeError):
        pass
    
    if condition_type == 'eq':
        return cell_value == condition_value
    elif condition_type == 'ne':
        return cell_value != condition_value
    elif condition_type == 'gt':
        return cell_value > condition_value
    elif condition_type == 'lt':
        return cell_value < condition_value
    elif condition_type == 'ge':
        return cell_value >= condition_value
    elif condition_type == 'le':
        return cell_value <= condition_value
    elif condition_type == 'contains':
        return str(condition_value) in str(cell_value)
    else:
        return False
