import pandas as pd
import io
import sys
import openpyxl
import json

# 默认设置
DEFAULT_SETTINGS = {
    'mergeMode': 'append',
    'includeHeaders': True,
    'skipEmptyRows': True,
    'sheetOption': 'all',
    'selectedSheets': '',
    'enableDetailedLogs': True
}

# 处理文件合并
def process(data):
    # 解析输入数据
    files = data['files']
    settings = data.get('settings', None)
    
    logs = []
    
    # 使用默认设置或传入的设置
    current_settings = DEFAULT_SETTINGS.copy()
    if settings:
        current_settings.update(settings)
    
    try:
        logs.append(f"合并模式: {current_settings['mergeMode']}")
        logs.append(f"工作表选项: {current_settings['sheetOption']}")
        logs.append(f"包含表头: {current_settings['includeHeaders']}")
        logs.append(f"跳过空行: {current_settings['skipEmptyRows']}")
        
        if current_settings['enableDetailedLogs']:
            logs.append(f"详细日志: 已启用")
        
        output = io.BytesIO()
        
        if current_settings['mergeMode'] == 'append':
            # 追加到同一工作表模式
            all_dataframes = []
            
            for filename, content in files.items():
                logs.append(f"正在读取文件: {filename}")
                
                # 获取要处理的工作表
                wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True)
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
                
                for sheet_name in sheets_to_process:
                    logs.append(f"  读取工作表: {sheet_name}")
                    
                    # 使用pandas读取工作表
                    df = pd.read_excel(
                        io.BytesIO(content), 
                        engine='openpyxl',
                        sheet_name=sheet_name
                    )
                    
                    # 添加源文件和工作表名列
                    df['来源文件'] = filename
                    df['来源工作表'] = sheet_name
                    
                    # 跳过空行
                    if current_settings['skipEmptyRows']:
                        initial_rows = len(df)
                        df = df.dropna(how='all')
                        if len(df) < initial_rows:
                            logs.append(f"  - 跳过了 {initial_rows - len(df)} 个空行")
                    
                    # 统计行数
                    logs.append(f"  - 读取到 {len(df)} 行数据")
                    
                    all_dataframes.append(df)
                
                wb.close()
            
            # 合并所有DataFrame
            if all_dataframes:
                merged_df = pd.concat(all_dataframes, ignore_index=True)
                logs.append(f"合并完成，共 {len(merged_df)} 行数据")
                
                # 将合并结果写入内存
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    merged_df.to_excel(writer, index=False, sheet_name='合并结果')
            else:
                return {
                    'success': False,
                    'error': '没有找到可合并的数据',
                    'logs': logs
                }
        
        elif current_settings['mergeMode'] == 'separate':
            # 保留原工作表模式
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                total_files = len(files)
                for i, (filename, content) in enumerate(files.items()):
                    logs.append(f"正在处理文件 {i+1}/{total_files}: {filename}")
                    
                    # 获取要处理的工作表
                    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True)
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
                    
                    for sheet_name in sheets_to_process:
                        # 为避免工作表名称冲突，添加文件标识
                        new_sheet_name = f"{sheet_name}({filename.split('.')[0]})"
                        if len(new_sheet_name) > 31:
                            # Excel工作表名称最多31个字符
                            new_sheet_name = new_sheet_name[:31]
                        
                        logs.append(f"  复制工作表: {sheet_name} -> {new_sheet_name}")
                        
                        # 使用pandas读取并写入工作表
                        df = pd.read_excel(
                            io.BytesIO(content), 
                            engine='openpyxl',
                            sheet_name=sheet_name
                        )
                        
                        # 跳过空行
                        if current_settings['skipEmptyRows']:
                            initial_rows = len(df)
                            df = df.dropna(how='all')
                            if len(df) < initial_rows:
                                logs.append(f"  - 跳过了 {initial_rows - len(df)} 个空行")
                        
                        df.to_excel(writer, index=False, sheet_name=new_sheet_name)
                    
                    wb.close()
            
            logs.append(f"处理完成，共合并了 {total_files} 个文件")
        
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

# 为了保持向后兼容性，保留原函数接口
merge_excel_files = process

# 测试函数（用于开发和调试）
def test():
    # 创建一个简单的测试数据
    test_files = {}
    # 这里需要替换为实际的测试文件路径
    test_file_paths = ['test1.xlsx', 'test2.xlsx']
    
    for file_path in test_file_paths:
        with open(file_path, 'rb') as f:
            test_files[file_path] = f.read()
    
    test_data = {
        'files': test_files,
        'settings': {
            'mergeMode': 'append',
            'includeHeaders': True,
            'skipEmptyRows': True,
            'sheetOption': 'all',
            'enableDetailedLogs': True
        }
    }
    
    result = process(test_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result['success']:
        with open('合并结果.xlsx', 'wb') as f:
            f.write(result['buffer'])
        print("合并结果已保存为: 合并结果.xlsx")

# 主入口函数
if __name__ == "__main__":
    # 在浏览器环境中，Pyodide会通过其他方式调用该函数
    test()