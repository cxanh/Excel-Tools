# 插件开发指南

本指南说明如何为Excel工具箱系统开发新插件。

## 插件结构

每个插件包含3个核心文件：

```
plugins/
└── your-plugin-name/
    ├── manifest.json      # 插件配置
    ├── index.vue          # Vue组件界面
    └── worker.py          # Python处理脚本
```

## 开发步骤

### 1. 创建插件目录

```bash
mkdir plugins/your-plugin-name
```

### 2. 创建manifest.json

```json
{
  "key": "your-plugin-name",
  "name": "插件显示名称",
  "icon": "icon-name",
  "description": "插件功能描述",
  "author": "Excel Toolbox Team",
  "version": "1.0.0",
  "dependencies": ["openpyxl", "其他Python包"]
}
```

**字段说明**:
- `key`: 插件唯一标识符（小写字母、数字、连字符）
- `name`: 在UI中显示的名称
- `icon`: 图标名称（Ant Design图标）
- `description`: 简短的功能描述
- `dependencies`: Python依赖包列表（自动安装）

### 3. 创建index.vue组件

```vue
<template>
  <div class="your-plugin-name">
    <a-card title="插件标题" :bordered="false">
      <!-- 功能说明 -->
      <a-alert
        message="功能说明"
        description="详细说明插件的功能"
        type="info"
        show-icon
        style="margin-bottom: 24px"
      />

      <!-- 文件上传 -->
      <a-card title="1. 选择文件" size="small" style="margin-bottom: 16px">
        <FileUpload
          :multiple="true"
          @change="handleFileChange"
          ref="fileUploadRef"
        />
      </a-card>

      <!-- 处理按钮 -->
      <a-card title="2. 开始处理" size="small" style="margin-bottom: 16px">
        <a-button
          type="primary"
          :loading="processing"
          :disabled="files.length === 0"
          @click="handleProcess"
        >
          开始处理
        </a-button>
        <a-progress v-if="processing" :percent="progress" />
      </a-card>

      <!-- 处理结果 -->
      <a-card title="3. 处理结果" size="small" v-if="results.length > 0">
        <!-- 显示结果列表 -->
      </a-card>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import FileUpload from '@/components/FileUpload.vue'
import { processFile, downloadResult, type ProcessResult } from '@/utils/file-service'

// 接收worker脚本作为prop
const props = defineProps<{
  workerScript?: string
}>()

const files = ref<File[]>([])
const processing = ref(false)
const progress = ref(0)
const results = ref<ProcessResult[]>([])

function handleFileChange(newFiles: File[]) {
  files.value = newFiles
  results.value = []
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
    for (let i = 0; i < files.value.length; i++) {
      const result = await processFile(files.value[i], props.workerScript)
      results.value.push(result)
      progress.value = Math.round(((i + 1) / files.value.length) * 100)
    }
    message.success('处理完成！')
  } catch (error) {
    message.error('处理失败: ' + (error as Error).message)
  } finally {
    processing.value = false
  }
}
</script>
```

### 4. 创建worker.py脚本

```python
import time
import io
from openpyxl import load_workbook

def process(data):
    """
    处理Excel文件
    
    参数:
        data: 包含file(bytes)和params(dict)的字典
    
    返回:
        包含success、buffer、logs、details的字典
    """
    logs = []
    start_time = time.time()
    
    try:
        logs.append("开始处理文件...")
        
        # 获取文件数据
        file_bytes = data.get('file')
        if not file_bytes:
            raise ValueError("未提供文件数据")
        
        # 加载Excel文件
        wb = load_workbook(io.BytesIO(file_bytes))
        
        # TODO: 实现你的处理逻辑
        # 例如：遍历工作表、修改单元格等
        
        # 保存到内存
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        result_bytes = output.read()
        
        # 计算处理时间
        processing_time = int((time.time() - start_time) * 1000)
        
        logs.append(f"处理完成！处理时间: {processing_time}ms")
        
        return {
            'success': True,
            'buffer': result_bytes,
            'logs': logs,
            'details': {
                'statistics': {
                    'processingTime': processing_time
                    # 添加其他统计信息
                }
            }
        }
        
    except Exception as e:
        logs.append(f"错误: {str(e)}")
        return {
            'success': False,
            'logs': logs,
            'error': str(e)
        }
```

