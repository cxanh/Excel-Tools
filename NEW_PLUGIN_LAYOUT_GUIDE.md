# 新插件布局系统使用指南

## 概述

基于您提供的界面设计，我创建了一个全新的插件布局系统，完全符合图片中的设计风格。

## 核心组件

### 1. PluginLayout 组件

**文件位置**：`packages/renderer/src/components/PluginLayout.vue`

**功能特性**：
- ✅ 顶部操作栏（返回按钮 + 标题 + 操作按钮）
- ✅ 步骤指示器（5步流程）
- ✅ 主内容区（可滚动）
- ✅ 底部操作栏（上一步/下一步按钮）

### 2. 示例插件

**文件位置**：`plugins/remove-empty-row/index-new.vue`

**实现功能**：
- ✅ 文件上传和管理
- ✅ 文件列表表格
- ✅ 处理规则配置
- ✅ 导出选项设置
- ✅ 输出目录选择
- ✅ 处理进度显示
- ✅ 结果展示和下载

## 界面布局

```
┌─────────────────────────────────────────────────────────┐
│  [← 返回到主面板]  按规则删除改 Excel 内容               │
│                    [+ 添加文件] [📁 从文件夹导入] [更多▼] │
├─────────────────────────────────────────────────────────┤
│  ① 选择待处理文件 → ② 设置处理规则 → ③ 设置导出选项    │
│  → ④ 设置输出目录 → ⑤ 开始处理                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│                    主内容区域                            │
│              （根据当前步骤显示不同内容）                │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                  [上一步]  [下一步 →]                    │
└─────────────────────────────────────────────────────────┘
```

## 使用方法

### 基础用法

```vue
<template>
  <PluginLayout
    title="按规则删除改 Excel 内容"
    :can-proceed="canProceed"
    :processing="processing"
    @step-change="handleStepChange"
    @next="handleNext"
    @prev="handlePrev"
    @reset="handleReset"
    ref="layoutRef"
  >
    <template #default="{ currentStep }">
      <!-- 步骤 0 -->
      <div v-if="currentStep === 0">
        步骤 1 的内容
      </div>
      
      <!-- 步骤 1 -->
      <div v-if="currentStep === 1">
        步骤 2 的内容
      </div>
      
      <!-- 更多步骤... -->
    </template>
  </PluginLayout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import PluginLayout from '@/components/PluginLayout.vue'

const layoutRef = ref()
const processing = ref(false)

const canProceed = computed(() => {
  const step = layoutRef.value?.currentStep || 0
  // 根据当前步骤返回是否可以继续
  return true
})

function handleStepChange(step: number) {
  console.log('当前步骤:', step)
}

function handleNext() {
  // 处理下一步逻辑
}

function handlePrev() {
  // 处理上一步逻辑
}

function handleReset() {
  // 重置所有状态
}
</script>
```

## 界面元素详解

### 1. 顶部操作栏

#### 左侧
- **返回按钮**：返回到主面板
- **标题**：显示当前插件名称

#### 右侧
- **添加文件**：打开文件选择对话框
- **从文件夹导入文件**：批量导入文件夹中的文件
- **更多**：下拉菜单，包含：
  - 清空所有
  - 导出配置
  - 导入配置

### 2. 步骤指示器

**默认步骤**：
1. 选择待处理文件
2. 设置处理规则
3. 设置导出选项
4. 设置输出目录
5. 开始处理

**自定义步骤**：
```vue
<PluginLayout
  :steps="[
    { title: '上传文件' },
    { title: '配置参数' },
    { title: '开始处理' }
  ]"
>
```

### 3. 主内容区

#### 步骤 0：选择待处理文件

**包含元素**：
- 警告提示框
- 文件上传区域（拖拽上传）
- 文件列表表格
  - 序号
  - 名称
  - 路径
  - 扩展名
  - 创建时间
  - 修改时间
  - 操作（预览、排除）

**表格示例**：
```vue
<a-table
  :columns="fileColumns"
  :data-source="files"
  :pagination="false"
  bordered
>
  <template #bodyCell="{ column, record, index }">
    <!-- 自定义单元格内容 -->
  </template>
</a-table>
```

#### 步骤 1：设置处理规则

**包含元素**：
- 卡片容器
- 表单控件
  - 单选框组
  - 文本域
  - 复选框组

#### 步骤 2：设置导出选项

**包含元素**：
- 文件命名规则
- 文件格式选择

#### 步骤 3：设置输出目录

**包含元素**：
- 目录选择输入框
- 浏览按钮
- 自动打开选项

#### 步骤 4：开始处理

