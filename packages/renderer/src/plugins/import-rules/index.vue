<template>
  <plugin-template
    :plugin-title="pluginTitle"
    :info-message="infoMessage"
    :error-message="errorMessage"
    :success-message="successMessage"
    :current-step="currentStep"
    :max-file-size="maxFileSize"
    :is-processing="isProcessing"
    :loading-progress="loadingProgress"
    :progress-text="progressText"
    :pyodide-loading="pyodideLoading"
    @add-file="handleAddFile"
    @import-folder="handleImportFolder"
    @more-action="handleMoreAction"
    @next-step="handleNextStep"
    @prev-step="handlePrevStep"
    @remove-file="handleRemoveFile"
    @close-info="infoMessage = ''"
    @close-error="errorMessage = ''"
    @close-success="successMessage = ''"
    @show-help="handleShowHelp"
  >
    <!-- 插件内容区域 -->
    <div class="plugin-specific-content">
      <!-- 步骤1：文件选择 -->
      <a-card v-if="currentStep === 0" title="步骤1：选择文件" class="step-card">
        <p>请选择要处理的 Excel 文件和规则文件</p>
        <div class="file-upload-section">
          <a-upload
            v-model:file-list="excelFileList"
            :before-upload="beforeUploadExcel"
            :custom-request="customRequestExcel"
            accept=".xlsx,.xls"
            :show-upload-list="true"
          >
            <a-button type="primary" icon="upload">上传 Excel 文件</a-button>
          </a-upload>
          <span class="file-hint">支持 .xlsx, .xls 格式</span>
        </div>
        <div class="file-upload-section" style="margin-top: 16px;">
          <a-upload
            v-model:file-list="ruleFileList"
            :before-upload="beforeUploadRule"
            :custom-request="customRequestRule"
            accept=".xlsx,.xls,.csv"
            :show-upload-list="true"
          >
            <a-button type="primary" icon="upload">上传规则文件</a-button>
          </a-upload>
          <span class="file-hint">支持 .xlsx, .xls, .csv 格式</span>
        </div>
      </a-card>
      
      <!-- 步骤2：设置规则 -->
      <a-card v-if="currentStep === 1" title="步骤2：设置规则" class="step-card">
        <p>请设置处理规则</p>
        <a-form layout="vertical">
          <a-form-item label="规则文件列映射">
            <a-select v-model:value="ruleColumnMap.findColumn" placeholder="选择规则文件中的查找列">
              <a-select-option value="A">A列</a-select-option>
              <a-select-option value="B">B列</a-select-option>
              <a-select-option value="C">C列</a-select-option>
            </a-select>
            <span style="margin: 0 8px;">→</span>
            <a-select v-model:value="ruleColumnMap.replaceColumn" placeholder="选择规则文件中的替换列">
              <a-select-option value="A">A列</a-select-option>
              <a-select-option value="B">B列</a-select-option>
              <a-select-option value="C">C列</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="匹配选项">
            <a-checkbox-group v-model:value="matchOptions">
              <a-checkbox value="caseSensitive">区分大小写</a-checkbox>
              <a-checkbox value="regex">使用正则表达式</a-checkbox>
              <a-checkbox value="wholeWord">匹配整个单词</a-checkbox>
            </a-checkbox-group>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤3：其他选项 -->
      <a-card v-if="currentStep === 2" title="步骤3：其他选项" class="step-card">
        <p>请设置其他选项</p>
        <a-form layout="vertical">
          <a-form-item label="处理范围">
            <a-select v-model:value="processScope" placeholder="选择处理范围">
              <a-select-option value="all">所有工作表</a-select-option>
              <a-select-option value="specific">指定工作表</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item v-if="processScope === 'specific'" label="指定工作表">
            <a-select v-model:value="selectedSheets" mode="multiple" placeholder="选择要处理的工作表">
              <a-select-option value="Sheet1">Sheet1</a-select-option>
              <a-select-option value="Sheet2">Sheet2</a-select-option>
            </a-select>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤4：输出设置 -->
      <a-card v-if="currentStep === 3" title="步骤4：输出设置" class="step-card">
        <p>请设置输出选项</p>
        <a-form layout="vertical">
          <a-form-item label="输出格式">
            <a-select v-model:value="outputFormat" placeholder="选择输出格式">
              <a-select-option value="xlsx">.xlsx</a-select-option>
              <a-select-option value="xls">.xls</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="输出文件名">
            <a-input v-model:value="outputFileName" placeholder="输入输出文件名" />
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤5：开始处理 -->
      <a-card v-if="currentStep === 4" title="步骤5：处理结果" class="step-card">
        <div v-if="!processingComplete">
          <a-spin size="large" tip="正在处理..."></a-spin>
        </div>
        <div v-else>
          <a-alert type="success" show-icon message="处理完成" description="Excel 文件已成功处理" />
          <div class="result-stats" style="margin-top: 16px;">
            <a-statistic title="处理文件数" :value="processedFiles" />
            <a-statistic title="修改单元格数" :value="modifiedCells" style="margin-left: 32px;" />
            <a-statistic title="执行时间" :value="executionTime" suffix="秒" style="margin-left: 32px;" />
          </div>
          <div class="download-section" style="margin-top: 24px;">
            <a-button type="primary" icon="download" @click="handleDownload">下载处理后的文件</a-button>
          </div>
        </div>
      </a-card>
    </div>
    
    <!-- 帮助文档插槽 -->
    <template #help-content>
      <div class="help-documentation">
        <h1>导入 Excel 规则修改 Excel 内容</h1>
        
        <h2>功能介绍</h2>
        <p>当不同的 Excel 文档有不同的修改规则时，可以通过导入规则文件进行批量修改。</p>
        
        <h2>操作步骤</h2>
        <ol>
          <li><strong>上传文件</strong>：上传要处理的 Excel 文件和规则文件</li>
          <li><strong>设置规则</strong>：配置规则文件列映射和匹配选项</li>
          <li><strong>其他选项</strong>：设置处理范围等其他选项</li>
          <li><strong>输出设置</strong>：配置输出格式和文件名</li>
          <li><strong>开始处理</strong>：执行处理并下载结果</li>
        </ol>
        
        <h2>规则文件格式</h2>
        <p>规则文件可以是 Excel 文件或 CSV 文件，包含两列：</p>
        <ul>
          <li>第一列：要查找的内容</li>
          <li>第二列：替换后的内容</li>
        </ul>
        
        <h2>注意事项</h2>
        <ul>
          <li>支持 .xlsx, .xls 格式的 Excel 文件</li>
          <li>支持 .xlsx, .xls, .csv 格式的规则文件</li>
          <li>单个文件大小限制为 10MB</li>
          <li>处理大型文件可能需要较长时间</li>
        </ul>
      </div>
    </template>
  </plugin-template>
