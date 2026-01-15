// Pyodide 集成工具模块
import { loadPyodide } from "pyodide";

// Pyodide 配置类型
interface PyodideConfig {
  version: string;
  loadMode: "cdn" | "local";
  localIndexURL: string;
  cdnIndexURL: string;
  fallbackMode: "local" | "cdn";
  retryAttempts: number;
  timeout: number;
}

// 默认配置
const DEFAULT_CONFIG: PyodideConfig = {
  version: "0.24.1",
  loadMode: "cdn",
  localIndexURL: "/pyodide/v0.24.1/full/",
  cdnIndexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/",
  fallbackMode: "local",
  retryAttempts: 3,
  timeout: 30000,
};

// 加载配置文件
async function loadConfig(): Promise<PyodideConfig> {
  try {
    const response = await fetch("/pyodide-config.json");
    if (response.ok) {
      const config = await response.json();
      return { ...DEFAULT_CONFIG, ...config };
    }
  } catch (error) {
    console.warn("无法加载 pyodide-config.json，使用默认配置:", error);
  }
  return DEFAULT_CONFIG;
}

// 类型定义
export type RunPyInput =
  | { type: "single"; file: Uint8Array; fileName: string; settings: any }
  | { type: "multiple"; files: Record<string, Uint8Array>; settings: any }
  | { type: "other"; data: any };

export type RunPyOutput = {
  success: boolean;
  buffer?: ArrayBuffer;
  logs: string[];
  details?: any;
  error?: string;
};

// 加载状态回调类型
export type LoadingCallback = (
  stage: string,
  progress: number,
  message?: string,
) => void;

// 日志级别枚举
export enum LogLevel {
  DEBUG = "DEBUG",
  INFO = "INFO",
  WARNING = "WARNING",
  ERROR = "ERROR",
  CRITICAL = "CRITICAL",
}

// 日志项类型
interface LogItem {
  timestamp: string;
  level: LogLevel;
  module: string;
  message: string;
  details?: any;
}

// 增强的日志记录函数
function log(
  level: LogLevel,
  module: string,
  message: string,
  details?: any,
): string {
  const timestamp = new Date().toISOString();
  const logItem: LogItem = {
    timestamp,
    level,
    module,
    message,
    details,
  };

  // 格式化日志输出
  const formattedLog = `${timestamp} [${level}] [${module}] ${message}${details ? ` - ${safeStringify(details)}` : ""}`;

  // 根据日志级别输出到控制台
  switch (level) {
    case LogLevel.DEBUG:
      console.debug(formattedLog);
      break;
    case LogLevel.INFO:
      console.info(formattedLog);
      break;
    case LogLevel.WARNING:
      console.warn(formattedLog);
      break;
    case LogLevel.ERROR:
      console.error(formattedLog);
      break;
    case LogLevel.CRITICAL:
      console.error(formattedLog);
      break;
  }

  return formattedLog;
}

/**
 * 安全地将值转换为字符串，过滤特殊字符和内存地址
 * @param value 需要转换的值
 * @returns 安全的字符串
 */
function safeStringify(value: any): string {
  if (value === null || value === undefined) {
    return String(value);
  }

  if (typeof value === "string") {
    // 过滤字符串中的内存地址
    return value.replace(/0x[0-9a-fA-F]+/g, "[内存地址]");
  }

  if (typeof value === "object") {
    try {
      // 优先使用 message 属性
      if (value.message && typeof value.message === "string") {
        return safeStringify(value.message);
      }
      // 转换为 JSON 字符串
      return JSON.stringify(value).replace(/0x[0-9a-fA-F]+/g, "[内存地址]");
    } catch (e) {
      // 如果 JSON 转换失败，使用 toString
      return String(value).replace(/0x[0-9a-fA-F]+/g, "[内存地址]");
    }
  }

  // 其他类型直接转换
  return String(value);
}

// Pyodide 单例管理
class PyodideManager {
  private static instance: PyodideManager;
  private pyodide: any = null;
  private isLoading: boolean = false;
  private loadPromise: Promise<any> | null = null;
  private installedPackages: Set<string> = new Set();
  private loadingCallbacks: LoadingCallback[] = [];
  private loadAttempts: number = 0;
  private maxLoadAttempts: number = 3;
  private config: PyodideConfig | null = null;

  private constructor() {}

