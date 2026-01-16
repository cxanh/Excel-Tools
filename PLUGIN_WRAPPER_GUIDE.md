# PluginWrapper 组件使用指南

## 概述

PluginWrapper 是一个可复用的插件包装器组件，为所有插件提供统一的步骤化流程界面。

## 核心功能

- 📊 **步骤导航**：4步标准流程（上传→配置→处理→下载）
- ⬅️ **可逆操作**：支持返回上一步
- 🔄 **重新开始**：一键重置所有状态
- 🚫 **智能禁用**：处理中自动禁用导航
- 🎨 **统一样式**：浅色玻璃态设计

## 快速开始

### 1. 基础用法

```vue
<template>
  <PluginWrapper
    :can-proceed="canProceed"
    :processing="processing"
    @next="handleNext"
    @prev="handlePrev"
    @reset="handleReset"
    ref="wrapperRef"
  >
    <template #default="{ currentStep }">
      <div v-if="currentStep === 0">步骤 1 内容</div>
      <div v-if="currentStep === 1">步骤 2 内容</div>
      <div v-if="currentStep === 2">步骤 3 内容</div>
      <div v-if="currentStep === 3">步骤 4 内容</div>
    </template>
  </PluginWrapper>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import PluginWrapper from '@/components/PluginWrapper.vue'

const wrapperRef = ref()
const processing = ref(false)

const canProceed = computed(() => {
  const step = wrapperRef.value?.currentStep || 0
  // 根据当前步骤返回是否可以继续
  return true
})

function handleNext() {
  console.log('下一步')
}

function handlePrev() {
  console.log('上一步')
}

function handleReset() {
  console.log('重置')
}
</script>
```

### 2. Props 说明

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| canProceed | boolean | true | 是否可以进入下一步 |
| processing | boolean | false | 是否正在处理（禁用所有导航） |

### 3. Events 说明

| 事件 | 参数 | 说明 |
|------|------|------|
| stepChange | step: number | 步骤变化时触发 |
| next | - | 点击下一步时触发 |
| prev | - | 点击上一步时触发 |
| reset | - | 点击重新开始时触发 |

### 4. Slot Props

| 属性 | 类型 | 说明 |
|------|------|------|
| currentStep | number | 当前步骤（0-3） |
| nextStep | () => void | 进入下一步的方法 |
| prevStep | () => void | 返回上一步的方法 |
| reset | () => void | 重置的方法 |

### 5. Ref 方法

```typescript
const wrapperRef = ref()

// 获取当前步骤
const step = wrapperRef.value?.currentStep

// 手动切换步骤
wrapperRef.value?.nextStep()
wrapperRef.value?.prevStep()
wrapperRef.value?.reset()
```

## 完整示例

### 文件处理插件示例

