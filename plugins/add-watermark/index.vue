<template>
  <PluginLayout
    title="添加水印"
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
          description="为Excel文件添加文本或图片水印，支持自定义样式、透明度和位置。"
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
              <template v-if="column.key === 'index'">
                {{ index + 1 }}
              </template>
              <template v-else-if="column.key === 'name'">
                {{ record.name }}
              </template>
              <template v-else-if="column.key === 'size'">
                {{ formatFileSize(record.size) }}
              </template>
              <template v-else-if="column.key === 'action'">
                <a-button type="link" danger size="small" @click="removeFile(index)">
                  删除
                </a-button>
              </template>
            </template>
          </a-table>
        </div>

        <div v-else class="empty-state">
          <a-empty description="请拖放文件到此处或点击上方添加文件按钮" />
        </div>
      </div>


      <!-- 步骤 1: 配置水印 -->
      <div v-if="currentStep === 1" class="step-content">
        <a-card title="水印配置" :bordered="false">
          
          <!-- 水印类型选择 -->
          <a-form-item label="水印类型">
            <a-radio-group v-model:value="watermarkType">
              <a-radio value="text">文本水印</a-radio>
              <a-radio value="image">图片水印</a-radio>
            </a-radio-group>
          </a-form-item>

          <!-- 文本水印配置 -->
          <div v-if="watermarkType === 'text'">
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
                :min="20" 
                :max="100" 
                :marks="{ 20: '20', 48: '48', 100: '100' }"
              />
              <span style="margin-left: 12px">{{ fontSize }}px</span>
            </a-form-item>

            <a-form-item label="文字颜色">
              <div style="display: flex; gap: 12px; align-items: center">
                <input 
                  type="color" 
                  v-model="textColor" 
                  style="width: 60px; height: 36px; border: 1px solid #d9d9d9; border-radius: 4px"
                />
                <span>{{ textColor }}</span>
              </div>
            </a-form-item>

            <a-form-item label="透明度">
              <a-slider 
                v-model:value="transparency" 
                :min="0" 
                :max="255" 
                :marks="{ 0: '透明', 128: '半透明', 255: '不透明' }"
              />
              <span style="margin-left: 12px">{{ transparency }}</span>
            </a-form-item>

            <a-form-item label="旋转角度">
              <a-slider 
                v-model:value="angle" 
                :min="-90" 
                :max="90" 
                :marks="{ '-90': '-90°', '-45': '-45°', 0: '0°', 45: '45°', 90: '90°' }"
              />
              <span style="margin-left: 12px">{{ angle }}°</span>
            </a-form-item>
          </div>

          <!-- 图片水印配置 -->
          <div v-if="watermarkType === 'image'">
            <a-form-item label="水印图片" required>
              <a-upload
                :before-upload="handleWatermarkImageUpload"
                :show-upload-list="false"
                accept="image/*"
              >
                <a-button>
                  <UploadOutlined /> 选择图片
                </a-button>
              </a-upload>
              <div v-if="watermarkImagePreview" style="margin-top: 12px">
                <img :src="watermarkImagePreview" style="max-width: 200px; max-height: 200px" />
              </div>
            </a-form-item>

            <a-form-item label="透明度">
              <a-slider 
                v-model:value="transparency" 
                :min="0" 
                :max="255" 
                :marks="{ 0: '透明', 128: '半透明', 255: '不透明' }"
              />
              <span style="margin-left: 12px">{{ transparency }}</span>
            </a-form-item>
          </div>

          <!-- 通用配置 -->
          <a-divider />

          <a-form-item label="水印位置">
            <a-select v-model:value="watermarkPosition" style="width: 200px">
              <a-select-option value="center">居中</a-select-option>
              <a-select-option value="top-left">左上角</a-select-option>
              <a-select-option value="top-right">右上角</a-select-option>
              <a-select-option value="bottom-left">左下角</a-select-option>
              <a-select-option value="bottom-right">右下角</a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item label="应用范围">
            <a-radio-group v-model:value="applyToAll">
              <a-radio :value="true">所有工作表</a-radio>
              <a-radio :value="false">仅当前工作表</a-radio>
            </a-radio-group>
          </a-form-item>

        </a-card>
      </div>


      <!-- 步骤 2: 开始处理 -->
      <div v-if="currentStep === 2" class="step-content">
        <a-result
          :status="processing ? 'info' : results.length > 0 ? 'success' : 'info'"
          :title="processing ? '正在处理...' : results.length > 0 ? '处理完成！' : '准备开始处理'"
          :sub-title="processing ? `正在处理第 ${currentFileIndex + 1} / ${files.length} 个文件` : results.length > 0 ? `成功: ${successCount} / ${results.length}` : '点击下方开始处理按钮'"
        >
          <template #icon>
            <LoadingOutlined v-if="processing" spin style="font-size: 48px; color: #6366f1" />
            <CheckCircleOutlined v-else-if="results.length > 0" style="font-size: 48px; color: #52c41a" />
            <FileProtectOutlined v-else style="font-size: 48px; color: #6366f1" />
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
          </template>
        </a-result>

        <!-- 处理进度 -->
        <div v-if="processing || results.length > 0" style="margin-top: 32px">
          <a-card title="处理详情" :bordered="false">
            <a-list :data-source="results" :loading="processing">
              <template #renderItem="{ item, index }">
                <a-list-item>
                  <a-list-item-meta>
                    <template #title>
                      <span>{{ files[index]?.name }}</span>
                      <a-tag 
                        :color="item.success ? 'success' : 'error'" 
                        style="margin-left: 8px"
                      >
                        {{ item.success ? '成功' : '失败' }}
                      </a-tag>
                    </template>
                    <template #description>
                      <div v-if="item.success">
                        <div>总工作表: {{ item.statistics.total_sheets }}</div>
                        <div>已添加水印: {{ item.statistics.processed_sheets }}</div>
                        <div>水印类型: {{ item.statistics.watermark_type === 'text' ? '文本' : '图片' }}</div>
                      </div>
                      <div v-else style="color: #ff4d4f">
                        {{ item.error }}
                      </div>
                    </template>
                  </a-list-item-meta>
                  <template #actions>
                    <a-button 
                      v-if="item.success" 
                      type="link" 
                      @click="downloadFile(index)"
                    >
                      下载
                    </a-button>
                  </template>
                </a-list-item>
              </template>
            </a-list>
          </a-card>
        </div>
      </div>

    </template>
  </PluginLayout>
