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
        <p>请选择要添加页眉页脚的 Excel 文件</p>
      </a-card>
      
      <!-- 步骤2：页眉设置 -->
      <a-card v-if="currentStep === 1" title="步骤2：页眉设置" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="页眉内容">
            <a-tabs v-model:activeKey="headerTab">
              <a-tab-pane key="left" tab="左侧">
                <a-input
                  v-model:value="header.left"
                  placeholder="请输入左侧页眉内容"
                />
              </a-tab-pane>
              <a-tab-pane key="center" tab="中间">
                <a-input
                  v-model:value="header.center"
                  placeholder="请输入中间页眉内容"
                />
              </a-tab-pane>
              <a-tab-pane key="right" tab="右侧">
                <a-input
                  v-model:value="header.right"
                  placeholder="请输入右侧页眉内容"
                />
              </a-tab-pane>
            </a-tabs>
          </a-form-item>
          <a-form-item label="页眉选项">
            <a-checkbox v-model:checked="headerOptions.differentOddEven">奇偶页不同</a-checkbox>
            <a-checkbox v-model:checked="headerOptions.differentFirst">首页不同</a-checkbox>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤3：页脚设置 -->
      <a-card v-if="currentStep === 2" title="步骤3：页脚设置" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="页脚内容">
            <a-tabs v-model:activeKey="footerTab">
              <a-tab-pane key="left" tab="左侧">
                <a-input
                  v-model:value="footer.left"
                  placeholder="请输入左侧页脚内容"
                />
              </a-tab-pane>
              <a-tab-pane key="center" tab="中间">
                <a-input
                  v-model:value="footer.center"
                  placeholder="请输入中间页脚内容"
                />
              </a-tab-pane>
              <a-tab-pane key="right" tab="右侧">
                <a-input
                  v-model:value="footer.right"
                  placeholder="请输入右侧页脚内容"
                />
              </a-tab-pane>
            </a-tabs>
          </a-form-item>
          <a-form-item label="快捷插入">
            <a-button-group>
              <a-button @click="insertHeaderFooterItem('&[页码]')">页码</a-button>
              <a-button @click="insertHeaderFooterItem('&[总页数]')">总页数</a-button>
              <a-button @click="insertHeaderFooterItem('&[日期]')">日期</a-button>
              <a-button @click="insertHeaderFooterItem('&[时间]')">时间</a-button>
              <a-button @click="insertHeaderFooterItem('&[文件名]')">文件名</a-button>
            </a-button-group>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤4：其他选项 -->
      <a-card v-if="currentStep === 3" title="步骤4：其他选项" class="step-card">
        <a-form layout="vertical">
          <a-form-item label="处理范围">
            <a-radio-group v-model:value="processingScope">
              <a-radio value="all">整个工作簿</a-radio>
              <a-radio value="selected">指定工作表</a-radio>
            </a-radio-group>
          </a-form-item>
          <a-form-item v-if="processingScope === 'selected'" label="工作表名称">
            <a-input
              v-model:value="targetSheet"
              placeholder="请输入要处理的工作表名称"
            />
          </a-form-item>
          <a-form-item label="输出选项">
            <a-checkbox v-model:checked="backupOriginal">备份原始文件</a-checkbox>
          </a-form-item>
        </a-form>
      </a-card>
      
      <!-- 步骤5：输出设置 -->
      <a-card v-if="currentStep === 4" title="步骤5：输出设置" class="step-card">
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
      
      <!-- 步骤6：开始处理 -->
      <a-card v-if="currentStep === 5" title="步骤6：处理结果" class="step-card">
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
        
        <h2>支持的页眉页脚代码</h2>
        <ul>
          <li>&[页码] - 当前页码</li>
          <li>&[总页数] - 总页数</li>
          <li>&[日期] - 当前日期</li>
          <li>&[时间] - 当前时间</li>
          <li>&[文件名] - 文件名</li>
          <li>&[工作表名] - 工作表名称</li>
          <li>&L - 左对齐</li>
          <li>&C - 居中对齐</li>
          <li>&R - 右对齐</li>
        </ul>
        
        <h2>操作步骤</h2>
        <ol>
          <li>上传 Excel 文件</li>
          <li>设置页眉内容和选项</li>
          <li>设置页脚内容</li>
          <li>设置处理范围和输出选项</li>
          <li>选择输出文件夹</li>
          <li>开始处理</li>
        </ol>
        
        <h2>注意事项</h2>
        <ul>
          <li>支持 .xlsx 格式文件</li>
          <li>单个文件大小限制为 10MB</li>
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
const pluginTitle = ref('添加/修改 Excel 页眉页脚')
const pluginDescription = ref('为 Excel 文件批量添加或修改页眉页脚，支持自定义内容和样式')

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
const processingScope = ref('all')
const targetSheet = ref('')
const backupOriginal = ref(true)

