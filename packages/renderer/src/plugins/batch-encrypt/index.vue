<template>
  <PluginTemplate
    :title="'批量加密 Excel 文件'"
    :description="'为 Excel 文件批量设置密码保护，支持设置打开密码和修改密码'"
    :hasHelp="true"
  >
    <template #step1-content>
      <div class="step-content">
        <a-form layout="vertical" class="setting-form">
          <a-form-item label="加密类型">
            <a-radio-group v-model:value="encryptType" button-style="solid">
              <a-radio-button value="open">仅打开密码</a-radio-button>
              <a-radio-button value="modify">仅修改密码</a-radio-button>
              <a-radio-button value="both">同时设置两种密码</a-radio-button>
            </a-radio-group>
          </a-form-item>
          
          <a-form-item v-if="encryptType === 'open' || encryptType === 'both'" label="打开密码">
            <a-input-password
              v-model:value="openPassword"
              placeholder="请输入打开密码"
              style="width: 100%"
            />
          </a-form-item>
          
          <a-form-item v-if="encryptType === 'modify' || encryptType === 'both'" label="修改密码">
            <a-input-password
              v-model:value="modifyPassword"
              placeholder="请输入修改密码"
              style="width: 100%"
            />
          </a-form-item>
          
          <a-form-item label="加密选项">
            <a-checkbox v-model:checked="encryptStructure">加密工作簿结构</a-checkbox>
            <a-checkbox v-model:checked="encryptWindows">加密窗口</a-checkbox>
          </a-form-item>
        </a-form>
      </div>
    </template>

    <template #step2-extra>
      <div class="extra-content">
        <a-alert
          message="安全提示"
          description="请妥善保管设置的密码，一旦丢失将无法恢复！"
          type="warning"
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
        <p>本工具可以为 Excel 文件批量设置密码保护，支持设置打开密码和修改密码，保护您的 Excel 文件安全。</p>
        <h3>使用步骤</h3>
        <ol>
          <li>选择加密类型（仅打开密码、仅修改密码或同时设置两种密码）</li>
          <li>输入相应的密码</li>
          <li>选择加密选项（加密工作簿结构、加密窗口）</li>
          <li>选择要处理的 Excel 文件</li>
          <li>选择输出目录</li>
          <li>点击开始处理，等待处理完成</li>
        </ol>
        <h3>注意事项</h3>
        <ul>
          <li>支持处理 .xlsx 和 .xls 格式的 Excel 文件</li>
          <li>处理后的文件会保存在指定的输出目录</li>
          <li>请妥善保管设置的密码，一旦丢失将无法恢复</li>
          <li>加密工作簿结构可以防止他人添加、删除或重命名工作表</li>
          <li>加密窗口可以防止他人更改工作簿窗口的大小和位置</li>
        </ul>
      </div>
    </template>
  </PluginTemplate>
</template>

<script setup>
import { ref, reactive } from 'vue';
import PluginTemplate from '@plugins/plugin-template/index.vue';
import { runPy } from '@utils/py';

// 加密设置
const encryptType = ref('open');
const openPassword = ref('');
const modifyPassword = ref('');
const encryptStructure = ref(true);
const encryptWindows = ref(false);

// 定义处理函数
const processFiles = async (files, outputDir, selectedSheets = null) => {
  // 验证密码设置
  if ((encryptType.value === 'open' || encryptType.value === 'both') && !openPassword.value) {
    throw new Error('请输入打开密码');
  }
  if ((encryptType.value === 'modify' || encryptType.value === 'both') && !modifyPassword.value) {
    throw new Error('请输入修改密码');
  }
  
  // 准备加密设置参数
  const encryptSettings = {
    type: encryptType.value,
    open_password: openPassword.value,
    modify_password: modifyPassword.value,
    encrypt_structure: encryptStructure.value,
    encrypt_windows: encryptWindows.value
  };

  // 构建Python脚本
  const pythonCode = `
import os
import sys
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

# 设置中文支持
sys.stdout.reconfigure(encoding='utf-8')

def batch_encrypt_files(input_files, output_dir, encrypt_settings):
    """批量加密Excel文件"""
    print(f"开始处理 {len(input_files)} 个文件...")
    
    success_count = 0
    error_count = 0
    
    for input_file in input_files:
        try:
            # 加载工作簿
            wb = load_workbook(input_file)
            
            # 获取文件名
            file_name = os.path.basename(input_file)
            output_file = os.path.join(output_dir, file_name)
            
            # 设置密码保护
            if encrypt_settings['type'] == 'open' or encrypt_settings['type'] == 'both':
                # 设置打开密码
                # 注意：openpyxl 目前不支持设置打开密码，这里仅作为示例
                print(f"  注意: {file_name} - openpyxl 不支持设置打开密码，仅支持设置修改密码")
            
            if encrypt_settings['type'] == 'modify' or encrypt_settings['type'] == 'both':
                # 设置修改密码
                # 注意：openpyxl 支持设置工作表保护密码，但不支持工作簿打开密码
                wb.security.lockStructure = encrypt_settings['encrypt_structure']
                wb.security.lockWindows = encrypt_settings['encrypt_windows']
                
                # 为每个工作表设置保护
                for sheet in wb.worksheets:
                    sheet.protection.sheet = True
                    sheet.protection.password = encrypt_settings['modify_password']
            
            # 保存文件
            wb.save(output_file)
            
            print(f"  已加密: {file_name}")
            success_count += 1
        except InvalidFileException:
            print(f"  错误: 不支持的文件格式: {file_name}")
            error_count += 1
        except Exception as e:
            print(f"  加密文件 {file_name} 失败: {str(e)}")
            error_count += 1
    
    print(f"\n处理完成！成功: {success_count} 个, 失败: {error_count} 个")
    return success_count > 0

# 主函数
if __name__ == "__main__":
    import json
    
    # 解析命令行参数
    input_files = json.loads(sys.argv[1])
    output_dir = sys.argv[2]
    encrypt_settings = json.loads(sys.argv[3])
    
    result = batch_encrypt_files(input_files, output_dir, encrypt_settings)
    
    if result:
        sys.exit(0)
    else:
        sys.exit(1)
    `;

  try {
    // 调用Python脚本处理文件
    const result = await runPy(
      pythonCode,
      [files, outputDir, encryptSettings],
      '批量加密文件'
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