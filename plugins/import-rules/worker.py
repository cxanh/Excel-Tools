import io
import openpyxl
import re
import sys

# 默认设置
DEFAULT_SETTINGS = {
    'caseSensitive': False,
    'matchEntireCell': False,
    'ignoreHiddenCells': True,
    'sheetOption': 'all',
    'selectedSheets': '',
    'rangeOption': 'all',
    'customRange': '',
    'enableDetailedLogs': True
}

# 处理内容替换
def process(data):
    # 解析输入数据
    file_content = data['file']
    file_name = data['fileName']
    settings = data['settings']
    replacement_rules = settings.get('replacementRules', [])
    
    logs = []
    
    # 使用默认设置或传入的设置
    current_settings = DEFAULT_SETTINGS.copy()
    if settings:
        current_settings.update(settings)
    
    try:
        # 加载Excel文件
        wb = openpyxl.load_workbook(io.BytesIO(file_content))
        logs.append(f"成功加载Excel文件: {file_name}，包含 {len(wb.sheetnames)} 个工作表")
        
        if current_settings['enableDetailedLogs']:
            logs.append(f"工作表列表: {', '.join(wb.sheetnames)}")
        
        # 确定要处理的工作表
        sheets_to_process = []
        
        if current_settings['sheetOption'] == 'all':
            sheets_to_process = wb.sheetnames
        elif current_settings['sheetOption'] == 'active':
            sheets_to_process = [wb.active.title]
        elif current_settings['sheetOption'] == 'selected':
            selected_sheets = [name.strip() for name in current_settings['selectedSheets'].split(',')]
            sheets_to_process = [sheet for sheet in selected_sheets if sheet in wb.sheetnames]
            if not sheets_to_process:
                logs.append(f"警告: 未找到指定的工作表，将处理所有工作表")
                sheets_to_process = wb.sheetnames
        
        total_replacements = 0
        
        # 遍历需要处理的工作表
        for sheet_name in sheets_to_process:
            ws = wb[sheet_name]
            sheet_replacements = 0
            cell_replacements = 0
            
            logs.append(f"处理工作表: {sheet_name}")
            
            # 获取处理范围
            if current_settings['rangeOption'] == 'custom' and current_settings['customRange']:
                # 解析自定义范围，例如 "A1:D100"
                import re
                range_match = re.match(r'([A-Z]+)(\d+):([A-Z]+)(\d+)', current_settings['customRange'].upper())
                if range_match:
                    start_col = openpyxl.utils.column_index_from_string(range_match.group(1))
                    start_row = int(range_match.group(2))
                    end_col = openpyxl.utils.column_index_from_string(range_match.group(3))
                    end_row = int(range_match.group(4))
                    logs.append(f"  自定义范围: {current_settings['customRange']} (A1坐标: {start_row},{start_col} 到 {end_row},{end_col})")
                else:
                    logs.append(f"  无效的范围格式: {current_settings['customRange']}，将处理整个工作表")
                    start_row, start_col = 1, 1
                    end_row, end_col = ws.max_row, ws.max_column
            elif current_settings['rangeOption'] == 'data':
                # 仅处理数据区域
                start_row, start_col = 1, 1
                end_row, end_col = ws.max_row, ws.max_column
                logs.append(f"  数据区域范围: A{start_row}:{openpyxl.utils.get_column_letter(end_col)}{end_row}")
            else:
                # 处理整个工作表
                start_row, start_col = 1, 1
                end_row, end_col = ws.max_row, ws.max_column
                logs.append(f"  整个工作表范围: A{start_row}:{openpyxl.utils.get_column_letter(end_col)}{end_row}")
            
            if current_settings['enableDetailedLogs']:
                logs.append(f"  开始行: {start_row}, 结束行: {end_row}")
                logs.append(f"  开始列: {openpyxl.utils.get_column_letter(start_col)}, 结束列: {openpyxl.utils.get_column_letter(end_col)}")
            
            # 遍历单元格
            for row in range(start_row, end_row + 1):
                for col in range(start_col, end_col + 1):
                    cell = ws.cell(row=row, column=col)
                    
                    # 检查是否需要忽略隐藏单元格
                    if current_settings['ignoreHiddenCells']:
                        # 检查行是否隐藏
                        if ws.row_dimensions[row].hidden:
                            continue
                        # 检查列是否隐藏
                        if ws.column_dimensions[openpyxl.utils.get_column_letter(col)].hidden:
                            continue
                    
                    # 只处理有值的单元格
                    if cell.value is not None:
                        original_value = str(cell.value)
                        modified_value = original_value
                        cell_changed = False
                        
                        # 应用所有替换规则
                        for rule in replacement_rules:
                            find_text = rule['findText']
                            replace_text = rule['replaceText']
                            match_mode = rule['matchMode']
                            
                            if not find_text:
                                continue
                            
                            # 确定正则标志
                            flags = re.IGNORECASE if not current_settings['caseSensitive'] else 0
                            
                            if match_mode == 'regex':
                                # 使用正则表达式替换
                                try:
                                    if current_settings['matchEntireCell']:
                                        if re.fullmatch(find_text, modified_value, flags=flags):
                                            modified_value = re.sub(find_text, replace_text, modified_value, flags=flags)
                                            cell_changed = True
                                    else:
                                        if re.search(find_text, modified_value, flags=flags):
                                            modified_value = re.sub(find_text, replace_text, modified_value, flags=flags)
                                            cell_changed = True
                                except re.error as e:
                                    logs.append(f"  正则表达式错误: {str(e)}")
                                    continue
                            else:
                                # 使用普通文本替换
                                if not current_settings['caseSensitive']:
                                    # 不区分大小写的普通替换
                                    if current_settings['matchEntireCell']:
                                        if modified_value.lower() == find_text.lower():
                                            modified_value = replace_text
                                            cell_changed = True
                                    else:
                                        if modified_value.lower().find(find_text.lower()) != -1:
                                            modified_value = modified_value.lower().replace(find_text.lower(), replace_text)
                                            # 保持原始大小写结构（简单实现）
                                            if replace_text:
                                                # 这是一个简单的实现，可能需要更复杂的逻辑
                                                # 来保持原始文本的大小写结构
                                                pass
                                            cell_changed = True
                                else:
                                    # 区分大小写的普通替换
                                    if current_settings['matchEntireCell']:
                                        if modified_value == find_text:
                                            modified_value = replace_text
                                            cell_changed = True
                                    else:
                                        if modified_value.find(find_text) != -1:
                                            modified_value = modified_value.replace(find_text, replace_text)
                                            cell_changed = True
                        
                        # 如果单元格内容发生了变化，更新单元格
                        if cell_changed:
                            try:
                                # 尝试保持原始数据类型
                                if isinstance(cell.value, (int, float)) and modified_value.isdigit():
                                    cell.value = int(modified_value)
                                elif isinstance(cell.value, float) and modified_value.replace('.', '', 1).isdigit():
                                    cell.value = float(modified_value)
                                else:
                                    cell.value = modified_value
                                cell_replacements += 1
                                sheet_replacements += 1
                            except ValueError:
                                # 如果类型转换失败，使用字符串
                                cell.value = modified_value
                                cell_replacements += 1
                                sheet_replacements += 1
            
            logs.append(f"  工作表 {sheet_name} 处理完成，共替换 {sheet_replacements} 处内容")
            total_replacements += sheet_replacements
        
        logs.append(f"所有工作表处理完成，总替换次数: {total_replacements}")
        
        # 将处理结果写入内存
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return {
            'success': True,
            'buffer': output.read(),
            'logs': logs
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logs.append(f"错误: {str(e)}")
        logs.append(f"详细错误: {error_trace}")
        return {
            'success': False,
            'error': str(e),
            'logs': logs
        }

# 为了保持向后兼容性，保留原函数接口作为别名
def replace_content_in_excel(file_bytes, replacement_rules, settings=None):
    # 构造data对象以调用新的process函数
    data = {
        'file': file_bytes,
        'fileName': 'unknown.xlsx',
        'settings': settings or {}
    }
    data['settings']['replacementRules'] = replacement_rules
    return process(data)

# 主入口函数
if __name__ == "__main__":
    # 在浏览器环境中，Pyodide会通过其他方式调用该函数
    pass