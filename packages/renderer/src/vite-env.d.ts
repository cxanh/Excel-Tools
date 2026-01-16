/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// Python文件作为原始文本导入
declare module '*.py' {
  const content: string
  export default content
}

declare module '*.py?raw' {
  const content: string
  export default content
}

// JSON文件导入
declare module '*.json' {
  const value: any
  export default value
}

// Electron API类型定义
interface ElectronAPI {
  app: {
    getVersion: () => Promise<string>
    getPlatform: () => Promise<string>
    getUserDataPath: () => Promise<string>
  }
  fs: {
    selectFile: () => Promise<string | null>
    selectFiles: () => Promise<string[]>
    selectFolder: () => Promise<string | null>
    saveFile: (data: ArrayBuffer, fileName: string) => Promise<string | null>
    readFile: (filePath: string) => Promise<ArrayBuffer>
  }
  dialog: {
    showError: (title: string, message: string) => Promise<void>
    showMessage: (options: any) => Promise<any>
  }
}

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}

export {}
