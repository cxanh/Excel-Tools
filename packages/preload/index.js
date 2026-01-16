import { contextBridge, ipcRenderer } from 'electron'

// 暴露安全的API给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 应用信息
  app: {
    getVersion: () => ipcRenderer.invoke('app:getVersion'),
    getPlatform: () => ipcRenderer.invoke('app:getPlatform'),
    getUserDataPath: () => ipcRenderer.invoke('app:getUserDataPath')
  },
  
  // 文件系统操作
  fs: {
    selectFile: () => ipcRenderer.invoke('fs:selectFile'),
    selectFiles: () => ipcRenderer.invoke('fs:selectFiles'),
    selectFolder: () => ipcRenderer.invoke('fs:selectFolder'),
    saveFile: (data, fileName) => ipcRenderer.invoke('fs:saveFile', data, fileName),
    readFile: (filePath) => ipcRenderer.invoke('fs:readFile', filePath)
  },
  
  // 对话框
  dialog: {
    showError: (title, message) => ipcRenderer.invoke('dialog:showError', title, message),
    showMessage: (options) => ipcRenderer.invoke('dialog:showMessage', options)
  }
})

console.log('Preload script loaded - contextBridge API exposed')