</template>

<script setup>
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import PluginTemplate from '@/components/PluginTemplate.vue'

// 插件基本信息
const pluginTitle = ref('导入 Excel 规则修改 Excel 内容')
const pluginDescription = ref('当不同的 Excel 文档有不同的修改规则时，可以通过导入规则文件进行批量修改')

// 状态管理
const infoMessage = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const currentStep = ref(0)
const maxFileSize = ref(10 * 1024 * 1024) // 10MB
const isProcessing = ref(false)
const loadingProgress = ref(0)
const progressText = ref('')
const pyodideLoading = ref(false)

// 文件相关
const excelFileList = ref([])
const ruleFileList = ref([])
const selectedFiles = ref([])

// 规则设置
const ruleColumnMap = ref({ findColumn: 'A', replaceColumn: 'B' })
const matchOptions = ref([])

// 其他选项
const processScope = ref('all')
const selectedSheets = ref([])

// 输出设置
const outputFormat = ref('xlsx')
const outputFileName = ref('processed_file')

// 处理结果
const processingComplete = ref(false)
const processedFiles = ref(0)
const modifiedCells = ref(0)
const executionTime = ref(0)

// 处理文件上传
const handleAddFile = () => {
  message.info('文件上传功能待实现')
}

// 从文件夹导入文件
const handleImportFolder = () => {
  message.info('从文件夹导入功能待实现')
}

