<template>
  <div
    class="excel-drop"
    :class="{ 'drag-over': isDragging }"
    @dragover.prevent="handleDragOver"
    @dragleave.prevent="handleDragLeave"
    @drop.prevent="handleDrop"
    @click="handleClick"
  >
    <input
      ref="fileInput"
      type="file"
      accept=".xlsx,.xls"
      style="display: none;"
      @change="handleFileChange"
    />
    <a-upload
      :show-upload-list="false"
      :before-upload="handleBeforeUpload"
      accept=".xlsx,.xls"
    >
      <div style="padding: 24px; text-align: center;">
        <CloudUploadOutlined style="font-size: 48px; color: #165DFF;" />
        <p style="margin: 16px 0;">拖拽 Excel 文件到此处，或点击上传</p>
        <a-button type="primary">选择文件</a-button>
      </div>
    </a-upload>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { CloudUploadOutlined } from '@ant-design/icons-vue'

const emit = defineEmits(['file'])
const isDragging = ref(false)
const fileInput = ref(null)

const handleDragOver = () => {
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

const handleDrop = (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) {
    emitFile(file)
  }
}

const handleClick = () => {
  fileInput.value?.click()
}

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    emitFile(file)
    // 清空 input，允许重复上传同一文件
    e.target.value = ''
  }
}

const handleBeforeUpload = (file) => {
  emitFile(file)
  return false // 阻止默认上传行为
}

const emitFile = (file) => {
  if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
    emit('file', file)
  } else {
    // 可以添加错误提示
    console.error('请上传 Excel 文件 (.xlsx, .xls)')
  }
}
</script>

<style scoped>
.excel-drop {
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  transition: all 0.3s;
  cursor: pointer;
}

.excel-drop:hover {
  border-color: #165DFF;
}

.excel-drop.drag-over {
  border-color: #165DFF;
  background-color: rgba(22, 93, 255, 0.04);
}
</style>