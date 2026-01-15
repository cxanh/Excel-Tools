<template>
  <PluginTemplate
    :title="'比较两个 Excel 文件差异'"
    :description="'比较两个 Excel 文件的内容差异，支持按单元格、行或列比较'"
    :hasHelp="true"
  >
    <template #step1-content>
      <div class="step-content">
        <a-form layout="vertical" class="setting-form">
          <a-form-item label="比较方式">
            <a-radio-group v-model:value="compareType" button-style="solid">
              <a-radio-button value="cell">按单元格比较</a-radio-button>
              <a-radio-button value="row">按行比较</a-radio-button>
              <a-radio-button value="column">按列比较</a-radio-button>
            </a-radio-group>
          </a-form-item>
          
          <a-form-item label="比较选项">
            <a-checkbox v-model:checked="ignoreCase">忽略大小写</a-checkbox>
            <a-checkbox v-model:checked="ignoreFormat">忽略格式差异</a-checkbox>
            <a-checkbox v-model:checked="ignoreEmpty">忽略空值差异</a-checkbox>
          </a-form-item>
          
          <a-form-item label="输出选项">
            <a-radio-group v-model:value="outputFormat" button-style="solid">
              <a-radio-button value="excel">输出为 Excel 文件</a-radio-button>
              <a-radio-button value="html">输出为 HTML 文件</a-radio-button>
            </a-radio-group>
          </a-form-item>
        </a-form>
      </div>
    </template>

    <template #step2-extra>
      <div class="extra-content">
        <a-alert
          message="注意事项"
          description="请选择两个要比较的 Excel 文件，系统将自动比较它们的内容差异。"
          type="info"
          show-icon
        />
      </div>
    </template>

    <template #step3-extra>
      <!-- 这里可以添加额外的输出选项 -->
    </template>

    <template #help-content>
      <div class="help-content">
        <h3>功能说明</h3>
        <p>本工具可以比较两个 Excel 文件的内容差异，支持按单元格、行或列比较，并可以选择不同的输出格式。</p>
        <h3>使用步骤</h3>
        <ol>
          <li>选择比较方式（按单元格、按行或按列）</li>
          <li>设置比较选项（忽略大小写、忽略格式差异、忽略空值差异）</li>
          <li>选择输出格式（Excel 或 HTML）</li>
          <li>选择要比较的两个 Excel 文件</li>
          <li>选择输出目录</li>
          <li>点击开始处理，等待处理完成</li>
        </ol>
        <h3>注意事项</h3>
        <ul>
          <li>支持处理 .xlsx 和 .xls 格式的 Excel 文件</li>
          <li>处理后的文件会保存在指定的输出目录</li>
          <li>建议选择按单元格比较以获得最详细的差异信息</li>
        </ul>
      </div>
    </template>
  </PluginTemplate>
</template>

<script setup>
import { ref, reactive } from 'vue';
import PluginTemplate from '@plugins/plugin-template/index.vue';
import { runPy } from '@utils/py';

// 比较设置
const compareType = ref('cell');
const ignoreCase = ref(false);
const ignoreFormat = ref(true);
const ignoreEmpty = ref(false);
const outputFormat = ref('excel');

