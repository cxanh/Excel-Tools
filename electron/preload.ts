import { contextBridge, ipcRenderer } from 'electron';

/**
 * Python Bridge API
 * 暴露给渲染进程的 Python 通信接口
 */
const pythonBridge = {
  /**
   * 发送命令到 Python 后端
   * @param command - 命令对象，包含 action 和 params
   */
  sendCommand: (command: { action: string; params: any }) => {
    ipcRenderer.send('python-command', command);
  },
  
  /**
   * 监听 Python 后端消息
   * @param callback - 消息回调函数
   */
  onMessage: (callback: (message: any) => void) => {
    ipcRenderer.on('python-message', (_event, message) => {
      callback(message);
    });
  },
  
  /**
   * 移除消息监听器
   */
  removeMessageListener: () => {
    ipcRenderer.removeAllListeners('python-message');
  }
};

/**
 * 通过 contextBridge 安全地暴露 API 到渲染进程
 */
contextBridge.exposeInMainWorld('pythonBridge', pythonBridge);

/**
 * TypeScript 类型声明
 * 在渲染进程中使用时可以获得类型提示
 */
declare global {
  interface Window {
    pythonBridge: typeof pythonBridge;
  }
}
