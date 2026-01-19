<template>
  <Transition name="toast-slide">
    <div v-if="visible" class="error-toast" :class="`toast-${type}`">
      <div class="toast-icon">
        <span v-if="type === 'error'">❌</span>
        <span v-else-if="type === 'warning'">⚠️</span>
        <span v-else-if="type === 'success'">✅</span>
        <span v-else>ℹ️</span>
      </div>
      
      <div class="toast-content">
        <h4 class="toast-title">{{ title }}</h4>
        <p class="toast-message">{{ message }}</p>
        <p v-if="detail" class="toast-detail">{{ detail }}</p>
        <button v-if="action" class="toast-action" @click="handleAction">
          {{ action.text }}
        </button>
      </div>
      
      <button class="toast-close" @click="close">✕</button>
    </div>
  </Transition>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'ErrorToast',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    type: {
      type: String as () => 'error' | 'warning' | 'success' | 'info',
      default: 'error'
    },
    title: {
      type: String,
      required: true
    },
    message: {
      type: String,
      required: true
    },
    detail: {
      type: String,
      default: ''
    },
    action: {
      type: Object as () => { text: string; callback: () => void } | null,
      default: null
    },
    duration: {
      type: Number,
      default: 5000
    }
  },
  emits: ['close', 'update:visible'],
  data() {
    return {
      timer: null as number | null
    }
  },
  watch: {
    visible(newVal) {
      if (newVal && this.duration > 0) {
        this.startTimer()
      } else {
        this.clearTimer()
      }
    }
  },
  methods: {
    close() {
      this.$emit('close')
      this.$emit('update:visible', false)
      this.clearTimer()
    },
    handleAction() {
      if (this.action?.callback) {
        this.action.callback()
      }
      this.close()
    },
    startTimer() {
      this.clearTimer()
      this.timer = window.setTimeout(() => {
        this.close()
      }, this.duration)
    },
    clearTimer() {
      if (this.timer) {
        clearTimeout(this.timer)
        this.timer = null
      }
    }
  },
  beforeUnmount() {
    this.clearTimer()
  }
})
</script>

<style scoped>
.error-toast {
  position: fixed;
  top: 80px;
  right: 24px;
  max-width: 420px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  display: flex;
  gap: 12px;
  padding: 16px;
  z-index: 9998;
  border-left: 4px solid;
}

.toast-error {
  border-left-color: #ef4444;
}

.toast-warning {
  border-left-color: #f59e0b;
}

.toast-success {
  border-left-color: #10b981;
}

.toast-info {
  border-left-color: #3b82f6;
}

.toast-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a202c;
  margin: 0 0 4px 0;
}

.toast-message {
  font-size: 14px;
  color: #4a5568;
  margin: 0 0 4px 0;
  line-height: 1.5;
}

.toast-detail {
  font-size: 12px;
  color: #8b95a1;
  margin: 0 0 8px 0;
  padding: 8px;
  background: #f8f9fb;
  border-radius: 6px;
  line-height: 1.4;
}

.toast-action {
  padding: 6px 12px;
  border: 1px solid #667eea;
  background: white;
  color: #667eea;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.toast-action:hover {
  background: #667eea;
  color: white;
}

.toast-close {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: #cbd5e0;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  align-self: flex-start;
}

.toast-close:hover {
  background: #f1f5f9;
  color: #4a5568;
}

.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.3s ease;
}

.toast-slide-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.toast-slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
