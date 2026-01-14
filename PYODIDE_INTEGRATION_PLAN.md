# Pyodide 集成完整步骤清单

## 1. 统一插件的 Python 接口规范

### 1.1 接口类型定义
- **函数式接口（推荐）**：
  ```python
  def process(data) -> dict:
      # data 结构: {file: bytes, fileName: str, settings: dict}
      return {
          "success": bool,
          "buffer": bytes | None,
          "logs": list[str],
          "details": dict | None
      }
  ```

- **脚本式接口（过渡用）**：
  ```python
  # 输入变量
  file_bytes = data['file']  # bytes
  file_name = data['fileName']  # str
  settings = data['settings']  # dict
  
  # 输出变量
  output = {
      "success": bool,
      "buffer": bytes | None,
      "logs": list[str],
      "details": dict | None
  }
  ```

### 1.2 现有插件接口统一改造
- ✅ `delete-duplicate-rows`: 已使用函数式接口，保持不变
- ✅ `delete-formula`: 已使用函数式接口，保持不变
- ✅ `generate-from-template`: 已使用函数式接口，保持不变
- ❌ `remove-empty-row`: 改为函数式接口
- ❌ `merge-excel`: 改为函数式接口，支持多文件输入
- ❌ `replace-content`: 改为函数式接口
- ❌ `import-rules`: 改为函数式接口
- ❌ `replace-picture`: 改为函数式接口
- ❌ `url-to-image`: 改为函数式接口

### 1.3 多文件处理接口规范
```python
# 合并Excel等多文件操作
def process(files, settings) -> dict:
    # files 结构: {fileName: bytes, ...}
    # settings: 处理设置
    return {
        "success": bool,
        "buffer": bytes | None,  # 合并后的文件
        "logs": list[str],
        "details": dict | None
    }
```

## 2. 完善 runPy 抽象（核心封装）

### 2.1 Pyodide 加载与管理
- 实现 Pyodide 懒加载机制
- 单例模式管理 Pyodide 实例
- 提供版本控制和缓存策略

### 2.2 依赖管理
- 实现按需安装依赖函数
- 预设依赖组合：
  - 基础Excel操作：`openpyxl`
  - 复杂数据处理：`openpyxl + pandas`
  - 图片处理：`PIL`
- 依赖安装状态管理

### 2.3 统一调用接口设计
```typescript
// 核心接口
export async function runPy(
  script: string, 
  data: RunPyInput
): Promise<RunPyOutput>;

// 输入类型定义
type RunPyInput = 
  | { type: 'single'; file: Uint8Array; fileName: string; settings: any }
  | { type: 'multiple'; files: Record<string, Uint8Array>; settings: any }
  | { type: 'other'; data: any };

// 输出类型定义
type RunPyOutput = {
  success: boolean;
  buffer?: ArrayBuffer;
  logs: string[];
  details?: any;
  error?: string;
};
```

### 2.4 调用路由逻辑
- 根据输入类型自动路由到不同调用方式
- 支持函数式和脚本式接口的自动适配
- 统一错误捕获和处理

## 3. 前端调用模式统一

### 3.1 统一调用流程
```javascript
// 1. 获取脚本
const script = await fetch(`/plugins/${pluginKey}/worker.py`).then(r => r.text());

// 2. 读取文件
const fileBuffer = await file.arrayBuffer();
const fileContent = new Uint8Array(fileBuffer);

// 3. 组装输入数据
const data = {
  type: 'single',
  file: fileContent,
  fileName: file.name,
  settings: pluginSettings
};

// 4. 调用 Python 处理
const result = await runPy(script, data);

// 5. 处理结果
if (result.success) {
  displayLogs(result.logs);
  triggerDownload(result.buffer, processedFileName);
} else {
  handleError(result.error, result.logs);
}
```

### 3.2 现有插件改造
- 统一所有插件的调用模式
- 实现文件读取和数据组装的工具函数
- 统一结果处理和用户反馈

## 4. 错误与日志规范

### 4.1 Python 端规范
- 所有异常必须捕获并记录到 logs
- 返回结果必须包含 `success` 字段
- 错误信息必须详细描述错误原因和位置
- 日志格式：`[时间] 级别: 消息`

### 4.2 前端端规范
- 统一错误展示格式
- 实现全局错误处理机制
- 提供详细的错误日志查看
- 控制按钮状态管理（禁用/Loading）

## 5. 性能与体验优化

### 5.1 Pyodide 加载优化
- 首次加载显示进度提示
- 实现 Pyodide 实例缓存
- 依赖预加载策略

### 5.2 文件处理优化
- 大文件分段处理
- 进度条实时更新
- 异步处理避免 UI 阻塞

### 5.3 用户体验增强
- 加载状态反馈
- 处理进度展示
- 操作取消功能
- 结果预览功能

## 6. 测试与验证

### 6.1 Python 单元测试
- 使用 `../test/test_excelbox_plugins.py` 进行本地测试
- 覆盖所有插件功能
- 验证接口规范一致性

### 6.2 前端集成测试
- 针对每个插件走一遍完整流程
- 使用 `../test` 目录下的测试文件
- 验证界面无报错
- 验证输出文件的正确性

### 6.3 性能测试
- 大文件处理性能测试
- Pyodide 加载时间测试
- 内存使用监控

## 7. Electron 打包与资源管理

### 7.1 Pyodide 资源管理
- 选择合适的 Pyodide 版本
- 考虑 CDN 加载 vs 本地打包
- 离线使用支持

### 7.2 依赖打包策略
- 预打包常用依赖
- 按需下载策略
- 缓存机制实现

### 7.3 打包配置
- 修改 Electron 打包配置
- 添加 Pyodide 资源到打包文件
- 验证打包后的功能完整性

## 实施计划

### 第一阶段（1-2天）
- 完成 runPy 核心封装
- 实现 Pyodide 懒加载和单例模式
- 统一 Python 接口规范文档

### 第二阶段（2-3天）
- 改造现有插件到统一接口
- 统一前端调用模式
- 实现基础错误和日志规范

### 第三阶段（2-3天）
- 性能和用户体验优化
- 完善测试和验证
- 处理 Electron 打包配置

### 第四阶段（1-2天）
- 全面测试和调试
- 文档完善
- 最终验证

## 注意事项

1. **版本兼容性**：确保 Pyodide 版本与依赖库兼容
2. **性能监控**：关注大文件处理时的内存使用
3. **错误边界**：处理各种异常情况，提供友好反馈
4. **用户体验**：避免长时间阻塞 UI，提供进度反馈
5. **可维护性**：保持代码结构清晰，文档完善