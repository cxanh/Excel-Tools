<template>
  <plugin-template
    :plugin-title="pluginTitle"
    :info-message="infoMessage"
    :error-message="errorMessage"
    :success-message="successMessage"
    :current-step="currentStep"
    :max-file-size="maxFileSize"
    :is-processing="isProcessing"
    :loading-progress="loadingProgress"
    :progress-text="progressText"
    :pyodide-loading="pyodideLoading"
    @add-file="handleAddFile"
    @import-folder="handleImportFolder"
    @more-action="handleMoreAction"
    @next-step="handleNextStep"
    @prev-step="handlePrevStep"
    @remove-file="handleRemoveFile"
    @close-info="infoMessage = ''"
    @close-error="errorMessage = ''"
    @close-success="successMessage = ''"
    @show-help="handleShowHelp"
  >
    <!-- 插件内容区域 -->
    <div class="plugin-specific-content">
      <!-- 步骤1：文件选择 -->
      <a-card v-if="currentStep === 0" title="步骤1：选择文件" class="step-card">
        <p>请选择要转换格式的 Excel 文件</p>
      </a-card>
      
      <!-- 步骤2：设置规则 -->
      <a-card v-if="currentStep === 1" title="步骤2：设置规则" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="目标格式">
            <a-select v-model:value="targetFormat">
              <a-select-option value="csv">CSV</a-select-option>
              <a-select-option value="xlsx">XLSX</a-select-option>
              <a-select-option value="xls">XLS</a-select-option>
              <a-select-option value="ods">ODS</a-select-option>
              <a-select-option value="html">HTML</a-select-option>
              <a-select-option value="txt">TXT</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item v-if="targetFormat === 'csv'" label="CSV选项">
            <a-row :gutter="[16, 0]">
              <a-col :span="12">
                <a-form-item no-style label="分隔符">
                  <a-input
                    v-model:value="csvDelimiter"
                    placeholder="请输入CSV分隔符"
                    style="width: 120px"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item no-style label="编码">
                  <a-select v-model:value="csvEncoding">
                    <a-select-option value="utf-8">UTF-8</a-select-option>
                    <a-select-option value="gbk">GBK</a-select-option>
                    <a-select-option value="gb2312">GB2312</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤3：其他选项 -->
      <a-card v-if="currentStep === 2" title="步骤3：其他选项" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="输出选项">
            <a-checkbox v-model:checked="overwriteExisting">覆盖现有文件</a-checkbox>
            <a-checkbox v-model:checked="createSubfolder">为每种格式创建子文件夹</a-checkbox>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤4：输出设置 -->
      <a-card v-if="currentStep === 3" title="步骤4：输出设置" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="输出文件夹">
            <a-input
              v-model:value="outputFolder"
              placeholder="请选择输出文件夹"
            >
              <template #addonAfter>
                <a-button type="primary" @click="selectOutputFolder">选择</a-button>
              </template>
            </a-input>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤5：开始处理 -->
      <a-card v-if="currentStep === 4" title="步骤5：处理结果" class="step-card">
        <div v-if="!isProcessing && processingResults.length > 0" class="results-container">
          <a-table
            :columns="resultColumns"
            :data-source="processingResults"
            :pagination="false"
            size="middle"
          ></a-table>
        </div>
      </a-card>
    </div>
    
    <!-- 帮助文档插槽 -->
    <template #help-content>
      <div class="help-documentation">
        <h1>{{ pluginTitle }}</h1>
        
        <h2>功能介绍</h2>
        <p>{{ pluginDescription }}</p>
        
        <h2>支持的转换格式</h2>
        <ul>
          <li>XLSX → CSV</li>
          <li>XLSX → XLS</li>
          <li>XLSX → ODS</li>
          <li>XLSX → HTML</li>
          <li>XLSX → TXT</li>
          <li>XLS → XLSX</li>
          <li>XLS → CSV</li>
          <li>CSV → XLSX</li>
        </ul>
        
        <h2>操作步骤</h2>
        <ol>
          <li>上传 Excel 文件</li>
          <li>选择目标格式</li>
          <li>设置输出选项</li>
          <li>选择输出文件夹</li>
          <li>开始处理</li>
        </ol>
        
        <h2>注意事项</h2>
        <ul>
          <li>支持 .xlsx、.xls、.csv 格式文件</li>
          <li>单个文件大小限制为 10MB</li>
          <li>处理大型文件可能需要较长时间</li>
        </ul>
      </div>
    </template>
  </plugin-template>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { message, notification } from 'ant-design-vue'
