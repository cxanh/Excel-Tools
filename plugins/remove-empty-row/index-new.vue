<template>
  <PluginLayout
    title="按规则删除改 Excel 内容"
    :can-proceed="canProceed"
    :processing="processing"
    @step-change="handleStepChange"
    @next="handleNext"
    @prev="handlePrev"
    @reset="handleReset"
    @add-files="handleAddFiles"
    @import-from-folder="handleImportFromFolder"
    @clear-all="handleClearAll"
    ref="layoutRef"
  >
    <template #default="{ currentStep }">
      <!-- 步骤 0: 选择待处理文件 -->
      <div v-if="currentStep === 0" class="step-content">
        <a-alert
          message="不同类型的【相关关键字】替换成【不同类型】内容"
          description="导入 Excel 规则修改 Excel 内容（如：需要将第一个文件中的 a 替换为 b，第二个文件中的 a 替换为 c，第三个文件中的 a 替换为 d）"
          type="warning"
          show-icon
          style="margin-bottom: 24px"
        />

        <!-- 文件上传区域 -->
        <div class="upload-area">
          <FileUpload
            :multiple="true"
            @change="handleFileChange"
            ref="fileUploadRef"
          />
        </div>

        <!-- 文件列表 -->
        <div v-if="files.length > 0" class="file-list">
          <a-table
            :columns="fileColumns"
            :data-source="files"
            :pagination="false"
            bordered
          >
            <template #bodyCell="{ column, record, index }">
              <template v-if="column.key === 'index'">
                {{ index + 1 }}
              </template>
              <template v-else-if="column.key === 'name'">
                <FileExcelOutlined style="color: #52c41a; margin-right: 8px" />
                {{ record.name }}
              </template>
              <template v-else-if="column.key === 'size'">
                {{ formatFileSize(record.size) }}
              </template>
              <template v-else-if="column.key === 'creator'">
                {{ record.creator || '-' }}
              </template>
              <template v-else-if="column.key === 'createTime'">
                {{ formatDate(record.lastModified) }}
              </template>
              <template v-else-if="column.key === 'modifyTime'">
                {{ formatDate(record.lastModified) }}
              </template>
              <template v-else-if="column.key === 'actions'">
                <a-space>
                  <a-button type="link" size="small" @click="previewFile(record)">
                    预览
                  </a-button>
                  <a-button type="link" size="small" danger @click="removeFile(index)">
                    排除
                  </a-button>
                </a-space>
              </template>
            </template>
          </a-table>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <a-empty description="您可以将待处理内容【拖放】到此处">
            <template #description>
              <p>如果无法拖动，请尝试【选择】或使用右上方【更多】中的从桌面新自动添加</p>
            </template>
          </a-empty>
        </div>
      </div>

      <!-- 步骤 1: 设置处理规则 -->
      <div v-if="currentStep === 1" class="step-content">
        <a-card title="处理规则配置" :bordered="false">
          <a-form :model="formData" layout="vertical">
            <a-form-item label="删除规则">
              <a-radio-group v-model:value="formData.deleteRule">
                <a-radio value="empty">删除完全空白的行</a-radio>
                <a-radio value="partial">删除部分空白的行</a-radio>
                <a-radio value="custom">自定义规则</a-radio>
              </a-radio-group>
            </a-form-item>

            <a-form-item v-if="formData.deleteRule === 'custom'" label="自定义规则">
              <a-textarea
                v-model:value="formData.customRule"
                placeholder="请输入自定义规则"
                :rows="4"
              />
            </a-form-item>

            <a-form-item label="处理范围">
              <a-checkbox-group v-model:value="formData.sheets">
                <a-checkbox value="all">所有工作表</a-checkbox>
                <a-checkbox value="active">仅当前工作表</a-checkbox>
                <a-checkbox value="custom">指定工作表</a-checkbox>
              </a-checkbox-group>
            </a-form-item>
          </a-form>
        </a-card>
      </div>

      <!-- 步骤 2: 设置导出选项 -->
      <div v-if="currentStep === 2" class="step-content">
        <a-card title="导出选项" :bordered="false">
          <a-form :model="exportOptions" layout="vertical">
            <a-form-item label="文件命名">
              <a-radio-group v-model:value="exportOptions.naming">
                <a-radio value="original">保持原文件名</a-radio>
                <a-radio value="suffix">添加后缀</a-radio>
                <a-radio value="custom">自定义命名</a-radio>
              </a-radio-group>
            </a-form-item>

            <a-form-item v-if="exportOptions.naming === 'suffix'" label="后缀内容">
              <a-input v-model:value="exportOptions.suffix" placeholder="例如：_processed" />
            </a-form-item>

            <a-form-item label="文件格式">
              <a-select v-model:value="exportOptions.format">
                <a-select-option value="xlsx">Excel 工作簿 (.xlsx)</a-select-option>
                <a-select-option value="xls">Excel 97-2003 (.xls)</a-select-option>
                <a-select-option value="csv">CSV 文件 (.csv)</a-select-option>
              </a-select>
            </a-form-item>
          </a-form>
        </a-card>
      </div>

      <!-- 步骤 3: 设置输出目录 -->
      <div v-if="currentStep === 3" class="step-content">
        <a-card title="输出目录" :bordered="false">
          <a-form layout="vertical">
            <a-form-item label="保存位置">
              <a-input
                v-model:value="outputPath"
                placeholder="选择输出目录"
                readonly
              >
                <template #addonAfter>
                  <a-button @click="selectOutputPath">
                    <FolderOpenOutlined />
                    浏览
                  </a-button>
                </template>
              </a-input>
            </a-form-item>

            <a-form-item>
              <a-checkbox v-model:checked="autoOpen">
                处理完成后自动打开输出目录
              </a-checkbox>
            </a-form-item>
          </a-form>
        </a-card>
      </div>

      <!-- 步骤 4: 开始处理 -->
      <div v-if="currentStep === 4" class="step-content">
        <a-result
          :status="processing ? 'info' : results.length > 0 ? 'success' : 'info'"
          :title="processing ? '正在处理...' : results.length > 0 ? '处理完成！' : '准备开始处理'"
          :sub-title="processing ? `正在处理第 ${currentFileIndex + 1} / ${files.length} 个文件` : results.length > 0 ? `成功: ${successCount} / ${results.length}` : '点击下方"开始处理"按钮'"
        >
          <template #icon>
            <LoadingOutlined v-if="processing" spin style="font-size: 48px; color: #6366f1" />
          </template>

          <template #extra>
            <a-progress
              v-if="processing"
              :percent="progress"
              :stroke-color="{
                '0%': '#6366f1',
                '100%': '#8b5cf6',
              }"
              style="max-width: 500px; margin: 0 auto"
            />

            <a-space v-if="results.length > 0" style="margin-top: 16px">
              <a-button type="primary" @click="downloadAll">
                <DownloadOutlined />
                下载全部
              </a-button>
              <a-button @click="openOutputFolder">
                <FolderOpenOutlined />
                打开文件夹
              </a-button>
            </a-space>
          </template>
        </a-result>

        <!-- 处理结果列表 -->
        <div v-if="results.length > 0" class="results-list">
          <a-list :data-source="results" :grid="{ gutter: 16, column: 1 }">
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
                    <a-button v-if="item.success" type="link" @click="handleDownload(item)">
                      <DownloadOutlined />
                      下载
                    </a-button>
                  </template>

                  <div v-if="item.success && item.statistics">
                    <a-descriptions :column="3" size="small">
                      <a-descriptions-item label="总行数">
                        {{ item.statistics.totalRows }}
                      </a-descriptions-item>
                      <a-descriptions-item label="删除行数">
                        <a-tag color="red">{{ item.statistics.deletedRows }}</a-tag>
                      </a-descriptions-item>
                      <a-descriptions-item label="处理时间">
                        {{ item.statistics.processingTime }}ms
                      </a-descriptions-item>
                    </a-descriptions>
                  </div>

                  <a-alert v-if="!item.success" :message="item.error" type="error" show-icon />
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
  FileExcelOutlined,
  FolderOpenOutlined,
  LoadingOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined
} from '@ant-design/icons-vue'
import PluginLayout from '@/components/PluginLayout.vue'
import FileUpload from '@/components/FileUpload.vue'
import { processFile, downloadResult, type ProcessResult } from '@/utils/file-service'

