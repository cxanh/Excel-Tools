<template>
  <div class="batch-summary-overlay" @click.self="$emit('close')">
    <div class="batch-summary-card">
      <div class="summary-header">
        <h3>批量处理完成</h3>
        <button @click="$emit('close')" class="close-btn">✕</button>
      </div>
      
      <!-- 处理摘要 -->
      <div class="summary-stats">
        <h4>📊 处理摘要</h4>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-label">总文件数</span>
            <span class="stat-value">{{ task.totalFiles }}</span>
          </div>
          <div class="stat-item success">
            <span class="stat-label">成功</span>
            <span class="stat-value">{{ successCount }}</span>
          </div>
          <div class="stat-item error">
            <span class="stat-label">失败</span>
            <span class="stat-value">{{ errorCount }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">总耗时</span>
            <span class="stat-value">{{ formatDuration(duration) }}</span>
          </div>
        </div>
      </div>
      
      <!-- 详细结果 -->
      <div class="detailed-results">
        <h4>📋 详细结果</h4>
        <div class="results-list">
          <div 
            v-for="(result, index) in task.results" 
            :key="index"
            :class="['result-item', result.status]"
          >
            <span class="result-icon">{{ result.status === 'success' ? '✓' : '✗' }}</span>
            <div class="result-content">
              <div class="result-file">{{ result.file_name }}</div>
              <div class="result-message">{{ result.message }}</div>
            </div>
            <span class="result-duration">{{ result.duration }}ms</span>
          </div>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="actions">
        <button @click="exportReport" class="btn btn-secondary">
          导出报告
        </button>
        <button @click="$emit('close')" class="btn btn-primary">
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { BatchTask } from '../stores/batchStore';

const props = defineProps<{
  task: BatchTask;
}>();

const emit = defineEmits<{
  close: [];
}>();

const successCount = computed(() => {
  return props.task.results.filter(r => r.status === 'success').length;
});

const errorCount = computed(() => {
  return props.task.results.filter(r => r.status === 'error').length;
});

const duration = computed(() => {
  if (props.task.startTime && props.task.endTime) {
    return props.task.endTime - props.task.startTime;
  }
  return 0;
});

function formatDuration(ms: number): string {
  if (ms < 1000) {
    return `${ms}ms`;
  }
  const seconds = Math.floor(ms / 1000);
  if (seconds < 60) {
    return `${seconds}秒`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}分${remainingSeconds}秒`;
}

function exportReport() {
  const report = {
    task: props.task.name,
    operation: props.task.operation,
    totalFiles: props.task.totalFiles,
    successCount: successCount.value,
    errorCount: errorCount.value,
    duration: duration.value,
    results: props.task.results,
    timestamp: new Date().toISOString(),
  };
  
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `batch-report-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
}
</script>

<style scoped>
.batch-summary-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.batch-summary-card {
  background: white;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  min-width: 600px;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.summary-header h3 {
  color: #1a202c;
  font-size: 20px;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #8b95a1;
  cursor: pointer;
  padding: 4px 8px;
  line-height: 1;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #1a202c;
}

.summary-stats {
  margin-bottom: 24px;
  padding: 20px;
  background: #f8f9fb;
  border-radius: 12px;
}

.summary-stats h4 {
  margin: 0 0 16px 0;
  color: #1a202c;
  font-size: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 2px solid #e1e4e8;
}

.stat-item.success {
  border-color: #10b981;
  background: #10b98108;
}

.stat-item.error {
  border-color: #ef4444;
  background: #ef444408;
}

.stat-label {
  font-size: 12px;
  color: #8b95a1;
  font-weight: 500;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #1a202c;
}

.stat-item.success .stat-value {
  color: #10b981;
}

.stat-item.error .stat-value {
  color: #ef4444;
}

.detailed-results {
  margin-bottom: 24px;
}

.detailed-results h4 {
  margin: 0 0 12px 0;
  color: #1a202c;
  font-size: 16px;
}

.results-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #e1e4e8;
}

.result-item:last-child {
  border-bottom: none;
}

.result-item.success {
  background: #10b98105;
}

.result-item.error {
  background: #ef444405;
}

.result-icon {
  font-size: 18px;
  font-weight: bold;
  min-width: 24px;
}

.result-item.success .result-icon {
  color: #10b981;
}

.result-item.error .result-icon {
  color: #ef4444;
}

.result-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.result-file {
  font-weight: 500;
  color: #1a202c;
  font-size: 14px;
}

.result-message {
  color: #5a6c7d;
  font-size: 13px;
}

.result-duration {
  color: #8b95a1;
  font-size: 12px;
  min-width: 60px;
  text-align: right;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: #f0f3f7;
  color: #5a6c7d;
}

.btn-secondary:hover {
  background: #e1e4e8;
}
</style>
