<template>
  <div class="extract-content-plugin">
    <!-- 插件标题和描述 -->
    <div class="plugin-header">
      <h2>提取 Excel 中的指定内容</h2>
      <p>从Excel文档中提取指定内容，支持按列、按行或按条件提取</p>
    </div>

    <!-- 文件上传区域 -->
    <a-card title="上传文件" class="upload-card">
      <div class="upload-area">
        <a-upload
          v-model:file-list="fileList"
          :before-upload="handleBeforeUpload"
          :custom-request="handleUpload"
          :show-upload-list="true"
          accept=".xlsx,.xls"
        >
          <a-button type="primary">
            <UploadOutlined /> 选择 Excel 文件
          </a-button>
          <div class="upload-hint">支持 .xlsx, .xls 格式文件</div>
        </a-upload>
      </div>
    </a-card>

    <!-- 提取配置区域 -->
    <a-card v-if="selectedFile" title="提取配置" class="config-card">
      <!-- 提取类型选择 -->
      <div class="config-section">
        <a-form-item label="提取类型">
          <a-radio-group v-model:value="extractType" button-style="solid">
            <a-radio-button value="columns">按列提取</a-radio-button>
            <a-radio-button value="rows">按行提取</a-radio-button>
            <a-radio-button value="condition">按条件提取</a-radio-button>
          </a-radio-group>
        </a-form-item>
      </div>

      <!-- 工作表选择 -->
      <div class="config-section">
        <a-form-item label="选择工作表">
          <a-select
            v-model:value="selectedSheets"
            mode="multiple"
            placeholder="选择要处理的工作表"
            style="width: 100%"
          >
            <a-select-option
              v-for="sheet in availableSheets"
              :key="sheet"
              :value="sheet"
            >
              {{ sheet }}
            </a-select-option>
          </a-select>
          <div class="hint-text">留空则处理所有工作表</div>
        </a-form-item>
      </div>

      <!-- 按列提取配置 -->
      <div v-if="extractType === 'columns'" class="config-section">
        <a-form-item label="选择列">
          <a-select
            v-model:value="selectedColumns"
            mode="multiple"
            placeholder="选择要提取的列"
            style="width: 100%"
          >
            <a-select-option
              v-for="col in availableColumns"
              :key="col.index"
              :value="col.index"
            >
              {{ col.name }} ({{ col.index + 1 }})
            </a-select-option>
          </a-select>
          <div class="hint-text">例如：0 表示第一列，1 表示第二列</div>
        </a-form-item>
      </div>

      <!-- 按行提取配置 -->
      <div v-if="extractType === 'rows'" class="config-section">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="开始行">
              <a-input-number
                v-model:value="startRow"
                :min="0"
                placeholder="从第1行开始"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="结束行">
              <a-input-number
                v-model:value="endRow"
                :min="-1"
                placeholder="-1 表示到末尾"
                style="width: 100%"
              />
              <div class="hint-text">输入 -1 表示提取到文件末尾</div>
            </a-form-item>
          </a-col>
        </a-row>
      </div>

      <!-- 按条件提取配置 -->
      <div v-if="extractType === 'condition'" class="config-section">
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="条件列">
              <a-select
                v-model:value="conditionColumn"
                placeholder="选择条件列"
                style="width: 100%"
              >
                <a-select-option
                  v-for="col in availableColumns"
                  :key="col.index"
                  :value="col.index"
                >
                  {{ col.name }} ({{ col.index + 1 }})
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="条件类型">
              <a-select
                v-model:value="conditionType"
                placeholder="选择条件类型"
                style="width: 100%"
              >
                <a-select-option value="eq">等于</a-select-option>
                <a-select-option value="ne">不等于</a-select-option>
                <a-select-option value="gt">大于</a-select-option>
                <a-select-option value="lt">小于</a-select-option>
                <a-select-option value="ge">大于等于</a-select-option>
                <a-select-option value="le">小于等于</a-select-option>
                <a-select-option value="contains">包含</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="条件值">
              <a-input
                v-model:value="conditionValue"
                placeholder="输入条件值"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </div>

      <!-- 执行提取按钮 -->
      <div class="action-section">
        <a-button
          type="primary"
          :loading="isExtracting"
          @click="handleExtract"
          :disabled="!canExtract"
        >
          <PlayCircleOutlined /> 开始提取
        </a-button>
      </div>
    </a-card>

    <!-- 提取结果区域 -->
    <a-card v-if="extractResult" title="提取结果" class="result-card">
      <div class="result-header">
        <span>提取完成，共处理 {{ Object.keys(extractResult).length }} 个工作表</span>
        <a-dropdown>
          <a-button type="default">
            <DownloadOutlined /> 下载结果
            <DownOutlined />
          </a-button>
          <template #overlay>
            <a-menu @click="handleDownload">
              <a-menu-item key="csv">导出为 CSV</a-menu-item>
              <a-menu-item key="json">导出为 JSON</a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>

      <!-- 结果表格 -->
      <div class="result-content">
        <a-tabs v-model:activeKey="activeSheet" type="card">
          <a-tab-pane
            v-for="sheetName in Object.keys(extractResult)"
            :key="sheetName"
            :tab="sheetName"
          >
            <a-table
              :columns="generateColumns(sheetName)"
              :data-source="extractResult[sheetName].slice(1)"
              :pagination="{ pageSize: 10 }"
              bordered
            >
              <!-- 动态渲染列 -->
            </a-table>
          </a-tab-pane>
        </a-tabs>
      </div>
    </a-card>

    <!-- 加载状态 -->
    <a-spin v-if="isLoading" tip="正在处理...">
      <div class="loading-placeholder"></div>
    </a-spin>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { 
  UploadOutlined, 
  PlayCircleOutlined, 
  DownloadOutlined, 
  DownOutlined 
} from '@ant-design/icons-vue'
import { runPy } from '@/utils/py'

