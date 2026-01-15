<template>
  <PluginTemplate
    :title="'批量重命名 Excel 文件'"
    :description="'为 Excel 文件批量重命名，支持自定义命名规则和批量处理'"
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
          <a-form-item v-if="renameRule === 'custom'" label="自定义名称格式">
            <a-input
              v-model:value="customNameFormat"
              placeholder="请输入自定义名称格式，如：文件_{index}_{date}"
              style="width: 100%"
            />
            <div class="help-text">可用变量：{index}（序号），{date}（当前日期）</div>
          </a-form-item>
          
          <a-form-item label="重命名选项">
            <a-checkbox v-model:checked="keepOriginalExtension">保留原始文件扩展名</a-checkbox>
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
        <p>本工具可以为 Excel 文件批量重命名，支持多种命名规则和批量处理。</p>
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
          <li>自定义名称时，可以使用 {index}（序号）和 {date}（当前日期）变量</li>
          <li>建议勾选"保留原始文件扩展名"选项</li>
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
const prefixText = ref('Excel_');
const suffixText = ref('_2024');
const findText = ref('');
const replaceText = ref('');
const customNameFormat = ref('文件_{index}_{date}');
const keepOriginalExtension = ref(true);

// 定义处理函数
const processFiles = async (files, outputDir, selectedSheets = null) => {
  // 准备重命名设置参数
  const renameSettings = {
    rule: renameRule.value,
    prefix: prefixText.value,
    suffix: suffixText.value,
    find: findText.value,
    replace: replaceText.value,
    custom_format: customNameFormat.value,
    keep_extension: keepOriginalExtension.value
  };

  // 构建Python脚本
  const pythonCode = `
import os
import sys
import datetime

# 设置中文支持
sys.stdout.reconfigure(encoding='utf-8')

def batch_rename_files(input_files, output_dir, rename_settings):
    """批量重命名Excel文件"""
    print(f"开始处理 {len(input_files)} 个文件...")
    
    success_count = 0
    error_count = 0
    
    for idx, input_file in enumerate(input_files, start=1):
        try:
            # 获取原始文件名和扩展名
            file_name = os.path.basename(input_file)
            base_name, extension = os.path.splitext(file_name)
            
            # 根据命名规则生成新名称
            new_base_name = base_name
            
            if rename_settings['rule'] == 'prefix':
                new_base_name = rename_settings['prefix'] + base_name
            elif rename_settings['rule'] == 'suffix':
                new_base_name = base_name + rename_settings['suffix']
            elif rename_settings['rule'] == 'replace':
                if rename_settings['find']:
                    new_base_name = base_name.replace(rename_settings['find'], rename_settings['replace'])
            elif rename_settings['rule'] == 'custom':
                # 替换变量
                current_date = datetime.datetime.now().strftime('%Y%m%d')
                new_base_name = rename_settings['custom_format']
                new_base_name = new_base_name.replace('{index}', str(idx))
                new_base_name = new_base_name.replace('{date}', current_date)
            
            # 构建新文件名
            if rename_settings['keep_extension']:
                new_file_name = new_base_name + extension
            else:
                new_file_name = new_base_name + '.xlsx'  # 默认转换为xlsx格式
            
            # 构建输出文件路径
            output_file = os.path.join(output_dir, new_file_name)
            
            # 复制文件到新路径（重命名）
            import shutil
            shutil.copy2(input_file, output_file)
            
            print(f"  已重命名: {file_name} -> {new_file_name}")
            success_count += 1
        except Exception as e:
            print(f"  重命名文件 {input_file} 失败: {str(e)}")
            error_count += 1
    
    return {
        'success': success_count,
        'error': error_count
    }

# 主函数
if __name__ == "__main__":
    import json
    
    # 解析命令行参数
    input_files = json.loads(sys.argv[1])
    output_dir = sys.argv[2]
    rename_settings = json.loads(sys.argv[3])
    
    result = batch_rename_files(input_files, output_dir, rename_settings)
    
    print(f"\n处理完成！成功: {result['success']} 个, 失败: {result['error']} 个")
    `;

  try {
    // 调用Python脚本处理文件
    const result = await runPy(
      pythonCode,
      [files, outputDir, renameSettings],
      '批量重命名文件'
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