import PluginTemplate from '@/components/PluginTemplate.vue'
import { runPyScript } from '@/utils/py'
import { fileSelect, folderSelect } from '@/utils/file'

// 插件基本信息
const pluginTitle = ref('转换 Excel 格式')
const pluginDescription = ref('将Excel文件转换为不同格式，如xlsx转csv、xls等')

// 状态管理
const infoMessage = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const currentStep = ref(0)
const maxFileSize = ref(10 * 1024 * 1024) // 10MB
const isProcessing = ref(false)
const loadingProgress = ref(0)
const progressText = ref('')
const pyodideLoading = ref(false)

// 文件相关
const files = ref([])
const outputFolder = ref('')

// 处理规则
const targetFormat = ref('csv')
const csvDelimiter = ref(',')
const csvEncoding = ref('utf-8')
const overwriteExisting = ref(false)
const createSubfolder = ref(false)

// 处理结果
const processingResults = ref([])
const resultColumns = [
  { title: '原文件名', dataIndex: 'originalName', key: 'originalName' },
  { title: '目标格式', dataIndex: 'targetFormat', key: 'targetFormat' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '结果', dataIndex: 'result', key: 'result' },
]

// 处理文件上传
const handleAddFile = async () => {
  const selectedFiles = await fileSelect({
    filters: [{ name: 'Excel Files', extensions: ['xlsx', 'xls', 'csv'] }],
    multiple: true,
  })
  
  if (selectedFiles && selectedFiles.length > 0) {
    files.value = [...files.value, ...selectedFiles]
  }
}

// 从文件夹导入文件
const handleImportFolder = async () => {
  const selectedFiles = await folderSelect({
    filters: [{ name: 'Excel Files', extensions: ['xlsx', 'xls', 'csv'] }],
  })
  
  if (selectedFiles && selectedFiles.length > 0) {
    files.value = [...files.value, ...selectedFiles]
  }
}

// 处理更多操作
const handleMoreAction = (action) => {
  if (action === 'clear') {
    files.value = []
    message.info('已清空文件列表')
  }
}

// 处理下一步
const handleNextStep = async () => {
  if (currentStep.value === 0 && files.value.length === 0) {
    message.error('请选择要处理的文件')
    return
  }
  
  if (currentStep.value === 3 && !outputFolder.value) {
    const selectedFolder = await folderSelect()
    if (selectedFolder) {
      outputFolder.value = selectedFolder[0].path
    } else {
      message.error('请选择输出文件夹')
      return
    }
  }
  
  if (currentStep.value === 4) {
    // 开始处理
    await startProcessing()
  } else {
    currentStep.value++
  }
}

// 处理上一步
const handlePrevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 处理文件删除
const handleRemoveFile = (key) => {
  files.value = files.value.filter(file => file.key !== key)
}

// 处理显示帮助
const handleShowHelp = () => {
  // 帮助内容通过插槽提供
}

// 选择输出文件夹
const selectOutputFolder = async () => {
  const selectedFolder = await folderSelect()
  if (selectedFolder) {
    outputFolder.value = selectedFolder[0].path
  }
}

