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
        <p>请选择要拆分的 Excel 文件</p>
      </a-card>
      
      <!-- 步骤2：设置规则 -->
      <a-card v-if="currentStep === 1" title="步骤2：设置规则" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="拆分方式">
            <a-radio-group v-model:value="splitMode">
              <a-radio value="by-sheet">按工作表拆分</a-radio>
              <a-radio value="by-rows">按行数拆分</a-radio>
            </a-radio-group>
          </a-form-item>
          <a-form-item v-if="splitMode === 'by-rows'" label="拆分参数">
            <a-row :gutter="[16, 0]">
              <a-col :span="12">
                <a-form-item no-style label="每个文件行数">
                  <a-input-number
                    v-model:value="rowsPerFile"
                    :min="1"
                    :step="1"
                    placeholder="请输入每个文件的行数"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item no-style label="工作表名称">
                  <a-input
                    v-model:value="targetSheet"
                    placeholder="请输入要拆分的工作表名称（留空表示所有工作表）"
                  />
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
            <a-checkbox v-model:checked="includeHeader">每个文件包含表头</a-checkbox>
            <a-checkbox v-model:checked="addFileIndex">文件名添加序号</a-checkbox>
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
        
        <h2>操作步骤</h2>
        <ol>
          <li>上传 Excel 文件</li>
          <li>设置拆分方式（按工作表或按行数）</li>
          <li>设置输出选项</li>
          <li>选择输出文件夹</li>
          <li>开始处理</li>
        </ol>
        
        <h2>注意事项</h2>
        <ul>
          <li>支持 .xlsx 格式文件</li>
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
const pluginTitle = ref('拆分Excel文件')
const pluginDescription = ref('将一个Excel文件拆分为多个文件，支持按工作表或行数拆分')

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
const splitMode = ref('by-sheet')
const rowsPerFile = ref(1000)
const targetSheet = ref('')
const includeHeader = ref(true)
const addFileIndex = ref(true)

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
    filters: [{ name: 'Excel Files', extensions: ['xlsx', 'xls'] }],
    multiple: true,
  })
  
  if (selectedFiles && selectedFiles.length > 0) {
    files.value = [...selectedFiles] // 只保留最后选择的文件，因为只能处理一个文件
  }
}

// 从文件夹导入文件
const handleImportFolder = async () => {
  message.warning('拆分功能一次只能处理一个文件，请使用文件选择功能')
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
    message.error('请选择要拆分的文件')
    return
  }
  
  if (currentStep.value === 1 && splitMode === 'by-rows' && !rowsPerFile.value) {
    message.error('请输入每个文件的行数')
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
    message.error('请选择要拆分的文件')
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
    const file = files.value[0]
    const arrayBuffer = await file.arrayBuffer()
    const buffer = new Uint8Array(arrayBuffer)
    
    loadingProgress.value = 30
    progressText.value = '正在准备拆分文件'
    
    // 准备Python脚本
    const scriptContent = `
from openpyxl import load_workbook, Workbook
import io
import os
import sys

# 设置工作目录
sys.path.append('.')

# 获取输入输出参数
file_data = io.BytesIO(${JSON.stringify(Array.from(buffer))})
output_path = ${JSON.stringify(outputFolder.value)}
file_name = ${JSON.stringify(file.name)}
split_mode = ${JSON.stringify(splitMode.value)}
rows_per_file = ${JSON.stringify(rowsPerFile.value)}
target_sheet = ${JSON.stringify(targetSheet.value)}
include_header = ${JSON.stringify(includeHeader.value)}
add_file_index = ${JSON.stringify(addFileIndex.value)}

# 加载工作簿
wb = load_workbook(file_data)

# 获取要处理的工作表
if target_sheet:
    # 只处理指定工作表
    sheets_to_process = [target_sheet] if target_sheet in wb.sheetnames else []
else:
    # 处理所有工作表
    sheets_to_process = wb.sheetnames

# 拆分文件
created_files = []

if split_mode == 'by-sheet':
    # 按工作表拆分
    for sheet_name in sheets_to_process:
        ws = wb[sheet_name]
        
        # 创建新工作簿
        new_wb = Workbook()
        new_ws = new_wb.active
        new_ws.title = sheet_name
        
        # 复制数据
        for row in ws.iter_rows():
            new_row = []
            for cell in row:
                new_row.append(cell.value)
            new_ws.append(new_row)
        
        # 保存文件
        base_name = os.path.splitext(file_name)[0]
        new_file_name = f"{base_name}_{sheet_name}.xlsx"
        save_path = os.path.join(output_path, new_file_name)
        new_wb.save(save_path)
        
        created_files.append(new_file_name)
        
elif split_mode == 'by-rows':
    # 按行数拆分
    for sheet_name in sheets_to_process:
        ws = wb[sheet_name]
        
        # 获取所有数据行
        all_rows = list(ws.iter_rows(values_only=True))
        if not all_rows:
            continue
        
        # 分离表头
        header = all_rows[0]
        data_rows = all_rows[1:] if include_header else all_rows
        
        # 计算需要创建的文件数
        total_rows = len(data_rows)
        num_files = (total_rows + rows_per_file - 1) // rows_per_file
        
        # 拆分数据并保存到多个文件
        for i in range(num_files):
            # 获取当前文件的数据
            start_idx = i * rows_per_file
            end_idx = (i + 1) * rows_per_file
            file_rows = data_rows[start_idx:end_idx]
            
            # 创建新工作簿
            new_wb = Workbook()
            new_ws = new_wb.active
            new_ws.title = sheet_name
            
            # 添加表头
            if include_header:
                new_ws.append(header)
            
            # 添加数据行
            for row in file_rows:
                new_ws.append(row)
            
            # 保存文件
            base_name = os.path.splitext(file_name)[0]
            if add_file_index:
                new_file_name = f"{base_name}_{sheet_name}_{i+1}.xlsx"
            else:
                new_file_name = f"{base_name}_{sheet_name}.xlsx"
            save_path = os.path.join(output_path, new_file_name)
            new_wb.save(save_path)
            
            created_files.append(new_file_name)

# 返回结果
result = {
    'status': 'success',
    'message': f'成功创建 {len(created_files)} 个文件',
    'created_files': created_files
}

print(str(result))
`
      
      pyodideLoading.value = false
      loadingProgress.value = 60
      progressText.value = '正在执行拆分操作'
      
      // 执行Python脚本
      const result = await runPyScript(scriptContent)
      
      loadingProgress.value = 90
      progressText.value = '正在保存结果'
      
      if (result.success) {
        try {
          const resultData = JSON.parse(result.output)
          // 添加每个创建的文件到结果列表
          resultData.created_files.forEach(fileName => {
            processingResults.value.push({
              key: fileName,
              fileName: fileName,
              status: '成功',
              result: '文件已创建'
            })
          })
        } catch (e) {
          processingResults.value.push({
            key: 'split-result',
            fileName: '拆分结果',
            status: '成功',
            result: result.output
          })
        }
      } else {
        processingResults.value.push({
          key: 'split-result',
          fileName: '拆分结果',
          status: '失败',
          result: result.error
        })
      }
    
    loadingProgress.value = 100
    progressText.value = '处理完成'
    successMessage.value = '文件拆分完成'
    
    notification.success({
      message: '处理完成',
      description: `成功拆分文件，创建了 ${processingResults.value.length} 个新文件`,
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