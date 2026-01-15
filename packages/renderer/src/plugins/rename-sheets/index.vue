<template>
  <PluginTemplate
    :title="'重命名 Excel 工作表'"
    :description="'为 Excel 文件批量重命名工作表，支持自定义命名规则和批量处理'"
    :hasHelp="true"
  >
    <template #step1-content>
      <div class="step-content">
        <a-form layout="vertical" class="setting-form">
          <a-form-item label="命名规则">
            <a-radio-group v-model:value="renameRule" button-style="solid">
              <a-radio-button value="prefix">添加前缀</a-radio-button>
              <a-radio-button value="suffix">添加后缀</a-radio-button>
              <a-radio-button value="replace">替换文本</a-radio-button>
              <a-radio-button value="custom">自定义名称</a-radio-button>
            </a-radio-group>
          </a-form-item>
          
          <!-- 添加前缀配置 -->
          <a-form-item v-if="renameRule === 'prefix'" label="前缀文本">
            <a-input
              v-model:value="prefixText"
              placeholder="请输入要添加的前缀"
              style="width: 100%"
            />
          </a-form-item>
          
          <!-- 添加后缀配置 -->
          <a-form-item v-if="renameRule === 'suffix'" label="后缀文本">
            <a-input
              v-model:value="suffixText"
              placeholder="请输入要添加的后缀"
              style="width: 100%"
            />
          </a-form-item>
          
          <!-- 替换文本配置 -->
          <template v-if="renameRule === 'replace'">
            <a-form-item label="查找文本">
              <a-input
                v-model:value="findText"
                placeholder="请输入要查找的文本"
                style="width: 100%"
              />
            </a-form-item>
            <a-form-item label="替换为">
              <a-input
                v-model:value="replaceText"
                placeholder="请输入要替换的文本"
                style="width: 100%"
              />
            </a-form-item>
          </template>
          
          <!-- 自定义名称配置 -->
          <a-form-item v-if="renameRule === 'custom'" label="自定义名称列表">
            <a-textarea
              v-model:value="customNames"
              placeholder="请输入自定义名称，每行一个"
              :rows="4"
              style="width: 100%"
            />
            <div class="help-text">提示：名称数量应与工作表数量匹配，多余名称将被忽略</div>
          </a-form-item>
          
          <a-form-item label="重命名选项">
            <a-checkbox v-model:checked="includeHiddenSheets">包含隐藏工作表</a-checkbox>
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
        <p>本工具可以为 Excel 文件批量重命名工作表，支持多种命名规则和批量处理。</p>
        <h3>使用步骤</h3>
        <ol>
          <li>选择命名规则（添加前缀、添加后缀、替换文本或自定义名称）</li>
          <li>根据选择的规则设置相应的参数</li>
          <li>选择要处理的 Excel 文件</li>
          <li>选择输出目录</li>
          <li>点击开始处理，等待处理完成</li>
        </ol>
        <h3>注意事项</h3>
        <ul>
          <li>支持处理 .xlsx 和 .xls 格式的 Excel 文件</li>
          <li>处理后的文件会保存在指定的输出目录</li>
          <li>工作表名称不能包含以下字符：\ / ? * [ ] : | < > "</li>
          <li>自定义名称时，名称数量应与工作表数量匹配</li>
        </ul>
      </div>
    </template>
  </PluginTemplate>
</template>

<script setup>
import { ref, reactive } from 'vue';
import PluginTemplate from '@plugins/plugin-template/index.vue';
import { runPy } from '@utils/py';

// 重命名设置
const renameRule = ref('prefix');
const prefixText = ref('Sheet_');
const suffixText = ref('_2024');
const findText = ref('');
const replaceText = ref('');
const customNames = ref('');
const includeHiddenSheets = ref(true);

// 定义处理函数
const processFiles = async (files, outputDir, selectedSheets = null) => {
  // 准备重命名设置参数
  const renameSettings = {
    rule: renameRule.value,
    prefix: prefixText.value,
    suffix: suffixText.value,
    find: findText.value,
    replace: replaceText.value,
    custom_names: customNames.value.split('\n').filter(name => name.trim() !== ''),
    include_hidden: includeHiddenSheets.value
  };

  // 构建Python脚本
  const pythonCode = `
import os
import sys
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

# 设置中文支持
sys.stdout.reconfigure(encoding='utf-8')

def rename_sheets(file_path, output_path, rename_settings):
    """重命名Excel文件中的工作表"""
    print(f"正在处理文件: {file_path}")
    
    try:
        # 加载工作簿
        wb = load_workbook(file_path)
        
        # 获取所有工作表（包括或排除隐藏工作表）
        if rename_settings['include_hidden']:
            sheets = wb.worksheets
        else:
            sheets = [sheet for sheet in wb.worksheets if not sheet.sheet_state == 'hidden']
        
        print(f"  找到 {len(sheets)} 个工作表")
        
        # 获取自定义名称列表
        custom_names = rename_settings['custom_names']
        
        # 遍历工作表并重命名
        for idx, sheet in enumerate(sheets):
            original_name = sheet.title
            new_name = original_name
            
            # 根据命名规则生成新名称
            if rename_settings['rule'] == 'prefix':
                new_name = rename_settings['prefix'] + original_name
            elif rename_settings['rule'] == 'suffix':
                new_name = original_name + rename_settings['suffix']
            elif rename_settings['rule'] == 'replace':
                if rename_settings['find']:
                    new_name = original_name.replace(rename_settings['find'], rename_settings['replace'])
            elif rename_settings['rule'] == 'custom':
                if idx < len(custom_names):
                    new_name = custom_names[idx]
            
            # 清理新名称（移除无效字符）
            invalid_chars = ['\\', '/', '?', '*', '[', ']', ':', '|', '<', '>', '"']
            for char in invalid_chars:
                new_name = new_name.replace(char, '_')
            
            # 确保名称不为空
            if not new_name.strip():
                new_name = f'Sheet_{idx + 1}'
            
            # 确保名称不超过31个字符
            if len(new_name) > 31:
                new_name = new_name[:31]
            
            # 重命名工作表（如果名称有变化）
            if new_name != original_name:
                try:
                    sheet.title = new_name
                    print(f"  工作表 '{original_name}' 已重命名为 '{new_name}'")
                except Exception as e:
                    print(f"  重命名工作表 '{original_name}' 失败: {str(e)}")
        
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
    rename_settings = json.loads(sys.argv[3])
    
    print(f"开始处理 {len(input_files)} 个文件...")
    
    success_count = 0
    error_count = 0
    
    for input_file in input_files:
        # 构建输出文件路径
        file_name = os.path.basename(input_file)
        output_file = os.path.join(output_dir, file_name)
        
        # 处理文件
        if rename_sheets(input_file, output_file, rename_settings):
            success_count += 1
        else:
            error_count += 1
    
    print(f"\n处理完成！成功: {success_count} 个, 失败: {error_count} 个")
    `;

  try {
    // 调用Python脚本处理文件
    const result = await runPy(
      pythonCode,
      [files, outputDir, renameSettings],
      '重命名工作表'
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

.help-text {
  margin-top: 8px;
  color: #666;
  font-size: 12px;
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