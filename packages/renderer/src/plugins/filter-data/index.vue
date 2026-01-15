<template>
  <PluginTemplate
    :title="'筛选 Excel 数据'"
    :description="'为 Excel 文件批量筛选数据，支持按条件筛选和自定义筛选规则'"
    :hasHelp="true"
  >
    <template #step1-content>
      <div class="step-content">
        <a-form layout="vertical" class="setting-form">
          <a-form-item label="筛选列">
            <a-input
              v-model:value="filterColumn"
              placeholder="请输入要筛选的列（如：A, B, C 或 1, 2, 3）"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="筛选条件">
            <a-select
              v-model:value="filterCondition"
              placeholder="请选择筛选条件"
              style="width: 100%"
            >
              <a-select-option value="equals">等于</a-select-option>
              <a-select-option value="contains">包含</a-select-option>
              <a-select-option value="starts_with">以...开头</a-select-option>
              <a-select-option value="ends_with">以...结尾</a-select-option>
              <a-select-option value="greater_than">大于</a-select-option>
              <a-select-option value="less_than">小于</a-select-option>
              <a-select-option value="greater_equals">大于等于</a-select-option>
              <a-select-option value="less_equals">小于等于</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="筛选值">
            <a-input
              v-model:value="filterValue"
              placeholder="请输入筛选值"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="筛选选项">
            <a-checkbox v-model:checked="filterHeaders">包含标题行</a-checkbox>
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
        <p>本工具可以为 Excel 文件批量筛选数据，支持多种筛选条件和自定义筛选规则。</p>
        <h3>使用步骤</h3>
        <ol>
          <li>输入要筛选的列（如：A, B, C 或 1, 2, 3）</li>
          <li>选择筛选条件（等于、包含、大于等）</li>
          <li>输入筛选值</li>
          <li>选择是否包含标题行</li>
          <li>选择要处理的 Excel 文件</li>
          <li>选择输出目录</li>
          <li>点击开始处理，等待处理完成</li>
        </ol>
        <h3>注意事项</h3>
        <ul>
          <li>支持处理 .xlsx 和 .xls 格式的 Excel 文件</li>
          <li>处理后的文件会保存在指定的输出目录</li>
          <li>筛选结果会保留符合条件的数据行</li>
        </ul>
      </div>
    </template>
  </PluginTemplate>
</template>

<script setup>
import { ref, reactive } from 'vue';
import PluginTemplate from '@plugins/plugin-template/index.vue';
import { runPy } from '@utils/py';

// 筛选设置
const filterColumn = ref('A');
const filterCondition = ref('equals');
const filterValue = ref('');
const filterHeaders = ref(true);

// 定义处理函数
const processFiles = async (files, outputDir, selectedSheets = null) => {
  // 准备筛选设置参数
  const filterSettings = {
    column: filterColumn.value,
    condition: filterCondition.value,
    value: filterValue.value,
    headers: filterHeaders.value
  };

  // 构建Python脚本
  const pythonCode = `
import os
import sys
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

# 设置中文支持
sys.stdout.reconfigure(encoding='utf-8')

def filter_excel_data(file_path, output_path, filter_settings):
    """筛选Excel文件中的数据"""
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
            if filter_settings['headers']:
                # 包含标题行
                data_start_row = 2
                header_row = 1
            else:
                # 不包含标题行
                data_start_row = 1
                header_row = None
            
            # 转换列字母为数字
            def col_to_num(col):
                if col.isdigit():
                    return int(col)
                col_num = 0
                for c in col.upper():
                    col_num = col_num * 26 + (ord(c) - ord('A') + 1)
                return col_num
            
            # 获取筛选列
            filter_col_num = col_to_num(filter_settings['column'])
            
            # 获取筛选值和条件
            filter_value = filter_settings['value']
            filter_condition = filter_settings['condition']
            
            # 定义筛选函数
            def is_match(cell_value):
                """判断单元格值是否匹配筛选条件"""
                # 处理空值
                if cell_value is None:
                    cell_value = ''
                
                # 转换为字符串进行比较
                cell_str = str(cell_value)
                filter_str = str(filter_value)
                
                if filter_condition == 'equals':
                    return cell_str == filter_str
                elif filter_condition == 'contains':
                    return filter_str in cell_str
                elif filter_condition == 'starts_with':
                    return cell_str.startswith(filter_str)
                elif filter_condition == 'ends_with':
                    return cell_str.endswith(filter_str)
                elif filter_condition == 'greater_than':
                    try:
                        return float(cell_str) > float(filter_str)
                    except ValueError:
                        return False
                elif filter_condition == 'less_than':
                    try:
                        return float(cell_str) < float(filter_str)
                    except ValueError:
                        return False
                elif filter_condition == 'greater_equals':
                    try:
                        return float(cell_str) >= float(filter_str)
                    except ValueError:
                        return False
                elif filter_condition == 'less_equals':
                    try:
                        return float(cell_str) <= float(filter_str)
                    except ValueError:
                        return False
                return False
            
            # 收集符合条件的行
            matched_rows = []
            
            # 收集标题行（如果有）
            if header_row:
                header = []
                for col in range(1, max_col + 1):
                    header.append(sheet.cell(row=header_row, column=col).value)
                matched_rows.append(header)
            
            # 收集符合条件的数据行
            for row in range(data_start_row, max_row + 1):
                cell_value = sheet.cell(row=row, column=filter_col_num).value
                if is_match(cell_value):
                    data_row = []
                    for col in range(1, max_col + 1):
                        data_row.append(sheet.cell(row=row, column=col).value)
                    matched_rows.append(data_row)
            
            # 清空工作表内容
            for row in range(1, max_row + 1):
                for col in range(1, max_col + 1):
                    sheet.cell(row=row, column=col).value = None
            
            # 写入筛选结果
            for new_row, data_row in enumerate(matched_rows, start=1):
                for new_col, cell_value in enumerate(data_row, start=1):
                    sheet.cell(row=new_row, column=new_col).value = cell_value
            
            print(f"  工作表 '{sheet.title}' 筛选完成，保留 {len(matched_rows)} 行数据")
        
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
    filter_settings = json.loads(sys.argv[3])
    
    print(f"开始处理 {len(input_files)} 个文件...")
    
    success_count = 0
    error_count = 0
    
    for input_file in input_files:
        # 构建输出文件路径
        file_name = os.path.basename(input_file)
        output_file = os.path.join(output_dir, file_name)
        
        # 处理文件
        if filter_excel_data(input_file, output_file, filter_settings):
            success_count += 1
        else:
            error_count += 1
    
    print(f"\n处理完成！成功: {success_count} 个, 失败: {error_count} 个")
    `;

  try {
    // 调用Python脚本处理文件
    const result = await runPy(
      pythonCode,
      [files, outputDir, filterSettings],
      '筛选数据'
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