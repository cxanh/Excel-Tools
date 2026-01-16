// Python脚本执行工具函数
import {
  pyodideManager,
  type RunPyInput,
  type RunPyOutput,
  type PyodideConfig,
} from "./pyodide-manager";

// 默认配置
const defaultConfig: PyodideConfig = {
  version: "0.24.1",
  loadMode: "cdn",
  localIndexURL: "/pyodide/v0.24.1/full/",
  cdnIndexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/",
  fallbackMode: "local",
  retryAttempts: 3,
  timeout: 30000,
};

// 初始化状态
let isInitialized = false;

/**
 * 初始化Pyodide环境
 */
export async function initPyodide(
  config?: Partial<PyodideConfig>,
): Promise<void> {
  if (isInitialized) {
    return;
  }

  const finalConfig = { ...defaultConfig, ...config };

  try {
    await pyodideManager.initialize(finalConfig);
    isInitialized = true;
  } catch (error) {
    console.error("Pyodide初始化失败:", error);
    throw error;
  }
}

/**
 * 运行Python脚本
 */
export async function runPy(
  script: string,
  input: RunPyInput,
  options?: {
    timeout?: number;
    dependencies?: string[];
    onProgress?: (progress: number) => void;
    onLog?: (log: string) => void;
  },
): Promise<RunPyOutput> {
  // 确保Pyodide已初始化
  if (!isInitialized) {
    await initPyodide();
  }

  try {
    // 安装依赖
    if (options?.dependencies && options.dependencies.length > 0) {
      for (const dep of options.dependencies) {
        await pyodideManager.installPackage(dep);
      }
    }

    // 执行脚本
    const result = await pyodideManager.runPython(
      script,
      input,
      options?.timeout || 60000,
    );

    // 触发日志回调
    if (options?.onLog && result.logs) {
      result.logs.forEach((log) => options.onLog!(log));
    }

    return result;
  } catch (error) {
    console.error("Python脚本执行失败:", error);
    return {
      success: false,
      logs: [],
      error: (error as Error).message,
    };
  }
}

/**
 * 检查Pyodide是否就绪
 */
export function isPyodideReady(): boolean {
  return pyodideManager.isReady();
}

/**
 * 预加载常用Python包
 */
export async function preloadCommonPackages(): Promise<void> {
  const commonPackages = ["micropip"];

  try {
    await pyodideManager.installPackages(commonPackages);
    console.log("常用Python包预加载完成");
  } catch (error) {
    console.error("预加载Python包失败:", error);
  }
}

/**
 * 获取Pyodide实例（高级用法）
 */
export function getPyodide(): any {
  return pyodideManager.getPyodide();
}

/**
 * 浏览器兼容的 base64 解码函数
 */
function base64ToBuffer(base64: string): ArrayBuffer {
  const binaryString = atob(base64);
  const length = binaryString.length;
  const bytes = new Uint8Array(length);

  for (let i = 0; i < length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }

  return bytes.buffer;
}

