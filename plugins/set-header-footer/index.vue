<template>
  <PluginLayout
    title="设置页眉页脚"
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
          description="批量设置Excel文件的页眉页脚，支持文本、页码、日期等元素，可配置左中右三个位置。"
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

      <!-- 步骤 1: 设置页眉页脚 -->
      <div v-if="currentStep === 1" class="step-content">
        <a-card title="页眉页脚配置" :bordered="false">
          <a-form layout="vertical">
            <a-divider orientation="left">页眉设置</a-divider>
            <a-row :gutter="16">
              <a-col :span="8">
                <a-form-item label="左侧内容">
                  <a-input v-model:value="formData.header_left" placeholder="例如：公司名称" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="中间内容">
                  <a-input v-model:value="formData.header_center" placeholder="例如：文档标题" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="右侧内容">
                  <a-input v-model:value="formData.header_right" placeholder="例如：&D (日期)" />
                </a-form-item>
              </a-col>
            </a-row>

            <a-divider orientation="left">页脚设置</a-divider>
            <a-row :gutter="16">
              <a-col :span="8">
                <a-form-item label="左侧内容">
                  <a-input v-model:value="formData.footer_left" placeholder="例如：部门名称" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="中间内容">
                  <a-input v-model:value="formData.footer_center" placeholder="例如：&P (页码)" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="右侧内容">
                  <a-input v-model:value="formData.footer_right" placeholder="例如：第 &P 页" />
                </a-form-item>
              </a-col>
            </a-row>

            <a-divider orientation="left">高级选项</a-divider>
            <a-form-item>
              <a-checkbox v-model:checked="formData.different_odd_even">区分奇偶页</a-checkbox>
            </a-form-item>
            <a-form-item>
              <a-checkbox v-model:checked="formData.apply_to_all">应用到所有工作表</a-checkbox>
            </a-form-item>

            <a-alert
              message="特殊代码说明"
              type="info"
              show-icon
              style="margin-top: 16px"
            >
              <template #description>
                <ul style="margin: 8px 0; padding-left: 20px">
                  <li>&D - 当前日期</li>
                  <li>&T - 当前时间</li>
                  <li>&P - 当前页码</li>
                  <li>&N - 总页数</li>
                  <li>&A - 工作表名称</li>
                  <li>&F - 文件名</li>
                </ul>
              </template>
            </a-alert>
          </a-form>
        </a-card>
      </div>

      <!-- 步骤 2: 设置导出选项 -->
      <div v-if="currentStep === 2" class="step-content">
        <a-card title="导出选项" :bordered="false">
          <a-form layout="vertical">
            <a-form-item label="文件命名">
              <a-radio-group v-model:value="exportOptions.naming">
                <a-radio value="original">保持原文件名</a-radio>
                <a-radio value="suffix">添加后缀</a-radio>
              </a-radio-group>
            </a-form-item>
            <a-form-item v-if="exportOptions.naming === 'suffix'" label="后缀内容">
              <a-input v-model:value="exportOptions.suffix" placeholder="例如：_header_footer" />
            </a-form-item>
          </a-form>
        </a-card>
      </div>

      <!-- 步骤 3: 设置输出目录 -->
      <div v-if="currentStep === 3" class="step-content">
        <a-card title="输出目录" :bordered="false">
          <a-form layout="vertical">
            <a-form-item label="保存位置">
              <a-input v-model:value="outputPath" placeholder="选择输出目录" readonly>
                <template #addonAfter>
                  <a-button @click="selectOutputPath">
                    <FolderOpenOutlined />浏览
                  </a-button>
                </template>
              </a-input>
            </a-form-item>
            <a-form-item>
              <a-checkbox v-model:checked="autoOpen">处理完成后自动打开输出目录</a-checkbox>
            </a-form-item>
          </a-form>
        </a-card>
      </div>

      <!-- 步骤 4: 开始处理 -->
      <div v-if="currentStep === 4" class="step-content">
        <a-result
          :status="processing ? 'info' : results.length > 0 ? 'success' : 'info'"
          :title="processing ? '正在处理...' : results.length > 0 ? '处理完成！' : '准备开始处理'"
          :sub-title="processing ? `正在处理第 ${currentFileIndex + 1} / ${files.length} 个文件` : results.length > 0 ? `成功: ${successCount} / ${results.length}` : '点击下方开始处理按钮'"
        >
          <template #icon>
            <LoadingOutlined v-if="processing" spin style="font-size: 48px; color: #6366f1" />
          </template>
          <template #extra>
            <a-progress v-if="processing" :percent="progress" :stroke-color="{ '0%': '#6366f1', '100%': '#8b5cf6' }" style="max-width: 500px; margin: 0 auto" />
            <a-space v-if="results.length > 0" style="margin-top: 16px">
              <a-button type="primary" @click="downloadAll"><DownloadOutlined />下载全部</a-button>
            </a-space>
          </template>
        </a-result>

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
                      <DownloadOutlined />下载
                    </a-button>
                  </template>
                  <div v-if="item.success && item.statistics">
                    <a-descriptions :column="3" size="small">
                      <a-descriptions-item label="总工作表">{{ item.statistics.totalSheets }}</a-descriptions-item>
                      <a-descriptions-item label="已设置"><a-tag color="green">{{ item.statistics.sheetsProcessed }}</a-tag></a-descriptions-item>
                      <a-descriptions-item label="奇偶页">{{ item.statistics.hasOddEven ? '是' : '否' }}</a-descriptions-item>
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
import { FileExcelOutlined, FolderOpenOutlined, LoadingOutlined, DownloadOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons-vue'
import PluginLayout from '@/components/PluginLayout.vue'
import FileUpload from '@/components/FileUpload.vue'
import { processFile, downloadResult, type ProcessResult } from '@/utils/file-service'

const props = defineProps<{ workerScript?: string }>()

const files = ref<File[]>([])
const formData = ref({
  header_left: '',
  header_center: '',
  header_right: '',
  footer_left: '',
  footer_center: '',
  footer_right: '',
  different_odd_even: false,
  apply_to_all: true
})
const exportOptions = ref({ naming: 'suffix', suffix: '_header_footer' })
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
  { title: '大小', key: 'size', width: 120 },
  { title: '类型', key: 'type', width: 100 },
  { title: '创建时间', key: 'createTime', width: 180 },
  { title: '修改时间', key: 'modifyTime', width: 180 },
  { title: '操作', key: 'actions', width: 100 }
]

const canProceed = computed(() => {
  const step = layoutRef.value?.currentStep || 0
  if (step === 0) return files.value.length > 0
  if (step === 3) return outputPath.value !== ''
  return true
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
  if (fileUploadRef.value) fileUploadRef.value.clear()
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

function formatDate(timestamp: number): string {
  return new Date(timestamp).toLocaleString('zh-CN')
}

function selectOutputPath() {
  outputPath.value = 'C:\\Users\\Desktop\\Output'
  message.success('已选择输出目录')
}

function handleStepChange(step: number) {
  console.log('Step changed to:', step)
}

function handleNext() {
  const step = layoutRef.value?.currentStep || 0
  if (step === 3) handleProcess()
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
        results.value.push({ success: false, fileName: file.name, logs: [], error: (error as Error).message })
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
