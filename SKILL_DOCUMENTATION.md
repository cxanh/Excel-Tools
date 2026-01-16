# Excel工具箱 - 技术文档

## 1. 项目概述

Excel工具箱是一个基于Electron + Vue3 + Pyodide的跨平台Excel处理工具，支持插件化开发模式，能够在浏览器环境中运行Python脚本处理Excel文件。

### 核心特性
- 🚀 **跨平台**：支持Windows、macOS、Linux
- 📦 **插件化架构**：热插拔设计，无需重编主程序
- 🐍 **Python支持**：基于Pyodide 0.24.1在浏览器中运行Python
- 💎 **现代前端**：Vue3 + Vite + Ant Design Vue构建
- 🎨 **自定义主题**：支持个性化主题配置
- 📂 **多文件处理**：支持拖拽上传和批量处理

## 2. 技术栈

| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **框架** | Electron | 27.3.11 | 桌面应用框架 |
| **前端** | Vue | 3.0.0 | 前端框架 |
| **构建工具** | Vite | 5.0.0 | 构建工具 |
| **UI组件库** | Ant Design Vue | 4.0.0 | UI组件库 |
| **路由** | Vue Router | 4.0.0 | 前端路由 |
| **Python环境** | Pyodide | 0.24.1 | 浏览器中运行Python |
| **打包工具** | electron-builder | 24.13.3 | 应用打包 |

## 3. 项目架构

### 3.1 目录结构

```
excelbox/
├─ packages/             # 核心代码
│  ├─ main/             # Electron主进程
│  │  └─ index.js       # 主进程入口
│  ├─ preload/          # 预加载脚本
│  │  └─ index.js       # 上下文桥接
│  └─ renderer/         # 渲染进程
│     └─ src/           # Vue应用源码
│        ├─ components/ # 通用组件
│        ├─ router/     # 路由配置
│        ├─ utils/      # 工具函数
│        ├─ views/      # 页面组件
│        ├─ App.vue     # 根组件
│        └─ main.js     # 渲染进程入口
├─ plugins/             # 插件目录
│  ├─ remove-empty-row/ # 删除空白行插件
│  ├─ replace-picture/  # 替换图片插件
│  └─ ...               # 其他插件
├─ dist/                # 构建输出目录
├─ package.json         # 项目配置
└─ vite.config.js       # Vite配置
```

### 3.2 核心模块

#### 3.2.1 主进程 (packages/main/index.js)
- 应用生命周期管理
- 窗口创建和管理
- 文件系统访问
- 原生API调用

#### 3.2.2 预加载脚本 (packages/preload/index.js)
- 安全的上下文桥接
- 主进程与渲染进程通信
- 权限控制

#### 3.2.3 渲染进程 (packages/renderer/src/)
- Vue3应用
- 用户界面
- 插件容器
- 文件上传和下载

#### 3.2.4 Pyodide集成 (packages/renderer/src/utils/py.ts)
- Python环境加载和管理
- Python脚本执行
- JavaScript与Python通信
- 依赖管理

## 4. 核心功能

### 4.1 Excel文件处理
- 支持.xlsx、.xls格式
- 拖拽上传
- 批量处理
- 进度跟踪

### 4.2 插件系统
- 热插拔设计
- 标准化接口
- 独立打包
- 版本控制

### 4.3 数据处理
- 行/列操作
- 内容替换
- 数据筛选
- 图片处理

### 4.4 结果管理
- 处理日志
- 结果预览
- 文件下载
- 历史记录

## 5. 插件开发

### 5.1 插件结构

```
plugin-name/
├─ index.vue        # Vue组件
├─ manifest.json    # 插件配置
└─ worker.py        # Python处理脚本
```

### 5.2 插件配置 (manifest.json)

```json
{
  "key": "remove-empty-row",
  "name": "删除空白行",
  "icon": "delete-row",
  "description": "删除Excel中的所有空白行",
  "author": "Developer",
  "version": "1.0.0",
  "dependencies": ["openpyxl"]
}
```

### 5.3 Vue组件 (index.vue)

```vue
<template>
  <PluginTemplate
    plugin-title="删除空白行"
    info-message="删除Excel中的所有空白行"
    :current-step="currentStep"
    @add-file="handleAddFile"
    @import-folder="handleImportFromFolder"
    @more-action="handleMoreAction"
    @next-step="handleNextStep"
    @prev-step="handlePrevStep"
    @remove-file="handleRemoveFile"
    ref="pluginTemplate"
  />
  <!-- 插件内容 -->
</template>

<script setup>
import { ref } from 'vue'
import PluginTemplate from '@/components/PluginTemplate.vue'
import { runPy } from '@/utils/py'

// 插件逻辑
</script>
```

### 5.4 Python脚本 (worker.py)

```python
import io
import openpyxl

def process(data):
    file_content = data['file']
    file_name = data['fileName']
    logs = []
    
    try:
        # 加载Excel文件
        wb = openpyxl.load_workbook(io.BytesIO(file_content), read_only=False)
        logs.append(f"成功加载Excel文件: {file_name}")
        
        # 处理逻辑
        # ...
        
        # 返回结果
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return {
            'success': True,
            'buffer': output.read(),
            'logs': logs,
            'details': {
                'statistics': {
                    'totalRows': total_rows,
                    'deletedRows': deleted_rows
                }
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'logs': logs
        }
```

### 5.5 插件API

