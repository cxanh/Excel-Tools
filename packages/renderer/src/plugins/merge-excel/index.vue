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
        <p>请选择要合并的多个 Excel 文件</p>
      </a-card>
      
      <!-- 步骤2：设置规则 -->
      <a-card v-if="currentStep === 1" title="步骤2：设置规则" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="合并方式">
            <a-radio-group v-model:value="mergeMode">
              <a-radio value="sheets">合并为多个工作表</a-radio>
              <a-radio value="data">合并数据到单个工作表</a-radio>
            </a-radio-group>
          </a-form-item>
          <a-form-item v-if="mergeMode === 'data'" label="数据合并选项">
            <a-checkbox v-model:checked="keepHeaders">保留每个文件的表头</a-checkbox>
            <a-checkbox v-model:checked="addSourceColumn">添加来源文件列</a-checkbox>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤3：其他选项 -->
      <a-card v-if="currentStep === 2" title="步骤3：其他选项" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="输出文件名">
            <a-input
              v-model:value="outputFileName"
              placeholder="请输入合并后的文件名（不包含扩展名）"
            />
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
          <li>上传多个 Excel 文件</li>
          <li>设置合并方式（多个工作表或单个工作表）</li>
          <li>设置输出文件名</li>
          <li>选择输出文件夹</li>
          <li>开始处理</li>
        </ol>
        
        <h2>注意事项</h2>
        <ul>
          <li>支持 .xlsx 和 .xls 格式文件</li>
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
const pluginTitle = ref('合并Excel文件')
const pluginDescription = ref('批量合并多个Excel文件的内容到一个文件中')

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
const outputFileName = ref('merged_excel')

// 处理规则
const mergeMode = ref('sheets')
const keepHeaders = ref(false)
const addSourceColumn = ref(false)

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
    files.value = [...files.value, ...selectedFiles]
  }
}

// 从文件夹导入文件
const handleImportFolder = async () => {
  const selectedFiles = await folderSelect({
    filters: [{ name: 'Excel Files', extensions: ['xlsx', 'xls'] }],
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
  if (currentStep.value === 0 && files.value.length < 2) {
    message.error('请选择至少2个要合并的文件')
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
  if (files.value.length < 2) {
    message.error('请选择至少2个要合并的文件')
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
    // 准备文件数据
    const fileDataList = []
    for (const file of files.value) {
      const arrayBuffer = await file.arrayBuffer()
      const buffer = new Uint8Array(arrayBuffer)
      fileDataList.push({
        name: file.name,
        data: Array.from(buffer)
      })
    }
    
    loadingProgress.value = 30
    progressText.value = '正在准备合并文件'
    
    // 准备Python脚本
    const scriptContent = `
from openpyxl import load_workbook, Workbook
import io
import os
import sys

# 设置工作目录
sys.path.append('.')

# 获取输入输出参数
output_path = ${JSON.stringify(outputFolder.value)}
output_file_name = ${JSON.stringify(outputFileName.value)}
file_data_list = ${JSON.stringify(fileDataList)}
merge_mode = ${JSON.stringify(mergeMode.value)}
keep_headers = ${JSON.stringify(keepHeaders.value)}
add_source_col = ${JSON.stringify(addSourceColumn.value)}

# 创建新工作簿
new_wb = Workbook()
new_wb.remove(new_wb.active)  # 删除默认工作表

# 合并文件
merged_files_count = 0
merged_sheets_count = 0

if merge_mode == 'sheets':
    # 合并为多个工作表模式
    for file_data in file_data_list:
        # 加载源工作簿
        wb = load_workbook(io.BytesIO(bytes(file_data['data'])))
        file_name = file_data['name']
        
        for sheet_name in wb.sheetnames:
            # 复制工作表到新工作簿
            ws = wb[sheet_name]
            # 为避免工作表名冲突，添加文件名前缀
            new_sheet_name = f"{os.path.splitext(file_name)[0]}_{sheet_name}"
            
            # 如果工作表名已存在，添加序号
            counter = 1
            original_name = new_sheet_name
            while new_sheet_name in new_wb.sheetnames:
                new_sheet_name = f"{original_name}_{counter}"
                counter += 1
            
            # 创建新工作表
            new_ws = new_wb.create_sheet(title=new_sheet_name)
            
            # 复制数据
            for row in ws.iter_rows():
                new_row = []
                for cell in row:
                    new_row.append(cell.value)
                new_ws.append(new_row)
            
            merged_sheets_count += 1
        
        merged_files_count += 1
        
elif merge_mode == 'data':
    # 合并数据到单个工作表模式
    new_ws = new_wb.active
    first_file = True
    
    for file_data in file_data_list:
        # 加载源工作簿
        wb = load_workbook(io.BytesIO(bytes(file_data['data'])))
        file_name = file_data['name']
        
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            rows = list(ws.iter_rows(values_only=True))
            
            if not rows:
                continue
            
            # 处理表头
            headers = rows[0]
            data_rows = rows[1:]
            
            if first_file:
                # 第一个文件，写入表头
                if add_source_col:
                    new_ws.append(list(headers) + ['来源文件'])
                else:
                    new_ws.append(list(headers))
                first_file = False
            elif not keep_headers:
                # 不是第一个文件且不保留表头，跳过表头
                pass
            else:
                # 保留表头，写入分隔行
                if add_source_col:
                    new_ws.append(list(headers) + ['来源文件'])
                else:
                    new_ws.append(list(headers))
            
            # 写入数据行
            for row in data_rows:
                if add_source_col:
                    new_ws.append(list(row) + [file_name])
                else:
                    new_ws.append(list(row))
            
            merged_sheets_count += 1
        
        merged_files_count += 1

# 保存合并后的文件
save_path = os.path.join(output_path, f"{output_file_name}.xlsx")
new_wb.save(save_path)

# 返回结果
result = {
    'status': 'success',
    'message': f'成功合并 {merged_files_count} 个文件，共 {merged_sheets_count} 个工作表',
    'file_name': f"{output_file_name}.xlsx"
}

print(str(result))
`
      
      pyodideLoading.value = false
      loadingProgress.value = 60
      progressText.value = '正在执行合并操作'
      
      // 执行Python脚本
      const result = await runPyScript(scriptContent)
      
      loadingProgress.value = 90
      progressText.value = '正在保存结果'
      
      if (result.success) {
        try {
          const resultData = JSON.parse(result.output)
          processingResults.value.push({
            key: 'merged-result',
            fileName: resultData.file_name,
            status: '成功',
            result: resultData.message
          })
        } catch (e) {
          processingResults.value.push({
            key: 'merged-result',
            fileName: f"{outputFileName.value}.xlsx",
            status: '成功',
            result: result.output
          })
        }
      } else {
        processingResults.value.push({
          key: 'merged-result',
          fileName: f"{outputFileName.value}.xlsx",
          status: '失败',
          result: result.error
        })
      }
    
    loadingProgress.value = 100
    progressText.value = '处理完成'
    successMessage.value = '文件合并完成'
    
    notification.success({
      message: '处理完成',
      description: `成功合并 ${files.value.length} 个文件`,
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