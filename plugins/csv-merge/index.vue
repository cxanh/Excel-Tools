<template>
  <PluginLayout
    title="CSV合并"
    :can-proceed="canProceed"
    :processing="processing"
    @step-change="handleStepChange"
    @next="handleNext"
    @add-files="handleAddFiles"
    @import-from-folder="handleImportFromFolder"
    @clear-all="handleClearAll"
    ref="layoutRef"
  >
    <template #default="{ currentStep }">
      <!-- 步骤 0: 选择待处理文件 -->
      <div v-if="currentStep === 0" class="step-content">
        <a-alert
          message="功能说明"
          description="合并多个CSV文件为一个文件，支持自动去重和列对齐。"
          type="info"
          show-icon
          style="margin-bottom: 24px"
        />

        <div class="upload-area">
          <FileUpload :multiple="true" @change="handleFileChange" ref="fileUploadRef" />
        </div>

        <div v-if="files.length > 0" class="file-list">
          <a-table :columns="fileColumns" :data-source="files" :pagination="false" bordered>
            <template #bodyCell="{ column, record, index }">
              <template v-if="column.key === 'index'">{{ index + 1 }}</template>
              <template v-else-if="column.key === 'name'">
                <FileExcelOutlined style="color: #52c41a; margin-right: 8px" />
                {{ record.name }}
              </template>
              <template v-else-if="column.key === 'size'">{{ formatFileSize(record.size) }}</template>
              <template v-else-if="column.key === 'type'">{{ record.type || 'CSV' }}</template>
              <template v-else-if="column.key === 'createTime'">{{ formatDate(record.lastModified) }}</template>
              <template v-else-if="column.key === 'modifyTime'">{{ formatDate(record.lastModified) }}</template>
              <template v-else-if="column.key === 'actions'">
                <a-button type="link" size="small" danger @click="removeFile(index)">移除</a-button>
              </template>
            </template>
          </a-table>
        </div>

        <div v-else class="empty-state">
          <a-empty description="请拖放文件到此处或点击上方添加文件按钮" />
        </div>
      </div>

      <!-- 步骤 1: 配置合并选项 -->
      <div v-if="currentStep === 1" class="step-content">
        <a-card title="合并选项" :bordered="false">
          <a-form layout="vertical">
            <a-form-item>
              <a-checkbox v-model:checked="removeDuplicates">自动去除重复行</a-checkbox>
            </a-form-item>
            <a-form-item>
              <a-checkbox v-model:checked="alignColumns">自动对齐列</a-checkbox>
            </a-form-item>
            <a-form-item>
              <a-checkbox v-model:checked="includeHeader">包含表头</a-checkbox>
            </a-form-item>
          </a-form>
        </a-card>
      </div>

      <!-- 步骤 2: 开始处理 -->
      <div v-if="currentStep === 2" class="step-content">
        <a-result
          :status="processing ? 'info' : results.length > 0 ? 'success' : 'info'"
          :title="processing ? '正在处理...' : results.length > 0 ? '处理完成！' : '准备开始处理'"
          :sub-title="processing ? '正在合并文件...' : results.length > 0 ? '合并成功' : '点击下方开始处理按钮'"
        >
          <template #icon>
            <LoadingOutlined v-if="processing" spin style="font-size: 48px; color: #6366f1" />
            <CheckCircleOutlined v-else-if="results.length > 0" style="font-size: 48px; color: #52c41a" />
            <FileExcelOutlined v-else style="font-size: 48px; color: #6366f1" />
          </template>
          <template #extra>
            <a-button 
              v-if="!processing && results.length === 0" 
              type="primary" 
              size="large"
              @click="startProcessing"
            >
              开始处理
            </a-button>
            <a-button 
              v-if="results.length > 0 && results[0].success" 
              type="primary" 
              @click="downloadFile(0)"
            >
              下载合并文件
            </a-button>
          </template>
        </a-result>
      </div>
    </template>
  </PluginLayout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import { 
  LoadingOutlined, 
  CheckCircleOutlined, 
  FileExcelOutlined 
} from '@ant-design/icons-vue'
import PluginLayout from '@/components/PluginLayout.vue'
import FileUpload from '@/components/FileUpload.vue'
import { runPythonScript } from '@/utils/py'
import { downloadProcessedFile, formatFileSize } from '@/utils/file-service'

const layoutRef = ref()
const fileUploadRef = ref()
const files = ref<File[]>([])
const results = ref<any[]>([])
const processing = ref(false)
const removeDuplicates = ref(false)
const alignColumns = ref(true)
const includeHeader = ref(true)

const fileColumns = [
  { title: '序号', key: 'index', width: 80 },
  { title: '文件名', key: 'name' },
  { title: '大小', key: 'size', width: 120 },
  { title: '类型', key: 'type', width: 100 },
  { title: '创建时间', key: 'createTime', width: 180 },
  { title: '修改时间', key: 'modifyTime', width: 180 },
  { title: '操作', key: 'actions', width: 100 }
]

const canProceed = computed(() => {
  const step = layoutRef.value?.currentStep || 0
  if (step === 0) return files.value.length >= 2
  return true
})

const successCount = computed(() => {
  return results.value.filter(r => r.success).length
})

const handleFileChange = (newFiles: File[]) => {
  files.value = newFiles
}

const handleAddFiles = () => {
  if (fileUploadRef.value) {
    fileUploadRef.value.openFileDialog()
  }
}

const handleImportFromFolder = (newFiles: File[]) => {
  files.value = [...files.value, ...newFiles]
}

const handleClearAll = () => {
  files.value = []
  results.value = []
  if (fileUploadRef.value) {
    fileUploadRef.value.clear()
  }
}

const removeFile = (index: number) => {
  files.value.splice(index, 1)
}

const formatDate = (timestamp: number) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

const handleStepChange = (step: number) => {
  // 步骤变化时的处理
}

const handleNext = () => {
  // 下一步按钮处理
}

const startProcessing = async () => {
  processing.value = true
  results.value = []

  try {
    const filesData = []
    for (const file of files.value) {
      const fileData = await readFileAsBase64(file)
      filesData.push({
        name: file.name,
        data: fileData.split(',')[1]
      })
    }

    const params = {
      files: filesData,
      removeDuplicates: removeDuplicates.value,
      alignColumns: alignColumns.value,
      includeHeader: includeHeader.value
    }

    const result = await runPythonScript('csv-merge', params)
    results.value.push(result)

    if (result.success) {
      message.success('合并完成！')
    } else {
      message.error('合并失败')
    }
  } catch (error: any) {
    message.error('处理过程中出现错误: ' + error.message)
    results.value.push({
      success: false,
      error: error.message || '处理失败'
    })
  } finally {
    processing.value = false
  }
}

const readFileAsBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

const downloadFile = (index: number) => {
  const result = results.value[index]
  
  if (result.success && result.data) {
    downloadProcessedFile(result.data, 'merged.csv')
  }
}
</script>

<style scoped>
.step-content {
  padding: 24px;
}

.upload-area {
  margin-bottom: 24px;
}

.file-list {
  margin-top: 24px;
}

.empty-state {
  padding: 48px 0;
  text-align: center;
}
</style>