#### 插件生命周期
- `onInit()`: 插件初始化
- `onFileAdded(file)`: 文件添加时调用
- `onProcessStart()`: 处理开始时调用
- `onProcessComplete(result)`: 处理完成时调用
- `onDestroy()`: 插件销毁时调用

#### 工具函数
```javascript
import { runPy } from '@/utils/py'

// 运行Python脚本
const result = await runPy(script, input, options)
```

## 6. 核心API

### 6.1 Pyodide集成

#### `runPy(script, input, options)`

运行Python脚本处理数据

**参数**:
- `script`: Python脚本内容（字符串）
- `input`: 输入数据（RunPyInput类型）
- `options`: 可选配置（加载回调、超时等）

**返回值**:
```typescript
interface RunPyOutput {
  success: boolean;        // 是否成功
  buffer?: ArrayBuffer;    // 处理后的文件缓冲区
  logs: string[];         // 处理日志
  details?: any;          // 详细结果
  error?: string;         // 错误信息
}
```

### 6.2 文件处理

#### `loadPyodide(options)`

加载Pyodide环境

**参数**:
- `options`: 配置选项（版本、索引URL等）

**返回值**:
- Pyodide环境实例

### 6.3 插件管理

#### `registerPlugin(plugin)`

注册新插件

**参数**:
- `plugin`: 插件对象

#### `unregisterPlugin(pluginKey)`

卸载插件

**参数**:
- `pluginKey`: 插件唯一标识

## 7. 开发指南

### 7.1 环境准备

```bash
# 安装依赖
npm install
```

### 7.2 开发模式

```bash
# 启动Vite开发服务器
npm run dev

# 在新终端启动Electron
npm run electron:dev
```

### 7.3 构建生产版本

```bash
# 构建Vue前端
npm run build

# 构建Electron应用
npm run electron:build
```

### 7.4 插件开发流程

1. 在`plugins/`目录下创建插件文件夹
2. 创建`manifest.json`配置文件
3. 编写Vue组件`index.vue`
4. 编写Python处理脚本`worker.py`
5. 测试插件功能
6. 发布插件

## 8. 已实现插件

### 8.1 删除空白行 (remove-empty-row)
- 支持批量处理Excel文件
- 自动识别和删除空白行
- 显示处理进度和统计信息
- 支持下载处理后的文件

### 8.2 替换图片 (replace-picture)
- 支持Excel中图片替换
- 图片预览功能
- 批量替换支持
- 处理日志记录

### 8.3 按规则修改内容 (replace-content)
- 支持普通文本和正则表达式替换
- 多规则批量处理
- 自定义处理范围
- 详细处理统计

### 8.4 导入规则 (import-rules)
- 支持从文件导入处理规则
- 规则预览和编辑
- 批量应用规则

### 8.5 删除公式 (delete-formula)
- 删除Excel中的公式
- 保留计算结果
- 批量处理支持

### 8.6 删除重复行 (delete-duplicate-rows)
- 识别和删除重复行
- 自定义重复判断列
- 处理统计信息

### 8.7 生成Excel (generate-from-template)
- 基于模板生成Excel
- 批量数据导入
- 格式保留

### 8.8 合并Excel (merge-excel)
- 多Excel文件合并
- 自定义合并规则
- 工作表管理

## 9. 配置管理

### 9.1 Pyodide配置 (pyodide-config.json)

```json
{
  "version": "0.24.1",
  "loadMode": "cdn",
  "localIndexURL": "/pyodide/v0.24.1/full/", 
  "cdnIndexURL": "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/",
  "fallbackMode": "local",
  "retryAttempts": 3,
  "timeout": 30000
}
```

### 9.2 主题配置

```javascript
// src/theme.ts
export const theme = {
  token: {
    colorPrimary: '#165DFF',
    borderRadius: 4,
  },
};
```

## 10. 性能优化

### 10.1 Pyodide加载优化
- 使用CDN加速
- 预加载常用依赖
- 按需加载Python包

### 10.2 文件处理优化
- 流式处理大文件
- 内存管理
- 并行处理支持

### 10.3 UI性能
- 虚拟滚动
- 组件懒加载
- 异步渲染

## 11. 安全措施

### 11.1 Electron安全
- 启用contextIsolation
- 使用contextBridge
- 禁用nodeIntegration
- 内容安全策略(CSP)

### 11.2 Python安全
- 沙箱环境运行
- 限制文件系统访问
- 网络请求控制

## 12. 故障排查

### 12.1 Pyodide加载失败
- 检查网络连接
- 验证版本配置
- 查看浏览器控制台

### 12.2 文件处理错误
- 检查文件格式
- 验证Python脚本
- 查看处理日志

### 12.3 插件加载失败
- 检查manifest.json格式
- 验证插件依赖
- 查看浏览器控制台

## 13. 后续规划

- ✅ 完善现有插件功能
- ✅ 增加更多实用插件
- ✅ 优化Pyodide加载速度
- ✅ 支持本地Python环境
- ✅ 实现插件市场
- ✅ 增加数据可视化功能
- ✅ 支持更多文件格式

## 14. 许可证

ISC License

## 15. 贡献

欢迎提交Issue和Pull Request！

### 贡献指南
1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 16. 联系方式

如有问题或建议，请通过以下方式联系：

- Email: developer@example.com
- GitHub: [https://github.com/excelbox/excelbox](https://github.com/excelbox/excelbox)

---

**文档更新时间**: 2026-01-15
**文档版本**: 1.0.0