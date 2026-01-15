/**
 * 插件工具模块
 * 提供插件相关的工具函数
 */

/**
 * 获取Python脚本内容
 * @param {string} pluginKey 插件名称
 * @returns {Promise<string>} Python脚本内容
 */
export async function getPythonScript(pluginKey) {
  try {
    const response = await fetch(`/@plugins/${pluginKey}/worker.py`);
    if (!response.ok) {
      throw new Error(`Failed to fetch script for plugin ${pluginKey}`);
    }
    return await response.text();
  } catch (error) {
    console.error(`Error getting Python script for plugin ${pluginKey}:`, error);
    throw error;
  }
}

/**
 * 生成插件配置
 * @param {Object} manifest 插件manifest.json内容
 * @returns {Object} 完整的插件配置
 */
export function generatePluginConfig(manifest) {
  return {
    ...manifest,
    // 添加默认值
    version: manifest.version || '1.0.0',
    enabled: manifest.enabled !== false,
    dependencies: manifest.dependencies || [],
  };
}

/**
 * 验证插件配置
 * @param {Object} config 插件配置
 * @returns {boolean} 是否有效
 */
export function validatePluginConfig(config) {
  return !!(config.key && config.name && config.description && config.category);
}

/**
 * 格式化插件错误信息
 * @param {Error} error 错误对象
 * @returns {string} 格式化的错误信息
 */
export function formatPluginError(error) {
  return error.message || '插件执行失败';
}
