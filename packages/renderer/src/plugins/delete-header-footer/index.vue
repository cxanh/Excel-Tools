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
        <p>请选择要删除页眉页脚的 Excel 文件</p>
      </a-card>
      
      <!-- 步骤2：设置规则 -->
      <a-card v-if="currentStep === 1" title="步骤2：设置规则" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="处理范围">
            <a-radio-group v-model:value="processingScope">
              <a-radio value="all">整个工作簿</a-radio>
              <a-radio value="selected">指定工作表</a-radio>
            </a-radio-group>
          </a-form-item>
          <a-form-item v-if="processingScope === 'selected'" label="工作表名称">
            <a-input
              v-model:value="targetSheet"
              placeholder="请输入要删除页眉页脚的工作表名称"
            />
          </a-form-item>
          <a-form-item label="删除选项">
            <a-checkbox v-model:checked="deleteHeader">删除页眉</a-checkbox>
            <a-checkbox v-model:checked="deleteFooter">删除页脚</a-checkbox>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤3：其他选项 -->
      <a-card v-if="currentStep === 2" title="步骤3：其他选项" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="输出选项">
            <a-checkbox v-model:checked="backupOriginal">备份原始文件</a-checkbox>
            <a-checkbox v-model:checked="overwriteExisting">覆盖现有文件</a-checkbox>
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
        
        <h2>支持的文件格式</h2>
        <ul>
          <li>.xlsx</li>
          <li>.xls</li>
          <li>.xlsm</li>
          <li>.xlsb</li>
        </ul>
        
        <h2>操作步骤</h2>
        <ol>
          <li>上传 Excel 文件</li>
          <li>选择处理范围和删除选项</li>
          <li>设置输出选项</li>
          <li>选择输出文件夹</li>
          <li>开始处理</li>
        </ol>
        
        <h2>注意事项</h2>
        <ul>
          <li>支持多种 Excel 格式文件</li>
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
const pluginTitle = ref('删除 Excel 页眉页脚')
const pluginDescription = ref('为 Excel 文件批量删除页眉页脚，支持指定工作表')

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
const processingScope = ref('all')
const targetSheet = ref('')
const deleteHeader = ref(true)
const deleteFooter = ref(true)
const backupOriginal = ref(true)
const overwriteExisting = ref(false)

// 处理结果
const processingResults = ref([])
const resultColumns = [
  { title: '文件名', dataIndex: 'fileName', key: 'fileName' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '结果', dataIndex: 'result', key: 'result' },
]

// 处理文件上传
const handleAddFile = async () => {
  const selectedFiles = await fileSelect({
    filters: [{ name: 'Excel Files', extensions: ['xlsx', 'xls', 'xlsm', 'xlsb'] }],
    multiple: true,
  })
  
  if (selectedFiles && selectedFiles.length > 0) {
    files.value = [...files.value, ...selectedFiles]
  }
}

// 从文件夹导入文件
const handleImportFolder = async () => {
  const selectedFiles = await folderSelect({
    filters: [{ name: 'Excel Files', extensions: ['xlsx', 'xls', 'xlsm', 'xlsb'] }],
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
  
  if (currentStep.value === 1 && !(deleteHeader.value || deleteFooter.value)) {
    message.error('请至少选择删除页眉或页脚')
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
      progressText.value = `正在准备处理文件: ${file.name}`
      
      // 读取文件内容
      const arrayBuffer = await file.arrayBuffer()
      const buffer = new Uint8Array(arrayBuffer)
      
      loadingProgress.value = 30 + Math.round((i / files.value.length) * 40)
      progressText.value = `正在删除页眉页脚: ${file.name}`
      
      // 准备Python脚本
      const scriptContent = `
from openpyxl import load_workbook
import io
import os
import sys

# 设置工作目录
sys.path.append('.')

# 获取输入输出参数
file_data = io.BytesIO(${JSON.stringify(Array.from(buffer))})
output_path = ${JSON.stringify(outputFolder.value)}
file_name = ${JSON.stringify(file.name)}
processing_scope = ${JSON.stringify(processingScope.value)}
target_sheet = ${JSON.stringify(targetSheet.value)}
del_header = ${JSON.stringify(deleteHeader.value)}
del_footer = ${JSON.stringify(deleteFooter.value)}
overwrite = ${JSON.stringify(overwriteExisting.value)}

# 加载工作簿
wb = load_workbook(file_data)

# 确定要处理的工作表
if processing_scope == 'all':
    sheet_names = wb.sheetnames
elif processing_scope == 'selected' and target_sheet:
    sheet_names = [target_sheet] if target_sheet in wb.sheetnames else []
else:
    sheet_names = []

# 为每个工作表删除页眉页脚
for sheet_name in sheet_names:
    ws = wb[sheet_name]
    
    if del_header:
        # 删除页眉
        ws.header_footer.left_header = ''
        ws.header_footer.center_header = ''
        ws.header_footer.right_header = ''
    
    if del_footer:
        # 删除页脚
        ws.header_footer.left_footer = ''
        ws.header_footer.center_footer = ''
        ws.header_footer.right_footer = ''

# 生成输出文件名
output_file_name = file_name

# 检查文件是否已存在
if os.path.exists(os.path.join(output_path, output_file_name)) and not overwrite:
    # 文件已存在且不覆盖，生成新文件名
    base_name = os.path.splitext(file_name)[0]
    ext = os.path.splitext(file_name)[1]
    counter = 1
    while os.path.exists(os.path.join(output_path, output_file_name)):
        output_file_name = f"{base_name}_{counter}{ext}"
        counter += 1

save_path = os.path.join(output_path, output_file_name)

# 保存文件
wb.save(save_path)

# 返回结果
result = {
    'status': 'success',
    'message': f'成功为 {len(sheet_names)} 个工作表删除页眉页脚',
    'file_name': file_name
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
            fileName: resultData.file_name,
            status: '成功',
            result: resultData.message
          })
        } catch (e) {
          processingResults.value.push({
            key: file.key,
            fileName: file.name,
            status: '成功',
            result: result.output
          })
        }
      } else {
        processingResults.value.push({
          key: file.key,
          fileName: file.name,
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