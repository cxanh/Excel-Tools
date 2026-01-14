import io
import openpyxl
import json

def process(data):
    # 解析输入数据
    file_content = data['file']
    file_name = data['fileName']
    settings = data['settings']
    
    logs = []
    deleted_sheets = 0
    deleted_rows = 0
    deleted_columns = 0
    
    try:
        # 默认设置
        default_settings = {
            "contentToRemove": ["emptyRows"],
            "sheetOption": "all",
            "selectedSheets": "",
            "emptyRowDefinition": "all",
            "keepHeaderRow": True,
            "emptyColumnDefinition": "all",
            "keepHeaderColumn": True,
            "ignoreHiddenSheets": True,
            "ignoreFilteredRows": True,
            "enableDetailedLogs": True
        }
        
        # 更新设置
        if settings:
            default_settings.update(settings)
        current_settings = default_settings
        
        # 加载Excel文件
        wb = openpyxl.load_workbook(io.BytesIO(file_content))
        logs.append(f"成功加载文件: {file_name}")
        logs.append(f"包含工作表: {wb.sheetnames}")
        
        # 确定要处理的工作表
        if current_settings["sheetOption"] == "all":
            sheets_to_process = wb.sheetnames
            logs.append("将处理所有工作表")
        elif current_settings["sheetOption"] == "active":
            sheets_to_process = [wb.active.title]
            logs.append(f"将处理活动工作表: {wb.active.title}")
        elif current_settings["sheetOption"] == "selected":
            selected_sheets = [name.strip() for name in current_settings["selectedSheets"].split(",")]
            sheets_to_process = [name for name in selected_sheets if name in wb.sheetnames]
            if not sheets_to_process:
                logs.append("警告: 未找到指定的工作表，将处理所有工作表")
                sheets_to_process = wb.sheetnames
            else:
                logs.append(f"将处理工作表: {sheets_to_process}")
        
        # 保存原始工作表列表用于后续处理
        original_sheets = wb.sheetnames.copy()
        
        # 删除空白工作表
        if "emptySheets" in current_settings["contentToRemove"]:
            sheets_to_delete = []
            for sheet_name in original_sheets:
                if sheet_name not in sheets_to_process:
                    continue
                    
                ws = wb[sheet_name]
                is_empty = True
                
                # 检查工作表是否为空
                for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
                    for cell in row:
                        if cell.value is not None and cell.value != '':
                            is_empty = False
                            break
                    if not is_empty:
                        break
                
                if is_empty:
                    sheets_to_delete.append(sheet_name)
            
            # 从工作簿中删除空白工作表
            for sheet_name in sheets_to_delete:
                logs.append(f"删除空白工作表: {sheet_name}")
                wb.remove(wb[sheet_name])
                # 从要处理的工作表列表中移除
                if sheet_name in sheets_to_process:
                    sheets_to_process.remove(sheet_name)
            
            deleted_sheets = len(sheets_to_delete)
            logs.append(f"共删除 {deleted_sheets} 个空白工作表")
        
        # 遍历需要处理的工作表
        for sheet_name in sheets_to_process:
            ws = wb[sheet_name]
            logs.append(f"处理工作表: {sheet_name}")
            
            # 删除空白行
            if "emptyRows" in current_settings["contentToRemove"]:
                # 获取最大行号，从下往上遍历
                max_row = ws.max_row
                sheet_deleted_rows = 0
                
                # 确定开始行号（如果保留表头）
                start_row = 2 if current_settings["keepHeaderRow"] else 1
                
                for row in range(max_row, start_row - 1, -1):
                    # 检查行是否为空
                    is_empty = True
                    
                    if current_settings["emptyRowDefinition"] == "all":
                        # 检查所有单元格
                        for cell in ws[row]:
                            if cell.value is not None and cell.value != '':
                                is_empty = False
                                break
                    elif current_settings["emptyRowDefinition"] == "data":
                        # 检查数据列（跳过空列）
                        data_columns = []
                        for col in ws.iter_cols(min_row=1, max_row=1, max_col=ws.max_column):
                            if col[0].value is not None and col[0].value != '':
                                data_columns.append(col[0].column)
                        
                        if data_columns:
                            for col in data_columns:
                                cell = ws.cell(row=row, column=col)
                                if cell.value is not None and cell.value != '':
                                    is_empty = False
                                    break
                    
                    if is_empty:
                        ws.delete_rows(row)
                        sheet_deleted_rows += 1
                
                logs.append(f"  删除了 {sheet_deleted_rows} 个空白行")
                deleted_rows += sheet_deleted_rows
            
            # 删除空白列
            if "emptyColumns" in current_settings["contentToRemove"]:
                # 获取最大列号，从右往左遍历
                max_col = ws.max_column
                sheet_deleted_columns = 0
                
                # 确定开始列号（如果保留表头）
                start_col = 2 if current_settings["keepHeaderColumn"] else 1
                
                for col in range(max_col, start_col - 1, -1):
                    # 检查列是否为空
                    is_empty = True
                    
                    if current_settings["emptyColumnDefinition"] == "all":
                        # 检查所有单元格
                        for row in range(1, ws.max_row + 1):
                            cell = ws.cell(row=row, column=col)
                            if cell.value is not None and cell.value != '':
                                is_empty = False
                                break
                    elif current_settings["emptyColumnDefinition"] == "data":
                        # 检查数据行（跳过空行）
                        data_rows = []
                        for row in range(1, ws.max_row + 1):
                            cell = ws.cell(row=row, column=1)  # 假设第一列是数据标识列
                            if cell.value is not None and cell.value != '':
                                data_rows.append(row)
                        
                        if data_rows:
                            for row in data_rows:
                                cell = ws.cell(row=row, column=col)
                                if cell.value is not None and cell.value != '':
                                    is_empty = False
                                    break
                    
                    if is_empty:
                        ws.delete_cols(col)
                        sheet_deleted_columns += 1
                
                logs.append(f"  删除了 {sheet_deleted_columns} 个空白列")
                deleted_columns += sheet_deleted_columns
        
        # 保存处理后的文件
        output_buffer = io.BytesIO()
        wb.save(output_buffer)
        output_buffer.seek(0)
        
        logs.append(f"文件 {file_name} 处理完成")
        logs.append(f"总计删除: {deleted_sheets} 个空白工作表, {deleted_rows} 个空白行, {deleted_columns} 个空白列")
        
        return {
            'success': True,
            'buffer': output_buffer.getvalue(),
            'deletedSheets': deleted_sheets,
            'deletedRows': deleted_rows,
            'deletedColumns': deleted_columns,
            'logs': logs
        }
        
    except Exception as e:
        logs.append(f"处理失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'deletedSheets': deleted_sheets,
            'deletedRows': deleted_rows,
            'deletedColumns': deleted_columns,
            'logs': logs
        }

# 测试函数（用于开发和调试）
def test():
    # 创建一个简单的测试数据
    test_data = {
        'file': open('test.xlsx', 'rb').read(),
        'fileName': 'test.xlsx',
        'settings': {
            'contentToRemove': ['emptySheets', 'emptyRows', 'emptyColumns'],
            'sheetOption': 'all',
            'selectedSheets': '',
            'emptyRowDefinition': 'all',
            'keepHeaderRow': True,
            'emptyColumnDefinition': 'all',
            'keepHeaderColumn': True
        }
    }
    
    result = process(test_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result['success']:
        with open('处理后_test.xlsx', 'wb') as f:
            f.write(result['buffer'])
        print("处理后的文件已保存为: 处理后_test.xlsx")

if __name__ == '__main__':
    test()