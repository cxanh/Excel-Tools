<template>
  <PluginTemplate
    :title="'排序 Excel 数据'"
    :description="'为 Excel 文件批量排序数据，支持按多列排序和自定义排序规则'"
    :hasHelp="true"
  >
    <template #step1-content>
      <div class="step-content">
        <a-form layout="vertical" class="setting-form">
          <a-form-item label="排序方式">
            <a-radio-group v-model:value="sortType" button-style="solid">
              <a-radio-button value="asc">升序</a-radio-button>
              <a-radio-button value="desc">降序</a-radio-button>
            </a-radio-group>
          </a-form-item>
          <a-form-item label="排序列">
            <a-input
              v-model:value="sortColumn"
              placeholder="请输入要排序的列（如：A, B, C 或 1, 2, 3）"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="排序选项">
            <a-checkbox v-model:checked="sortHeaders">包含标题行</a-checkbox>
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
        <p>本工具可以为 Excel 文件批量排序数据，支持按多列排序和自定义排序规则。</p>
        <h3>使用步骤</h3>
        <ol>
          <li>选择排序方式（升序或降序）</li>
          <li>输入要排序的列（如：A, B, C 或 1, 2, 3）</li>
          <li>选择是否包含标题行</li>
          <li>选择要处理的 Excel 文件</li>
          <li>选择输出目录</li>
          <li>点击开始处理，等待处理完成</li>
        </ol>
        <h3>注意事项</h3>
        <ul>
          <li>支持处理 .xlsx 和 .xls 格式的 Excel 文件</li>
          <li>处理后的文件会保存在指定的输出目录</li>
          <li>可以同时指定多个排序列，用逗号分隔（如：A,B,C）</li>
        </ul>
      </div>
    </template>
  </PluginTemplate>
</template>

<script setup>
import { ref, reactive } from 'vue';
import PluginTemplate from '@plugins/plugin-template/index.vue';
import { runPy } from '@utils/py';

// 排序设置
const sortType = ref('asc');
const sortColumn = ref('A');
const sortHeaders = ref(true);

// 定义处理函数
const processFiles = async (files, outputDir, selectedSheets = null) => {
  // 准备排序设置参数
  const sortSettings = {
    type: sortType.value,
    column: sortColumn.value,
    headers: sortHeaders.value
  };

  // 构建Python脚本
  const pythonCode = `
import os
import sys
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

# 设置中文支持
sys.stdout.reconfigure(encoding='utf-8')

def sort_excel_data(file_path, output_path, sort_settings):
    """排序Excel文件中的数据"""
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
            if sort_settings['headers']:
                # 包含标题行，从第2行开始排序
                data_start_row = 2
                header_row = 1
            else:
                # 不包含标题行，从第1行开始排序
                data_start_row = 1
                header_row = None
            
            # 获取排序列
            sort_columns = [col.strip() for col in sort_settings['column'].split(',')]
            
            # 转换列字母为数字
            def col_to_num(col):
                if col.isdigit():
                    return int(col)
                col_num = 0
                for c in col.upper():
                    col_num = col_num * 26 + (ord(c) - ord('A') + 1)
                return col_num
            
            # 转换所有排序列为数字
            sort_col_nums = [col_to_num(col) for col in sort_columns]
            
            # 获取数据范围
            data = []
            for row in range(data_start_row, max_row + 1):
                row_data = []
                for col in range(1, max_col + 1):
                    cell_value = sheet.cell(row=row, column=col).value
                    row_data.append(cell_value)
                # 添加行号以便排序后恢复
                row_data.append(row)
                data.append(row_data)
            
            # 定义排序键
            def sort_key(row_data):
                keys = []
                for col_num in sort_col_nums:
                    if col_num <= len(row_data) - 1:  # 减1是因为最后一列是行号
                        keys.append(row_data[col_num - 1])
                    else:
                        keys.append(None)
                return keys
            
            # 执行排序
            data.sort(key=sort_key, reverse=(sort_settings['type'] == 'desc'))
            
            # 将排序后的数据写回工作表
            for idx, row_data in enumerate(data):
                original_row = row_data.pop()  # 获取原始行号
                new_row = data_start_row + idx
                
                # 如果行号相同，跳过
                if original_row == new_row:
                    continue
                
                # 复制数据到新位置
                for col in range(1, max_col + 1):
                    sheet.cell(row=new_row, column=col).value = row_data[col - 1]
            
            print(f"  工作表 '{sheet.title}' 排序完成")
        
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
    sort_settings = json.loads(sys.argv[3])
    
    print(f"开始处理 {len(input_files)} 个文件...")
    
    success_count = 0
    error_count = 0
    
    for input_file in input_files:
        # 构建输出文件路径
        file_name = os.path.basename(input_file)
        output_file = os.path.join(output_dir, file_name)
        
        # 处理文件
        if sort_excel_data(input_file, output_file, sort_settings):
            success_count += 1
        else:
            error_count += 1
    
    print(f"\n处理完成！成功: {success_count} 个, 失败: {error_count} 个")
    `;

  try {
    // 调用Python脚本处理文件
    const result = await runPy(
      pythonCode,
      [files, outputDir, sortSettings],
      '排序数据'
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