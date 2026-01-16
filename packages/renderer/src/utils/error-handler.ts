// 全局错误处理器
import { message } from 'ant-design-vue'

export interface ErrorLog {
  timestamp: number
  type: 'user' | 'environment' | 'processing' | 'system'
  level: 'warning' | 'error' | 'critical'
  message: string
  stack?: string
  context?: Record<string, any>
}

class ErrorHandler {
  private logs: ErrorLog[] = []
  private maxLogs = 100

  /**
   * 记录错误
   */
  logError(error: ErrorLog): void {
    this.logs.push(error)
    
    // 限制日志数量
    if (this.logs.length > this.maxLogs) {
      this.logs.shift()
    }

    // 输出到控制台
    console.error(`[${error.type}] ${error.message}`, error)

    // 显示用户友好的错误消息
    if (error.level === 'error' || error.level === 'critical') {
      message.error(this.getUserFriendlyMessage(error))
    } else {
      message.warning(this.getUserFriendlyMessage(error))
    }
  }

  /**
   * 获取用户友好的错误消息
   */
  private getUserFriendlyMessage(error: ErrorLog): string {
    // 根据错误类型返回友好的消息
    switch (error.type) {
      case 'user':
        return error.message
      case 'environment':
        return `环境错误: ${error.message}`
      case 'processing':
        return `处理失败: ${error.message}`
      case 'system':
        return '系统错误，请刷新页面重试'
      default:
        return error.message
    }
  }

  /**
   * 获取所有日志
   */
  getLogs(): ErrorLog[] {
    return [...this.logs]
  }

  /**
   * 清空日志
   */
  clearLogs(): void {
    this.logs = []
  }

  /**
   * 处理Vue错误
   */
  handleVueError(err: Error, instance: any, info: string): void {
    this.logError({
      timestamp: Date.now(),
      type: 'system',
      level: 'error',
      message: err.message,
      stack: err.stack,
      context: {
        component: instance?.$options?.name,
        info
      }
    })
  }

  /**
   * 处理Promise错误
   */
  handlePromiseError(event: PromiseRejectionEvent): void {
    this.logError({
      timestamp: Date.now(),
      type: 'system',
      level: 'error',
      message: event.reason?.message || String(event.reason),
      stack: event.reason?.stack,
      context: {
        promise: true
      }
    })
  }

  /**
   * 处理用户输入错误
   */
  handleUserError(message: string): void {
    this.logError({
      timestamp: Date.now(),
      type: 'user',
      level: 'warning',
      message
    })
  }

  /**
   * 处理环境错误
   */
  handleEnvironmentError(message: string, error?: Error): void {
    this.logError({
      timestamp: Date.now(),
      type: 'environment',
      level: 'error',
      message,
      stack: error?.stack
    })
  }

  /**
   * 处理处理错误
   */
  handleProcessingError(message: string, error?: Error): void {
    this.logError({
      timestamp: Date.now(),
      type: 'processing',
      level: 'error',
      message,
      stack: error?.stack
    })
  }
}

// 导出单例
export const errorHandler = new ErrorHandler()

/**
 * 安装全局错误处理器
 */
export function installErrorHandler(app: any): void {
  // Vue错误处理
  app.config.errorHandler = (err: Error, instance: any, info: string) => {
    errorHandler.handleVueError(err, instance, info)
  }

  // Promise错误处理
  window.addEventListener('unhandledrejection', (event) => {
    errorHandler.handlePromiseError(event)
  })

  console.log('全局错误处理器已安装')
}
