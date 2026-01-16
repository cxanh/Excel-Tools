<template>
  <PluginWrapper
    :can-proceed="canProceed"
    :processing="processing"
    @step-change="handleStepChange"
    @next="handleNext"
    @prev="handlePrev"
    @reset="handleReset"
    ref="wrapperRef"
  >
    <template #default="{ currentStep }">
      <!-- 步骤 0: 上传文件 -->
      <div v-if="currentStep === 0" class="step-content">
        <a-alert
          message="删除空白行"
          description="自动识别并删除Excel文件中的所有空白行，保留原始格式和样式。"
          type="info"
          show-icon
          style="margin-bottom: 24px"
        />

        <FileUpload
          :multiple="true"
          @change="handleFileChange"
          ref="fileUploadRef"
        />
        
        <div v-if="files.length > 0" style="margin-top: 16px">
          <a-space direction="vertical" style="width: 100%">
            <a-tag color="blue">已选择 {{ files.length }} 个文件</a-tag>
            <a-list
              :data-source="files"
              size="small"
              bordered
            >
              <template #renderItem="{ item, index }">
                <a-list-item>
                  <a-space>
                    <FileExcelOutlined style="color: #52c41a" />
                    <span>{{ item.name }}</span>
                    <a-tag>{{ formatFileSize(item.size) }}</a-tag>
                  </a-space>
                  <template #actions>
                    <a-button
                      type="link"
                      danger
                      size="small"
                      @click="removeFile(index)"
                    >
                      删除
                    </a-button>
                  </template>
                </a-list-item>
              </template>
            </a-list>
          </a-space>
        </div>
      </div>

      <!-- 步骤 1: 配置参数 -->
      <div v-if="currentStep === 1" class="step-content">
        <a-alert
          message="配置处理选项"
          description="此功能无需额外配置，将自动删除所有空白行。"
          type="info"
          show-icon
          style="margin-bottom: 24px"
        />

        <a-card title="处理摘要" :bordered="false">
          <a-descriptions :column="1">
            <a-descriptions-item label="待处理文件">
              {{ files.length }} 个
            </a-descriptions-item>
            <a-descriptions-item label="处理方式">
              删除所有空白行
            </a-descriptions-item>
            <a-descriptions-item label="保留内容">
              原始格式和样式
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </div>

      <!-- 步骤 2: 处理中 -->
      <div v-if="currentStep === 2" class="step-content">
        <a-result
          status="info"
          title="准备处理"
          sub-title="点击"开始处理"按钮开始处理文件"
        >
          <template #icon>
            <LoadingOutlined v-if="processing" spin />
            <PlayCircleOutlined v-else />
          </template>
          <template #extra>
            <a-progress
              v-if="processing"
              :percent="progress"
              status="active"
              :stroke-color="{
                '0%': '#108ee9',
                '100%': '#87d068',
              }"
            />
            <div v-if="processing" style="margin-top: 16px">
              <a-space direction="vertical" align="center" style="width: 100%">
                <a-spin size="large" />
                <span>正在处理文件 {{ currentFileIndex + 1 }} / {{ files.length }}</span>
              </a-space>
            </div>
          </template>
        </a-result>
      </div>

      <!-- 步骤 3: 下载结果 -->
      <div v-if="currentStep === 3" class="step-content">
        <a-result
          :status="allSuccess ? 'success' : 'warning'"
          :title="allSuccess ? '处理完成！' : '处理完成（部分失败）'"
          :sub-title="`成功: ${successCount} / ${results.length}`"
        >
          <template #extra>
            <a-space>
              <a-button type="primary" @click="downloadAll" v-if="successCount > 0">
                <DownloadOutlined />
                下载全部
              </a-button>
            </a-space>
          </template>
        </a-result>

        <a-list
          :data-source="results"
          :grid="{ gutter: 16, column: 1 }"
          style="margin-top: 24px"
        >
          <template #renderItem="{ item }">
            <a-list-item>
              <a-card size="small">
                <template #title>
                  <a-space>
                    <CheckCircleOutlined v-if="item.success" style="color: #52c41a" />
                    <CloseCircleOutlined v-else style="color: #ff4d4f" />
                    <span>{{ item.fileName }}</span>
                  </a-space>
                </template>
                
                <template #extra>
                  <a-button
                    v-if="item.success"
                    type="link"
                    @click="handleDownload(item)"
                  >
                    <DownloadOutlined />
                    下载
                  </a-button>
                </template>

                <!-- 统计信息 -->
                <div v-if="item.success && item.statistics">
                  <a-descriptions :column="2" size="small">
                    <a-descriptions-item label="总行数">
                      {{ item.statistics.totalRows }}
                    </a-descriptions-item>
                    <a-descriptions-item label="删除行数">
                      <a-tag color="red">{{ item.statistics.deletedRows }}</a-tag>
                    </a-descriptions-item>
                    <a-descriptions-item label="剩余行数">
                      {{ item.statistics.remainingRows }}
                    </a-descriptions-item>
                    <a-descriptions-item label="处理时间">
                      {{ item.statistics.processingTime }}ms
                    </a-descriptions-item>
                  </a-descriptions>
                </div>

                <!-- 错误信息 -->
                <a-alert
                  v-if="!item.success"
                  :message="item.error"
                  type="error"
                  show-icon
                />

                <!-- 处理日志 -->
                <a-collapse v-if="item.logs.length > 0" style="margin-top: 12px">
                  <a-collapse-panel key="1" header="查看详细日志">
                    <div class="log-container">
                      <div v-for="(log, index) in item.logs" :key="index" class="log-item">
                        {{ log }}
                      </div>
                    </div>
                  </a-collapse-panel>
                </a-collapse>
              </a-card>
            </a-list-item>
          </template>
        </a-list>
      </div>
    </template>
  </PluginWrapper>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import {
  PlayCircleOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  FileExcelOutlined,
  LoadingOutlined
} from '@ant-design/icons-vue'
import PluginWrapper from '@/components/PluginWrapper.vue'
import FileUpload from '@/components/FileUpload.vue'
import { processFile, downloadResult, type ProcessResult } from '@/utils/file-service'

