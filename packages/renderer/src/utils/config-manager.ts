// 配置管理器
import type { PyodideConfig } from './pyodide-manager'

export interface AppConfig {
  pyodide: PyodideConfig
  theme: {
    colorPrimary: string
    borderRadius: number
  }
}

// 默认配置
const defaultConfig: AppConfig = {
  pyodide: {
    version: '0.24.1',
    loadMode: 'cdn',
    localIndexURL: '/pyodide/v0.24.1/full/',
    cdnIndexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/',
    fallbackMode: 'local',
    retryAttempts: 3,
    timeout: 30000
  },
  theme: {
    colorPrimary: '#165DFF',
    borderRadius: 4
  }
}

class ConfigManager {
  private config: AppConfig = defaultConfig

  /**
   * 加载配置
   */
  async loadConfig(): Promise<void> {
    try {
      // 尝试从根目录加载pyodide-config.json
      const response = await fetch('/pyodide-config.json')
      
      if (response.ok) {
        const pyodideConfig = await response.json()
        this.config.pyodide = { ...this.config.pyodide, ...pyodideConfig }
        console.log('Pyodide配置加载成功')
      } else {
        console.log('使用默认Pyodide配置')
      }
    } catch (error) {
      console.warn('加载Pyodide配置失败，使用默认配置:', error)
    }
  }

  /**
   * 获取配置
   */
  getConfig(): AppConfig {
    return { ...this.config }
  }

  /**
   * 获取Pyodide配置
   */
  getPyodideConfig(): PyodideConfig {
    return { ...this.config.pyodide }
  }

  /**
   * 获取主题配置
   */
  getThemeConfig() {
    return { ...this.config.theme }
  }

  /**
   * 更新配置
   */
  updateConfig(config: Partial<AppConfig>): void {
    this.config = { ...this.config, ...config }
  }
}

// 导出单例
export const configManager = new ConfigManager()