// 处理更多操作
const handleMoreAction = (action) => {
  message.info(`更多操作: ${action}`)
}

// 处理下一步
const handleNextStep = () => {
  if (currentStep.value < 4) {
    currentStep.value++
  } else {
    // 开始处理
    handleProcess()
  }
}

// 处理上一步
const handlePrevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 处理文件删除
const handleRemoveFile = (key) => {
  selectedFiles.value = selectedFiles.value.filter(file => file.key !== key)
}

// 处理显示帮助
const handleShowHelp = () => {
  message.info('显示帮助')
}

// 处理文件上传前的验证
const beforeUploadExcel = (file) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                 file.type === 'application/vnd.ms-excel'
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isExcel) {
    message.error('请上传 Excel 文件！')
    return false
  }
  if (!isLt10M) {
    message.error('文件大小不能超过 10MB！')
    return false
  }
  return true
}

// 处理规则文件上传前的验证
const beforeUploadRule = (file) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                 file.type === 'application/vnd.ms-excel'
  const isCSV = file.type === 'text/csv'
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isExcel && !isCSV) {
    message.error('请上传 Excel 或 CSV 文件！')
    return false
  }
  if (!isLt10M) {
    message.error('文件大小不能超过 10MB！')
    return false
  }
  return true
}

// 自定义 Excel 文件上传处理
const customRequestExcel = (options) => {
  const file = options.file
  excelFileList.value.push(file)
  options.onSuccess({ status: 'done' })
  message.success('Excel 文件上传成功！')
}

// 自定义规则文件上传处理
const customRequestRule = (options) => {
  const file = options.file
  ruleFileList.value.push(file)
  options.onSuccess({ status: 'done' })
  message.success('规则文件上传成功！')
}

// 处理文件
const handleProcess = async () => {
  if (excelFileList.value.length === 0 || ruleFileList.value.length === 0) {
    message.error('请上传 Excel 文件和规则文件！')
    return
  }
  
  isProcessing.value = true
  loadingProgress.value = 0
  processingComplete.value = false
  
  // 模拟处理过程
  try {
    // 初始化进度
    loadingProgress.value = 10
    progressText.value = '正在初始化 Python 环境...'
    
    // 模拟处理
    await new Promise(resolve => setTimeout(resolve, 1000))
    loadingProgress.value = 30
    progressText.value = '正在解析规则文件...'
    
    await new Promise(resolve => setTimeout(resolve, 1000))
    loadingProgress.value = 60
    progressText.value = '正在处理 Excel 文件...'
    
    await new Promise(resolve => setTimeout(resolve, 1500))
    loadingProgress.value = 90
    progressText.value = '正在生成输出文件...'
    
    await new Promise(resolve => setTimeout(resolve, 500))
    loadingProgress.value = 100
    progressText.value = '处理完成'
    
    // 更新处理结果
    processedFiles.value = excelFileList.value.length
    modifiedCells.value = Math.floor(Math.random() * 1000) + 100
    executionTime.value = Math.round(4000 / 1000)
    processingComplete.value = true
    
    message.success('文件处理完成！')
  } catch (error) {
    message.error('文件处理失败：' + error.message)
    errorMessage.value = '文件处理失败：' + error.message
  } finally {
    isProcessing.value = false
  }
}

// 处理下载
const handleDownload = () => {
  message.info('文件下载功能待实现')
}
</script>

<style scoped>
.plugin-specific-content {
  margin: 20px 0;
}

.step-card {
  margin-bottom: 20px;
}

.file-upload-section {
  margin: 16px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-hint {
  color: #999;
  font-size: 12px;
}

.result-stats {
  display: flex;
  align-items: center;
}

.download-section {
  display: flex;
  justify-content: center;
}
</style>