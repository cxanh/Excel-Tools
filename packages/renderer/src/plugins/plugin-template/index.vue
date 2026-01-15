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
      <!-- 这里放置插件的具体内容 -->
      <a-card title="插件功能介绍" class="plugin-info-card">
        <p>{{ pluginDescription }}</p>
      </a-card>
      
      <!-- 步骤1：文件选择 -->
      <a-card v-if="currentStep === 0" title="步骤1：选择文件" class="step-card">
        <p>请选择要处理的 Excel 文件</p>
      </a-card>
      
      <!-- 步骤2：设置规则 -->
      <a-card v-if="currentStep === 1" title="步骤2：设置规则" class="step-card">
        <p>请设置处理规则</p>
      </a-card>
      
      <!-- 步骤3：其他选项 -->
      <a-card v-if="currentStep === 2" title="步骤3：其他选项" class="step-card">
        <p>请设置其他选项</p>
      </a-card>
      
      <!-- 步骤4：输出设置 -->
      <a-card v-if="currentStep === 3" title="步骤4：输出设置" class="step-card">
        <p>请设置输出选项</p>
      </a-card>
      
      <!-- 步骤5：开始处理 -->
      <a-card v-if="currentStep === 4" title="步骤5：处理结果" class="step-card">
        <p>处理结果将显示在这里</p>
      </a-card>
    </div>
    
    <!-- 帮助文档插槽 -->
    <template #help-content>
      <div class="help-documentation">
        <h1>{{ pluginTitle }}</h1>
        
        <h2>功能介绍</h2>
        <p>{{ pluginDescription }}</p>
        
        <h2>操作步骤</h2>
        <ol>
          <li>上传 Excel 文件</li>
          <li>设置处理规则</li>
          <li>设置其他选项</li>
          <li>设置输出选项</li>
          <li>开始处理</li>
        </ol>
        
        <h2>注意事项</h2>
        <ul>
          <li>支持 .xlsx 和 .xls 格式文件</li>
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
const pluginTitle = ref('插件功能名称')
const pluginDescription = ref('插件功能描述')

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
const files = ref([])

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
  files.value = files.value.filter(file => file.key !== key)
}

// 处理显示帮助
const handleShowHelp = () => {
  message.info('显示帮助')
}
</script>

<style scoped>
.plugin-specific-content {
  margin: 20px 0;
}

.plugin-info-card {
  margin-bottom: 20px;
}

.step-card {
  margin-bottom: 20px;
}
</style>