# ✅ Import Error Fixed - openpyxl

## 错误原因

### 问题描述
```
Failed to resolve import "openpyxl" from "plugins/delete-replace-sheet/index.vue"
```

### 根本原因
**在浏览器端的 Vue 组件中直接尝试导入 Python 包**

```javascript
// ❌ 错误做法 - 在 Vue 组件中
const openpyxl = await import('openpyxl')
```

### 为什么会报错
1. `openpyxl` 是 **Python 包**，不是 JavaScript/npm 包
2. 浏览器环境无法直接 `import` Python 包
3. Vite 构建工具尝试解析导入时找不到对应的模块

---

## 正确的架构

### 项目中 Python 代码的执行方式

```
┌─────────────────┐
│  Vue Component  │  (浏览器端 JavaScript)
│   index.vue     │
└────────┬────────┘
         │
         │ 调用 runPy() 或 runPythonScript()
         ▼
┌─────────────────┐
│  Pyodide        │  (浏览器中的 Python 运行时)
│  Runtime        │
└────────┬────────┘
         │
         │ 执行 Python 代码
         ▼
┌─────────────────┐
│  worker.py      │  (Python 脚本)
│  + openpyxl     │  (Python 包)
└─────────────────┘
```

### 正确的代码模式

```javascript
// ✅ 正确做法 - 在 Vue 组件中
import { runPy } from '@/utils/py'

const loadSheetNames = async (file: File) => {
  const arrayBuffer = await file.arrayBuffer()
  const uint8Array = new Uint8Array(arrayBuffer)
  
  // Python 脚本
  const script = `
import openpyxl
from io import BytesIO

def get_sheet_names(file_data):
    wb = openpyxl.load_workbook(BytesIO(bytes(file_data)), read_only=True)
    return wb.sheetnames
  `
  
  // 通过 Pyodide 执行 Python 代码
  const result = await runPy(script, 'get_sheet_names', uint8Array, '{}')
  return result
}
```

---

## 修复内容

### 文件: `plugins/delete-replace-sheet/index.vue`

**修复前 (第178行)**:
```javascript
const openpyxl = await import('openpyxl')  // ❌ 错误
const arrayBuffer = await file.arrayBuffer()
const workbook = openpyxl.load_workbook(arrayBuffer)
```

**修复后**:
```javascript
// 使用 Pyodide 读取 Sheet 名称
const arrayBuffer = await file.arrayBuffer()
const uint8Array = new Uint8Array(arrayBuffer)

const script = `
import openpyxl
from io import BytesIO

def get_sheet_names(file_data):
    wb = openpyxl.load_workbook(BytesIO(bytes(file_data)), read_only=True)
    return wb.sheetnames
`

const result = await runPy(script, 'get_sheet_names', uint8Array, '{}')
```

---

## 验证结果

### 错误状态
- ❌ 之前: `Failed to resolve import "openpyxl"`
- ✅ 现在: 错误已解决，服务器继续运行

### 新发现的问题
服务器现在报告另一个文件的问题:
```
remove-macro/index.vue - At least one <template> or <script> is required
```

这是一个不同的问题（文件格式问题），说明 `delete-replace-sheet` 的导入错误已经成功修复。

---

## 经验教训

### 不要做的事
1. ❌ 在浏览器端 Vue 组件中直接导入 Python 包
2. ❌ 使用 `import('openpyxl')` 或 `import('pandas')` 等
3. ❌ 假设 Python 包可以像 npm 包一样导入

### 应该做的事
1. ✅ 所有 Python 代码通过 Pyodide 执行
2. ✅ 使用 `runPy()` 或 `runPythonScript()` 工具函数
3. ✅ 将 Python 逻辑放在字符串或 `worker.py` 文件中
4. ✅ 通过 Uint8Array 传递二进制数据给 Python

---

## 相关文件

- ✅ `plugins/delete-replace-sheet/index.vue` - 已修复
- 📝 `packages/renderer/src/utils/py.ts` - Python 执行工具
- 📝 `packages/renderer/src/utils/pyodide-manager.ts` - Pyodide 管理器

---

**状态**: ✅ 已修复  
**影响**: delete-replace-sheet 插件现在可以正确加载  
**下一步**: 修复 remove-macro/index.vue 的文件格式问题
