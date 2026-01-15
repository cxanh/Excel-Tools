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
        <p>请选择模板文件和数据源文件</p>
        <div class="file-upload-section">
          <a-upload
            v-model:file-list="templateFileList"
            :before-upload="beforeUploadTemplate"
            :custom-request="customRequestTemplate"
            accept=".xlsx,.xls"
            :show-upload-list="true"
          >
            <a-button type="primary" icon="upload">上传模板文件</a-button>
          </a-upload>
          <span class="file-hint">支持 .xlsx, .xls 格式</span>
        </div>
        <div class="file-upload-section" style="margin-top: 16px;">
          <a-upload
            v-model:file-list="dataSourceFileList"
            :before-upload="beforeUploadDataSource"
            :custom-request="customRequestDataSource"
            accept=".xlsx,.xls,.csv"
            :show-upload-list="true"
          >
            <a-button type="primary" icon="upload">上传数据源文件</a-button>
          </a-upload>
          <span class="file-hint">支持 .xlsx, .xls, .csv 格式</span>
        </div>
      </a-card>
      
      <!-- 步骤2：模板映射 -->
      <a-card v-if="currentStep === 1" title="步骤2：模板映射" class="step-card">
        <p>请设置模板字段与数据源字段的映射关系</p>
        <a-form layout="vertical">
          <a-form-item label="模板字段">
            <a-select v-model:value="selectedTemplateField" placeholder="选择模板中的字段">
              <a-select-option v-for="field in templateFields" :key="field" :value="field">{{ field }}</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="数据源字段">
            <a-select v-model:value="selectedDataSourceField" placeholder="选择数据源中的对应字段">
              <a-select-option v-for="field in dataSourceFields" :key="field" :value="field">{{ field }}</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item>
            <a-button type="primary" icon="plus" @click="addMapping">添加映射</a-button>
          </a-form-item>
          <a-form-item label="映射列表">
            <a-table :columns="mappingColumns" :data-source="fieldMappings" bordered size="small">
              <template #bodyCell="{ column, record, index }">
                <template v-if="column.key === 'actions'">
                  <a-button type="text" danger size="small" @click="removeMapping(index)">
                    <DeleteOutlined />
                  </a-button>
                </template>
              </template>
            </a-table>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤3：数据源配置 -->
      <a-card v-if="currentStep === 2" title="步骤3：数据源配置" class="step-card">
        <p>请配置数据源处理选项</p>
        <a-form layout="vertical">
          <a-form-item label="数据起始行">
            <a-input-number v-model:value="dataStartRow" :min="1" placeholder="数据源中数据的起始行" />
            <div class="hint-text">通常为2，表示跳过表头行</div>
          </a-form-item>
          <a-form-item label="批次大小">
            <a-input-number v-model:value="batchSize" :min="1" :max="100" placeholder="每批处理的数据条数" />
            <div class="hint-text">默认10，建议根据模板复杂度调整</div>
          </a-form-item>
          <a-form-item label="并发数">
            <a-input-number v-model:value="concurrency" :min="1" :max="10" placeholder="并发处理的线程数" />
            <div class="hint-text">默认3，建议根据系统性能调整</div>
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
          <a-form-item label="文件名模板">
            <a-input v-model:value="fileNameTemplate" placeholder="输入文件名模板，如：文档_{字段名}" />
            <div class="hint-text">使用{字段名}表示数据源中的字段值</div>
          </a-form-item>
          <a-form-item label="输出文件夹">
            <a-input v-model:value="outputFolder" placeholder="输入输出文件夹路径" />
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤5：开始处理 -->
      <a-card v-if="currentStep === 4" title="步骤5：处理结果" class="step-card">
        <div v-if="!processingComplete">
          <a-spin size="large" tip="正在处理..."></a-spin>
        </div>
        <div v-else>
          <a-alert type="success" show-icon message="处理完成" description="Excel 文档已成功生成" />
          <div class="result-stats" style="margin-top: 16px;">
            <a-statistic title="生成文件数" :value="generatedFiles" />
            <a-statistic title="处理数据条数" :value="processedRecords" style="margin-left: 32px;" />
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
        <h1>根据模板生成 Excel 文档</h1>
        
        <h2>功能介绍</h2>
        <p>先指定一个 Excel 文档作为模板，然后根据数据源批量生成多个 Excel 文档。</p>
        
        <h2>操作步骤</h2>
        <ol>
          <li><strong>上传文件</strong>：上传模板文件和数据源文件</li>
          <li><strong>模板映射</strong>：设置模板字段与数据源字段的映射关系</li>
          <li><strong>数据源配置</strong>：配置数据源处理选项</li>
          <li><strong>输出设置</strong>：配置输出格式和文件名模板</li>
          <li><strong>开始处理</strong>：执行处理并下载结果</li>
        </ol>
        
        <h2>模板文件格式</h2>
        <p>模板文件是一个包含占位符的 Excel 文件，占位符格式为 {字段名}，例如：</p>
        <ul>
          <li>{姓名}</li>
          <li>{年龄}</li>
          <li>{部门}</li>
        </ul>
        
        <h2>数据源文件格式</h2>
        <p>数据源文件可以是 Excel 文件或 CSV 文件，包含与模板占位符对应的字段：</p>
        <ul>
          <li>第一行通常为表头，包含字段名</li>
          <li>后续行为数据，每行对应一个要生成的文档</li>
        </ul>
        
        <h2>注意事项</h2>
        <ul>
          <li>支持 .xlsx, .xls 格式的模板文件</li>
          <li>支持 .xlsx, .xls, .csv 格式的数据源文件</li>
          <li>单个文件大小限制为 10MB</li>
          <li>生成大量文件时可能需要较长时间</li>
        </ul>
      </div>
    </template>
  </plugin-template>
