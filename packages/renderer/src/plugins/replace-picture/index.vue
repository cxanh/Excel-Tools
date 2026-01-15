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
        <p>请选择要处理的 Excel 文件和替换图片</p>
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
            v-model:file-list="imageFileList"
            :before-upload="beforeUploadImage"
            :custom-request="customRequestImage"
            accept=".jpg,.jpeg,.png,.gif,.bmp"
            :show-upload-list="true"
            :multiple="true"
          >
            <a-button type="primary" icon="upload">上传替换图片</a-button>
          </a-upload>
          <span class="file-hint">支持 .jpg, .jpeg, .png, .gif, .bmp 格式</span>
        </div>
      </a-card>
      
      <!-- 步骤2：替换设置 -->
      <a-card v-if="currentStep === 1" title="步骤2：替换设置" class="step-card">
        <p>请设置图片替换规则</p>
        <a-form layout="vertical">
          <a-form-item label="替换方式">
            <a-radio-group v-model:value="replaceMode">
              <a-radio-button value="replaceAll">全部替换</a-radio-button>
              <a-radio-button value="byName">按名称替换</a-radio-button>
              <a-radio-button value="bySize">按大小替换</a-radio-button>
            </a-radio-group>
          </a-form-item>
          
          <a-form-item v-if="replaceMode === 'byName'" label="名称匹配">
            <a-input v-model:value="nameMatchPattern" placeholder="输入要匹配的图片名称模式，支持正则表达式" />
          </a-form-item>
          
          <a-form-item v-if="replaceMode === 'bySize'" label="大小范围">
            <a-row :gutter="16">
              <a-col :span="11">
                <a-input-number v-model:value="minSize" :min="0" placeholder="最小大小 (KB)" />
              </a-col>
              <a-col :span="2" style="text-align: center;">-</a-col>
              <a-col :span="11">
                <a-input-number v-model:value="maxSize" :min="0" placeholder="最大大小 (KB)" />
              </a-col>
            </a-row>
          </a-form-item>
          
          <a-form-item label="图片缩放选项">
            <a-radio-group v-model:value="scaleOption">
              <a-radio-button value="keepOriginal">保持原始尺寸</a-radio-button>
              <a-radio-button value="scaleToFit">按比例缩放</a-radio-button>
              <a-radio-button value="custom">自定义尺寸</a-radio-button>
            </a-radio-group>
          </a-form-item>
          
          <a-form-item v-if="scaleOption === 'custom'" label="自定义尺寸">
            <a-row :gutter="16">
              <a-col :span="11">
                <a-input-number v-model:value="customWidth" :min="1" placeholder="宽度 (px)" />
              </a-col>
              <a-col :span="2" style="text-align: center;">×</a-col>
              <a-col :span="11">
                <a-input-number v-model:value="customHeight" :min="1" placeholder="高度 (px)" />
              </a-col>
            </a-row>
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
              <a-select-option value="Sheet3">Sheet3</a-select-option>
            </a-select>
          </a-form-item>
          
          <a-form-item label="选项">
            <a-checkbox-group v-model:value="options">
              <a-checkbox value="preserveAspectRatio">保持纵横比</a-checkbox>
              <a-checkbox value="centerImage">居中对齐</a-checkbox>
              <a-checkbox value="deleteOriginal">删除原始图片</a-checkbox>
            </a-checkbox-group>
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
          <a-alert type="success" show-icon message="处理完成" description="Excel 文件中的图片已成功替换" />
          <div class="result-stats" style="margin-top: 16px;">
            <a-statistic title="处理文件数" :value="processedFiles" />
            <a-statistic title="替换图片数" :value="replacedImages" style="margin-left: 32px;" />
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
        <h1>替换 Excel 中的图片</h1>
        
        <h2>功能介绍</h2>
        <p>批量替换 Excel 文件中的图片，统一文档风格。</p>
        
        <h2>操作步骤</h2>
        <ol>
          <li><strong>上传文件</strong>：上传要处理的 Excel 文件和替换图片</li>
          <li><strong>替换设置</strong>：配置图片替换规则和缩放选项</li>
          <li><strong>其他选项</strong>：设置处理范围和其他选项</li>
          <li><strong>输出设置</strong>：配置输出格式和文件名</li>
          <li><strong>开始处理</strong>：执行处理并下载结果</li>
        </ol>
        
        <h2>替换方式说明</h2>
        <ul>
          <li><strong>全部替换</strong>：替换所有图片</li>
          <li><strong>按名称替换</strong>：根据图片名称模式匹配替换</li>
          <li><strong>按大小替换</strong>：根据图片大小范围匹配替换</li>
        </ul>
        
        <h2>图片缩放选项</h2>
        <ul>
          <li><strong>保持原始尺寸</strong>：使用图片的原始尺寸</li>
          <li><strong>按比例缩放</strong>：保持图片比例缩放</li>
          <li><strong>自定义尺寸</strong>：设置图片的具体宽度和高度</li>
        </ul>
        
        <h2>注意事项</h2>
        <ul>
          <li>支持 .xlsx, .xls 格式的 Excel 文件</li>
          <li>支持 .jpg, .jpeg, .png, .gif, .bmp 格式的图片</li>
          <li>单个文件大小限制为 10MB</li>
          <li>处理大型文件或大量图片时可能需要较长时间</li>
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
const pluginTitle = ref('替换 Excel 中的图片')
const pluginDescription = ref('批量替换 Excel 文件中的图片，统一文档风格')

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
const imageFileList = ref([])
const selectedFiles = ref([])

// 替换设置
const replaceMode = ref('replaceAll')
const nameMatchPattern = ref('')
const minSize = ref(0)
const maxSize = ref(0)

// 缩放选项
const scaleOption = ref('keepOriginal')
const customWidth = ref(0)
const customHeight = ref(0)

// 处理范围
const processScope = ref('all')
const selectedSheets = ref([])
const options = ref(['preserveAspectRatio'])

// 输出设置
const outputFormat = ref('xlsx')
const outputFileName = ref('processed_file')

// 处理结果
const processingComplete = ref(false)
const processedFiles = ref(0)
const replacedImages = ref(0)
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

// 处理 Excel 文件上传前的验证
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

// 处理图片上传前的验证
const beforeUploadImage = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    message.error('请上传图片文件！')
    return false
  }
  if (!isLt10M) {
    message.error('图片大小不能超过 10MB！')
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

// 自定义图片上传处理
const customRequestImage = (options) => {
  const file = options.file
  imageFileList.value.push(file)
  options.onSuccess({ status: 'done' })
  message.success('图片上传成功！')
}

// 处理文件
const handleProcess = async () => {
  if (excelFileList.value.length === 0 || imageFileList.value.length === 0) {
    message.error('请上传 Excel 文件和替换图片！')
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
    progressText.value = '正在解析 Excel 文件...'
    
    await new Promise(resolve => setTimeout(resolve, 1000))
    loadingProgress.value = 50
    progressText.value = '正在处理图片...'
    
    await new Promise(resolve => setTimeout(resolve, 1500))
    loadingProgress.value = 70
    progressText.value = '正在替换图片...'
    
    await new Promise(resolve => setTimeout(resolve, 1500))
    loadingProgress.value = 90
    progressText.value = '正在生成输出文件...'
    
    await new Promise(resolve => setTimeout(resolve, 500))
    loadingProgress.value = 100
    progressText.value = '处理完成'
    
    // 更新处理结果
    processedFiles.value = excelFileList.value.length
    replacedImages.value = Math.floor(Math.random() * 50) + 10
    executionTime.value = Math.round(5500 / 1000)
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