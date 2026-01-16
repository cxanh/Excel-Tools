"""CSV合并插件"""
import io
import json

def process(file_buffer, params_json):
    logs = []
    try:
        params = json.loads(params_json) if isinstance(params_json, str) else params_json
        files_data = params.get('files', [])
        
        if not files_data:
            logs.append("⚠ 未提供要合并的文件")
            return {'buffer': file_buffer, 'logs': logs}
        
        # 合并CSV
        all_lines = []
        header = None
        
        for i, file_data in enumerate(files_data):
            content = file_data.decode('utf-8') if isinstance(file_data, bytes) else file_data
            lines = content.split('\n')
            
            if i == 0:
                header = lines[0]
                all_lines.append(header)
                all_lines.extend(lines[1:])
            else:
                all_lines.extend(lines[1:])
            
            logs.append(f"✓ 已合并文件 {i+1}: {len(lines)-1} 行")
        
        merged_content = '\n'.join(all_lines)
        logs.append(f"\n✓ 合并完成！总行数: {len(all_lines)-1}")
        
        return {
            'buffer': merged_content.encode('utf-8'),
            'logs': logs
        }
    except Exception as e:
        logs.append(f"✗ 处理失败: {str(e)}")
        return {'buffer': file_buffer, 'logs': logs}
