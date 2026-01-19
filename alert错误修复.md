# Alert 错误修复 ✅

## 问题描述

应用启动后出现错误对话框：
```
A JavaScript error occurred in the main process

Uncaught Exception:
ReferenceError: alert is not defined
    at sendCommandToPython (C:\Users\12607\Desktop\excel工具箱—kiro版\dist-electron\main.js:87:3)
```

## 问题原因

在 `electron/main.ts` 的 `sendCommandToPython` 函数中使用了 `alert()` 函数：

```typescript
function sendCommandToPython(command: any): void {
  // ...
  console.log('command'+'第一次')
  alert('command'+'第一次')  // ❌ 错误：主进程中没有 alert
  // ...
}
```

**为什么会出错？**
- `alert()` 是浏览器/渲染进程的函数
- Electron 主进程是 Node.js 环境，没有 `alert()`
- 这是调试代码，应该被删除

## 解决方案

### 修复代码
删除了 `alert()` 和多余的调试代码：

```typescript
/**
 * 发送命令到 Python 后端
 */
function sendCommandToPython(command: any): void {
  if (!pythonProcess || !pythonProcess.stdin) {
    console.error('[MAIN] Python process not available');
    return;
  }
  
  const commandJson = JSON.stringify(command) + '\n';
  pythonProcess.stdin.write(commandJson);
}
```

### 修改内容
- ❌ 删除：`console.log('command'+'第一次')`
- ❌ 删除：`alert('command'+'第一次')`
- ❌ 删除：`console.log('[MAIN DEBUG] Sending raw command to Python:', ...)`
- ❌ 删除：`console.log('command'+'第二次')`
- ✅ 保留：基本的错误检查和命令发送

## 测试结果

### ✅ 应用启动成功
```
[MAIN] Starting Python backend: python
[PYTHON LOG] [BACKEND] Excel Toolkit Backend starting...
[PYTHON] {
  type: 'startup',
  status: 'ready',
  message: 'Backend initialized successfully'
}
[MAIN] Python backend started successfully
```

### ✅ 无错误对话框
- 应用正常启动
- 没有 JavaScript 错误
- 后端成功连接

## 调试建议

### 在主进程中调试
如果需要在主进程中调试，使用以下方法：

#### 1. 使用 console.log
```typescript
console.log('[MAIN]', 'Debug message:', data);
```

#### 2. 使用 Electron 的 dialog
```typescript
import { dialog } from 'electron';

dialog.showMessageBox({
  type: 'info',
  title: 'Debug',
  message: 'Debug message'
});
```

#### 3. 使用 Node.js 调试器
```bash
# 启动时添加调试标志
npm run dev -- --inspect
```

### 在渲染进程中调试
如果需要在渲染进程中调试：

#### 1. 使用 console.log
```typescript
console.log('Debug message:', data);
```

#### 2. 使用 alert（仅渲染进程）
```typescript
alert('Debug message');
```

#### 3. 使用开发者工具
- 按 F12 打开开发者工具
- 查看 Console 标签

## 最佳实践

### ✅ 推荐做法
1. **使用 console.log** - 适用于所有环境
2. **添加日志前缀** - 如 `[MAIN]`, `[RENDERER]`
3. **使用条件编译** - 生产环境移除调试代码
4. **使用日志库** - 如 electron-log

### ❌ 避免做法
1. **在主进程使用 alert** - 会导致错误
2. **在主进程使用 window** - 主进程没有 window 对象
3. **在主进程使用 document** - 主进程没有 DOM
4. **留下调试代码** - 应该在提交前删除

## 环境区分

### 主进程 (Main Process)
- **环境**: Node.js
- **可用**: console, require, fs, path, child_process
- **不可用**: window, document, alert, DOM APIs

### 渲染进程 (Renderer Process)
- **环境**: Chromium (类似浏览器)
- **可用**: console, window, document, alert, DOM APIs
- **可用**: 通过 preload 暴露的 API

## 条件编译示例

如果需要保留调试代码但只在开发环境运行：

```typescript
function sendCommandToPython(command: any): void {
  if (!pythonProcess || !pythonProcess.stdin) {
    console.error('[MAIN] Python process not available');
    return;
  }
  
  // 仅在开发环境输出详细日志
  if (process.env.NODE_ENV === 'development') {
    console.log('[MAIN DEBUG] Sending command:', command);
  }
  
  const commandJson = JSON.stringify(command) + '\n';
  pythonProcess.stdin.write(commandJson);
}
```

## 日志库推荐

### electron-log
```bash
npm install electron-log
```

```typescript
import log from 'electron-log';

// 自动区分主进程和渲染进程
log.info('Info message');
log.error('Error message');
log.debug('Debug message');

// 日志会保存到文件
// Windows: %USERPROFILE%\AppData\Roaming\<app name>\logs
```

## 总结

✅ **问题已解决**
- 删除了主进程中的 `alert()` 调用
- 清理了多余的调试代码
- 应用正常启动

🎯 **经验教训**
- 主进程和渲染进程是不同的环境
- 调试代码应该在提交前删除
- 使用 console.log 而不是 alert

📝 **建议**
- 使用日志库管理日志
- 区分开发和生产环境
- 添加适当的日志前缀

---

**修复时间**: 2026-01-19  
**状态**: ✅ 完全修复  
**应用状态**: 🟢 正常运行