const props = defineProps<{
  workerScript?: string
}>()

const files = ref<File[]>([])
const processing = ref(false)
const progress = ref(0)
const currentFileIndex = ref(0)
const results = ref<ProcessResult[]>([])
const fileUploadRef = ref()
const wrapperRef = ref()

const canProceed = computed(() => {
  const step = wrapperRef.value?.currentStep || 0
  if (step === 0) return files.value.length > 0
  if (step === 1) return true
  if (step === 2) return !processing.value
  return false
})

const successCount = computed(() => results.value.filter(r => r.success).length)
const allSuccess = computed(() => results.value.length > 0 && successCount.value === results.value.length)

function handleFileChange(newFiles: File[]) {
  files.value = newFiles
}

function removeFile(index: number) {
  files.value.splice(index, 1)
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

function handleStepChange(step: number) {
  console.log('Step changed to:', step)
}

function handleNext() {
  const step = wrapperRef.value?.currentStep || 0
  if (step === 2) {
    // 开始处理
    handleProcess()
  }
}

function handlePrev() {
  // 返回上一步时清空结果
  if (wrapperRef.value?.currentStep === 1) {
    results.value = []
  }
}

function handleReset() {
  files.value = []
  results.value = []
  progress.value = 0
  currentFileIndex.value = 0
  if (fileUploadRef.value) {
    fileUploadRef.value.clear()
  }
}

async function handleProcess() {
  if (files.value.length === 0) {
    message.warning('请先选择文件')
    return
  }

  const workerScript = props.workerScript
  if (!workerScript) {
    message.error('插件配置错误：缺少worker脚本')
    return
  }

  processing.value = true
  progress.value = 0
  results.value = []
  currentFileIndex.value = 0

  try {
    const totalFiles = files.value.length

    for (let i = 0; i < totalFiles; i++) {
      currentFileIndex.value = i
      const file = files.value[i]
      
      try {
        const result = await processFile(file, workerScript)
        results.value.push(result)
      } catch (error) {
        results.value.push({
          success: false,
          fileName: file.name,
          logs: [],
          error: (error as Error).message
        })
      }

      progress.value = Math.round(((i + 1) / totalFiles) * 100)
    }

    message.success(`处理完成！成功: ${successCount.value}/${totalFiles}`)
    
    // 自动进入下一步
    if (wrapperRef.value) {
      wrapperRef.value.nextStep()
    }
  } catch (error) {
    message.error('处理失败: ' + (error as Error).message)
  } finally {
    processing.value = false
  }
}

async function handleDownload(result: ProcessResult) {
  try {
    await downloadResult(result, result.fileName)
    message.success('文件已保存')
  } catch (error) {
    message.error('下载失败: ' + (error as Error).message)
  }
}

async function downloadAll() {
  const successResults = results.value.filter(r => r.success)
  for (const result of successResults) {
    await handleDownload(result)
  }
}
</script>

<style scoped>
.step-content {
  min-height: 400px;
}

.log-container {
  max-height: 200px;
  overflow-y: auto;
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.log-item {
  padding: 4px 0;
  border-bottom: 1px solid #e8e8e8;
}

.log-item:last-child {
  border-bottom: none;
}
</style>
