<template>
  <div class="recent-files-panel">
    <div class="panel-header">
      <h3 class="panel-title">📂 最近打开</h3>
      <button 
        v-if="recentFilesStore.recentFiles.length > 0"
        class="clear-btn"
        @click="handleClearAll"
        title="清空列表"
      >
        🗑️ 清空
      </button>
    </div>
    
    <div v-if="recentFilesStore.recentFiles.length === 0" class="empty-state">
      <div class="empty-icon">📭</div>
      <p class="empty-text">暂无最近打开的文件</p>
      <p class="empty-hint">打开文件后会显示在这里</p>
    </div>
    
    <div v-else class="recent-files-list">
      <div 
        v-for="file in recentFilesStore.recentFiles" 
        :key="file.path"
        class="recent-file-item"
        @click="$emit('file-selected', file)"
      >
        <div class="file-icon">
          <span v-if="file.format === 'xlsx'">📗</span>
          <span v-else-if="file.format === 'xls'">📘</span>
          <span v-else-if="file.format === 'csv'">📄</span>
          <span v-else>📋</span>
        </div>
        
        <div class="file-info">
          <h4 class="file-name" :title="file.name">{{ file.name }}</h4>
          <p class="file-meta">
            <span class="file-time">{{ recentFilesStore.formatTime(file.lastOpened) }}</span>
            <span v-if="file.size" class="file-size">· {{ formatFileSize(file.size) }}</span>
          </p>
          <p class="file-path" :title="file.path">{{ file.path }}</p>
        </div>
        
        <button 
          class="remove-btn"
          @click.stop="handleRemove(file.path)"
          title="从列表中移除"
        >
          ✕
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useRecentFilesStore } from '../stores/recentFilesStore'

export default defineComponent({
  name: 'RecentFilesList',
  emits: ['file-selected'],
  setup() {
    const recentFilesStore = useRecentFilesStore()
    return { recentFilesStore }
  },
  methods: {
    handleRemove(path: string) {
      this.recentFilesStore.removeRecentFile(path)
    },
    handleClearAll() {
      if (confirm('确定要清空最近文件列表吗？')) {
        this.recentFilesStore.clearRecentFiles()
      }
    },
    formatFileSize(bytes: number): string {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    }
  }
})
</script>

<style scoped>
.recent-files-panel {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.clear-btn {
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #8b95a1;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: #fee2e2;
  border-color: #fecaca;
  color: #ef4444;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-text {
  font-size: 15px;
  color: #4a5568;
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 13px;
  color: #8b95a1;
  margin: 0;
}

.recent-files-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.recent-file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.recent-file-item:hover {
  background: linear-gradient(135deg, #667eea08 0%, #764ba208 100%);
  border-color: #667eea;
  transform: translateX(4px);
}

.file-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #1a202c;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  font-size: 12px;
  color: #8b95a1;
  margin: 0 0 4px 0;
}

.file-time {
  color: #667eea;
  font-weight: 500;
}

.file-size {
  color: #8b95a1;
}

.file-path {
  font-size: 11px;
  color: #a0aec0;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: 'Consolas', 'Monaco', monospace;
}

.remove-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: #cbd5e0;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background: #fee2e2;
  color: #ef4444;
}

/* 滚动条样式 */
.recent-files-list::-webkit-scrollbar {
  width: 6px;
}

.recent-files-list::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.recent-files-list::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

.recent-files-list::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}
</style>