// 文件相关状态
const fileList = ref([])
const selectedFile = ref(null)
const isLoading = ref(false)

// 工作表信息
const availableSheets = ref([])
const selectedSheets = ref([])
const availableColumns = ref([])

// 提取配置
const extractType = ref('columns')
const selectedColumns = ref([])
const startRow = ref(0)
const endRow = ref(-1)
const conditionColumn = ref(0)
const conditionType = ref('eq')
const conditionValue = ref('')

// 提取状态
const isExtracting = ref(false)
const extractResult = ref(null)

// 处理文件上传前的验证
const handleBeforeUpload = (file) => {
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

  return false // 阻止自动上传，使用自定义上传
}

// 处理文件上传
const handleUpload = async (options) => {
  const file = options.file
  isLoading.value = true
  
  try {
    // 读取文件内容
    const arrayBuffer = await file.arrayBuffer()
    const fileData = new Uint8Array(arrayBuffer)
    
    // 存储选中的文件
    selectedFile.value = {
      name: file.name,
      data: fileData
    }
    
    // 解析 Excel 文件，获取工作表和列信息
    await parseExcelFile(fileData)
    
    message.success('文件上传成功！')
  } catch (error) {
    message.error('文件上传失败：' + error.message)
  } finally {
    isLoading.value = false
  }
}

// 解析 Excel 文件，获取工作表和列信息
const parseExcelFile = async (fileData) => {
  try {
    // 读取 Python 代码
    const pythonCode = await fetch('/@plugins/extract-content/worker.py').then(res => res.text())
    
    // 先获取工作表名称
    const getSheetsCode = `
import sys
import os
from openpyxl import load_workbook
from io import BytesIO

file_data = bytes.fromhex('${Array.from(fileData).map(b => b.toString(16).padStart(2, '0')).join('')}')
workbook = load_workbook(filename=BytesIO(file_data))
print(','.join(workbook.sheetnames))
    `
    
    // 执行代码获取工作表名称
    const sheetsResult = await runPy(getSheetsCode, {
      type: "other",
      data: {}
    })
    availableSheets.value = sheetsResult.logs[sheetsResult.logs.length - 2].split(',')
    
    // 获取第一个工作表的列信息
    if (availableSheets.value.length > 0) {
      const getColumnsCode = `
import sys
import os
from openpyxl import load_workbook
from io import BytesIO

file_data = bytes.fromhex('${Array.from(fileData).map(b => b.toString(16).padStart(2, '0')).join('')}')
workbook = load_workbook(filename=BytesIO(file_data))
sheet = workbook[workbook.sheetnames[0]]
header = []
for col in range(1, sheet.max_column + 1):
    cell_value = sheet.cell(row=1, column=col).value
    header.append(cell_value or f'列{col}')
print(','.join(header))
      `
      
      const columnsResult = await runPy(getColumnsCode, {
        type: "other",
        data: {}
      })
      const columnNames = columnsResult.logs[columnsResult.logs.length - 2].split(',')
      availableColumns.value = columnNames.map((name, index) => ({
        index,
        name
      }))
    }
  } catch (error) {
    console.error('解析文件失败：', error)
    throw error
  }
}

