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
      <BgColorsOutlined :style="{ fontSize: '48px', color: '#165DFF' }" />
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
            <a-radio value="remove">删除背景图片</a-radio>
            <a-radio value="replace">替换背景图片</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item v-if="mode === 'replace'" label="新背景图片" required>
          <input
            type="file"
            accept="image/*"
            @change="handleBackgroundImageSelect"
            style="display: block"
          />
          <div v-if="backgroundImagePreview" style="margin-top: 12px">
            <img
              :src="backgroundImagePreview"
              alt="背景预览"
              style="max-width: 300px; max-height: 200px; border: 1px solid #d9d9d9; border-radius: 4px"
            />
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
          {{ mode === 'remove' ? '删除背景图片' : '替换背景图片' }}
        </a-descriptions-item>
        <a-descriptions-item v-if="mode === 'replace'" label="新背景图片">
          已选择
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
import { BgColorsOutlined } from '@ant-design/icons-vue'
import PluginLayout from '@/components/PluginLayout.vue'
import FileUpload from '@/components/FileUpload.vue'
import { runPy } from '@/utils/py'
import { downloadFile } from '@/utils/file-service'
import manifest from './manifest.json'
import workerScript from './worker.py?raw'

// 状态管理
const currentStep = ref(1)
const processing = ref(false)
const files = ref<File[]>([])
const results = ref<any[]>([])
const currentFileIndex = ref(0)

// 配置参数
const mode = ref<'remove' | 'replace'>('remove')
const backgroundImagePreview = ref('')
const backgroundImageData = ref('')

// 计算属性
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

// 事件处理
const handleFilesSelected = (selectedFiles: File[]) => {
  files.value = selectedFiles
  currentStep.value = 2
}

const handleBackgroundImageSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      backgroundImageData.value = e.target?.result as string
      backgroundImagePreview.value = backgroundImageData.value
    }
    reader.readAsDataURL(file)
  }
}

const validateConfig = () => {
  if (mode.value === 'replace' && !backgroundImageData.value) {
    throw new Error('请选择新背景图片')
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
          background_image: backgroundImageData.value
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
    const suffix = mode.value === 'remove' ? '已删除背景' : '已替换背景'
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
  mode.value = 'remove'
  backgroundImagePreview.value = ''
  backgroundImageData.value = ''
}
</script>

<style scoped>
.ant-descriptions {
  background: #fff;
}
</style>
