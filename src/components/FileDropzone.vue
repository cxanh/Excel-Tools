<template>
  <div 
    class="file-dropzone"
    :class="{ 
      'is-dragging': isDragging,
      'has-file': hasFile,
      'is-disabled': disabled
    }"
    @dragenter.prevent="handleDragEnter"
    @dragover.prevent="handleDragOver"
    @dragleave.prevent="handleDragLeave"
    @drop.prevent="handleDrop"
    @click="triggerFileInput"
  >
    <input
      ref="fileInput"
      type="file"
      :accept="accept"
      :multiple="multiple"
      @change="handleFileSelect"
      class="file-input-hidden"
    />
    
    <div class="dropzone-content">
      <div v-if="!hasFile" class="dropzone-empty">
        <div class="dropzone-icon">
          <span v-if="!isDragging">📁</span>
          <span v-else class="drop-animation">📂</span>
        </div>
        <h3 class="dropzone-title">
          {{ isDragging ? '释放鼠标开始解析' : title }}
        </h3>
        <p class="dropzone-description">
          {{ isDragging ? '支持 .xlsx, .xls, .csv 格式' : description }}
        </p>
        <button 
          v-if="!isDragging" 
          class="browse-btn"
          @click.stop="triggerFileInput"
          :disabled="disabled"
        >
          或点击浏览文件
        </button>
      </div>
      
      <div v-else class="dropzone-file-info">
        <div class="file-icon">📄</div>
        <div class="file-details">
          <h4 class="file-name">{{ fileName }}</h4>
          <p class="file-size">{{ formatFileSize(fileSize) }}</p>
        </div>
        <button 
          class="remove-btn"
          @click.stop="clearFile"
          :disabled="disabled"
        >
          ✕
        </button>
      </div>
    </div>
    
    <div v-if="isDragging" class="drag-overlay">
      <div class="drag-overlay-content">
        <div class="pulse-circle"></div>
        <span class="drag-text">释放文件</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'FileDropzone',
  props: {
    title: {
      type: String,
      default: '拖拽 Excel 文件到这里'
    },
    description: {
      type: String,
      default: '支持 .xlsx, .xls, .csv 格式'
    },
    accept: {
      type: String,
      default: '.xlsx,.xls,.csv'
    },
    multiple: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    maxSize: {
      type: Number,
      default: 100 * 1024 * 1024 // 100MB
    }
  },
  emits: ['file-selected', 'file-error', 'file-cleared'],
  data() {
    return {
      isDragging: false,
      dragCounter: 0,
      fileName: '',
      fileSize: 0,
      filePath: ''
    }
  },
  computed: {
    hasFile(): boolean {
      return this.fileName !== ''
    }
  },
  methods: {
    handleDragEnter(e: DragEvent) {
      if (this.disabled) return
      this.dragCounter++
      if (this.dragCounter === 1) {
        this.isDragging = true
      }
    },
    handleDragOver(e: DragEvent) {
      if (this.disabled) return
      e.dataTransfer!.dropEffect = 'copy'
    },
    handleDragLeave(e: DragEvent) {
      if (this.disabled) return
      this.dragCounter--
      if (this.dragCounter === 0) {
        this.isDragging = false
      }
    },
    handleDrop(e: DragEvent) {
      if (this.disabled) return
      this.isDragging = false
      this.dragCounter = 0
      
      const files = e.dataTransfer?.files
      if (files && files.length > 0) {
        this.processFile(files[0])
      }
    },
    triggerFileInput() {
      if (this.disabled) return
      const input = this.$refs.fileInput as HTMLInputElement
      input.click()
    },
    handleFileSelect(e: Event) {
      const input = e.target as HTMLInputElement
      const files = input.files
      if (files && files.length > 0) {
        this.processFile(files[0])
      }
    },
    processFile(file: File) {
      // 验证文件类型
      const acceptedTypes = this.accept.split(',').map(t => t.trim())
      const fileExt = '.' + file.name.split('.').pop()?.toLowerCase()
      
      if (!acceptedTypes.includes(fileExt)) {
        this.$emit('file-error', {
          type: 'invalid-type',
          message: `不支持的文件格式: ${fileExt}`,
          file
        })
        return
      }
      
      // 验证文件大小
      if (file.size > this.maxSize) {
        this.$emit('file-error', {
          type: 'too-large',
          message: `文件过大: ${this.formatFileSize(file.size)} (最大 ${this.formatFileSize(this.maxSize)})`,
          file
        })
        return
      }
      
      // 保存文件信息
      this.fileName = file.name
      this.fileSize = file.size
      
      // 获取文件路径（Electron 环境）
      if ((file as any).path) {
        this.filePath = (file as any).path
      }
      
      // 触发事件
      this.$emit('file-selected', {
        file,
        name: file.name,
        size: file.size,
        path: this.filePath || file.name
      })
    },
    clearFile() {
      if (this.disabled) return
      this.fileName = ''
      this.fileSize = 0
      this.filePath = ''
      
      // 清空 input
      const input = this.$refs.fileInput as HTMLInputElement
      if (input) {
        input.value = ''
      }
      
      this.$emit('file-cleared')
    },
    formatFileSize(bytes: number): string {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
    }
  }
})
</script>

<style scoped>
.file-dropzone {
  position: relative;
  border: 2px dashed #cbd5e0;
  border-radius: 16px;
  padding: 40px;
  background: #f8f9fb;
  transition: all 0.3s ease;
  cursor: pointer;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.file-dropzone:hover:not(.is-disabled) {
  border-color: #667eea;
  background: #f0f3f7;
}

.file-dropzone.is-dragging {
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border-width: 3px;
  transform: scale(1.02);
}

.file-dropzone.has-file {
  border-style: solid;
  border-color: #10b981;
  background: #10b98108;
}

.file-dropzone.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.file-input-hidden {
  display: none;
}

.dropzone-content {
  width: 100%;
  text-align: center;
  position: relative;
  z-index: 1;
}

.dropzone-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.dropzone-icon {
  font-size: 64px;
  margin-bottom: 8px;
  transition: transform 0.3s ease;
}

.file-dropzone:hover .dropzone-icon {
  transform: scale(1.1);
}

.drop-animation {
  display: inline-block;
  animation: bounce 0.6s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.dropzone-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.file-dropzone.is-dragging .dropzone-title {
  color: #667eea;
  font-size: 24px;
}

.dropzone-description {
  font-size: 14px;
  color: #8b95a1;
  margin: 0;
}

.browse-btn {
  margin-top: 8px;
  padding: 10px 24px;
  border: 2px solid #667eea;
  background: white;
  color: #667eea;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.browse-btn:hover:not(:disabled) {
  background: #667eea;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.browse-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dropzone-file-info {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.file-icon {
  font-size: 48px;
  flex-shrink: 0;
}

.file-details {
  flex: 1;
  text-align: left;
}

.file-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
  margin: 0 0 4px 0;
  word-break: break-all;
}

.file-size {
  font-size: 13px;
  color: #8b95a1;
  margin: 0;
}

.remove-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #ef444410;
  color: #ef4444;
  border-radius: 8px;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover:not(:disabled) {
  background: #ef4444;
  color: white;
  transform: scale(1.1);
}

.remove-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.drag-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.drag-overlay-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.pulse-circle {
  width: 80px;
  height: 80px;
  border: 4px solid white;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }
}

.drag-text {
  font-size: 24px;
  font-weight: 600;
  color: white;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
</style>
