// 文件处理服务
import { runPy, type RunPyInput, type RunPyOutput } from './py'

export interface ValidationResult {
  valid: boolean
  error?: string
}

export interface ProcessResult {
  success: boolean
  fileName: string
  buffer?: ArrayBuffer
  logs: string[]
  statistics?: Record<string, any>
  error?: string
}

/**
 * 验证文件
 */
export function validateFile(file: File): ValidationResult {
  // 检查文件是否存在
  if (!file) {
    return {
      valid: false,
      error: '请选择文件'
    }
  }

  // 检查文件大小
  const maxSize = 100 * 1024 * 1024 // 100MB
  if (file.size > maxSize) {
    return {
      valid: false,
      error: `文件过大，建议处理小于100MB的文件（当前: ${(file.size / 1024 / 1024).toFixed(2)}MB）`
    }
  }

  // 检查文件类型
  const fileName = file.name.toLowerCase()
  const validExtensions = ['.xlsx', '.xls', '.csv']
  const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext))

  if (!hasValidExtension) {
    return {
      valid: false,
      error: '不支持的文件格式，请上传.xlsx、.xls或.csv文件'
    }
  }

  // 检查文件是否为空
  if (file.size === 0) {
    return {
      valid: false,
      error: '文件为空'
    }
  }

  return { valid: true }
}

/**
 * 批量验证文件
 */
export function validateFiles(files: File[]): ValidationResult {
  if (!files || files.length === 0) {
    return {
      valid: false,
      error: '请选择至少一个文件'
    }
  }

  for (const file of files) {
    const result = validateFile(file)
    if (!result.valid) {
      return {
        valid: false,
        error: `文件 "${file.name}" 验证失败: ${result.error}`
      }
    }
  }

  return { valid: true }
}

/**
 * 处理单个文件
 */
export async function processFile(
  file: File,
  worker: string,
  params?: any
): Promise<ProcessResult> {
  try {
    // 验证文件
    const validation = validateFile(file)
    if (!validation.valid) {
      return {
        success: false,
        fileName: file.name,
        logs: [],
        error: validation.error
      }
    }

    // 读取文件
    const buffer = await file.arrayBuffer()

    // 准备输入数据
    const input: RunPyInput = {
      file: buffer,
      fileName: file.name,
      params: params || {}
    }

    // 执行Python脚本
    const result: RunPyOutput = await runPy(worker, input)

    // 返回处理结果
    return {
      success: result.success,
      fileName: file.name,
      buffer: result.buffer,
      logs: result.logs,
      statistics: result.details?.statistics,
      error: result.error
    }
  } catch (error) {
    console.error('文件处理失败:', error)
    return {
      success: false,
      fileName: file.name,
      logs: [],
      error: (error as Error).message
    }
  }
}

/**
 * 批量处理文件
 */
export async function processBatch(
  files: File[],
  worker: string,
  params?: any,
  onProgress?: (current: number, total: number) => void
): Promise<ProcessResult[]> {
  const results: ProcessResult[] = []

  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    
    // 更新进度
    if (onProgress) {
      onProgress(i + 1, files.length)
    }

    // 处理文件
    const result = await processFile(file, worker, params)
    results.push(result)
  }

  return results
}

/**
 * 下载处理结果
 */
export async function downloadResult(result: ProcessResult, fileName?: string): Promise<void> {
  if (!result.buffer) {
    throw new Error('没有可下载的文件')
  }

  try {
    const finalFileName = fileName || result.fileName

    // 使用Electron API保存文件
    if (window.electronAPI) {
      await window.electronAPI.fs.saveFile(result.buffer, finalFileName)
    } else {
      // 浏览器环境回退方案
      const blob = new Blob([result.buffer])
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = finalFileName
      a.click()
      URL.revokeObjectURL(url)
    }
  } catch (error) {
    console.error('下载文件失败:', error)
    throw error
  }
}

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

/**
 * 下载处理后的文件（兼容旧插件）
 */
export async function downloadProcessedFile(data: ArrayBuffer, fileName: string): Promise<void> {
  const result: ProcessResult = {
    success: true,
    fileName: fileName,
    buffer: data,
    logs: []
  }
  return downloadResult(result, fileName)
}

/**
 * 下载文件（兼容旧插件）
 */
export async function downloadFile(data: ArrayBuffer, fileName: string): Promise<void> {
  const result: ProcessResult = {
    success: true,
    fileName: fileName,
    buffer: data,
    logs: []
  }
  return downloadResult(result, fileName)
}