</template>


<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import { 
  LoadingOutlined, 
  CheckCircleOutlined, 
  FileProtectOutlined,
  UploadOutlined
} from '@ant-design/icons-vue'
import PluginLayout from '@/components/PluginLayout.vue'
import FileUpload from '@/components/FileUpload.vue'
import { runPythonScript } from '@/utils/py'
import { downloadProcessedFile, formatFileSize } from '@/utils/file-service'

// 引用
const layoutRef = ref()
const fileUploadRef = ref()

// 文件相关
const files = ref<File[]>([])
const results = ref<any[]>([])
const processing = ref(false)
const currentFileIndex = ref(0)

// 水印配置
const watermarkType = ref<'text' | 'image'>('text')
const watermarkText = ref('WATERMARK')
const fontSize = ref(48)
const textColor = ref('#808080')
const transparency = ref(128)
const angle = ref(-45)
const watermarkPosition = ref('center')
const applyToAll = ref(true)
const watermarkImageData = ref('')
const watermarkImagePreview = ref('')

// 表格列定义
const fileColumns = [
  { title: '序号', key: 'index', width: 80 },
  { title: '文件名', key: 'name' },
  { title: '大小', key: 'size', width: 120 },
  { title: '操作', key: 'action', width: 100 }
]

// 计算属性
const canProceed = computed(() => {
  const step = layoutRef.value?.currentStep || 0
  if (step === 0) return files.value.length > 0
  if (step === 1) {
    if (watermarkType.value === 'text') {
      return watermarkText.value.trim().length > 0
    } else {
      return watermarkImageData.value.length > 0
    }
  }
  return true
})

const successCount = computed(() => {
  return results.value.filter(r => r.success).length
})

// 文件处理
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

// 水印图片上传
const handleWatermarkImageUpload = (file: File) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const base64 = (e.target?.result as string).split(',')[1]
    watermarkImageData.value = base64
    watermarkImagePreview.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
  return false // 阻止自动上传
}

// 步骤处理
const handleStepChange = (step: number) => {
  // 步骤变化时的处理
}

const handleNext = () => {
  // 下一步按钮处理
}

// 开始处理
const startProcessing = async () => {
  processing.value = true
  results.value = []
  currentFileIndex.value = 0

  try {
    // 准备水印配置
    const watermarkConfig: any = {
      type: watermarkType.value,
      position: watermarkPosition.value,
      apply_to_all: applyToAll.value,
      transparency: transparency.value
    }

    if (watermarkType.value === 'text') {
      // 文本水印配置
      watermarkConfig.text = watermarkText.value
      watermarkConfig.font_size = fontSize.value
      
      // 转换颜色格式
      const hex = textColor.value.replace('#', '')
      watermarkConfig.color = [
        parseInt(hex.substr(0, 2), 16),
        parseInt(hex.substr(2, 2), 16),
        parseInt(hex.substr(4, 2), 16)
      ]
      watermarkConfig.angle = angle.value
    } else {
      // 图片水印配置
      watermarkConfig.image_data = watermarkImageData.value
    }

    // 处理每个文件
    for (let i = 0; i < files.value.length; i++) {
      currentFileIndex.value = i
      const file = files.value[i]

      try {
        // 读取文件为Base64
        const fileData = await readFileAsBase64(file)

        // 调用Python脚本处理
        const result = await runPythonScript('add-watermark', {
          fileData: fileData.split(',')[1],
          watermarkConfig
        })

        results.value.push(result)
      } catch (error: any) {
        results.value.push({
          success: false,
          error: error.message || '处理失败'
        })
      }
    }

    message.success(`处理完成！成功: ${successCount.value}/${files.value.length}`)
  } catch (error: any) {
    message.error('处理过程中出现错误: ' + error.message)
  } finally {
    processing.value = false
  }
}

// 读取文件为Base64
const readFileAsBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

// 下载文件
const downloadFile = (index: number) => {
  const result = results.value[index]
  const file = files.value[index]
  
  if (result.success && result.data) {
    const fileName = file.name.replace(/\.xlsx?$/i, '_watermark.xlsx')
    downloadProcessedFile(result.data, fileName)
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