  public static getInstance(): PyodideManager {
    if (!PyodideManager.instance) {
      PyodideManager.instance = new PyodideManager();
    }
    return PyodideManager.instance;
  }

  // 获取配置
  private async getConfig(): Promise<PyodideConfig> {
    if (!this.config) {
      this.config = await loadConfig();
    }
    return this.config;
  }

  // 添加加载状态回调
  public addLoadingCallback(callback: LoadingCallback): void {
    this.loadingCallbacks.push(callback);
  }

  // 移除加载状态回调
  public removeLoadingCallback(callback: LoadingCallback): void {
    this.loadingCallbacks = this.loadingCallbacks.filter(
      (cb) => cb !== callback,
    );
  }

  // 触发加载状态回调
  private triggerLoadingCallback(
    stage: string,
    progress: number,
    message?: string,
  ): void {
    this.loadingCallbacks.forEach((callback) => {
      try {
        callback(stage, progress, message);
      } catch (error) {
        console.error("加载回调执行失败:", error);
      }
    });
  }

  // 懒加载 Pyodide
  public async loadPyodide(): Promise<any> {
    if (this.pyodide) {
      return this.pyodide;
    }

    if (this.isLoading && this.loadPromise) {
      return this.loadPromise;
    }

    this.isLoading = true;
    this.loadAttempts = 0;
    this.loadPromise = this.doLoadPyodideWithRetry();

    try {
      this.pyodide = await this.loadPromise;
      this.triggerLoadingCallback("complete", 100, "Python 环境初始化完成");
      return this.pyodide;
    } finally {
      this.isLoading = false;
      this.loadPromise = null;
    }
  }

  // 带重试机制的 Pyodide 加载
  private async doLoadPyodideWithRetry(): Promise<any> {
    while (this.loadAttempts < this.maxLoadAttempts) {
      this.loadAttempts++;
      try {
        return await this.doLoadPyodide();
      } catch (error) {
        console.error(
          `Pyodide 加载失败 (尝试 ${this.loadAttempts}/${this.maxLoadAttempts}):`,
          error,
        );
        if (this.loadAttempts >= this.maxLoadAttempts) {
          throw new Error(
            `Pyodide 加载失败，已重试 ${this.maxLoadAttempts} 次，请检查网络连接或稍后再试`,
          );
        }
        this.triggerLoadingCallback(
          "retry",
          0,
          `Pyodide 加载失败，正在重试 (${this.loadAttempts}/${this.maxLoadAttempts})...`,
        );
        // 等待一段时间后重试
        await new Promise((resolve) =>
          setTimeout(resolve, 2000 * this.loadAttempts),
        );
      }
    }
    throw new Error("Pyodide 加载失败，已超过最大重试次数");
  }