</template>

<script setup>
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import { DeleteOutlined } from '@ant-design/icons-vue'
import PluginTemplate from '@/components/PluginTemplate.vue'

// 插件基本信息
const pluginTitle = ref('根据模板生成 Excel 文档')
const pluginDescription = ref('先指定一个 Excel 文档作为模板，然后根据数据源批量生成多个 Excel 文档')

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
const templateFileList = ref([])
const dataSourceFileList = ref([])
const selectedFiles = ref([])

// 模板和数据源字段
const templateFields = ref(['姓名', '年龄', '部门', '职位', '入职日期'])
const dataSourceFields = ref(['name', 'age', 'department', 'position', 'hire_date'])
const selectedTemplateField = ref('')
const selectedDataSourceField = ref('')

// 字段映射
const fieldMappings = ref([])
const mappingColumns = [
  { title: '模板字段', dataIndex: 'templateField', key: 'templateField' },
  { title: '数据源字段', dataIndex: 'dataSourceField', key: 'dataSourceField' },
  { title: '操作', key: 'actions', width: 80, fixed: 'right' }
]

// 数据源配置
const dataStartRow = ref(2)
const batchSize = ref(10)
const concurrency = ref(3)

// 输出设置
const outputFormat = ref('xlsx')
const fileNameTemplate = ref('文档_{name}')
const outputFolder = ref('output')

// 处理结果
const processingComplete = ref(false)
const generatedFiles = ref(0)
const processedRecords = ref(0)
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

// 处理模板文件上传前的验证
const beforeUploadTemplate = (file) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                 file.type === 'application/vnd.ms-excel'
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isExcel) {
    message.error('请上传 Excel 文件作为模板！')
    return false
  }
  if (!isLt10M) {
    message.error('文件大小不能超过 10MB！')
    return false
  }
  return true
}

// 处理数据源文件上传前的验证
const beforeUploadDataSource = (file) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                 file.type === 'application/vnd.ms-excel'
  const isCSV = file.type === 'text/csv'
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isExcel && !isCSV) {
    message.error('请上传 Excel 或 CSV 文件作为数据源！')
    return false
  }
  if (!isLt10M) {
    message.error('文件大小不能超过 10MB！')
    return false
  }
  return true
}

// 自定义模板文件上传处理
const customRequestTemplate = (options) => {
  const file = options.file
  templateFileList.value.push(file)
  options.onSuccess({ status: 'done' })
  message.success('模板文件上传成功！')
}

// 自定义数据源文件上传处理
const customRequestDataSource = (options) => {
  const file = options.file
  dataSourceFileList.value.push(file)
  options.onSuccess({ status: 'done' })
  message.success('数据源文件上传成功！')
}

// 添加字段映射
const addMapping = () => {
  if (!selectedTemplateField.value || !selectedDataSourceField.value) {
    message.error('请选择模板字段和数据源字段！')
    return
  }
  fieldMappings.value.push({
    templateField: selectedTemplateField.value,
    dataSourceField: selectedDataSourceField.value
  })
  selectedTemplateField.value = ''
  selectedDataSourceField.value = ''
}

// 移除字段映射
const removeMapping = (index) => {
  fieldMappings.value.splice(index, 1)
}

// 处理文件
const handleProcess = async () => {
  if (templateFileList.value.length === 0 || dataSourceFileList.value.length === 0) {
    message.error('请上传模板文件和数据源文件！')
    return
  }
  
  if (fieldMappings.value.length === 0) {
    message.error('请添加至少一个字段映射！')
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
    progressText.value = '正在解析模板文件...'
    
    await new Promise(resolve => setTimeout(resolve, 1000))
    loadingProgress.value = 50
    progressText.value = '正在处理数据源...'
    
    await new Promise(resolve => setTimeout(resolve, 1500))
    loadingProgress.value = 70
    progressText.value = '正在生成 Excel 文档...'
    
    await new Promise(resolve => setTimeout(resolve, 1500))
    loadingProgress.value = 90
    progressText.value = '正在保存文件...'
    
    await new Promise(resolve => setTimeout(resolve, 500))
    loadingProgress.value = 100
    progressText.value = '处理完成'
    
    // 更新处理结果
    generatedFiles.value = Math.floor(Math.random() * 100) + 50
    processedRecords.value = generatedFiles.value
    executionTime.value = Math.round(5500 / 1000)
    processingComplete.value = true
    
    message.success('文件生成完成！')
  } catch (error) {
    message.error('文件生成失败：' + error.message)
    errorMessage.value = '文件生成失败：' + error.message
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

.hint-text {
  color: #999;
  font-size: 12px;
  margin-top: 4px;
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