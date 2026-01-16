"""CSV拆分插件"""
import io
import json

def process(file_buffer, params_json):
    logs = []
    try:
        params = json.loads(params_json) if isinstance(params_json, str) else params_json
        rows_per_file = params.get('rows_per_file', 1000)
        
        # 解码CSV
        content = file_buffer.decode('utf-8')
        lines = content.split('\n')
        header = lines[0] if lines else ''
        data_lines = lines[1:]
        
        # 拆分文件
        files = []
        for i in range(0, len(data_lines), rows_per_file):
            chunk = data_lines[i:i+rows_per_file]
            file_content = header + '\n' + '\n'.join(chunk)
            files.append(file_content.encode('utf-8'))
            logs.append(f"✓ 生成文件 {len(files)}: {len(chunk)} 行")
        
        logs.append(f"\n✓ 拆分完成！共生成 {len(files)} 个文件")
        
        return {
            'buffer': files[0] if files else file_buffer,
            'logs': logs,
            'files': files
        }
    except Exception as e:
        logs.append(f"✗ 处理失败: {str(e)}")
        return {'buffer': file_buffer, 'logs': logs}
