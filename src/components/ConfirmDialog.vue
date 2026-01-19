<template>
  <Transition name="dialog-fade">
    <div v-if="visible" class="dialog-overlay" @click="handleOverlayClick">
      <div class="dialog-container" @click.stop>
        <div class="dialog-header">
          <div class="dialog-icon" :class="`icon-${type}`">
            <span v-if="type === 'warning'">⚠️</span>
            <span v-else-if="type === 'danger'">🚨</span>
            <span v-else-if="type === 'info'">ℹ️</span>
            <span v-else>❓</span>
          </div>
          <h3 class="dialog-title">{{ title }}</h3>
        </div>
        
        <div class="dialog-body">
          <p class="dialog-message">{{ message }}</p>
          <p v-if="detail" class="dialog-detail">{{ detail }}</p>
        </div>
        
        <div class="dialog-footer">
          <button 
            class="dialog-btn btn-cancel" 
            @click="handleCancel"
            :disabled="loading"
          >
            {{ cancelText }}
          </button>
          <button 
            class="dialog-btn btn-confirm" 
            :class="`btn-${type}`"
            @click="handleConfirm"
            :disabled="loading"
          >
            <span v-if="loading" class="btn-loading">⏳</span>
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'ConfirmDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: '确认操作'
    },
    message: {
      type: String,
      required: true
    },
    detail: {
      type: String,
      default: ''
    },
    type: {
      type: String as () => 'warning' | 'danger' | 'info' | 'question',
      default: 'warning'
    },
    confirmText: {
      type: String,
      default: '确定'
    },
    cancelText: {
      type: String,
      default: '取消'
    },
    loading: {
      type: Boolean,
      default: false
    },
    closeOnOverlay: {
      type: Boolean,
      default: true
    }
  },
  emits: ['confirm', 'cancel', 'update:visible'],
  methods: {
    handleConfirm() {
      this.$emit('confirm')
    },
    handleCancel() {
      this.$emit('cancel')
      this.$emit('update:visible', false)
    },
    handleOverlayClick() {
      if (this.closeOnOverlay && !this.loading) {
        this.handleCancel()
      }
    }
  }
})
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.dialog-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 480px;
  width: 90%;
  overflow: hidden;
  animation: dialogSlideIn 0.3s ease;
}

@keyframes dialogSlideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.dialog-header {
  padding: 24px 24px 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.dialog-icon {
  font-size: 32px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  flex-shrink: 0;
}

.dialog-icon.icon-warning {
  background: #fef3c7;
}

.dialog-icon.icon-danger {
  background: #fee2e2;
}

.dialog-icon.icon-info {
  background: #dbeafe;
}

.dialog-icon.icon-question {
  background: #e0e7ff;
}

.dialog-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.dialog-body {
  padding: 0 24px 24px;
}

.dialog-message {
  font-size: 15px;
  color: #4a5568;
  margin: 0 0 8px 0;
  line-height: 1.6;
}

.dialog-detail {
  font-size: 13px;
  color: #8b95a1;
  margin: 0;
  line-height: 1.5;
  padding: 12px;
  background: #f8f9fb;
  border-radius: 8px;
}

.dialog-footer {
  padding: 16px 24px;
  background: #f8f9fb;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.dialog-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dialog-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-cancel {
  background: white;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}

.btn-cancel:hover:not(:disabled) {
  background: #f8f9fb;
  border-color: #cbd5e0;
}

.btn-confirm {
  color: white;
}

.btn-confirm.btn-warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.btn-confirm.btn-danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.btn-confirm.btn-info {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.btn-confirm.btn-question {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.btn-confirm:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-loading {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: opacity 0.3s ease;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}
</style>
