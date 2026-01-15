<template>
  <PluginTemplate
    :title="'批量添加 Excel 公式'"
    :description="'为 Excel 文件批量添加公式，支持自定义公式和批量处理'"
    :hasHelp="true"
  >
    <template #step1-content>
      <div class="step-content">
        <a-form layout="vertical" class="setting-form">
          <a-form-item label="目标列">
            <a-input
              v-model:value="targetColumn"
              placeholder="请输入要添加公式的目标列（如：A, B, C 或 1, 2, 3）"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="公式内容">
            <a-textarea
              v-model:value="formulaContent"
              placeholder="请输入公式内容，如：=A1+B1"
              :rows="3"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="公式选项">
            <a-checkbox v-model:checked="includeHeaders">包含标题行</a-checkbox>
          </a-form-item>
        </a-form>
      </div>
    </template>

    <template #step2-extra>
      <!-- 这里可以添加额外的选项，如处理范围等 -->
    </template>

    <template #step3-extra>
      <!-- 这里可以添加额外的输出选项 -->
    </template>

    <template #help-content>
      <div class="help-content">
        <h3>功能说明</h3>
        <p>本工具可以为 Excel 文件批量添加公式，支持自定义公式和批量处理。</p>
        <h3>使用步骤</h3>
        <ol>
          <li>输入要添加公式的目标列（如：A, B, C 或 1, 2, 3）</li>
          <li>输入公式内容（如：=A1+B1）</li>
          <li>选择是否包含标题行</li>
          <li>选择要处理的 Excel 文件</li>
          <li>选择输出目录</li>
          <li>点击开始处理，等待处理完成</li>
        </ol>
        <h3>注意事项</h3>
        <ul>
          <li>支持处理 .xlsx 和 .xls 格式的 Excel 文件</li>
          <li>处理后的文件会保存在指定的输出目录</li>
          <li>公式必须以等号 "=" 开头</li>
          <li>公式中的单元格引用会自动调整为对应行</li>
        </ul>
      </div>
    </template>
  </PluginTemplate>
</template>

<script setup>
import { ref, reactive } from 'vue';
import PluginTemplate from '@plugins/plugin-template/index.vue';
import { runPy } from '@utils/py';

// 公式设置
const targetColumn = ref('C');
const formulaContent = ref('=A1+B1');
const includeHeaders = ref(true);

// 定义处理函数
const processFiles = async (files, outputDir, selectedSheets = null) => {
  // 准备公式设置参数
  const formulaSettings = {
    target_column: targetColumn.value,
    formula: formulaContent.value,
    include_headers: includeHeaders.value
  };

  // 构建Python脚本
  const pythonCode = `
import os
import sys
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

# 设置中文支持
sys.stdout.reconfigure(encoding='utf-8')

def add_formula_to_excel(file_path, output_path, formula_settings):
    """为Excel文件批量添加公式"""
    print(f"正在处理文件: {file_path}")
    
    try:
        # 加载工作簿
        wb = load_workbook(file_path)
        
        # 遍历所有工作表
        for sheet in wb.worksheets:
            print(f"  处理工作表: {sheet.title}")
            
            # 获取最大行和最大列
            max_row = sheet.max_row
            max_col = sheet.max_column
            
            # 如果工作表为空，跳过
            if max_row <= 1:
                print(f"  工作表 '{sheet.title}' 为空，跳过")
                continue
            
            # 确定数据范围
            if formula_settings['include_headers']:
                # 包含标题行，从第2行开始添加公式
                data_start_row = 2
            else:
                # 不包含标题行，从第1行开始添加公式
                data_start_row = 1
            
            # 转换列字母为数字
            def col_to_num(col):
                if col.isdigit():
                    return int(col)
                col_num = 0
                for c in col.upper():
                    col_num = col_num * 26 + (ord(c) - ord('A') + 1)
                return col_num
            
            # 获取目标列
            target_col_num = col_to_num(formula_settings['target_column'])
            
            # 获取公式内容
            formula = formula_settings['formula']
            
            # 确保公式以等号开头
            if not formula.startswith('='):
                formula = '=' + formula
            
            # 为每一行添加公式
            for row in range(data_start_row, max_row + 1):
                # 构建当前行的公式（替换行号）
                # 简单实现：将公式中的数字行号替换为当前行号
                # 注意：这是一个简化的实现，可能需要更复杂的处理
                current_formula = formula
                
                # 将公式中的行号替换为当前行号
                # 例如：将 A1 替换为 A{row}，B2 替换为 B{row} 等
                import re
                def replace_row(match):
                    col = match.group(1)
                    return f"{col}{row}"
                
                # 使用正则表达式替换行号
                current_formula = re.sub(r'([A-Z]+)(\d+)', replace_row, current_formula)
                
                # 设置单元格公式
                sheet.cell(row=row, column=target_col_num).value = current_formula
            
            print(f"  工作表 '{sheet.title}' 公式添加完成")
        
        # 保存文件
        wb.save(output_path)
        print(f"  文件处理完成，保存到: {output_path}")
        return True
    except InvalidFileException:
        print(f"  错误: 不支持的文件格式: {file_path}")
        return False
    except Exception as e:
        print(f"  处理文件 {file_path} 时出错: {str(e)}")
        return False

# 主函数
if __name__ == "__main__":
    import json
    
    # 解析命令行参数
    input_files = json.loads(sys.argv[1])
    output_dir = sys.argv[2]
    formula_settings = json.loads(sys.argv[3])
    
    print(f"开始处理 {len(input_files)} 个文件...")
    
    success_count = 0
    error_count = 0
    
    for input_file in input_files:
        # 构建输出文件路径
        file_name = os.path.basename(input_file)
        output_file = os.path.join(output_dir, file_name)
        
        # 处理文件
        if add_formula_to_excel(input_file, output_file, formula_settings):
            success_count += 1
        else:
            error_count += 1
    
    print(f"\n处理完成！成功: {success_count} 个, 失败: {error_count} 个")
    `;

  try {
    // 调用Python脚本处理文件
    const result = await runPy(
      pythonCode,
      [files, outputDir, formulaSettings],
      '添加公式'
    );
    return result;
  } catch (error) {
    console.error('处理文件时出错:', error);
    throw error;
  }
};
</script>

<style scoped>
.step-content {
  padding: 0 20px;
}

.setting-form {
  max-width: 600px;
  margin: 0 auto;
}

.help-content {
  padding: 10px;
}

.help-content h3 {
  margin-top: 20px;
  margin-bottom: 10px;
  font-size: 16px;
  font-weight: 500;
}

.help-content p,
.help-content li {
  margin-bottom: 8px;
  line-height: 1.5;
}
</style>