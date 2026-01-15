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
        <p>请选择要删除重复行的 Excel 文件</p>
      </a-card>
      
      <!-- 步骤2：设置规则 -->
      <a-card v-if="currentStep === 1" title="步骤2：设置规则" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="重复行定义">
            <a-radio-group v-model:value="duplicateDefinition">
              <a-radio value="all-columns">所有列相同</a-radio>
              <a-radio value="key-columns">关键列相同</a-radio>
            </a-radio-group>
          </a-form-item>
          <a-form-item v-if="duplicateDefinition === 'key-columns'" label="关键列（用逗号分隔）">
            <a-input
              v-model:value="keyColumns"
              placeholder="例如：A,B,C 或 1,2,3"
            />
          </a-form-item>
          <a-form-item label="处理选项">
            <a-checkbox v-model:checked="keepFirstOccurrence">保留首次出现的行</a-checkbox>
            <a-checkbox v-model:checked="keepLastOccurrence">保留最后出现的行</a-checkbox>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤3：其他选项 -->
      <a-card v-if="currentStep === 2" title="步骤3：其他选项" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="处理选项">
            <a-checkbox v-model:checked="backupOriginal">备份原始文件</a-checkbox>
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
          <li>设置重复行定义（所有列相同或关键列相同）</li>
          <li>设置处理选项（保留首次/最后出现的行）</li>
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
const pluginTitle = ref('删除 Excel 重复行')
const pluginDescription = ref('删除 Excel 文件中的重复行，确保数据唯一性')

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
const duplicateDefinition = ref('all-columns')
const keyColumns = ref('')
const keepFirstOccurrence = ref(true)
const keepLastOccurrence = ref(false)
const backupOriginal = ref(true)

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
  if (currentStep.value === 0 && files.value.length === 0) {
    message.error('请先选择要处理的文件')
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
    message.error('请先选择要处理的文件')
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
dup_def = ${JSON.stringify(duplicateDefinition.value)}
key_cols = ${JSON.stringify(keyColumns.value)}
keep_first = ${JSON.stringify(keepFirstOccurrence.value)}
keep_last = ${JSON.stringify(keepLastOccurrence.value)}
backup_original = ${JSON.stringify(backupOriginal.value)}

# 加载工作簿
wb = load_workbook(file_data)

# 处理每个工作表
removed_duplicates_count = 0

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    # 获取所有行数据
    rows = list(ws.iter_rows(values_only=True))
    header = rows[0] if rows else []
    data_rows = rows[1:] if len(rows) > 1 else []
    
    # 计算要保留的行索引
    seen_rows = {}
    rows_to_keep = []
    
    for idx, row in enumerate(data_rows):
        # 生成行的唯一键
        if dup_def == 'all-columns':
            # 使用所有列作为键
            row_key = tuple(row)
        elif dup_def == 'key-columns' and key_cols:
            # 使用关键列作为键
            cols = key_cols.split(',')
            key_values = []
            for col in cols:
                col = col.strip()
                if col.isalpha():
                    # 字母列名（A, B, C）
                    col_idx = ord(col.upper()) - ord('A')
                else:
                    # 数字列名（1, 2, 3）
                    col_idx = int(col) - 1
                
                if 0 <= col_idx < len(row):
                    key_values.append(row[col_idx])
            row_key = tuple(key_values)
        else:
            row_key = tuple(row)
        
        if row_key not in seen_rows:
            # 第一次出现，保留
            seen_rows[row_key] = idx
            rows_to_keep.append(idx)
        else:
            # 重复行
            if keep_last:
                # 保留最后一次出现，移除之前的
                if seen_rows[row_key] in rows_to_keep:
                    rows_to_keep.remove(seen_rows[row_key])
                seen_rows[row_key] = idx
                rows_to_keep.append(idx)
            elif keep_first:
                # 保留第一次出现，跳过当前行
                pass
            removed_duplicates_count += 1
    
    # 从下往上删除重复行
    rows_to_delete = sorted([i for i in range(len(data_rows)) if i not in rows_to_keep], reverse=True)
    for idx in rows_to_delete:
        ws.delete_rows(idx + 2)  # +2 因为表头占1行，索引从1开始

# 保存文件
save_path = os.path.join(output_path, file_name)
wb.save(save_path)

# 返回结果
result = {
    'status': 'success',
    'message': f'成功删除 {removed_duplicates_count} 行重复数据',
    'file_name': file_name
}

print(str(result))
`
      
      pyodideLoading.value = false
      loadingProgress.value = 30 + Math.round((i / files.value.length) * 70)
      progressText.value = `正在处理文件: ${file.name}`
      
      // 执行Python脚本
      const result = await runPyScript(scriptContent)
      
      if (result.success) {
        try {
          const resultData = JSON.parse(result.output)
          processingResults.value.push({
            key: file.key,
            fileName: file.name,
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