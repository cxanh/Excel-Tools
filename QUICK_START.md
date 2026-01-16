# Excel工具箱 - 快速开始指南

## 前置要求

- Node.js 18+ 
- npm 或 yarn

## 安装步骤

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发环境

**方式一：分别启动（推荐）**

在第一个终端窗口启动Vite开发服务器：
```bash
npm run dev
```

在第二个终端窗口启动Electron：
```bash
npm run electron:dev
```

**方式二：使用并发启动（需要安装concurrently）**

```bash
npm install -D concurrently
```

然后在package.json中添加脚本：
```json
"scripts": {
  "start": "concurrently \"npm run dev\" \"npm run electron:dev\""
}
```

运行：
```bash
npm start
```

## 项目结构说明

```
excel-toolbox/
├── packages/
│   ├── main/          # Electron主进程
│   ├── preload/       # 预加载脚本
│   └── renderer/      # Vue3前端应用
├── plugins/           # 插件目录
└── scripts/           # 构建脚本
```

## 核心功能

### 已实现的功能

✅ **Electron主进程**
- 应用生命周期管理
- 窗口状态保存/恢复
- IPC通信
- 文件对话框

✅ **Pyodide环境**
- Python环境加载
- 依赖包管理
- 脚本执行

✅ **插件系统**
- 插件注册
- 动态路由
- 生命周期管理

✅ **文件处理**
- 文件验证
- 拖拽上传
- 批量处理
- 结果下载

✅ **错误处理**
- 全局错误捕获
- 用户友好提示
- 日志记录

✅ **配置管理**
- Pyodide配置
- 主题配置

## 开发插件

### 插件结构

```
plugins/your-plugin/
├── manifest.json    # 插件配置
├── index.vue        # Vue组件
└── worker.py        # Python脚本
```

### manifest.json示例

```json
{
  "key": "your-plugin",
  "name": "插件名称",
  "icon": "icon-name",
  "description": "插件描述",
  "author": "作者",
  "version": "1.0.0",
  "dependencies": ["openpyxl"]
}
```

### index.vue示例

```vue
<template>
  <div>
    <FileUpload @change="handleFileChange" />
    <a-button @click="handleProcess">处理</a-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FileUpload from '@/components/FileUpload.vue'
import { processFile } from '@/utils/file-service'
import workerScript from './worker.py?raw'

const files = ref<File[]>([])

function handleFileChange(newFiles: File[]) {
  files.value = newFiles
}

async function handleProcess() {
  if (files.value.length === 0) return
  
  const result = await processFile(files.value[0], workerScript)
  
  if (result.success) {
    // 处理成功
  }
}
</script>
```

### worker.py示例

```python
import io
import openpyxl

def process(data):
    file_content = data['file']
    file_name = data['fileName']
    logs = []
    
    try:
        wb = openpyxl.load_workbook(io.BytesIO(file_content))
        logs.append(f"成功加载: {file_name}")
        
        # 处理逻辑
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return {
            'success': True,
            'buffer': output.read(),
            'logs': logs
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'logs': logs
        }
```

## 构建生产版本

### 构建前端

```bash
npm run build
```

### 构建Electron应用

```bash
npm run electron:build
```

这将生成以下平台的安装包：
- Windows: NSIS安装程序和便携版
- macOS: DMG和ZIP
- Linux: AppImage和DEB

## 常见问题

### Q: Pyodide加载失败？
A: 检查网络连接，或修改`pyodide-config.json`使用本地模式。

### Q: 文件处理失败？
A: 检查文件格式是否支持（.xlsx, .xls, .csv），文件大小是否超过100MB。

### Q: 插件无法加载？
A: 检查manifest.json格式是否正确，依赖包是否已安装。

### Q: 开发模式下热重载不工作？
A: 确保Vite开发服务器正在运行（npm run dev）。

## 调试技巧

### 查看控制台日志

开发模式下，Electron会自动打开DevTools。

### 查看主进程日志

主进程日志会输出到启动Electron的终端窗口。

### 查看Pyodide日志

Pyodide相关日志会输出到浏览器控制台。

## 下一步

1. 阅读`IMPLEMENTATION_STATUS.md`了解已完成的功能
2. 查看`.kiro/specs/excel-toolbox-system/`目录下的需求和设计文档
3. 开始开发插件（参考`plugins/README.md`）
4. 运行测试确保功能正常

## 获取帮助

- 查看项目文档
- 查看设计文档：`.kiro/specs/excel-toolbox-system/design.md`
- 查看任务列表：`.kiro/specs/excel-toolbox-system/tasks.md`

祝开发愉快！🚀