// 导入所有插件的 Python 脚本
import removeEmptyRowWorker from "@plugins/remove-empty-row/worker.py?raw";
import removeDuplicateRowWorker from "@plugins/remove-duplicate-row/worker.py?raw";
import modifyByRulesWorker from "@plugins/modify-by-rules/worker.py?raw";
import mergeExcelWorker from "@plugins/merge-excel/worker.py?raw";
import splitExcelWorker from "@plugins/split-excel/worker.py?raw";
import removeImageWorker from "@plugins/remove-image/worker.py?raw";
import replaceImageWorker from "@plugins/replace-image/worker.py?raw";
import urlToImageWorker from "@plugins/url-to-image/worker.py?raw";
import extractImageWorker from "@plugins/extract-image/worker.py?raw";
import removeFormulaWorker from "@plugins/remove-formula/worker.py?raw";
import generateFromTemplateWorker from "@plugins/generate-from-template/worker.py?raw";
import formatConverterWorker from "@plugins/format-converter/worker.py?raw";
import importRulesWorker from "@plugins/import-rules/worker.py?raw";
import extractContentWorker from "@plugins/extract-content/worker.py?raw";
import removeMacroWorker from "@plugins/remove-macro/worker.py?raw";
import setHeaderFooterWorker from "@plugins/set-header-footer/worker.py?raw";
import removeHeaderFooterWorker from "@plugins/remove-header-footer/worker.py?raw";
import addWatermarkWorker from "@plugins/add-watermark/worker.py?raw";
import addImageWatermarkWorker from "@plugins/add-image-watermark/worker.py?raw";
import modifyBackgroundWorker from "@plugins/modify-background/worker.py?raw";
import deleteReplaceSheetWorker from "@plugins/delete-replace-sheet/worker.py?raw";
import insertSheetWorker from "@plugins/insert-sheet/worker.py?raw";
import csvSplitWorker from "@plugins/csv-split/worker.py?raw";
import csvMergeWorker from "@plugins/csv-merge/worker.py?raw";
import clearMetadataWorker from "@plugins/clear-metadata/worker.py?raw";
import modifyMetadataWorker from "@plugins/modify-metadata/worker.py?raw";
import manageProtectionWorker from "@plugins/manage-protection/worker.py?raw";
import optimizeExcelWorker from "@plugins/optimize-excel/worker.py?raw";

// 插件脚本映射表
const pluginWorkers: Record<string, string> = {
  "remove-empty-row": removeEmptyRowWorker,
  "remove-duplicate-row": removeDuplicateRowWorker,
  "modify-by-rules": modifyByRulesWorker,
  "merge-excel": mergeExcelWorker,
  "split-excel": splitExcelWorker,
  "remove-image": removeImageWorker,
  "replace-image": replaceImageWorker,
  "url-to-image": urlToImageWorker,
  "extract-image": extractImageWorker,
  "remove-formula": removeFormulaWorker,
  "generate-from-template": generateFromTemplateWorker,
  "format-converter": formatConverterWorker,
  "import-rules": importRulesWorker,
  "extract-content": extractContentWorker,
  "remove-macro": removeMacroWorker,
  "set-header-footer": setHeaderFooterWorker,
  "remove-header-footer": removeHeaderFooterWorker,
  "add-watermark": addWatermarkWorker,
  "add-image-watermark": addImageWatermarkWorker,
  "modify-background": modifyBackgroundWorker,
  "delete-replace-sheet": deleteReplaceSheetWorker,
  "insert-sheet": insertSheetWorker,
  "csv-split": csvSplitWorker,
  "csv-merge": csvMergeWorker,
  "clear-metadata": clearMetadataWorker,
  "modify-metadata": modifyMetadataWorker,
  "manage-protection": manageProtectionWorker,
  "optimize-excel": optimizeExcelWorker,
};

/**
 * 运行Python脚本（兼容旧插件）
 */
export async function runPythonScript(
  script: string,
  input: any,
  options?: any,
): Promise<any> {
  // 转换输入格式
  const runPyInput: RunPyInput = {
    file: input.fileData ? base64ToBuffer(input.fileData) : undefined,
    fileName: input.fileName || "file.xlsx",
    params: input,
  };

  // 获取插件对应的Python脚本
  let pythonScript = script;
  if (pluginWorkers[script]) {
    pythonScript = pluginWorkers[script];
  }

  // 构建完整的Python执行脚本
  const fullScript = `
import sys
import io
from types import SimpleNamespace

# 模拟模块
sys.modules['__main__'] = SimpleNamespace()

# 执行插件脚本
${pythonScript}

# 调用process函数
output = process(input_data)
  `;

  // 执行Python脚本
  const result = await runPy(fullScript, runPyInput, options);

  // 转换输出格式以兼容旧插件
  return {
    success: result.success,
    data: result.buffer,
    error: result.error,
    logs: result.logs,
    statistics: result.details?.statistics,
    size: result.buffer?.byteLength || 0,
    emptyRowsDeleted: result.details?.statistics?.deletedRows || 0,
  };
}