  private async doLoadPyodide(): Promise<any> {
    try {
      const config = await this.getConfig();
      this.maxLoadAttempts = config.retryAttempts;

      this.triggerLoadingCallback("init", 0, "正在初始化 Python 环境...");

      // 根据配置选择加载URL
      let indexURL =
        config.loadMode === "cdn" ? config.cdnIndexURL : config.localIndexURL;

      log(
        LogLevel.INFO,
        "PyodideManager",
        `正在从 ${config.loadMode} 模式加载 Pyodide v${config.version}`,
        indexURL,
      );

      // 分阶段加载，提供更详细的进度信息
      const pyodide = await loadPyodide({
        indexURL: indexURL,
        packages: [], // 不预加载包，改为按需加载
        onDownloadProgress: (progress: any) => {
          // 估计加载进度
          const estimatedProgress = Math.min(
            50,
            Math.round((progress.loaded / (progress.total || 1)) * 50),
          );
          this.triggerLoadingCallback(
            "download",
            estimatedProgress,
            `正在下载 Python 核心组件... ${Math.round(estimatedProgress)}%`,
          );
        },
      });

      this.triggerLoadingCallback("init", 50, "正在初始化 Python 解释器...");

      // 安装 micropip
      await pyodide.loadPackage("micropip");
      this.installedPackages.add("micropip");

      this.triggerLoadingCallback("init", 75, "正在配置 Python 环境...");

      // 预加载一些常用模块
      await pyodide.runPythonAsync("import sys, os, io, json, re");

      this.triggerLoadingCallback("init", 100, "Python 环境初始化完成");
      log(LogLevel.INFO, "PyodideManager", "Pyodide 加载完成");

      return pyodide;
    } catch (error) {
      const config = await this.getConfig();

      // 如果是CDN模式失败，尝试fallback到本地模式
      if (config.loadMode === "cdn" && config.fallbackMode === "local") {
        log(
          LogLevel.WARNING,
          "PyodideManager",
          "CDN加载失败，尝试使用本地资源",
          error,
        );
        this.triggerLoadingCallback(
          "fallback",
          0,
          "CDN加载失败，正在尝试本地资源...",
        );

        try {
          const pyodide = await loadPyodide({
            indexURL: config.localIndexURL,
            packages: [],
            onDownloadProgress: (progress: any) => {
              const estimatedProgress = Math.min(
                50,
                Math.round((progress.loaded / (progress.total || 1)) * 50),
              );
              this.triggerLoadingCallback(
                "download",
                estimatedProgress,
                `正在从本地加载 Python 核心组件... ${Math.round(estimatedProgress)}%`,
              );
            },
          });

          this.triggerLoadingCallback(
            "init",
            50,
            "正在初始化 Python 解释器...",
          );
          await pyodide.loadPackage("micropip");
          this.installedPackages.add("micropip");
          this.triggerLoadingCallback("init", 75, "正在配置 Python 环境...");
          await pyodide.runPythonAsync("import sys, os, io, json, re");
          this.triggerLoadingCallback("init", 100, "Python 环境初始化完成");
          log(LogLevel.INFO, "PyodideManager", "Pyodide 本地加载完成");
          return pyodide;
        } catch (fallbackError) {
          log(
            LogLevel.ERROR,
            "PyodideManager",
            "本地加载也失败",
            fallbackError,
          );
          this.triggerLoadingCallback(
            "error",
            0,
            `Pyodide 加载失败: ${safeStringify(fallbackError)}`,
          );
          throw fallbackError;
        }
      }

      this.triggerLoadingCallback(
        "error",
        0,
        `Pyodide 加载失败: ${safeStringify(error)}`,
      );
      log(LogLevel.ERROR, "PyodideManager", "Pyodide 加载失败", error);
      throw error;
    }
  }

  // 安装依赖包
  public async installPackages(packages: string[]): Promise<void> {
    const pyodide = await this.loadPyodide();
    const micropip = pyodide.pyimport("micropip");

    // 过滤已安装的包
    const packagesToInstall = packages.filter(
      (pkg) => !this.installedPackages.has(pkg),
    );

    if (packagesToInstall.length > 0) {
      this.triggerLoadingCallback(
        "install",
        0,
        `正在安装依赖包: ${packagesToInstall.join(", ")}...`,
      );
      log(
        LogLevel.INFO,
        "PyodideManager",
        `安装依赖: ${packagesToInstall.join(", ")}`,
      );

      // 分批安装包，避免一次性加载过多
      const batchSize = 3;
      for (let i = 0; i < packagesToInstall.length; i += batchSize) {
        const batch = packagesToInstall.slice(i, i + batchSize);
        const progress = Math.round((i / packagesToInstall.length) * 100);
        this.triggerLoadingCallback(
          "install",
          progress,
          `正在安装依赖包 (${i + 1}/${packagesToInstall.length})...`,
        );
        await micropip.install(batch);
        batch.forEach((pkg) => this.installedPackages.add(pkg));
      }

      this.triggerLoadingCallback("install", 100, "依赖包安装完成");
    }
  }

  // 检查 Pyodide 是否已加载
  public isLoaded(): boolean {
    return this.pyodide !== null;
  }

  // 获取安装的包列表
  public getInstalledPackages(): string[] {
    return Array.from(this.installedPackages);
  }

  // 清理资源
  public async dispose(): Promise<void> {
    if (this.pyodide) {
      try {
        // 执行清理操作
        await this.pyodide.runPythonAsync("import gc; gc.collect()");
        this.pyodide = null;
        this.installedPackages.clear();
        this.loadingCallbacks = [];
        log(LogLevel.INFO, "PyodideManager", "Pyodide 资源已清理");
      } catch (error) {
        log(LogLevel.ERROR, "PyodideManager", "清理 Pyodide 资源失败", error);
      }
    }
  }
}

