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
        <p>请选择要提取图片的 Excel 文件</p>
      </a-card>
      
      <!-- 步骤2：设置规则 -->
      <a-card v-if="currentStep === 1" title="步骤2：设置规则" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="图片格式">
            <a-select v-model:value="imageFormat">
              <a-select-option value="original">保持原始格式</a-select-option>
              <a-select-option value="png">PNG</a-select-option>
              <a-select-option value="jpg">JPG</a-select-option>
              <a-select-option value="webp">WebP</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="图片尺寸">
            <a-row :gutter="[16, 0]">
              <a-col :span="8">
                <a-form-item no-style label="宽度">
                  <a-input-number
                    v-model:value="imageWidth"
                    :min="0"
                    :step="1"
                    placeholder="保持原始宽度"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item no-style label="高度">
                  <a-input-number
                    v-model:value="imageHeight"
                    :min="0"
                    :step="1"
                    placeholder="保持原始高度"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item no-style label="DPI">
                  <a-select v-model:value="imageDpi">
                    <a-select-option value="96">96 DPI</a-select-option>
                    <a-select-option value="150">150 DPI</a-select-option>
                    <a-select-option value="300">300 DPI</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤3：其他选项 -->
      <a-card v-if="currentStep === 2" title="步骤3：其他选项" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="输出选项">
            <a-checkbox v-model:checked="createSubfolder">为每个文件创建子文件夹</a-checkbox>
            <a-checkbox v-model:checked="addSheetName">文件名包含工作表名称</a-checkbox>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤4：输出设置 -->
      <a-card v-if="currentStep === 3" title="步骤4：输出设置" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="输出文件夹">
            <a-input
              v-model:value="outputFolder"
              placeholder="请选择输出文件夹"
            >
              <template #addonAfter>
                <a-button type="primary" @click="selectOutputFolder">选择</a-button>
              </template>
            </a-input>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤5：开始处理 -->
      <a-card v-if="currentStep === 4" title="步骤5：处理结果" class="step-card">
        <div v-if="!isProcessing && processingResults.length > 0" class="results-container">
          <a-table
            :columns="resultColumns"
            :data-source="processingResults"
            :pagination="false"
            size="middle"
          ></a-table>
        </div>
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
          <li>设置图片格式和尺寸</li>
          <li>设置输出选项</li>
          <li>选择输出文件夹</li>
          <li>开始处理</li>
        </ol>
        
        <h2>注意事项</h2>
        <ul>
          <li>支持 .xlsx 格式文件</li>
          <li>单个文件大小限制为 10MB</li>
          <li>处理大型文件可能需要较长时间</li>
          <li>提取的图片会按顺序命名</li>
        </ul>
      </div>
    </template>
  </plugin-template>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { message, notification } from 'ant-design-vue'
import PluginTemplate from '@/components/PluginTemplate.vue'
import { runPyScript } from '@/utils/py'
import { fileSelect, folderSelect } from '@/utils/file'

// 插件基本信息
const pluginTitle = ref('提取 Excel 中的图片')
const pluginDescription = ref('从Excel文档中提取所有图片，保存为单独文件')

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
const outputFolder = ref('')

// 处理规则
const imageFormat = ref('original')
const imageWidth = ref(0) // 0表示保持原始宽度
const imageHeight = ref(0) // 0表示保持原始高度
const imageDpi = ref('96')
const createSubfolder = ref(true)
const addSheetName = ref(true)

// 处理结果
const processingResults = ref([])
const resultColumns = [
  { title: '文件名', dataIndex: 'fileName', key: 'fileName' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '提取图片数', dataIndex: 'imageCount', key: 'imageCount' },
  { title: '结果', dataIndex: 'result', key: 'result' },
]

// 处理文件上传
const handleAddFile = async () => {
  const selectedFiles = await fileSelect({
    filters: [{ name: 'Excel Files', extensions: ['xlsx', 'xls'] }],
    multiple: true,
  })
  
  if (selectedFiles && selectedFiles.length > 0) {
    files.value = [...files.value, ...selectedFiles]
  }
}

// 从文件夹导入文件
const handleImportFolder = async () => {
  const selectedFiles = await folderSelect({
    filters: [{ name: 'Excel Files', extensions: ['xlsx', 'xls'] }],
  })
  
  if (selectedFiles && selectedFiles.length > 0) {
    files.value = [...files.value, ...selectedFiles]
  }
}

// 处理更多操作
const handleMoreAction = (action) => {
  if (action === 'clear') {
    files.value = []
    message.info('已清空文件列表')
  }
}

