<template>
  <PluginTemplate
    plugin-title="Excel 拆分成多个文件"
    info-message="将一个Excel文件根据指定条件拆分成多个Excel文件"
    :current-step="currentStep"
    @add-file="handleAddFile"
    @import-folder="handleImportFromFolder"
    @more-action="handleMoreAction"
    @next-step="handleNextStep"
    @prev-step="handlePrevStep"
    @remove-file="handleRemoveFile"
    ref="pluginTemplate"
  >
    <!-- 插件内容 -->
    <div class="plugin-content">
      <a-alert
        message="拆分说明"
        description="支持三种拆分模式：按行数拆分、按列值拆分、按工作表拆分。按工作表拆分将为每个工作表生成一个新文件。"
        type="info"
        show-icon
        class="mb-4"
      />
      
      <div class="settings-section">
        <h3 class="section-title">拆分设置</h3>
        
        <a-form-item label="拆分模式">
          <a-select v-model:value="splitMode" placeholder="请选择拆分模式">
            <a-select-option value="by_row">按行数拆分</a-select-option>
            <a-select-option value="by_column">按列值拆分</a-select-option>
            <a-select-option value="by_sheet">按工作表拆分</a-select-option>
          </a-select>
        </a-form-item>
        
        <!-- 工作表选择（仅在按行数或列值拆分时显示） -->
        <a-form-item v-if="splitMode !== 'by_sheet'" label="工作表">
          <a-select v-model:value="sheetName" placeholder="自动选择活动工作表">
            <a-select-option v-for="sheet in availableSheets" :key="sheet" :value="sheet">
              {{ sheet }}
            </a-select-option>
          </a-select>
        </a-form-item>
        
        <!-- 按行数拆分选项 -->
        <template v-if="splitMode === 'by_row'">
          <a-form-item label="每文件行数">
            <a-input-number
              v-model:value="splitOptions.rowsPerFile"
              :min="1"
              :max="100000"
              placeholder="请输入每文件行数"
            />
          </a-form-item>
          <a-alert
            message="注意"
            description="建议每文件行数不超过10000行，以保证处理速度和稳定性。"
            type="warning"
            show-icon
            class="mt-2 mb-2"
          />
        </template>
        
        <!-- 按列值拆分选项 -->
        <template v-else-if="splitMode === 'by_column'">
          <a-form-item label="拆分列">
            <a-radio-group v-model:value="columnSelectionMode" class="mr-4">
              <a-radio value="by_index">按列索引</a-radio>
              <a-radio value="by_name">按列名</a-radio>
            </a-radio-group>
          </a-form-item>
          
          <a-form-item v-if="columnSelectionMode === 'by_index'" label="列索引">
            <a-input-number
              v-model:value="splitOptions.columnIndex"
              :min="1"
              :max="1000"
              placeholder="请输入列索引"
            />
          </a-form-item>
          
          <a-form-item v-else label="列名">
            <a-input
              v-model:value="splitOptions.columnName"
              placeholder="请输入列名"
            />
          </a-form-item>
          
          <a-alert
            message="提示"
            description="拆分将基于所选列的唯一值进行，每个唯一值生成一个新文件。"
            type="info"
            show-icon
            class="mt-2 mb-2"
          />
        </template>
      </div>
    </div>
  </PluginTemplate>
</template>

<script setup>
import { ref, watch } from 'vue'
import PluginTemplate from '@/components/PluginTemplate.vue'
import { runPy } from '@/utils/py'
import { getPythonScript } from '@/utils/plugin'

const currentStep = ref(1)
const pluginTemplate = ref(null)
const splitMode = ref('by_row')
const sheetName = ref('')
const availableSheets = ref([])
const columnSelectionMode = ref('by_index')
const splitOptions = ref({
  rowsPerFile: 1000,
  columnIndex: 1,
  columnName: ''
})

// 监听文件变化，获取可用工作表
watch(
  () => pluginTemplate.value?.files,
  async (newFiles) => {
    if (newFiles && newFiles.length > 0) {
      // 获取第一个文件的工作表信息
      await loadSheetNames(newFiles[0])
    }
  },
  { deep: true }
)

// 监听拆分模式变化，重置相关设置
watch(
  splitMode,
  (newMode) => {
    if (newMode === 'by_row') {
      splitOptions.value.rowsPerFile = 1000
    } else if (newMode === 'by_column') {
      splitOptions.value.columnIndex = 1
      splitOptions.value.columnName = ''
      columnSelectionMode.value = 'by_index'
    }
  }
)

// 加载工作表名称
const loadSheetNames = async (file) => {
  try {
    const script = await getPythonScript('split-excel')
    if (!script) return
    
    // 创建一个临时脚本，仅用于获取工作表名称
    const getSheetsScript = `
import io
import openpyxl

def process(data):
    file_content = data['file']
    wb = openpyxl.load_workbook(io.BytesIO(file_content), read_only=True)
    return {
        'success': True,
        'sheetNames': wb.sheetnames,
        'activeSheet': wb.active.title
    }
    `
    
    const result = await runPy(getSheetsScript, {
      type: 'single',
      file: file.file,
      fileName: file.name,
      settings: {}
    })
    
    if (result.success) {
      availableSheets.value = result.sheetNames || []
      sheetName.value = result.activeSheet || ''
    }
  } catch (error) {
    console.error('获取工作表名称失败:', error)
    availableSheets.value = []
  }
}

// 处理文件
const processFiles = async () => {
  const files = pluginTemplate.value.files
  if (files.length === 0) {
    return
  }
  
  const script = await getPythonScript('split-excel')
  if (!script) {
    return
  }
  
  for (const file of files) {
    try {
      const result = await runPy(script, {
        type: 'single',
        file: file.file,
        fileName: file.name,
        settings: {
          splitMode: splitMode.value,
          sheetName: sheetName.value,
          splitOptions: splitOptions.value
        }
      })
      
      if (result.success) {
        // 处理拆分结果
        if (result.results && result.results.length > 0) {
          // 对于每个拆分结果，调用处理完成回调
          for (const splitResult of result.results) {
            pluginTemplate.value.handleFileProcessed(
              {
                ...file,
                name: splitResult.file_name,
                mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
              },
              {
                ...result,
                buffer: splitResult.buffer
              }
            )
          }
        } else {
          pluginTemplate.value.handleFileProcessed(file, result)
        }
      } else {
        pluginTemplate.value.handleFileError(file, result.error || '拆分失败')
      }
    } catch (error) {
      pluginTemplate.value.handleFileError(file, error.message || '拆分失败')
    }
  }
}

// 下一步处理
const handleNextStep = async () => {
  if (currentStep.value === 1) {
    await processFiles()
  }
  currentStep.value++
}

// 其他方法
const handleAddFile = (files) => {
  pluginTemplate.value.addFiles(files)
}

const handleImportFromFolder = () => {
  pluginTemplate.value.importFromFolder()
}

const handleMoreAction = () => {
  pluginTemplate.value.showMoreActions()
}

const handlePrevStep = () => {
  currentStep.value--
}

const handleRemoveFile = (index) => {
  pluginTemplate.value.removeFile(index)
}
</script>

<style scoped>
.plugin-content {
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.settings-section {
  margin-top: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #333;
}
</style>