// 开始处理
const startProcessing = async () => {
  if (files.value.length === 0) {
    message.error('请选择要处理的文件')
    return
  }
  
  if (!outputFolder.value) {
    message.error('请选择输出文件夹')
    return
  }
  
  isProcessing.value = true
  pyodideLoading.value = true
  processingResults.value = []
  
  try {
    for (let i = 0; i < files.value.length; i++) {
      const file = files.value[i]
      loadingProgress.value = Math.round((i / files.value.length) * 30)
      progressText.value = `正在准备转换文件: ${file.name}`
      
      // 读取文件内容
      let fileContent
      if (file.name.toLowerCase().endsWith('.csv')) {
        fileContent = await file.text()
      } else {
        const arrayBuffer = await file.arrayBuffer()
        fileContent = Array.from(new Uint8Array(arrayBuffer))
      }
      
      loadingProgress.value = 30 + Math.round((i / files.value.length) * 40)
      progressText.value = `正在转换文件: ${file.name}`
      
      // 准备Python脚本
      const scriptContent = `
import pandas as pd
import io
import os
import sys

# 设置工作目录
sys.path.append('.')

# 获取输入输出参数
output_path = ${JSON.stringify(outputFolder.value)}
file_name = ${JSON.stringify(file.name)}
target_format = ${JSON.stringify(targetFormat.value)}
csv_delimiter = ${JSON.stringify(csvDelimiter.value) if csvDelimiter.value else ','}
csv_encoding = ${JSON.stringify(csvEncoding.value)}
overwrite = ${JSON.stringify(overwriteExisting.value)}
create_subfolder = ${JSON.stringify(createSubfolder.value)}

# 确定文件读取方式
file_ext = os.path.splitext(file_name)[1].lower()

# 创建输出目录
if create_subfolder:
    format_output_path = os.path.join(output_path, target_format)
    os.makedirs(format_output_path, exist_ok=True)
else:
    format_output_path = output_path

# 生成输出文件名
base_name = os.path.splitext(file_name)[0]
output_file_name = f"{base_name}.{target_format}"
save_path = os.path.join(format_output_path, output_file_name)

# 检查文件是否已存在
if os.path.exists(save_path) and not overwrite:
    # 文件已存在且不覆盖，生成新文件名
    counter = 1
    while os.path.exists(save_path):
        output_file_name = f"{base_name}_{counter}.{target_format}"
        save_path = os.path.join(format_output_path, output_file_name)
        counter += 1

# 读取原始文件
if file_ext in ['.xlsx', '.xls']:
    # 读取Excel文件
    df = pd.read_excel(io.BytesIO(bytes(${JSON.stringify(fileContent)})))
elif file_ext == '.csv':
    # 读取CSV文件
    df = pd.read_csv(io.StringIO(${JSON.stringify(fileContent)}), delimiter=csv_delimiter, encoding=csv_encoding)
else:
    # 不支持的文件格式
    result = {
        'status': 'error',
        'message': f'不支持的文件格式: {file_ext}',
        'original_name': file_name,
        'target_format': target_format
    }
    print(str(result))
    sys.exit()

# 转换并保存文件
if target_format == 'csv':
    df.to_csv(save_path, index=False, sep=csv_delimiter, encoding=csv_encoding)
elif target_format == 'xlsx':
    df.to_excel(save_path, index=False, engine='openpyxl')
elif target_format == 'xls':
    df.to_excel(save_path, index=False, engine='xlwt')
elif target_format == 'ods':
    df.to_excel(save_path, index=False, engine='odf')
elif target_format == 'html':
    df.to_html(save_path, index=False)
elif target_format == 'txt':
    df.to_csv(save_path, index=False, sep='\t', encoding=csv_encoding)

# 返回结果
result = {
    'status': 'success',
    'message': f'成功转换为 {target_format} 格式',
    'original_name': file_name,
    'target_format': target_format
}

print(str(result))
`
      
      // 执行Python脚本
      const result = await runPyScript(scriptContent)
      
      loadingProgress.value = 70 + Math.round((i / files.value.length) * 30)
      progressText.value = `正在保存结果: ${file.name}`
      
      if (result.success) {
        try {
          const resultData = JSON.parse(result.output)
          processingResults.value.push({
            key: file.key,
            originalName: resultData.original_name,
            targetFormat: resultData.target_format,
            status: resultData.status === 'success' ? '成功' : '失败',
            result: resultData.message
          })
        } catch (e) {
          processingResults.value.push({
            key: file.key,
            originalName: file.name,
            targetFormat: targetFormat.value,
            status: '成功',
            result: result.output
          })
        }
      } else {
        processingResults.value.push({
          key: file.key,
          originalName: file.name,
          targetFormat: targetFormat.value,
          status: '失败',
          result: result.error
        })
      }
    }
    
    loadingProgress.value = 100
    progressText.value = '处理完成'
    successMessage.value = '所有文件处理完成'
    
    notification.success({
      message: '处理完成',
      description: `共处理 ${files.value.length} 个文件`,
      placement: 'topRight'
    })
  } catch (error) {
    errorMessage.value = `处理失败: ${error.message}`
    notification.error({
      message: '处理失败',
      description: error.message,
      placement: 'topRight'
    })
  } finally {
    isProcessing.value = false
    pyodideLoading.value = false
  }
}
</script>

<style scoped>
.plugin-specific-content {
  margin: 20px 0;
}

.step-card {
  margin-bottom: 20px;
}

.results-container {
  margin-top: 20px;
}
</style>