// Pyodide管理器
// 负责加载、初始化和管理Pyodide环境

export interface PyodideConfig {
  version: string;
  loadMode: "cdn" | "local";
  localIndexURL?: string;
  cdnIndexURL?: string;
  fallbackMode?: "local" | "cdn";
  retryAttempts: number;
  timeout: number;
}

export interface RunPyInput {
  file: ArrayBuffer;
  fileName: string;
  params?: Record<string, any>;
}

export interface RunPyOutput {
  success: boolean;
  buffer?: ArrayBuffer;
  logs: string[];
  details?: any;
  error?: string;
}

class PyodideManager {
  private pyodide: any = null;
  private config: PyodideConfig | null = null;
  private isInitializing = false;
  private initPromise: Promise<void> | null = null;
  private installedPackages = new Set<string>();

  /**
   * 初始化Pyodide环境
   */
  async initialize(config: PyodideConfig): Promise<void> {
    // 如果已经初始化，直接返回
    if (this.pyodide) {
      return;
    }

    // 如果正在初始化，等待初始化完成
    if (this.isInitializing && this.initPromise) {
      return this.initPromise;
    }

    this.isInitializing = true;
    this.config = config;

    this.initPromise = this._loadPyodideWithRetry();

    try {
      await this.initPromise;
      console.log("Pyodide初始化成功");
    } finally {
      this.isInitializing = false;
    }
  }

  /**
   * 带重试的Pyodide加载
   */
  private async _loadPyodideWithRetry(): Promise<void> {
    if (!this.config) {
      throw new Error("Pyodide配置未设置");
    }

    let lastError: Error | null = null;
    let currentMode = this.config.loadMode;

    for (let attempt = 0; attempt < this.config.retryAttempts; attempt++) {
      try {
        console.log(
          `尝试加载Pyodide (尝试 ${attempt + 1}/${this.config.retryAttempts}, 模式: ${currentMode})`,
        );

        const indexURL =
          currentMode === "cdn"
            ? this.config.cdnIndexURL
            : this.config.localIndexURL;

        // 使用超时控制
        this.pyodide = await this._loadWithTimeout(
          indexURL!,
          this.config.timeout,
        );

        console.log("Pyodide加载成功");
        return;
      } catch (error) {
        lastError = error as Error;
        console.error(`Pyodide加载失败 (尝试 ${attempt + 1}):`, error);

        // 如果配置了回退模式且是第一次失败，切换到回退模式
        if (
          attempt === 0 &&
          this.config.fallbackMode &&
          this.config.fallbackMode !== currentMode
        ) {
          console.log(`切换到回退模式: ${this.config.fallbackMode}`);
          currentMode = this.config.fallbackMode;
        }
      }
    }

    throw new Error(
      `Pyodide加载失败，已重试${this.config.retryAttempts}次: ${lastError?.message}`,
    );
  }