### 5. 注册插件

在`packages/renderer/src/plugins.ts`中添加：

```typescript
// 导入插件
import YourPlugin from '../../plugins/your-plugin-name/index.vue'
import yourPluginManifest from '../../plugins/your-plugin-name/manifest.json'
import yourPluginWorker from '../../plugins/your-plugin-name/worker.py?raw'

// 在plugins数组中添加
const plugins: PluginInstance[] = [
  // ... 其他插件
  {
    metadata: yourPluginManifest,
    component: YourPlugin,
    worker: yourPluginWorker,
    route: `/plugin/${yourPluginManifest.key}`,
    state: PluginState.UNLOADED
  }
]
```

## API参考

### FileUpload组件

```typescript
// Props
interface FileUploadProps {
  multiple?: boolean  // 是否支持多文件
  accept?: string     // 接受的文件类型
}

// Events
@change: (files: File[]) => void  // 文件选择变化
```

### processFile函数

```typescript
async function processFile(
  file: File,
  worker: string,
  params?: any
): Promise<ProcessResult>

interface ProcessResult {
  success: boolean
  fileName: string
  buffer?: ArrayBuffer
  logs: string[]
  statistics?: Record<string, any>
  error?: string
}
```

### downloadResult函数

```typescript
async function downloadResult(
  result: ProcessResult,
  fileName?: string
): Promise<void>
```

## Python Worker规范

### 输入格式

```python
data = {
    'file': bytes,           # 文件二进制数据
    'fileName': str,         # 文件名
    'params': dict          # 自定义参数
}
```

### 输出格式

```python
# 成功
{
    'success': True,
    'buffer': bytes,         # 处理后的文件数据
    'logs': [str],          # 日志列表
    'details': {
        'statistics': {     # 统计信息
            'key': value
        }
    }
}

# 失败
{
    'success': False,
    'logs': [str],
    'error': str            # 错误信息
}
```

## 最佳实践

### 1. 错误处理
- 始终使用try-except捕获异常
- 提供清晰的错误消息
- 记录详细的日志

### 2. 性能优化
- 对于大文件，考虑流式处理
- 避免在内存中保存多个文件副本
- 使用进度回调提供反馈

### 3. 用户体验
- 提供清晰的功能说明
- 显示处理进度
- 提供详细的统计信息
- 支持批量处理

### 4. 代码质量
- 遵循TypeScript和Python的最佳实践
- 添加适当的注释
- 保持代码简洁和可维护

## 常用Python库

- `openpyxl`: Excel文件读写（.xlsx）
- `xlrd`: 读取旧版Excel文件（.xls）
- `pandas`: 数据处理和分析
- `Pillow`: 图片处理
- `re`: 正则表达式

## 调试技巧

1. **查看日志**: 在worker.py中使用logs.append()记录调试信息
2. **浏览器控制台**: 查看JavaScript错误和日志
3. **Pyodide控制台**: 在浏览器中直接测试Python代码
4. **分步测试**: 先测试小文件，再测试大文件

## 示例插件

参考`plugins/remove-empty-row/`目录查看完整的插件实现示例。

## 常见问题

### Q: 如何添加自定义参数？
A: 在Vue组件中收集参数，通过processFile的第三个参数传递。

### Q: 如何处理非Excel文件？
A: 在worker.py中根据文件扩展名使用不同的处理逻辑。

### Q: 如何优化大文件处理？
A: 考虑使用流式处理、分块处理或Web Worker。

### Q: 如何添加单元测试？
A: 在`tests/`目录下创建对应的测试文件。

---

**需要帮助？** 查看现有插件代码或联系开发团队。