// 定义处理函数
const processFiles = async (files, outputDir, selectedSheets = null) => {
  // 检查是否选择了两个文件
  if (files.length !== 2) {
    throw new Error('请选择两个要比较的 Excel 文件');
  }
  
  // 准备比较设置参数
  const compareSettings = {
    type: compareType.value,
    ignore_case: ignoreCase.value,
    ignore_format: ignoreFormat.value,
    ignore_empty: ignoreEmpty.value,
    output_format: outputFormat.value
  };

  // 构建Python脚本
  const pythonCode = `
import os
import sys
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

# 设置中文支持
sys.stdout.reconfigure(encoding='utf-8')

def compare_excel_files(file1, file2, output_dir, compare_settings):
    """比较两个Excel文件的差异"""
    print(f"正在比较文件: {os.path.basename(file1)} 和 {os.path.basename(file2)}")
    
    try:
        # 加载两个工作簿
        wb1 = load_workbook(file1)
        wb2 = load_workbook(file2)
        
        # 获取所有工作表名称
        sheets1 = [sheet.title for sheet in wb1.worksheets]
        sheets2 = [sheet.title for sheet in wb2.worksheets]
        
        # 找出共同的工作表
        common_sheets = list(set(sheets1) & set(sheets2))
        
        if not common_sheets:
            print("  错误: 两个文件没有共同的工作表")
            return False
        
        print(f"  找到 {len(common_sheets)} 个共同工作表")
        
        # 比较结果统计
        differences = {
            'total': 0,
            'sheets': {}
        }
        
        # 遍历共同工作表进行比较
        for sheet_name in common_sheets:
            sheet1 = wb1[sheet_name]
            sheet2 = wb2[sheet_name]
            
            # 获取最大行和最大列
            max_row1 = sheet1.max_row
            max_row2 = sheet2.max_row
            max_col1 = sheet1.max_column
            max_col2 = sheet2.max_column
            
            max_row = max(max_row1, max_row2)
            max_col = max(max_col1, max_col2)
            
            sheet_diff_count = 0
            sheet_diffs = []
            
            # 按单元格比较
            if compare_settings['type'] == 'cell':
                for row in range(1, max_row + 1):
                    for col in range(1, max_col + 1):
                        cell1 = sheet1.cell(row=row, column=col).value
                        cell2 = sheet2.cell(row=row, column=col).value
                        
                        # 检查是否需要忽略差异
                        if compare_settings['ignore_empty'] and cell1 is None and cell2 is None:
                            continue
                        
                        # 忽略大小写比较
                        if compare_settings['ignore_case'] and isinstance(cell1, str) and isinstance(cell2, str):
                            cell1_lower = cell1.lower()
                            cell2_lower = cell2.lower()
                            if cell1_lower != cell2_lower:
                                sheet_diff_count += 1
                                sheet_diffs.append(f"单元格 {row},{col}: {cell1} != {cell2}")
                        else:
                            if cell1 != cell2:
                                sheet_diff_count += 1
                                sheet_diffs.append(f"单元格 {row},{col}: {cell1} != {cell2}")
            
            # 按行比较
            elif compare_settings['type'] == 'row':
                for row in range(1, max_row + 1):
                    row1 = []
                    row2 = []
                    for col in range(1, max_col + 1):
                        row1.append(sheet1.cell(row=row, column=col).value)
                        row2.append(sheet2.cell(row=row, column=col).value)
                    
                    # 忽略空值
                    if compare_settings['ignore_empty']:
                        row1 = [cell for cell in row1 if cell is not None]
                        row2 = [cell for cell in row2 if cell is not None]
                    
                    if row1 != row2:
                        sheet_diff_count += 1
                        sheet_diffs.append(f"行 {row} 存在差异")
            
            # 按列比较
            elif compare_settings['type'] == 'column':
                for col in range(1, max_col + 1):
                    col1 = []
                    col2 = []
                    for row in range(1, max_row + 1):
                        col1.append(sheet1.cell(row=row, column=col).value)
                        col2.append(sheet2.cell(row=row, column=col).value)
                    
                    # 忽略空值
                    if compare_settings['ignore_empty']:
                        col1 = [cell for cell in col1 if cell is not None]
                        col2 = [cell for cell in col2 if cell is not None]
                    
                    if col1 != col2:
                        sheet_diff_count += 1
                        sheet_diffs.append(f"列 {col} 存在差异")
            
            # 保存工作表差异
            if sheet_diff_count > 0:
                differences['total'] += sheet_diff_count
                differences['sheets'][sheet_name] = {
                    'count': sheet_diff_count,
                    'details': sheet_diffs
                }
            
            print(f"  工作表 '{sheet_name}' 发现 {sheet_diff_count} 处差异")
        
        # 生成比较结果文件
        output_file = os.path.join(output_dir, 'compare_result.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Excel文件比较结果\n")
            f.write(f"====================\n")
            f.write(f"文件1: {os.path.basename(file1)}\n")
            f.write(f"文件2: {os.path.basename(file2)}\n")
            f.write(f"比较方式: {compare_settings['type']}\n")
            f.write(f"总差异数: {differences['total']}\n")
            f.write(f"====================\n\n")
            
            for sheet_name, diff_info in differences['sheets'].items():
                f.write(f"工作表: {sheet_name}\n")
                f.write(f"差异数: {diff_info['count']}\n")
                f.write(f"差异详情:\n")
                for detail in diff_info['details']:
                    f.write(f"  - {detail}\n")
                f.write(f"\n")
        
        print(f"  比较结果已保存到: {output_file}")
        print(f"  共发现 {differences['total']} 处差异")
        
        return True
    except InvalidFileException as e:
        print(f"  错误: 不支持的文件格式: {str(e)}")
        return False
    except Exception as e:
        print(f"  比较文件时出错: {str(e)}")
        return False

# 主函数
if __name__ == "__main__":
    import json
    
    # 解析命令行参数
    input_files = json.loads(sys.argv[1])
    output_dir = sys.argv[2]
    compare_settings = json.loads(sys.argv[3])
    
    if len(input_files) != 2:
        print("错误: 请选择两个要比较的Excel文件")
        sys.exit(1)
    
    file1 = input_files[0]
    file2 = input_files[1]
    
    result = compare_excel_files(file1, file2, output_dir, compare_settings)
    
    if result:
        print("\n比较完成！")
        sys.exit(0)
    else:
        print("\n比较失败！")
        sys.exit(1)
    `;

  try {
    // 调用Python脚本处理文件
    const result = await runPy(
      pythonCode,
      [files, outputDir, compareSettings],
      '比较文件差异'
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

.extra-content {
  margin-top: 16px;
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