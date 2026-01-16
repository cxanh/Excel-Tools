// 插件管理器
import type { Component } from 'vue'
import { pyodideManager } from './pyodide-manager'

export interface PluginMetadata {
  key: string
  name: string
  icon: string
  description: string
  author?: string
  version?: string
  dependencies?: string[]
}

export interface PluginInstance {
  metadata: PluginMetadata
  component: Component
  worker: string
  route: string
  state: PluginState
}

export enum PluginState {
  UNLOADED = 'unloaded',
  LOADING = 'loading',
  LOADED = 'loaded',
  ERROR = 'error'
}

class PluginManager {
  private plugins: Map<string, PluginInstance> = new Map()
  private pluginRoutes: Map<string, string> = new Map()

  /**
   * 加载所有插件
   */
  async loadPlugins(): Promise<PluginInstance[]> {
    // 在实际应用中，这里会扫描plugins目录
    // 由于我们在浏览器环境中，需要预先定义插件列表
    // 或者通过API获取插件列表
    
    console.log('插件管理器: 开始加载插件')
    
    // 这里返回空数组，实际插件将在后续任务中添加
    return []
  }

  /**
   * 注册插件
   */
  async registerPlugin(plugin: PluginInstance): Promise<void> {
    // 验证插件key唯一性
    if (this.plugins.has(plugin.metadata.key)) {
      console.warn(`插件 ${plugin.metadata.key} 已存在，跳过注册`)
      return
    }

    // 验证路由唯一性
    if (this.pluginRoutes.has(plugin.route)) {
      throw new Error(`路由 ${plugin.route} 已被占用`)
    }

    // 验证manifest
    this._validateManifest(plugin.metadata)

    // 设置插件状态为加载中
    plugin.state = PluginState.LOADING

    try {
      // 先注册插件（即使依赖安装失败也能显示在列表中）
      this.plugins.set(plugin.metadata.key, plugin)
      this.pluginRoutes.set(plugin.route, plugin.metadata.key)

      // 安装依赖（如果失败，插件仍然注册，但状态会标记为错误）
      if (plugin.metadata.dependencies && plugin.metadata.dependencies.length > 0) {
        console.log(`安装插件 ${plugin.metadata.key} 的依赖:`, plugin.metadata.dependencies)
        try {
          await pyodideManager.installPackages(plugin.metadata.dependencies)
        } catch (depError) {
          console.warn(`插件 ${plugin.metadata.key} 依赖安装失败，但插件已注册:`, depError)
          // 不抛出错误，允许插件注册成功，稍后使用时再尝试安装
        }
      }

      // 设置状态为已加载
      plugin.state = PluginState.LOADED

      console.log(`插件 ${plugin.metadata.key} 注册成功`)
    } catch (error) {
      plugin.state = PluginState.ERROR
      console.error(`插件 ${plugin.metadata.key} 注册失败:`, error)
      // 移除已注册的插件
      this.plugins.delete(plugin.metadata.key)
      this.pluginRoutes.delete(plugin.route)
      throw error
    }
  }

  /**
   * 卸载插件
   */
  unregisterPlugin(pluginKey: string): void {
    const plugin = this.plugins.get(pluginKey)
    
    if (!plugin) {
      console.warn(`插件 ${pluginKey} 不存在`)
      return
    }

    // 移除路由
    this.pluginRoutes.delete(plugin.route)

    // 移除插件
    this.plugins.delete(pluginKey)

    console.log(`插件 ${pluginKey} 已卸载`)
  }

  /**
   * 获取所有插件
   */
  getPlugins(): PluginInstance[] {
    return Array.from(this.plugins.values())
  }

  /**
   * 获取单个插件
   */
  getPlugin(pluginKey: string): PluginInstance | null {
    return this.plugins.get(pluginKey) || null
  }

  /**
   * 根据路由获取插件
   */
  getPluginByRoute(route: string): PluginInstance | null {
    const pluginKey = this.pluginRoutes.get(route)
    return pluginKey ? this.getPlugin(pluginKey) : null
  }

  /**
   * 验证manifest
   */
  private _validateManifest(metadata: PluginMetadata): void {
    if (!metadata.key || metadata.key.trim() === '') {
      throw new Error('插件key不能为空')
    }

    if (!metadata.name || metadata.name.trim() === '') {
      throw new Error('插件name不能为空')
    }

    if (!metadata.icon || metadata.icon.trim() === '') {
      throw new Error('插件icon不能为空')
    }

    if (!metadata.description || metadata.description.trim() === '') {
      throw new Error('插件description不能为空')
    }

    // 验证key格式（只允许小写字母、数字和连字符）
    if (!/^[a-z0-9-]+$/.test(metadata.key)) {
      throw new Error('插件key只能包含小写字母、数字和连字符')
    }
  }

  /**
   * 清空所有插件
   */
  clear(): void {
    this.plugins.clear()
    this.pluginRoutes.clear()
  }
}

// 导出单例
export const pluginManager = new PluginManager()
