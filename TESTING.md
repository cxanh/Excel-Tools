# 测试指南

本文档说明如何测试 Excel 工具箱的前后端通信功能。

## 已完成的功能

✅ **阶段 1: 项目基础设施**
- 项目结构搭建完成
- 前后端通信机制实现完成
  - Python CLI 路由器（长连接模式）
  - Electron Python 桥接（实时进度更新）
  - 通信集成测试

## 测试方法

### 1. 运行 Python 后端单元测试

测试 CLI 路由器的基本功能：

```bash
# 运行所有单元测试
python -m pytest python-backend/tests/test_cli_router.py -v

# 运行特定测试
python -m pytest python-backend/tests/test_cli_router.py::TestCLIRouter::test_ping_command -v
```

**测试覆盖**：
- ✅ Ping 命令测试
- ✅ Echo 命令测试
- ✅ 缺少 action 字段的错误处理
- ✅ 未知 action 的错误处理
- ✅ 处理器异常的错误处理
- ✅ 进度消息测试

### 2. 运行集成测试

测试完整的前后端通信流程：

```bash
# 运行集成测试
python python-backend/tests/test_integration.py
```

**测试覆盖**：
- ✅ 后端启动测试
- ✅ Ping 命令通信测试
- ✅ Echo 命令通信测试
- ✅ 进度更新测试（5 步进度）
- ✅ 多个连续命令测试
- ✅ 错误处理测试

### 3. 运行 Electron 应用测试

启动完整的 Electron 应用进行手动测试：

```bash
# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

**测试步骤**：
1. 应用启动后，查看控制台是否显示 "后端启动成功"
2. 点击 "测试 Ping" 按钮，查看是否收到 pong 响应
3. 点击 "测试 Echo" 按钮，查看是否正确回显数据
4. 点击 "测试进度更新" 按钮，查看进度条是否正常更新（0% → 20% → 40% → 60% → 80% → 100%）
5. 查看消息日志，确认所有消息都被正确记录

## 测试结果

### 单元测试结果

```
================================ test session starts ================================
collected 6 items

python-backend/tests/test_cli_router.py::TestCLIRouter::test_ping_command PASSED [ 16%]
python-backend/tests/test_cli_router.py::TestCLIRouter::test_echo_command PASSED [ 33%]
python-backend/tests/test_cli_router.py::TestCLIRouter::test_missing_action PASSED [ 50%]
python-backend/tests/test_cli_router.py::TestCLIRouter::test_unknown_action PASSED [ 66%]
python-backend/tests/test_cli_router.py::TestCLIRouter::test_handler_exception PASSED [ 83%]
python-backend/tests/test_cli_router.py::TestProgressMessages::test_progress_command PASSED [100%]

================================= 6 passed in 0.39s =================================
```

### 集成测试结果

```
============================================================
Python 后端集成测试
============================================================

=== 测试 1: 后端启动 ===
✓ 后端启动成功

=== 测试 2: Ping 命令 ===
✓ Ping 命令测试通过

=== 测试 3: Echo 命令 ===
✓ Echo 命令测试通过

=== 测试 4: 进度更新 ===
✓ 进度更新测试通过

=== 测试 5: 多个连续命令 ===
✓ 多命令测试通过

=== 测试 6: 错误处理 ===
✓ 错误处理测试通过

============================================================
测试结果: 6 通过, 0 失败
============================================================
```

## 通信协议说明

### 消息格式

**命令格式（Electron → Python）**：
```json
{
  "action": "ping",
  "params": {
    "timestamp": 123456
  }
}
```

**进度消息格式（Python → Electron）**：
```json
{
  "type": "progress",
  "progress": 45,
  "message": "正在处理第 3/10 个文件",
  "data": {
    "step": 3,
    "total": 10
  }
}
```

**结果消息格式（Python → Electron）**：
```json
{
  "type": "result",
  "status": "success",
  "message": "操作完成",
  "data": {
    "output_file": "result.xlsx"
  }
}
```

**错误消息格式（Python → Electron）**：
```json
{
  "type": "result",
  "status": "error",
  "error_code": "FILE_NOT_FOUND",
  "message": "文件不存在"
}
```

### 启动消息格式（Python → Electron）：
```json
{
  "type": "startup",
  "status": "ready",
  "message": "Backend initialized successfully"
}
```

## 关键实现细节

### 1. Python 长连接模式

Python 后端在 Electron 启动时启动，保持运行直到应用关闭：

```python
# 主循环：持续监听 stdin
while True:
    line = sys.stdin.readline()
    if not line:
        break
    
    command = json.loads(line.strip())
    result = router.route(command)
    print(json.dumps(result), flush=True)
```

### 2. 日志分离

所有日志输出到 stderr，避免干扰 stdout 中的 JSON 数据：

```python
def log(message):
    """将日志输出到 stderr"""
    sys.stderr.write(f"[BACKEND] {message}\n")
    sys.stderr.flush()
```

### 3. 实时进度更新

Python 后端在长时间操作中实时发送进度消息：

```python
def send_progress(progress, message="", data=None):
    """发送进度消息到 stdout"""
    progress_msg = {
        "type": "progress",
        "progress": progress,
        "message": message
    }
    if data:
        progress_msg["data"] = data
    
    print(json.dumps(progress_msg), flush=True)
```

### 4. Electron 消息处理

Electron 主进程监听 Python 的 stdout，区分进度消息和结果消息：

```typescript
pythonProcess.stdout?.on('data', (data) => {
  const lines = data.toString().split('\n');
  for (const line of lines) {
    if (line.trim()) {
      const message = JSON.parse(line);
      
      // 转发消息到渲染进程
      if (mainWindow) {
        mainWindow.webContents.send('python-message', message);
      }
    }
  }
});
```

## 下一步

通信机制已经完成并通过测试。接下来可以开始实现核心功能模块：

- **阶段 2: 核心文件操作**
  - 任务 4: 实现文件加载模块
  - 任务 5: 实现文件保存模块

运行以下命令查看下一个任务：

```bash
# 查看任务列表
cat .kiro/specs/excel-toolkit-desktop/tasks.md
```
