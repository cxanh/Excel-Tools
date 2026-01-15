<template>
  <PluginTemplate
    plugin-title="Excel 转换为其它格式"
    info-message="将Excel文件转换为CSV、JSON、HTML等其他格式"
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
        message="格式转换说明"
        description="支持将Excel文件转换为CSV、JSON和HTML格式。转换时仅处理单个工作表。"
        type="info"
        show-icon
        class="mb-4"
      />
      
      <div class="settings-section">
        <h3 class="section-title">转换设置</h3>
        
        <a-form-item label="目标格式">
          <a-select v-model:value="targetFormat" placeholder="请选择目标格式">
            <a-select-option value="csv">CSV</a-select-option>
            <a-select-option value="json">JSON</a-select-option>
            <a-select-option value="html">HTML</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item label="工作表选择">
          <a-select v-model:value="sheetName" placeholder="自动选择活动工作表">
            <a-select-option v-for="sheet in availableSheets" :key="sheet" :value="sheet">
              {{ sheet }}
            </a-select-option>
          </a-select>
        </a-form-item>
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
const targetFormat = ref('csv')
const sheetName = ref('')
const availableSheets = ref([])

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

// 加载工作表名称
const loadSheetNames = async (file) => {
  try {
    const script = await getPythonScript('convert-format')
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
  
  const script = await getPythonScript('convert-format')
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
          targetFormat: targetFormat.value,
          sheetName: sheetName.value
        }
      })
      
      if (result.success) {
        // 根据目标格式设置文件名和MIME类型
        let newFileName = file.name.replace(/\.[^/.]+$/, '')
        let mimeType = 'application/octet-stream'
        
        if (targetFormat.value === 'csv') {
          newFileName += '.csv'
          mimeType = 'text/csv'
        } else if (targetFormat.value === 'json') {
          newFileName += '.json'
          mimeType = 'application/json'
        } else if (targetFormat.value === 'html') {
          newFileName += '.html'
          mimeType = 'text/html'
        }
        
        pluginTemplate.value.handleFileProcessed(
          { ...file, name: newFileName, mimeType }, 
          result
        )
      } else {
        pluginTemplate.value.handleFileError(file, result.error || '转换失败')
      }
    } catch (error) {
      pluginTemplate.value.handleFileError(file, error.message || '转换失败')
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