// 检查是否可以开始提取
const canExtract = computed(() => {
  if (!selectedFile.value) return false
  
  if (extractType.value === 'columns') {
    return selectedColumns.value.length > 0
  } else if (extractType.value === 'rows') {
    return startRow.value >= 0
  } else if (extractType.value === 'condition') {
    return conditionValue.value !== ''
  }
  
  return false
})

// 开始提取内容
const handleExtract = async () => {
  if (!canExtract.value) {
    message.warning('请完成提取配置！')
    return
  }
  
  isExtracting.value = true
  
  try {
    // 准备提取选项
    const settings = {
      extractType: extractType.value,
      sheetNames: selectedSheets.value,
      columns: selectedColumns.value,
      startRow: startRow.value,
      endRow: endRow.value,
      conditionColumn: conditionColumn.value,
      conditionType: conditionType.value,
      conditionValue: conditionValue.value
    }
    
    // 读取 Python 代码
    const pythonCode = await fetch('/@plugins/extract-content/worker.py').then(res => res.text())
    
    // 执行提取
    const result = await runPy(pythonCode, {
      type: "single",
      file: selectedFile.value.data,
      fileName: selectedFile.value.name,
      settings: settings
    })
    
    if (result.success) {
      extractResult.value = result.data.data
      activeSheet.value = Object.keys(result.data.data)[0] || ''
      message.success('提取完成！')
    } else {
      message.error('提取失败：' + result.error)
    }
  } catch (error) {
    console.error('提取失败：', error)
    message.error('提取失败：' + error.message)
  } finally {
    isExtracting.value = false
  }
}

// 生成表格列配置
const generateColumns = (sheetName) => {
  const data = extractResult.value[sheetName]
  if (!data || data.length === 0) return []
  
  const headers = data[0]
  return headers.map((header, index) => ({
    title: header,
    dataIndex: index.toString(),
    key: index.toString(),
  }))
}

// 下载提取结果
const handleDownload = ({ key }) => {
  if (!extractResult.value) return
  
  // 根据选择的格式导出
  if (key === 'csv') {
    exportToCSV()
  } else if (key === 'json') {
    exportToJSON()
  }
}

// 导出为 CSV
const exportToCSV = () => {
  // 简化实现，仅导出当前激活工作表
  const sheetName = activeSheet.value
  const data = extractResult.value[sheetName]
  
  if (!data || data.length === 0) return
  
  // 生成 CSV 内容
  const csvContent = data.map(row => 
    row.map(cell => `"${cell || ''}"`).join(',')
  ).join('\n')
  
  // 创建下载链接
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `${sheetName}_extract_result.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 导出为 JSON
const exportToJSON = () => {
  // 生成 JSON 内容
  const jsonContent = JSON.stringify(extractResult.value, null, 2)
  
  // 创建下载链接
  const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', 'extract_result.json')
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 当前激活的工作表
const activeSheet = ref('')
</script>

<style scoped>
.extract-content-plugin {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.plugin-header {
  text-align: center;
  margin-bottom: 24px;
}

.plugin-header h2 {
  color: #165dff;
  margin-bottom: 8px;
}

.plugin-header p {
  color: #666;
  margin: 0;
}

.upload-card,
.config-card,
.result-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.upload-hint {
  margin-top: 12px;
  color: #999;
  font-size: 14px;
}

.config-section {
  margin-bottom: 20px;
}

.hint-text {
  margin-top: 4px;
  color: #999;
  font-size: 12px;
}

.action-section {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.result-content {
  max-height: 600px;
  overflow: auto;
}

.loading-placeholder {
  height: 400px;
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .extract-content-plugin {
    padding: 12px;
  }
  
  .plugin-header h2 {
    font-size: 20px;
  }
  
  .result-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
