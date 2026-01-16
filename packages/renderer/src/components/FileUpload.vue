<template>
  <div class="file-upload">
    <a-upload-dragger
      v-model:fileList="fileList"
      :multiple="multiple"
      :before-upload="handleBeforeUpload"
      :accept="accept"
      @remove="handleRemove"
    >
      <p class="ant-upload-drag-icon">
        <InboxOutlined />
      </p>
      <p class="ant-upload-text">
        点击或拖拽文件到此区域上传
      </p>
      <p class="ant-upload-hint">
        {{ hint || '支持.xlsx、.xls、.csv格式文件' }}
      </p>
    </a-upload-dragger>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { InboxOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import type { UploadProps } from 'ant-design-vue'
import { validateFile } from '@/utils/file-service'

interface Props {
  multiple?: boolean
  accept?: string
  hint?: string
}

const props = withDefaults(defineProps<Props>(), {
  multiple: false,
  accept: '.xlsx,.xls,.csv',
  hint: ''
})

const emit = defineEmits<{
  (e: 'change', files: File[]): void
  (e: 'remove', file: File): void
}>()

const fileList = ref<UploadProps['fileList']>([])

const handleBeforeUpload: UploadProps['beforeUpload'] = (file) => {
  // 验证文件
  const validation = validateFile(file as File)
  
  if (!validation.valid) {
    message.error(validation.error || '文件验证失败')
    return false
  }

  // 添加到文件列表
  fileList.value = fileList.value || []
  
  if (!props.multiple) {
    fileList.value = []
  }

  // 触发change事件
  const files = [...(fileList.value || []).map(f => f.originFileObj as File), file as File]
  emit('change', files)

  // 阻止自动上传
  return false
}

const handleRemove: UploadProps['onRemove'] = (file) => {
  emit('remove', file.originFileObj as File)
}

// 暴露方法给父组件
defineExpose({
  clear: () => {
    fileList.value = []
  },
  openFileDialog: () => {
    // 触发文件选择对话框
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = props.accept
    input.multiple = props.multiple
    input.onchange = (e) => {
      const target = e.target as HTMLInputElement
      if (target.files) {
        const files = Array.from(target.files)
        files.forEach(file => {
          handleBeforeUpload(file)
        })
      }
    }
    input.click()
  }
})
</script>

<style scoped>
.file-upload {
  width: 100%;
}
</style>
