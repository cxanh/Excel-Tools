import io
import openpyxl
import os

def process(data):
    """将Excel文件拆分成多个文件"""
    file_content = data['file']
    file_name = data['fileName']
    settings = data.get('settings', {})
    split_mode = settings.get('splitMode', 'by_row')  # by_row, by_column, by_sheet
    split_options = settings.get('splitOptions', {})
    logs = []
    
    try:
        logs.append(f"正在加载文件: {file_name}")
        # 加载Excel文件
        wb = openpyxl.load_workbook(io.BytesIO(file_content), read_only=False)
        logs.append(f"文件加载成功，包含 {len(wb.sheetnames)} 个工作表")
        
        # 根据拆分模式执行不同的拆分逻辑
        if split_mode == 'by_sheet':
            # 按工作表拆分
            return split_by_sheet(wb, file_name, logs)
        else:
            # 按行数或列值拆分，仅处理单个工作表
            sheet_name = settings.get('sheetName', wb.active.title)
            if sheet_name not in wb.sheetnames:
                sheet_name = wb.active.title
            ws = wb[sheet_name]
            logs.append(f"正在处理工作表: {sheet_name}")
            
            if split_mode == 'by_row':
                # 按行数拆分
                return split_by_row(ws, file_name, split_options, logs)
            elif split_mode == 'by_column':
                # 按列值拆分
                return split_by_column(ws, file_name, split_options, logs)
            else:
                raise ValueError(f"不支持的拆分模式: {split_mode}")
        
    except Exception as e:
        logs.append(f"拆分失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'logs': logs
        }


def split_by_sheet(wb, original_file_name, logs):
    """按工作表拆分Excel文件"""
    logs.append("开始按工作表拆分")
    results = []
    
    for sheet_name in wb.sheetnames:
        logs.append(f"正在拆分工作表: {sheet_name}")
        
        # 创建新工作簿
        new_wb = openpyxl.Workbook()
        new_ws = new_wb.active
        new_ws.title = sheet_name
        
        # 复制数据
        source_ws = wb[sheet_name]
        
        # 复制列宽
        for col in source_ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            new_ws.column_dimensions[column].width = adjusted_width
        
        # 复制数据和样式
        for row in source_ws.iter_rows(min_row=1, max_row=source_ws.max_row, min_col=1, max_col=source_ws.max_column, values_only=False):
            for cell in row:
                new_cell = new_ws.cell(row=cell.row, column=cell.column, value=cell.value)
                # 复制单元格样式
                if cell.has_style:
                    new_cell.font = cell.font.copy()
                    new_cell.border = cell.border.copy()
                    new_cell.fill = cell.fill.copy()
                    new_cell.number_format = cell.number_format
                    new_cell.protection = cell.protection.copy()
                    new_cell.alignment = cell.alignment.copy()
        
        # 保存到缓冲区
        buffer = io.BytesIO()
        new_wb.save(buffer)
        buffer.seek(0)
        
        # 生成新文件名
        base_name = original_file_name.replace('.xlsx', '').replace('.xls', '')
        new_file_name = f"{base_name}_{sheet_name}.xlsx"
        
        results.append({
            'file_name': new_file_name,
            'buffer': buffer.read()
        })
        
        logs.append(f"工作表 {sheet_name} 拆分完成")
    
    logs.append(f"按工作表拆分完成，共生成 {len(results)} 个文件")
    return {
        'success': True,
        'logs': logs,
        'results': results,
        'details': {
            'splitMode': 'by_sheet',
            'fileCount': len(results)
        }
    }


