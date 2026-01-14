import openpyxl
import io
import re
import json
import os
from PIL import Image
from openpyxl.drawing.image import Image as OpenpyxlImage
from openpyxl.utils import get_column_letter

def process(data):
    # 解析输入数据
    file_content = data['file']
    file_name = data['fileName']
    settings = data['settings']
    
    logs = []
    converted_count = 0
    processed_cells = 0
    
    try:
        # 加载Excel文件
        workbook = openpyxl.load_workbook(io.BytesIO(file_content))
        logs.append(f"成功加载文件: {file_name}")
        logs.append(f"包含工作表: {workbook.sheetnames}")
        
        # 获取需要处理的工作表
        sheets_to_process = []
        if settings.get('sheetOption', 'all') == 'all':
            sheets_to_process = workbook.sheetnames
            logs.append("将处理所有工作表")
        else:
            # 解析指定工作表
            specific_sheets = settings.get('specificSheets', '')
            if specific_sheets:
                # 分割工作表名称
                sheet_patterns = [s.strip() for s in specific_sheets.split(',') if s.strip()]
                
                # 匹配工作表名称
                for sheet_name in workbook.sheetnames:
                    for pattern in sheet_patterns:
                        # 转换为正则表达式模式
                        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
                        if re.match(regex_pattern, sheet_name, re.IGNORECASE):
                            sheets_to_process.append(sheet_name)
                            break
                
                if sheets_to_process:
                    logs.append(f"将处理工作表: {sheets_to_process}")
                else:
                    logs.append(f"没有匹配的工作表: {specific_sheets}")
                    return {
                        'success': False,
                        'error': '没有匹配的工作表',
                        'logs': logs,
                        'convertedCount': converted_count
                    }
            else:
                logs.append("没有指定工作表")
                return {
                    'success': False,
                    'error': '没有指定工作表',
                    'logs': logs,
                    'convertedCount': converted_count
                }
        
        # 获取图片路径识别选项
        path_option = settings.get('pathOption', 'all')
        specific_columns = settings.get('specificColumns', '')
        
        # 获取图片位置选项
        position_option = settings.get('positionOption', 'replace')
        
        # 获取图片大小选项
        size_option = settings.get('sizeOption', 'fitCell')
        custom_size = settings.get('customSize', {'width': 300, 'height': 200})
        
        # 获取高级选项
        advanced_options = settings.get('advancedOptions', ['resizeCell', 'ignoreInvalid'])
        keep_path = 'keepPath' in advanced_options
        resize_cell = 'resizeCell' in advanced_options
        ignore_invalid = 'ignoreInvalid' in advanced_options
        recursive = 'recursive' in advanced_options
        
        logs.append(f"图片路径识别: {path_option}{f' ({specific_columns})' if path_option == 'specific' else ''}")
        logs.append(f"图片位置: {position_option}")
        logs.append(f"图片大小: {size_option}{f' ({custom_size})' if size_option == 'custom' else ''}")
        logs.append(f"高级选项: {'保留路径' if keep_path else '不保留路径'}, {'调整单元格' if resize_cell else '不调整单元格'}, {'忽略无效路径' if ignore_invalid else '不忽略无效路径'}, {'递归检查' if recursive else '不递归检查'}")
        
        # 处理每个工作表
        for sheet_name in sheets_to_process:
            sheet = workbook[sheet_name]
            sheet_converted = 0
            sheet_processed = 0
            
            logs.append(f"开始处理工作表: {sheet_name}")
            
            # 获取工作表的行列信息
            max_row = sheet.max_row
            max_col = sheet.max_column
            
            if max_row < 1:
                logs.append(f"工作表 {sheet_name} 没有数据行")
                continue
            
            # 解析指定的列
            target_columns = []
            if path_option == 'specific' and specific_columns:
                # 支持列字母(A,B,C)或列名称
                column_patterns = [s.strip() for s in specific_columns.split(',') if s.strip()]
                
                # 获取表头信息
                headers = []
                if max_row > 0:
                    headers = [sheet.cell(row=1, column=col).value for col in range(1, max_col + 1)]
                    headers = [str(h) if h is not None else f"column_{col+1}" for col, h in enumerate(headers)]
                
                # 解析列信息
                for pattern in column_patterns:
                    # 检查是否是列字母
                    if re.match(r'^[A-Za-z]+$', pattern):
                        # 转换为列索引
                        col_idx = 0
                        for c in pattern.upper():
                            col_idx = col_idx * 26 + (ord(c) - ord('A') + 1)
                        target_columns.append(col_idx)
                    else:
                        # 按列名称匹配
                        for idx, header in enumerate(headers):
                            if header and (header == pattern or header.lower() == pattern.lower()):
                                target_columns.append(idx + 1)  # 转换为1-based索引
                                break
                
                # 去重并排序
                target_columns = sorted(list(set(target_columns)))
                
                if not target_columns:
                    logs.append(f"没有找到匹配的列: {specific_columns}")
                    target_columns = list(range(1, max_col + 1))  # 默认使用所有列
            else:
                # 使用所有列
                target_columns = list(range(1, max_col + 1))
            
            logs.append(f"使用列: {target_columns}")
            
            # 收集需要处理的单元格
            cells_to_process = []
            for row_idx in range(1, max_row + 1):
                for col_idx in target_columns:
                    cell = sheet.cell(row=row_idx, column=col_idx)
                    if cell.value and isinstance(cell.value, str):
                        cells_to_process.append((row_idx, col_idx, cell))
            
            processed_cells += len(cells_to_process)
            sheet_processed += len(cells_to_process)
            
            # 处理每个单元格
            for row_idx, col_idx, cell in cells_to_process:
                path = cell.value.strip()
                
                # 检查是否是有效路径
                image_path = None
                if os.path.exists(path):
                    image_path = path
                elif os.path.exists(os.path.abspath(path)):
                    image_path = os.path.abspath(path)
                elif recursive:
                    # 递归检查子目录
                    excel_dir = os.path.dirname(os.path.abspath(file_name))
                    potential_path = os.path.join(excel_dir, path)
                    if os.path.exists(potential_path):
                        image_path = potential_path
                
                if image_path and os.path.isfile(image_path):
                    try:
                        # 打开图片
                        img = Image.open(image_path)
                        
                        # 根据设置调整图片大小
                        if size_option == 'fitCell':
                            # 获取单元格尺寸（默认列宽约为8.43字符，行高约为15点）
                            cell_width = sheet.column_dimensions[get_column_letter(col_idx)].width or 8.43
                            cell_height = sheet.row_dimensions[row_idx].height or 15
                            
                            # 转换为像素
                            cell_width_px = cell_width * 6.4  # 近似转换
                            cell_height_px = cell_height * 1.33  # 近似转换
                            
                            # 按比例调整图片大小
                            img_width, img_height = img.size
                            ratio = min(cell_width_px / img_width, cell_height_px / img_height)
                            new_width = int(img_width * ratio)
                            new_height = int(img_height * ratio)
                            
                            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        elif size_option == 'custom':
                            # 自定义大小
                            new_width = custom_size.get('width', 300)
                            new_height = custom_size.get('height', 200)
                            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # 保存图片到临时缓冲区
                        img_buffer = io.BytesIO()
                        img.save(img_buffer, format='PNG')
                        img_buffer.seek(0)
                        
                        # 创建openpyxl图片对象
                        openpyxl_img = OpenpyxlImage(img_buffer)
                        
                        # 根据位置选项插入图片
                        if position_option == 'replace':
                            # 替换原单元格内容
                            if not keep_path:
                                cell.value = None
                            
                            # 插入图片
                            sheet.add_image(openpyxl_img, f'{get_column_letter(col_idx)}{row_idx}')
                            
                            # 调整图片大小以适应单元格
                            if size_option == 'fitCell':
                                openpyxl_img.width = new_width
                                openpyxl_img.height = new_height
                        elif position_option == 'insert':
                            # 插入到单元格上方，需要插入新行
                            sheet.insert_rows(row_idx)
                            sheet.add_image(openpyxl_img, f'{get_column_letter(col_idx)}{row_idx}')
                        elif position_option == 'right':
                            # 插入到单元格右侧
                            sheet.add_image(openpyxl_img, f'{get_column_letter(col_idx+1)}{row_idx}')
                        
                        # 自动调整单元格大小
                        if resize_cell:
                            if size_option == 'fitCell':
                                sheet.row_dimensions[row_idx].height = new_height / 1.33
                                sheet.column_dimensions[get_column_letter(col_idx)].width = new_width / 6.4
                        
                        converted_count += 1
                        sheet_converted += 1
                        
                        logs.append(f"成功转换图片: {path} -> 单元格 {get_column_letter(col_idx)}{row_idx}")
                        
                    except Exception as e:
                        logs.append(f"处理图片 {path} 失败: {str(e)}")
                        if not ignore_invalid:
                            raise
                elif not ignore_invalid:
                    logs.append(f"无效图片路径: {path}")
                    if not ignore_invalid:
                        raise FileNotFoundError(f"图片文件不存在: {path}")
            
            logs.append(f"工作表 {sheet_name} 处理完成: 转换了 {sheet_converted} 个图片, 处理了 {sheet_processed} 个单元格")
        
        # 保存处理后的文件
        output_buffer = io.BytesIO()
        workbook.save(output_buffer)
        output_buffer.seek(0)
        
        logs.append(f"文件 {file_name} 处理完成")
        logs.append(f"总计转换: {converted_count} 个图片")
        logs.append(f"总计处理: {processed_cells} 个单元格")
        
        return {
            'success': True,
            'buffer': output_buffer.getvalue(),
            'convertedCount': converted_count,
            'processedCells': processed_cells,
            'logs': logs
        }
        
    except Exception as e:
        logs.append(f"处理失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'convertedCount': converted_count,
            'logs': logs
        }

# 测试函数（用于开发和调试）
def test():
    # 创建一个简单的测试数据
    test_data = {
        'file': open('test.xlsx', 'rb').read(),
        'fileName': 'test.xlsx',
        'settings': {
            'sheetOption': 'all',
            'specificSheets': '',
            'pathOption': 'all',
            'specificColumns': '',
            'positionOption': 'replace',
            'sizeOption': 'fitCell',
            'customSize': {'width': 300, 'height': 200},
            'advancedOptions': ['resizeCell', 'ignoreInvalid']
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
