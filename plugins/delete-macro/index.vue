<template>
  <PluginTemplate
    plugin-title="删除 Excel 中的宏"
    info-message="删除Excel文件中的所有宏和VBA代码"
    :current-step="currentStep"
    @add-file="handleAddFile"
    @import-folder="handleImportFromFolder"
    @more-action="handleMoreAction"
    @next-step="handleNextStep"
    @prev-step="handlePrevStep"
    @remove-file="handleRemoveFile"
    ref="pluginTemplate"
  >
    <!-- 插件内容 -->
    <div class="plugin-content">
      <a-alert
        message="注意事项"
        description="此插件将删除Excel文件中的所有宏和VBA代码，操作不可逆，请谨慎使用。"
        type="info"
        show-icon
        class="mb-4"
      />
      
      <div class="settings-section">
        <h3 class="section-title">处理设置</h3>
        <a-checkbox v-model:checked="deleteAllMacros" disabled>删除所有宏和VBA代码</a-checkbox>
      </div>
    </div>
  </PluginTemplate>
</template>

<script setup>
import { ref } from 'vue'
import PluginTemplate from '@/components/PluginTemplate.vue'
import { runPy } from '@/utils/py'
import { getPythonScript } from '@/utils/plugin'

const currentStep = ref(1)
const pluginTemplate = ref(null)
const deleteAllMacros = ref(true)

// 处理文件
const processFiles = async () => {
  const files = pluginTemplate.value.files
  if (files.length === 0) {
    return
  }
  
  const script = await getPythonScript('delete-macro')
  if (!script) {
    return
  }
  
  for (const file of files) {
    try {
      const result = await runPy(script, {
        type: 'single',
        file: file.file,
        fileName: file.name,
        settings: {
          deleteAllMacros: deleteAllMacros.value
        }
      })
      
      if (result.success) {
        pluginTemplate.value.handleFileProcessed(file, result)
      } else {
        pluginTemplate.value.handleFileError(file, result.error || '处理失败')
      }
    } catch (error) {
      pluginTemplate.value.handleFileError(file, error.message || '处理失败')
    }
  }
}

// 下一步处理
const handleNextStep = async () => {
  if (currentStep.value === 1) {
    await processFiles()
  }
  currentStep.value++
}

// 其他方法
const handleAddFile = (files) => {
  pluginTemplate.value.addFiles(files)
}

const handleImportFromFolder = () => {
  pluginTemplate.value.importFromFolder()
}

const handleMoreAction = () => {
  pluginTemplate.value.showMoreActions()
}

const handlePrevStep = () => {
  currentStep.value--
}

const handleRemoveFile = (index) => {
  pluginTemplate.value.removeFile(index)
}
</script>

<style scoped>
.plugin-content {
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.settings-section {
  margin-top: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #333;
}
</style>