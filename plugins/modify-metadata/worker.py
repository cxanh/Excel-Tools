"""修改文档元数据插件"""
import io
import json
from openpyxl import load_workbook

def process(file_buffer, params_json):
    logs = []
    try:
        params = json.loads(params_json) if isinstance(params_json, str) else params_json
        wb = load_workbook(io.BytesIO(file_buffer))
        logs.append(f"成功加载工作簿")
        
        # 修改元数据
        updated_fields = 0
        if 'creator' in params:
            wb.properties.creator = params['creator']
            updated_fields += 1
        if 'title' in params:
            wb.properties.title = params['title']
            updated_fields += 1
        if 'subject' in params:
            wb.properties.subject = params['subject']
            updated_fields += 1
        if 'description' in params:
            wb.properties.description = params['description']
            updated_fields += 1
        if 'keywords' in params:
            wb.properties.keywords = params['keywords']
            updated_fields += 1
        if 'category' in params:
            wb.properties.category = params['category']
            updated_fields += 1
        if 'company' in params:
            wb.properties.company = params['company']
            updated_fields += 1
        
        logs.append(f"✓ 已更新 {updated_fields} 个元数据字段")
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return {'buffer': output.getvalue(), 'logs': logs}
    except Exception as e:
        logs.append(f"✗ 处理失败: {str(e)}")
        return {'buffer': file_buffer, 'logs': logs}
