<template>
  <PluginTemplate
    :title="'修改 Excel 文件属性'"
    :description="'为 Excel 文件批量修改文件属性，支持标题、作者、主题、关键词等元数据'"
    :hasHelp="true"
  >
    <template #step1-content>
      <div class="step-content">
        <a-form layout="vertical" class="setting-form">
          <a-form-item label="标题">
            <a-input
              v-model:value="fileProperties.title"
              placeholder="请输入文件标题"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="作者">
            <a-input
              v-model:value="fileProperties.author"
              placeholder="请输入作者名称"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="主题">
            <a-input
              v-model:value="fileProperties.subject"
              placeholder="请输入文件主题"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="关键词">
            <a-input
              v-model:value="fileProperties.keywords"
              placeholder="请输入关键词，多个关键词用逗号分隔"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="备注">
            <a-textarea
              v-model:value="fileProperties.comments"
              placeholder="请输入备注信息"
              :rows="3"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="公司">
            <a-input
              v-model:value="fileProperties.company"
              placeholder="请输入公司名称"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="类别">
            <a-input
              v-model:value="fileProperties.category"
              placeholder="请输入文件类别"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="模板">
            <a-input
              v-model:value="fileProperties.template"
              placeholder="请输入模板名称"
              style="width: 100%"
            />
          </a-form-item>
          <a-form-item label="属性设置选项">
            <a-checkbox v-model:checked="clearExistingProperties">清除现有属性后再设置</a-checkbox>
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
        <p>本工具可以为 Excel 文件批量修改文件属性，支持标题、作者、主题、关键词等元数据。</p>
        <h3>使用步骤</h3>
        <ol>
          <li>填写要修改的文件属性信息</li>
          <li>选择是否清除现有属性后再设置</li>
          <li>选择要处理的 Excel 文件</li>
          <li>选择输出目录</li>
          <li>点击开始处理，等待处理完成</li>
        </ol>
        <h3>注意事项</h3>
        <ul>
          <li>支持处理 .xlsx 和 .xls 格式的 Excel 文件</li>
          <li>处理后的文件会保存在指定的输出目录</li>
          <li>为空的属性字段不会被修改</li>
          <li>勾选"清除现有属性后再设置"会先清除所有现有属性，然后再应用新的属性设置</li>
        </ul>
      </div>
    </template>
  </PluginTemplate>
</template>

<script setup>
import { ref, reactive } from 'vue';
import PluginTemplate from '@plugins/plugin-template/index.vue';
import { runPy } from '@utils/py';

// 文件属性设置
const fileProperties = reactive({
  title: '',
  author: '',
  subject: '',
  keywords: '',
  comments: '',
  company: '',
  category: '',
  template: ''
});

const clearExistingProperties = ref(false);

// 定义处理函数
const processFiles = async (files, outputDir, selectedSheets = null) => {
  // 准备文件属性参数
  const properties = { ...fileProperties };
  const settings = {
    properties,
    clear_existing: clearExistingProperties.value
  };

  // 构建Python脚本
  const pythonCode = `
import os
import sys
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from openpyxl.workbook.properties import DocumentProperties

# 设置中文支持
sys.stdout.reconfigure(encoding='utf-8')

def update_file_properties(file_path, output_path, settings):
    """修改Excel文件的属性"""
    print(f"正在处理文件: {file_path}")
    
    try:
        # 加载工作簿
        wb = load_workbook(file_path)
        
        # 获取现有属性
        existing_props = wb.properties
        
        if settings['clear_existing']:
            # 清除现有属性，创建新的属性对象
            new_props = DocumentProperties()
        else:
            # 使用现有属性对象
            new_props = existing_props
        
        # 更新属性
        props_to_update = settings['properties']
        
        # 只更新非空的属性
        if props_to_update.get('title'):
            new_props.title = props_to_update['title']
            print(f"  更新标题: {props_to_update['title']}")
        
        if props_to_update.get('author'):
            new_props.creator = props_to_update['author']
            new_props.lastModifiedBy = props_to_update['author']
            print(f"  更新作者: {props_to_update['author']}")
        
        if props_to_update.get('subject'):
            new_props.subject = props_to_update['subject']
            print(f"  更新主题: {props_to_update['subject']}")
        
        if props_to_update.get('keywords'):
            new_props.keywords = props_to_update['keywords']
            print(f"  更新关键词: {props_to_update['keywords']}")
        
        if props_to_update.get('comments'):
            new_props.description = props_to_update['comments']
            print(f"  更新备注: {props_to_update['comments']}")
        
        if props_to_update.get('company'):
            # openpyxl的DocumentProperties没有直接的company属性，需要通过customProperties设置
            # 注意：这里需要特殊处理
            pass
        
        if props_to_update.get('category'):
            new_props.category = props_to_update['category']
            print(f"  更新类别: {props_to_update['category']}")
        
        if props_to_update.get('template'):
            new_props.template = props_to_update['template']
            print(f"  更新模板: {props_to_update['template']}")
        
        # 设置工作簿属性
        wb.properties = new_props
        
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
    settings = json.loads(sys.argv[3])
    
    print(f"开始处理 {len(input_files)} 个文件...")
    
    success_count = 0
    error_count = 0
    
    for input_file in input_files:
        # 构建输出文件路径
        file_name = os.path.basename(input_file)
        output_file = os.path.join(output_dir, file_name)
        
        # 处理文件
        if update_file_properties(input_file, output_file, settings):
            success_count += 1
        else:
            error_count += 1
    
    print(f"\n处理完成！成功: {success_count} 个, 失败: {error_count} 个")
    `;

  try {
    // 调用Python脚本处理文件
    const result = await runPy(
      pythonCode,
      [files, outputDir, settings],
      '修改文件属性'
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