<template>
  <div class="plugin-wrapper">
    <!-- 步骤导航 -->
    <div class="steps-container">
      <a-steps :current="currentStep" size="small">
        <a-step title="上传文件" />
        <a-step title="配置参数" />
        <a-step title="处理中" />
        <a-step title="下载结果" />
      </a-steps>
    </div>

    <!-- 内容区域 -->
    <div class="plugin-content">
      <slot :current-step="currentStep" :next-step="nextStep" :prev-step="prevStep" :reset="reset" />
    </div>

    <!-- 操作按钮 -->
    <div class="plugin-actions">
      <a-space>
        <a-button 
          v-if="currentStep > 0 && currentStep < 3" 
          @click="prevStep"
          :disabled="processing"
        >
          <LeftOutlined />
          上一步
        </a-button>
        
        <a-button 
          v-if="currentStep < 3" 
          type="primary" 
          @click="nextStep"
          :disabled="!canProceed || processing"
          :loading="processing"
        >
          {{ currentStep === 2 ? '开始处理' : '下一步' }}
          <RightOutlined v-if="currentStep < 2" />
        </a-button>

        <a-button 
          v-if="currentStep === 3" 
          type="primary" 
          @click="reset"
        >
          <ReloadOutlined />
          重新开始
        </a-button>
      </a-space>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { LeftOutlined, RightOutlined, ReloadOutlined } from '@ant-design/icons-vue'

interface Props {
  canProceed?: boolean
  processing?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  canProceed: true,
  processing: false
})

const emit = defineEmits<{
  stepChange: [step: number]
  next: []
  prev: []
  reset: []
}>()

const currentStep = ref(0)

function nextStep() {
  if (currentStep.value < 3) {
    currentStep.value++
    emit('stepChange', currentStep.value)
    emit('next')
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
    emit('stepChange', currentStep.value)
    emit('prev')
  }
}

function reset() {
  currentStep.value = 0
  emit('stepChange', currentStep.value)
  emit('reset')
}

// 暴露方法给父组件
defineExpose({
  currentStep,
  nextStep,
  prevStep,
  reset
})
</script>

<style scoped>
.plugin-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
}

.steps-container {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.plugin-content {
  flex: 1;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  overflow-y: auto;
}

.plugin-actions {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  padding: 16px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  display: flex;
  justify-content: flex-end;
}

/* 滚动条样式 */
.plugin-content::-webkit-scrollbar {
  width: 8px;
}

.plugin-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.03);
  border-radius: 4px;
}

.plugin-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 4px;
}

.plugin-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.25);
}
</style>
