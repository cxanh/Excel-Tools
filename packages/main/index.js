import { app, BrowserWindow, ipcMain, dialog } from 'electron'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs/promises'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

let mainWindow = null
let windowState = {
  width: 1200,
  height: 800,
  x: undefined,
  y: undefined,
  isMaximized: false
}

// 加载窗口状态
async function loadWindowState() {
  try {
    const userDataPath = app.getPath('userData')
    const stateFile = path.join(userDataPath, 'window-state.json')
    const data = await fs.readFile(stateFile, 'utf-8')
    windowState = JSON.parse(data)
  } catch (error) {
    // 使用默认状态
    console.log('使用默认窗口状态')
  }
}

// 保存窗口状态
async function saveWindowState() {
  if (!mainWindow) return
  
  try {
    const bounds = mainWindow.getBounds()
    windowState = {
      width: bounds.width,
      height: bounds.height,
      x: bounds.x,
      y: bounds.y,
      isMaximized: mainWindow.isMaximized()
    }
    
    const userDataPath = app.getPath('userData')
    const stateFile = path.join(userDataPath, 'window-state.json')
    await fs.writeFile(stateFile, JSON.stringify(windowState, null, 2))
  } catch (error) {
    console.error('保存窗口状态失败:', error)
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: windowState.width,
    height: windowState.height,
    x: windowState.x,
    y: windowState.y,
    minWidth: 800,
    minHeight: 600,
    show: false, // 先隐藏，加载完成后显示
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      preload: path.join(__dirname, '../preload/index.js')
    }
  })

  // 恢复最大化状态
  if (windowState.isMaximized) {
    mainWindow.maximize()
  }

  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })

  // 开发模式加载Vite开发服务器
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    // 生产模式加载构建后的文件
    mainWindow.loadFile(path.join(__dirname, '../renderer/dist/index.html'))
  }

  // 监听窗口状态变化
  mainWindow.on('resize', () => {
    if (!mainWindow.isMaximized()) {
      saveWindowState()
    }
  })

  mainWindow.on('move', () => {
    if (!mainWindow.isMaximized()) {
      saveWindowState()
    }
  })

  mainWindow.on('maximize', () => {
    saveWindowState()
  })

  mainWindow.on('unmaximize', () => {
    saveWindowState()
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// 应用初始化
async function initialize() {
  try {
    await loadWindowState()
    createWindow()
    console.log('应用初始化成功')
  } catch (error) {
    console.error('应用初始化失败:', error)
    dialog.showErrorBox('启动错误', `应用启动失败: ${error.message}`)
    app.quit()
  }
}

// 应用清理
async function cleanup() {
  try {
    await saveWindowState()
    console.log('应用清理完成')
  } catch (error) {
    console.error('应用清理失败:', error)
  }
}

// 应用就绪
app.whenReady().then(() => {
  initialize()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

// 所有窗口关闭
app.on('window-all-closed', async () => {
  await cleanup()
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// 应用退出前
app.on('before-quit', async (event) => {
  event.preventDefault()
  await cleanup()
  app.exit(0)
})


// ==================== IPC通信处理器 ====================

// 获取应用版本
ipcMain.handle('app:getVersion', () => {
  return app.getVersion()
})

// 获取平台信息
ipcMain.handle('app:getPlatform', () => {
  return process.platform
})

// 选择文件
ipcMain.handle('fs:selectFile', async () => {
  try {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openFile'],
      filters: [
        { name: 'Excel文件', extensions: ['xlsx', 'xls'] },
        { name: '所有文件', extensions: ['*'] }
      ]
    })
    
    if (result.canceled) {
      return null
    }
    
    return result.filePaths[0]
  } catch (error) {
    console.error('选择文件失败:', error)
    throw error
  }
})

// 选择多个文件
ipcMain.handle('fs:selectFiles', async () => {
  try {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openFile', 'multiSelections'],
      filters: [
        { name: 'Excel文件', extensions: ['xlsx', 'xls'] },
        { name: 'CSV文件', extensions: ['csv'] },
        { name: '所有文件', extensions: ['*'] }
      ]
    })
    
    if (result.canceled) {
      return []
    }
    
    return result.filePaths
  } catch (error) {
    console.error('选择文件失败:', error)
    throw error
  }
})

// 选择文件夹
ipcMain.handle('fs:selectFolder', async () => {
  try {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openDirectory']
    })
    
    if (result.canceled) {
      return null
    }
    
    return result.filePaths[0]
  } catch (error) {
    console.error('选择文件夹失败:', error)
    throw error
  }
})

// 保存文件
ipcMain.handle('fs:saveFile', async (event, data, fileName) => {
  try {
    const result = await dialog.showSaveDialog(mainWindow, {
      defaultPath: fileName,
      filters: [
        { name: 'Excel文件', extensions: ['xlsx'] },
        { name: '所有文件', extensions: ['*'] }
      ]
    })
    
    if (result.canceled) {
      return null
    }
    
    // 将ArrayBuffer转换为Buffer
    const buffer = Buffer.from(data)
    await fs.writeFile(result.filePath, buffer)
    
    return result.filePath
  } catch (error) {
    console.error('保存文件失败:', error)
    throw error
  }
})

// 读取文件
ipcMain.handle('fs:readFile', async (event, filePath) => {
  try {
    const buffer = await fs.readFile(filePath)
    return buffer.buffer
  } catch (error) {
    console.error('读取文件失败:', error)
    throw error
  }
})

// 获取用户数据目录
ipcMain.handle('app:getUserDataPath', () => {
  return app.getPath('userData')
})

// 显示错误对话框
ipcMain.handle('dialog:showError', (event, title, message) => {
  dialog.showErrorBox(title, message)
})

// 显示消息对话框
ipcMain.handle('dialog:showMessage', async (event, options) => {
  return await dialog.showMessageBox(mainWindow, options)
})

console.log('IPC通信处理器已注册')
