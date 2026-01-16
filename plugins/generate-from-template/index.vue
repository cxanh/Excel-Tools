<template>
  <PluginLayout
    title="从模板生成"
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
          description="基于Excel模板和数据源批量生成标准化文档。模板中使用 {{变量名}} 作为占位符，系统将自动替换为数据源中的对应值。"
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
              <template v-else-if="column.key === 'type'">{{ record.type || 'Excel' }}</template>
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

      <!-- 步骤 1: 上传数据源 -->
      <div v-if="currentStep === 1" class="step-content">
        <a-card title="上传数据源" :bordered="false">
          <a-alert
            message="数据源格式"
            description="支持Excel或CSV格式，第一行为表头，包含模板中使用的变量名。"
            type="info"
            show-icon
            style="margin-bottom: 16px"
          />
          <a-upload
            :before-upload="handleDataUpload"
            :show-upload-list="false"
            accept=".xlsx,.xls,.csv"
          >
            <a-button type="primary">
              <UploadOutlined />
              选择数据源文件
            </a-button>
          </a-upload>
          <div v-if="dataSourceFile" style="margin-top: 16px">
            <a-tag color="green">{{ dataSourceFile.name }}</a-tag>
            <a-button type="link" size="small" danger @click="removeDataSourceFile">移除</a-button>
          </div>
        </a-card>
      </div>

      <!-- 步骤 2: 开始处理 -->
      <div v-if="currentStep === 2" class="step-content">
        <a-result
          :status="processing ? 'info' : result ? 'success' : 'info'"
          :title="processing ? '正在处理...' : result ? '处理完成！' : '准备开始处理'"
          :sub-title="processing ? `正在生成文档，请稍候...` : result ? `成功生成 ${result.files.length} 个文档` : '点击下方开始处理按钮'"
        >
          <template #icon>
            <LoadingOutlined v-if="processing" spin style="font-size: 48px; color: #6366f1" />
            <CheckCircleOutlined v-else-if="result" style="font-size: 48px; color: #52c41a" />
            <FileExcelOutlined v-else style="font-size: 48px; color: #6366f1" />
          </template>
          <template #extra>
            <a-progress v-if="processing" :percent="progress" :stroke-color="{ '0%': '#6366f1', '100%': '#8b5cf6' }" style="max-width: 500px; margin: 0 auto" />
            <a-space v-if="result && result.success" style="margin-top: 16px">
              <a-button type="primary" @click="handleDownload(result)">
                <DownloadOutlined />下载压缩包
              </a-button>
            </a-space>
          </template>
        </a-result>

        <div v-if="result && result.success" class="results-list">
          <a-list :data-source="result.files" :grid="{ gutter: 16, column: 1 }">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-card size="small">
                  <template #title>
                    <a-space>
                      <CheckCircleOutlined style="color: #52c41a" />
                      <span>{{ item.fileName }}</span>
                    </a-space>
                  </template>
                  <template #extra>
                    <a-tag color="blue">{{ item.fileSize }}</a-tag>
                  </template>
                  <div>
                    <div>生成时间: {{ item.createdAt }}</div>
                    <div>状态: 成功</div>
                  </div>
                </a-card>
              </a-list-item>
            </template>
          </a-list>
        </div>
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
  FileExcelOutlined,
  UploadOutlined,
  DownloadOutlined
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
const currentFileIndex = ref(0)
const dataSourceFile = ref<File | null>(null)
const dataSourceData = ref('')
const result = ref<any>(null)
const progress = ref(0)

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
  if (step === 0) return files.value.length > 0
  if (step === 1) return dataSourceFile.value !== null
  return true
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
  dataSourceFile.value = null
  dataSourceData.value = ''
  result.value = null
  if (fileUploadRef.value) {
    fileUploadRef.value.clear()
  }
}

const removeFile = (index: number) => {
  files.value.splice(index, 1)
}

const handleDataUpload = async (file: File) => {
  dataSourceFile.value = file
  const reader = new FileReader()
  reader.onload = () => {
    dataSourceData.value = reader.result as string
  }
  reader.readAsDataURL(file)
  message.success('数据源文件已上传')
  return false
}

const removeDataSourceFile = () => {
  dataSourceFile.value = null
  dataSourceData.value = ''
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
  progress.value = 0

  try {
    const templateFile = files.value[0]
    
    if (!templateFile) {
      message.error('请选择模板文件')
      return
    }

    const fileData = await readFileAsBase64(templateFile)

    const params = {
      templateData: fileData.split(',')[1],
      dataSource: dataSourceData.value.split(',')[1]
    }

    const processingResult = await runPythonScript('generate-from-template', params)
    result.value = processingResult

    message.success(`处理完成！成功生成 ${processingResult.files.length} 个文档`)
  } catch (error: any) {
    message.error('处理过程中出现错误: ' + error.message)
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

const handleDownload = (result: any) => {
  if (result.success && result.data) {
    downloadProcessedFile(result.data, 'generated_documents.zip')
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

.results-list {
  margin-top: 24px;
}
</style>