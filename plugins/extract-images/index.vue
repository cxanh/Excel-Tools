<template>
  <PluginTemplate
    plugin-title="提取 Excel 文档中的图片"
    info-message="从Excel文档中提取所有图片并保存为单独文件"
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
        message="提取说明"
        description="支持从Excel文档中提取所有图片，包括嵌入在工作表中的图片。提取的图片将保持原始格式或转换为PNG格式。"
        type="info"
        show-icon
        class="mb-4"
      />
      
      <div class="settings-section">
        <h3 class="section-title">提取设置</h3>
        
        <a-form-item label="输出格式">
          <a-select v-model:value="outputFormat" placeholder="请选择输出格式">
            <a-select-option value="original">保持原始格式</a-select-option>
            <a-select-option value="png">统一转换为PNG</a-select-option>
            <a-select-option value="jpg">统一转换为JPG</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item label="图片命名规则">
          <a-select v-model:value="namingRule" placeholder="请选择图片命名规则">
            <a-select-option value="sheet_index">工作表_序号</a-select-option>
            <a-select-option value="original">原始文件名</a-select-option>
            <a-select-option value="index">仅序号</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-alert
          message="提示"
          description="提取的图片将以单个文件形式返回，可直接下载使用。"
          type="success"
          show-icon
          class="mt-4"
        />
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
const outputFormat = ref('original')
const namingRule = ref('sheet_index')

// 处理文件
const processFiles = async () => {
  const files = pluginTemplate.value.files
  if (files.length === 0) {
    return
  }
  
  const script = await getPythonScript('extract-images')
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
          outputFormat: outputFormat.value,
          namingRule: namingRule.value
        }
      })
      
      if (result.success) {
        // 处理提取结果
        if (result.results && result.results.length > 0) {
          // 对于每个提取的图片，调用处理完成回调
          for (const imageResult of result.results) {
            // 根据图片格式设置MIME类型
            let mimeType = 'image/png'
            if (imageResult.format === 'jpg' || imageResult.format === 'jpeg') {
              mimeType = 'image/jpeg'
            } else if (imageResult.format === 'gif') {
              mimeType = 'image/gif'
            } else if (imageResult.format === 'bmp') {
              mimeType = 'image/bmp'
            }
            
            pluginTemplate.value.handleFileProcessed(
              {
                ...file,
                name: imageResult.file_name,
                mimeType: mimeType
              },
              {
                ...result,
                buffer: imageResult.buffer
              }
            )
          }
        } else {
          pluginTemplate.value.handleFileError(file, '未提取到任何图片')
        }
      } else {
        pluginTemplate.value.handleFileError(file, result.error || '提取失败')
      }
    } catch (error) {
      pluginTemplate.value.handleFileError(file, error.message || '提取失败')
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