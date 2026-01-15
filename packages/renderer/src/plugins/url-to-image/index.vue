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
        <p>请选择要转换图片地址的 Excel 文件</p>
      </a-card>
      
      <!-- 步骤2：设置规则 -->
      <a-card v-if="currentStep === 1" title="步骤2：设置规则" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="图片地址列">
            <a-input
              v-model:value="imageUrlColumn"
              placeholder="请输入包含图片地址的列（如：A, B, C 或 1, 2, 3）"
            />
          </a-form-item>
          <a-form-item label="图片尺寸">
            <a-row :gutter="[16, 0]">
              <a-col :span="12">
                <a-form-item no-style>
                  <a-input
                    v-model:value="imageWidth"
                    placeholder="宽度（像素）"
                    type="number"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item no-style>
                  <a-input
                    v-model:value="imageHeight"
                    placeholder="高度（像素）"
                    type="number"
                  />
                </a-form-item>
              </a-col>
            </a-row>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤3：其他选项 -->
      <a-card v-if="currentStep === 2" title="步骤3：其他选项" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="处理选项">
            <a-checkbox v-model:checked="backupOriginal">备份原始文件</a-checkbox>
            <a-checkbox v-model:checked="deleteOriginalUrl">删除原始图片地址</a-checkbox>
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
          <li>设置图片地址列和图片尺寸</li>
          <li>设置处理选项（备份原始文件、删除原始地址）</li>
          <li>选择输出文件夹</li>
          <li>开始处理</li>
        </ol>
        
        <h2>注意事项</h2>
        <ul>
          <li>支持 .xlsx 格式文件</li>
          <li>单个文件大小限制为 10MB</li>
          <li>图片地址必须是有效的本地文件路径或网络URL</li>
          <li>处理大型文件可能需要较长时间</li>
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
const pluginTitle = ref('Excel 中图片地址转为图片')
const pluginDescription = ref('将单元格里的本地路径批量还原成嵌入图片')

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
const imageUrlColumn = ref('')
const imageWidth = ref(100)
const imageHeight = ref(100)
const backupOriginal = ref(true)
const deleteOriginalUrl = ref(false)

// 处理结果
const processingResults = ref([])
const resultColumns = [
  { title: '文件名', dataIndex: 'fileName', key: 'fileName' },
  { title: '状态', dataIndex: 'status', key: 'status' },
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
    message.error('请先选择要处理的文件')
    return
  }
  
  if (currentStep.value === 1 && !imageUrlColumn.value) {
    message.error('请输入图片地址列')
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
    message.error('请先选择要处理的文件')
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
      progressText.value = `正在准备处理文件: ${file.name}`
      
      // 读取文件内容
      const arrayBuffer = await file.arrayBuffer()
      const buffer = new Uint8Array(arrayBuffer)
      
      // 准备Python脚本
      const scriptContent = `
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as OpenpyxlImage
import io
import os
import sys
import requests
from PIL import Image as PILImage

# 设置工作目录
sys.path.append('.')

# 获取输入输出参数
file_data = io.BytesIO(${JSON.stringify(Array.from(buffer))})
output_path = ${JSON.stringify(outputFolder.value)}
file_name = ${JSON.stringify(file.name)}
image_col = ${JSON.stringify(imageUrlColumn.value)}
img_width = ${JSON.stringify(imageWidth.value)}
img_height = ${JSON.stringify(imageHeight.value)}
backup_original = ${JSON.stringify(backupOriginal.value)}
delete_url = ${JSON.stringify(deleteOriginalUrl.value)}

# 加载工作簿
wb = load_workbook(file_data)

# 处理每个工作表
converted_images_count = 0

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    
    # 确定图片地址列索引
    if image_col.isalpha():
        # 字母列名（A, B, C）
        col_idx = ord(image_col.upper()) - ord('A')
    else:
        # 数字列名（1, 2, 3）
        col_idx = int(image_col) - 1
    
    # 获取所有行
    rows = list(ws.iter_rows())
    
    for row_idx, row in enumerate(rows):
        if col_idx < len(row):
            cell = row[col_idx]
            image_url = cell.value
            
            if image_url and isinstance(image_url, str):
                image_url = image_url.strip()
                if image_url:
                    try:
                        # 尝试加载图片
                        if image_url.startswith('http://') or image_url.startswith('https://'):
                            # 网络图片
                            response = requests.get(image_url)
                            img_data = io.BytesIO(response.content)
                        else:
                            # 本地图片
                            if os.path.exists(image_url):
                                with open(image_url, 'rb') as f:
                                    img_data = io.BytesIO(f.read())
                            else:
                                continue
                        
                        # 调整图片尺寸
                        pil_img = PILImage.open(img_data)
                        pil_img = pil_img.resize((img_width, img_height), PILImage.LANCZOS)
                        
                        # 保存调整后的图片到内存
                        resized_img_data = io.BytesIO()
                        pil_img.save(resized_img_data, format=pil_img.format)
                        resized_img_data.seek(0)
                        
                        # 创建Openpyxl图片对象
                        img = OpenpyxlImage(resized_img_data)
                        
                        # 在当前单元格嵌入图片
                        img.anchor = cell.coordinate
                        ws.add_image(img)
                        
                        # 如果需要删除原始URL
                        if delete_url:
                            cell.value = None
                        
                        converted_images_count += 1
                    except Exception as e:
                        # 忽略单个图片处理错误，继续处理其他图片
                        continue

# 保存文件
save_path = os.path.join(output_path, file_name)
wb.save(save_path)

# 返回结果
result = {
    'status': 'success',
    'message': f'成功转换 {converted_images_count} 张图片',
    'file_name': file_name
}

print(str(result))
`
      
      pyodideLoading.value = false
      loadingProgress.value = 30 + Math.round((i / files.value.length) * 70)
      progressText.value = `正在处理文件: ${file.name}`
      
      // 执行Python脚本
      const result = await runPyScript(scriptContent)
      
      if (result.success) {
        try {
          const resultData = JSON.parse(result.output)
          processingResults.value.push({
            key: file.key,
            fileName: file.name,
            status: '成功',
            result: resultData.message
          })
        } catch (e) {
          processingResults.value.push({
            key: file.key,
            fileName: file.name,
            status: '成功',
            result: result.output
          })
        }
      } else {
        processingResults.value.push({
          key: file.key,
          fileName: file.name,
          status: '失败',
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