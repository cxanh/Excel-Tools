<template>
  <div class="plugin-layout">
    <!-- 顶部操作栏 -->
    <div class="plugin-header">
      <div class="header-left">
        <a-button class="back-button" @click="handleBack">
          <LeftOutlined />
          返回到主面板
        </a-button>
        <span class="plugin-title">{{ title }}</span>
      </div>
      <div class="header-right">
        <slot name="header-actions">
          <a-button type="primary" @click="$emit('add-files')">
            <PlusOutlined />
            添加文件
          </a-button>
          <a-button @click="$emit('import-from-folder')">
            <FolderOpenOutlined />
            从文件夹导入文件
          </a-button>
          <a-dropdown>
            <a-button>
              更多
              <DownOutlined />
            </a-button>
            <template #overlay>
              <a-menu>
                <a-menu-item key="1" @click="$emit('clear-all')">
                  <DeleteOutlined />
                  清空所有
                </a-menu-item>
                <a-menu-item key="2" @click="$emit('export-config')">
                  <ExportOutlined />
                  导出配置
                </a-menu-item>
                <a-menu-item key="3" @click="$emit('import-config')">
                  <ImportOutlined />
                  导入配置
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </slot>
      </div>
    </div>

    <!-- 步骤指示器 -->
    <div class="steps-container">
      <a-steps :current="currentStep" :items="steps" />
    </div>

    <!-- 主内容区 -->
    <div class="plugin-content">
      <slot :current-step="currentStep" />
    </div>

    <!-- 底部操作栏 -->
    <div class="plugin-footer">
      <a-space :size="16">
        <a-button 
          v-if="currentStep > 0" 
          size="large"
          @click="prevStep"
          :disabled="processing"
        >
          <LeftOutlined />
          上一步
        </a-button>
        
        <a-button 
          v-if="currentStep < steps.length - 1"
          type="primary" 
          size="large"
          @click="nextStep"
          :disabled="!canProceed || processing"
          :loading="processing"
        >
          {{ currentStep === steps.length - 2 ? '开始处理' : '下一步' }}
          <RightOutlined />
        </a-button>

        <a-button 
          v-if="currentStep === steps.length - 1"
          type="primary" 
          size="large"
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
import { useRouter } from 'vue-router'
import {
  LeftOutlined,
  RightOutlined,
  PlusOutlined,
  FolderOpenOutlined,
  DownOutlined,
  DeleteOutlined,
  ExportOutlined,
  ImportOutlined,
  ReloadOutlined
} from '@ant-design/icons-vue'

interface Step {
  title: string
  description?: string
}

interface Props {
  title: string
  steps?: Step[]
  canProceed?: boolean
  processing?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  steps: () => [
    { title: '选择待处理文件' },
    { title: '设置处理规则' },
    { title: '设置导出选项' },
    { title: '设置输出目录' },
    { title: '开始处理' }
  ],
  canProceed: true,
  processing: false
})

const emit = defineEmits<{
  'step-change': [step: number]
  'next': []
  'prev': []
  'reset': []
  'add-files': []
  'import-from-folder': []
  'clear-all': []
  'export-config': []
  'import-config': []
}>()

const router = useRouter()
const currentStep = ref(0)

function handleBack() {
  router.push('/')
}

function nextStep() {
  if (currentStep.value < props.steps.length - 1) {
    currentStep.value++
    emit('step-change', currentStep.value)
    emit('next')
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
    emit('step-change', currentStep.value)
    emit('prev')
  }
}

function reset() {
  currentStep.value = 0
  emit('step-change', currentStep.value)
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
.plugin-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f7fa;
}

/* 顶部操作栏 */
.plugin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6366f1;
  border-color: #6366f1;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: rgba(99, 102, 241, 0.1);
  border-color: #6366f1;
  color: #6366f1;
}

.plugin-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* 步骤指示器 */
.steps-container {
  padding: 24px 48px;
  background: #fff;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

/* 主内容区 */
.plugin-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

/* 底部操作栏 */
.plugin-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.04);
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

/* Ant Design Steps 样式覆盖 */
:deep(.ant-steps-item-process .ant-steps-item-icon) {
  background: #6366f1;
  border-color: #6366f1;
}

:deep(.ant-steps-item-finish .ant-steps-item-icon) {
  border-color: #6366f1;
}

:deep(.ant-steps-item-finish .ant-steps-item-icon > .ant-steps-icon) {
  color: #6366f1;
}

:deep(.ant-steps-item-finish > .ant-steps-item-container > .ant-steps-item-tail::after) {
  background-color: #6366f1;
}
</style>