// 页眉页脚设置
const header = reactive({
  left: '',
  center: '',
  right: ''
})

const footer = reactive({
  left: '',
  center: '',
  right: ''
})

const headerOptions = reactive({
  differentOddEven: false,
  differentFirst: false
})

// 当前激活的标签页
const headerTab = ref('left')
const footerTab = ref('left')

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
    message.error('请选择要处理的文件')
    return
  }
  
  if (currentStep.value === 4 && !outputFolder.value) {
    const selectedFolder = await folderSelect()
    if (selectedFolder) {
      outputFolder.value = selectedFolder[0].path
    } else {
      message.error('请选择输出文件夹')
      return
    }
  }
  
  if (currentStep.value === 5) {
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

// 插入页眉页脚项目
const insertHeaderFooterItem = (item) => {
  if (currentStep.value === 1) {
    // 页眉设置
    if (headerTab.value === 'left') {
      header.left += item
    } else if (headerTab.value === 'center') {
      header.center += item
    } else {
      header.right += item
    }
  } else if (currentStep.value === 2) {
    // 页脚设置
    if (footerTab.value === 'left') {
      footer.left += item
    } else if (footerTab.value === 'center') {
      footer.center += item
    } else {
      footer.right += item
    }
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
      progressText.value = `正在准备处理文件: ${file.name}`
      
      // 读取文件内容
      const arrayBuffer = await file.arrayBuffer()
      const buffer = new Uint8Array(arrayBuffer)
      
      loadingProgress.value = 30 + Math.round((i / files.value.length) * 40)
      progressText.value = `正在添加页眉页脚: ${file.name}`
      
      // 准备Python脚本
      const scriptContent = `
from openpyxl import load_workbook
import io
import os
import sys

# 设置工作目录
sys.path.append('.')

# 获取输入输出参数
file_data = io.BytesIO(${JSON.stringify(Array.from(buffer))})
output_path = ${JSON.stringify(outputFolder.value)}
file_name = ${JSON.stringify(file.name)}
processing_scope = ${JSON.stringify(processingScope.value)}
target_sheet = ${JSON.stringify(targetSheet.value)}
header_left = ${JSON.stringify(header.left)}
header_center = ${JSON.stringify(header.center)}
header_right = ${JSON.stringify(header.right)}
footer_left = ${JSON.stringify(footer.left)}
footer_center = ${JSON.stringify(footer.center)}
footer_right = ${JSON.stringify(footer.right)}
different_odd_even = ${JSON.stringify(headerOptions.differentOddEven)}
different_first = ${JSON.stringify(headerOptions.differentFirst)}

# 加载工作簿
wb = load_workbook(file_data)

# 确定要处理的工作表
if processing_scope == 'all':
    sheet_names = wb.sheetnames
elif processing_scope == 'selected' and target_sheet:
    sheet_names = [target_sheet] if target_sheet in wb.sheetnames else []
else:
    sheet_names = []

# 为每个工作表设置页眉页脚
for sheet_name in sheet_names:
    ws = wb[sheet_name]
    
    # 构建页眉页脚字符串
    header_str = f"&L{header_left}&C{header_center}&R{header_right}"
    footer_str = f"&L{footer_left}&C{footer_center}&R{footer_right}"
    
    # 设置页眉页脚
    ws.header_footer.left_header = header_left
    ws.header_footer.center_header = header_center
    ws.header_footer.right_header = header_right
    ws.header_footer.left_footer = footer_left
    ws.header_footer.center_footer = footer_center
    ws.header_footer.right_footer = footer_right
    
    # 设置页眉页脚选项
    ws.header_footer.differentOddEven = different_odd_even
    ws.header_footer.differentFirst = different_first

# 保存文件
save_path = os.path.join(output_path, file_name)
wb.save(save_path)

# 返回结果
result = {
    'status': 'success',
    'message': f'成功为 {len(sheet_names)} 个工作表添加页眉页脚',
    'file_name': file_name
}

print(str(result))
`
      
      // 执行Python脚本
      const result = await runPyScript(scriptContent)
      
      loadingProgress.value = 70 + Math.round((i / files.value.length) * 30)
      progressText.value = `正在保存结果: ${file.name}`
      
      if (result.success) {
        try {
          const resultData = JSON.parse(result.output)
          processingResults.value.push({
            key: file.key,
            fileName: resultData.file_name,
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