const props = defineProps<{
  workerScript?: string
}>()

const files = ref<File[]>([])
const formData = ref({
  deleteRule: 'empty',
  customRule: '',
  sheets: ['all']
})
const exportOptions = ref({
  naming: 'suffix',
  suffix: '_processed',
  format: 'xlsx'
})
const outputPath = ref('')
const autoOpen = ref(true)
const processing = ref(false)
const progress = ref(0)
const currentFileIndex = ref(0)
const results = ref<ProcessResult[]>([])
const fileUploadRef = ref()
const layoutRef = ref()

const fileColumns = [
  { title: '序号', key: 'index', width: 80 },
  { title: '名称', key: 'name' },
  { title: '路径', key: 'path', width: 150 },
  { title: '扩展名', key: 'extension', width: 100 },
  { title: '创建时间', key: 'createTime', width: 180 },
  { title: '修改时间', key: 'modifyTime', width: 180 },
  { title: '操作', key: 'actions', width: 150 }
]

const canProceed = computed(() => {
  const step = layoutRef.value?.currentStep || 0
  if (step === 0) return files.value.length > 0
  if (step === 1) return true
  if (step === 2) return true
  if (step === 3) return outputPath.value !== ''
  return false
})

const successCount = computed(() => results.value.filter(r => r.success).length)