def split_by_row(ws, original_file_name, split_options, logs):
    """按行数拆分Excel文件"""
    rows_per_file = split_options.get('rowsPerFile', 1000)
    logs.append(f"开始按行数拆分，每 {rows_per_file} 行一个文件")
    
    # 获取总行数
    total_rows = ws.max_row
    logs.append(f"总共有 {total_rows} 行数据")
    
    # 计算需要生成的文件数
    total_files = (total_rows + rows_per_file - 1) // rows_per_file
    logs.append(f"预计生成 {total_files} 个文件")
    
    results = []
    
    # 拆分数据
    for file_index in range(total_files):
        start_row = file_index * rows_per_file + 1
        end_row = min((file_index + 1) * rows_per_file, total_rows)
        logs.append(f"正在处理第 {file_index + 1} 个文件，处理行范围: {start_row} - {end_row}")
        
        # 创建新工作簿
        new_wb = openpyxl.Workbook()
        new_ws = new_wb.active
        new_ws.title = ws.title
        
        # 复制表头
        if start_row > 1:
            # 如果不是第一个文件，复制表头
            for col in ws.columns:
                col_letter = col[0].column_letter
                for cell in ws[1]:
                    new_cell = new_ws.cell(row=1, column=cell.column, value=cell.value)
                    # 复制样式
                    if cell.has_style:
                        new_cell.font = cell.font.copy()
                        new_cell.border = cell.border.copy()
                        new_cell.fill = cell.fill.copy()
                        new_cell.number_format = cell.number_format
                        new_cell.protection = cell.protection.copy()
                        new_cell.alignment = cell.alignment.copy()
        
        # 复制数据行
        data_start_row = 1 if start_row == 1 else 2
        for row in range(start_row, end_row + 1):
            for col in range(1, ws.max_column + 1):
                cell_value = ws.cell(row=row, column=col).value
                new_ws.cell(row=data_start_row, column=col, value=cell_value)
            data_start_row += 1
        
        # 保存到缓冲区
        buffer = io.BytesIO()
        new_wb.save(buffer)
        buffer.seek(0)
        
        # 生成新文件名
        base_name = original_file_name.replace('.xlsx', '').replace('.xls', '')
        new_file_name = f"{base_name}_rows_{start_row}_{end_row}.xlsx"
        
        results.append({
            'file_name': new_file_name,
            'buffer': buffer.read()
        })
        
        logs.append(f"第 {file_index + 1} 个文件生成完成")
    
    logs.append(f"按行数拆分完成，共生成 {len(results)} 个文件")
    return {
        'success': True,
        'logs': logs,
        'results': results,
        'details': {
            'splitMode': 'by_row',
            'rowsPerFile': rows_per_file,
            'totalRows': total_rows,
            'fileCount': len(results)
        }
    }


def split_by_column(ws, original_file_name, split_options, logs):
    """按列值拆分Excel文件"""
    column_index = split_options.get('columnIndex', 1)  # 默认第一列
    column_name = split_options.get('columnName', '')
    logs.append(f"开始按列值拆分，列索引: {column_index}")
    
    # 如果提供了列名，查找对应的列索引
    if column_name:
        for col in range(1, ws.max_column + 1):
            if ws.cell(row=1, column=col).value == column_name:
                column_index = col
                break
        logs.append(f"根据列名 '{column_name}' 找到列索引: {column_index}")
    
    # 收集所有唯一列值
    unique_values = set()
    for row in range(2, ws.max_row + 1):  # 跳过表头
        cell_value = ws.cell(row=row, column=column_index).value
        if cell_value is not None:
            unique_values.add(cell_value)
    
    logs.append(f"找到 {len(unique_values)} 个唯一列值")
    
    results = []
    
    # 按每个唯一值生成一个文件
    for value in sorted(unique_values):
        logs.append(f"正在处理列值: {value}")
        
        # 创建新工作簿
        new_wb = openpyxl.Workbook()
        new_ws = new_wb.active
        new_ws.title = ws.title
        
        # 复制表头
        for cell in ws[1]:
            new_cell = new_ws.cell(row=1, column=cell.column, value=cell.value)
            # 复制样式
            if cell.has_style:
                new_cell.font = cell.font.copy()
                new_cell.border = cell.border.copy()
                new_cell.fill = cell.fill.copy()
                new_cell.number_format = cell.number_format
                new_cell.protection = cell.protection.copy()
                new_cell.alignment = cell.alignment.copy()
        
        # 复制匹配的数据行
        new_row = 2
        for row in range(2, ws.max_row + 1):
            cell_value = ws.cell(row=row, column=column_index).value
            if cell_value == value:
                for col in range(1, ws.max_column + 1):
                    new_ws.cell(row=new_row, column=col, value=ws.cell(row=row, column=col).value)
                new_row += 1
        
        # 保存到缓冲区
        buffer = io.BytesIO()
        new_wb.save(buffer)
        buffer.seek(0)
        
        # 生成新文件名
        base_name = original_file_name.replace('.xlsx', '').replace('.xls', '')
        # 确保文件名安全
        safe_value = str(value).replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        new_file_name = f"{base_name}_{safe_value}.xlsx"
        
        results.append({
            'file_name': new_file_name,
            'buffer': buffer.read()
        })
        
        logs.append(f"列值 '{value}' 处理完成，生成 {new_row - 2} 行数据")
    
    logs.append(f"按列值拆分完成，共生成 {len(results)} 个文件")
    return {
        'success': True,
        'logs': logs,
        'results': results,
        'details': {
            'splitMode': 'by_column',
            'columnIndex': column_index,
            'uniqueValues': len(unique_values),
            'fileCount': len(results)
        }
    }
