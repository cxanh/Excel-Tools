<template>
  <div class="batch-progress-overlay">
    <div class="batch-progress-card">
      <h3>批量处理中...</h3>
      
      <!-- 整体进度 -->
      <div class="progress-section">
        <div class="progress-label">
          整体进度: {{ task.progress }}% ({{ task.currentFileIndex }}/{{ task.totalFiles }} 个文件)
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: task.progress + '%' }">
            {{ task.progress }}%
          </div>
        </div>
      </div>
      
      <!-- 当前文件 -->
      <div class="current-file-section">
        <div class="current-file-label">
          当前文件: {{ task.currentFile || '准备中...' }}
        </div>
      </div>
      
      <!-- 已完成列表 -->
      <div class="completed-section" v-if="task.results.length > 0">
        <h4>已完成:</h4>
        <div class="completed-list">
          <div 
            v-for="(result, index) in task.results" 
            :key="index"
            :class="['completed-item', result.status]"
          >
            <span class="status-icon">{{ result.status === 'success' ? '✓' : '✗' }}</span>
            <span class="file-name">{{ result.file_name }}</span>
            <span class="result-message">{{ result.message }}</span>
          </div>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="actions">
        <button @click="$emit('cancel')" class="btn btn-secondary">
          取消批量处理
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { BatchTask } from '../stores/batchStore';

defineProps<{
  task: BatchTask;
}>();

defineEmits<{
  cancel: [];
}>();
</script>

<style scoped>
.batch-progress-overlay {
  position: fixed;
  top: 0;
  left: 260px;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.batch-progress-card {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  min-width: 600px;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
}

.batch-progress-card h3 {
  margin-bottom: 24px;
  color: #667eea;
  font-size: 20px;
  text-align: center;
}

.progress-section {
  margin-bottom: 24px;
}

.progress-label {
  margin-bottom: 8px;
  color: #5a6c7d;
  font-size: 14px;
  font-weight: 500;
}

.progress-bar {
  background: #e1e4e8;
  border-radius: 12px;
  height: 32px;
  overflow: hidden;
}

.progress-fill {
  background: linear-gradient(90deg, #667eea, #764ba2);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
  transition: width 0.3s ease;
  min-width: 60px;
}

.current-file-section {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fb;
  border-radius: 8px;
}

.current-file-label {
  color: #1a202c;
  font-size: 14px;
  font-weight: 500;
}

.completed-section {
  margin-bottom: 24px;
}

.completed-section h4 {
  margin-bottom: 12px;
  color: #5a6c7d;
  font-size: 14px;
  font-weight: 500;
}

.completed-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  padding: 8px;
}

.completed-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 4px;
  font-size: 13px;
}

.completed-item.success {
  background: #10b98108;
}

.completed-item.error {
  background: #ef444408;
}

.status-icon {
  font-weight: bold;
  min-width: 20px;
}

.completed-item.success .status-icon {
  color: #10b981;
}

.completed-item.error .status-icon {
  color: #ef4444;
}

.file-name {
  font-weight: 500;
  color: #1a202c;
  min-width: 150px;
}

.result-message {
  color: #5a6c7d;
  flex: 1;
}

.actions {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: #f0f3f7;
  color: #5a6c7d;
}

.btn-secondary:hover {
  background: #e1e4e8;
}
</style>
