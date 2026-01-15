import io
import openpyxl

def process(data):
    """删除Excel文件中的所有宏和VBA代码"""
    file_content = data['file']
    file_name = data['fileName']
    logs = []
    
    try:
        # 加载Excel文件，keep_vba=True表示保留宏以便删除
        logs.append(f"正在加载文件: {file_name}")
        wb = openpyxl.load_workbook(io.BytesIO(file_content), read_only=False, keep_vba=True)
        
        # 检查是否包含宏
        has_vba = bool(wb.vba_archive)
        if has_vba:
            logs.append(f"检测到宏代码，正在删除...")
            # 删除宏
            wb.vba_archive = None
            logs.append(f"宏删除成功")
        else:
            logs.append(f"文件中未检测到宏代码")
        
        # 保存结果
        logs.append(f"正在保存处理后的文件...")
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return {
            'success': True,
            'buffer': output.read(),
            'logs': logs,
            'details': {
                'hasMacro': has_vba,
                'result': '宏已删除' if has_vba else '无宏可删除'
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'logs': logs
        }