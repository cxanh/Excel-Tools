import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';


let mainWindow: BrowserWindow | null = null;
let pythonProcess: ChildProcess | null = null;

/**
 * 获取 Python 可执行文件路径
 */
function getPythonExecutablePath(): string {
  if (app.isPackaged) {
    // 生产环境：从 resources 目录获取
    const platform = process.platform;
    const exeName = platform === 'win32' ? 'excel-toolkit-backend.exe' : 'excel-toolkit-backend';
    return path.join(process.resourcesPath, 'python', exeName);
  } else {
    // 开发环境：直接运行 Python 脚本
    return 'python';
  }
}

/**
 * 获取 Python 脚本路径（仅开发环境使用）
 */
function getPythonScriptPath(): string {
  return path.join(__dirname, '..', 'python-backend', 'main.py');
}

/**
 * 启动 Python 后端进程
 */
function startPythonBackend(): Promise<void> {
  return new Promise((resolve, reject) => {
    const pythonPath = getPythonExecutablePath();
    
    console.log('[MAIN] Starting Python backend:', pythonPath);
    
    let resolved = false;
    
    // 启动 Python 进程
    if (app.isPackaged) {
      // 生产环境：直接运行打包后的可执行文件
      pythonProcess = spawn(pythonPath, [], {
        stdio: ['pipe', 'pipe', 'pipe']
      });
    } else {
      // 开发环境：运行 Python 脚本
      const scriptPath = getPythonScriptPath();
      console.log('[MAIN] Python script path:', scriptPath);
      pythonProcess = spawn(pythonPath, [scriptPath], {
      stdio: ['pipe', 'pipe', 'pipe'],
      env: {
      ...process.env,
      PYTHONIOENCODING: 'utf-8'
    }
  });

    }
    
    // 监听 stdout（JSON 响应）
    pythonProcess.stdout?.on('data', (data) => {
      const lines = data.toString().split('\n');
      for (const line of lines) {
        if (line.trim()) {
          try {
            const message = JSON.parse(line);
            console.log('[PYTHON]', message);
            
            // 如果是启动消息，resolve Promise
            if (message.type === 'startup' && message.status === 'ready' && !resolved) {
              resolved = true;
              resolve();
            }
            
            // 转发消息到渲染进程
            if (mainWindow) {
              mainWindow.webContents.send('python-message', message);
            }
          } catch (e) {
            console.error('[MAIN] Failed to parse Python message:', line);
          }
        }
      }
    });
    
    // 监听 stderr（日志）
    pythonProcess.stderr?.on('data', (data) => {
      console.log('[PYTHON LOG]', data.toString());
    });
    
    // 监听进程退出
    pythonProcess.on('exit', (code) => {
      console.log('[MAIN] Python process exited with code:', code);
      pythonProcess = null;
      if (!resolved) {
        reject(new Error(`Python process exited with code ${code}`));
      }
    });
    
    // 监听进程错误
    pythonProcess.on('error', (err) => {
      console.error('[MAIN] Python process error:', err);
      if (!resolved) {
        resolved = true;
        reject(err);
      }
    });
    
    // 设置超时
    setTimeout(() => {
      if (!resolved) {
        resolved = true;
        reject(new Error('Python backend startup timeout'));
      }
    }, 10000);
  });
}

/**
 * 发送命令到 Python 后端
 */
function normalizePath(p: string | undefined): string {
  if (!p) return '';
  return p.replace(/\\/g, '/');
}

function sendCommandToPython(command: any): void {
  if (!pythonProcess || !pythonProcess.stdin) {
    console.error('[MAIN] Python process not available');
    return;
  }
  
  // 只有当 file_path 存在时才进行路径规范化
  if (command.params && command.params.file_path) {
    command.params.file_path = normalizePath(command.params.file_path);
  }

  const commandJson = JSON.stringify(command);
  pythonProcess.stdin.write(commandJson + '\n');
}

/**
 * 创建主窗口
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });
  
  // 加载应用
  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL);
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }
  
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

/**
 * 注册 IPC 处理器
 */