function handleFileChange(newFiles: File[]) {
  files.value = newFiles
}

function handleAddFiles() {
  fileUploadRef.value?.openFileDialog()
}

function handleImportFromFolder() {
  message.info('从文件夹导入功能开发中...')
}

function handleClearAll() {
  files.value = []
  results.value = []
  if (fileUploadRef.value) {
    fileUploadRef.value.clear()
  }
}

function removeFile(index: number) {
  files.value.splice(index, 1)
}

function previewFile(file: File) {
  message.info(`预览文件: ${file.name}`)
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

function formatDate(timestamp: number): string {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

function selectOutputPath() {
  // 这里应该调用 Electron 的文件选择对话框
  outputPath.value = 'C:\\Users\\Desktop\\Output'
  message.success('已选择输出目录')
}

function handleStepChange(step: number) {
  console.log('Step changed to:', step)
}

function handleNext() {
  const step = layoutRef.value?.currentStep || 0
  if (step === 4) {
    handleProcess()
  }
}

function handlePrev() {
  // 返回上一步
}

function handleReset() {
  files.value = []
  results.value = []
  progress.value = 0
  currentFileIndex.value = 0
  formData.value = {
    deleteRule: 'empty',
    customRule: '',
    sheets: ['all']
  }
  exportOptions.value = {
    naming: 'suffix',
    suffix: '_processed',
    format: 'xlsx'
  }
  outputPath.value = ''
  if (fileUploadRef.value) {
    fileUploadRef.value.clear()
  }
}

async function handleProcess() {
  if (!props.workerScript) {
    message.error('插件配置错误')
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
        const result = await processFile(file, props.workerScript, formData.value)
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

function openOutputFolder() {
  message.info('打开输出文件夹: ' + outputPath.value)
}
</script>

<style scoped>
.step-content {
  max-width: 1200px;
  margin: 0 auto;
}

.upload-area {
  margin-bottom: 24px;
}

.file-list {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.empty-state {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 8px;
}

.results-list {
  margin-top: 24px;
  max-width: 1000px;
  margin-left: auto;
  margin-right: auto;
}
</style>
