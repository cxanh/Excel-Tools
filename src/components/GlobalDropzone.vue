<template>
  <div 
    v-if="isGlobalDragging" 
    class="global-dropzone-overlay"
    @dragenter.prevent
    @dragover.prevent="handleDragOver"
    @dragleave.prevent="handleDragLeave"
    @drop.prevent="handleDrop"
  >
    <div class="global-dropzone-content">
      <div class="drop-icon">📂</div>
      <h2 class="drop-title">释放文件开始处理</h2>
      <p class="drop-description">支持 Excel 文件 (.xlsx, .xls, .csv)</p>
      <div class="drop-animation-ring"></div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'GlobalDropzone',
  emits: ['file-dropped'],
  data() {
    return {
      isGlobalDragging: false,
      dragCounter: 0,
      dragLeaveTimer: null as number | null
    }
  },
  mounted() {
    // 监听全局拖拽事件
    window.addEventListener('dragenter', this.handleGlobalDragEnter)
    window.addEventListener('dragleave', this.handleGlobalDragLeave)
    window.addEventListener('dragover', this.handleGlobalDragOver)
    window.addEventListener('drop', this.handleGlobalDrop)
  },
  beforeUnmount() {
    // 清理事件监听
    window.removeEventListener('dragenter', this.handleGlobalDragEnter)
    window.removeEventListener('dragleave', this.handleGlobalDragLeave)
    window.removeEventListener('dragover', this.handleGlobalDragOver)
    window.removeEventListener('drop', this.handleGlobalDrop)
    
    if (this.dragLeaveTimer) {
      clearTimeout(this.dragLeaveTimer)
    }
  },
  methods: {
    handleGlobalDragEnter(e: DragEvent) {
      e.preventDefault()
      
      // 检查是否是文件拖拽
      if (e.dataTransfer?.types.includes('Files')) {
        this.dragCounter++
        if (this.dragCounter === 1) {
          this.isGlobalDragging = true
        }
        
        if (this.dragLeaveTimer) {
          clearTimeout(this.dragLeaveTimer)
          this.dragLeaveTimer = null
        }
      }
    },
    handleGlobalDragOver(e: DragEvent) {
      e.preventDefault()
      if (e.dataTransfer) {
        e.dataTransfer.dropEffect = 'copy'
      }
    },
    handleGlobalDragLeave(e: DragEvent) {
      e.preventDefault()
      this.dragCounter--
      
      // 使用延迟来避免快速进出导致的闪烁
      if (this.dragCounter <= 0) {
        this.dragLeaveTimer = window.setTimeout(() => {
          this.isGlobalDragging = false
          this.dragCounter = 0
        }, 100)
      }
    },
    handleGlobalDrop(e: DragEvent) {
      e.preventDefault()
      this.isGlobalDragging = false
      this.dragCounter = 0
      
      if (this.dragLeaveTimer) {
        clearTimeout(this.dragLeaveTimer)
        this.dragLeaveTimer = null
      }
      
      const files = e.dataTransfer?.files
      if (files && files.length > 0) {
        this.$emit('file-dropped', files[0])
      }
    },
    handleDragOver(e: DragEvent) {
      e.dataTransfer!.dropEffect = 'copy'
    },
    handleDragLeave(e: DragEvent) {
      // 只在离开覆盖层本身时处理
      if (e.target === e.currentTarget) {
        this.isGlobalDragging = false
        this.dragCounter = 0
      }
    },
    handleDrop(e: DragEvent) {
      this.isGlobalDragging = false
      this.dragCounter = 0
      
      const files = e.dataTransfer?.files
      if (files && files.length > 0) {
        this.$emit('file-dropped', files[0])
      }
    }
  }
})
</script>

<style scoped>
.global-dropzone-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.97) 0%, rgba(118, 75, 162, 0.97) 100%);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.global-dropzone-content {
  text-align: center;
  color: white;
  position: relative;
}

.drop-icon {
  font-size: 120px;
  margin-bottom: 24px;
  animation: float 2s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

.drop-title {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 16px 0;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.drop-description {
  font-size: 18px;
  margin: 0;
  opacity: 0.95;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.drop-animation-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 300px;
  height: 300px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation: ringPulse 2s ease-in-out infinite;
  pointer-events: none;
}

@keyframes ringPulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.3);
    opacity: 0.3;
  }
}
</style>