function registerIpcHandlers() {
  // 处理来自渲染进程的命令
  ipcMain.on('python-command', (_event, command) => {
    console.log('[MAIN] Received command from renderer:', command);
    sendCommandToPython(command);
  });
  
  // 打开文件对话框
  ipcMain.handle('dialog:openFile', async () => {
    if (!mainWindow) return { canceled: true };
    
    const result = await dialog.showOpenDialog(mainWindow, {
      title: '选择 Excel 文件',
      filters: [
        { name: 'Excel 文件', extensions: ['xlsx', 'xls', 'xlsm'] },
        { name: 'CSV 文件', extensions: ['csv'] },
        { name: '所有文件', extensions: ['*'] }
      ],
      properties: ['openFile']
    });
    
    return result;
  });
  
  // 打开多文件对话框
  ipcMain.handle('dialog:openFiles', async () => {
    if (!mainWindow) return { canceled: true };
    
    const result = await dialog.showOpenDialog(mainWindow, {
      title: '选择 Excel 文件',
      filters: [
        { name: 'Excel 文件', extensions: ['xlsx', 'xls', 'xlsm'] },
        { name: 'CSV 文件', extensions: ['csv'] },
        { name: '所有文件', extensions: ['*'] }
      ],
      properties: ['openFile', 'multiSelections']
    });
    
    return result;
  });
  
  // 保存文件对话框
  ipcMain.handle('dialog:saveFile', async (_event, options) => {
    if (!mainWindow) return { canceled: true };
    
    const result = await dialog.showSaveDialog(mainWindow, {
      title: options?.title || '保存文件',
      defaultPath: options?.defaultPath || 'output.xlsx',
      filters: options?.filters || [
        { name: 'Excel 文件', extensions: ['xlsx'] },
        { name: '所有文件', extensions: ['*'] }
      ]
    });
    
    return result;
  });
  
  // 选择文件夹对话框
  ipcMain.handle('dialog:openDirectory', async (_event, options) => {
    if (!mainWindow) return { canceled: true };
    
    const result = await dialog.showOpenDialog(mainWindow, {
      title: options?.title || '选择文件夹',
      properties: ['openDirectory']
    });
    
    return result;
  });
  
  // 确认对话框
  ipcMain.handle('dialog:confirm', async (_event, options) => {
    if (!mainWindow) return { response: 1 };
    
    const result = await dialog.showMessageBox(mainWindow, {
      type: options?.type || 'question',
      title: options?.title || '确认',
      message: options?.message || '确定要执行此操作吗？',
      detail: options?.detail,
      buttons: options?.buttons || ['确定', '取消'],
      defaultId: 0,
      cancelId: 1
    });
    
    return result;
  });
  
  // 错误对话框
  ipcMain.handle('dialog:error', async (_event, options) => {
    if (!mainWindow) return;
    
    await dialog.showMessageBox(mainWindow, {
      type: 'error',
      title: options?.title || '错误',
      message: options?.message || '发生了一个错误',
      detail: options?.detail,
      buttons: ['确定']
    });
  });
  
  // 信息对话框
  ipcMain.handle('dialog:info', async (_event, options) => {
    if (!mainWindow) return;
    
    await dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: options?.title || '提示',
      message: options?.message || '',
      detail: options?.detail,
      buttons: ['确定']
    });
  });
}

/**
 * 应用启动
 */
app.whenReady().then(async () => {
  try {
    // 启动 Python 后端
    await startPythonBackend();
    console.log('[MAIN] Python backend started successfully');
    
    // 注册 IPC 处理器
    registerIpcHandlers();
    
    // 创建主窗口
    createWindow();
  } catch (error) {
    console.error('[MAIN] Failed to start application:', error);
    app.quit();
  }
});

/**
 * 应用退出时清理
 */
app.on('will-quit', () => {
  if (pythonProcess) {
    console.log('[MAIN] Terminating Python process...');
    pythonProcess.kill();
  }
});

/**
 * 所有窗口关闭时退出（macOS 除外）
 */
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

/**
 * macOS 激活时重新创建窗口
 */
app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});