// 处理下一步
const handleNextStep = async () => {
  if (currentStep.value === 0 && files.value.length === 0) {
    message.error('请选择要处理的文件')
    return
  }
  
  if (currentStep.value === 3 && !outputFolder.value) {
    const selectedFolder = await folderSelect()
    if (selectedFolder) {
      outputFolder.value = selectedFolder[0].path
    } else {
      message.error('请选择输出文件夹')
      return
    }
  }
  
  if (currentStep.value === 4) {
    // 开始处理
    await startProcessing()
  } else {
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
  // 帮助内容通过插槽提供
}

// 选择输出文件夹
const selectOutputFolder = async () => {
  const selectedFolder = await folderSelect()
  if (selectedFolder) {
    outputFolder.value = selectedFolder[0].path
  }
}

// 开始处理
const startProcessing = async () => {
  if (files.value.length === 0) {
    message.error('请选择要处理的文件')
    return
  }
  
  if (!outputFolder.value) {
    message.error('请选择输出文件夹')
    return
  }
  
  isProcessing.value = true
  pyodideLoading.value = true
  processingResults.value = []
  
  try {
    for (let i = 0; i < files.value.length; i++) {
      const file = files.value[i]
      loadingProgress.value = Math.round((i / files.value.length) * 30)
      progressText.value = `正在准备提取文件: ${file.name}`
      
      // 读取文件内容
      const arrayBuffer = await file.arrayBuffer()
      const buffer = new Uint8Array(arrayBuffer)
      
      // 准备Python脚本
      const scriptContent = `
from openpyxl import load_workbook
import io
import os
import sys
from PIL import Image
import base64
import uuid

# 设置工作目录
sys.path.append('.')

# 获取输入输出参数
file_data = io.BytesIO(${JSON.stringify(Array.from(buffer))})
output_path = ${JSON.stringify(outputFolder.value)}
file_name = ${JSON.stringify(file.name)}
image_format = ${JSON.stringify(imageFormat.value)}
img_width = ${JSON.stringify(imageWidth.value)}
img_height = ${JSON.stringify(imageHeight.value)}
img_dpi = ${JSON.stringify(imageDpi.value)}
create_subfolder = ${JSON.stringify(createSubfolder.value)}
add_sheet_name = ${JSON.stringify(addSheetName.value)}

# 加载工作簿
wb = load_workbook(file_data)

# 提取图片
image_count = 0

# 创建输出目录
if create_subfolder:
    base_name = os.path.splitext(file_name)[0]
    file_output_path = os.path.join(output_path, base_name)
    os.makedirs(file_output_path, exist_ok=True)
else:
    file_output_path = output_path

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    
    # 检查工作表中是否有图片
    if hasattr(ws, '_images'):
        for img_idx, img in enumerate(ws._images):
            # 获取图片数据
            img_data = img._data()
            
            # 处理图片
            pil_img = Image.open(io.BytesIO(img_data))
            
            # 调整图片尺寸
            if img_width > 0 or img_height > 0:
                if img_width > 0 and img_height > 0:
                    # 同时指定了宽度和高度
                    new_size = (img_width, img_height)
                elif img_width > 0:
                    # 只指定了宽度，按比例调整高度
                    w, h = pil_img.size
                    ratio = img_width / w
                    new_size = (img_width, int(h * ratio))
                else:
                    # 只指定了高度，按比例调整宽度
                    w, h = pil_img.size
                    ratio = img_height / h
                    new_size = (int(w * ratio), img_height)
                
                pil_img = pil_img.resize(new_size, Image.LANCZOS)
            
            # 生成文件名
            if add_sheet_name:
                img_file_name = f"{sheet_name}_image_{img_idx + 1}"
            else:
                img_file_name = f"image_{img_idx + 1}"
            
            # 确定文件扩展名
            if image_format == 'original':
                # 保持原始格式
                ext = pil_img.format.lower() if pil_img.format else 'png'
            else:
                # 使用指定格式
                ext = image_format
            
            # 保存图片
            save_file_path = os.path.join(file_output_path, f"{img_file_name}.{ext}")
            pil_img.save(save_file_path, dpi=(int(img_dpi), int(img_dpi)))
            
            image_count += 1

# 返回结果
result = {
    'status': 'success',
    'message': f'成功提取 {image_count} 张图片',
    'file_name': file_name,
    'image_count': image_count
}

print(str(result))
`
      
      pyodideLoading.value = false
      loadingProgress.value = 30 + Math.round((i / files.value.length) * 70)
      progressText.value = `正在提取图片: ${file.name}`
      
      // 执行Python脚本
      const result = await runPyScript(scriptContent)
      
      if (result.success) {
        try {
          const resultData = JSON.parse(result.output)
          processingResults.value.push({
            key: file.key,
            fileName: file.name,
            status: '成功',
            imageCount: resultData.image_count,
            result: resultData.message
          })
        } catch (e) {
          processingResults.value.push({
            key: file.key,
            fileName: file.name,
            status: '成功',
            imageCount: 0,
            result: result.output
          })
        }
      } else {
        processingResults.value.push({
          key: file.key,
          fileName: file.name,
          status: '失败',
          imageCount: 0,
          result: result.error
        })
      }
    }
    
    loadingProgress.value = 100
    progressText.value = '处理完成'
    successMessage.value = '所有文件处理完成'
    
    notification.success({
      message: '处理完成',
      description: `共处理 ${files.value.length} 个文件`,
      placement: 'topRight'
    })
  } catch (error) {
    errorMessage.value = `处理失败: ${error.message}`
    notification.error({
      message: '处理失败',
      description: error.message,
      placement: 'topRight'
    })
  } finally {
    isProcessing.value = false
    pyodideLoading.value = false
  }
}
</script>

<style scoped>
.plugin-specific-content {
  margin: 20px 0;
}

.step-card {
  margin-bottom: 20px;
}

.results-container {
  margin-top: 20px;
}
</style>