  /**
   * 带超时的加载
   */
  private async _loadWithTimeout(
    indexURL: string,
    timeout: number,
  ): Promise<any> {
    return new Promise(async (resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`Pyodide加载超时 (${timeout}ms)`));
      }, timeout);

      try {
        // 从CDN加载Pyodide
        const script = document.createElement("script");
        script.src = `${indexURL}pyodide.js`;
        script.async = true;
        script.onload = async () => {
          try {
            // @ts-ignore - loadPyodide is loaded from the script
            const pyodide = await loadPyodide({
              indexURL,
              fullStdLib: false, // 不加载完整标准库，按需加载
            });
            clearTimeout(timer);
            resolve(pyodide);
          } catch (error) {
            clearTimeout(timer);
            reject(error);
          }
        };
        script.onerror = () => {
          clearTimeout(timer);
          reject(new Error("加载Pyodide脚本失败"));
        };
        document.head.appendChild(script);
      } catch (error) {
        clearTimeout(timer);
        reject(error);
      }
    });
  }

  /**
   * 检查Pyodide是否就绪
   */
  isReady(): boolean {
    return this.pyodide !== null;
  }

  /**
   * 获取Pyodide实例
   */
  getPyodide(): any {
    if (!this.pyodide) {
      throw new Error("Pyodide未初始化");
    }
    return this.pyodide;
  }

  /**
   * 安装Python包
   */
  async installPackage(packageName: string, version?: string): Promise<void> {
    if (!this.pyodide) {
      throw new Error("Pyodide未初始化");
    }

    const packageKey = version ? `${packageName}==${version}` : packageName;

    // 如果已安装，跳过
    if (this.installedPackages.has(packageKey)) {
      console.log(`包 ${packageKey} 已安装`);
      return;
    }

    try {
      console.log(`安装Python包: ${packageKey}`);

      // 首先尝试使用 Pyodide 的 loadPackage (用于内置包)
      try {
        await this.pyodide.loadPackage(packageName);
        this.installedPackages.add(packageKey);
        console.log(`包 ${packageKey} 安装成功 (通过 loadPackage)`);
        return;
      } catch (loadPackageError) {
        // 如果 loadPackage 失败，尝试使用 micropip
        console.log(
          `${packageName} 不在 Pyodide 内置包中，尝试使用 micropip 安装...`,
        );

        // 确保 micropip 已加载
        await this.pyodide.loadPackage("micropip");
        const micropip = this.pyodide.pyimport("micropip");

        // 使用 micropip 安装包
        await micropip.install(packageKey);
        this.installedPackages.add(packageKey);
        console.log(`包 ${packageKey} 安装成功 (通过 micropip)`);
      }
    } catch (error) {
      console.error(`包 ${packageKey} 安装失败:`, error);
      throw new Error(`安装包 ${packageKey} 失败: ${(error as Error).message}`);
    }
  }

  /**
   * 批量安装Python包
   */
  async installPackages(packages: string[]): Promise<void> {
    for (const pkg of packages) {
      await this.installPackage(pkg);
    }
  }

  /**
   * 执行Python脚本
   */
  async runPython(
    script: string,
    input: RunPyInput,
    timeout: number = 60000,
  ): Promise<RunPyOutput> {
    if (!this.pyodide) {
      throw new Error("Pyodide未初始化");
    }

    try {
      // 设置超时
      const timeoutPromise = new Promise<never>((_, reject) => {
        setTimeout(() => reject(new Error("Python脚本执行超时")), timeout);
      });

      // 执行脚本
      const executePromise = this._executePython(script, input);

      // 竞速执行
      const result = await Promise.race([executePromise, timeoutPromise]);
      return result;
    } catch (error) {
      console.error("Python脚本执行失败:", JSON.stringify(error, null, 2));
      return {
        success: false,
        logs: [],
        error: (error as Error).message,
      };
    }
  }

  /**
   * 内部执行Python脚本
   */
  private async _executePython(
    script: string,
    input: RunPyInput,
  ): Promise<RunPyOutput> {
    // 将输入数据传递给Python
    this.pyodide.globals.set("input_data", {
      file: input.file,
      fileName: input.fileName,
      params: input.params || {},
    });

    // 执行Python脚本
    await this.pyodide.runPythonAsync(script);

    // 获取输出
    const output = this.pyodide.globals.get("output");

    if (!output) {
      throw new Error("Python脚本未返回output变量");
    }

    // 转换Python对象为JavaScript对象
    const result = output.toJs({ dict_converter: Object.fromEntries });

    return {
      success: result.success || false,
      buffer: result.buffer,
      logs: result.logs || [],
      details: result.details,
      error: result.error,
    };
  }

  /**
   * 清理资源
   */
  destroy(): void {
    this.pyodide = null;
    this.config = null;
    this.installedPackages.clear();
    this.isInitializing = false;
    this.initPromise = null;
  }
}

// 导出单例
export const pyodideManager = new PyodideManager();
