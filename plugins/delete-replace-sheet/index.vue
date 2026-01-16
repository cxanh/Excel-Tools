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
        <a-form-item label="操作模式">
          <a-radio-group v-model:value="mode">
            <a-radio value="delete">删除工作表</a-radio>
            <a-radio value="replace">替换工作表</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item label="选择工作表" required>
          <a-select
            v-model:value="selectedSheets"
            mode="multiple"
            placeholder="请选择要操作的工作表"
            style="width: 100%"
            :options="sheetOptions"
          />
          <div style="margin-top: 8px; color: #999; font-size: 12px">
            可以选择多个工作表进行批量操作
          </div>
        </a-form-item>

        <a-form-item v-if="mode === 'replace'" label="替换文件" required>
          <input
            type="file"
            accept=".xlsx,.xls"
            @change="handleReplaceFileSelect"
            style="display: block"
          />
          <div v-if="replaceFileName" style="margin-top: 8px; color: #52c41a">
            已选择: {{ replaceFileName }}
          </div>
        </a-form-item>
      </a-form>
    </template>

    <template #step3>
      <a-descriptions bordered :column="1">
        <a-descriptions-item label="待处理文件">
          {{ files.length }} 个
        </a-descriptions-item>
        <a-descriptions-item label="操作模式">
          {{ mode === 'delete' ? '删除工作表' : '替换工作表' }}
        </a-descriptions-item>
        <a-descriptions-item label="选中工作表">
          {{ selectedSheets.length }} 个
        </a-descriptions-item>
        <a-descriptions-item v-if="mode === 'replace'" label="替换文件">
          {{ replaceFileName }}
        </a-descriptions-item>
      </a-descriptions>
    </template>

    <template #step5>
      <a-list
        :data-source="results"
        :split="true"
      >
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
              <a-button
                v-if="item.success"
                type="link"
                @click="handleDownload(item)"
              >
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

const mode = ref<'delete' | 'replace'>('delete')
const selectedSheets = ref<string[]>([])
const sheetOptions = ref<any[]>([])
const replaceFileName = ref('')
const replaceFileData = ref('')

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

const handleFilesSelected = async (selectedFiles: File[]) => {
  files.value = selectedFiles
  
  if (selectedFiles.length > 0) {
    await loadSheetNames(selectedFiles[0])
  }
  
  currentStep.value = 2
}

const loadSheetNames = async (file: File) => {
  try {
    // 使用 Pyodide 读取 Sheet 名称
    const arrayBuffer = await file.arrayBuffer()
    const uint8Array = new Uint8Array(arrayBuffer)
    
    // 简单的 Python 脚本来获取 sheet 名称
    const script = `
import openpyxl
from io import BytesIO

def get_sheet_names(file_data):
    wb = openpyxl.load_workbook(BytesIO(bytes(file_data)), read_only=True)
    return wb.sheetnames

get_sheet_names(file_data)
`
    
    const result = await runPy(script, 'get_sheet_names', uint8Array, '{}')
    const sheets = result as string[]
    
    sheetOptions.value = sheets.map((name: string) => ({
      label: name,
      value: name
    }))
  } catch (error) {
    // 如果读取失败，提供默认选项
    sheetOptions.value = [
      { label: 'Sheet1', value: 'Sheet1' },
      { label: 'Sheet2', value: 'Sheet2' },
      { label: 'Sheet3', value: 'Sheet3' }
    ]
  }
}

const handleReplaceFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    replaceFileName.value = file.name
    const reader = new FileReader()
    reader.onload = (e) => {
      replaceFileData.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const validateConfig = () => {
  if (selectedSheets.value.length === 0) {
    throw new Error('请选择要操作的工作表')
  }
  if (mode.value === 'replace' && !replaceFileData.value) {
    throw new Error('请选择替换文件')
  }
}

const handleStartProcess = async () => {
  try {
    validateConfig()
    
    processing.value = true
    results.value = []
    currentStep.value = 4
    
    for (let i = 0; i < files.value.length; i++) {
      currentFileIndex.value = i
      const file = files.value[i]
      
      try {
        const arrayBuffer = await file.arrayBuffer()
        const uint8Array = new Uint8Array(arrayBuffer)
        
        const params = {
          mode: mode.value,
          sheet_names: selectedSheets.value,
          replace_file: replaceFileData.value
        }
        
        const result = await runPy(workerScript, 'process', uint8Array, JSON.stringify(params))
        
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
  } catch (error: any) {
    alert(error.message)
    processing.value = false
  }
}

const handleDownload = (result: any) => {
  if (result.buffer) {
    const originalName = result.fileName
    const nameParts = originalName.split('.')
    const ext = nameParts.pop()
    const baseName = nameParts.join('.')
    const suffix = mode.value === 'delete' ? '已删除工作表' : '已替换工作表'
    const newName = `${baseName}_${suffix}.${ext}`
    
    downloadFile(result.buffer, newName)
  }
}

const handleReset = () => {
  currentStep.value = 1
  processing.value = false
  files.value = []
  results.value = []
  currentFileIndex.value = 0
  mode.value = 'delete'
  selectedSheets.value = []
  sheetOptions.value = []
  replaceFileName.value = ''
  replaceFileData.value = ''
}
</script>

<style scoped>
.ant-descriptions {
  background: #fff;
}
</style>
