"""清空文档元数据插件"""
import io
import json
from openpyxl import load_workbook

def process(file_buffer, params_json):
    logs = []
    try:
        wb = load_workbook(io.BytesIO(file_buffer))
        logs.append(f"成功加载工作簿")
        
        # 清空元数据
        cleared_fields = 0
        if wb.properties.creator:
            wb.properties.creator = ''
            cleared_fields += 1
        if wb.properties.title:
            wb.properties.title = ''
            cleared_fields += 1
        if wb.properties.subject:
            wb.properties.subject = ''
            cleared_fields += 1
        if wb.properties.description:
            wb.properties.description = ''
            cleared_fields += 1
        if wb.properties.keywords:
            wb.properties.keywords = ''
            cleared_fields += 1
        if wb.properties.category:
            wb.properties.category = ''
            cleared_fields += 1
        if wb.properties.company:
            wb.properties.company = ''
            cleared_fields += 1
        
        logs.append(f"✓ 已清空 {cleared_fields} 个元数据字段")
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return {'buffer': output.getvalue(), 'logs': logs}
    except Exception as e:
        logs.append(f"✗ 处理失败: {str(e)}")
        return {'buffer': file_buffer, 'logs': logs}
