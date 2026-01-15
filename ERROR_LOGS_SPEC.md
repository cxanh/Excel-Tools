# 错误与日志规范

## 1. Python 端规范

### 1.1 日志格式

```python
# 日志格式：[时间] [级别] [模块] 消息
# 示例：
logs.append("[2024-01-14 15:30:25] [INFO] [ExcelHandler] 成功加载文件: example.xlsx")
logs.append("[2024-01-14 15:30:26] [DEBUG] [ExcelHandler] 处理工作表: Sheet1")
logs.append("[2024-01-14 15:30:27] [ERROR] [ExcelHandler] 单元格处理失败: A1")
```

### 1.2 日志级别

- **INFO**: 一般信息，如文件加载、处理完成等
- **DEBUG**: 调试信息，如工作表名称、处理的单元格范围等
- **WARN**: 警告信息，如跳过空行、格式不规范等
- **ERROR**: 错误信息，如文件格式错误、权限问题等

### 1.3 错误处理

```python
def process(data):
    logs = []
    try:
        # 业务逻辑
        logs.append("[INFO] 开始处理文件")
        # ... 处理代码 ...

        return {
            "success": True,
            "buffer": processed_file_bytes,
            "logs": logs,
            "details": {
                "totalSheets": len(workbook.sheetnames),
                "totalCells": total_cells_processed,
                "totalReplacements": replacement_count
            }
        }

    except FileNotFoundError as e:
        logs.append(f"[ERROR] 文件未找到: {str(e)}")
        return {
            "success": False,
            "logs": logs,
            "error": f"文件未找到: {str(e)}"
        }

    except ValueError as e:
        logs.append(f"[ERROR] 数值错误: {str(e)}")
        return {
            "success": False,
            "logs": logs,
            "error": f"数值错误: {str(e)}"
        }

    except Exception as e:
        logs.append(f"[ERROR] 处理失败: {str(e)}")
        return {
            "success": False,
            "logs": logs,
            "error": f"处理失败: {str(e)}"
        }
```

### 1.4 现有Python脚本改造要求

1. 所有异常必须捕获并记录到logs
2. 返回结果必须包含`success`字段
3. 错误信息必须详细描述错误原因和位置
4. 日志必须包含时间戳和级别

## 2. 前端规范

### 2.1 错误处理模式

```javascript
try {
  const result = await runPy(script, processingData);

  if (result.success) {
    // 处理成功
    logs.value.push(...result.logs);

    if (result.buffer) {
      // 处理文件下载
      handleDownload(result.buffer, fileName);
    }
  } else {
    // 处理失败
    logs.value.push("[ERROR] 处理失败:");
    logs.value.push(...result.logs);
    logs.value.push(`[ERROR] 错误原因: ${result.error}`);

    // 显示错误提示
    message.error(`处理失败: ${result.error}`);
  }
} catch (error) {
  // 捕获JS层面的错误
  logs.value.push(`[ERROR] 执行错误: ${error.message}`);
  message.error(`执行错误: ${error.message}`);
}
```

### 2.2 按钮状态管理

```javascript
const isProcessing = ref(false);

const handleProcess = async () => {
  isProcessing.value = true;

  try {
    // 处理逻辑
    await processFiles();
  } finally {
    isProcessing.value = false;
  }
};

// 模板中使用
<a-button type="primary" :loading="isProcessing" @click="handleProcess">
  开始处理
</a-button>
```

### 2.3 日志展示

```vue
<div class="logs-container">
  <a-list bordered :data-source="logs" size="small">
    <template #renderItem="{ item }">
      <a-list-item :class="getLogClass(item)">
        {{ item }}
      </a-list-item>
    </template>
  </a-list>
</div>

<script>
const getLogClass = (log) => {
  if (log.includes("[ERROR]")) return "log-error";
  if (log.includes("[WARN]")) return "log-warning";
  if (log.includes("[DEBUG]")) return "log-debug";
  return "log-info";
};
</script>

<style>
.log-error {
  color: #ff4d4f;
}
.log-warning {
  color: #faad14;
}
.log-info {
  color: #1890ff;
}
.log-debug {
  color: #52c41a;
}
</style>
```

### 2.4 错误提示

```javascript
import { message } from "ant-design-vue";

// 显示错误提示
message.error("处理失败，请检查文件格式");

// 显示成功提示
message.success("处理完成");

// 显示加载提示
const loading = message.loading("处理中...", 0);
try {
  await processFiles();
  loading(); // 关闭加载提示
  message.success("处理完成");
} catch (error) {
  loading(); // 关闭加载提示
  message.error(`处理失败: ${error.message}`);
}
```

## 3. 统一错误码（可选）

| 错误码 | 描述           | 示例                    |
| ------ | -------------- | ----------------------- |
| 10001  | 文件格式错误   | 文件不是有效的Excel格式 |
| 10002  | 权限问题       | 无法读取/写入文件       |
| 10003  | 内存不足       | 处理大文件时内存不足    |
| 10004  | 依赖缺失       | 缺少必要的Python库      |
| 20001  | 单元格处理错误 | 无法处理特定单元格      |
| 20002  | 工作表不存在   | 指定的工作表不存在      |
| 30001  | 网络错误       | Pyodide加载失败         |
| 30002  | 脚本执行错误   | Python脚本语法错误      |

## 4. 现有前端代码改造要求

1. 统一使用`message`组件显示错误和成功提示
2. 所有异步操作必须有加载状态
3. 错误信息必须清晰可见
4. 日志展示必须有不同级别的样式区分
5. 按钮在处理过程中必须禁用，避免重复点击
