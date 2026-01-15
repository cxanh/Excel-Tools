import io
import csv
import codecs
from collections import defaultdict

def process(data):
    """将CSV文件拆分成多个文件"""
    file_content = data['file']
    file_name = data['fileName']
    settings = data.get('settings', {})
    split_mode = settings.get('splitMode', 'by_row')  # by_row, by_column
    split_options = settings.get('splitOptions', {})
    logs = []
    
    try:
        logs.append(f"正在加载文件: {file_name}")
        
        # 读取CSV文件内容
        content = file_content.decode(settings.get('encoding', 'utf-8'))
        csv_reader = csv.reader(io.StringIO(content), delimiter=settings.get('delimiter', ','))
        
        # 获取表头
        headers = next(csv_reader, None)
        if headers is None:
            raise ValueError("CSV文件没有表头")
        logs.append(f"CSV文件加载成功，表头: {headers}")
        
        # 获取所有行数据
        rows = list(csv_reader)
        total_rows = len(rows)
        logs.append(f"总共有 {total_rows} 行数据")
        
        if total_rows == 0:
            raise ValueError("CSV文件没有数据行")
        
        if split_mode == 'by_row':
            # 按行数拆分
            return split_csv_by_row(headers, rows, file_name, split_options, logs)
        elif split_mode == 'by_column':
            # 按列值拆分
            return split_csv_by_column(headers, rows, file_name, split_options, logs)
        else:
            raise ValueError(f"不支持的拆分模式: {split_mode}")
        
    except Exception as e:
        logs.append(f"拆分失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'logs': logs
        }


def split_csv_by_row(headers, rows, original_file_name, split_options, logs):
    """按行数拆分CSV文件"""
    rows_per_file = split_options.get('rowsPerFile', 1000)
    logs.append(f"开始按行数拆分，每 {rows_per_file} 行一个文件")
    
    # 计算需要生成的文件数
    total_files = (len(rows) + rows_per_file - 1) // rows_per_file
    logs.append(f"预计生成 {total_files} 个文件")
    
    results = []
    
    # 拆分数据
    for file_index in range(total_files):
        start_row = file_index * rows_per_file
        end_row = min((file_index + 1) * rows_per_file, len(rows))
        logs.append(f"正在处理第 {file_index + 1} 个文件，处理行范围: {start_row} - {end_row}")
        
        # 获取当前文件的数据
        current_rows = rows[start_row:end_row]
        
        # 创建新的CSV内容
        output = io.BytesIO()
        # 使用utf-8编码写入
        writer = csv.writer(io.TextIOWrapper(output, encoding='utf-8', newline=''))
        
        # 写入表头
        writer.writerow(headers)
        
        # 写入数据
        for row in current_rows:
            writer.writerow(row)
        
        # 刷新缓冲区
        output.seek(0)
        
        # 生成新文件名
        base_name = original_file_name.replace('.csv', '')
        new_file_name = f"{base_name}_rows_{start_row + 1}_{end_row}.csv"
        
        results.append({
            'file_name': new_file_name,
            'buffer': output.read()
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
            'totalRows': len(rows),
            'fileCount': len(results)
        }
    }


def split_csv_by_column(headers, rows, original_file_name, split_options, logs):
    """按列值拆分CSV文件"""
    column_index = split_options.get('columnIndex', 0)  # 默认第一列
    column_name = split_options.get('columnName', '')
    logs.append(f"开始按列值拆分")
    
    # 如果提供了列名，查找对应的列索引
    if column_name:
        if column_name in headers:
            column_index = headers.index(column_name)
            logs.append(f"根据列名 '{column_name}' 找到列索引: {column_index}")
        else:
            raise ValueError(f"未找到列名 '{column_name}'")
    
    # 按列值分组数据
    grouped_data = defaultdict(list)
    for row in rows:
        if len(row) > column_index:
            key = row[column_index] or "空值"
            grouped_data[key].append(row)
    
    logs.append(f"找到 {len(grouped_data)} 个唯一列值")
    
    results = []
    
    # 为每个分组生成一个文件
    for key, group_rows in sorted(grouped_data.items()):
        logs.append(f"正在处理列值: {key}")
        
        # 创建新的CSV内容
        output = io.BytesIO()
        writer = csv.writer(io.TextIOWrapper(output, encoding='utf-8', newline=''))
        
        # 写入表头
        writer.writerow(headers)
        
        # 写入数据
        for row in group_rows:
            writer.writerow(row)
        
        # 刷新缓冲区
        output.seek(0)
        
        # 生成新文件名
        base_name = original_file_name.replace('.csv', '')
        # 确保文件名安全
        safe_key = str(key).replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        new_file_name = f"{base_name}_{safe_key}.csv"
        
        results.append({
            'file_name': new_file_name,
            'buffer': output.read()
        })
        
        logs.append(f"列值 '{key}' 处理完成，生成 {len(group_rows)} 行数据")
    
    logs.append(f"按列值拆分完成，共生成 {len(results)} 个文件")
    return {
        'success': True,
        'logs': logs,
        'results': results,
        'details': {
            'splitMode': 'by_column',
            'columnIndex': column_index,
            'uniqueValues': len(grouped_data),
            'fileCount': len(results)
        }
    }
