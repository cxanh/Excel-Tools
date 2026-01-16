<template>
  <transition name="slide-down">
    <div v-if="fileStore.hasLoadedFile" class="current-file-bar">
      <div class="file-bar-content">
        <div class="file-info">
          <span class="file-icon">📄</span>
          <div class="file-details">
            <span class="file-name">{{ fileStore.fileName }}</span>
            <span class="file-meta">
              {{ fileStore.loadedFile?.file_format.toUpperCase() }} · 
              {{ formatFileSize(fileStore.loadedFile?.file_size || 0) }} · 
              {{ fileStore.loadedFile?.sheet_count }} 个工作表
            </span>
          </div>
        </div>
        
        <div class="file-actions">
          <Tooltip text="查看文件详情" position="bottom">
            <button 
              class="action-btn info-btn"
              @click="goToFileView"
            >
              <span>ℹ️</span>
            </button>
          </Tooltip>
          
          <Tooltip text="保存文件 (Ctrl+S)" position="bottom">
            <button 
              class="action-btn save-btn"
              @click="$emit('save-file')"
              :disabled="fileStore.isLoading"
            >
              <span>💾</span>
            </button>
          </Tooltip>
          
          <Tooltip text="关闭文件 (Ctrl+W)" position="bottom">
            <button 
              class="action-btn close-btn"
              @click="$emit('close-file')"
              :disabled="fileStore.isLoading"
            >
              <span>✕</span>
            </button>
          </Tooltip>
        </div>
      </div>
    </div>
  </transition>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useFileStore } from '../stores/fileStore'
import { useSettingsStore } from '../stores/settingsStore'
import Tooltip from './Tooltip.vue'

export default defineComponent({
  name: 'CurrentFileBar',
  components: {
    Tooltip
  },
  emits: ['save-file', 'close-file'],
  setup() {
    const fileStore = useFileStore()
    const settingsStore = useSettingsStore()
    
    const formatFileSize = (bytes: number): string => {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
    }
    
    const goToFileView = () => {
      settingsStore.setCurrentView('file')
    }
    
    return {
      fileStore,
      formatFileSize,
      goToFileView
    }
  }
})
</script>

<style scoped>
.current-file-bar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.file-bar-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.file-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.file-name {
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  font-size: 12px;
  opacity: 0.9;
}

.file-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.action-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.action-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.action-btn:active:not(:disabled) {
  transform: translateY(0);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.info-btn:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.3);
}

.save-btn:hover:not(:disabled) {
  background: rgba(16, 185, 129, 0.3);
}

.close-btn:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.3);
}

/* 动画 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  transform: translateY(-100%);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .file-bar-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .file-actions {
    justify-content: flex-end;
  }
  
  .file-name {
    font-size: 14px;
  }
  
  .file-meta {
    font-size: 11px;
  }
}
</style>
