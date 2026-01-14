// Pyodide 集成工具模块
import { loadPyodide } from "pyodide";

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

  private constructor() {}

  public static getInstance(): PyodideManager {
    if (!PyodideManager.instance) {
      PyodideManager.instance = new PyodideManager();
    }
    return PyodideManager.instance;
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
      this.triggerLoadingCallback("init", 0, "正在初始化 Python 环境...");

      // 分阶段加载，提供更详细的进度信息
      const pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.0/full/",
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
      console.log("Pyodide 加载完成");

      return pyodide;
    } catch (error) {
      this.triggerLoadingCallback("error", 0, `Pyodide 加载失败: ${error}`);
      console.error("Pyodide 加载失败:", error);
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
      console.log(`安装依赖: ${packagesToInstall.join(", ")}`);

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
        console.log("Pyodide 资源已清理");
      } catch (error) {
        console.error("清理 Pyodide 资源失败:", error);
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
    console.error("Pyodide 执行错误:", error);
    const executionTime = Date.now() - startTime;
    return {
      success: false,
      logs: [
        ...logs,
        `执行错误: ${error.message}`,
        `总执行时间: ${executionTime}ms`,
      ],
      error: error.message,
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
    const scriptStartTime = Date.now();
    await pyodide.runPythonAsync(script);
    const scriptExecutionTime = Date.now() - scriptStartTime;
    logs.push(`Python 脚本执行耗时: ${scriptExecutionTime}ms`);

    // 6. 获取执行结果
    let result: any = {};

    try {
      // 优先尝试标准 process 函数接口
      if (pyodide.globals.has("process")) {
        logs.push("调用标准 process 函数...");
        const processFn = pyodide.globals.get("process");
        result = processFn(pyInput);
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
      // 其次尝试 replace-content 插件的接口
      else if (pyodide.globals.has("replace_content_in_excel")) {
        logs.push("调用 replace_content_in_excel 函数...");
        const replaceFn = pyodide.globals.get("replace_content_in_excel");
        if (input.type === "single") {
          result = replaceFn(
            input.file,
            input.settings?.replacementRules || [],
            input.settings || {},
          );
        } else {
          throw new Error(
            "replace_content_in_excel 函数需要 single 类型的输入",
          );
        }
      }
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
      logs.push(`获取结果时出错: ${error.message}`);
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
      finalResult.buffer = result.buffer.buffer;
    }

    // 确保 success 为布尔值
    if (finalResult.success === undefined) {
      finalResult.success = true;
    }

    // 确保 logs 为数组
    if (!Array.isArray(finalResult.logs)) {
      finalResult.logs = logs;
    }

    // 如果失败但没有错误信息，添加默认错误信息
    if (!finalResult.success && !finalResult.error) {
      finalResult.error = "处理失败，但未提供具体错误信息";
    }

    // 添加执行时间信息
    const totalExecutionTime = Date.now() - startTime;
    finalResult.logs.push(`总执行时间: ${totalExecutionTime}ms`);

    logs.push("Python 脚本执行完成");
    return finalResult;
  } catch (error: any) {
    console.error("Pyodide 执行错误:", error);
    const totalExecutionTime = Date.now() - startTime;
    throw new Error(
      `执行错误: ${error.message} (总执行时间: ${totalExecutionTime}ms)`,
    );
  }
}