// 预定义依赖组合
export const dependencyPresets = {
  basicExcel: ["openpyxl"],
  advancedExcel: ["openpyxl", "pandas"],
  imageProcessing: ["Pillow"],
  full: ["openpyxl", "pandas", "Pillow", "numpy"],
};

// 获取文件扩展名
export function getFileExtension(fileName: string): string {
  const lastDotIndex = fileName.lastIndexOf(".");
  if (lastDotIndex === -1) return "";
  return fileName.substring(lastDotIndex + 1).toLowerCase();
}

// 根据输入类型推断需要的依赖
function inferDependencies(input: RunPyInput): string[] {
  // 基础依赖
  let dependencies: string[] = [...dependencyPresets.basicExcel];

  // 如果是多文件处理，可能需要 pandas
  if (input.type === "multiple") {
    dependencies.push("pandas");
  }

  // 如果是图片相关操作，添加 PIL
  if (input.type === "other" && input.data?.replaceImage) {
    dependencies.push("Pillow");
  }

  // 去重
  return [...new Set(dependencies)];
}

// 主函数：运行 Python 脚本
export async function runPy(
  script: string,
  input: RunPyInput,
  options?: {
    loadingCallback?: LoadingCallback;
    timeout?: number;
    additionalDependencies?: string[];
  },
): Promise<RunPyOutput> {
  const manager = PyodideManager.getInstance();
  const logs: string[] = [];
  const startTime = Date.now();
  let timeoutId: NodeJS.Timeout | null = null;

  try {
    // 添加加载状态回调
    if (options?.loadingCallback) {
      manager.addLoadingCallback(options.loadingCallback);
    }

    // 设置超时
    if (options?.timeout) {
      const timeoutPromise = new Promise<never>((_, reject) => {
        timeoutId = setTimeout(() => {
          reject(new Error(`Python 脚本执行超时 (${options.timeout}ms)`));
        }, options.timeout);
      });

      // 同时执行 runPy 逻辑和超时检查
      return await Promise.race([
        timeoutPromise,
        doRunPy(manager, script, input, logs, options?.additionalDependencies),
      ]);
    } else {
      // 正常执行（无超时）
      return await doRunPy(
        manager,
        script,
        input,
        logs,
        options?.additionalDependencies,
      );
    }
  } catch (error: any) {
    log(LogLevel.ERROR, "runPy", "Pyodide 执行错误", error);
    const executionTime = Date.now() - startTime;
    return {
      success: false,
      logs: [
        ...logs,
        `执行错误: ${safeStringify(error.message)}`,
        `总执行时间: ${executionTime}ms`,
      ],
      error: safeStringify(error.message),
    };
  } finally {
    // 清理资源
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    if (options?.loadingCallback) {
      manager.removeLoadingCallback(options.loadingCallback);
    }
  }
}