```vue
<template>
  <PluginWrapper
    :can-proceed="canProceed"
    :processing="processing"
    @next="handleNext"
    @prev="handlePrev"
    @reset="handleReset"
    ref="wrapperRef"
  >
    <template #default="{ currentStep }">
      <!-- 步骤 0: 上传文件 -->
      <div v-if="currentStep === 0" class="step-content">
        <a-alert
          message="功能说明"
          description="这里是功能描述"
          type="info"
          show-icon
          style="margin-bottom: 24px"
        />

        <FileUpload
          :multiple="true"
          @change="handleFileChange"
          ref="fileUploadRef"
        />
        
        <div v-if="files.length > 0" style="margin-top: 16px">
          <a-tag color="blue">已选择 {{ files.length }} 个文件</a-tag>
        </div>
      </div>

      <!-- 步骤 1: 配置参数 -->
      <div v-if="currentStep === 1" class="step-content">
        <a-form :model="formData" layout="vertical">
          <a-form-item label="参数1">
            <a-input v-model:value="formData.param1" />
          </a-form-item>
          <a-form-item label="参数2">
            <a-select v-model:value="formData.param2">
              <a-select-option value="option1">选项1</a-select-option>
              <a-select-option value="option2">选项2</a-select-option>
            </a-select>
          </a-form-item>
        </a-form>
      </div>

      <!-- 步骤 2: 处理中 -->
      <div v-if="currentStep === 2" class="step-content">
        <a-result
          status="info"
          title="准备处理"
          sub-title="点击"开始处理"按钮开始处理文件"
        >
          <template #icon>
            <LoadingOutlined v-if="processing" spin />
            <PlayCircleOutlined v-else />
          </template>
          <template #extra>
            <a-progress
              v-if="processing"
              :percent="progress"
              status="active"
            />
          </template>
        </a-result>
      </div>

      <!-- 步骤 3: 下载结果 -->
      <div v-if="currentStep === 3" class="step-content">
        <a-result
          status="success"
          title="处理完成！"
          :sub-title="`成功: ${successCount} / ${results.length}`"
        >
          <template #extra>
            <a-button type="primary" @click="downloadAll">
              <DownloadOutlined />
              下载全部
            </a-button>
          </template>
        </a-result>

        <a-list :data-source="results" style="margin-top: 24px">
          <template #renderItem="{ item }">
            <a-list-item>
              <a-card size="small">
                <template #title>
                  <a-space>
                    <CheckCircleOutlined v-if="item.success" style="color: #52c41a" />
                    <CloseCircleOutlined v-else style="color: #ff4d4f" />
                    <span>{{ item.fileName }}</span>
                  </a-space>
                </template>
                
                <template #extra>
                  <a-button
                    v-if="item.success"
                    type="link"
                    @click="handleDownload(item)"
                  >
                    <DownloadOutlined />
                    下载
                  </a-button>
                </template>
              </a-card>
            </a-list-item>
          </template>
        </a-list>
      </div>
    </template>
  </PluginWrapper>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import PluginWrapper from '@/components/PluginWrapper.vue'
import FileUpload from '@/components/FileUpload.vue'
import { processFile, downloadResult } from '@/utils/file-service'

const props = defineProps<{
  workerScript?: string
}>()

const files = ref<File[]>([])
const formData = ref({
  param1: '',
  param2: 'option1'
})
const processing = ref(false)
const progress = ref(0)
const results = ref([])
const fileUploadRef = ref()
const wrapperRef = ref()

// 控制是否可以进入下一步
const canProceed = computed(() => {
  const step = wrapperRef.value?.currentStep || 0
  if (step === 0) return files.value.length > 0  // 必须选择文件
  if (step === 1) return formData.value.param1 !== ''  // 必须填写参数
  if (step === 2) return !processing.value  // 处理完成才能继续
  return false
})

const successCount = computed(() => 
  results.value.filter(r => r.success).length
)

function handleFileChange(newFiles: File[]) {
  files.value = newFiles
}

function handleNext() {
  const step = wrapperRef.value?.currentStep || 0
  if (step === 2) {
    // 在步骤2点击"开始处理"时执行处理
    handleProcess()
  }
}

function handlePrev() {
  // 返回上一步时可以清空某些状态
  const step = wrapperRef.value?.currentStep || 0
  if (step === 1) {
    results.value = []
  }
}

function handleReset() {
  // 重置所有状态
  files.value = []
  formData.value = {
    param1: '',
    param2: 'option1'
  }
  results.value = []
  progress.value = 0
  if (fileUploadRef.value) {
    fileUploadRef.value.clear()
  }
}

async function handleProcess() {
  if (!props.workerScript) {
    message.error('插件配置错误')
    return
  }

  processing.value = true
  progress.value = 0
  results.value = []

  try {
    const totalFiles = files.value.length

    for (let i = 0; i < totalFiles; i++) {
      const file = files.value[i]
      
      try {
        const result = await processFile(file, props.workerScript, formData.value)
        results.value.push(result)
      } catch (error) {
        results.value.push({
          success: false,
          fileName: file.name,
          logs: [],
          error: (error as Error).message
        })
      }

      progress.value = Math.round(((i + 1) / totalFiles) * 100)
    }

    message.success(`处理完成！成功: ${successCount.value}/${totalFiles}`)
    
    // 自动进入下一步
    if (wrapperRef.value) {
      wrapperRef.value.nextStep()
    }
  } catch (error) {
    message.error('处理失败: ' + (error as Error).message)
  } finally {
    processing.value = false
  }
}

async function handleDownload(result) {
  try {
    await downloadResult(result, result.fileName)
    message.success('文件已保存')
  } catch (error) {
    message.error('下载失败: ' + (error as Error).message)
  }
}

async function downloadAll() {
  const successResults = results.value.filter(r => r.success)
  for (const result of successResults) {
    await handleDownload(result)
  }
}
</script>

<style scoped>
.step-content {
  min-height: 400px;
}
</style>
```