**包含元素**：
- 结果状态（成功/处理中/准备）
- 进度条
- 操作按钮（下载全部、打开文件夹）
- 结果列表

### 4. 底部操作栏

**按钮显示逻辑**：
- 第一步：只显示"下一步"
- 中间步骤：显示"上一步"和"下一步"
- 倒数第二步："下一步"变为"开始处理"
- 最后一步：显示"重新开始"

## 样式特点

### 1. 颜色系统

```css
/* 主题色 */
--primary-color: #6366f1;  /* 紫色 */
--success-color: #52c41a;  /* 绿色 */
--error-color: #ff4d4f;    /* 红色 */
--warning-color: #faad14;  /* 橙色 */

/* 背景色 */
--bg-primary: #f5f7fa;     /* 浅灰 */
--bg-white: #ffffff;       /* 白色 */

/* 文字色 */
--text-primary: #1e293b;   /* 深灰 */
--text-secondary: #64748b; /* 中灰 */
```

### 2. 间距系统

```css
/* 内边距 */
--padding-sm: 16px;
--padding-md: 24px;
--padding-lg: 48px;

/* 外边距 */
--margin-sm: 12px;
--margin-md: 16px;
--margin-lg: 24px;
```

### 3. 圆角

```css
--border-radius: 8px;
```

### 4. 阴影

```css
--shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04);
--shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08);
```

## 事件系统

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| title | string | - | 插件标题 |
| steps | Step[] | 默认5步 | 步骤配置 |
| canProceed | boolean | true | 是否可以进入下一步 |
| processing | boolean | false | 是否正在处理 |

### Events

| 事件 | 参数 | 说明 |
|------|------|------|
| step-change | step: number | 步骤变化 |
| next | - | 下一步 |
| prev | - | 上一步 |
| reset | - | 重置 |
| add-files | - | 添加文件 |
| import-from-folder | - | 从文件夹导入 |
| clear-all | - | 清空所有 |
| export-config | - | 导出配置 |
| import-config | - | 导入配置 |

## 响应式设计

### 断点

```css
/* 大屏幕 */
@media (min-width: 1200px) {
  .step-content {
    max-width: 1200px;
  }
}

/* 中等屏幕 */
@media (max-width: 1200px) {
  .step-content {
    max-width: 100%;
  }
}

/* 小屏幕 */
@media (max-width: 768px) {
  .plugin-header {
    flex-direction: column;
    gap: 12px;
  }
}
```

## 最佳实践

### 1. 文件上传

```vue
<FileUpload
  :multiple="true"
  @change="handleFileChange"
  ref="fileUploadRef"
/>
```

### 2. 文件列表

```vue
<a-table
  :columns="fileColumns"
  :data-source="files"
  :pagination="false"
  bordered
/>
```

### 3. 进度显示

```vue
<a-progress
  :percent="progress"
  :stroke-color="{
    '0%': '#6366f1',
    '100%': '#8b5cf6',
  }"
/>
```

### 4. 结果展示

```vue
<a-result
  :status="processing ? 'info' : 'success'"
  :title="processing ? '正在处理...' : '处理完成！'"
>
  <template #icon>
    <LoadingOutlined v-if="processing" spin />
  </template>
</a-result>
```

## 如何应用到现有插件

### 步骤 1：导入组件

```vue
import PluginLayout from '@/components/PluginLayout.vue'
```

### 步骤 2：替换模板

将现有的插件模板替换为 PluginLayout：

```vue
<template>
  <PluginLayout
    title="你的插件名称"
    :can-proceed="canProceed"
    :processing="processing"
    @next="handleNext"
    @prev="handlePrev"
    @reset="handleReset"
    ref="layoutRef"
  >
    <template #default="{ currentStep }">
      <!-- 你的插件内容 -->
    </template>
  </PluginLayout>
</template>
```

### 步骤 3：实现逻辑

```typescript
const layoutRef = ref()
const processing = ref(false)

const canProceed = computed(() => {
  const step = layoutRef.value?.currentStep || 0
  // 实现你的逻辑
  return true
})

function handleNext() {
  // 实现下一步逻辑
}

function handlePrev() {
  // 实现上一步逻辑
}

function handleReset() {
  // 实现重置逻辑
}
```

## 总结

新的插件布局系统提供了：

✅ 完全符合设计图的界面
✅ 统一的用户体验
✅ 灵活的配置选项
✅ 丰富的交互功能
✅ 响应式布局
✅ 易于使用和扩展

使用这个布局系统，可以快速创建专业、美观、易用的插件界面！
