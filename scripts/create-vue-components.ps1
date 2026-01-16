# 批量创建Vue组件的脚本

$template = @'
<template>
  <PluginLayout
    :title="manifest.name"
    :description="manifest.description"
    :current-step="currentStep"
    :status="status"
    :status-title="statusTitle"
    :status-sub-title="statusSubTitle"
    :processing="processing"
    :results="results"
    :success-count="successCount"
    @start-process="handleStartProcess"
    @download="handleDownload"
    @reset="handleReset"
  >
    <template #icon>
      <FileExcelOutlined :style="{ fontSize: '48px', color: '#165DFF' }" />
    </template>

    <template #step1>
      <FileUpload
        accept=".xlsx,.xls"
        :max-size="100"
        @files-selected="handleFilesSelected"
      >
        <template #tip>
          支持 .xlsx 和 .xls 格式，单个文件最大 100MB
        </template>
      </FileUpload>
    </template>

    <template #step2>
      <a-form :label-col="{ span: 6 }" :wrapper-col="{ span: 18 }">
        <a-alert message="配置参数" type="info" show-icon style="margin-bottom: 16px" />
      </a-form>
    </template>

    <template #step3>
      <a-descriptions bordered :column="1">
        <a-descriptions-item label="待处理文件">
          {{ files.length }} 个
        </a-descriptions-item>
      </a-descriptions>
    </template>

    <template #step5>
      <a-list :data-source="results" :split="true">
        <template #renderItem="{ item }">
          <a-list-item>
            <a-list-item-meta>
              <template #title>
                <span :style="{ color: item.success ? '#52c41a' : '#ff4d4f' }">
                  {{ item.success ? '✓' : '✗' }} {{ item.fileName }}
                </span>
              </template>
              <template #description>
                <div style="white-space: pre-wrap; font-family: monospace; font-size: 12px">
                  {{ item.logs.join('\n') }}
                </div>
              </template>
            </a-list-item-meta>
            <template #actions>
              <a-button v-if="item.success" type="link" @click="handleDownload(item)">
                下载
              </a-button>
            </template>
          </a-list-item>
        </template>
      </a-list>
    </template>
  </PluginLayout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { FileExcelOutlined } from '@ant-design/icons-vue'
import PluginLayout from '@/components/PluginLayout.vue'
import FileUpload from '@/components/FileUpload.vue'
import { runPy } from '@/utils/py'
import { downloadFile } from '@/utils/file-service'
import manifest from './manifest.json'
import workerScript from './worker.py?raw'

const currentStep = ref(1)
const processing = ref(false)
const files = ref<File[]>([])
const results = ref<any[]>([])
const currentFileIndex = ref(0)

const successCount = computed(() => results.value.filter(r => r.success).length)

const status = computed(() => {
  if (processing.value) return 'info'
  if (results.value.length > 0) return 'success'
  return 'info'
})

const statusTitle = computed(() => {
  if (processing.value) return '正在处理...'
  if (results.value.length > 0) return '处理完成！'
  return '准备开始处理'
})

const statusSubTitle = computed(() => {
  if (processing.value) {
    return `正在处理第 ${currentFileIndex.value + 1} / ${files.value.length} 个文件`
  }
  if (results.value.length > 0) {
    return `成功: ${successCount.value} / ${results.value.length}`
  }
  return '点击下方开始处理按钮'
})

const handleFilesSelected = (selectedFiles: File[]) => {
  files.value = selectedFiles
  currentStep.value = 2
}

const handleStartProcess = async () => {
  processing.value = true
  results.value = []
  currentStep.value = 4
  
  for (let i = 0; i < files.value.length; i++) {
    currentFileIndex.value = i
    const file = files.value[i]
    
    try {
      const arrayBuffer = await file.arrayBuffer()
      const uint8Array = new Uint8Array(arrayBuffer)
      const result = await runPy(workerScript, 'process', uint8Array, '{}')
      
      results.value.push({
        fileName: file.name,
        success: true,
        buffer: result.buffer,
        logs: result.logs || []
      })
    } catch (error: any) {
      results.value.push({
        fileName: file.name,
        success: false,
        logs: [error.message || '处理失败']
      })
    }
  }
  
  processing.value = false
  currentStep.value = 5
}

const handleDownload = (result: any) => {
  if (result.buffer) {
    const originalName = result.fileName
    const nameParts = originalName.split('.')
    const ext = nameParts.pop()
    const baseName = nameParts.join('.')
    const newName = `${baseName}_processed.${ext}`
    downloadFile(result.buffer, newName)
  }
}

const handleReset = () => {
  currentStep.value = 1
  processing.value = false
  files.value = []
  results.value = []
  currentFileIndex.value = 0
}
</script>

<style scoped>
.ant-descriptions {
  background: #fff;
}
</style>
'@

$plugins = @('insert-sheet', 'csv-split', 'csv-merge', 'clear-metadata', 'modify-metadata', 'manage-protection', 'optimize-excel')

foreach ($plugin in $plugins) {
    $path = "plugins\$plugin\index.vue"
    if (!(Test-Path $path)) {
        $template | Out-File -FilePath $path -Encoding UTF8
        Write-Host "Created: $path"
    }
}