## 最佳实践

### 1. 步骤控制

```typescript
// ✅ 好的做法：根据实际条件控制
const canProceed = computed(() => {
  const step = wrapperRef.value?.currentStep || 0
  switch (step) {
    case 0: return files.value.length > 0
    case 1: return isFormValid.value
    case 2: return !processing.value
    default: return false
  }
})

// ❌ 不好的做法：总是返回 true
const canProceed = computed(() => true)
```

### 2. 处理时机

```typescript
// ✅ 好的做法：在 handleNext 中判断步骤
function handleNext() {
  const step = wrapperRef.value?.currentStep || 0
  if (step === 2) {
    handleProcess()  // 只在步骤2开始处理
  }
}

// ❌ 不好的做法：在 watch 中处理
watch(() => wrapperRef.value?.currentStep, (step) => {
  if (step === 2) {
    handleProcess()  // 可能导致重复执行
  }
})
```

### 3. 状态重置

```typescript
// ✅ 好的做法：完整重置所有状态
function handleReset() {
  files.value = []
  formData.value = getDefaultFormData()
  results.value = []
  progress.value = 0
  processing.value = false
  if (fileUploadRef.value) {
    fileUploadRef.value.clear()
  }
}

// ❌ 不好的做法：部分重置
function handleReset() {
  files.value = []
  // 忘记重置其他状态
}
```

### 4. 自动跳转

```typescript
// ✅ 好的做法：处理完成后自动跳转
async function handleProcess() {
  // ... 处理逻辑
  
  if (wrapperRef.value) {
    wrapperRef.value.nextStep()  // 自动进入结果页
  }
}

// ❌ 不好的做法：需要用户手动点击
async function handleProcess() {
  // ... 处理逻辑
  // 没有自动跳转，用户需要手动点击"下一步"
}
```

## 常见问题

### Q1: 如何自定义步骤名称？

A: 目前步骤名称是固定的。如果需要自定义，可以修改 PluginWrapper 组件：

```vue
<a-steps :current="currentStep" size="small">
  <a-step :title="stepTitles[0]" />
  <a-step :title="stepTitles[1]" />
  <a-step :title="stepTitles[2]" />
  <a-step :title="stepTitles[3]" />
</a-steps>

<script setup>
const props = defineProps<{
  stepTitles?: string[]
}>()

const defaultTitles = ['上传文件', '配置参数', '处理中', '下载结果']
const stepTitles = computed(() => props.stepTitles || defaultTitles)
</script>
```

### Q2: 如何跳过某个步骤？

A: 可以在 handleNext 中直接跳过：

```typescript
function handleNext() {
  const step = wrapperRef.value?.currentStep || 0
  
  // 如果步骤1不需要配置，直接跳到步骤2
  if (step === 1 && !needsConfig.value) {
    wrapperRef.value?.nextStep()  // 再次调用跳过
  }
}
```

### Q3: 如何在处理中禁止返回？

A: 使用 processing 属性：

```vue
<PluginWrapper :processing="processing">
  <!-- 处理中时，所有导航按钮都会被禁用 -->
</PluginWrapper>
```

### Q4: 如何添加更多步骤？

A: 修改 PluginWrapper 组件，增加步骤数量：

```vue
<a-steps :current="currentStep" size="small">
  <a-step title="步骤1" />
  <a-step title="步骤2" />
  <a-step title="步骤3" />
  <a-step title="步骤4" />
  <a-step title="步骤5" />  <!-- 新增 -->
</a-steps>

<script setup>
// 修改最大步骤数
function nextStep() {
  if (currentStep.value < 4) {  // 改为 4
    currentStep.value++
    // ...
  }
}
</script>
```

## 总结

PluginWrapper 组件提供了：

✅ 统一的步骤化流程
✅ 可逆的操作体验
✅ 智能的状态管理
✅ 优雅的视觉设计
✅ 简单的集成方式

使用这个组件可以大幅提升插件的用户体验，让文件处理过程更加清晰、可控。
