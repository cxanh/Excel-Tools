import openpyxl
import pandas as pd
import io
import re
import json
from datetime import datetime
import uuid

def process(data):
    # 解析输入数据
    template_content = data['template']
    data_content = data['data']
    settings = data['settings']
    data_info = data['dataInfo']
    
    logs = []
    result_files = []
    
    try:
        # 加载模板文件
        template_workbook = openpyxl.load_workbook(io.BytesIO(template_content))
        logs.append(f"加载模板文件成功，包含工作表: {template_workbook.sheetnames}")
        
        # 选择模板工作表
        template_sheet_name = settings.get('templateSheet', template_workbook.sheetnames[0])
        template_sheet = template_workbook[template_sheet_name]
        logs.append(f"选择模板工作表: {template_sheet_name}")
        
        # 加载数据源
        try:
            # 尝试作为Excel文件加载
            data_workbook = openpyxl.load_workbook(io.BytesIO(data_content))
            data_sheet = data_workbook.active
            
            # 提取数据
            data_list = []
            header_row = settings.get('dataStartRow', 1) - 1  # 转换为0-based索引
            
            # 获取表头
            headers = []
            for cell in data_sheet[header_row + 1]:
                if cell.value is not None:
                    headers.append(str(cell.value))
                else:
                    headers.append(f"column_{len(headers)+1}")
            
            # 获取数据行
            for row in data_sheet.iter_rows(min_row=header_row + 2, values_only=True):
                if all(cell is None for cell in row):
                    continue
                    
                row_data = {}
                for i, cell_value in enumerate(row):
                    if i < len(headers):
                        row_data[headers[i]] = cell_value
                    else:
                        row_data[f"column_{i+1}"] = cell_value
                
                if any(row_data.values()):  # 只保留非空行
                    data_list.append(row_data)
                    
            logs.append(f"从Excel数据源加载数据: {len(data_list)} 条记录")
            
        except Exception as e:
            # 尝试作为CSV文件加载
            data_df = pd.read_csv(io.BytesIO(data_content))
            data_list = data_df.to_dict('records')
            logs.append(f"从CSV数据源加载数据: {len(data_list)} 条记录")
        
        # 限制最大批量生成数量
        max_batch_size = 100
        if len(data_list) > max_batch_size:
            data_list = data_list[:max_batch_size]
            logs.append(f"批量生成数量限制为: {max_batch_size} 条记录")
        
        # 处理每条记录
        for index, record in enumerate(data_list):
            # 创建模板副本
            new_workbook = openpyxl.Workbook()
            new_sheet = new_workbook.active
            new_sheet.title = template_sheet_name
            
            # 复制模板内容到新工作簿
            for row in template_sheet.iter_rows(min_row=1, max_row=template_sheet.max_row, min_col=1, max_col=template_sheet.max_column):
                for cell in row:
                    new_cell = new_sheet.cell(row=cell.row, column=cell.column)
                    
                    # 复制单元格值
                    if cell.value is not None:
                        new_value = cell.value
                        
                        # 替换占位符
                        if isinstance(new_value, str):
                            for key, value in record.items():
                                placeholder = f"{{{key}}}"
                                if placeholder in new_value:
                                    # 转换值类型
                                    if value is not None:
                                        new_value = new_value.replace(placeholder, str(value))
                                    else:
                                        new_value = new_value.replace(placeholder, "")
                                
                            # 替换序号
                            new_value = new_value.replace("{序号}", str(index + 1))
                        
                        new_cell.value = new_value
                    
                    # 复制单元格样式
                    if cell.has_style:
                        new_cell.font = cell.font
                        new_cell.border = cell.border
                        new_cell.fill = cell.fill
                        new_cell.number_format = cell.number_format
                        new_cell.protection = cell.protection
                        new_cell.alignment = cell.alignment
            
            # 生成文件名
            filename_rule = settings.get('outputFilenameRule', "文档_{序号}.xlsx")
            new_filename = filename_rule
            
            # 替换文件名中的占位符
            for key, value in record.items():
                placeholder = f"{{{key}}}"
                if placeholder in new_filename:
                    if value is not None:
                        # 清理文件名中的非法字符
                        safe_value = re.sub(r'[\\/:*?\"<>|]', '_', str(value))
                        new_filename = new_filename.replace(placeholder, safe_value)
                    else:
                        new_filename = new_filename.replace(placeholder, "")
                        
            # 替换序号
            new_filename = new_filename.replace("{序号}", str(index + 1))
            
            # 确保文件名有效
            if not new_filename.endswith('.xlsx'):
                new_filename += '.xlsx'
                
            # 保存新文件到内存
            output_buffer = io.BytesIO()
            new_workbook.save(output_buffer)
            output_buffer.seek(0)
            
            # 添加到结果列表
            result_files.append({
                'filename': new_filename,
                'content': output_buffer.getvalue()
            })
            
            logs.append(f"生成文件: {new_filename}")
        
        # 返回结果
        return {
            'success': True,
            'logs': logs,
            'resultFiles': result_files
        }
        
    except Exception as e:
        logs.append(f"处理失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'logs': logs
        }

# 测试函数（用于开发和调试）
def test():
    # 创建一个简单的测试数据
    test_data = {
        'template': open('template.xlsx', 'rb').read(),
        'data': open('data.xlsx', 'rb').read(),
        'settings': {
            'outputFilenameRule': '合同_{合同编号}.xlsx',
            'dataStartRow': 1,
            'templateSheet': 'Sheet1'
        },
        'dataInfo': {
            'columns': ['合同编号', '客户名称', '金额', '日期', '状态'],
            'sampleData': [
                {"合同编号": "HT001", "客户名称": "客户A", "金额": 10000, "日期": "2026-01-14", "状态": "生效"},
                {"合同编号": "HT002", "客户名称": "客户B", "金额": 20000, "日期": "2026-01-15", "状态": "生效"}
            ],
            'totalRows': 2
        }
    }
    
    result = process(test_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 保存生成的文件
    if result['success']:
        for i, file_data in enumerate(result['resultFiles']):
            with open(f'generated_test_{i+1}.xlsx', 'wb') as f:
                f.write(file_data['content'])

if __name__ == '__main__':
    test()
