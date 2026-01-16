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
      <PictureOutlined :style="{ fontSize: '48px', color: '#165DFF' }" />
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
        <a-form-item label="水印类型">
          <a-radio-group v-model:value="watermarkType">
            <a-radio value="text">文本水印</a-radio>
            <a-radio value="image">图片水印</a-radio>
          </a-radio-group>
        </a-form-item>

        <template v-if="watermarkType === 'text'">
          <a-form-item label="水印文字" required>
            <a-input
              v-model:value="watermarkText"
              placeholder="请输入水印文字"
              :maxlength="50"
            />
          </a-form-item>

          <a-form-item label="字体大小">
            <a-slider
              v-model:value="fontSize"
              :min="12"
              :max="120"
              :marks="{ 12: '12', 48: '48', 120: '120' }"
            />
            <span style="margin-left: 12px">{{ fontSize }}px</span>
          </a-form-item>

          <a-form-item label="文字颜色">
            <input
              type="color"
              v-model="textColor"
              style="width: 60px; height: 32px; border: 1px solid #d9d9d9; border-radius: 4px; cursor: pointer"
            />
            <span style="margin-left: 12px">{{ textColor }}</span>
          </a-form-item>
        </template>

        <template v-if="watermarkType === 'image'">
          <a-form-item label="水印图片" required>
            <input
              type="file"
              accept="image/*"
              @change="handleWatermarkImageSelect"
              style="display: block"
            />
            <div v-if="watermarkImagePreview" style="margin-top: 12px">
              <img
                :src="watermarkImagePreview"
                alt="水印预览"
                style="max-width: 200px; max-height: 200px; border: 1px solid #d9d9d9; border-radius: 4px"
              />
            </div>
          </a-form-item>
        </template>

        <a-form-item label="透明度">
          <a-slider
            v-model:value="opacity"
            :min="0"
            :max="100"
            :marks="{ 0: '0%', 50: '50%', 100: '100%' }"
          />
          <span style="margin-left: 12px">{{ opacity }}%</span>
        </a-form-item>

        <a-form-item label="水印位置">
          <a-select v-model:value="position" style="width: 200px">
            <a-select-option value="center">居中</a-select-option>
            <a-select-option value="top-left">左上角</a-select-option>
            <a-select-option value="top-right">右上角</a-select-option>
            <a-select-option value="bottom-left">左下角</a-select-option>
            <a-select-option value="bottom-right">右下角</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </template>

    <template #step3>
      <a-descriptions bordered :column="1">
        <a-descriptions-item label="待处理文件">
          {{ files.length }} 个
        </a-descriptions-item>
        <a-descriptions-item label="水印类型">
          {{ watermarkType === 'text' ? '文本水印' : '图片水印' }}
        </a-descriptions-item>
        <a-descriptions-item v-if="watermarkType === 'text'" label="水印文字">
          {{ watermarkText }}
        </a-descriptions-item>
        <a-descriptions-item v-if="watermarkType === 'text'" label="字体大小">
          {{ fontSize }}px
        </a-descriptions-item>
        <a-descriptions-item v-if="watermarkType === 'text'" label="文字颜色">
          <span :style="{ color: textColor }">{{ textColor }}</span>
        </a-descriptions-item>
        <a-descriptions-item label="透明度">
          {{ opacity }}%
        </a-descriptions-item>
        <a-descriptions-item label="水印位置">
          {{ getPositionLabel(position) }}
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
import { PictureOutlined } from '@ant-design/icons-vue'
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
const watermarkType = ref<'text' | 'image'>('text')
const watermarkText = ref('WATERMARK')
const fontSize = ref(48)
const textColor = ref('#000000')
const watermarkImagePreview = ref('')
const watermarkImageData = ref('')
const opacity = ref(50)
const position = ref('center')

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

const handleWatermarkImageSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      watermarkImageData.value = e.target?.result as string
      watermarkImagePreview.value = watermarkImageData.value
    }
    reader.readAsDataURL(file)
  }
}

const getPositionLabel = (pos: string) => {
  const labels: Record<string, string> = {
    'center': '居中',
    'top-left': '左上角',
    'top-right': '右上角',
    'bottom-left': '左下角',
    'bottom-right': '右下角'
  }
  return labels[pos] || pos
}

const validateConfig = () => {
  if (watermarkType.value === 'text' && !watermarkText.value.trim()) {
    throw new Error('请输入水印文字')
  }
  if (watermarkType.value === 'image' && !watermarkImageData.value) {
    throw new Error('请选择水印图片')
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
          watermark_type: watermarkType.value,
          watermark_text: watermarkText.value,
          watermark_image: watermarkImageData.value,
          font_size: fontSize.value,
          color: textColor.value,
          opacity: opacity.value,
          position: position.value
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
    const newName = `${baseName}_图片水印.${ext}`
    
    downloadFile(result.buffer, newName)
  }
}

const handleReset = () => {
  currentStep.value = 1
  processing.value = false
  files.value = []
  results.value = []
  currentFileIndex.value = 0
  watermarkType.value = 'text'
  watermarkText.value = 'WATERMARK'
  fontSize.value = 48
  textColor.value = '#000000'
  watermarkImagePreview.value = ''
  watermarkImageData.value = ''
  opacity.value = 50
  position.value = 'center'
}
</script>

<style scoped>
.ant-descriptions {
  background: #fff;
}
</style>
