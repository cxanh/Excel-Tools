import { app, BrowserWindow, ipcMain } from 'electron';
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
    
    // 启动 Python 进程
    if (app.isPackaged) {
      // 生产环境：直接运行打包后的可执行文件
      pythonProcess = spawn(pythonPath, [], {
        stdio: ['pipe', 'pipe', 'pipe']
      });
    } else {
      // 开发环境：运行 Python 脚本
      const scriptPath = getPythonScriptPath();
      pythonProcess = spawn(pythonPath, [scriptPath], {
        stdio: ['pipe', 'pipe', 'pipe']
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
            if (message.type === 'startup' && message.status === 'ready') {
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
    });
    
    // 监听进程错误
    pythonProcess.on('error', (err) => {
      console.error('[MAIN] Python process error:', err);
      reject(err);
    });
    
    // 设置超时
    setTimeout(() => {
      if (pythonProcess) {
        reject(new Error('Python backend startup timeout'));
      }
    }, 10000);
  });
}

/**
 * 发送命令到 Python 后端
 */
function sendCommandToPython(command: any): void {
  if (!pythonProcess || !pythonProcess.stdin) {
    console.error('[MAIN] Python process not available');
    return;
  }
  
  const commandJson = JSON.stringify(command) + '\n';
  pythonProcess.stdin.write(commandJson);
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