// 内部执行函数
async function doRunPy(
  manager: PyodideManager,
  script: string,
  input: RunPyInput,
  logs: string[],
  additionalDependencies?: string[],
): Promise<RunPyOutput> {
  const startTime = Date.now();

  try {
    // 1. 加载 Pyodide
    const pyodide = await manager.loadPyodide();
    logs.push(`Pyodide 版本: ${pyodide.version}`);

    // 2. 推断并安装依赖
    let dependencies = inferDependencies(input);

    // 添加额外依赖
    if (additionalDependencies) {
      dependencies = [...new Set([...dependencies, ...additionalDependencies])];
    }

    if (dependencies.length > 0) {
      logs.push(`安装依赖: ${dependencies.join(", ")}...`);
      await manager.installPackages(dependencies);
      logs.push("依赖安装完成");
    }

    // 3. 准备输入数据
    let pyInput: any = {};

    if (input.type === "single") {
      pyInput = {
        file: input.file,
        fileName: input.fileName,
        settings: input.settings,
      };
    } else if (input.type === "multiple") {
      pyInput = {
        files: input.files,
        settings: input.settings,
      };
    } else {
      pyInput = input.data;
    }

    // 4. 准备执行上下文
    pyodide.globals.set("input_data", pyInput);

    // 5. 执行 Python 脚本
    logs.push("开始执行 Python 脚本...");
    logs.push(`脚本长度: ${script.length} 字符`);
    const scriptStartTime = Date.now();
    try {
      // 添加执行环境信息
      logs.push(`执行环境: ${input.type} 类型输入`);
      if (input.type === "single") {
        logs.push(`处理文件: ${input.fileName}`);
      } else if (input.type === "multiple") {
        logs.push(`处理文件数量: ${Object.keys(input.files).length}`);
      }

      await pyodide.runPythonAsync(script);
      logs.push(`Python 脚本执行完成，耗时: ${Date.now() - scriptStartTime}ms`);
    } catch (pythonError: any) {
      const errorMessage = safeStringify(pythonError.message);
      logs.push(`Python 脚本执行错误: ${errorMessage}`);

      // 错误分类和详细提示
      let errorCategory = "未知错误";
      if (errorMessage.includes("ModuleNotFoundError")) {
        errorCategory = "模块未找到错误";
        logs.push(
          "错误详情: 缺少必要的 Python 依赖包，请确保已正确安装所有依赖",
        );
      } else if (errorMessage.includes("FileNotFoundError")) {
        errorCategory = "文件未找到错误";
        logs.push("错误详情: 无法找到指定的文件，请检查文件路径是否正确");
      } else if (errorMessage.includes("PermissionError")) {
        errorCategory = "权限错误";
        logs.push("错误详情: 没有足够的权限访问文件，请检查文件权限设置");
      } else if (errorMessage.includes("ValueError")) {
        errorCategory = "数值错误";
        logs.push("错误详情: 输入参数无效或格式错误");
      } else if (errorMessage.includes("TypeError")) {
        errorCategory = "类型错误";
        logs.push("错误详情: 函数参数类型不匹配");
      } else if (errorMessage.includes("SyntaxError")) {
        errorCategory = "语法错误";
        logs.push("错误详情: Python 脚本语法错误，请检查脚本代码");
      }

      // 记录错误类型
      logs.push(`错误类型: ${errorCategory}`);

      if (pythonError.stack) {
        logs.push(`Python 错误堆栈: ${safeStringify(pythonError.stack)}`);
      }

      // 尝试获取更详细的 Python 错误信息
      try {
        if (pyodide.globals.has("sys")) {
          const sys = pyodide.globals.get("sys");
          if (sys.last_traceback) {
            logs.push("Python 详细堆栈跟踪:");
            // 将 Python 堆栈跟踪转换为字符串
            try {
              pyodide.runPython(`
import traceback
import sys
if hasattr(sys, 'last_traceback'):
    sys.last_traceback_str = ''.join(traceback.format_exception(*sys.exc_info()))
              `);
              if (
                pyodide.globals.has("sys") &&
                pyodide.globals.get("sys").last_traceback_str
              ) {
                let traceback = safeStringify(
                  pyodide.globals.get("sys").last_traceback_str,
                );
                // 过滤内存地址
                traceback = traceback.replace(/0x[0-9a-fA-F]+/g, "[内存地址]");
                logs.push(traceback);
              }
            } catch (e) {
              logs.push("无法获取详细堆栈跟踪");
            }
          }
        }
      } catch (e) {
        logs.push(`获取错误详情失败: ${safeStringify(e.message)}`);
      }

      // 记录执行时间
      const scriptExecutionTime = Date.now() - scriptStartTime;
      logs.push(`脚本执行失败，耗时: ${scriptExecutionTime}ms`);

      throw pythonError;
    }
    // 6. 获取执行结果
    let result: any = {};

    try {
      // 优先尝试标准 process 函数接口
      if (pyodide.globals.has("process")) {
        logs.push("调用标准 process 函数...");
        const processFn = pyodide.globals.get("process");
        try {
          result = processFn(pyInput);
        } catch (processError: any) {
          logs.push(`process 函数执行错误: ${processError.message}`);
          if (processError.stack) {
            logs.push(`process 函数错误堆栈: ${processError.stack}`);
          }
          throw processError;
        }
      }
      // 其次尝试 merge-excel 插件的接口
      else if (pyodide.globals.has("merge_excel_files")) {
        logs.push("调用 merge_excel_files 函数...");
        const mergeFn = pyodide.globals.get("merge_excel_files");
        if (input.type === "multiple") {
          result = mergeFn(input.files, input.settings || {});
        } else {
          throw new Error("merge_excel_files 函数需要 multiple 类型的输入");
        }
      }
      // 其次尝试 replace-content 插件的接口（process 函数应该已经存在）
      // replace_content_in_excel 是 process 的别名，统一使用 process 接口
      // 其次尝试脚本式接口
      else if (pyodide.globals.has("output")) {
        logs.push("读取脚本式 output 变量...");
        result = pyodide.globals.get("output");
      }
      // 如果都没有，尝试返回默认结果
      else {
        logs.push(
          "未找到标准 process 函数或 output 变量，尝试从标准输出获取结果...",
        );
        result = { success: true, logs: ["脚本执行完成"] };
      }
    } catch (error: any) {
      logs.push(`获取结果时出错: ${safeStringify(error.message)}`);
      throw error;
    }

    // 7. 转换结果格式
    const finalResult: RunPyOutput = {
      success: Boolean(result.success),
      logs: result.logs ? Array.from(result.logs) : logs,
      details: result.details
        ? JSON.parse(pyodide.globals.JSON.stringify(result.details))
        : undefined,
      error: result.error ? String(result.error) : undefined,
    };

    // 处理返回的文件缓冲区
    if (result.buffer) {
      logs.push("检测到返回的文件缓冲区");
      try {
        // Pyodide 会将 Python bytes 转换为 Uint8Array
        // 如果 result.buffer 是 Uint8Array，直接使用
        if (result.buffer instanceof Uint8Array) {
          finalResult.buffer = result.buffer.buffer;
          logs.push(`文件缓冲区大小: ${finalResult.buffer.byteLength} 字节`);
        }
        // 如果 result.buffer 是 Python bytes 对象，需要转换为 Uint8Array
        else if (result.buffer.toJs) {
          // Python bytes 对象，使用 toJs() 转换
          const uint8Array = result.buffer.toJs();
          finalResult.buffer = uint8Array.buffer;
          logs.push(`文件缓冲区大小: ${finalResult.buffer.byteLength} 字节`);
        }
        // 已经是 TypedArray，获取其底层 ArrayBuffer
        else if (typeof result.buffer === "object" && result.buffer.buffer) {
          finalResult.buffer = result.buffer.buffer;
          logs.push(`文件缓冲区大小: ${finalResult.buffer.byteLength} 字节`);
        }
        // 其他情况，尝试直接使用
        else {
          finalResult.buffer = result.buffer;
          logs.push(`文件缓冲区类型: ${typeof result.buffer}`);
        }
      } catch (bufferError: any) {
        logs.push(`处理文件缓冲区失败: ${safeStringify(bufferError.message)}`);
        finalResult.success = false;
        finalResult.error = finalResult.error || "处理文件缓冲区时发生错误";
      }
    } else {
      logs.push("未检测到返回的文件缓冲区");
    }

    // 确保 success 为布尔值
    if (finalResult.success === undefined) {
      finalResult.success = true;
      logs.push("结果中未指定 success 字段，默认设置为 true");
    }

    // 确保 logs 为数组
    if (!Array.isArray(finalResult.logs)) {
      logs.push("结果中的 logs 不是数组，使用默认日志");
      finalResult.logs = logs;
    }

    // 如果失败但没有错误信息，添加默认错误信息
    if (!finalResult.success && !finalResult.error) {
      const defaultError = "处理失败，但未提供具体错误信息";
      finalResult.error = defaultError;
      logs.push(defaultError);
    }

    // 记录结果状态
    logs.push(`处理结果: ${finalResult.success ? "成功" : "失败"}`);
    if (finalResult.success && finalResult.buffer) {
      logs.push("文件处理成功，生成了新的 Excel 文件");
    } else if (finalResult.success) {
      logs.push("处理成功，没有生成新文件");
    } else {
      logs.push(`处理失败，错误信息: ${finalResult.error}`);
    }

    // 添加执行时间信息
    const totalExecutionTime = Date.now() - startTime;
    finalResult.logs.push(`总执行时间: ${totalExecutionTime}ms`);
    logs.push(
      `平均处理速度: ${Math.round(totalExecutionTime / Math.max(1, finalResult.logs.length))}ms/步骤`,
    );

    logs.push("Python 脚本执行完成");
    return finalResult;
  } catch (error: any) {
    log(LogLevel.ERROR, "doRunPy", "Pyodide 执行错误", error);
    const totalExecutionTime = Date.now() - startTime;
    throw new Error(
      `执行错误: ${safeStringify(error.message)} (总执行时间: ${totalExecutionTime}ms)`,
    );
  }
}
